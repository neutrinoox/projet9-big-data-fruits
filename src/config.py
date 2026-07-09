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
MODELS_DIR = PROJECT_ROOT / "models"

# Parametres images.
IMAGE_SIZE = (224, 224)
IMAGE_CHANNELS = 3

# Parametres PCA.
# On commence avec 50 composantes, puis on ajustera selon la variance expliquee.
PCA_N_COMPONENTS = 50

# Noms de colonnes standard dans les DataFrames Spark.
COL_IMAGE_PATH = "image_path"
COL_LABEL = "label"
COL_FEATURES = "features"
COL_PCA_FEATURES = "pca_features"

# Chemins S3 a remplacer quand le bucket AWS sera cree.
S3_INPUT_PATH = "s3://TON-BUCKET-P9/data/fruits/"
S3_OUTPUT_PATH = "s3://TON-BUCKET-P9/outputs/features/"
