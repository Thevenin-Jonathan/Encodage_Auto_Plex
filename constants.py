import os
from datetime import datetime

# Dossiers à surveiller et leurs presets HandBrake
dossiers_presets = {
    "D:/Torrents/Dessins_animes": "Dessins animes FR 1000kbps",
    "D:/Torrents/Films": "1080p HD-Light 1500kbps",
    "D:/Torrents/Manga": "Mangas MULTI 1000kbps",
    "D:/Torrents/Manga_VO": "Mangas VO 1000kbps",
    "D:/Torrents/Series": "1080p HD-Light 1500kbps"
}

# Chemin du dossier de sortie pour les fichiers encodés
dossier_sortie = "D:/Ripped"

# Fichier de presets personnalisés
fichier_presets = 'custom_presets.json'

# Critères pour filtrer les pistes françaises indésirables
criteres_audios = ["VFQ", "CA", "AD", "audiodescription",
                   "Quebec", "Canad", "NAD", "Narration", "Descriptive Audio", "FR-AD"]

# Critères pour les sous-titres
criteres_sous_titres_burn = ["forced", "forces", "forcés", "forcé"]
criteres_sous_titres_supprimer = ["SDH", "malentendant"]

# Dossiers pour encodage manuel
dossier_encodage_manuel = "D:/Torrents/Encodage_manuel"

# Taille maximal des messages de notifications windows
maxsize_message = 70

# Obtenir l'horodatage actuel


def horodatage():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
