import json
import os
from constants import config_file
from logger import setup_logger

CONFIG_FILE = config_file

# Valeurs par défaut
DEFAULT_CONFIG = {
    "notifications_enabled": True,
    "dossiers_sortie_surveillance": {
        "D:/Torrents/Dessins animes VF": "D:/Ripped/seriesJeunes",
        "D:/Torrents/Film VF": "D:/Ripped/films",
        "D:/Torrents/Film Jeunes VF": "D:/Ripped/filmsJeunes",
        "D:/Torrents/Series VF": "D:/Ripped/series",
        "D:/Torrents/Film MULTI": "D:/Ripped/films",
        "D:/Torrents/Film Jeunes MULTI": "D:/Ripped/filmsJeunes",
        "D:/Torrents/Series MULTI": "D:/Ripped/series",
        "D:/Torrents/Mangas MULTI": "D:/Ripped/seriesJeunes",
        "D:/Torrents/Mangas VO": "D:/Ripped/seriesJeunes",
        "D:/Torrents/Film 4K": "D:/Ripped/films4K",
        "D:/Torrents/Serie 4K": "D:/Ripped/series4K",
        "D:/Torrents/Series Jeunes VF": "D:/Ripped/seriesJeunes",
        "D:/Torrents/Series Jeunes MULTI": "D:/Ripped/seriesJeunes",
    },
}

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


def get_output_directories_for_surveillance():
    """Récupère les dossiers de sortie pour chaque dossier surveillé depuis la configuration"""
    config = load_config()
    return config.get(
        "dossiers_sortie_surveillance", DEFAULT_CONFIG["dossiers_sortie_surveillance"]
    )


def update_output_directory_for_source(dossier_source, nouveau_dossier):
    """Met à jour le dossier de sortie pour un dossier source spécifique"""
    config = load_config()
    if "dossiers_sortie_surveillance" not in config:
        config["dossiers_sortie_surveillance"] = DEFAULT_CONFIG[
            "dossiers_sortie_surveillance"
        ].copy()

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


def get_output_directories():
    """Récupère les dossiers de sortie pour chaque preset depuis la configuration
    DEPRECATED: Utilisez get_output_directories_for_surveillance() à la place"""
    config = load_config()
    return config.get("dossiers_sortie_presets", {})


def update_output_directory(preset, nouveau_dossier):
    """Met à jour le dossier de sortie pour un preset spécifique
    DEPRECATED: Utilisez update_output_directory_for_source() à la place"""
    config = load_config()
    if "dossiers_sortie_presets" not in config:
        config["dossiers_sortie_presets"] = {}

    config["dossiers_sortie_presets"][preset] = nouveau_dossier
    save_config(config)
    logger.info(f"Dossier de sortie mis à jour pour '{preset}': {nouveau_dossier}")


def get_output_directory_for_preset(preset):
    """Récupère le dossier de sortie pour un preset spécifique
    DEPRECATED: Utilisez get_output_directory_for_source_folder() à la place"""
    dossiers = get_output_directories()
    from constants import dossier_sortie

    return dossiers.get(preset, dossier_sortie)
