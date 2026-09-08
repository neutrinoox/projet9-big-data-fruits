"""Valide les 100 images officielles avec le vrai pipeline et en conserve les preuves."""

# Orchestre téléchargement vérifié, préparation sûre et exécution Spark dans un même run traçable.
import json
import shutil
import subprocess
from pathlib import Path
from scripts.download_validation_sample import download_sample
from scripts.prepare_sample import prepare_sample

# Exécute un run de validation ; les résultats restent distincts des preuves cloud EMR.
def main():
    root = Path(__file__).resolve().parents[1]
    source = root / 'data/fruits-validation'
    sample = root / 'data/sample-ci'
    output = root / 'outputs/real-fruits'
    download_sample(source)
    manifest = prepare_sample(source / 'Training', sample, 100, 10)
    assert manifest['actual_images'] == 100 and manifest['classes'] == 10
    from src.pipeline_spark import run_pipeline
    result = run_pipeline(str(sample), str(output), 100, 20, 8, partitions=2)
    assert result['images'] == 100 and result['components'] == 20
    assert result['active_partitions'] == 2 and len(result['label_counts']) == 10
    # Conserve la provenance des images et le commit du code avec les résultats du calcul.
    shutil.copy2(sample / '_sample_manifest.json', output / 'sample_manifest.json')
    shutil.copy2(source / '_source_manifest.json', output / 'source_manifest.json')
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    (output / 'code_commit.txt').write_text(revision)
    print(json.dumps({'validation': 'real_fruits_passed', 'commit': revision,
                      'images': result['images'], 'components': result['components'],
                      'explained_variance': result['explained_variance']}, indent=2))

# Lance la validation complète uniquement sur demande explicite.
if __name__ == '__main__':
    main()
