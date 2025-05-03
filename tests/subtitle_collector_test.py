import os
import json
import unittest
import shutil
from unittest.mock import patch, mock_open
import tempfile
import sys

# Ajouter le dossier parent au chemin pour pouvoir importer le module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from subtitle_collector import (
    SubtitleTitleCollector,
    collect_subtitle_title,
    get_data_dir,
)


class TestSubtitleCollector(unittest.TestCase):

    def setUp(self):
        """Configuration avant chaque test"""
        # Créer un dossier temporaire pour les tests
        self.test_dir = tempfile.mkdtemp()

        # Patcher la fonction get_data_dir pour qu'elle retourne notre dossier de test
        self.patcher = patch(
            "subtitle_collector.get_data_dir", return_value=self.test_dir
        )
        self.mock_get_data_dir = self.patcher.start()

        # Chemin du fichier de collection de test
        self.test_collection_file = os.path.join(self.test_dir, "test_collection.json")

        # Données de test
        self.sample_title = "français"
        self.sample_language = "fra"
        self.sample_info = {
            "StreamSize": "12345",
            "ElementCount": "678",
            "Duration": "3600.0",
            "Forced": "No",
            "Default": "Yes",
        }

    def tearDown(self):
        """Nettoyage après chaque test"""
        self.patcher.stop()
        shutil.rmtree(self.test_dir)

    def test_get_data_dir_creates_directory(self):
        """Tester que get_data_dir crée le dossier s'il n'existe pas"""
        # Restaurer le comportement original
        self.patcher.stop()

        # Supprimer le dossier data s'il existe
        data_dir_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "datas"
        )
        if os.path.exists(data_dir_path):
            os.rename(data_dir_path, f"{data_dir_path}_backup")

        try:
            # Appeler la fonction
            data_dir = get_data_dir()

            # Vérifier que le dossier existe maintenant
            self.assertTrue(os.path.exists(data_dir))
            self.assertEqual(data_dir, data_dir_path)
        finally:
            # Restaurer le dossier original s'il existait
            if os.path.exists(f"{data_dir_path}_backup"):
                if os.path.exists(data_dir_path):
                    os.rmdir(data_dir_path)
                os.rename(f"{data_dir_path}_backup", data_dir_path)

        # Remettre le patch en place pour les autres tests
        self.patcher = patch(
            "subtitle_collector.get_data_dir", return_value=self.test_dir
        )
        self.mock_get_data_dir = self.patcher.start()

    def test_collector_initialization_empty_file(self):
        """Tester l'initialisation du collecteur avec un fichier inexistant"""
        collector = SubtitleTitleCollector("test_collection.json")

        # Vérifier que le fichier est correct
        self.assertEqual(collector.collection_file, self.test_collection_file)

        # Vérifier la structure de données
        self.assertEqual(collector.titles["titles"], [])
        self.assertIn("metadata", collector.titles)
        self.assertIn("last_updated", collector.titles["metadata"])

    def test_collector_initialization_existing_file(self):
        """Tester l'initialisation du collecteur avec un fichier existant"""
        # Créer un fichier de collection existant
        existing_data = {
            "titles": [{"title": "test", "language": "eng"}],
            "metadata": {"last_updated": "2025-05-01"},
        }
        with open(self.test_collection_file, "w", encoding="utf-8") as f:
            json.dump(existing_data, f)

        collector = SubtitleTitleCollector("test_collection.json")

        # Vérifier que les données sont chargées
        self.assertEqual(len(collector.titles["titles"]), 1)
        self.assertEqual(collector.titles["titles"][0]["title"], "test")

    def test_save_new_title(self):
        """Tester la sauvegarde d'un nouveau titre de sous-titre"""
        collector = SubtitleTitleCollector("test_collection.json")

        # Sauvegarder un nouveau titre
        result = collector.save_title(
            self.sample_title, self.sample_language, self.sample_info
        )

        # Vérifier le résultat
        self.assertTrue(result)
        self.assertEqual(len(collector.titles["titles"]), 1)
        self.assertEqual(collector.titles["titles"][0]["title"], self.sample_title)
        self.assertEqual(
            collector.titles["titles"][0]["language"], self.sample_language
        )

        # Vérifier que le fichier a été créé
        self.assertTrue(os.path.exists(self.test_collection_file))

        # Vérifier le contenu du fichier
        with open(self.test_collection_file, "r", encoding="utf-8") as f:
            saved_data = json.load(f)

        self.assertEqual(saved_data["titles"][0]["title"], self.sample_title)

    def test_skip_duplicate_title(self):
        """Tester que les titres en double sont ignorés"""
        collector = SubtitleTitleCollector("test_collection.json")

        # Sauvegarder un titre
        collector.save_title(self.sample_title, self.sample_language, self.sample_info)

        # Taille initiale de la collection
        initial_size = len(collector.titles["titles"])

        # Essayer de sauvegarder le même titre
        result = collector.save_title(
            self.sample_title, self.sample_language, self.sample_info
        )

        # Vérifier que le titre n'a pas été ajouté
        self.assertFalse(result)
        self.assertEqual(len(collector.titles["titles"]), initial_size)

    def test_case_insensitive_comparison(self):
        """Tester que la comparaison des titres est insensible à la casse"""
        collector = SubtitleTitleCollector("test_collection.json")

        # Sauvegarder un titre en minuscules
        collector.save_title("français", self.sample_language, self.sample_info)

        # Essayer de sauvegarder le même titre en majuscules
        result = collector.save_title(
            "FRANÇAIS", self.sample_language, self.sample_info
        )

        # Vérifier que le titre n'a pas été ajouté
        self.assertFalse(result)
        self.assertEqual(len(collector.titles["titles"]), 1)

    def test_empty_title(self):
        """Tester le comportement avec un titre vide"""
        collector = SubtitleTitleCollector("test_collection.json")

        # Essayer de sauvegarder un titre vide
        result = collector.save_title("", self.sample_language, self.sample_info)

        # Vérifier que le titre n'a pas été ajouté
        self.assertFalse(result)
        self.assertEqual(len(collector.titles["titles"]), 0)

    def test_collect_subtitle_title_function(self):
        """Tester la fonction pratique collect_subtitle_title"""
        # Appeler la fonction
        result = collect_subtitle_title(
            self.sample_title,
            self.sample_language,
            self.sample_info,
            collection_filename="test_collection.json",
        )

        # Vérifier que le titre a été ajouté
        self.assertTrue(result)

        # Vérifier que le fichier a été créé
        self.assertTrue(os.path.exists(self.test_collection_file))

        # Vérifier le contenu du fichier
        with open(self.test_collection_file, "r", encoding="utf-8") as f:
            saved_data = json.load(f)

        self.assertEqual(saved_data["titles"][0]["title"], self.sample_title)

    @patch("json.dump")
    def test_error_handling_during_save(self, mock_json_dump):
        """Tester la gestion des erreurs pendant la sauvegarde"""
        # Configurer le mock pour lever une exception
        mock_json_dump.side_effect = Exception("Erreur de sauvegarde")

        # Créer le collecteur et tenter de sauvegarder
        collector = SubtitleTitleCollector("test_collection.json")
        result = collector.save_title(
            self.sample_title, self.sample_language, self.sample_info
        )

        # Vérifier que le résultat indique l'échec
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
