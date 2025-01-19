from queue import Queue
from threading import Thread
import time
from surveillance import surveille_dossiers
from encoding import traitement_file_encodage

# Dossiers à surveiller et leurs presets HandBrake
dossiers_presets = {
    "D:/Torrents/Dessins_animes": "Dessins animes FR 1000kbps",
    "D:/Torrents/Films": "1080p HD-Light 1500kbps",
    "D:/Torrents/Manga": "Mangas MULTI 1000kbps",
    "D:/Torrents/Manga_VO": "Mangas MULTI 1000kbps",
    "D:/Torrents/Series": "1080p HD-Light 1500kbps"
}

# File d'attente pour les encodages
file_encodage = Queue()

# Démarrer le thread de traitement de la file d'attente d'encodage
thread_encodage = Thread(target=traitement_file_encodage, args=(
    file_encodage,), daemon=True)
thread_encodage.start()

# Surveiller les dossiers spécifiés
surveille_dossiers(dossiers_presets, file_encodage)
