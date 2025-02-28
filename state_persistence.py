import os
import json
import logging
from datetime import datetime

# Configuration du logger
logger = logging.getLogger(__name__)

# Chemin du fichier de sauvegarde d'état
state_file = os.path.join(os.path.dirname(__file__), "interrupted_encodings.json")


def save_interrupted_encodings(current_encoding=None, encoding_queue=None):
    """
    Sauvegarde les informations sur l'encodage interrompu et la file d'attente dans un fichier JSON.
    Ne sauvegarde pas l'état détaillé de l'encodage, juste les fichiers à encoder.

    Args:
        current_encoding (dict, optional): Informations sur l'encodage en cours.
            Format: {"file": chemin_fichier, "preset": preset, "folder": dossier}
        encoding_queue (list, optional): Liste des encodages en attente.
            Format: [{"file": chemin_fichier, "preset": preset, "folder": dossier}, ...]

    Returns:
        bool: True si la sauvegarde a réussi, False sinon.
    """
    try:
        # Vérifier si le chemin du fichier en cours est un chemin absolu
        if current_encoding and "file" in current_encoding:
            fichier = current_encoding["file"]
            if fichier and not os.path.isabs(fichier):
                logger.warning(
                    f"Le chemin du fichier en cours n'est pas absolu: {fichier}"
                )
                # On ne modifie pas le chemin ici, on le laisse tel quel
                # Le code dans main.py se chargera de trouver le chemin complet lors du chargement

        # Vérifier si les chemins des fichiers dans la file d'attente sont des chemins absolus
        if encoding_queue:
            for item in encoding_queue:
                if "file" in item:
                    fichier = item["file"]
                    if fichier and not os.path.isabs(fichier):
                        logger.warning(
                            f"Le chemin d'un fichier dans la file d'attente n'est pas absolu: {fichier}"
                        )
                        # On ne modifie pas le chemin ici, on le laisse tel quel
                        # Le code dans main.py se chargera de trouver le chemin complet lors du chargement

        # Préparer les données à sauvegarder
        # Charger l'état existant s'il y en a un
        if os.path.exists(state_file):
            with open(state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
        else:
            state = {}
        old_current_encoding = state.get("current_encoding", None)

        state = {
            "timestamp": datetime.now().isoformat(),
            "current_encoding": (
                current_encoding
                if current_encoding is not None
                else old_current_encoding
            ),
            "encoding_queue": encoding_queue if encoding_queue else [],
        }
        # Sauvegarder dans un fichier JSON
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

        logger.info(f"Encodages interrompus sauvegardés dans {state_file}")
        return True

    except Exception as e:
        logger.error(
            f"Erreur lors de la sauvegarde des encodages interrompus: {str(e)}"
        )
        return False


def load_interrupted_encodings():
    """
    Charge les informations sur les encodages interrompus depuis le fichier JSON.

    Returns:
        dict: Informations sur les encodages interrompus ou None si aucun n'est trouvé ou en cas d'erreur.
            Format: {
                "timestamp": horodatage,
                "current_encoding": {"file": chemin_fichier, "preset": preset, "folder": dossier},
                "encoding_queue": [{"file": chemin_fichier, "preset": preset, "folder": dossier}, ...]
            }
    """
    if not os.path.exists(state_file):
        logger.info("Aucun fichier d'encodages interrompus trouvé")
        return None

    try:
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)

        logger.info(f"Encodages interrompus chargés depuis {state_file}")
        return state

    except Exception as e:
        logger.error(f"Erreur lors du chargement des encodages interrompus: {str(e)}")
        return None


def clear_interrupted_encodings():
    """
    Supprime le fichier d'encodages interrompus s'il existe.

    Returns:
        bool: True si la suppression a réussi ou si le fichier n'existait pas, False en cas d'erreur.
    """
    if not os.path.exists(state_file):
        return True

    try:
        os.remove(state_file)
        logger.info(f"Fichier d'encodages interrompus supprimé: {state_file}")
        return True

    except Exception as e:
        logger.error(
            f"Erreur lors de la suppression du fichier d'encodages interrompus: {str(e)}"
        )
        return False


def has_interrupted_encodings():
    """
    Vérifie si un fichier d'encodages interrompus existe.

    Returns:
        bool: True si un fichier d'encodages interrompus existe, False sinon.
    """
    return os.path.exists(state_file)
