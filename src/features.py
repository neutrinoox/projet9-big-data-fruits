"""Fonctions d'extraction de features images.

Le principe du projet : transformer chaque image en vecteur numerique.
On utilise un CNN pre-entraine comme extracteur de caracteristiques.
"""

import numpy as np
from PIL import Image
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array

from src.config import IMAGE_SIZE


def build_feature_extractor():
    """Cree le modele ResNet50 sans sa couche de classification.

    include_top=False retire la derniere couche qui predit les classes ImageNet.
    pooling='avg' transforme la sortie du CNN en un vecteur plat.
    """
    model = ResNet50(
        weights="imagenet",
        include_top=False,
        pooling="avg",
        input_shape=(IMAGE_SIZE[0], IMAGE_SIZE[1], 3),
    )
    return model


def load_image_as_array(image_path: str) -> np.ndarray:
    """Charge une image locale et la prepare pour ResNet50."""
    # On force le format RGB pour eviter les problemes avec les images en niveaux de gris.
    image = Image.open(image_path).convert("RGB")

    # ResNet50 attend des images de taille 224 x 224.
    image = image.resize(IMAGE_SIZE)

    # Conversion PIL -> tableau numpy.
    array = img_to_array(image)

    # Ajout de la dimension batch : (224, 224, 3) devient (1, 224, 224, 3).
    array = np.expand_dims(array, axis=0)

    # Preprocessing officiel attendu par ResNet50.
    array = preprocess_input(array)
    return array


def extract_single_image_features(model, image_path: str) -> np.ndarray:
    """Extrait le vecteur de features d'une image."""
    array = load_image_as_array(image_path)

    # Prediction du CNN : on recupere un vecteur numerique representant l'image.
    features = model.predict(array, verbose=0)

    # On renvoie un vecteur 1D plus simple a stocker.
    return features.flatten()
