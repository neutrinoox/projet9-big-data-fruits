# Installation locale

Prérequis : Python 3.10 à 3.12, Java 17, espace disque suffisant pour TensorFlow, Spark et le dataset.
La version Python des workers doit être la même que celle du driver.

```bash
# Crée un environnement isolé, puis l'active sous Linux/macOS.
python -m venv .venv
source .venv/bin/activate
# Installe les versions directes communes au projet et vérifie les dépendances.
python -m pip install -r requirements.txt
python -m pip check
# Vérifie Java, Python et le comportement de la préparation des données.
java -version
python --version
python -m unittest discover -v
```

Sous Windows, activer `.venv\Scripts\activate` ; pour Spark, privilégier Colab ou Linux si la configuration
Java/Hadoop locale bloque. Le notebook fournit un parcours Colab qui exécute les calculs dans des
sous-processus frais après installation des dépendances, afin d'éviter les anciens imports TensorFlow.

La copie du dataset se fait avec un dossier Training explicitement choisi. Voir `commands.md`.
Sur EMR, utiliser uniquement le bootstrap et `requirements-emr.txt` : ne pas remplacer le Spark fourni par AWS.
