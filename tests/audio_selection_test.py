import unittest
import sys
import os
import logging

# Configurer le logger pour afficher les messages DEBUG
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Ajouter le répertoire racine au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from audio_selection import filtrer_pistes_audio
from logger import setup_logger

logger = setup_logger(__name__)


class TestAudioSelection(unittest.TestCase):
    def setUp(self):
        self.info_pistes1 = {
            "TitleList": [
                {
                    "AudioList": [
                        {"TrackNumber": 1, "LanguageCode": "fra", "Name": "Full"},
                        {"TrackNumber": 2, "LanguageCode": "eng", "Name": "Full"},
                    ]
                }
            ]
        }

        self.info_pistes2 = {
            "TitleList": [
                {
                    "AudioList": [
                        {"TrackNumber": 1, "LanguageCode": "fra", "Name": ""},
                        {"TrackNumber": 2, "LanguageCode": "fra", "Name": "VFQ"},
                        {"TrackNumber": 3, "LanguageCode": "fra", "Name": "VF-ad"},
                        {"TrackNumber": 4, "LanguageCode": "fra", "Name": "AD"},
                        {
                            "TrackNumber": 5,
                            "LanguageCode": "fra",
                            "Name": "audiodescription",
                        },
                        {"TrackNumber": 6, "LanguageCode": "fra", "Name": "quebec"},
                        {"TrackNumber": 7, "LanguageCode": "fra", "Name": "canada"},
                        {
                            "TrackNumber": 8,
                            "LanguageCode": "fra",
                            "Name": "descriptive audio",
                        },
                    ]
                }
            ]
        }

        self.info_pistes3 = {
            "TitleList": [
                {
                    "AudioList": [
                        {
                            "TrackNumber": 2,
                        },
                        {"TrackNumber": 1, "LanguageCode": "fra"},
                    ]
                }
            ]
        }

        self.info_pistes4 = {"TitleList": [{"AudioList": []}]}

        self.info_pistes5 = {
            "TitleList": [
                {
                    "AudioList": [
                        {
                            "TrackNumber": 1,
                            "LanguageCode": "fra",
                            "Name": "Audio VF -NoFace696",
                        },
                    ]
                }
            ]
        }

        # Cas complexe 1 : Plusieurs langues avec des noms descriptifs
        self.info_pistes6 = {
            "TitleList": [
                {
                    "AudioList": [
                        {"TrackNumber": 1, "LanguageCode": "fra", "Name": "Full"},
                        {
                            "TrackNumber": 2,
                            "LanguageCode": "eng",
                            "Name": "Descriptive Audio",
                        },
                        {
                            "TrackNumber": 3,
                            "LanguageCode": "spa",
                            "Name": "Audio Español",
                        },
                        {"TrackNumber": 4, "LanguageCode": "fra", "Name": "VFQ"},
                    ]
                }
            ]
        }

        # Cas complexe 2 : Aucune langue définie
        self.info_pistes7 = {
            "TitleList": [
                {
                    "AudioList": [
                        {"TrackNumber": 1, "Name": "Audio 1"},
                        {"TrackNumber": 2, "Name": "Audio 2"},
                    ]
                }
            ]
        }

        # Cas complexe 3 : Une seule piste valide
        self.info_pistes8 = {
            "TitleList": [
                {
                    "AudioList": [
                        {"TrackNumber": 1, "LanguageCode": "fra", "Name": "Full"},
                    ]
                }
            ]
        }

        # Cas complexe 4 : Plusieurs pistes valides mais avec des critères d'exclusion
        self.info_pistes9 = {
            "TitleList": [
                {
                    "AudioList": [
                        {
                            "TrackNumber": 1,
                            "LanguageCode": "fra",
                            "Name": "Descriptive Audio",
                        },
                        {"TrackNumber": 2, "LanguageCode": "eng", "Name": "Full"},
                        {"TrackNumber": 3, "LanguageCode": "fra", "Name": "VFQ"},
                    ]
                }
            ]
        }

        # Cas complexe 5 : Une piste par langue mais avec des doublons
        self.info_pistes10 = {
            "TitleList": [
                {
                    "AudioList": [
                        {"TrackNumber": 1, "LanguageCode": "fra", "Name": "Full"},
                        {"TrackNumber": 2, "LanguageCode": "fra", "Name": "VFQ"},
                        {"TrackNumber": 3, "LanguageCode": "eng", "Name": "Full"},
                        {
                            "TrackNumber": 4,
                            "LanguageCode": "eng",
                            "Name": "Descriptive Audio",
                        },
                    ]
                }
            ]
        }

        # Cas complexe 6 : Une seule piste sans language code
        self.info_pistes11 = {
            "TitleList": [
                {
                    "AudioList": [
                        {"TrackNumber": 1, "Name": "fre"},
                    ]
                }
            ]
        }

    def test_selectionner_pistes_audio_films_series(self):
        for preset in ["Dessins animes VF", "Films - Series VF", "4K - 10bits"]:
            # Test avec info_pistes1
            result = filtrer_pistes_audio(self.info_pistes1, preset)
            self.assertEqual(result, [1])

            # Test avec info_pistes2
            result = filtrer_pistes_audio(self.info_pistes2, preset)
            self.assertEqual(result, [1])

            # Test avec info_pistes3
            result = filtrer_pistes_audio(self.info_pistes3, preset)
            self.assertEqual(result, [1])

            # Test avec info_pistes4
            result = filtrer_pistes_audio(self.info_pistes4, preset)
            self.assertEqual(result, None)

            # Test avec info_pistes5
            result = filtrer_pistes_audio(self.info_pistes5, preset)
            self.assertEqual(result, [1])

            # Test avec info_pistes6
            result = filtrer_pistes_audio(self.info_pistes6, preset)
            self.assertEqual(result, [1])

            # Test avec info_pistes7
            result = filtrer_pistes_audio(self.info_pistes7, preset)
            self.assertEqual(result, None)

            # Test avec info_pistes8
            result = filtrer_pistes_audio(self.info_pistes8, preset)
            self.assertEqual(result, [1])

            # Test avec info_pistes9
            result = filtrer_pistes_audio(self.info_pistes9, preset)
            self.assertEqual(result, [3])

            # Test avec info_pistes10
            result = filtrer_pistes_audio(self.info_pistes10, preset)
            self.assertEqual(result, [1])

            # Test avec info_pistes11
            result = filtrer_pistes_audio(self.info_pistes11, preset)
            self.assertEqual(result, [1])

    def test_selectionner_pistes_audio_mangas_multi(self):
        preset = "Mangas MULTI"

        # Test avec info_pistes1
        result = filtrer_pistes_audio(self.info_pistes1, preset)
        self.assertEqual(result, [1, 2])

        # Test avec info_pistes2
        result = filtrer_pistes_audio(self.info_pistes2, preset)
        self.assertEqual(result, None)

        # Test avec info_pistes3
        result = filtrer_pistes_audio(self.info_pistes3, preset)
        self.assertEqual(result, None)

        # Test avec info_pistes4
        result = filtrer_pistes_audio(self.info_pistes4, preset)
        self.assertEqual(result, None)

        # Test avec info_pistes6
        result = filtrer_pistes_audio(self.info_pistes6, preset)
        self.assertEqual(result, [1, 3])

        # Test avec info_pistes7
        result = filtrer_pistes_audio(self.info_pistes7, preset)
        self.assertEqual(result, None)

        # Test avec info_pistes8
        result = filtrer_pistes_audio(self.info_pistes8, preset)
        self.assertEqual(result, None)

        # Test avec info_pistes9
        result = filtrer_pistes_audio(self.info_pistes9, preset)
        self.assertEqual(result, [3, 2])

        # Test avec info_pistes10
        result = filtrer_pistes_audio(self.info_pistes10, preset)
        self.assertEqual(result, [1, 3])

        # Test avec info_pistes11
        result = filtrer_pistes_audio(self.info_pistes11, preset)
        self.assertEqual(result, None)

    def test_selectionner_pistes_audio_mangas_vo(self):
        preset = "Mangas VO"

        # Test avec info_pistes1
        result = filtrer_pistes_audio(self.info_pistes1, preset)
        self.assertEqual(result, None)

        # Test avec info_pistes2
        result = filtrer_pistes_audio(self.info_pistes2, preset)
        self.assertEqual(result, None)

        # Test avec info_pistes3
        result = filtrer_pistes_audio(self.info_pistes3, preset)
        self.assertEqual(result, [1])

        # Test avec info_pistes4
        result = filtrer_pistes_audio(self.info_pistes4, preset)
        self.assertEqual(result, None)

        # Test avec info_pistes5
        result = filtrer_pistes_audio(self.info_pistes5, preset)
        self.assertEqual(result, [1])

        # Test avec info_pistes6
        result = filtrer_pistes_audio(self.info_pistes6, preset)
        self.assertEqual(result, None)

        # Test avec info_pistes7
        result = filtrer_pistes_audio(self.info_pistes7, preset)
        self.assertEqual(result, None)

        # Test avec info_pistes8
        result = filtrer_pistes_audio(self.info_pistes8, preset)
        self.assertEqual(result, [1])

        # Test avec info_pistes9
        result = filtrer_pistes_audio(self.info_pistes9, preset)
        self.assertEqual(result, None)

        # Test avec info_pistes10
        result = filtrer_pistes_audio(self.info_pistes10, preset)
        self.assertEqual(result, None)

        # Test avec info_pistes11
        result = filtrer_pistes_audio(self.info_pistes11, preset)
        self.assertEqual(result, [1])


if __name__ == "__main__":
    unittest.main()
