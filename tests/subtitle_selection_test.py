"""
Module de tests unitaires pour l'analyse des sous-titres et l'interaction avec MediaInfo.
Ce module contient deux classes principales de tests :
1. `TestSubtitleAnalyzer` : Teste les fonctionnalités d'analyse des sous-titres pour différents
    scénarios et presets.
2. `TestMediaInfoFunctions` : Teste les fonctions qui interagissent avec l'outil MediaInfo,
    notamment la récupération des métadonnées des fichiers multimédias.
----------
- `TestSubtitleAnalyzer` :
     - Vérifie le comportement de la fonction `analyser_sous_titres_francais` en simulant
        différentes configurations de sous-titres.
     - Teste des cas standards, des cas avec des sous-titres forcés, des langues indéfinies,
        des noms mixtes, et des structures de données anormales.
     - Utilise des données mockées pour simuler les sorties de MediaInfo.
- `TestMediaInfoFunctions` :
     - Valide le comportement des fonctions `obtenir_info_mediainfo` et
        `obtenir_info_mediainfo_explicit_path`.
     - Teste des scénarios où MediaInfo retourne des données valides, échoue, ou retourne
        un JSON invalide.
     - Vérifie également le mécanisme de fallback vers un chemin explicite lorsque MediaInfo
Fonctionnalités testées :
-------------------------
1. Analyse des sous-titres :
     - Identification des sous-titres verbaux et non verbaux selon différents presets.
     - Gestion des cas exceptionnels, tels que des structures de données malformées ou vides.
     - Validation des comportements pour des fichiers sans pistes de sous-titres.
2. Interaction avec MediaInfo :
     - Vérification de la disponibilité de MediaInfo dans le PATH système.
     - Récupération des métadonnées des fichiers multimédias via MediaInfo.
     - Gestion des erreurs, telles que l'absence de MediaInfo, des JSON invalides, ou des
        échecs d'exécution.
Dépendances :
-------------
- `unittest` : Framework de tests unitaires.
- `unittest.mock` : Pour simuler des appels à des fonctions externes et des dépendances.
- `subprocess` : Pour exécuter des commandes MediaInfo.
- `json` : Pour manipuler les données JSON retournées par MediaInfo.
- `os` et `sys` : Pour gérer les chemins et les imports dynamiques.
Exécution :
-----------
Pour exécuter les tests, lancez simplement ce fichier avec Python :
"""

import unittest
import sys
import os
import json
from unittest.mock import patch, MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# pylint: disable=wrong-import-position
from constants import dossiers_presets
from subtitle_analyzer import (
    analyser_sous_titres_francais,
    obtenir_info_mediainfo,
    obtenir_info_mediainfo_explicit_path,
)


