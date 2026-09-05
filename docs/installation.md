# Installation locale

## 1. Récupérer le projet

```bash
git clone https://github.com/neutrinoox/projet9-big-data-fruits.git
cd projet9-big-data-fruits
```

## 2. Créer l'environnement

```bash
python -m venv .venv
```

Windows : `.venv\\Scripts\\activate`

Mac/Linux : `source .venv/bin/activate`

## 3. Installer

```bash
pip install -r requirements.txt
```

Java doit aussi être installé pour PySpark.

## 4. Préparer les données

```bash
python -m scripts.download_dataset
python -m src.validate_dataset
python -m scripts.prepare_sample
```

## 5. Exécuter les preuves de concept

```bash
python -m src.pipeline_local --input data/sample
python -m src.pipeline_spark --input data/sample --output outputs/spark_pca
```

Résultats attendus :

- `outputs/local_features_pca.parquet` ;
- dossier Parquet `outputs/spark_pca`.
