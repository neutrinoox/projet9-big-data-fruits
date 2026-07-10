#!/bin/bash

# Arrete le script des qu'une commande echoue.
set -e

# Met pip a jour pour eviter des problemes d'installation.
sudo python3 -m pip install --upgrade pip

# Installe les bibliotheques necessaires sur chaque noeud EMR.
sudo python3 -m pip install \
  pandas>=2.0.0 \
  numpy>=1.24.0 \
  pillow>=10.0.0 \
  pyarrow>=14.0.0 \
  tensorflow-cpu>=2.15.0

echo "Dependances EMR installees avec succes."
