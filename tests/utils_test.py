import unittest
import sys
import os

# Ajouter le répertoire racine au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import horodatage, enlever_accents, tronquer_nom_fichier


class TestUtils(unittest.TestCase):
    def test_horodatage(self):
        result = horodatage()
        self.assertIsInstance(result, str)
        self.assertRegex(result, r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")

    def test_enlever_accents(self):
        self.assertEqual(enlever_accents("éàçAB"), "eacab")

    def test_tronquer_nom_fichier_short(self):
        nom_fichier = "short_filename.txt"
        result = tronquer_nom_fichier(nom_fichier)
        self.assertEqual(result, nom_fichier)

    def test_tronquer_nom_fichier_exact_length(self):
        nom_fichier = "a" * 40 + "b" * 20
        result = tronquer_nom_fichier(nom_fichier)
        self.assertEqual(result, nom_fichier)

    def test_tronquer_nom_fichier_long(self):
        nom_fichier = "a" * 50 + "b" * 30
        result = tronquer_nom_fichier(nom_fichier)
        expected = "a" * 40 + "..." + "b" * 20
        self.assertEqual(result, expected)

    def test_tronquer_nom_fichier_custom_debut_fin(self):
        nom_fichier = "a" * 50 + "b" * 30
        result = tronquer_nom_fichier(nom_fichier, debut=10, fin=10)
        expected = "a" * 10 + "..." + "b" * 10
        self.assertEqual(result, expected)

    def test_tronquer_nom_fichier_no_truncation_needed(self):
        nom_fichier = "a" * 30 + "b" * 10
        result = tronquer_nom_fichier(nom_fichier, debut=40, fin=20)
        self.assertEqual(result, nom_fichier)

    def test_tronquer_nom_fichier_avec_espaces(self):
        nom_fichier = " " * 5 + "a" * 39 + " test " + "b" * 19 + " " * 5
        result = tronquer_nom_fichier(nom_fichier)
        expected = "a" * 39 + "..." + "b" * 19
        self.assertEqual(result, expected)

    def test_tronquer_nom_fichier_avec_espaces_custom_debut_fin(self):
        nom_fichier = " " * 5 + "a" * 50 + "b" * 30 + " " * 5
        result = tronquer_nom_fichier(nom_fichier, debut=10, fin=10)
        expected = "a" * 10 + "..." + "b" * 10
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
