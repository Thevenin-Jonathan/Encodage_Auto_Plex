import threading
import os
import subprocess
import re
import time
from tqdm import tqdm
from audio_selection import selectionner_pistes_audio
from subtitle_selection import selectionner_sous_titres
from constants import (
    dossier_sortie,
    debug_mode,
    fichier_presets,
)
from utils import horodatage, tronquer_nom_fichier
from file_operations import (
    obtenir_pistes,
    verifier_dossiers,
    ajouter_fichier_a_liste_encodage_manuel,
)
from command_builder import construire_commande_handbrake
from notifications import (
    notifier_encodage_lancement,
    notifier_encodage_termine,
    notifier_erreur_encodage,
)
from logger import setup_logger

# Configuration du logger
logger = setup_logger(__name__)

# Verrou pour synchroniser l'accès à la console
console_lock = threading.Lock()


def read_output(pipe, process_output):
    """
    Lit les sorties standard (stdout) et les erreurs (stderr) d'un processus en cours
    et les affiche dans la console tout en les ajoutant à une liste.

    Arguments:
    pipe -- Flux de sortie ou d'erreur du processus.
    process_output -- Liste pour stocker les sorties lues.
    """
    for line in iter(pipe.readline, ""):
        with console_lock:
            print(line, end="")
        process_output.append(line)
    pipe.close()


def normaliser_chemin(chemin):
    return chemin.replace("\\", "/")


def lancer_encodage_avec_gui(
    fichier, preset, dossier, signals=None, control_flags=None
):
    logger = setup_logger(__name__)

    # Normaliser les chemins (remplacer les antislash par des slash)
    fichier = normaliser_chemin(fichier)

    # Récupérer uniquement le nom du fichier
    nom_fichier = os.path.basename(fichier)
    short_fichier = tronquer_nom_fichier(nom_fichier)
    base_nom, extension = os.path.splitext(nom_fichier)
    fichier_sortie = f"{base_nom}_encoded.mkv"  # Toujours utiliser .mkv comme extension
    chemin_sortie = normaliser_chemin(os.path.join(dossier_sortie, fichier_sortie))

    # Mettre à jour le chemin de sortie dans l'interface si disponible
    if signals and hasattr(signals, "update_output_path"):
        signals.update_output_path.emit(chemin_sortie)

    # Afficher les informations du fichier dans l'interface
    if signals and hasattr(signals, "update_file_info"):
        signals.update_file_info.emit(short_fichier, preset)

    # Vérifier si le fichier existe et est accessible
    if not os.path.exists(fichier) or not os.access(fichier, os.R_OK):
        logger.error(f"Le fichier {fichier} n'existe pas ou n'est pas accessible")
        return False

    # Vérifier si le fichier a déjà été encodé
    if "_encoded" in nom_fichier:
        logger.warning(f"Le fichier {nom_fichier} a déjà été encodé, ignoré")
        return False

    try:
        # Initialiser le temps de début pour calculer le temps écoulé
        start_time = time.time()

        # Analyse des pistes du fichier
        info_pistes = obtenir_pistes(fichier)
        if info_pistes is None:
            logger.error(
                f"Erreur lors de l'obtention des informations des pistes pour {fichier}"
            )
            return False

        # Sélection des pistes audio selon le preset
        audio_tracks = selectionner_pistes_audio(info_pistes, preset)
        if audio_tracks is None:
            logger.warning(f"Pas de piste audio française disponibles.")
            return False

        # Sélection des sous-titres selon le preset
        subtitle_tracks, burn_track = selectionner_sous_titres(info_pistes, preset)

        # Préparer les options audio et sous-titres
        audio_option = (
            f'--audio={",".join(map(str, audio_tracks))}' if audio_tracks else ""
        )
        subtitle_option = (
            f'--subtitle={",".join(map(str, subtitle_tracks))}'
            if subtitle_tracks
            else ""
        )
        burn_option = (
            f"--subtitle-burned={subtitle_tracks.index(burn_track) + 1}"
            if burn_track is not None and subtitle_tracks
            else ""
        )

        # Construire la commande complète
        handbrake_cmd = [
            "HandBrakeCLI",
            "--preset-import-file",
            fichier_presets,
            "-i",
            fichier,
            "-o",
            chemin_sortie,
            "--preset",
            preset,
        ]

        # Ajouter les options audio et sous-titres si disponibles
        if audio_option:
            handbrake_cmd.append(audio_option)
        if subtitle_option:
            handbrake_cmd.append(subtitle_option)
        if burn_option:
            handbrake_cmd.append(burn_option)

        # Ajouter les paramètres d'encodage audio
        handbrake_cmd.extend(["--aencoder=aac", "--ab=192", "--mixdown=5point1"])

        if debug_mode:
            logger.info(f"Exécution de la commande: {' '.join(handbrake_cmd)}")
            print(f"{horodatage()} 🔧 Commande d'encodage : {' '.join(handbrake_cmd)}")

        # Exécuter HandBrake
        process = subprocess.Popen(
            handbrake_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            text=True,
        )

        # Variables pour suivre la progression
        last_percent_complete = -1
        percent_pattern = re.compile(r"Encoding:.*?(\d+\.\d+)\s?%")
        fps_pattern = re.compile(r"(\d+\.\d+) fps")
        time_pattern = re.compile(r"ETA (\d+h\d+m\d+s)")
        size_pattern = re.compile(r"size: (\d+\.\d+ [KMG]B)")

        # Initialiser percent_complete avant utilisation
        percent_complete = 0
        current_fps = "0.0"
        current_size = "0.0 MB"

        # Gérer la sortie du processus en continue
        while True:
            # Vérifier si l'encodage doit être interrompu
            if control_flags and control_flags.get("stop_all", False):
                logger.info(f"Arrêt de l'encodage demandé pour {short_fichier}")
                process.terminate()
                if signals:
                    signals.encoding_done.emit()
                return False

            # Vérifier si l'encodage doit être sauté
            if control_flags and control_flags.get("skip", False):
                logger.info(f"Saut de l'encodage demandé pour {short_fichier}")
                process.terminate()
                control_flags["skip"] = False
                if signals:
                    signals.encoding_done.emit()
                return False

            # Gérer la pause
            while control_flags and control_flags.get("pause", False):
                time.sleep(0.5)  # Attendre pendant la pause

            # Lire la sortie
            output = process.stdout.readline()
            if output == "" and process.poll() is not None:
                break

            if output:
                if debug_mode:
                    print(output.strip())

                # Extraire le pourcentage d'avancement
                match = percent_pattern.search(output)
                if match:
                    percent_complete = float(match.group(1))
                    if percent_complete != last_percent_complete:
                        last_percent_complete = percent_complete

                        # Mettre à jour la barre de progression
                        if signals and hasattr(signals, "update_progress"):
                            signals.update_progress.emit(int(percent_complete))

                        # Calculer le temps écoulé et restant
                        elapsed = time.time() - start_time
                        elapsed_str = f"{int(elapsed // 3600)}h{int((elapsed % 3600) // 60)}m{int(elapsed % 60)}s"

                        # Estimer le temps restant
                        if percent_complete > 0:
                            remaining = (
                                elapsed * (100 - percent_complete) / percent_complete
                            )
                            remaining_str = f"{int(remaining // 3600)}h{int((remaining % 3600) // 60)}m{int(remaining % 60)}s"
                        else:
                            remaining_str = "Calcul en cours..."

                        # Mettre à jour les infos de temps
                        if signals and hasattr(signals, "update_time_info"):
                            signals.update_time_info.emit(elapsed_str, remaining_str)

                # Extraire les informations d'encodage (fps, taille)
                fps_match = fps_pattern.search(output)
                if fps_match:
                    current_fps = fps_match.group(1)

                size_match = size_pattern.search(output)
                if size_match:
                    current_size = size_match.group(1)

                # Seulement mettre à jour l'interface si on a de nouvelles informations
                if fps_match or size_match:
                    # Estimer la taille finale en fonction du pourcentage actuel
                    estimated_size = "Calcul en cours..."
                    if percent_complete > 0 and size_match:
                        size_value = float(current_size.split()[0])
                        size_unit = current_size.split()[1]
                        estimated_size = (
                            f"{(size_value * 100 / percent_complete):.2f} {size_unit}"
                        )

                    # Mettre à jour les statistiques d'encodage
                    if signals and hasattr(signals, "update_encoding_stats"):
                        signals.update_encoding_stats.emit(
                            current_fps, current_size, estimated_size
                        )

        # Vérifier le résultat
        process.wait()
        if process.returncode == 0:
            if os.path.exists(chemin_sortie):
                taille = os.path.getsize(chemin_sortie) / (1024 * 1024)  # En MB
                logger.info(
                    f"Fichier encodé avec succès: {chemin_sortie} ({taille:.2f} MB)"
                )
            else:
                logger.warning(f"Le fichier encodé n'a pas été trouvé: {chemin_sortie}")
        else:
            logger.error(
                f"Échec de l'encodage pour {nom_fichier} avec code de retour {process.returncode}"
            )

        # Signaler la fin de l'encodage
        if signals and hasattr(signals, "encoding_done"):
            signals.encoding_done.emit()

        return process.returncode == 0

    except Exception as e:
        logger.error(
            f"Exception pendant l'encodage de {nom_fichier}: {str(e)}", exc_info=True
        )
        if signals and hasattr(signals, "encoding_done"):
            signals.encoding_done.emit()
        return False


