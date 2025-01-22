import unittest
import sys
import os

# Ajouter le répertoire racine au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from subtitle_selection import selectionner_sous_titres


class TestSubtitleSelection(unittest.TestCase):
    def setUp(self):
        self.info_pistes = {
            "TitleList": [
                {
                    "SubtitleList": [
                        {"TrackNumber": 1, "LanguageCode": "fra", "Name": "French"},
                        {"TrackNumber": 2, "LanguageCode": "eng", "Name": "English"},
                    ]
                }
            ]
        }

    def test_selectionner_sous_titres_dessins_animes(self):
        preset = "Dessins animés FR 1000kbps"
        result, burn = selectionner_sous_titres(self.info_pistes, preset)
        self.assertEqual(result, [1])
        self.assertIsNone(burn)

    def test_selectionner_sous_titres_mangas_multi(self):
        preset = "Mangas MULTI 1000kbps"
        result, burn = selectionner_sous_titres(self.info_pistes, preset)
        self.assertEqual(result, [1])
        self.assertIsNone(burn)

    def test_selectionner_sous_titres_mangas_vo(self):
        preset = "Mangas VO 1000kbps"
        result, burn = selectionner_sous_titres(self.info_pistes, preset)
        self.assertEqual(result, [1])
        self.assertEqual(burn, 1)


if __name__ == "__main__":
    unittest.main()
