"""Pipeline Spark principal du projet P9.

Ce script prepare la logique Big Data :
- lire les images avec Spark ;
- recuperer les labels ;
- sauvegarder une table de controle.

L'extraction CNN distribuee sera ajoutee ensuite dans une version plus avancee.
"""

from src.config import S3_INPUT_PATH, S3_OUTPUT_PATH
from src.spark_utils import create_spark_session, read_image_paths



def main():
    """Lance un premier pipeline Spark compatible AWS EMR."""
    spark = create_spark_session()

    # Sur AWS, ce chemin devra pointer vers le bucket S3 contenant les images.
    input_path = S3_INPUT_PATH + "Training/*"
    output_path = S3_OUTPUT_PATH + "image_index"

    # Spark lit les images comme des fichiers binaires.
    df_images = read_image_paths(spark, input_path)

    # On affiche quelques lignes pour verifier que Spark lit bien les donnees.
    df_images.select("image_path", "label").show(10, truncate=False)

    # On sauvegarde un index simple des images en Parquet.
    df_images.select("image_path", "label").write.mode("overwrite").parquet(output_path)

    print(f"Index des images sauvegarde dans : {output_path}")
    spark.stop()


if __name__ == "__main__":
    main()
