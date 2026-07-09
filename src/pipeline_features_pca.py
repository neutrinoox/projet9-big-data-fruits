"""Pipeline local features + PCA."""

from pathlib import Path
import pandas as pd
from sklearn.decomposition import PCA

from src.config import DATA_DIR, OUTPUTS_DIR, PCA_N_COMPONENTS
from src.features import build_feature_extractor, extract_single_image_features


def main():
    # Dossier attendu pour les images locales.
    images_root = DATA_DIR / "fruits"
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # On prend un petit echantillon pour tester sans bloquer le PC.
    image_paths = list(images_root.rglob("*.jpg"))[:100]
    if not image_paths:
        raise FileNotFoundError("Ajoute le dataset dans data/fruits avant de lancer ce script.")

    # ResNet50 transforme chaque image en vecteur numerique.
    model = build_feature_extractor()
    rows = []

    for path in image_paths:
        features = extract_single_image_features(model, str(path))
        rows.append({"image_path": str(path), "label": path.parent.name, "features": features.tolist()})

    df = pd.DataFrame(rows)

    # La PCA reduit la taille des vecteurs pour obtenir un resultat plus leger.
    n_components = min(PCA_N_COMPONENTS, len(df), len(df["features"].iloc[0]))
    pca = PCA(n_components=n_components)
    pca_features = pca.fit_transform(df["features"].tolist())

    result = pd.DataFrame(pca_features, columns=[f"pca_{i}" for i in range(n_components)])
    result.insert(0, "label", df["label"])
    result.insert(0, "image_path", df["image_path"])

    result.to_parquet(OUTPUTS_DIR / "features_pca.parquet", index=False)
    result.to_csv(OUTPUTS_DIR / "features_pca.csv", index=False)
    print("Resultats crees dans outputs/features_pca.parquet et outputs/features_pca.csv")


if __name__ == "__main__":
    main()
