"""Pipeline Spark unique, exécutable en local puis sur AWS EMR.

Exemple local :
python -m src.pipeline_spark --input data/fruits/Training --output outputs/spark_pca
"""

import argparse
import io

import numpy as np
from PIL import Image
from pyspark.ml.feature import PCA
from pyspark.ml.functions import array_to_vector
from pyspark.sql.types import ArrayType, FloatType, StringType, StructField, StructType

from src.config import IMAGE_SIZE, INFERENCE_BATCH_SIZE, LOCAL_MAX_IMAGES, LOCAL_PCA_COMPONENTS
from src.features import build_feature_extractor
from src.spark_utils import create_spark_session, read_image_paths


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Dossier local ou URI S3 contenant les images")
    parser.add_argument("--output", required=True, help="Dossier Parquet local ou URI S3")
    parser.add_argument("--max-images", type=int, default=LOCAL_MAX_IMAGES)
    parser.add_argument("--components", type=int, default=LOCAL_PCA_COMPONENTS)
    parser.add_argument("--batch-size", type=int, default=INFERENCE_BATCH_SIZE)
    return parser.parse_args()


def extract_partition(rows, weights, batch_size):
    """Extrait les features par lots à l'intérieur d'une partition Spark."""
    from tensorflow.keras.applications.resnet50 import preprocess_input

    model = build_feature_extractor(weights=None)
    model.set_weights(weights)
    batch = []

    def predict(current_batch):
        arrays = []
        for row in current_batch:
            image = Image.open(io.BytesIO(row.content)).convert("RGB").resize(IMAGE_SIZE)
            arrays.append(np.asarray(image, dtype=np.float32))
        vectors = model.predict(
            preprocess_input(np.stack(arrays)),
            batch_size=batch_size,
            verbose=0,
        )
        for row, vector in zip(current_batch, vectors):
            yield row.image_path, row.label, vector.astype(float).tolist()

    for row in rows:
        batch.append(row)
        if len(batch) == batch_size:
            yield from predict(batch)
            batch = []
    if batch:
        yield from predict(batch)


def run_pipeline(input_path, output_path, max_images, components, batch_size):
    """Lit les images, extrait les features, applique la PCA et sauvegarde."""
    spark = create_spark_session()
    images = read_image_paths(spark, input_path).limit(max_images).cache()
    image_count = images.count()
    if image_count < 2:
        spark.stop()
        raise ValueError("Il faut au moins deux images pour appliquer une PCA.")

    driver_model = build_feature_extractor()
    broadcast_weights = spark.sparkContext.broadcast(driver_model.get_weights())
    schema = StructType([
        StructField("image_path", StringType(), nullable=False),
        StructField("label", StringType(), nullable=False),
        StructField("features_array", ArrayType(FloatType(), containsNull=False), nullable=False),
    ])
    feature_rows = images.rdd.mapPartitions(
        lambda rows: extract_partition(rows, broadcast_weights.value, batch_size)
    )
    featured = spark.createDataFrame(feature_rows, schema)
    featured = (
        featured.withColumn("features", array_to_vector("features_array"))
        .select("image_path", "label", "features")
        .cache()
    )
    # Matérialise et mémorise les features : ResNet50 ne sera pas recalculé
    # pendant l'ajustement puis l'application de la PCA.
    featured.count()

    n_components = min(components, image_count - 1, 2048)
    pca = PCA(k=n_components, inputCol="features", outputCol="pca_features")
    pca_model = pca.fit(featured)
    result = pca_model.transform(featured).select("image_path", "label", "pca_features")
    result.write.mode("overwrite").parquet(output_path)

    metrics = {
        "images": image_count,
        "components": n_components,
        "explained_variance": float(pca_model.explainedVariance.sum()),
    }
    broadcast_weights.destroy()
    featured.unpersist()
    images.unpersist()
    spark.stop()
    return metrics


def main():
    args = parse_args()
    metrics = run_pipeline(
        args.input,
        args.output,
        args.max_images,
        args.components,
        args.batch_size,
    )
    print(f"Images traitees : {metrics['images']}")
    print(f"Dimensions conservees : {metrics['components']}")
    print(f"Variance expliquee cumulee : {metrics['explained_variance']:.2%}")
    print(f"Resultat : {args.output}")


if __name__ == "__main__":
    main()
