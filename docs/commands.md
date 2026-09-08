# Commandes reproductibles

Exécuter depuis la racine du dépôt, dans l'environnement local installé (voir `installation.md`).
Les URI et le dossier Training sont des paramètres à renseigner, pas des ressources déjà créées.

## Préparer les données

```bash
# Télécharge le dataset public ; relève ensuite le chemin exact de la variante Training choisie.
python -m scripts.download_dataset
# Examine les chemins dans le notebook avant de choisir une variante : pas de mélange Training/Test.
python -m scripts.prepare_sample --input data/fruits/CHEMIN-EXACT/Training --output data/sample-v2 --images 100 --classes 10
```

La copie conserve les chemins relatifs et un manifeste avec les empreintes SHA-256. Un dossier
existant non identifié est refusé. L'ancien `data/sample` peut rester en place ; le nouveau utilise `sample-v2`.

## Tester localement

```bash
# Lance les tests de protection du dataset et de sélection des images.
python -m unittest discover -v
# Construit l'archive du code destinée aux workers Spark.
python -m scripts.package_emr
# Choisit une destination neuve et limite le nombre de threads TensorFlow/BLAS.
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 TF_NUM_INTRAOP_THREADS=1 TF_NUM_INTEROP_THREADS=1
run_id="$(date -u +%Y%m%dT%H%M%SZ)"
# Exécute le véritable pipeline Spark sur deux threads locaux ; cela ne prouve pas un cluster multi-machine.
spark-submit --master 'local[2]' --driver-memory 4g \
  --py-files dist/p9_src.zip dist/run_pipeline.py \
  --input data/sample-v2 --output "outputs/spark-${run_id}" \
  --max-images 100 --components 20 --batch-size 8 --partitions 2
```

`--max-images 0` traite toutes les images : n'utiliser cette option qu'après un petit run réussi.
Pour un grand dataset, `limit` ne produit pas un échantillon aléatoire ou équilibré ; utiliser un échantillon
préparé séparément pour comparer les mesures. La redistribution après la limite restaure plusieurs partitions.

## Test d'intégration sans télécharger ImageNet (facultatif)

```bash
# Teste le vrai code Spark avec ResNet50 à poids aléatoires et images synthétiques ; aucune valeur métier.
P9_RUN_SPARK_TEST=1 PYSPARK_SUBMIT_ARGS='--master local[2] --driver-memory 4g pyspark-shell' \
  OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 TF_NUM_INTRAOP_THREADS=1 TF_NUM_INTEROP_THREADS=1 \
  python -m unittest tests.test_spark_integration -v
```

## Transférer et exécuter sur EMR après validation du budget

```bash
# Définit le bucket et le préfixe du code déjà préparés dans la région européenne retenue.
export P9_BUCKET='NOM-DU-BUCKET'
export P9_CODE_PREFIX='code/COMMIT-VERIFIE'
# Transfère code et petit échantillon sans supprimer les objets existants.
aws s3 cp dist/ "s3://${P9_BUCKET}/${P9_CODE_PREFIX}/" --recursive
aws s3 cp data/sample-v2/ "s3://${P9_BUCKET}/data/sample-v2/" --recursive
```

La commande suivante se lance **sur le primaire EMR après réussite du bootstrap**, avec les fichiers
`dist/` récupérés. Pour une étape EMR, fournir les mêmes arguments à `command-runner.jar`.

```bash
# Récupère l'archive Python et le lanceur provenant du même préfixe de code.
aws s3 cp "s3://${P9_BUCKET}/${P9_CODE_PREFIX}/" ./p9-code/ --recursive
# Fixe le même interpréteur isolé pour le driver et les executors.
export PYSPARK_PYTHON=/opt/p9-venv/bin/python
export PYSPARK_DRIVER_PYTHON=/opt/p9-venv/bin/python
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 TF_NUM_INTRAOP_THREADS=1 TF_NUM_INTEROP_THREADS=1
run_id="$(date -u +%Y%m%dT%H%M%SZ)"
# Deux executors mono-cœur limitent la concurrence TensorFlow ; ajuster la mémoire au cluster réel.
spark-submit --master yarn --deploy-mode client \
  --conf spark.dynamicAllocation.enabled=false \
  --num-executors 2 --executor-cores 1 --executor-memory 3g --driver-memory 4g \
  --conf spark.executor.memoryOverhead=3g \
  --conf spark.pyspark.python=/opt/p9-venv/bin/python \
  --conf spark.executorEnv.OMP_NUM_THREADS=1 \
  --conf spark.executorEnv.OPENBLAS_NUM_THREADS=1 \
  --conf spark.executorEnv.TF_NUM_INTRAOP_THREADS=1 \
  --conf spark.executorEnv.TF_NUM_INTEROP_THREADS=1 \
  --py-files p9-code/p9_src.zip p9-code/run_pipeline.py \
  --input "s3://${P9_BUCKET}/data/sample-v2/" \
  --output "s3://${P9_BUCKET}/runs/${run_id}" \
  --max-images 100 --components 20 --batch-size 8 --partitions 4
```

La sortie contient `data/` (Parquet), `centering_model/`, `pca_model/` et `metrics/`.
Le `_SUCCESS` de **metrics/** est écrit en dernier, après relecture et validation des données.
Une sortie partielle sans métriques validées ne doit pas être présentée comme une exécution réussie.
Deux executors ne garantissent pas deux machines : vérifier `worker_hosts` et la Spark UI.
