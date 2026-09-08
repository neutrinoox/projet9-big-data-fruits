"""Test opt-in du vrai pipeline Spark/ResNet50 sur des images synthétiques, sans téléchargement."""

# Le test est explicite car il consomme plusieurs minutes et nécessite Java, Spark et TensorFlow.
import os
import tempfile
import shutil
import unittest
from pathlib import Path

@unittest.skipUnless(os.environ.get('P9_RUN_SPARK_TEST') == '1', 'Test Spark opt-in : P9_RUN_SPARK_TEST=1')
class SparkIntegrationTest(unittest.TestCase):
    # Vérifie calcul multi-partitions, PCA, relecture et refus d'écrasement avec des poids aléatoires.
    def test_pipeline_and_output_protection(self):
        import numpy as np
        from PIL import Image
        from src.pipeline_spark import run_pipeline
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for index in range(8):
                folder = root / 'images' / ('Apple' if index < 4 else 'Banana')
                folder.mkdir(parents=True, exist_ok=True)
                pixels = np.random.default_rng(index).integers(0, 256, (64, 64, 3), dtype=np.uint8)
                Image.fromarray(pixels).save(folder / f'{index}.png')
            output = str(root / 'run')
            result = run_pipeline(str(root / 'images'), output, 8, 3, 2, partitions=2, weights=os.environ.get('P9_TEST_WEIGHTS') or None)
            self.assertEqual(result['images'], 8)
            self.assertEqual(result['components'], 3)
            self.assertEqual(result['active_partitions'], 2)
            self.assertGreater(result['explained_variance'], 0)
            self.assertTrue((root / 'run' / 'metrics' / '_SUCCESS').exists())
            # Conserve les sorties du smoke test si un dossier de preuves est demandé.
            evidence = os.environ.get('P9_TEST_EVIDENCE')
            if evidence:
                shutil.copytree(root / 'run', evidence)
            with self.assertRaises(FileExistsError):
                run_pipeline(str(root / 'images'), output, 8, 3, 2)

# Permet un lancement direct après activation explicite du test.
if __name__ == '__main__':
    unittest.main()
