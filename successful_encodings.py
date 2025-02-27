import os
import json
import time
from datetime import datetime, timedelta
from logger import setup_logger

# Configuration du logger
logger = setup_logger(__name__)

# Chemin du fichier pour stocker les encodages réussis
SUCCESSFUL_ENCODINGS_FILE = os.path.join(os.path.dirname(__file__), "datas", "successful_encodings.json")

def ensure_file_exists():
    """
    S'assure que le fichier des encodages réussis existe.
    Crée le fichier et le dossier parent si nécessaire.
    """
    directory = os.path.dirname(SUCCESSFUL_ENCODINGS_FILE)
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    if not os.path.exists(SUCCESSFUL_ENCODINGS_FILE):
        with open(SUCCESSFUL_ENCODINGS_FILE, "w") as f:
            json.dump([], f)

def record_successful_encoding(file_path, file_size):
    """
    Enregistre un encodage réussi avec l'horodatage, le nom du fichier et sa taille.
    
    Arguments:
    file_path -- Chemin du fichier encodé
    file_size -- Taille du fichier en MB
    """
    ensure_file_exists()
    
    # Charger les encodages existants
    try:
        with open(SUCCESSFUL_ENCODINGS_FILE, "r") as f:
            encodings = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        encodings = []
    
    # Créer un nouvel enregistrement
    timestamp = time.time()
    filename = os.path.basename(file_path)
    
    new_encoding = {
        "timestamp": timestamp,
        "datetime": datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S"),
        "filename": filename,
        "file_path": file_path,
        "file_size": round(file_size, 2)  # Arrondir à 2 décimales
    }
    
    # Ajouter le nouvel enregistrement
    encodings.append(new_encoding)
    
    # Sauvegarder les encodages mis à jour
    with open(SUCCESSFUL_ENCODINGS_FILE, "w") as f:
        json.dump(encodings, f, indent=4)
    
    logger.info(f"Encodage réussi enregistré: {filename} ({round(file_size, 2)} MB)")

def get_recent_encodings(hours=72):
    """
    Récupère les encodages réussis des dernières heures spécifiées.
    
    Arguments:
    hours -- Nombre d'heures à remonter (par défaut 72)
    
    Retourne:
    Une liste d'encodages réussis, triée du plus récent au plus ancien
    """
    ensure_file_exists()
    
    try:
        with open(SUCCESSFUL_ENCODINGS_FILE, "r") as f:
            encodings = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []
    
    # Calculer le timestamp limite
    cutoff_time = time.time() - (hours * 3600)
    
    # Filtrer les encodages récents
    recent_encodings = [
        encoding for encoding in encodings 
        if encoding.get("timestamp", 0) >= cutoff_time
    ]
    
    # Trier par timestamp décroissant (plus récent en premier)
    recent_encodings.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    
    return recent_encodings