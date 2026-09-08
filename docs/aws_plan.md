# Plan AWS — préparation, exécution et preuves

Statut : préparation du déploiement. Aucun cluster n'a été créé ou testé par ces corrections.
Le passage sur AWS et la démonstration finale restent à effectuer.

## Architecture

Images et code sur S3 → driver Spark sur EMR → workers ResNet50 → centrage/PCA Spark → S3.

- S3 : conserve images, archive du code, modèles PCA/centrage, Parquet, métriques et journaux.
- EMR : configure Hadoop/Spark et YARN ; le driver coordonne les tâches, les executors calculent.
- IAM : rôle de service EMR et profil d'instance EC2 ; permissions limitées aux chemins S3 du projet,
  aux journaux et aux opérations EMR nécessaires. Ne pas mettre de clés dans le notebook.
- Réseau : sous-réseau avec accès aux services S3 et aux dépendances nécessaires ; aucun port
  Jupyter/SSH ouvert à tout Internet. Les modalités d'accès seront choisies avec le compte disponible.

## Cible technique documentée

Cible initiale à confirmer lors du lancement : EMR 7.5.0, Spark 3.5.2-amzn-1,
Java 17, Python 3.11, machines x86_64. Cette version EMR est annoncée en support standard
jusqu'au 20 novembre 2026 : si l'exécution est plus tardive, sélectionner et tester une version supportée.
Installer Spark dans les applications EMR ; le bootstrap installe TensorFlow dans `/opt/p9-venv`.
Ne pas installer `requirements.txt` sur EMR : PySpark est fourni par EMR.

Source AWS : https://docs.aws.amazon.com/emr/latest/ReleaseGuide/emr-750-release.html
Distribution Python : https://spark.apache.org/docs/3.5.3/api/python/user_guide/python_packaging.html

Les dépendances directes sont fixées dans `requirements-emr.txt`. Les dépendances transitives
ne constituent pas un verrou complet : conserver `pip freeze` et le manifeste du paquet pour chaque run.

## Avant d'engager des coûts

1. Confirmer région, budget, crédits éventuels, quotas EC2 et accès IAM avec Maxime.
2. Utiliser la même région européenne pour le calcul, S3 et les journaux (exemple : Paris).
3. Bloquer l'accès public S3 ; vérifier le chiffrement et les permissions effectives.
4. Préparer un petit échantillon de validation, le paquet `dist/` et la sortie dédiée à un run.
5. Choisir un cluster à capacité fixe avec suffisamment de mémoire ; pour démontrer plusieurs machines,
   prévoir un primaire et deux workers, et vérifier la répartition effective dans les métriques et Spark UI.
6. Configurer l'arrêt après les étapes et/ou l'arrêt automatique sur inactivité. Une alerte de budget
   n'est pas un plafond de dépenses. Prévoir aussi une heure limite de vérification manuelle.

## Préparer le cluster et le calcul

- Copier `dist/` vers un préfixe S3 propre au commit, ainsi que l'échantillon et son manifeste.
- Le bootstrap reçoit l'URI S3 du fichier `requirements-emr.txt` comme premier argument.
- Configurer driver et workers avec `/opt/p9-venv/bin/python` ; les versions Python doivent correspondre.
- Prévoir l'accès sortant pour pip pendant le bootstrap et pour les poids ImageNet au premier lancement
  (ou un cache de poids Keras préchargé). Seul le driver charge ImageNet ; les workers utilisent le broadcast.
- Exécuter d'abord 100 images, puis augmenter progressivement le volume et mesurer ; ne pas lancer
  100 000 images immédiatement pour découvrir un problème de dépendances.
- Utiliser les commandes de `commands.md`, avec une destination neuve pour chaque exécution.

## Preuves à conserver

- Région des buckets et du cluster, version EMR, configuration des instances et rôles IAM (sans secrets).
- Journal du bootstrap et versions Python/paquets ; statut de l'étape et identifiant d'application Spark.
- Spark UI : executors, tâches, durées, éventuels échanges réseau et répartition effective sur les machines.
- `metrics/` : nombre d'images, classes, composantes, variance, partitions, hôtes et temps.
- `data/`, `centering_model/`, `pca_model/`, manifeste d'échantillon et manifeste du code.
- Vérification de l'arrêt effectif du cluster et des ressources facturées résiduelles (S3, volumes, réseau).

## Démonstration à la soutenance

La consigne publique retrouvée demande un environnement EMR opérationnel et l'explication du script.
Préparer un petit run rapide et la procédure de recréation ; confirmer auprès d'OC les modalités exactes.
Garder également des captures et logs d'un run réussi en cas d'incident, sans supposer qu'ils remplacent
une démonstration exigée. Le cluster ne doit pas rester allumé entre préparation et soutenance.

Le choix d'une région européenne répond à la contrainte géographique du projet ; il ne suffit pas,
à lui seul, à établir une conformité RGPD générale. Les images publiques de fruits ne nécessitent pas
l'ajout de données personnelles ; conserver les contrôles d'accès et la durée de conservation adaptés.
