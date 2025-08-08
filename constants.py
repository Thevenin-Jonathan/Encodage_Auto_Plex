import sys
import os

# Définir le chemin de base en fonction de l'exécution en tant que script ou exécutable
if getattr(sys, "frozen", False):
    # Mode exécutable - utiliser le dossier où se trouve l'exécutable
    BASE_PATH = os.path.dirname(sys.executable)
else:
    BASE_PATH = os.path.dirname(__file__)

# Définir la variable debug_mode
debug_mode = True  # Change cette valeur à True pour activer le mode débogage

config_file = os.path.join(BASE_PATH, "datas", "config.json")

icon_file = os.path.join(BASE_PATH, "images", "ico.ico")

# Dossiers à surveiller et leurs presets HandBrake
dossiers_presets = {
    "D:/Torrents/Dessins animes VF": "Dessins animes VF",
    "D:/Torrents/Film VF": "Films - Series VF",
    "D:/Torrents/Film Jeunes VF": "Films - Series VF",
    "D:/Torrents/Series VF": "Films - Series VF",
    "D:/Torrents/Series Jeunes VF": "Films - Series VF",
    "D:/Torrents/Series Jeunes MULTI": "Films - Series VF",
    "D:/Torrents/Film MULTI": "Films - Series MULTI",
    "D:/Torrents/Film Jeunes MULTI": "Films - Series MULTI",
    "D:/Torrents/Series MULTI": "Films - Series MULTI",
    "D:/Torrents/Mangas MULTI": "Mangas MULTI",
    "D:/Torrents/Mangas VO": "Mangas VO",
    "D:/Torrents/Film 4K": "4K - 10bits",
    "D:/Torrents/Serie 4K": "4K - 10bits",
}

# Configuration des dossiers de sortie pour chaque dossier surveillé
# Chaque dossier surveillé a son propre dossier de sortie correspondant
dossiers_sortie_surveillance = {
    "D:/Torrents/Dessins animes VF": "D:/Ripped/seriesJeunes",
    "D:/Torrents/Film VF": "D:/Ripped/films",
    "D:/Torrents/Film Jeunes VF": "D:/Ripped/filmsJeunes",
    "D:/Torrents/Series VF": "D:/Ripped/series",
    "D:/Torrents/Series Jeunes VF": "D:/Ripped/seriesJeunes",
    "D:/Torrents/Series Jeunes MULTI": "D:/Ripped/seriesJeunes",
    "D:/Torrents/Film MULTI": "D:/Ripped/films",
    "D:/Torrents/Film Jeunes MULTI": "D:/Ripped/filmsJeunes",
    "D:/Torrents/Series MULTI": "D:/Ripped/series",
    "D:/Torrents/Mangas MULTI": "D:/Ripped/seriesJeunes",
    "D:/Torrents/Mangas VO": "D:/Ripped/seriesJeunes",
    "D:/Torrents/Film 4K": "D:/Ripped/films4K",
    "D:/Torrents/Serie 4K": "D:/Ripped/series4K",
}

# Chemin du dossier de sortie par défaut (pour compatibilité)
# Utilisé si aucun dossier spécifique n'est défini pour un dossier surveillé
dossier_sortie = "D:/Ripped"

# Fichier de presets personnalisés
fichier_presets = os.path.join(BASE_PATH, "datas", "custom_presets.json")

# Fichier de sauvegarde des fichiers détectés et encodés
fichier_sauvegarde = os.path.join(BASE_PATH, "datas", "fichiers_detectes.json")
fichier_encodes = os.path.join(BASE_PATH, "datas", "fichiers_encodes.json")

# Fichier qui enregistre les titres de sous-titres collectés
fichier_sous_titres = os.path.join(
    BASE_PATH, "datas", "subtitle_titles_collection.json"
)

# Extensions de fichiers à surveiller
extensions = [".mkv", ".mp4", ".avi"]

# Critères pour filtrer les pistes françaises indésirables
criteres_audios = [
    "vfq",
    "ad",
    "audiodescription",
    "quebec",
    "descriptive",
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
