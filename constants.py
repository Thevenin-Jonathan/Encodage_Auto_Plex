import sys
import os

# Définir le chemin de base en fonction de l'exécution en tant que script ou exécutable
if getattr(sys, "frozen", False):
    # Mode exécutable - utiliser le dossier où se trouve l'exécutable
    BASE_PATH = os.path.dirname(sys.executable)
else:
    BASE_PATH = os.path.dirname(__file__)

# Définir la variable debug_mode
debug_mode = False  # Change cette valeur à True pour activer le mode débogage

config_file = os.path.join(BASE_PATH, "datas", "config.json")

icon_file = os.path.join(BASE_PATH, "images", "ico.ico")

# Dossiers à surveiller et leurs presets HandBrake
dossiers_presets = {
    "D:/Torrents/Dessins animes VF": "Dessins animes VF",
    "D:/Torrents/Film - series VF": "Films - Series VF",
    "D:/Torrents/Film - series MULTI": "Films - Series MULTI",
    "D:/Torrents/Mangas MULTI": "Mangas MULTI",
    "D:/Torrents/Mangas VO": "Mangas VO",
    "D:/Torrents/4K - 10bits": "4K - 10bits",
}

# Chemin du dossier de sortie pour les fichiers encodés
dossier_sortie = "D:/Ripped"

# Fichier de presets personnalisés
fichier_presets = os.path.join(BASE_PATH, "datas", "custom_presets.json")

# Fichier de sauvegarde des fichiers détectés et encodés
fichier_sauvegarde = os.path.join(BASE_PATH, "datas", "fichiers_detectes.json")
fichier_encodes = os.path.join(BASE_PATH, "datas", "fichiers_encodes.json")

# Extensions de fichiers à surveiller
extensions = [".mkv", ".mp4", ".avi"]

# Critères pour filtrer les pistes françaises indésirables
criteres_audios = [
    "vfq",
    "ad",
    " ad",
    "-ad",
    "audiodescription",
    "quebec",
    "nad",
    "descriptive audio",
]

# Critères pour les sous-titres
criteres_sous_titres_burn = ["force"]
criteres_sous_titres_supprimer = [
    "sdh",
    "malentendant",
    "vfq",
    "quebe",
    "nad",
    "comment",
]

# Dossiers pour encodage manuel
dossier_encodage_manuel = "D:/Torrents/Encodage_manuel"
fichier_encodage_manuel = os.path.join(BASE_PATH, "Encodage_manuel.txt")

# Dossier pour l'historique des encodages réussis
fichier_historique = os.path.join(BASE_PATH, "datas", "successful_encodings.json")

state_file = os.path.join(BASE_PATH, "datas", "interrupted_encodings.json")

# Taille maximal des messages de notifications windows
maxsize_message = 70

# État par défaut des notifications Windows (True = activées, False = désactivées)
notifications_enabled_default = True
