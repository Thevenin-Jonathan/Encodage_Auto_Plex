import os
import time
from datetime import datetime
from file_handling import charger_fichiers, sauvegarder_fichiers

# Fichier de sauvegarde des fichiers détectés et encodés
fichier_sauvegarde = "fichiers_detectes.json"
fichier_encodes = "fichiers_encodes.json"

# Extensions de fichiers à surveiller
extensions = [".mkv", ".mp4", ".avi"]

# Obtenir l'horodatage actuel


def horodatage():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Obtenir la liste initiale des fichiers dans un dossier


def obtenir_fichiers(dossier):
    try:
        return {
            fichier
            for fichier in os.listdir(dossier)
            if os.path.splitext(fichier)[1].lower() in extensions
        }
    except FileNotFoundError:
        print(f"{horodatage()} 📁 Dossier non trouvé: {dossier}")
        return set()


# Fonction pour surveiller les dossiers


def surveille_dossiers(dossiers_presets, file_encodage):
    fichiers_detectes = charger_fichiers(fichier_sauvegarde)
    fichiers_encodes = charger_fichiers(fichier_encodes)
    fichiers_initiaux = {
        dossier: obtenir_fichiers(dossier) for dossier in dossiers_presets
    }

    print(f"{horodatage()} 🔍 Surveillance initiale des dossiers terminée.")

    while True:
        for dossier, preset in dossiers_presets.items():
            fichiers_actuels = obtenir_fichiers(dossier)
            nouveaux_fichiers = fichiers_actuels - fichiers_initiaux[dossier]
            fichiers_supprimes = fichiers_initiaux[dossier] - fichiers_actuels

            if nouveaux_fichiers:
                for fichier in nouveaux_fichiers:
                    if fichier.endswith("_encoded.mp4"):
                        # Ignorer les fichiers déjà encodés
                        continue
                    print(
                        f"{horodatage()} 🆕 Nouveau fichier détecté dans {
                          dossier}: {fichier}"
                    )
                    if dossier not in fichiers_detectes:
                        fichiers_detectes[dossier] = []
                    fichiers_detectes[dossier].append(fichier)

                    # Ajouter le fichier à la file d'attente s'il n'a pas déjà été encodé
                    if fichier not in fichiers_encodes.get(dossier, []):
                        file_encodage.put((dossier, fichier, preset))
                        if dossier not in fichiers_encodes:
                            fichiers_encodes[dossier] = []
                        fichiers_encodes[dossier].append(fichier)
                        print(
                            f"{horodatage()} 📥 Fichier ajouté à la file d'attente d'encodage: {fichier}"
                        )

            if fichiers_supprimes:
                for fichier in fichiers_supprimes:
                    print(
                        f"{horodatage()} 🗑️ Fichier supprimé dans {
                          dossier}: {fichier}"
                    )
                    if (
                        dossier in fichiers_detectes
                        and fichier in fichiers_detectes[dossier]
                    ):
                        fichiers_detectes[dossier].remove(fichier)
                    if (
                        dossier in fichiers_encodes
                        and fichier in fichiers_encodes[dossier]
                    ):
                        fichiers_encodes[dossier].remove(fichier)

            fichiers_initiaux[dossier] = fichiers_actuels

        # Sauvegarder l'état actuel des fichiers détectés et encodés
        sauvegarder_fichiers(fichier_sauvegarde, fichiers_detectes)
        sauvegarder_fichiers(fichier_encodes, fichiers_encodes)
        time.sleep(10)
