"""Telecharge et extrait le dataset Fruits-360 avec l'API Kaggle.

Prerequis :
1. Installer le package Kaggle : pip install kaggle
2. Configurer le fichier kaggle.json dans le dossier attendu par Kaggle.

Le dataset est extrait dans data/fruits/ et reste ignore par GitHub.
"""

from pathlib import Path
import subprocess
import sys
import zipfile


DATA_DIR = Path("data/fruits")
ZIP_PATH = Path("data/fruits360.zip")
DATASET_SLUG = "moltean/fruits"


def main():
    # Cree le dossier data s'il n'existe pas encore.
    DATA_DIR.parent.mkdir(parents=True, exist_ok=True)

    # Telecharge l'archive officielle via l'outil Kaggle.
    command = [
        "kaggle",
        "datasets",
        "download",
        "-d",
        DATASET_SLUG,
        "-p",
        str(DATA_DIR.parent),
        "--force",
    ]
    subprocess.run(command, check=True)

    # Kaggle nomme habituellement l'archive fruits.zip.
    downloaded_zip = DATA_DIR.parent / "fruits.zip"
    if not downloaded_zip.exists():
        raise FileNotFoundError("Archive Kaggle introuvable apres le telechargement.")

    downloaded_zip.rename(ZIP_PATH)

    # Extrait les images dans data/fruits/.
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH, "r") as archive:
        archive.extractall(DATA_DIR)

    print(f"Dataset extrait dans : {DATA_DIR.resolve()}")
    print("Etape suivante : python -m src.validate_dataset")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        print("Le telechargement Kaggle a echoue. Verifie ta configuration kaggle.json.")
        sys.exit(error.returncode)
