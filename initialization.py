import json
import os
from constants import fichier_sauvegarde, fichier_encodes
from logger import setup_logger

logger = setup_logger(__name__)


def vider_fichiers():
    """
    Vide les fichiers temporaires au démarrage
    """
    try:
        logger.info("Nettoyage des fichiers temporaires en cours...")

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

        logger.info("Nettoyage des fichiers temporaires terminé")
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage des fichiers: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    vider_fichiers()
