# Commandes utiles

## Verifier le dataset local

```bash
python -m src.validate_dataset
```

Cette commande verifie que le dossier `data/fruits` existe et contient des images.

## Tester l'extraction de features localement

```bash
python -m src.pipeline_features_pca
```

Cette commande prend un echantillon d'images, extrait les features avec ResNet50, applique une PCA et sauvegarde les resultats.

## Tester Spark localement

```bash
python -m src.pipeline_spark
```

Cette commande sera surtout utile quand les chemins S3 seront configures.

## Envoyer le dataset vers S3

```bash
aws s3 sync data/fruits/ s3://TON-BUCKET-P9/data/fruits/
```

## Recuperer les resultats depuis S3

```bash
aws s3 sync s3://TON-BUCKET-P9/outputs/ outputs_s3/
```
