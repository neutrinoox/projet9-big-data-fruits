# Expliquer le code simplement

Ce document sert a preparer la soutenance.
Il explique les fichiers avec des mots simples.

## src/config.py

Ce fichier contient les reglages du projet.

A dire au jury :

> J'ai centralise les chemins et les parametres dans un fichier de configuration pour eviter de recopier les memes valeurs dans plusieurs scripts.

## src/features.py

Ce fichier transforme une image en vecteur de nombres.

A dire au jury :

> Une image brute est difficile a manipuler directement. J'utilise ResNet50, un modele deja entraine, pour extraire une representation numerique de chaque image.

## src/spark_utils.py

Ce fichier contient les fonctions liees a Spark.

A dire au jury :

> Spark permet de lire beaucoup d'images et de distribuer le travail sur plusieurs machines, ce qui est l'objectif Big Data du projet.

## src/pca_utils.py

Ce fichier sert a reduire la taille des vecteurs.

A dire au jury :

> Les features extraites par le CNN sont riches mais volumineuses. La PCA permet de garder l'information principale dans moins de dimensions.

## src/pipeline_local.py

Ce fichier sert a tester le projet sur quelques images avant AWS.

A dire au jury :

> Avant de lancer le cloud, je teste localement sur un petit echantillon pour verifier que l'extraction de features fonctionne.

## src/pipeline_spark.py

Ce fichier prepare l'execution Big Data.

A dire au jury :

> Ce pipeline lit les images depuis S3 avec Spark, recupere les labels et sauvegarde les resultats dans un format adapte au Big Data : Parquet.
