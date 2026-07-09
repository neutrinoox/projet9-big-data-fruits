# Notes de soutenance

## Probleme metier

La startup Fruits! veut industrialiser un traitement d'images de fruits.
L'objectif est de preparer une chaine capable de traiter beaucoup d'images.

## Pourquoi le Big Data ?

Un dataset d'images peut devenir lourd :

- beaucoup de fichiers ;
- beaucoup de pixels ;
- extraction de features couteuse ;
- besoin de stockage scalable.

Spark permet de distribuer le travail sur plusieurs machines.

## Architecture retenue

```text
Dataset images -> S3 -> EMR Spark -> features CNN -> PCA -> Parquet sur S3
```

## Role de ResNet50

ResNet50 est un modele deja entraine sur ImageNet.
On ne l'utilise pas pour classifier directement les fruits.
On l'utilise comme extracteur de caracteristiques.

## Role de la PCA

Les features CNN sont riches mais volumineuses.
La PCA reduit la dimension tout en conservant l'information principale.

## Choix Cloud

AWS S3 stocke les donnees.
AWS EMR execute Spark.
Une region europeenne limite les risques RGPD.

## Points a expliquer clairement

- Le dataset n'est pas pousse sur GitHub.
- Les resultats lourds sont stockes sur S3.
- Le cluster EMR doit etre eteint apres execution.
- Le pipeline est concu pour passer du local vers le cloud.
