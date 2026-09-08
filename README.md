# Projet 9 — Traitement Big Data sur le Cloud

Projet OpenClassrooms **Fruits!** : images → ResNet50 → centrage → PCA Spark → Parquet.
Le projet prépare un traitement distribué, sans entraîner un classificateur de fruits.

[Notebook de validation Colab](https://colab.research.google.com/github/neutrinoox/projet9-big-data-fruits/blob/fix/p9-pre-aws-validation/notebooks/P9_traitement_big_data_cloud.ipynb)

## État réel

Le notebook précédent contenait une exécution locale réussie sur 100 images et 10 classes.
La version corrigée doit être réexécutée : les anciennes sorties ont été retirées pour ne pas
les attribuer au nouveau code. Consulter [le bilan de validation](docs/validation.md).
**Aucune exécution AWS n'est encore attestée par ce dépôt.**

## Corrections de préparation AWS

- Copie des images sans collisions, protection des dossiers et manifeste SHA-256.
- Redistribution explicite avant l'extraction, broadcast et lots TensorFlow.
- Relecture Parquet : effectifs, unicité, dimensions et valeurs finies.
- Sauvegarde du centrage, de la PCA et des mesures de variance, temps, partitions et hôtes.
- Nouvelle destination pour chaque essai ; aucun écrasement automatique des runs.
- Archive du code pour `--py-files`, dépendances directes fixées et bootstrap Python isolé.

## Démarrage

Suivre [installation.md](docs/installation.md), puis [commands.md](docs/commands.md).
Le dossier Training doit être choisi explicitement pour éviter de mélanger variantes et splits.
L'échantillon de départ est limité à 100 images, 10 classes ; augmenter seulement après validation.

## Organisation

| Fichier | Rôle |
|---|---|
| `notebooks/P9_traitement_big_data_cloud.ipynb` | Parcours Colab avec commentaires français et preuves sauvegardées |
| `scripts/prepare_sample.py` | Échantillon sûr et manifeste |
| `src/pipeline_local.py` | Contrôle ResNet50 + sklearn PCA hors Spark |
| `src/pipeline_spark.py` | Pipeline à exécuter en local puis sur EMR |
| `scripts/package_emr.py` | Paquet du code et manifeste pour les workers |
| `bootstrap/install_emr_dependencies.sh` | Installation identique sur chaque nœud EMR |
| `docs/criteres_evaluation.md` | CE retrouvés, preuves et étapes restant à valider |
| `docs/aws_plan.md` | Architecture, paramètres à confirmer et démonstration |
| `docs/soutenance.md` | Explications et questions de jury |

Les données, paquets générés, résultats et secrets ne sont pas versionnés dans Git.
Après chaque run, conserver les preuves dans un espace durable, puis sur S3 pour le livrable cloud.
La grille publique retrouvée est une reproduction étudiante, à confirmer auprès d'OC lors de la reprise.
