"""Enchaine les deux etapes du pipeline EMR.

Etape 1 : extraction des features ResNet50.
Etape 2 : reduction de dimension avec une PCA Spark.

Ce script prepare les commandes a lancer avec spark-submit sur le cluster EMR.
"""

import argparse
import subprocess
import sys


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--images", required=True, help="Chemin S3 des images")
    parser.add_argument("--features", required=True, help="Chemin S3 temporaire des features")
    parser.add_argument("--output", required=True, help="Chemin S3 final des features PCA")
    parser.add_argument("--components", type=int, default=50)
    return parser.parse_args()


def run_command(command):
    """Execute une commande et arrete le pipeline en cas d'erreur."""
    print("Commande lancee :", " ".join(command))
    subprocess.run(command, check=True)


def main():
    args = parse_args()

    # Premiere etape : images S3 -> features ResNet50 en Parquet.
    run_command([
        "spark-submit",
        "src/emr_features_job.py",
        "--input",
        args.images,
        "--output",
        args.features,
    ])

    # Deuxieme etape : features ResNet50 -> PCA -> Parquet final.
    run_command([
        "spark-submit",
        "src/emr_pca_job.py",
        "--input",
        args.features,
        "--output",
        args.output,
        "--components",
        str(args.components),
    ])

    print("Pipeline EMR termine avec succes.")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        print(f"Le pipeline s'est arrete avec le code {error.returncode}.")
        sys.exit(error.returncode)
