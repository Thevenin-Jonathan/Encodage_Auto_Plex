# Définir la variable debug_mode
debug_mode = False  # Change cette valeur à True pour activer le mode débogage

# Dossiers à surveiller et leurs presets HandBrake
dossiers_presets = {
    "D:/Torrents/Dessins_animes": "Dessins animes FR 1000kbps",
    "D:/Torrents/Films": "1080p HD-Light 1500kbps",
    "D:/Torrents/Manga": "Mangas MULTI 1000kbps",
    "D:/Torrents/Manga_VO": "Mangas VO 1000kbps",
    "D:/Torrents/Series": "1080p HD-Light 1500kbps",
}

# Chemin du dossier de sortie pour les fichiers encodés
dossier_sortie = "D:/Ripped"

# Fichier de presets personnalisés
fichier_presets = "custom_presets.json"

# Fichier de sauvegarde des fichiers détectés et encodés
fichier_sauvegarde = "fichiers_detectes.json"
fichier_encodes = "fichiers_encodes.json"

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
criteres_sous_titres_supprimer = ["sdh", "malentendant"]

# Dossiers pour encodage manuel
dossier_encodage_manuel = "D:/Torrents/Encodage_manuel"

# Taille maximal des messages de notifications windows
maxsize_message = 70
