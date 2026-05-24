import os, json, logging, tempfile
from datetime import datetime
from constants import state_file

# Configuration du logger
logger = logging.getLogger(__name__)

# Chemin du fichier de sauvegarde d'état
STATE_FILE = state_file


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
        # Charger l'état existant si possible
        state = {}
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r", encoding="utf-8") as f:
                    state = json.load(f)
            except Exception:
                # JSON corrompu → on repart propre
                state = {}

        old_current_encoding = state.get("current_encoding")

        state = {
            "timestamp": datetime.now().isoformat(),
            "current_encoding": (
                current_encoding if current_encoding else old_current_encoding
            ),
            "encoding_queue": encoding_queue if encoding_queue else [],
        }

        # Écriture atomique
        dir_name = os.path.dirname(STATE_FILE)
        with tempfile.NamedTemporaryFile(
            "w", dir=dir_name, delete=False, encoding="utf-8"
        ) as tmp:
            json.dump(state, tmp, ensure_ascii=False, indent=2)
            temp_name = tmp.name

        os.replace(temp_name, STATE_FILE)

        logger.info(f"Encodages interrompus sauvegardés dans {STATE_FILE}")
        return True

    except Exception as e:
        logger.error(
            f"Erreur lors de la sauvegarde des encodages interrompus: {str(e)}"
        )
        return


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
    if not os.path.exists(STATE_FILE):
        logger.info("Aucun fichier d'encodages interrompus trouvé")
        return None

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)

        logger.info(f"Encodages interrompus chargés depuis {STATE_FILE}")
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
    if not os.path.exists(STATE_FILE):
        return True

    try:
        os.remove(STATE_FILE)
        logger.info(f"Fichier d'encodages interrompus supprimé: {STATE_FILE}")
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
    return os.path.exists(STATE_FILE)
