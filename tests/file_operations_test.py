import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import sys
import subprocess

# Ajouter le répertoire racine au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from file_operations import (
    obtenir_pistes,
    verifier_dossiers,
)
from constants import dossier_encodage_manuel, dossier_sortie
from utils import horodatage


class TestFileOperations(unittest.TestCase):

    @patch("subprocess.run")
    def test_obtenir_pistes_success(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0, stdout='JSON Title Set: {"title": "test"}'
        )
        result = obtenir_pistes("dummy_path")
        self.assertIsNotNone(result)
        self.assertIn("title", result)

    @patch("subprocess.run")
    def test_obtenir_pistes_failure(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stderr="Error")
        result = obtenir_pistes("dummy_path")
        self.assertIsNone(result)

    @patch("subprocess.run")
    def test_obtenir_pistes_empty_output(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="")
        result = obtenir_pistes("dummy_path")
        self.assertIsNone(result)

    @patch("os.makedirs")
    @patch("os.path.exists", return_value=False)
    def test_verifier_dossiers_creation(self, mock_exists, mock_makedirs):
        verifier_dossiers()
        mock_makedirs.assert_any_call(dossier_sortie)
        mock_makedirs.assert_any_call(dossier_encodage_manuel)

    @patch("os.makedirs")
    @patch("os.path.exists", return_value=True)
    def test_verifier_dossiers_no_creation(self, mock_exists, mock_makedirs):
        verifier_dossiers()
        mock_makedirs.assert_not_called()


if __name__ == "__main__":
    unittest.main()
