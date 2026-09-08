# Préparation de la soutenance P9

Ce document prépare les explications. Il ne prétend pas que l'exécution AWS a déjà eu lieu.

## Fil de présentation

1. **Besoin Fruits!** : préparer une chaîne d'images capable de passer à l'échelle ; aucun
   classificateur entraîné à ce stade.
2. **Données** : variante Fruits-360 et split Training choisis explicitement ; sélection de 100 images
   et 10 classes pour commencer ; manifeste, empreintes et nombre de fichiers réellement copiés.
3. **Architecture** : S3 stocke, EMR configure le calcul, YARN alloue les ressources, Spark distribue,
   IAM contrôle les accès. Montrer le chemin complet des entrées jusqu'aux sorties.
4. **Extraction** : RGB et 224×224, preprocessing ResNet50 officiel ; réseau ImageNet sans tête,
   pooling moyen donnant 2 048 caractéristiques. Les labels ne sont pas utilisés pour entraîner le CNN.
5. **Distribution** : le driver charge les poids ; broadcast, modèle construit par partition non vide,
   traitement par lots ; threads limités pour éviter la surallocation CPU/mémoire.
6. **Réduction** : centrage sans normalisation de variance puis PCA Spark. Justifier k par la courbe
   de variance et le compromis stockage/information, pas seulement par le chiffre 20 choisi pour le test.
7. **Résultats** : montrer uniquement les métriques du run présenté, la relecture des fichiers,
   les durées, partitions et hôtes ; distinguer test local et exécution EMR.
8. **Limites et coût** : petit échantillon, consommation mémoire et poids de l'inférence, coût des
   échanges de données, coût de la PCA ; configuration européenne, arrêt du cluster et coût observé.

## Questions probables et idées à maîtriser

| Question | Réponse à comprendre |
|---|---|
| Pourquoi Spark pour 100 images ? | Le petit lot valide le pipeline. Le besoin cible est une croissance de volume ; le gain de vitesse n'est pas garanti sur un petit lot. |
| Pourquoi ResNet50 ? | Extracteur pré-entraîné disponible et réutilisable ; il transforme les pixels en caractéristiques. Ce n'est pas ici un classificateur Fruits-360 entraîné. |
| Pourquoi broadcast ? | Les mêmes poids sont réutilisés par les tâches ; Spark organise leur diffusion et évite de les joindre à chaque ligne. |
| Un modèle par image ? | Non, un modèle par partition non vide, puis plusieurs lots ; trop de petites partitions provoquent trop de chargements. |
| Deux partitions prouvent-elles deux machines ? | Non : il faut regarder les hôtes et les executors dans les métriques et la Spark UI. |
| Pourquoi repartition après limit ? | Pour redistribuer l'échantillon avant l'étape coûteuse ; cela a aussi un coût réseau. |
| Pourquoi cache/persist ? | Les mêmes features servent à la validation, au centrage et à la PCA. MEMORY_AND_DISK réduit les recalculs, sans garantir l'absence de recalcul en cas de perte de worker. |
| Pourquoi centrer ? | La PCA s'appuie sur les variations autour de la moyenne. Le centrage explicite rend les coordonnées comparables à sklearn, à un signe près. |
| Pourquoi ne pas standardiser chaque feature ? | Ce choix conserve les échelles des activations CNN ; il doit être expliqué et peut être comparé si pertinent. |
| Que signifie 96,62 % ? | C'était la variance cumulée observée dans l'ancien prototype local, avec 20 composantes. Ce n'est ni une accuracy ni un résultat AWS, et les nouveaux résultats peuvent changer. |
| Que signifie (100, 3) ? | 100 lignes et trois colonnes du DataFrame ; chaque cellule pca_features contient un vecteur de k composantes. |
| Quelles limites à l'échelle ? | I/O des images, mémoire des modèles par worker, nombre de tâches et shuffles ; la PCA sur 2 048 variables conserve un coût en dimension même si les images sont distribuées. |
| Comment reproduire ? | Commit/empreinte de l'archive, manifestes des images, versions des paquets, paramètres et modèles sauvegardés. |
| Pourquoi une région européenne ? | Pour satisfaire la contrainte géographique explicite du scénario ; cela ne démontre pas toute la conformité RGPD à soi seul. |
| Pourquoi arrêter EMR ? | Les machines actives coûtent même hors calcul ; S3 et certaines ressources peuvent encore coûter après l'arrêt du cluster. |

## Captures et démonstration

Préparer le petit run, les métriques JSON et le Parquet relu, les pages executors/stages de Spark,
les régions S3/EMR, les statuts de succès et d'arrêt. Ne jamais afficher de secrets.
Expliquer un échec et son diagnostic si pertinent ; ne pas effacer l'historique pour inventer une réussite.
Les captures ne remplacent une démonstration en direct que si les modalités OC le permettent.
