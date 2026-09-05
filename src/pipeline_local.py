"""Preuve de concept locale : images -> ResNet50 -> PCA -> Parquet."""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

from src.config import (
    DATA_DIR,
    INFERENCE_BATCH_SIZE,
    LOCAL_MAX_IMAGES,
    LOCAL_PCA_COMPONENTS,
    OUTPUTS_DIR,
)
from src.features import build_feature_extractor, extract_batch_features
from src.validate_dataset import find_images, select_balanced_images


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default=str(DATA_DIR / "fruits"))
    parser.add_argument("--output", default=str(OUTPUTS_DIR / "local_features_pca.parquet"))
    parser.add_argument("--max-images", type=int, default=LOCAL_MAX_IMAGES)
    parser.add_argument("--components", type=int, default=LOCAL_PCA_COMPONENTS)
    parser.add_argument("--batch-size", type=int, default=INFERENCE_BATCH_SIZE)
    return parser.parse_args()


def run_local_pipeline(input_path, output_path, max_images, components, batch_size):
    """Execute le prototype et renvoie le DataFrame final et le modele PCA."""
    image_paths = select_balanced_images(find_images(input_path), max_images)
    if len(image_paths) < 2:
        raise ValueError("Il faut au moins deux images pour appliquer une PCA.")

    model = build_feature_extractor()
    feature_batches = []
    for start in range(0, len(image_paths), batch_size):
        batch = image_paths[start : start + batch_size]
        feature_batches.append(extract_batch_features(model, map(str, batch)))
    features = np.vstack(feature_batches)

    n_components = min(components, len(image_paths) - 1, features.shape[1])
    pca = PCA(n_components=n_components, random_state=42)
    reduced = pca.fit_transform(features)

    result = pd.DataFrame({
        "image_path": [str(path) for path in image_paths],
        "label": [path.parent.name for path in image_paths],
        "pca_features": [row.astype(float).tolist() for row in reduced],
    })
    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_parquet(output_path, index=False)
    return result, pca


def main():
    args = parse_args()
    result, pca = run_local_pipeline(
        input_path=Path(args.input),
        output_path=Path(args.output),
        max_images=args.max_images,
        components=args.components,
        batch_size=args.batch_size,
    )
    print(f"Images traitees : {len(result)}")
    print(f"Dimensions conservees : {pca.n_components_}")
    print(f"Variance expliquee cumulee : {pca.explained_variance_ratio_.sum():.2%}")
    print(f"Resultat : {args.output}")


if __name__ == "__main__":
    main()
