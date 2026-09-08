# Correspondance exigences / preuves du P9

Référence publique retrouvée (projet appelé P8 dans ce dépôt, même scénario Fruits!) :
https://github.com/Pimouss75/DS_Projet_8-Deploiement-d-un-modele-dans-le-cloud#référentiel-dévaluation

Il s'agit d'une reproduction par un étudiant, pas d'une confirmation d'OpenClassrooms de la version
applicable à Maxime. Les CE1/CE2 recommencent pour chaque compétence. Ne pas annoncer les CE cloud
comme acquis sur la seule base d'une exécution locale. Vérification de référence : 8 septembre 2026.

| Compétence / CE | Exigence reformulée | Preuve prévue dans le projet | État |
|---|---|---|---|
| Identifier — CE1 | Identifier les briques Big Data | `aws_plan.md`, architecture S3/EMR/YARN/IAM et présentation | Documenté ; présentation finale à produire |
| Identifier — CE2 | Choisir des outils adaptés à la contrainte RGPD | Région européenne, accès S3 et IAM décrits | Configuration réelle AWS à vérifier |
| Utiliser — CE1 | Stocker entrées et résultats dans le cloud | Images, manifeste et `runs/.../data` sur S3 | À exécuter sur AWS |
| Utiliser — CE2 | Exécuter sur des machines cloud | Étape EMR réussie, application YARN, logs et versions | À exécuter sur AWS |
| Utiliser — CE3 | Écrire directement dans le stockage cloud | Sorties Spark Parquet, modèles et métriques vers S3 | Implémenté ; test S3 à faire |
| Paralléliser — CE1 | Identifier les traitements critiques | Mesures lecture/CNN/PCA, mémoire et échanges réseau | Instrumenté ; analyse cloud à compléter |
| Paralléliser — CE2 | Stocker et traiter en Europe | Régions du cluster et des buckets ; configuration IAM | À vérifier sur AWS |
| Paralléliser — CE3 | Développer avec Spark | `pipeline_spark.py`, broadcast, partitions, centrage et PCA MLlib | Implémenté ; résultats des tests dans `validation.md` |
| Paralléliser — CE4 | Exécuter toute la chaîne dans le cloud | Lecture S3 → extraction → PCA → écriture S3, logs complets | À exécuter sur AWS |

## Exigences du scénario en plus des CE

- Broadcast des poids du modèle TensorFlow : créé sur le driver, consulté dans chaque worker.
- PCA PySpark : présente ; modèle de centrage et PCA sauvegardés pour reproduire les transformations.
- Aucune obligation d'entraîner un classificateur dans la consigne retrouvée : ne pas ajouter de taux
  d'accuracy fictif ; les labels servent ici au contrôle des classes et à l'analyse.
- Notebook exécutable dans le cloud : parcours local préparé ; transposer le lancement à EMR comme
  indiqué dans `commands.md` et conserver les sorties effectives dans le notebook final.
- Données initiales et matrice réduite disponibles dans le stockage cloud : à produire sur S3.
- Support de soutenance : architecture, rôles des services, mise en place et étapes PySpark.
- Démonstration d'un environnement EMR opérationnel : préparer sa recréation, confirmer les modalités OC.
- Maîtrise des coûts : arrêt après les tests/démos et contrôle effectif de la facturation résiduelle.

## Conditions pour dire « prêt pour AWS »

1. Tests de protection des données réussis.
2. Pipeline complet exécuté après les corrections, avec ResNet50 et PCA Spark.
3. Petit échantillon réel de fruits traité, relecture Parquet et métriques validées.
4. Au moins deux partitions actives constatées ; aucune conclusion multi-machine en local.
5. Archive Python reconstruite depuis le commit retenu, dépendances et manifeste conservés.
6. Budget, région, rôles et configuration AWS préparés.

## Conditions pour dire « prêt pour la soutenance »

Un run AWS réussi avec preuves ci-dessus, les livrables finaux déposables et une répétition orale.
Avant la réinscription payante, confirmer auprès d'OC la version des projets et la disponibilité des
soutenances dans le mois. Prévoir une marge pour les corrections et les rendez-vous.
