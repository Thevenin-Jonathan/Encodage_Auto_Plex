import json
from constants import config_file
from logger import setup_logger

CONFIG_FILE = config_file

# Configurer le logger pour le module principal
logger = setup_logger(__name__)


def load_config():
    """Charge la configuration depuis le fichier JSON sans fallback."""
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la configuration: {e}")
        raise


def save_config(config_data):
    """Sauvegarde la configuration dans un fichier JSON."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Erreur lors de la sauvegarde de la configuration: {e}")
        raise


def get_output_directories_for_surveillance():
    """Retourne les dossiers de sortie pour la surveillance."""
    config = load_config()
    return config.get("dossiers_sortie_surveillance", {})


def update_output_directory_for_source(dossier_source, nouveau_dossier):
    """Met à jour un dossier de sortie pour un dossier source."""
    config = load_config()

    if "dossiers_sortie_surveillance" not in config:
        config["dossiers_sortie_surveillance"] = {}

    config["dossiers_sortie_surveillance"][dossier_source] = nouveau_dossier
    save_config(config)

    logger.info(
        f"Dossier de sortie mis à jour pour '{dossier_source}': {nouveau_dossier}"
    )


def get_output_directory_for_source_folder(dossier_source):
    """Récupère le dossier de sortie pour un dossier source spécifique"""
    dossiers = get_output_directories_for_surveillance()
    from constants import dossier_sortie

    return dossiers.get(dossier_source, dossier_sortie)
