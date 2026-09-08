# Validation des corrections — 8 septembre 2026

## Contrôles effectivement exécutés dans l'environnement de correction

- Six tests unitaires réussis : sélection équilibrée, collisions de noms, dossiers imbriqués,
  dossier existant non identifié, remplacement sûr, paramètres invalides.
- Construction de l'archive Python pour EMR réussie.
- Syntaxe du bootstrap vérifiée avec `bash -n`.

## Exécution complète

L'installation locale de Spark/TensorFlow a été interrompue par le contrôle réseau de l'environnement.
Le test d'intégration n'a donc pas été exécuté ici. Un workflow GitHub Actions est fourni pour tester
le vrai pipeline Spark et ResNet50/ImageNet sur des images synthétiques, puis conserver les preuves.
Son résultat doit être consulté : la présence du workflow ne prouve pas qu'il a réussi.

Le notebook Colab permet de valider ensuite 100 images réelles de fruits et 10 classes.
Les sorties de l'ancien notebook ont été retirées de la version corrigée : les résultats historiques
ne prouvent pas le fonctionnement du nouveau code. Ils restent consultables dans l'historique Git.

## Ce qui exige encore AWS

Bootstrap sur chaque nœud, accès IAM/S3, exécution EMR, stockage et calcul européens, répartition
réelle sur plusieurs machines et arrêt du cluster. Aucun de ces points n'est déclaré testé ici.
