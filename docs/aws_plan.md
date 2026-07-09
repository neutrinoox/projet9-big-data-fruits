# Plan AWS pour le P9

## Idee generale

AWS sert a montrer que le traitement peut passer a l'echelle.

Architecture simple :

```text
Images Fruits-360 -> S3 -> EMR / Spark -> Parquet -> S3
```

## Etapes

1. Creer un bucket S3 en region europeenne.
2. Envoyer les images dans le bucket.
3. Creer un cluster EMR avec Spark.
4. Executer le notebook ou le script PySpark.
5. Sauvegarder les features PCA en Parquet sur S3.
6. Supprimer le cluster EMR pour eviter les couts.

## RGPD

Pour limiter les risques RGPD :

- utiliser une region europeenne, par exemple eu-west-3 Paris ;
- ne pas stocker de donnees personnelles ;
- supprimer les ressources inutiles apres execution ;
- documenter les choix de stockage et de securite.

## Cout

EMR peut couter cher si le cluster reste actif.

Regle simple :

- creer le cluster uniquement pour l'execution ;
- verifier les resultats ;
- eteindre le cluster juste apres.
