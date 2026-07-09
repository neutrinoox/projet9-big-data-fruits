"""Job Spark prevu pour AWS EMR.

Ce script est volontairement simple : il lit les images depuis S3,
recupere leur label et sauvegarde un index en Parquet.
Il servira de base pour l'execution cloud.
"""

import argparse

from src.spark_utils import create_spark_session, read_image_paths



def parse_args():
    # argparse permet de passer les chemins S3 au moment du lancement.
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Chemin S3 des images")
    parser.add_argument("--output", required=True, help="Chemin S3 de sortie")
    return parser.parse_args()



def main():
    args = parse_args()
    spark = create_spark_session("P9 Fruits EMR Job")

    # Lecture des images par Spark.
    df_images = read_image_paths(spark, args.input)

    # On garde un index simple pour verifier que la lecture cloud fonctionne.
    df_index = df_images.select("image_path", "label")

    print("Apercu des images lues :")
    df_index.show(10, truncate=False)

    # Parquet est un format adapte au Big Data.
    df_index.write.mode("overwrite").parquet(args.output)

    print(f"Index sauvegarde dans : {args.output}")
    spark.stop()


if __name__ == "__main__":
    main()
