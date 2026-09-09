"""Télécharge 100 images officielles Fruits-360, fixées à un commit et vérifiées par empreinte."""

# Utilise le manifeste du dépôt : aucun appel à une API payante ni authentification Kaggle.
import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen

# Refuse de toucher un dossier existant ; publie seulement un téléchargement complet et vérifié.
def download_sample(output_path):
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / 'docs/fruits_validation_manifest.json').read_text())
    output = Path(output_path).resolve()
    if output.exists():
        raise FileExistsError(f'Dossier existant : {output}. Réutilisez-le ou choisissez un nouveau chemin.')
    output.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.p9-download-', dir=output.parent))
    try:
        # Chaque fichier est rattaché au commit source, jamais à une branche mouvante.
        for record in manifest['images']:
            relative = Path(record['path'])
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('Chemin non sûr dans le manifeste.')
            url = f"https://raw.githubusercontent.com/{manifest['repository']}/{manifest['revision']}/{quote(record['path'], safe='/')}"
            with urlopen(url, timeout=60) as response:
                data = response.read(10_000_001)
            if len(data) > 10_000_000:
                raise ValueError('Image anormalement volumineuse.')
            git_hash = hashlib.sha1(f'blob {len(data)}\0'.encode() + data).hexdigest()
            if git_hash != record['git_blob_sha']:
                raise ValueError(f"Empreinte source incorrecte : {record['path']}")
            destination = stage / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
        (stage / '_source_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
        stage.rename(output)
    finally:
        if stage.exists():
            shutil.rmtree(stage)
    print(f"100 images vérifiées : {output / 'Training'} ; commit source {manifest['revision']}")

# Permet un petit téléchargement reproductible à la place du dataset Kaggle complet pour les tests.
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='data/fruits-validation')
    args = parser.parse_args()
    download_sample(args.output)

# Lance le téléchargement seulement à l'appel explicite du script.
if __name__ == '__main__':
    main()
