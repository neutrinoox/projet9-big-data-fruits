"""Prépare un échantillon traçable sans écrasement de noms ni suppression des sources."""

# Charge les outils de copie, d'empreinte et de préparation transactionnelle.
import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from src.validate_dataset import find_images, select_balanced_images

MARKER = '_sample_manifest.json'

# Prépare entièrement la nouvelle copie avant de remplacer un échantillon identifié.
def prepare_sample(input_path, output_path, images=100, classes=10):
    source_root = Path(input_path).resolve()
    raw_output = Path(output_path)
    output_root = raw_output.resolve()
    if raw_output.is_symlink():
        raise ValueError('La sortie ne doit pas être un lien symbolique.')
    if (source_root == output_root or source_root in output_root.parents
            or output_root in source_root.parents):
        raise ValueError('Les dossiers source et sortie ne doivent pas être imbriqués.')
    if output_root.exists():
        marker = output_root / MARKER
        if not marker.is_file() or json.loads(marker.read_text()).get('generator') != 'p9.prepare_sample.v2':
            raise ValueError('Sortie existante non identifiée : choisissez un nouveau dossier.')
    selected = select_balanced_images(find_images(source_root), images, classes)
    output_root.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.p9-sample-', dir=output_root.parent))
    backup = None
    try:
        # Conserve les chemins relatifs pour distinguer les fichiers homonymes.
        records = []
        for source in selected:
            if not source.resolve().is_relative_to(source_root):
                raise ValueError('Une image pointe hors du dossier source.')
            relative = source.relative_to(source_root)
            destination = stage / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            records.append({'path': relative.as_posix(), 'label': source.parent.name,
                            'sha256': hashlib.sha256(destination.read_bytes()).hexdigest()})
        if len(find_images(stage)) != len(records):
            raise RuntimeError('Le nombre de fichiers copiés diffère de la sélection.')
        manifest = {'generator': 'p9.prepare_sample.v2', 'source': str(source_root),
                    'requested_images': images, 'actual_images': len(records),
                    'classes': len({r['label'] for r in records}), 'files': records}
        (stage / MARKER).write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
        # Garde l'ancien échantillon jusqu'à ce que le remplacement ait réussi.
        if output_root.exists():
            backup = Path(tempfile.mkdtemp(prefix='.p9-backup-', dir=output_root.parent))
            backup.rmdir()
            output_root.rename(backup)
        try:
            stage.rename(output_root)
        except Exception:
            if backup is not None:
                backup.rename(output_root)
            raise
        if backup is not None:
            shutil.rmtree(backup)
        return manifest
    finally:
        if stage.exists():
            shutil.rmtree(stage)

# Expose le dossier Training explicitement choisi et la taille du prototype.
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, help='Dossier Training de la variante Fruits-360 retenue')
    parser.add_argument('--output', default='data/sample-v2')
    parser.add_argument('--images', type=int, default=100)
    parser.add_argument('--classes', type=int, default=10)
    args = parser.parse_args()
    manifest = prepare_sample(args.input, args.output, args.images, args.classes)
    print(f"Échantillon vérifié : {manifest['actual_images']} images, {manifest['classes']} classes")

# Permet l'exécution avec python -m scripts.prepare_sample.
if __name__ == '__main__':
    main()
