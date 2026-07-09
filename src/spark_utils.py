"""Outils Spark pour le projet P9.

Ce module contient les fonctions de base pour creer une session Spark
et lire les chemins des images.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import input_file_name, regexp_extract



def create_spark_session(app_name: str = "P9 Big Data Fruits") -> SparkSession:
    """Cree une session Spark locale ou compatible EMR.

    SparkSession est le point d'entree principal de PySpark.
    En local, Spark utilise ton ordinateur.
    Sur AWS EMR, Spark utilise le cluster.
    """
    spark = (
        SparkSession.builder
        .appName(app_name)
        .config("spark.sql.execution.arrow.pyspark.enabled", "true")
        .getOrCreate()
    )
    return spark



def read_image_paths(spark: SparkSession, images_path: str):
    """Lit les images avec Spark et ajoute chemin + label.

    images_path peut etre un chemin local ou un chemin S3.
    Exemple local : data/fruits/Training/*
    Exemple S3 : s3://bucket/data/fruits/Training/*
    """
    df = spark.read.format("binaryFile").load(images_path)

    # input_file_name recupere le chemin exact du fichier lu par Spark.
    df = df.withColumn("image_path", input_file_name())

    # Le label est extrait depuis le nom du dossier parent.
    # Exemple : data/fruits/Training/Banana/1.jpg -> Banana
    df = df.withColumn("label", regexp_extract("image_path", r"/([^/]+)/[^/]+$", 1))

    return df.select("image_path", "label", "content")
