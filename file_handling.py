import os
import json

# Charger les fichiers détectés et encodés à partir des fichiers de sauvegarde


def charger_fichiers(fichier):
    if os.path.exists(fichier):
        with open(fichier, 'r') as f:
            return json.load(f)
    return {}

# Sauvegarder les fichiers détectés et encodés dans les fichiers de sauvegarde


def sauvegarder_fichiers(fichier, fichiers):
    with open(fichier, 'w') as f:
        json.dump(fichiers, f, indent=4)
