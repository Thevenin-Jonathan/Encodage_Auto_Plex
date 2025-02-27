from queue import Queue
from threading import Thread
from surveillance import surveille_dossiers
from encoding import traitement_file_encodage
from constants import dossiers_presets
from initialization import vider_fichiers
from logger import setup_logger
import os

# Configurer le logger pour le module principal
logger = setup_logger(__name__)

# Définir le titre de la fenêtre du terminal
os.system(f"title Encodage_Auto_Plex")
logger.info("=== Démarrage de l'application Encodage_Auto_Plex ===")

# Vider les fichiers détectés et encodés au démarrage
logger.info("Nettoyage des fichiers temporaires")
vider_fichiers()

# File d'attente pour les encodages
file_encodage = Queue()
logger.info("Initialisation de la file d'attente d'encodage")

# Démarrer le thread de traitement de la file d'attente d'encodage
logger.info("Démarrage du thread d'encodage")
thread_encodage = Thread(
    target=traitement_file_encodage, args=(file_encodage,), daemon=True
)
thread_encodage.start()

# Surveiller les dossiers spécifiés
logger.info(f"Démarrage de la surveillance des dossiers")
surveille_dossiers(dossiers_presets, file_encodage)
