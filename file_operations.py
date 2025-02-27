import logging
import os
import json
import subprocess
import sys
from constants import (
    debug_mode,
    dossier_encodage_manuel,
    dossier_sortie,
    fichier_encodage_manuel,
)
from logger import colored_log, setup_logger
from utils import horodatage

# Configuration du logger
logger = setup_logger(__name__)


def obtenir_pistes(filepath):
    """
    Exécute HandBrakeCLI pour scanner le fichier spécifié et obtenir des informations sur les pistes
    sous forme de JSON.

    Arguments:
    filepath -- Chemin du fichier à analyser.

    Retourne:
    Un dictionnaire contenant les informations des pistes si réussi, None sinon.
    """
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
        json_start = result.stdout.find("{", result.stdout.find("JSON Title Set:"))
        json_end = result.stdout.rfind("}") + 1
        json_str = result.stdout[json_start:json_end]
        info_pistes = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Erreur de décodage JSON: {e}")
        return None
    return info_pistes


def verifier_dossiers():
    """
    Vérifie si les dossiers de sortie et d'encodage manuel existent, et les crée sinon.
    """
    if not os.path.exists(dossier_sortie):
        os.makedirs(dossier_sortie)
    if not os.path.exists(dossier_encodage_manuel):
        os.makedirs(dossier_encodage_manuel)


def ajouter_fichier_a_liste_encodage_manuel(
    filepath, nom_fichier, preset=None, signals=None
):
    """
    Ajoute le fichier spécifié et son preset dans la liste d'encodage manuel,
    en évitant les doublons.

    Arguments:
    filepath -- Chemin du fichier à ajouter.
    preset -- Preset à utiliser pour l'encodage (optionnel).
    signals -- Objets de signaux pour mettre à jour l'interface (optionnel).
    """
    base_name = os.path.basename(filepath)
    liste_fichiers_path = fichier_encodage_manuel
    # Utiliser le logger déjà défini au niveau du module
    # au lieu de créer une nouvelle instance dans la fonction

    # Préparer la ligne à ajouter
    if preset:
        new_line = f"{filepath}|{preset}"
    else:
        new_line = f"{base_name}"

    # Instructions de débogage
    if debug_mode:
        print(f"Chemin du fichier d'encodage manuel : {liste_fichiers_path}")

    try:
        # Créer le fichier s'il n'existe pas
        if not os.path.exists(liste_fichiers_path):
            open(liste_fichiers_path, "w").close()
            print(f"Fichier créé : {liste_fichiers_path}")
            existing_lines = []
        else:
            # Lire les lignes existantes
            with open(liste_fichiers_path, "r", encoding="utf-8") as file:
                existing_lines = [line.strip() for line in file.readlines()]

        # Vérifier si la ligne existe déjà
        if new_line in existing_lines:
            colored_log(
                logger,  # Utiliser le logger global
                f"Le fichier {base_name} est déjà dans la liste d'encodage manuel",
                "INFO",
                "orange",
            )
            return True

        colored_log(
            logger,  # Utiliser le logger global
            f"Ajout de {nom_fichier} à la liste des encodages manuels (pas de piste audio compatible)",
            "INFO",
            "orange",
        )

        # Ajouter la nouvelle ligne
        with open(liste_fichiers_path, "a", encoding="utf-8") as file:
            file.write(new_line + "\n")
            print(
                f"{horodatage()} 📁 Fichier ajouté à la liste d'encodage manuel : {base_name} {'(preset: ' + preset + ')' if preset else ''}"
            )

        # Émettre le signal pour mettre à jour l'interface
        if signals and hasattr(signals, "update_manual_encodings"):
            signals.update_manual_encodings.emit()

        return True
    except Exception as e:
        print(f"Erreur lors de l'écriture dans le fichier : {e}")
        return False
