"""Tests rapides ne nécessitant ni TensorFlow ni Spark."""

import tempfile
import unittest
from pathlib import Path

from src.validate_dataset import find_images, select_balanced_images


class DatasetUtilsTest(unittest.TestCase):
    def test_find_and_balance_images(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for label, count in {"Apple": 3, "Banana": 2}.items():
                folder = root / label
                folder.mkdir()
                for index in range(count):
                    (folder / f"{index}.jpg").touch()
            (root / "notes.txt").touch()

            images = find_images(root)
            sample = select_balanced_images(images, 4)

            self.assertEqual(len(images), 5)
            self.assertEqual(len(sample), 4)
            self.assertEqual({path.parent.name for path in sample}, {"Apple", "Banana"})


if __name__ == "__main__":
    unittest.main()
