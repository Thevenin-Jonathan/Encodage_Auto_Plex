import logging
from queue import Queue
from threading import Thread
import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal, QObject
import qdarkstyle  # Ajouter cet import en haut du fichier

from surveillance import surveille_dossiers
from encoding import traitement_file_encodage
from constants import dossiers_presets
from initialization import vider_fichiers
from logger import setup_logger
from gui import MainWindow, LogHandler


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


# Point d'entrée principal
def main():
    # Créer l'application Qt
    app = QApplication(sys.argv)

    # Appliquer le thème sombre avec des boutons plus hauts
    base_style = qdarkstyle.load_stylesheet_pyqt5()
    button_style = "QPushButton { min-height: 30px; }"
    app.setStyleSheet(base_style + button_style)

    # Configurer le logger pour le module principal
    logger = setup_logger(__name__)

    # Créer la fenêtre principale
    window = MainWindow()
    window.show()

    # Configuration du gestionnaire de logs pour l'interface graphique
    log_handler = LogHandler()
    log_handler.log_signal.connect(window.add_log)

    # Ajouter le handler au logger racine pour capturer tous les logs
    root_logger = logging.getLogger()
    root_logger.addHandler(log_handler)

    # Fonction de nettoyage pour éviter l'erreur à la fermeture
    def cleanup():
        root_logger.removeHandler(log_handler)

    # Connecter la fonction de nettoyage à la fermeture de l'application
    app.aboutToQuit.connect(cleanup)

    logger.info("=== Démarrage de l'application Encodage_Auto_Plex ===")

    # Vider les fichiers détectés et encodés au démarrage
    logger.info("Nettoyage des fichiers temporaires")
    vider_fichiers()

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
    control_flags = {"pause": False, "skip": False, "stop_all": False}

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

    window.pause_button.clicked.connect(update_pause_flag)
    window.skip_button.clicked.connect(trigger_skip)
    window.stop_button.clicked.connect(trigger_stop_all)

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
