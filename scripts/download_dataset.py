"""Télécharge et extrait Fruits-360 avec la bibliothèque officielle KaggleHub."""

from pathlib import Path

import kagglehub


DATA_DIR = Path("data/fruits")
DATASET_SLUG = "moltean/fruits"


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    downloaded_path = kagglehub.dataset_download(
        DATASET_SLUG,
        output_dir=str(DATA_DIR),
    )
    print(f"Dataset disponible dans : {Path(downloaded_path).resolve()}")
    print("Étape suivante : python -m src.validate_dataset")


if __name__ == "__main__":
    main()
