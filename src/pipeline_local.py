"""Test local minimal avant AWS."""

from pathlib import Path
import pandas as pd

from src.config import DATA_DIR, OUTPUTS_DIR
from src.features import build_feature_extractor, extract_single_image_features


def main():
    """Extrait les features de quelques images locales."""
    images_root = DATA_DIR / "fruits"
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # On cherche quelques images jpg/png dans le dataset local.
    image_paths = list(images_root.rglob("*.jpg"))[:10]

    if not image_paths:
        raise FileNotFoundError("Ajoute le dataset dans data/fruits avant de lancer ce script.")

    # Le modele ResNet50 transforme chaque image en vecteur numerique.
    model = build_feature_extractor()
    rows = []

    for path in image_paths:
        features = extract_single_image_features(model, str(path))
        rows.append({"image_path": str(path), "label": path.parent.name, "features": features.tolist()})

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUTS_DIR / "sample_features.csv", index=False)
    print("Fichier cree : outputs/sample_features.csv")


if __name__ == "__main__":
    main()
