import unittest
import sys
import os
import json

# Ajouter le répertoire racine au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from file_handling import charger_fichiers


class TestFileHandling(unittest.TestCase):

    def setUp(self):
        self.test_file = "test_file.json"
        self.test_data = {"key": "value"}

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_charger_fichiers_file_exists(self):
        with open(self.test_file, "w") as f:
            json.dump(self.test_data, f)

        result = charger_fichiers(self.test_file)
        self.assertEqual(result, self.test_data)

    def test_charger_fichiers_file_does_not_exist(self):
        result = charger_fichiers("non_existent_file.json")
        self.assertEqual(result, {})


if __name__ == "__main__":
    unittest.main()
