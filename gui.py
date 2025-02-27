import sys
import os
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
)
from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QIcon, QFont


class LogHandler(QObject, logging.Handler):
    log_signal = pyqtSignal(str)

    def __init__(self, level=logging.NOTSET):
        QObject.__init__(self)
        logging.Handler.__init__(self, level)
        self.lock = None  # Sera initialisé par createLock
        self.createLock()

    def createLock(self):
        self.lock = RLock()

    def acquire(self):
        if self.lock:
            self.lock.acquire()

    def release(self):
        if self.lock:
            self.lock.release()

    def emit(self, record):
        log_entry = self.format(record)
        self.log_signal.emit(log_entry)


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

        # FPS et taille
        info_layout = QHBoxLayout()
        self.fps_label = QLabel("FPS: -")
        self.size_label = QLabel("Taille: - / -")
        info_layout.addWidget(self.fps_label)
        info_layout.addWidget(self.size_label)
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

    def update_encoding_stats(self, fps, current_size, estimated_size):
        self.fps_label.setText(f"FPS: {fps}")
        self.size_label.setText(f"Taille: {current_size} / {estimated_size}")

    def clear(self):
        self.file_label.setText("Aucun encodage en cours")
        self.preset_label.setText("Preset: -")
        self.elapsed_label.setText("Temps écoulé: 00:00:00")
        self.remaining_label.setText("Temps restant: --:--:--")
        self.progress_bar.setValue(0)
        self.fps_label.setText("FPS: -")
        self.size_label.setText("Taille: - / -")

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

        # Liste des encodages en attente
        queue_label = QLabel("File d'attente:")
        queue_label.setFont(QFont("Arial", 10, QFont.Bold))
        main_layout.addWidget(queue_label)

        self.queue_text = QTextEdit()
        self.queue_text.setReadOnly(True)
        self.queue_text.setMaximumHeight(100)
        main_layout.addWidget(self.queue_text)

        # Boutons de contrôle
        button_layout = QHBoxLayout()

        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.toggle_pause)
        self.is_paused = False

        self.skip_button = QPushButton("Passer au suivant")
        self.skip_button.clicked.connect(self.skip_encoding)

        self.stop_button = QPushButton("Arrêter tous les encodages")
        self.stop_button.clicked.connect(self.stop_all)
        self.stop_button.setStyleSheet("background-color: #ff6b6b;")

        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.skip_button)
        button_layout.addWidget(self.stop_button)

        main_layout.addLayout(button_layout)

        self.setCentralWidget(central_widget)

    def add_log(self, message, level="INFO"):
        """Ajoute un message dans la zone de logs avec coloration selon le niveau"""
        color_map = {
            "DEBUG": "gray",
            "INFO": "black",
            "WARNING": "orange",
            "ERROR": "red",
            "CRITICAL": "darkred",
        }
        color = color_map.get(level, "black")
        self.log_text.append(f"<span style='color:{color};'>{message}</span>")
        # Auto-scroll to bottom
        sb = self.log_text.verticalScrollBar()
        sb.setValue(sb.maximum())

    def update_queue(self, queue_items):
        """Met à jour la liste des encodages en attente"""
        self.queue_text.clear()
        if not queue_items:
            self.queue_text.append("Aucun fichier en attente")
            return

        for i, item in enumerate(queue_items, 1):
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
