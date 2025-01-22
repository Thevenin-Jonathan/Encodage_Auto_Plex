import unittest
import sys
import os

# Ajouter le répertoire racine au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from audio_selection import selectionner_pistes_audio


class TestAudioSelection(unittest.TestCase):
    def setUp(self):
        self.info_pistes = {
            "TitleList": [
                {
                    "AudioList": [
                        {"TrackNumber": 1, "LanguageCode": "fra", "Name": "French"},
                        {"TrackNumber": 2, "LanguageCode": "eng", "Name": "English"},
                    ]
                }
            ]
        }

    def test_selectionner_pistes_audio_dessins_animes(self):
        preset = "Dessins animés FR 1000kbps"
        result = selectionner_pistes_audio(self.info_pistes, preset)
        self.assertEqual(result, [1])

    def test_selectionner_pistes_audio_mangas_multi(self):
        preset = "Mangas MULTI 1000kbps"
        result = selectionner_pistes_audio(self.info_pistes, preset)
        self.assertEqual(result, [1, 2])

    def test_selectionner_pistes_audio_mangas_vo(self):
        preset = "Mangas VO 1000kbps"
        result = selectionner_pistes_audio(self.info_pistes, preset)
        self.assertEqual(result, [1, 2])


if __name__ == "__main__":
    unittest.main()
