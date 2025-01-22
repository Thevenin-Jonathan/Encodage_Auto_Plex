import unittest
import sys
import os

# Ajouter le répertoire racine au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from subtitle_selection import selectionner_sous_titres


class TestSubtitleSelection(unittest.TestCase):
    def setUp(self):
        self.info_pistes1 = {
            "TitleList": [
                {
                    "SubtitleList": [
                        {"TrackNumber": 2, "LanguageCode": "eng", "Name": "Full"},
                        {"TrackNumber": 5, "LanguageCode": "fra", "Name": "Full"},
                    ]
                }
            ]
        }

        self.info_pistes2 = {
            "TitleList": [
                {
                    "SubtitleList": [
                        {"TrackNumber": 1, "LanguageCode": "fra", "Name": "Forced"},
                        {"TrackNumber": 2, "LanguageCode": "eng", "Name": "Forced"},
                        {"TrackNumber": 3, "LanguageCode": "fra", "Name": "Full"},
                        {"TrackNumber": 4, "LanguageCode": "eng", "Name": "Full"},
                        {"TrackNumber": 5, "LanguageCode": "fra", "Name": "SDH"},
                        {
                            "TrackNumber": 6,
                            "LanguageCode": "fra",
                            "Name": "malentendant",
                        },
                        {"TrackNumber": 7, "LanguageCode": "fra", "Name": "FR SDH"},
                    ]
                }
            ]
        }

        self.info_pistes3 = {
            "TitleList": [
                {
                    "SubtitleList": [
                        {"TrackNumber": 2, "LanguageCode": "fra", "Name": "Forced"},
                        {
                            "TrackNumber": 3,
                            "LanguageCode": "fra",
                            "Name": "Forced-colored",
                        },
                        {"TrackNumber": 4, "LanguageCode": "fra", "Name": "Full"},
                        {
                            "TrackNumber": 5,
                            "LanguageCode": "fra",
                            "Name": "Commentaires",
                        },
                    ]
                }
            ]
        }

        self.info_pistes4 = {"TitleList": [{"SubtitleList": []}]}

        self.info_pistes5 = {
            "TitleList": [
                {
                    "SubtitleList": [
                        {"TrackNumber": 2, "LanguageCode": "fra", "Name": "Forced"},
                        {"TrackNumber": 5, "LanguageCode": "fra"},
                    ]
                },
            ]
        }

        self.info_pistes6 = {
            "TitleList": [
                {
                    "SubtitleList": [
                        {"TrackNumber": 2, "LanguageCode": "fra", "Name": "Forced"},
                        {"TrackNumber": 5},
                    ]
                },
            ]
        }

    def test_selectionner_sous_titres_dessins_animes(self):
        """
        Vérifie que le preset 'Dessins animes FR 1000kbps' sélectionne correctement les sous-titres.
        """
        preset = "Dessins animes FR 1000kbps"

        # Test avec info_pistes1
        result, burn = selectionner_sous_titres(self.info_pistes1, preset)
        self.assertEqual(result, [5])
        self.assertIsNone(burn)

        # Test avec info_pistes2
        result, burn = selectionner_sous_titres(self.info_pistes2, preset)
        self.assertEqual(result, [1, 3])
        self.assertEqual(burn, 1)

        # Test avec info_pistes3
        result, burn = selectionner_sous_titres(self.info_pistes3, preset)
        self.assertEqual(result, None)
        self.assertEqual(burn, None)

        # Test avec info_pistes5
        result, burn = selectionner_sous_titres(self.info_pistes5, preset)
        self.assertEqual(result, [2, 5])
        self.assertEqual(burn, 2)

        # Test avec info_pistes6
        result, burn = selectionner_sous_titres(self.info_pistes6, preset)
        self.assertEqual(result, [2])
        self.assertEqual(burn, 2)

    def test_selectionner_sous_titres_films_series(self):
        """
        Vérifie que le preset '1080p HD-Light 1500kbps' sélectionne correctement les sous-titres.
        """
        preset = "1080p HD-Light 1500kbps"

        # Test avec info_pistes1
        result, burn = selectionner_sous_titres(self.info_pistes1, preset)
        self.assertEqual(result, [5])
        self.assertIsNone(burn)

        # Test avec info_pistes2
        result, burn = selectionner_sous_titres(self.info_pistes2, preset)
        self.assertEqual(result, [1, 3])
        self.assertEqual(burn, 1)

        # Test avec info_pistes3
        result, burn = selectionner_sous_titres(self.info_pistes3, preset)
        self.assertEqual(result, None)
        self.assertEqual(burn, None)

        # Test avec info_pistes5
        result, burn = selectionner_sous_titres(self.info_pistes5, preset)
        self.assertEqual(result, [2, 5])
        self.assertEqual(burn, 2)

        # Test avec info_pistes6
        result, burn = selectionner_sous_titres(self.info_pistes6, preset)
        self.assertEqual(result, [2])
        self.assertEqual(burn, 2)

    def test_selectionner_sous_titres_mangas_multi(self):
        """
        Vérifie que le preset 'Mangas MULTI 1000kbps' sélectionne correctement les sous-titres.
        """
        preset = "Mangas MULTI 1000kbps"

        # Test avec info_pistes1
        result, burn = selectionner_sous_titres(self.info_pistes1, preset)
        self.assertEqual(result, [5])
        self.assertIsNone(burn)

        # Test avec info_pistes2
        result, burn = selectionner_sous_titres(self.info_pistes2, preset)
        self.assertEqual(result, [1, 3])
        self.assertEqual(burn, 1)

        # Test avec info_pistes3
        result, burn = selectionner_sous_titres(self.info_pistes3, preset)
        self.assertEqual(result, None)
        self.assertEqual(burn, None)

        # Test avec info_pistes5
        result, burn = selectionner_sous_titres(self.info_pistes5, preset)
        self.assertEqual(result, [2, 5])
        self.assertEqual(burn, 2)

        # Test avec info_pistes6
        result, burn = selectionner_sous_titres(self.info_pistes6, preset)
        self.assertEqual(result, [2])
        self.assertEqual(burn, 2)

    def test_selectionner_sous_titres_mangas_vo(self):
        """
        Vérifie que le preset 'Mangas VO 1000kbps' sélectionne correctement les sous-titres.
        """
        preset = "Mangas VO 1000kbps"

        # Test avec info_pistes1
        result, burn = selectionner_sous_titres(self.info_pistes1, preset)
        self.assertEqual(result, [5])
        self.assertEqual(burn, 5)

        # Test avec info_pistes4
        result, burn = selectionner_sous_titres(self.info_pistes4, preset)
        self.assertEqual(result, None)
        self.assertEqual(burn, None)

        # Test avec info_pistes5
        result, burn = selectionner_sous_titres(self.info_pistes5, preset)
        self.assertEqual(result, None)
        self.assertEqual(burn, None)

        # Test avec info_pistes6
        result, burn = selectionner_sous_titres(self.info_pistes6, preset)
        self.assertEqual(result, [2])
        self.assertEqual(burn, 2)

    def test_selectionner_sous_titres_empty_tracks(self):
        """
        Vérifie que la fonction ne sélectionne aucun sous-titre si la liste des sous-titres est vide.
        """
        presets = [
            "Dessins animes FR 1000kbps",
            "1080p HD-Light 1500kbps",
            "Mangas MULTI 1000kbps",
            "Mangas VO 1000kbps",
        ]

        for preset in presets:
            result, burn = selectionner_sous_titres(self.info_pistes4, preset)
            self.assertEqual(result, None)
            self.assertEqual(burn, None)


if __name__ == "__main__":
    unittest.main()
