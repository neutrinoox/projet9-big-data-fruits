"""Verification simple du dataset local.

Ce script sert a verifier que les images sont au bon endroit
avant de lancer les traitements plus lourds.
"""

from collections import Counter
from src.config import DATA_DIR


VALID_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def main():
    # Le dataset devra etre place dans data/fruits.
    images_root = DATA_DIR / "fruits"

    if not images_root.exists():
        raise FileNotFoundError("Le dossier data/fruits n'existe pas encore.")

    # On recupere toutes les images jpg/jpeg/png.
    image_paths = [p for p in images_root.rglob("*") if p.suffix.lower() in VALID_EXTENSIONS]

    if not image_paths:
        raise FileNotFoundError("Aucune image trouvee dans data/fruits.")

    # Le label correspond au nom du dossier parent.
    labels = [p.parent.name for p in image_paths]
    label_counts = Counter(labels)

    print(f"Nombre total d'images : {len(image_paths)}")
    print(f"Nombre de classes : {len(label_counts)}")
    print("\nExemples de classes :")

    for label, count in label_counts.most_common(10):
        print(f"- {label} : {count} images")


if __name__ == "__main__":
    main()