class TestSubtitleAnalyzer(unittest.TestCase):
    """TestSubtitleAnalyzer est une suite de tests pour vérifier la fonctionnalité de la logique
    d'analyse des sous-titres dans divers scénarios. Elle utilise le framework unittest et
    simule différentes configurations de sous-titres en se basant sur des données mockées.
    Classes :
        TestSubtitleAnalyzer : Contient des cas de tests pour analyser les sous-titres selon
        différents presets.
    Méthodes :
        setUp() :
            Configure les cas de tests avec des configurations de sous-titres prédéfinies :
            - Cas standards avec sous-titres français et anglais.
            - Cas avec sous-titres forcés et normaux, y compris SDH.
            - Cas avec codes de langue indéfinis.
            - Cas avec noms de langues mixtes dans les titres des sous-titres.
            - Cas avec structures de sous-titres anormales.
        test_analyser_sous_titres_dessins_animes(mock_mediainfo) :
            Vérifie que le preset 'Dessins animés VF' analyse correctement les sous-titres
            verbaux et non verbaux.
        test_analyser_sous_titres_mangas_multi(mock_mediainfo) :
            Vérifie que le preset 'Mangas MULTI' analyse correctement les sous-titres
            verbaux et non verbaux.
        test_analyser_sous_titres_mangas_vo(mock_mediainfo) :
            Vérifie que le preset 'Mangas VO' analyse correctement les sous-titres verbaux
            tout en ignorant les sous-titres non verbaux.
        test_analyser_sous_titres_empty_tracks(mock_mediainfo) :
            dans le fichier média.
        test_analyser_sous_titres_exceptional_cases(mock_mediainfo) :
            Teste des cas exceptionnels, tels que des structures de données malformées ou
            incomplètes, des données vides, et des erreurs lors de l'exécution de MediaInfo,
            pour s'assurer que la fonction les gère correctement.
    """

    def setUp(self):
        # Cas standard avec sous-titres français et anglais
        self.info_pistes1 = {
            "media": {
                "track": [
                    {"@type": "General", "Title": "Test Video"},
                    {"@type": "Video", "Width": "1920"},
                    {"@type": "Audio", "Language": "fra", "ID": "1"},
                    {
                        "@type": "Text",
                        "Language": "eng",
                        "Title": "Full",
                        "ID": "2",
                        "StreamSize": "10000",
                        "ElementCount": "500",
                        "Duration": "3600",
                    },
                    {
                        "@type": "Text",
                        "Language": "fra",
                        "Title": "Full",
                        "ID": "5",
                        "StreamSize": "12000",
                        "ElementCount": "600",
                        "Duration": "3600",
                    },
                ]
            }
        }

        # Cas avec sous-titres forcés et normaux, plus malentendants
        self.info_pistes2 = {
            "media": {
                "track": [
                    {"@type": "General", "Title": "Test Video"},
                    {"@type": "Video", "Width": "1920"},
                    {"@type": "Audio", "Language": "fra", "ID": "1"},
                    {
                        "@type": "Text",
                        "Language": "fra",
                        "Title": "Forced",
                        "ID": "1",
                        "@typeorder": "1",
                        "StreamSize": "1000",
                        "ElementCount": "5",
                        "Duration": "3600",
                        "Forced": "Yes",
                    },
                    {
                        "@type": "Text",
                        "Language": "eng",
                        "Title": "Forced",
                        "ID": "2",
                        "@typeorder": "2",
                        "StreamSize": "900",
                        "ElementCount": "5",
                        "Duration": "3600",
                        "Forced": "Yes",
                    },
                    {
                        "@type": "Text",
                        "Language": "fra",
                        "Title": "Full",
                        "ID": "3",
                        "@typeorder": "3",
                        "StreamSize": "12000",
                        "ElementCount": "600",
                        "Duration": "3600",
                    },
                    {
                        "@type": "Text",
                        "Language": "fra",
                        "Title": "SDH",
                        "ID": "5",
                        "@typeorder": "5",
                        "StreamSize": "15000",
                        "ElementCount": "650",
                        "Duration": "3600",
                    },
                ]
            }
        }

        # Cas standard avec sous-titres français et charactère spéciaux
        self.info_pistes3 = {
            "media": {
                "track": [
                    {"@type": "General", "Title": "Test Video"},
                    {"@type": "Video", "Width": "1920"},
                    {"@type": "Audio", "Language": "fra", "ID": "1"},
                    {
                        "@type": "Text",
                        "Language": "fra",
                        "Title": "français",
                        "ID": "2",
                        "StreamSize": "10000",
                        "ElementCount": "500",
                        "Duration": "3600",
                    },
                    {
                        "@type": "Text",
                        "Language": "fra",
                        "Title": "French [ForcedNarrative]",
                        "ID": "5",
                        "StreamSize": "800",
                        "ElementCount": "5",
                        "Duration": "3600",
                    },
                ]
            }
        }

        # Cas avec code de langue "und" (undefined)
        self.info_pistes8 = {
            "media": {
                "track": [
                    {"@type": "General", "Title": "Test Video"},
                    {"@type": "Video", "Width": "1920"},
                    {"@type": "Audio", "Language": "fra", "ID": "1"},
                    {
                        "@type": "Text",
                        "Language": "und",
                        "Title": "Forced",
                        "ID": "1",
                        "@typeorder": "1",
                        "StreamSize": "1000",
                        "ElementCount": "5",
                        "Duration": "3600",
                        "Forced": "Yes",
                    },
                    {
                        "@type": "Text",
                        "Language": "und",
                        "Title": "Full",
                        "ID": "2",
                        "@typeorder": "2",
                        "StreamSize": "12000",
                        "ElementCount": "600",
                        "Duration": "3600",
                    },
                ]
            }
        }

        # Cas avec langues multiples dans le nom
        self.info_pistes9 = {
            "media": {
                "track": [
                    {"@type": "General", "Title": "Test Video"},
                    {"@type": "Video", "Width": "1920"},
                    {"@type": "Audio", "Language": "fra", "ID": "1"},
                    {
                        "@type": "Text",
                        "Language": "fra",
                        "Title": "French/English",
                        "ID": "1",
                        "@typeorder": "1",
                        "StreamSize": "12000",
                        "ElementCount": "600",
                        "Duration": "3600",
                    },
                    {
                        "@type": "Text",
                        "Language": "eng",
                        "Title": "English/French",
                        "ID": "2",
                        "@typeorder": "2",
                        "StreamSize": "11000",
                        "ElementCount": "550",
                        "Duration": "3600",
                    },
                    {
                        "@type": "Text",
                        "Language": "und",
                        "Title": "FR-EN",
                        "ID": "3",
                        "@typeorder": "3",
                        "StreamSize": "10000",
                        "ElementCount": "500",
                        "Duration": "3600",
                    },
                ]
            }
        }

        # Cas avec structure anormale de sous-titres
        self.info_pistes10 = {
            "media": {
                "track": [
                    {"@type": "General", "Title": "Test Video"},
                    {"@type": "Video", "Width": "1920"},
                    {"@type": "Audio", "Language": "fra", "ID": "1"},
                    {
                        "@type": "Text",
                        "Language": "fra",
                        "Title": "",
                        "ID": "1",
                        "@typeorder": "1",
                        "StreamSize": "12000",
                        "ElementCount": "600",
                        "Duration": "3600",
                    },
                    {
                        "@type": "Text",
                        "Language": "fra",
                        "Title": "Forced",
                        "ID": "invalid",
                        "@typeorder": "3",
                        "StreamSize": "1000",
                        "ElementCount": "5",
                        "Duration": "3600",
                    },
                ]
            }
        }

    @patch("subtitle_analyzer.obtenir_info_mediainfo")
    def test_analyser_sous_titres_dessins_animes(self, mock_mediainfo):
        """
        Vérifie que le preset 'Dessins animes VF' analyse correctement les sous-titres.
        """
        preset = "Dessins animes VF"

        # Test avec info_pistes1
        mock_mediainfo.return_value = self.info_pistes1
        verbal, non_verbal, _ = analyser_sous_titres_francais("dummy_file.mkv", preset)
        self.assertEqual(verbal, 2)  # Index du sous-titre verbal
        self.assertIsNone(non_verbal)  # Pas de sous-titre non-verbal

        # Test avec info_pistes2
        mock_mediainfo.return_value = self.info_pistes2
        verbal, non_verbal, _ = analyser_sous_titres_francais("dummy_file.mkv", preset)
        self.assertEqual(verbal, 3)  # Index du sous-titre verbal normal
        self.assertEqual(non_verbal, 1)  # Index du sous-titre forcé

        # Test avec info_pistes3 (caractères spéciaux)
        mock_mediainfo.return_value = self.info_pistes3
        verbal, non_verbal, _ = analyser_sous_titres_francais("dummy_file.mkv", preset)
        self.assertEqual(verbal, 1)  # Index du sous-titre verbal normal
        self.assertEqual(non_verbal, 2)  # Index du sous-titre forcé

        # Test avec info_pistes8 (langue indéfinie)
        mock_mediainfo.return_value = self.info_pistes8
        verbal, non_verbal, _ = analyser_sous_titres_francais("dummy_file.mkv", preset)
        self.assertIsNone(verbal)  # Devrait reconnaître "Full" comme verbal
        self.assertIsNone(non_verbal)  # Devrait reconnaître "Forced" comme non verbal

        # Test avec info_pistes9 (noms mixtes)
        mock_mediainfo.return_value = self.info_pistes9
        verbal, non_verbal, _ = analyser_sous_titres_francais("dummy_file.mkv", preset)
        self.assertEqual(verbal, 1)  # Devrait choisir le premier sous-titre français
        self.assertIsNone(non_verbal)  # Pas de sous-titre forcé

        # Test avec info_pistes10 (données anormales)
        mock_mediainfo.return_value = self.info_pistes10
        verbal, non_verbal, _ = analyser_sous_titres_francais("dummy_file.mkv", preset)
        self.assertEqual(verbal, 1)  # Devrait reconnaître le premier comme verbal
        self.assertEqual(
            non_verbal, 2
        )  # Devrait ignorer l'ID invalide de mediainfo et le considérer comme non verbal

    @patch("subtitle_analyzer.obtenir_info_mediainfo")
    def test_analyser_sous_titres_mangas_vo(self, mock_mediainfo):
        """
        Vérifie que le preset 'Mangas VO' analyse correctement les sous-titres.
        """
        preset = "Mangas VO"

        # Test avec info_pistes1
        mock_mediainfo.return_value = self.info_pistes1
        verbal, non_verbal, _ = analyser_sous_titres_francais("dummy_file.mkv", preset)
        self.assertEqual(
            verbal, 2
        )  # Index du sous-titre verbal à intégrer dans la vidéo
        self.assertIsNone(non_verbal)  # Ignore les sous-titres non verbaux en mode VO

        # Test avec info_pistes2
        mock_mediainfo.return_value = self.info_pistes2
        verbal, non_verbal, _ = analyser_sous_titres_francais("dummy_file.mkv", preset)
        self.assertEqual(verbal, 3)  # Index du sous-titre verbal normal
        self.assertIsNone(
            non_verbal
        )  # Ignore les sous-titres non-verbal avec le preset VO

        # Test avec info_pistes3 (caractères spéciaux)
        mock_mediainfo.return_value = self.info_pistes3
        verbal, non_verbal, _ = analyser_sous_titres_francais("dummy_file.mkv", preset)
        self.assertEqual(verbal, 1)  # Index du sous-titre verbal normal
        self.assertIsNone(
            non_verbal
        )  # Ignore les sous-titres non-verbal avec le preset VO

        # Test avec info_pistes8 (langue indéfinie)
        mock_mediainfo.return_value = self.info_pistes8
        verbal, non_verbal, _ = analyser_sous_titres_francais("dummy_file.mkv", preset)
        self.assertIsNone(verbal)  # None car "Full" est de type de language undefined
        self.assertIsNone(
            non_verbal
        )  # Ignore les sous-titres non-verbal avec le preset VO

        # Test avec info_pistes9 (noms mixtes)
        mock_mediainfo.return_value = self.info_pistes9
        verbal, non_verbal, _ = analyser_sous_titres_francais("dummy_file.mkv", preset)
        self.assertEqual(verbal, 1)  # Devrait choisir le premier sous-titre français
        self.assertIsNone(
            non_verbal
        )  # Ignore les sous-titres non-verbal avec le preset VO

        # Test avec info_pistes10 (données anormales)
        mock_mediainfo.return_value = self.info_pistes10
        verbal, non_verbal, _ = analyser_sous_titres_francais("dummy_file.mkv", preset)
        self.assertEqual(verbal, 1)  # Devrait reconnaître le premier comme verbal
        self.assertIsNone(
            non_verbal
        )  # Ignore les sous-titres non-verbal avec le preset VO

    @patch("subtitle_analyzer.obtenir_info_mediainfo")
    def test_analyser_sous_titres_empty_tracks(self, mock_mediainfo):
        """
        Vérifie que la fonction ne sélectionne aucun sous-titre si aucun n'est disponible
        """
        empty_info = {
            "media": {
                "track": [
                    {"@type": "General", "Title": "Test Video"},
                    {"@type": "Video", "Width": "1920"},
                    {"@type": "Audio", "Language": "fra", "ID": "1"},
                ]
            }
        }

        presets = list(dossiers_presets.values())

        for preset in presets:
            mock_mediainfo.return_value = empty_info
            verbal, non_verbal, _ = analyser_sous_titres_francais(
                "dummy_file.mkv", preset
            )
            self.assertIsNone(verbal)
            self.assertIsNone(non_verbal)

    @patch("subtitle_analyzer.obtenir_info_mediainfo")
    def test_analyser_sous_titres_exceptional_cases(self, mock_mediainfo):
        """
        Tests pour des cas exceptionnels qui pourraient causer des anomalies
        """
        preset = "Films - Series VF"

        # Structure de données incomplète ou malformée
        mock_mediainfo.return_value = {"media": {"track": [{"@type": "General"}]}}
        verbal, non_verbal, _ = analyser_sous_titres_francais("dummy_file.mkv", preset)
        self.assertIsNone(verbal)
        self.assertIsNone(non_verbal)

        # Structure de données vide
        mock_mediainfo.return_value = {}
        verbal, non_verbal, _ = analyser_sous_titres_francais("dummy_file.mkv", preset)
        self.assertIsNone(verbal)
        self.assertIsNone(non_verbal)

        # Erreur lors de l'exécution de mediainfo
        mock_mediainfo.return_value = "Erreur MediaInfo"
        verbal, non_verbal, _ = analyser_sous_titres_francais("dummy_file.mkv", preset)
        self.assertIsNone(verbal)
        self.assertIsNone(non_verbal)


