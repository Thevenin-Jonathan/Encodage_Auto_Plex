from queue import Queue
from threading import Thread
from surveillance import surveille_dossiers
from encoding import traitement_file_encodage
from constants import dossiers_presets
from initialization import vider_fichiers

# Vider les fichiers détectés et encodés au démarrage
vider_fichiers()

# File d'attente pour les encodages
file_encodage = Queue()

# Démarrer le thread de traitement de la file d'attente d'encodage
thread_encodage = Thread(
    target=traitement_file_encodage, args=(file_encodage,), daemon=True
)
thread_encodage.start()

# Surveiller les dossiers spécifiés
surveille_dossiers(dossiers_presets, file_encodage)
