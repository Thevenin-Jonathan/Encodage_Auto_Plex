import os
from datetime import datetime

# Chemin du dossier de sortie pour les fichiers encodés
dossier_sortie = "D:/Ripped"

# Fichier de presets personnalisés
fichier_presets = 'custom_presets.json'

# Critères pour filtrer les pistes françaises indésirables
criteres_nom_pistes = ["VFQ", "CA", "AD", "audiodescription",
                       "Quebec", "Canad", "NAD", "Narration", "Descriptive Audio", "FR-AD"]

# Dossiers pour encodage manuel
dossier_encodage_manuel = "D:/Torrents/Encodage_manuel"

# Obtenir l'horodatage actuel


def horodatage():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
