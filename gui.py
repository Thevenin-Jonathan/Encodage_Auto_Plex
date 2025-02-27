import sys
import os
import subprocess
import logging
from threading import RLock
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTextEdit,
    QProgressBar,
    QLabel,
    QFrame,
    QListWidget,
)
from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QFont


class LogHandler(QObject, logging.Handler):
    log_signal = pyqtSignal(str, str, str)  # message, level, custom_color

    def __init__(self):
        super().__init__()
        logging.Handler.__init__(self)
        self.flushOnClose = False

    def emit(self, record):
        msg = self.format(record) if self.formatter else record.getMessage()
        # Vérifier si le message contient une indication de couleur personnalisée
        custom_color = getattr(record, "custom_color", None)
        self.log_signal.emit(msg, record.levelname, custom_color)


class EncodingStatusWidget(QFrame):
    """Widget affichant les informations sur l'encodage en cours"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)

        # Layout principal
        layout = QVBoxLayout(self)

        # Informations sur le fichier en cours
        self.file_label = QLabel("Aucun encodage en cours")
        self.file_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(self.file_label)

        # Preset utilisé
        self.preset_label = QLabel("Preset: -")
        layout.addWidget(self.preset_label)

        # Temps écoulé et temps restant
        time_layout = QHBoxLayout()
        self.elapsed_label = QLabel("Temps écoulé: 00:00:00")
        self.remaining_label = QLabel("Temps restant: --:--:--")
        time_layout.addWidget(self.elapsed_label)
        time_layout.addWidget(self.remaining_label)
        layout.addLayout(time_layout)

        # Barre de progression
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # FPS
        info_layout = QHBoxLayout()
        self.fps_label = QLabel("FPS: -")
        info_layout.addWidget(self.fps_label)
        layout.addLayout(info_layout)

        self.setLayout(layout)

    def update_progress(self, percentage):
        self.progress_bar.setValue(int(percentage))

    def update_file_info(self, filename, preset):
        self.file_label.setText(f"En cours: {os.path.basename(filename)}")
        self.preset_label.setText(f"Preset: {preset}")

    def update_time_info(self, elapsed, remaining):
        self.elapsed_label.setText(f"Temps écoulé: {elapsed}")
        self.remaining_label.setText(f"Temps restant: {remaining}")

    def update_encoding_stats(self, fps):
        self.fps_label.setText(f"FPS: {fps}")

    def clear(self):
        self.file_label.setText("Aucun encodage en cours")
        self.preset_label.setText("Preset: -")
        self.elapsed_label.setText("Temps écoulé: 00:00:00")
        self.remaining_label.setText("Temps restant: --:--:--")
        self.progress_bar.setValue(0)
        self.fps_label.setText("FPS: -")

    def show_output_path(self, path):
        """Affiche le chemin du fichier de sortie"""
        self.output_path_label = QLabel(f"Sortie: {path}")
        self.layout().addWidget(self.output_path_label)


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Encodage Auto Plex")
        self.resize(800, 600)

        # Widget central
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # Zone de logs
        log_label = QLabel("Logs:")
        log_label.setFont(QFont("Arial", 10, QFont.Bold))
        main_layout.addWidget(log_label)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QTextEdit.NoWrap)
        self.log_text.setFont(QFont("Consolas", 9))
        main_layout.addWidget(self.log_text)

        # Informations sur l'encodage en cours
        encoding_label = QLabel("Encodage en cours:")
        encoding_label.setFont(QFont("Arial", 10, QFont.Bold))
        main_layout.addWidget(encoding_label)

        self.encoding_status = EncodingStatusWidget()
        main_layout.addWidget(self.encoding_status)

        # NOUVEAU: Ajouter les boutons de contrôle juste après la barre de chargement
        control_buttons_layout = QHBoxLayout()

        self.pause_button = QPushButton("Pause")
        self.pause_button.setCheckable(True)
        self.is_paused = False
        self.pause_button.clicked.connect(self.toggle_pause)
        control_buttons_layout.addWidget(self.pause_button)

        self.skip_button = QPushButton("Passer")
        control_buttons_layout.addWidget(self.skip_button)

        self.stop_button = QPushButton("Stopper tout")
        self.stop_button.setStyleSheet("background-color: #ff6b6b;")
        control_buttons_layout.addWidget(self.stop_button)

        main_layout.addLayout(control_buttons_layout)

        # Ensuite, section de la file d'attente
        self.queue_label = QLabel("File d'attente (0):")
        self.queue_label.setFont(QFont("Arial", 10, QFont.Bold))
        main_layout.addWidget(self.queue_label)

        self.queue_text = QTextEdit()
        self.queue_text.setReadOnly(True)
        self.queue_text.setMaximumHeight(100)
        main_layout.addWidget(self.queue_text)

        # Section des encodages manuels
        self.manual_encodings_label = QLabel("Encodages manuels (0):")
        self.manual_encodings_label.setFont(QFont("Arial", 10, QFont.Bold))
        main_layout.addWidget(self.manual_encodings_label)

        # Liste des encodages manuels avec possibilité de sélection
        self.manual_list = QListWidget()
        self.manual_list.setMaximumHeight(150)
        self.manual_list.setSelectionMode(QListWidget.MultiSelection)
        main_layout.addWidget(self.manual_list)

        # Boutons pour gérer les encodages manuels
        manual_buttons_layout = QHBoxLayout()

        self.refresh_manual_btn = QPushButton("Rafraîchir")
        self.refresh_manual_btn.clicked.connect(self.load_manual_encodings)

        self.delete_selected_btn = QPushButton("Supprimer sélection")
        self.delete_selected_btn.clicked.connect(self.delete_selected_encodings)

        self.delete_all_btn = QPushButton("Tout supprimer")
        self.delete_all_btn.clicked.connect(self.delete_all_encodings)
        self.delete_all_btn.setStyleSheet("background-color: #ff6b6b;")

        # Ajouter le nouveau bouton pour localiser le fichier
        self.locate_file_btn = QPushButton("Localiser fichier")
        self.locate_file_btn.clicked.connect(self.locate_selected_file)
        self.locate_file_btn.setStyleSheet("background-color: #4dabf7;")

        manual_buttons_layout.addWidget(self.refresh_manual_btn)
        manual_buttons_layout.addWidget(self.delete_selected_btn)
        manual_buttons_layout.addWidget(
            self.locate_file_btn
        )  # Ajouter le nouveau bouton
        manual_buttons_layout.addWidget(self.delete_all_btn)

        main_layout.addLayout(manual_buttons_layout)

        self.setCentralWidget(central_widget)

        # Ou ajout d'une action dans un menu existant
        # file_menu = menubar.addMenu("Fichier")
        # self.queue_action = QAction("File d'attente (0)", self)
        # file_menu.addAction(self.queue_action)

        # Charger les encodages manuels au démarrage
        self.load_manual_encodings()

    def add_log(self, message, level="INFO", custom_color=None):
        """Ajoute un message dans la zone de logs avec coloration selon le niveau ou personnalisée"""
        color_map = {
            "DEBUG": "gray",
            "INFO": "black",
            "WARNING": "orange",
            "ERROR": "red",
            "CRITICAL": "darkred",
        }
        # Utiliser la couleur personnalisée si fournie, sinon celle du niveau
        color = custom_color if custom_color else color_map.get(level, "black")
        self.log_text.append(f"<span style='color:{color};'>{message}</span>")
        # Auto-scroll to bottom
        sb = self.log_text.verticalScrollBar()
        sb.setValue(sb.maximum())

    def update_queue(self, queue_files):
        """Met à jour la liste des encodages en attente"""
        self.queue_text.clear()

        # Mettre à jour le nombre de fichiers dans le menu (toujours le faire, même si vide)
        queue_count = len(queue_files)
        self.update_queue_count_in_menu(queue_count)

        if not queue_files:
            self.queue_text.append("Aucun fichier en attente")
            return

        for i, item in enumerate(queue_files, 1):
            if isinstance(item, dict):
                # Si l'élément est un dictionnaire
                filename = os.path.basename(item.get("file", "Inconnu"))
                preset = item.get("preset", "Preset inconnu")
            elif isinstance(item, tuple) and len(item) >= 2:
                # Si l'élément est un tuple
                filename = os.path.basename(item[0])
                preset = item[1]
            else:
                # Format inconnu
                filename = "Format inconnu"
                preset = "Preset inconnu"

            self.queue_text.append(f"{i}. {filename} - {preset}")

    def update_queue_count_in_menu(self, count):
        # Mettre à jour l'action dans un menu existant
        if hasattr(self, "queue_action"):
            self.queue_action.setText(f"File d'attente ({count})")

        # Mettre à jour le label dans l'interface principale
        if hasattr(self, "queue_label"):
            self.queue_label.setText(f"File d'attente ({count}):")

        # Alternative: mettre à jour dans la barre de statut
        if hasattr(self, "statusBar"):
            self.statusBar().showMessage(f"Fichiers en attente: {count}")

    def toggle_pause(self):
        """Mettre en pause ou reprendre l'encodage en cours"""
        self.is_paused = not self.is_paused
        if self.is_paused:
            self.pause_button.setText("Reprendre")
            # Signal to pause encoding
        else:
            self.pause_button.setText("Pause")
            # Signal to resume encoding

    def skip_encoding(self):
        """Arrête l'encodage en cours et passe au suivant"""
        # Signal to skip current encoding
        pass

    def stop_all(self):
        """Arrête tous les encodages et vide la file d'attente"""
        # Signal to stop all encodings
        self.encoding_status.clear()
        self.update_queue([])
        pass

    def load_manual_encodings(self):
        """Charge les encodages manuels depuis le fichier"""
        self.manual_list.clear()
        try:
            with open("Encodage_manuel.txt", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        self.manual_list.addItem(line)

            # Mettre à jour le titre avec le nombre d'encodages
            count = self.manual_list.count()
            self.manual_encodings_label.setText(f"Encodages manuels ({count}):")
        except Exception as e:
            self.add_log(
                f"Erreur lors du chargement des encodages manuels: {str(e)}", "ERROR"
            )

    def delete_selected_encodings(self):
        """Supprime les encodages sélectionnés du fichier"""
        selected_items = self.manual_list.selectedItems()
        if not selected_items:
            return

        try:
            # Lire toutes les lignes
            with open("Encodage_manuel.txt", "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Filtrer les lignes à conserver
            selected_texts = [item.text() for item in selected_items]
            filtered_lines = [
                line for line in lines if line.strip() not in selected_texts
            ]

            # Réécrire le fichier sans les lignes sélectionnées
            with open("Encodage_manuel.txt", "w", encoding="utf-8") as f:
                f.writelines(filtered_lines)

            self.add_log(
                f"{len(selected_items)} encodage(s) manuel(s) supprimé(s)",
                "INFO",
                "green",
            )
            self.load_manual_encodings()
        except Exception as e:
            self.add_log(f"Erreur lors de la suppression: {str(e)}", "ERROR")

    def delete_all_encodings(self):
        """Supprime tous les encodages manuels du fichier"""
        if self.manual_list.count() == 0:
            return

        try:
            # Vider complètement le fichier
            with open("Encodage_manuel.txt", "w", encoding="utf-8") as f:
                pass

            self.add_log(
                "Tous les encodages manuels ont été supprimés", "INFO", "green"
            )
            self.load_manual_encodings()
        except Exception as e:
            self.add_log(f"Erreur lors de la suppression: {str(e)}", "ERROR")

    def locate_selected_file(self):
        """Ouvre l'explorateur à l'emplacement du fichier sélectionné"""
        selected_items = self.manual_list.selectedItems()
        if not selected_items:
            self.add_log("Aucun fichier sélectionné", "WARNING", "orange")
            return

        # Utiliser le premier élément sélectionné
        selected_text = selected_items[0].text()

        try:
            # Si le format est "chemin_complet|preset"
            if "|" in selected_text:
                filepath = selected_text.split("|")[0]
            else:
                # Si c'est juste le nom du fichier, impossible de localiser
                self.add_log(
                    "Impossible de localiser le fichier (chemin complet non disponible)",
                    "ERROR",
                    "red",
                )
                return

            # Vérifier si le fichier existe
            if not os.path.exists(filepath):
                self.add_log(f"Le fichier n'existe pas: {filepath}", "ERROR", "red")
                return

            # Ouvrir l'explorateur Windows à l'emplacement du fichier
            directory = os.path.dirname(filepath)

            # Ouvrir l'explorateur et sélectionner le fichier
            self.add_log(f"Ouverture de l'explorateur à: {directory}", "INFO", "green")

            if os.name == "nt":  # Windows
                # Méthode corrigée pour ouvrir l'explorateur au bon endroit
                normalized_path = os.path.normpath(filepath)
                # Utiliser une chaîne de commande complète avec shell=True
                subprocess.run(f'explorer /select,"{normalized_path}"', shell=True)
            else:  # Linux, Mac
                subprocess.Popen(["xdg-open", directory])

        except Exception as e:
            self.add_log(
                f"Erreur lors de la localisation du fichier: {str(e)}",
                "ERROR",
                "red",
            )
