"""Construit une archive des modules Python et un lanceur pour spark-submit."""

# Sélectionne uniquement le code du projet, sans données ni secrets.
import hashlib
import json
import shutil
import subprocess
import zipfile
from pathlib import Path

# Prépare les fichiers à transférer sur S3 pour une exécution EMR.
def main():
    root = Path(__file__).resolve().parents[1]
    target = root / 'dist'
    target.mkdir(exist_ok=True)
    archive = target / 'p9_src.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted((root / 'src').glob('*.py')):
            bundle.write(path, path.relative_to(root))
    launcher = '# Lance le pipeline provenant de l’archive distribuée avec --py-files.\nfrom src.pipeline_spark import main\n\nif __name__ == "__main__":\n    main()\n'
    (target / 'run_pipeline.py').write_text(launcher)
    shutil.copy2(root / 'requirements-emr.txt', target)
    shutil.copy2(root / 'bootstrap/install_emr_dependencies.sh', target)
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    dirty = bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=root, text=True).strip())
    manifest = {'git_commit': revision, 'working_tree_dirty': dirty,
                'sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                           for p in sorted(target.iterdir()) if p.is_file() and p.name != 'manifest.json'}}
    (target / 'manifest.json').write_text(json.dumps(manifest, indent=2))
    print(f'Archive prête : {archive} ; commit {revision} ; modifications locales : {dirty}')

# Permet de reconstruire le paquet avec python -m scripts.package_emr.
if __name__ == '__main__':
    main()
