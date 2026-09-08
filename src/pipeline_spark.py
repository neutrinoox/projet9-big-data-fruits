"""Chaîne Spark image → ResNet50 → centrage → PCA → Parquet et preuves d'exécution."""

# Charge les API Spark et les outils de mesure sans charger TensorFlow sur le driver à l'import.
import argparse
import io
import json
import math
import socket
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
import numpy as np
from PIL import Image
from pyspark import StorageLevel, TaskContext
from pyspark.ml.feature import PCA, StandardScaler
from pyspark.ml.functions import array_to_vector, vector_to_array
from pyspark.sql import functions as F
from pyspark.sql.types import ArrayType, FloatType, IntegerType, StringType, StructField, StructType
from src.config import IMAGE_SIZE, INFERENCE_BATCH_SIZE, LOCAL_MAX_IMAGES, LOCAL_PCA_COMPONENTS
from src.spark_utils import create_spark_session, read_image_paths

# Vérifie les paramètres avant toute lecture ou écriture coûteuse.
def validate_parameters(input_path, output_path, max_images, components, batch_size, partitions):
    if max_images < 0 or components < 1 or batch_size < 1 or partitions < 1:
        raise ValueError('max_images doit être >= 0 ; composantes, lot et partitions doivent être > 0.')
    def normalized(value):
        uri = urlsplit(str(value))
        if uri.scheme in ('s3', 's3a', 's3n'):
            return 's3://' + uri.netloc + uri.path.rstrip('/')
        return str(Path(value).resolve())
    source, target = normalized(input_path), normalized(output_path)
    if source == target or source.startswith(target + '/') or target.startswith(source + '/'):
        raise ValueError('Entrée et sortie ne doivent pas être identiques ou imbriquées.')

# Fixe la concurrence TensorFlow pour éviter plusieurs pools de threads par tâche Spark.
def feature_model(weights):
    import tensorflow as tf
    # Un worker Python réutilisé a déjà initialisé TensorFlow avec ces limites.
    try:
        tf.config.threading.set_intra_op_parallelism_threads(1)
        tf.config.threading.set_inter_op_parallelism_threads(1)
    except RuntimeError:
        pass
    tf.keras.backend.clear_session()
    from src.features import build_feature_extractor
    return build_feature_extractor(weights=weights)

# Crée un modèle par partition non vide ; les poids proviennent du broadcast du driver.
def extract_partition(rows, weights, batch_size):
    from itertools import chain
    from tensorflow.keras.applications.resnet50 import preprocess_input
    rows = iter(rows)
    first = next(rows, None)
    if first is None:
        return
    model = feature_model(None)
    model.set_weights(weights)
    context = TaskContext.get()
    partition_id = context.partitionId() if context else -1
    hostname = socket.gethostname()
    batch = []
    # Convertit un lot d'images et renvoie aussi la provenance réelle du calcul.
    def predict(current_batch):
        arrays = []
        for row in current_batch:
            try:
                with Image.open(io.BytesIO(row.content)) as image:
                    arrays.append(np.asarray(image.convert('RGB').resize(IMAGE_SIZE), dtype=np.float32))
            except Exception as exc:
                raise ValueError(f'Image illisible : {row.image_path}') from exc
        vectors = model(preprocess_input(np.stack(arrays)), training=False).numpy()
        for row, vector in zip(current_batch, vectors):
            yield row.image_path, row.label, vector.astype(float).tolist(), partition_id, hostname
    for row in chain([first], rows):
        batch.append(row)
        if len(batch) == batch_size:
            yield from predict(batch)
            batch = []
    if batch:
        yield from predict(batch)

# Contrôle les valeurs, les dimensions et l'unicité après matérialisation ou relecture.
def validate_vectors(frame, vector_col, dimension, expected_count):
    array = vector_to_array(vector_col)
    invalid = (F.col(vector_col).isNull() | F.col('image_path').isNull()
               | F.col('label').isNull() | (F.length('label') == 0)
               | (F.size(array) != dimension)
               | F.exists(array, lambda x: x.isNull() | F.isnan(x) | (F.abs(x) == float('inf'))))
    if frame.filter(invalid).limit(1).count():
        raise ValueError(f'Vecteur ou métadonnées invalides dans {vector_col}.')
    counts = frame.agg(F.count('*').alias('rows'), F.countDistinct('image_path').alias('unique')).first()
    if counts.rows != expected_count or counts.unique != expected_count:
        raise ValueError(f'Nombre de lignes ou chemins uniques incorrect : {counts}.')

# Écrit un petit document JSON via Spark, en local comme sur S3, sans écraser un résultat.
def write_json(spark, path, document):
    spark.sparkContext.parallelize([json.dumps(document, ensure_ascii=False, allow_nan=False)], 1).saveAsTextFile(path)

