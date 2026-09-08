"""Tests de régression des pertes de fichiers et des protections du dataset."""

# Utilise exclusivement des fichiers factices dans des dossiers temporaires.
import json
import tempfile
import unittest
from pathlib import Path
from scripts.prepare_sample import prepare_sample, MARKER
from src.validate_dataset import select_balanced_images

class SampleSafetyTest(unittest.TestCase):
    # Vérifie que Training/Apple/1.jpg et Test/Apple/1.jpg restent distincts.
    def test_identical_names_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for split in ('Training', 'Test'):
                source = root / 'source' / split / 'Apple'
                source.mkdir(parents=True)
                (source / '1.jpg').write_text(split)
            result = prepare_sample(root / 'source', root / 'sample', 2, 1)
            files = list((root / 'sample').rglob('*.jpg'))
            self.assertEqual(result['actual_images'], len(files))
            self.assertEqual({p.read_text() for p in files}, {'Training', 'Test'})
            self.assertEqual(len({r['sha256'] for r in result['files']}), 2)

    # Refuse les dossiers imbriqués dans les deux sens avant toute suppression.
    def test_related_paths_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'source'
            source.mkdir()
            sentinel = source / '1.jpg'
            sentinel.write_text('original')
            for output in (root, source, source / 'nested'):
                with self.assertRaises(ValueError):
                    prepare_sample(source, output)
                self.assertEqual(sentinel.read_text(), 'original')

    # Protège tout dossier existant qui n'a pas été créé par cet outil.
    def test_unowned_output_preserved(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, output = root / 'source', root / 'output'
            source.mkdir()
            output.mkdir()
            (source / '1.jpg').write_text('image')
            (output / 'important.txt').write_text('conserver')
            with self.assertRaises(ValueError):
                prepare_sample(source, output)
            self.assertEqual((output / 'important.txt').read_text(), 'conserver')

    # Remplace un échantillon identifié et conserve sa dernière version si la nouvelle source est vide.
    def test_repeat_and_failure_preserve_previous(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'source' / 'Apple'
            source.mkdir(parents=True)
            image = source / '1.jpg'
            image.write_text('first')
            output = root / 'sample'
            prepare_sample(source.parent, output, 1, 1)
            image.write_text('second')
            prepare_sample(source.parent, output, 1, 1)
            image.unlink()
            with self.assertRaises(FileNotFoundError):
                prepare_sample(source.parent, output, 1, 1)
            self.assertEqual((output / 'Apple' / '1.jpg').read_text(), 'second')
            self.assertEqual(json.loads((output / MARKER).read_text())['actual_images'], 1)

    # Refuse les paramètres sans signification au lieu de produire un échantillon vide.
    def test_invalid_sizes(self):
        for images, classes in ((0, 10), (-1, 2), (2, 0)):
            with self.assertRaises(ValueError):
                select_balanced_images([], images, classes)

# Autorise l'exécution autonome des tests.
if __name__ == '__main__':
    unittest.main()
