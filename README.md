# Projet 9 — Traitement Big Data sur le Cloud

Projet OpenClassrooms réalisé pour la startup fictive **Fruits!**.

[Ouvrir le notebook dans Google Colab](https://colab.research.google.com/github/neutrinoox/projet9-big-data-fruits/blob/main/notebooks/P9_traitement_big_data_cloud.ipynb)

## Objectif

Construire une chaîne de traitement capable de passer à l'échelle :

1. lire des images de fruits ;
2. extraire un vecteur de 2 048 caractéristiques avec ResNet50 pré-entraîné ;
3. réduire sa dimension avec une PCA ;
4. sauvegarder les résultats en Parquet.

Il n'est pas demandé d'entraîner un classificateur.

## Architecture

```text
Images -> Spark binaryFile -> ResNet50 -> Spark PCA -> Parquet
```

Le même pipeline accepte un chemin local pendant la preuve de concept et un
chemin `s3://` lors du passage sur AWS EMR.

## Démarrage local

```bash
python -m venv .venv
source .venv/bin/activate          # Windows : .venv\\Scripts\\activate
pip install -r requirements.txt
python -m scripts.download_dataset
python -m src.validate_dataset
python -m scripts.prepare_sample
python -m src.pipeline_local --input data/sample
python -m src.pipeline_spark --input data/sample --output outputs/spark_pca
```

Le prototype est limité à 100 images afin de rester raisonnable sur une machine
disposant de 8 Go de RAM.

## Contenu du dépôt

- `notebooks/P9_traitement_big_data_cloud.ipynb` : notebook principal du projet.
- `src/features.py` : préparation des images et extraction ResNet50.
- `src/pipeline_local.py` : contrôle rapide hors Spark.
- `src/pipeline_spark.py` : pipeline final local ou EMR, avec poids diffusés par broadcast.
- `src/spark_utils.py` : lecture distribuée des images.
- `src/validate_dataset.py` : audit du dataset.
- `scripts/` : téléchargement et préparation d'un échantillon.
- `docs/` : installation, commandes, architecture AWS et aide à la soutenance.
- `bootstrap/` : installation des dépendances Python sur les nœuds EMR.

Les images, résultats, identifiants AWS et clés privées sont exclus de Git.

## État

- [x] Structure du dépôt
- [x] Téléchargement et validation du dataset
- [x] Prototype local ResNet50 + PCA
- [x] Pipeline PySpark réutilisable sur EMR
- [x] Sortie Parquet
- [ ] Exécution locale avec le dataset réel et conservation des résultats
- [ ] Déploiement S3 / EMR
- [ ] Captures et mesures de l'exécution cloud
- [ ] Support final de soutenance
