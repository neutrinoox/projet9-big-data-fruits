#!/bin/bash
# Interrompt immédiatement le bootstrap si un téléchargement ou une installation échoue.
set -euo pipefail

# Reçoit le fichier de versions depuis S3 ; aucune dépendance n'est dupliquée dans ce script.
requirements_uri="${1:?Indiquer s3://bucket/code/requirements-emr.txt}"
case "$requirements_uri" in
  s3://*) ;;
  *) echo 'Le fichier de dépendances doit être sur S3.' >&2; exit 2 ;;
esac

# Vérifie la présence de Python 3.11, prévu par la version EMR documentée.
command -v python3.11 >/dev/null
requirements_local="$(mktemp /tmp/p9-requirements.XXXXXX)"
trap 'rm -f "$requirements_local"' EXIT
aws s3 cp "$requirements_uri" "$requirements_local"

# Isole les dépendances du projet pour préserver le Python système d'EMR.
sudo python3.11 -m venv /opt/p9-venv
sudo /opt/p9-venv/bin/python -m pip install -r "$requirements_local"
sudo /opt/p9-venv/bin/python -m pip check
sudo /opt/p9-venv/bin/python -c 'import tensorflow, numpy, pandas, PIL; print(tensorflow.__version__, numpy.__version__)'