# Exécute et mesure chaque étape ; une nouvelle destination est exigée pour chaque essai.
def run_pipeline(input_path, output_path, max_images, components, batch_size, partitions=2, weights='imagenet'):
    validate_parameters(input_path, output_path, max_images, components, batch_size, partitions)
    started = time.perf_counter()
    spark = create_spark_session()
    images = featured = None
    broadcast_weights = None
    output_path = str(output_path).rstrip('/')
    try:
        # Refuse une sortie existante, y compris un essai incomplet, pour préserver ses preuves.
        target = spark._jvm.org.apache.hadoop.fs.Path(output_path)
        filesystem = target.getFileSystem(spark._jsc.hadoopConfiguration())
        if filesystem.exists(target):
            raise FileExistsError(f'Sortie existante : {output_path}. Utilisez un nouvel identifiant de run.')
        images = read_image_paths(spark, str(input_path))
        if max_images:
            images = images.limit(max_images)
        # Redistribue après la limite pour ne pas confiner le CNN dans une seule partition.
        images = images.repartition(partitions).persist(StorageLevel.MEMORY_AND_DISK)
        image_count = images.count()
        if image_count < 2:
            raise ValueError('Il faut au moins deux images pour appliquer une PCA.')
        loaded = time.perf_counter()
        driver_model = feature_model(weights)
        broadcast_weights = spark.sparkContext.broadcast(driver_model.get_weights())
        del driver_model
        schema = StructType([
            StructField('image_path', StringType(), False), StructField('label', StringType(), False),
            StructField('features_array', ArrayType(FloatType(), False), False),
            StructField('worker_partition', IntegerType(), False), StructField('worker_host', StringType(), False),
        ])
        rows = images.rdd.mapPartitions(lambda partition: extract_partition(partition, broadcast_weights.value, batch_size))
        featured = (spark.createDataFrame(rows, schema)
                    .withColumn('features', array_to_vector('features_array')).drop('features_array')
                    .persist(StorageLevel.MEMORY_AND_DISK))
        validate_vectors(featured, 'features', 2048, image_count)
        extracted = time.perf_counter()
        # Centre explicitement les variables afin de rendre la projection cohérente avec sklearn PCA.
        scaler = StandardScaler(inputCol='features', outputCol='centered', withMean=True, withStd=False).fit(featured)
        centered = scaler.transform(featured)
        n_components = min(components, image_count - 1, 2048)
        pca_model = PCA(k=n_components, inputCol='centered', outputCol='pca_features').fit(centered)
        variance = [float(v) for v in pca_model.explainedVariance]
        if not all(math.isfinite(v) and v >= 0 for v in variance) or sum(variance) <= 0:
            raise ValueError('Variance PCA non exploitable : vérifier la diversité des images.')
        result = pca_model.transform(centered).select('image_path', 'label', 'pca_features')
        reduced = time.perf_counter()
        # Sauvegarde puis relit réellement les résultats ; le marqueur final certifie tous les contrôles.
        result.write.mode('errorifexists').parquet(output_path + '/data')
        saved = spark.read.parquet(output_path + '/data')
        validate_vectors(saved, 'pca_features', n_components, image_count)
        scaler.write().save(output_path + '/centering_model')
        pca_model.write().save(output_path + '/pca_model')
        distribution = [r.asDict() for r in featured.groupBy('worker_partition', 'worker_host').count().collect()]
        label_counts = [r.asDict() for r in featured.groupBy('label').count().collect()]
        metrics = {
            'status': 'validated', 'created_utc': datetime.now(timezone.utc).isoformat(),
            'input': str(input_path), 'output': output_path, 'images': image_count,
            'features': 2048, 'components': n_components, 'requested_components': components,
            'explained_variance': sum(variance), 'variance_by_component': variance,
            'requested_partitions': partitions, 'active_partitions': len(distribution),
            'worker_hosts': sorted({r['worker_host'] for r in distribution}),
            'partition_distribution': distribution, 'label_counts': label_counts,
            'spark_version': spark.version, 'spark_master': spark.sparkContext.master,
            'application_id': spark.sparkContext.applicationId, 'weights': weights,
            'batch_size': batch_size, 'max_images': max_images,
            'seconds': {'read': loaded-started, 'cnn_and_validation': extracted-loaded,
                        'pca': reduced-extracted, 'total_before_metrics': time.perf_counter()-started},
        }
        write_json(spark, output_path + '/metrics', metrics)
        print(json.dumps(metrics, ensure_ascii=False, indent=2))
        return metrics
    finally:
        # Libère les caches, les poids et la session même lorsqu'une étape échoue.
        for frame in (featured, images):
            if frame is not None:
                frame.unpersist()
        if broadcast_weights is not None:
            broadcast_weights.destroy()
        spark.stop()

# Rend les tailles explicites ; zéro désactive volontairement la limite d'images.
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--max-images', type=int, default=LOCAL_MAX_IMAGES, help='0 = toutes les images')
    parser.add_argument('--components', type=int, default=LOCAL_PCA_COMPONENTS)
    parser.add_argument('--batch-size', type=int, default=INFERENCE_BATCH_SIZE)
    parser.add_argument('--partitions', type=int, default=2)
    args = parser.parse_args()
    run_pipeline(args.input, args.output, args.max_images, args.components, args.batch_size, args.partitions)

# Permet le lancement direct par spark-submit ou python -m.
if __name__ == '__main__':
    main()
