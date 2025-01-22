import unittest
import sys
import os

# Ajouter le répertoire racine au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import horodatage, enlever_accents


class TestUtils(unittest.TestCase):
    def test_horodatage(self):
        result = horodatage()
        self.assertIsInstance(result, str)
        self.assertRegex(result, r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")

    def test_enlever_accents(self):
        self.assertEqual(enlever_accents("éàç"), "eac")


if __name__ == "__main__":
    unittest.main()
