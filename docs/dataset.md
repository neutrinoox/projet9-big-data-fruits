# Dataset du projet

## Point important

Le dataset ne doit pas etre stocke dans GitHub.

Pourquoi ?

- Les images sont trop nombreuses et trop lourdes.
- GitHub n'est pas fait pour stocker des jeux de donnees volumineux.
- Pour le projet P9, le bon stockage est AWS S3.

## Dataset vise

Le projet est prepare pour le dataset Fruits-360.

Organisation attendue :

```text
data/fruits/
├── Training/
│   ├── Apple .../
│   ├── Banana .../
│   └── ...
└── Test/
    ├── Apple .../
    ├── Banana .../
    └── ...
```

Chaque sous-dossier represente une classe de fruit.

## Utilisation dans le pipeline

Le pipeline doit :

1. lire les images ;
2. recuperer le label depuis le nom du dossier ;
3. extraire un vecteur de features avec un CNN ;
4. appliquer une PCA ;
5. sauvegarder les resultats en Parquet.

## Etape AWS

Quand le dataset sera telecharge, il faudra l'envoyer dans S3, par exemple :

```bash
aws s3 sync data/fruits/ s3://TON-BUCKET-P9/data/fruits/
```
