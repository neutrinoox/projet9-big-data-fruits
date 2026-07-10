"""PCA distribuee sur les features deja extraites avec Spark."""

import argparse

from pyspark.ml.feature import PCA
from pyspark.ml.linalg import VectorUDT, Vectors
from pyspark.sql.functions import udf

from src.spark_utils import create_spark_session


# Spark ML attend un vecteur Spark et non une simple liste Python.
to_vector = udf(lambda values: Vectors.dense(values), VectorUDT())


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Parquet S3 contenant la colonne features")
    parser.add_argument("--output", required=True, help="Chemin S3 de sortie pour les features PCA")
    parser.add_argument("--components", type=int, default=50, help="Nombre de composantes PCA")
    return parser.parse_args()


def main():
    args = parse_args()
    spark = create_spark_session("P9 EMR PCA")

    # Lecture des features produites par le job ResNet50.
    df = spark.read.parquet(args.input)

    # Conversion de la liste de nombres vers le type Vector attendu par Spark ML.
    df = df.withColumn("features_vector", to_vector("features"))

    # La PCA reduit le nombre de dimensions des vecteurs.
    pca = PCA(
        k=args.components,
        inputCol="features_vector",
        outputCol="pca_features",
    )
    model = pca.fit(df)
    result = model.transform(df)

    # On sauvegarde uniquement les informations utiles pour la suite.
    result.select("image_path", "label", "pca_features").write.mode("overwrite").parquet(args.output)

    spark.stop()


if __name__ == "__main__":
    main()
