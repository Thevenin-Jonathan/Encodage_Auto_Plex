import unittest
import sys
import os

# Ajouter le répertoire racine au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from audio_selection import selectionner_pistes_audio


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

    def test_selectionner_pistes_audio_films_series(self):
        for preset in ["Dessins animes FR 1000kbps", "1080p HD-Light 1500kbps"]:
            # Test avec info_pistes1
            result = selectionner_pistes_audio(self.info_pistes1, preset)
            self.assertEqual(result, [1])

            # Test avec info_pistes2
            result = selectionner_pistes_audio(self.info_pistes2, preset)
            self.assertEqual(result, [1])

            # Test avec info_pistes3
            result = selectionner_pistes_audio(self.info_pistes3, preset)
            self.assertEqual(result, [1])

            # Test avec info_pistes4
            result = selectionner_pistes_audio(self.info_pistes4, preset)
            self.assertEqual(result, None)

            # Test avec info_pistes5
            result = selectionner_pistes_audio(self.info_pistes5, preset)
            self.assertEqual(result, [1])

    def test_selectionner_pistes_audio_mangas_multi(self):
        preset = "Mangas MULTI 1000kbps"

        # Test avec info_pistes1
        result = selectionner_pistes_audio(self.info_pistes1, preset)
        self.assertEqual(result, [1, 2])

        # Test avec info_pistes2
        result = selectionner_pistes_audio(self.info_pistes2, preset)
        self.assertEqual(result, [1, 2, 3, 4, 5, 6, 7, 8])

        # Test avec info_pistes3
        result = selectionner_pistes_audio(self.info_pistes3, preset)
        self.assertEqual(result, [1, 2])

        # Test avec info_pistes4
        result = selectionner_pistes_audio(self.info_pistes4, preset)
        self.assertEqual(result, None)

    def test_selectionner_pistes_audio_mangas_vo(self):
        preset = "Mangas VO 1000kbps"

        # Test avec info_pistes1
        result = selectionner_pistes_audio(self.info_pistes1, preset)
        self.assertEqual(result, [1, 2])

        # Test avec info_pistes2
        result = selectionner_pistes_audio(self.info_pistes2, preset)
        self.assertEqual(result, None)

        # Test avec info_pistes3
        result = selectionner_pistes_audio(self.info_pistes3, preset)
        self.assertEqual(result, [1, 2])

        # Test avec info_pistes4
        result = selectionner_pistes_audio(self.info_pistes4, preset)
        self.assertEqual(result, None)


if __name__ == "__main__":
    unittest.main()
