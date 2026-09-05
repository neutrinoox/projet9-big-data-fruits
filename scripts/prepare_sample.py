"""Crée un petit échantillon équilibré sans modifier le dataset original."""

import argparse
import shutil
from pathlib import Path

from src.validate_dataset import find_images, select_balanced_images


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="data/fruits")
    parser.add_argument("--output", default="data/sample")
    parser.add_argument("--images", type=int, default=100)
    parser.add_argument("--classes", type=int, default=10)
    return parser.parse_args()


def main():
    args = parse_args()
    input_root = Path(args.input).resolve()
    output_root = Path(args.output)
    if output_root.resolve() == input_root:
        raise ValueError("Le dossier de sortie doit être différent du dataset source.")
    if output_root.exists():
        shutil.rmtree(output_root)

    selected = select_balanced_images(find_images(input_root), args.images, args.classes)

    for source in selected:
        destination = output_root / source.parent.name / source.name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)

    print(f"Échantillon créé : {len(selected)} images dans {output_root}")
    print(f"Classes représentées : {len({path.parent.name for path in selected})}")


if __name__ == "__main__":
    main()