def traitement_file_encodage(file_encodage, signals=None, control_flags=None):
    """
    Fonction qui traite la file d'attente des fichiers à encoder
    Avec support pour l'interface graphique
    """
    logger = setup_logger(__name__)
    logger.info("Thread de traitement de la file d'encodage démarré")

    while True:
        # Vérifier si on doit arrêter complètement
        if control_flags and control_flags.get("stop_all", False):
            logger.info("Arrêt de tous les encodages demandé")
            control_flags["stop_all"] = False
            # Envoyer un signal pour mettre à jour l'interface
            if signals:
                signals.encoding_done.emit()
                signals.update_queue.emit([])
            time.sleep(1)
            continue

        # Attendre qu'un fichier soit disponible dans la file
        if file_encodage.empty():
            time.sleep(1)
            continue

        # Extraire le prochain fichier à traiter
        tache = file_encodage.get()

        if isinstance(tache, dict):
            fichier = tache.get("file")
            preset = tache.get("preset")
            dossier = tache.get("folder", "")
        else:
            # Fallback au cas où c'est un tuple
            fichier = tache[0] if len(tache) > 0 else ""
            preset = tache[1] if len(tache) > 1 else ""
            dossier = ""

        # Mettre à jour la file d'attente dans l'interface
        if signals and hasattr(signals, "update_queue"):
            queue_items = []
            if not file_encodage.empty():
                queue_items = list(file_encodage.queue)
            signals.update_queue.emit(queue_items)

        # Encodage avec gestion GUI
        logger.info(f"Début de l'encodage de {fichier} avec le preset {preset}")
        lancer_encodage_avec_gui(fichier, preset, dossier, signals, control_flags)