class TestMediaInfoFunctions(unittest.TestCase):
    """
    TestMediaInfoFunctions est une suite de tests pour valider le comportement des fonctions
    qui interagissent avec l'outil MediaInfo. Elle utilise le framework unittest et des mocks
    pour simuler divers scénarios.
        TestMediaInfoFunctions: Contient les cas de test pour les fonctions liées à MediaInfo.
    Méthodes:
            Configure un exemple de sortie JSON de MediaInfo à utiliser dans les tests.
            Teste le cas où MediaInfo est disponible et retourne des données valides.
            Teste le mécanisme de fallback vers un chemin explicite lorsque MediaInfo
            n'est pas trouvé dans le PATH système.
            Teste la gestion des erreurs lorsque l'exécution de MediaInfo échoue.
            Teste la gestion des erreurs lorsque MediaInfo retourne un JSON invalide.
            Teste la fonction avec un chemin explicite vers l'exécutable MediaInfo
            et vérifie qu'elle s'exécute avec succès.
            Teste la gestion des erreurs lorsque l'exécution avec un chemin explicite
            vers MediaInfo échoue.
    """

    def setUp(self):
        # Exemple de sortie JSON que MediaInfo pourrait renvoyer
        self.sample_mediainfo_json = json.dumps(
            {
                "media": {
                    "track": [
                        {"@type": "General", "Title": "Test Video"},
                        {"@type": "Video", "Width": "1920"},
                        {"@type": "Audio", "Language": "fra", "ID": "1"},
                        {
                            "@type": "Text",
                            "Language": "fra",
                            "Title": "French",
                            "ID": "2",
                        },
                    ]
                }
            }
        )

    @patch("subprocess.run")
    def test_obtenir_info_mediainfo_success(self, mock_run):
        """Teste le cas où MediaInfo est disponible et retourne des données valides"""
        # Configurer le mock pour simuler une exécution réussie de mediainfo
        version_process = MagicMock()
        version_process.stdout = "MediaInfo v21.03\n"
        version_process.returncode = 0

        mediainfo_process = MagicMock()
        mediainfo_process.stdout = self.sample_mediainfo_json
        mediainfo_process.returncode = 0

        # Le premier appel à run() vérifie la version, le second obtient les infos du fichier
        mock_run.side_effect = [version_process, mediainfo_process]

        # Tester la fonction avec un fichier fictif
        result = obtenir_info_mediainfo("dummy.mkv")

        # Vérifier que subprocess.run a été appelé correctement
        self.assertEqual(mock_run.call_count, 2)

        # Vérifier que le résultat est bien un dictionnaire avec la structure attendue
        self.assertIsInstance(result, dict)
        self.assertIn("media", result)
        self.assertIn("track", result["media"])
        self.assertEqual(len(result["media"]["track"]), 4)

    @patch("subprocess.run")
    @patch("os.path.exists")
    def test_obtenir_info_mediainfo_fallback_path(self, mock_exists, mock_run):
        """Teste le fallback vers le chemin explicite quand mediainfo n'est pas dans le PATH"""
        # Simuler que MediaInfo n'est pas dans le PATH mais existe dans un chemin spécifique
        mock_run.side_effect = FileNotFoundError("mediainfo not found")
        mock_exists.return_value = True  # Chemin alternatif existe

        # Configurer le mock pour le chemin explicite
        explicit_process = MagicMock()
        explicit_process.stdout = self.sample_mediainfo_json
        explicit_process.returncode = 0

        # Utiliser un autre patch pour le chemin explicite
        with patch(
            "subtitle_analyzer.obtenir_info_mediainfo_explicit_path",
            return_value=json.loads(self.sample_mediainfo_json),
        ) as mock_explicit:
            result = obtenir_info_mediainfo("dummy.mkv")

            # Vérifier que la fonction a tenté d'utiliser le chemin explicite
            mock_explicit.assert_called_once()

            # Vérifier le résultat
            self.assertIsInstance(result, dict)
            self.assertIn("media", result)

    @patch("subprocess.run")
    def test_obtenir_info_mediainfo_error(self, mock_run):
        """Teste la gestion des erreurs quand MediaInfo échoue"""
        # Simuler une erreur dans l'exécution de MediaInfo
        error_process = MagicMock()
        error_process.returncode = 1
        error_process.stderr = "Error: File not found"

        mock_run.return_value = error_process

        result = obtenir_info_mediainfo("nonexistent.mkv")

        # Vérifier que le résultat est une chaîne d'erreur
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("Erreur MediaInfo"))

    @patch("subprocess.run")
    def test_obtenir_info_mediainfo_invalid_json(self, mock_run):
        """Teste la gestion des erreurs quand MediaInfo retourne un JSON invalide"""
        # Configurer le mock pour renvoyer un JSON invalide
        version_process = MagicMock()
        version_process.stdout = "MediaInfo v21.03\n"
        version_process.returncode = 0

        invalid_json_process = MagicMock()
        invalid_json_process.stdout = "Not a valid JSON"
        invalid_json_process.returncode = 0

        mock_run.side_effect = [version_process, invalid_json_process]

        result = obtenir_info_mediainfo("dummy.mkv")

        # Vérifier que le résultat est une chaîne d'erreur relative au JSON
        self.assertIsInstance(result, str)
        self.assertTrue("Erreur de décodage JSON" in result)

    @patch("subprocess.run")
    def test_obtenir_info_mediainfo_explicit_path_success(self, mock_run):
        """Teste la fonction avec un chemin explicite vers MediaInfo"""
        # Configurer le mock pour simuler une exécution réussie
        mock_process = MagicMock()
        mock_process.stdout = self.sample_mediainfo_json
        mock_process.returncode = 0

        mock_run.return_value = mock_process

        # Utiliser un chemin qui s'adapte au système d'exploitation
        if os.name == "nt":  # Windows
            mediainfo_path = os.path.join(
                os.environ.get("PROGRAMFILES", "C:/Program Files"),
                "MediaInfo",
                "MediaInfo.exe",
            )
        else:  # Linux/Mac
            mediainfo_path = "/usr/bin/mediainfo"

        result = obtenir_info_mediainfo_explicit_path("dummy.mkv", mediainfo_path)

        # Vérifier que subprocess.run a été appelé avec le bon chemin
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        self.assertEqual(call_args[0], mediainfo_path)

        # Vérifier le résultat
        self.assertIsInstance(result, dict)
        self.assertIn("media", result)

    @patch("subprocess.run")
    def test_obtenir_info_mediainfo_explicit_path_error(self, mock_run):
        """Teste la gestion des erreurs avec un chemin explicite"""
        # Simuler une exception lors de l'exécution
        mock_run.side_effect = Exception("Test exception")

        result = obtenir_info_mediainfo_explicit_path("dummy.mkv", "invalid/path")

        # Vérifier que le résultat est une chaîne d'erreur
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("Une erreur avec le chemin explicite"))


if __name__ == "__main__":
    unittest.main()
