# Installation locale

## Objectif

Cette page explique comment lancer le projet sur ton ordinateur avant AWS.

## 1. Recuperer le projet

```bash
git clone https://github.com/neutrinoox/projet9-big-data-fruits.git
cd projet9-big-data-fruits
```

## 2. Creer un environnement Python

```bash
python -m venv .venv
```

Activation Windows :

```bash
.venv\Scripts\activate
```

Activation Mac/Linux :

```bash
source .venv/bin/activate
```

## 3. Installer les dependances

```bash
pip install -r requirements.txt
```

## 4. Ajouter le dataset

Le dataset doit etre place ici :

```text
data/fruits/
```

Ce dossier est ignore par GitHub.

## 5. Tester le pipeline local

```bash
python -m src.pipeline_local
```

Si tout fonctionne, un fichier sera cree :

```text
outputs/sample_features.csv
```
