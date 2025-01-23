import json
import os
from constants import fichier_sauvegarde, fichier_encodes


def vider_fichiers():
    """
    Vide toutes les listes des fichiers 'fichiers_detectes.json' et 'fichiers_encodes.json'.
    """
    fichiers = [fichier_sauvegarde, fichier_encodes]

    for fichier in fichiers:
        if os.path.exists(fichier):
            with open(fichier, "r") as f:
                data = json.load(f)

            # Vider toutes les listes dans le dictionnaire
            for key in data:
                data[key] = []

            # Sauvegarder les modifications
            with open(fichier, "w") as f:
                json.dump(data, f, indent=4)
        else:
            print(f"Le fichier {fichier} n'existe pas.")


if __name__ == "__main__":
    vider_fichiers()
