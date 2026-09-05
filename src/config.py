"""Configuration centrale du projet P9.

Ce fichier regroupe les chemins et parametres utilises dans les notebooks et scripts.
L'objectif est d'eviter de recopier les memes valeurs partout.
"""

from pathlib import Path


# Racine du projet en local.
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Dossiers locaux. Ils sont ignores par Git car ils peuvent devenir volumineux.
DATA_DIR = PROJECT_ROOT / "data"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Parametres images.
IMAGE_SIZE = (224, 224)
IMAGE_CHANNELS = 3

# Parametres du prototype local. Ils restent modestes pour un ordinateur de 8 Go.
LOCAL_MAX_IMAGES = 100
LOCAL_PCA_COMPONENTS = 20
INFERENCE_BATCH_SIZE = 16

# Noms de colonnes standard dans les DataFrames Spark.
COL_IMAGE_PATH = "image_path"
COL_LABEL = "label"
COL_FEATURES = "features"
COL_PCA_FEATURES = "pca_features"
