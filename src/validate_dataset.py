"""Verification simple du dataset local.

Ce script sert a verifier que les images sont au bon endroit
avant de lancer les traitements plus lourds.
"""

from collections import Counter
from pathlib import Path
from src.config import DATA_DIR


VALID_EXTENSIONS = {".jpg", ".jpeg", ".png"}


def find_images(images_root):
    """Retourne toutes les images valides dans un ordre reproductible."""
    images_root = Path(images_root)
    if not images_root.exists():
        raise FileNotFoundError(f"Le dossier {images_root} n'existe pas.")
    paths = sorted(
        path for path in images_root.rglob("*")
        if path.is_file() and path.suffix.lower() in VALID_EXTENSIONS
    )
    if not paths:
        raise FileNotFoundError(f"Aucune image trouvee dans {images_root}.")
    return paths


def select_balanced_images(image_paths, max_images):
    """Sélectionne autant que possible le même nombre d'images par classe."""
    by_label = {}
    for path in image_paths:
        by_label.setdefault(path.parent.name, []).append(path)

    selected = []
    labels = sorted(by_label)
    cursor = 0
    while len(selected) < min(max_images, len(image_paths)):
        added = False
        for label in labels:
            if cursor < len(by_label[label]):
                selected.append(by_label[label][cursor])
                added = True
                if len(selected) == max_images:
                    break
        if not added:
            break
        cursor += 1
    return selected


def main():
    # Le dataset devra etre place dans data/fruits.
    images_root = DATA_DIR / "fruits"

    image_paths = find_images(images_root)

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
