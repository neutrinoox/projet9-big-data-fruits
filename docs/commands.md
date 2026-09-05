# Commandes utiles

## Préparer les données

```bash
python -m scripts.download_dataset
python -m src.validate_dataset
python -m scripts.prepare_sample
```

Le dataset complet reste dans `data/fruits`. Un échantillon équilibré de
100 images est copié dans `data/sample`.

## Tester ResNet50 + PCA sans Spark

```bash
python -m src.pipeline_local --input data/sample
```

## Tester le pipeline Spark complet localement

```bash
python -m src.pipeline_spark --input data/sample --output outputs/spark_pca
```

## Plus tard : envoyer les données vers S3

```bash
aws s3 sync data/fruits/ s3://TON-BUCKET-P9/data/fruits/
```

## Plus tard : lancer le même pipeline sur EMR

```bash
spark-submit src/pipeline_spark.py \
  --input s3://TON-BUCKET-P9/data/fruits/Training \
  --output s3://TON-BUCKET-P9/outputs/features_pca \
  --max-images 100000 \
  --components 50
```
