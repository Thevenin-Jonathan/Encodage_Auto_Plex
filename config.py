import json
import os
from constants import config_file
from logger import setup_logger

CONFIG_FILE = config_file

# Valeurs par défaut
DEFAULT_CONFIG = {"notifications_enabled": True}

# Configurer le logger pour le module principal
logger = setup_logger(__name__)


def save_config(config_data):
    """Sauvegarde la configuration dans un fichier JSON"""
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config_data, f)
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde de la configuration: {e}")


def load_config():
    """Charge la configuration depuis le fichier JSON"""
    if not os.path.exists(CONFIG_FILE):
        # Si le fichier n'existe pas, créer avec les valeurs par défaut
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
            # S'assurer que toutes les clés par défaut sont présentes
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            return config
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la configuration: {e}")
        return DEFAULT_CONFIG.copy()
