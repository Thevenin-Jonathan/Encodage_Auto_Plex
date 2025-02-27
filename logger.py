import os
import logging
from logging.handlers import RotatingFileHandler
import datetime

# Créer le dossier logs s'il n'existe pas
logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(logs_dir, exist_ok=True)


# Configuration du logger
def setup_logger(name):
    logger = logging.getLogger(name)

    # Si le logger est déjà configuré, le retourner directement
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Format du log
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    # Handler pour le fichier uniquement (pas de console)
    log_file = os.path.join(
        logs_dir, f"encodage_{datetime.date.today().strftime('%Y-%m-%d')}.log"
    )
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10485760, backupCount=5
    )  # ~10MB max
    file_handler.setLevel(logging.DEBUG)  # DEBUG et plus pour le fichier
    file_handler.setFormatter(formatter)

    # Ajouter uniquement le handler pour le fichier
    logger.addHandler(file_handler)

    return logger
