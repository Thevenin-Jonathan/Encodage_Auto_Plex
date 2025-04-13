import os
import logging
from logging.handlers import RotatingFileHandler
import datetime
import sys

# Définir le chemin de base en fonction de l'exécution en tant que script ou exécutable
if getattr(sys, "frozen", False):
    # Mode exécutable - utiliser le dossier où se trouve l'exécutable
    BASE_PATH = os.path.dirname(sys.executable)
else:
    # Mode développement - utiliser le dossier du script
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))

# Créer le dossier logs s'il n'existe pas
logs_dir = os.path.join(BASE_PATH, "logs")
os.makedirs(logs_dir, exist_ok=True)


# Configuration du logger
def setup_logger(name):
    logger = logging.getLogger(name)

    # Si le logger est déjà configuré, le retourner directement
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Format du log
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    # Handler pour le fichier avec rotation automatique
    log_file = os.path.join(
        logs_dir, f"encodage_{datetime.date.today().strftime('%Y-%m-%d')}.log"
    )

    # Rotation des fichiers: taille max 10MB, garder 5 fichiers d'archives
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10MB
        backupCount=5,  # Conserver 5 fichiers de backup
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Ajouter uniquement le handler pour le fichier
    logger.addHandler(file_handler)

    return logger


def colored_log(logger, message, level="INFO", color=None):
    """Ajoute un log avec une couleur personnalisée"""
    # Créer un LogRecord avec un attribut custom_color
    record = logger.makeRecord(
        logger.name, getattr(logging, level), "", 0, message, None, None
    )
    record.custom_color = color
    logger.handle(record)
