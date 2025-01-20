import os
import json
import subprocess
from constants import dossier_encodage_manuel, dossier_sortie, horodatage


def obtenir_pistes(filepath):
    commande = ["HandBrakeCLI", "-i", filepath, "--scan", "--json"]
    result = subprocess.run(commande, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Erreur lors de l'exécution de HandBrakeCLI: {result.stderr}")
        return None
    if not result.stdout.strip():  # Vérification supplémentaire
        print("Erreur : la sortie de HandBrakeCLI est vide.")
        return None
    try:
        # Extraire uniquement la partie JSON correcte de la sortie
        json_start = result.stdout.find(
            '{', result.stdout.find('JSON Title Set:'))
        json_end = result.stdout.rfind('}') + 1
        json_str = result.stdout[json_start:json_end]
        info_pistes = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Erreur de décodage JSON: {e}")
        return None
    return info_pistes


def verifier_dossiers():
    if not os.path.exists(dossier_sortie):
        os.makedirs(dossier_sortie)
    if not os.path.exists(dossier_encodage_manuel):
        os.makedirs(dossier_encodage_manuel)

# Fonction pour copier un fichier dans le dossier d'encodage manuel en évitant les conflits de noms


def copier_fichier_dossier_encodage_manuel(filepath):
    base_name = os.path.basename(filepath)
    new_path = os.path.join(dossier_encodage_manuel, base_name)
    if os.path.exists(new_path):
        base, extension = os.path.splitext(base_name)
        counter = 1
        while os.path.exists(new_path):
            new_path = os.path.join(dossier_encodage_manuel, f"{
                                    base}_{counter}{extension}")
            counter += 1
    os.rename(filepath, new_path)
    print(f"{horodatage()} 📁 Fichier déplacé pour encodage manuel: {
          os.path.basename(new_path)}")
