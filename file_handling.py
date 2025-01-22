import os
import json


def charger_fichiers(fichier):
    """
    Charge les fichiers détectés et encodés à partir d'un fichier JSON de sauvegarde.

    Arguments:
    fichier -- Chemin du fichier JSON à charger.

    Retourne:
    Un dictionnaire contenant les données chargées si le fichier existe,
    un dictionnaire vide sinon.
    """
    if os.path.exists(fichier):
        with open(fichier, "r") as f:
            return json.load(f)
    return {}


def sauvegarder_fichiers(fichier, fichiers):
    """
    Sauvegarde les fichiers détectés et encodés dans un fichier JSON de sauvegarde.

    Arguments:
    fichier -- Chemin du fichier JSON où sauvegarder les données.
    fichiers -- Dictionnaire contenant les données à sauvegarder.
    """
    with open(fichier, "w") as f:
        json.dump(fichiers, f, indent=4)
