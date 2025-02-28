import logging
from queue import Queue
import subprocess
from threading import Thread
import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QIcon  # Ajoutez cette importation
import qdarkstyle  # Ajouter cet import en haut du fichier

from surveillance import surveille_dossiers
from encoding import traitement_file_encodage
from constants import dossiers_presets, icon_file
from initialization import vider_fichiers
from logger import setup_logger
from gui import MainWindow, LogHandler
from state_persistence import (
    load_interrupted_encodings,
    clear_interrupted_encodings,
    has_interrupted_encodings,
)
from resume_dialog import RestartEncodingDialog

# Définir le chemin de base en fonction de l'exécution en tant que script ou exécutable
if hasattr(sys, "_MEIPASS"):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.dirname(__file__)


# Fonction pour vérifier si HandBrakeCLI est installé
def check_handbrake_cli():
    try:
        result = subprocess.run(
            ["HandBrakeCLI", "--version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=5,
        )
        return result.returncode == 0, result.stdout if result.returncode == 0 else None
    except (FileNotFoundError, subprocess.SubprocessError):
        return False, None


# Classe intermédiaire pour les signaux entre threads
class EncodingSignals(QObject):
    update_progress = pyqtSignal(int)  # pourcentage de progression
    update_file_info = pyqtSignal(str, str)  # filename, preset
    update_time_info = pyqtSignal(str, str)  # elapsed, remaining
    update_encoding_stats = pyqtSignal(str)  # fps
    encoding_done = pyqtSignal()  # signal quand l'encodage est terminé
    update_queue = pyqtSignal(list)  # liste des fichiers en attente
    update_output_path = pyqtSignal(str)  # chemin du fichier de sortie
    update_manual_encodings = (
        pyqtSignal()
    )  # signal pour mettre à jour la liste des encodages manuels
    refresh_history = (
        pyqtSignal()
    )  # signal pour rafraîchir l'historique des encodages réussis


# Variable globale pour suivre l'encodage en cours
current_encoding_info = None


# Point d'entrée principal
def main():
    global current_encoding_info
    # Créer l'application Qt
    app = QApplication(sys.argv)
    # Définir l'icône de l'application (affecte toutes les fenêtres)
    app_icon = QIcon(icon_file)
    app.setWindowIcon(app_icon)

    # Appliquer le thème sombre avec des boutons plus hauts
    base_style = qdarkstyle.load_stylesheet_pyqt5()
    button_style = "QPushButton { min-height: 30px; font-size: 14px; font-weight: bold; font-family: 'Segoe UI', 'Arial', sans-serif; }"
    app.setStyleSheet(base_style + button_style)

    # Configurer le logger pour le module principal
    logger = setup_logger(__name__)

    # Créer la fenêtre principale
    window = MainWindow()

    # Configuration du gestionnaire de logs pour l'interface graphique
    log_handler = LogHandler()
    log_handler.log_signal.connect(window.add_log)

    # Ajouter le handler au logger racine pour capturer tous les logs
    root_logger = logging.getLogger()
    root_logger.addHandler(log_handler)

    # Fonction de nettoyage pour éviter l'erreur à la fermeture
    # et sauvegarder l'état des encodages en cours
    def cleanup():
        # Indiquer que l'application est en cours de fermeture
        control_flags["closing"] = True

        # Supprimer le handler de log pour éviter les erreurs
        root_logger.removeHandler(log_handler)

        # Sauvegarder l'état des encodages en cours
        logger.info("Sauvegarde de l'état des encodages en cours avant fermeture")

        # Récupérer l'encodage en cours et la file d'attente
        current_encoding = current_encoding_info
        queue_items = []

        # Récupérer les éléments de la file d'attente sans les retirer
        # Note: Queue.queue est un attribut interne qui peut ne pas être fiable
        # Nous utilisons une approche plus sûre en créant une copie de la file
        queue_size = file_encodage.qsize()
        queue_items = []

        if queue_size > 0:
            logger.info(f"Sauvegarde de {queue_size} éléments dans la file d'attente")
            # Créer une liste temporaire pour stocker les éléments
            temp_items = []

            # Retirer tous les éléments de la file
            for _ in range(queue_size):
                if not file_encodage.empty():
                    item = file_encodage.get()
                    temp_items.append(item)

            # Remettre les éléments dans la file et les ajouter à notre liste
            for item in temp_items:
                file_encodage.put(item)
                queue_items.append(item)

        # Terminer tous les processus HandBrakeCLI en cours
        logger.info("Arrêt des processus HandBrakeCLI en cours")
        import psutil

        # Fonction pour tuer un processus avec plusieurs tentatives
        def kill_process(proc):
            try:
                # D'abord essayer de terminer proprement le processus
                logger.info(
                    f"Tentative d'arrêt du processus HandBrakeCLI (PID: {proc.pid})"
                )
                proc.terminate()

                # Attendre jusqu'à 3 secondes pour que le processus se termine
                gone, still_alive = psutil.wait_procs([proc], timeout=3)

                # Si le processus est toujours en vie, le tuer de force
                if still_alive:
                    logger.warning(
                        f"Le processus HandBrakeCLI (PID: {proc.pid}) ne répond pas, arrêt forcé"
                    )
                    for p in still_alive:
                        p.kill()

                return True
            except (
                psutil.NoSuchProcess,
                psutil.AccessDenied,
                psutil.ZombieProcess,
            ) as e:
                logger.error(
                    f"Erreur lors de l'arrêt du processus (PID: {proc.pid}): {str(e)}"
                )
                return False

        # Trouver et tuer tous les processus HandBrakeCLI
        handbrake_processes = []
        for proc in psutil.process_iter(["pid", "name"]):
            try:
                # Si c'est un processus HandBrakeCLI, l'ajouter à la liste
                if "HandBrakeCLI" in proc.info["name"]:
                    handbrake_processes.append(psutil.Process(proc.info["pid"]))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        # Tuer tous les processus HandBrakeCLI trouvés
        if handbrake_processes:
            logger.info(f"Arrêt de {len(handbrake_processes)} processus HandBrakeCLI")
            for proc in handbrake_processes:
                kill_process(proc)
        else:
            logger.info("Aucun processus HandBrakeCLI en cours d'exécution")

    # Connecter la fonction de nettoyage à la fermeture de l'application
    app.aboutToQuit.connect(cleanup)

    # Définir la fonction de nettoyage pour la fenêtre principale
    window.set_cleanup_function(cleanup)

    logger.info("=== Démarrage de l'application Encodage_Auto_Plex ===")

    # Vérifier l'installation de HandBrakeCLI
    handbrake_installed, version_info = check_handbrake_cli()
    if handbrake_installed:
        logger.info(f"✅ HandBrakeCLI installé et opérationnel: {version_info.strip()}")
    else:
        logger.error(
            "❌ HandBrakeCLI n'est pas installé ou n'est pas accessible. L'encodage ne fonctionnera pas!"
        )

    # Créer les signaux pour la communication entre threads
    signals = EncodingSignals()
    signals.update_progress.connect(window.encoding_status.update_progress)
    signals.update_file_info.connect(window.encoding_status.update_file_info)
    signals.update_time_info.connect(window.encoding_status.update_time_info)
    signals.update_encoding_stats.connect(window.encoding_status.update_encoding_stats)
    signals.encoding_done.connect(window.encoding_status.clear)
    signals.update_queue.connect(window.update_queue)
    signals.update_manual_encodings.connect(window.load_manual_encodings)
    signals.refresh_history.connect(window.refresh_history_panel)

    # File d'attente pour les encodages
    file_encodage = Queue()
    logger.info("Initialisation de la file d'attente d'encodage")

    # Variable de contrôle pour la pause et l'arrêt
    control_flags = {"pause": False, "skip": False, "stop_all": False, "closing": False}

    # Associer les control_flags à la fenêtre principale
    window.set_control_flags(control_flags)

    # Connecter les boutons de l'interface aux flags de contrôle
    def update_pause_flag():
        control_flags["pause"] = window.is_paused

    def trigger_skip():
        control_flags["skip"] = True

    def trigger_stop_all():
        control_flags["stop_all"] = True
        # Vider la file d'attente
        while not file_encodage.empty():
            file_encodage.get()
        # Effacer les encodages interrompus
        clear_interrupted_encodings()

    window.pause_button.clicked.connect(update_pause_flag)
    window.skip_button.clicked.connect(trigger_skip)
    window.stop_button.clicked.connect(trigger_stop_all)

    # Vérifier s'il y a des encodages interrompus
    restart_encoding = False
    if has_interrupted_encodings():
        # Charger les informations sur les encodages interrompus
        interrupted_state = load_interrupted_encodings()
        if interrupted_state:
            # Afficher la fenêtre principale pour que la boîte de dialogue soit centrée
            window.show()

            # Afficher la boîte de dialogue pour demander à l'utilisateur s'il veut recommencer
            restart_encoding = RestartEncodingDialog.show_dialog(
                interrupted_state, window
            )

            if restart_encoding:
                logger.info("Redémarrage des encodages interrompus")

                # Récupérer l'encodage interrompu
                current_encoding = interrupted_state.get("current_encoding")
                if current_encoding:
                    # Vérifier si le chemin du fichier est complet ou juste un nom de fichier
                    fichier = current_encoding.get("file", "")
                    if fichier and not os.path.isabs(fichier):
                        # Si c'est juste un nom de fichier, essayer de trouver le fichier dans les dossiers surveillés
                        found = False
                        for items in dossiers_presets:
                            chemin_complet = os.path.join(items[0], fichier)
                            if os.path.exists(chemin_complet):
                                # Mettre à jour le chemin dans l'encodage interrompu
                                current_encoding["file"] = chemin_complet
                                current_encoding["folder"] = items[0]
                                found = True
                                logger.info(f"Fichier trouvé: {chemin_complet}")
                                break

                        if not found:
                            logger.warning(
                                f"Impossible de trouver le fichier: {fichier}"
                            )
                            # Continuer quand même, peut-être que le fichier existe ailleurs

                    # Ajouter l'encodage interrompu à la file d'attente en premier
                    file_encodage.put(current_encoding)

                # Récupérer la file d'attente
                queue_items = interrupted_state.get("encoding_queue", [])
                for item in queue_items:
                    # Vérifier si le chemin du fichier est complet ou juste un nom de fichier
                    fichier = item.get("file", "")
                    if fichier and not os.path.isabs(fichier):
                        # Si c'est juste un nom de fichier, essayer de trouver le fichier dans les dossiers surveillés
                        found = False
                        for items in dossiers_presets:
                            chemin_complet = os.path.join(items[0], fichier)
                            if os.path.exists(chemin_complet):
                                # Mettre à jour le chemin dans l'item
                                item["file"] = chemin_complet
                                item["folder"] = items[0]
                                found = True
                                logger.info(f"Fichier trouvé: {chemin_complet}")
                                break

                        if not found:
                            logger.warning(
                                f"Impossible de trouver le fichier: {fichier}"
                            )
                            # Continuer quand même, peut-être que le fichier existe ailleurs

                    file_encodage.put(item)

                # Mettre à jour l'interface avec la file d'attente
                if signals and hasattr(signals, "update_queue"):
                    all_items = [current_encoding] if current_encoding else []
                    all_items.extend(queue_items)
                    signals.update_queue.emit(all_items)
            else:
                # L'utilisateur a choisi de repartir à zéro
                logger.info("Démarrage à zéro, effacement des encodages interrompus")
                clear_interrupted_encodings()
                # Vider les fichiers détectés et encodés au démarrage
                logger.info("Nettoyage des fichiers temporaires")
                vider_fichiers()
    else:
        # Pas d'état sauvegardé, démarrage normal
        # Vider les fichiers détectés et encodés au démarrage
        logger.info("Nettoyage des fichiers temporaires")
        vider_fichiers()
        # Afficher la fenêtre principale
        window.show()

    # Fonction pour mettre à jour l'encodage en cours
    def update_current_encoding(file_info, preset_info):
        global current_encoding_info
        if file_info and preset_info:
            # Vérifier si le chemin du fichier est complet ou juste un nom de fichier
            if file_info and not os.path.isabs(file_info):
                # Si c'est juste un nom de fichier, essayer de trouver le fichier dans les dossiers surveillés
                found = False
                for items in dossiers_presets:
                    chemin_complet = os.path.join(items, file_info)
                    if os.path.exists(chemin_complet):
                        # Utiliser le chemin complet
                        file_info = chemin_complet
                        folder = items
                        found = True
                        logger.info(
                            f"Fichier trouvé pour l'encodage en cours: {chemin_complet}"
                        )
                        break

                if not found:
                    logger.warning(
                        f"Impossible de trouver le chemin complet pour: {file_info}"
                    )
                    # Continuer quand même, peut-être que le fichier existe ailleurs
                    folder = ""
                else:
                    folder = items
            else:
                # Si c'est déjà un chemin complet, utiliser le dossier parent
                folder = os.path.dirname(file_info) if os.path.isabs(file_info) else ""

            # Créer un dictionnaire avec les informations de l'encodage en cours
            current_encoding_info = {
                "file": file_info,
                "preset": preset_info,
                "folder": folder,
            }
        else:
            current_encoding_info = None

    # Connecter le signal de mise à jour des informations de fichier à notre fonction
    signals.update_file_info.connect(update_current_encoding)

    # Connecter le signal de fin d'encodage pour réinitialiser l'encodage en cours
    def clear_current_encoding():
        global current_encoding_info
        current_encoding_info = None

    signals.encoding_done.connect(clear_current_encoding)

    # Démarrer le thread de traitement de la file d'attente d'encodage
    logger.info("Démarrage du thread d'encodage")
    thread_encodage = Thread(
        target=traitement_file_encodage,
        args=(file_encodage, signals, control_flags),
        daemon=True,
    )
    thread_encodage.start()

    # Démarrer le thread de surveillance des dossiers
    logger.info(f"Démarrage de la surveillance des dossiers")
    thread_surveillance = Thread(
        target=surveille_dossiers,
        args=(dossiers_presets, file_encodage, signals, control_flags),
        daemon=True,
    )
    thread_surveillance.start()

    # Exécuter l'application
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
