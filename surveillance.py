import os
import time
from file_handling import charger_fichiers, sauvegarder_fichiers
from constants import debug_mode, fichier_encodes, fichier_sauvegarde, extensions
from utils import horodatage
from logger import setup_logger

logger = setup_logger(__name__)


def obtenir_fichiers(dossier):
    """
    Retourne un ensemble de fichiers présents dans le dossier et ses sous-dossiers dont les extensions
    correspondent à celles spécifiées dans la liste 'extensions'.
    """
    fichiers = set()
    for root, _, files in os.walk(dossier):
        for fichier in files:
            if os.path.splitext(fichier)[1].lower() in extensions:
                fichiers.add(os.path.join(root, fichier))
    return fichiers


def surveille_dossiers(
    dossiers_presets, file_encodage, signals=None, control_flags=None
):
    """
    Surveille les dossiers spécifiés et ajoute les nouveaux fichiers détectés
    à la file d'attente d'encodage. La fonction ignore les fichiers déjà encodés
    et sauvegarde l'état actuel des fichiers détectés et encodés.

    Arguments:
    dossiers_presets -- Dictionnaire contenant les dossiers à surveiller et leurs presets associés.
    file_encodage -- Queue pour la file d'attente d'encodage.
    signals -- Les signaux pour mettre à jour l'interface graphique.
    control_flags -- Les drapeaux de contrôle.
    """
    logger.info(f"Démarrage de la surveillance sur {len(dossiers_presets)} dossier(s)")

    try:
        # Charger les fichiers détectés et encodés à partir des fichiers de sauvegarde
        fichiers_detectes = charger_fichiers(fichier_sauvegarde)
        fichiers_encodes = charger_fichiers(fichier_encodes)

        # Obtenir la liste initiale des fichiers dans chaque dossier
        fichiers_initiaux = {
            dossier: obtenir_fichiers(dossier) for dossier in dossiers_presets
        }

        print(f"{horodatage()} 🔍 Surveillance initiale des dossiers terminée.")

        while True:
            for dossier, preset in dossiers_presets.items():
                # Obtenir la liste actuelle des fichiers dans le dossier
                fichiers_actuels = obtenir_fichiers(dossier)
                # Déterminer les nouveaux fichiers et les fichiers supprimés
                nouveaux_fichiers = fichiers_actuels - fichiers_initiaux[dossier]
                fichiers_supprimes = fichiers_initiaux[dossier] - fichiers_actuels

                # Traiter les nouveaux fichiers détectés
                if nouveaux_fichiers:
                    for fichier in nouveaux_fichiers:
                        # Vérifier si le fichier se termine par l'une des extensions encodées
                        if any(
                            fichier.endswith(f"_encoded{ext}") for ext in extensions
                        ):
                            # Ignorer les fichiers déjà encodés
                            continue
                        if debug_mode:
                            print(
                                f"{horodatage()} 🆕 Nouveau fichier détecté dans {dossier}: {fichier}"
                            )
                        logger.info(
                            f"Nouveau fichier détecté: {fichier} dans {dossier}"
                        )
                        if dossier not in fichiers_detectes:
                            fichiers_detectes[dossier] = []
                        fichiers_detectes[dossier].append(fichier)

                        # Ajouter un délai après la détection d'un fichier
                        logger.info(
                            f"Attente de 5 secondes pour s'assurer que le fichier est bien disponible..."
                        )
                        time.sleep(5)

                        # Vérifier si le fichier est toujours accessible
                        if os.path.exists(fichier) and os.access(fichier, os.R_OK):
                            # Ajouter le fichier à la file d'attente s'il n'a pas déjà été encodé
                            if fichier not in fichiers_encodes.get(dossier, []):
                                file_encodage.put(
                                    {
                                        "folder": dossier,
                                        "file": fichier,
                                        "preset": preset,
                                    }
                                )
                                if dossier not in fichiers_encodes:
                                    fichiers_encodes[dossier] = []
                                fichiers_encodes[dossier].append(fichier)
                                print(
                                    f"{horodatage()} 📥 Fichier ajouté à la file d'attente d'encodage: {fichier}"
                                )
                                logger.info(
                                    f"Fichier {fichier} ajouté à la file d'encodage avec preset {preset}"
                                )
                                # Mettre à jour l'interface graphique
                                if signals:
                                    # Créer une copie temporaire de la queue pour l'affichage
                                    queue_items = list(file_encodage.queue)
                                    signals.update_queue.emit(queue_items)
                        else:
                            logger.error(
                                f"Le fichier {fichier} n'est plus accessible, ignoré"
                            )

                # Traiter les fichiers supprimés détectés
                if fichiers_supprimes:
                    for fichier in fichiers_supprimes:
                        if debug_mode:
                            print(
                                f"{horodatage()} 🗑️ Fichier supprimé dans {dossier}: {fichier}"
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

                # Mettre à jour la liste des fichiers initialement détectés pour le prochain cycle
                fichiers_initiaux[dossier] = fichiers_actuels

            # Sauvegarder l'état actuel des fichiers détectés et encodés
            sauvegarder_fichiers(fichier_sauvegarde, fichiers_detectes)
            sauvegarder_fichiers(fichier_encodes, fichiers_encodes)

            # Attendre avant le prochain cycle de surveillance
            time.sleep(10)
    except Exception as e:
        logger.error(
            f"Erreur dans la surveillance des dossiers: {str(e)}", exc_info=True
        )
        raise
