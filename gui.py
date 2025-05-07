import sys
import os
import subprocess
import logging
from PyQt5.QtWidgets import (
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
    QSplitter,
    QToolButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QCheckBox,
    QListWidgetItem,
    QFileDialog,  # Ajout pour la boîte de dialogue de sélection de fichier
    QComboBox,  # Ajout pour la liste déroulante de presets
    QMessageBox,  # Ajout pour afficher des messages
)
from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont
from successful_encodings import get_recent_encodings
from constants import fichier_encodage_manuel, extensions, dossiers_presets
from config import load_config


class LogHandler(QObject, logging.Handler):
    log_signal = pyqtSignal(str, str, str)  # message, level, custom_color

    def __init__(self):
        super().__init__()
        logging.Handler.__init__(self)
        self.flushOnClose = False
        self.formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

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


class EncodingsHistoryPanel(QWidget):
    """Widget pour afficher l'historique des encodages réussis dans un panneau latéral"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # En-tête avec titre et bouton de fermeture
        header_layout = QHBoxLayout()

        history_label = QLabel("Encodages réussis (72h):")
        history_label.setFont(QFont("Arial", 10, QFont.Bold))
        header_layout.addWidget(history_label)

        header_layout.addStretch()

        self.close_button = QToolButton()
        self.close_button.setText("×")
        self.close_button.setToolTip("Masquer l'historique")
        self.close_button.setStyleSheet("QToolButton { font-size: 16px; }")
        header_layout.addWidget(self.close_button)

        layout.addLayout(header_layout)

        # Tableau pour les encodages réussis
        self.encodings_table = QTableWidget()
        self.encodings_table.setColumnCount(3)
        self.encodings_table.setHorizontalHeaderLabels(
            ["Date/Heure", "Fichier", "Taille"]
        )
        self.encodings_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents
        )
        self.encodings_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.Stretch
        )
        self.encodings_table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeToContents
        )
        self.encodings_table.setAlternatingRowColors(True)
        # Définir les couleurs alternées pour les lignes du tableau
        self.encodings_table.setStyleSheet(
            """
            QTableView {
                background-color: #19232d;
                alternate-background-color: #243240;
            }
        """
        )
        self.encodings_table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )  # Lecture seule
        self.encodings_table.setSortingEnabled(True)  # Activer le tri par colonne
        layout.addWidget(self.encodings_table)

        # Définir une largeur minimale pour le panneau
        self.setMinimumWidth(400)

    def load_recent_encodings(self):
        """Charge et affiche les encodages réussis des dernières 72 heures"""
        # Effacer le tableau
        self.encodings_table.setRowCount(0)

        # Récupérer les encodages récents
        recent_encodings = get_recent_encodings(72)

        if not recent_encodings:
            # Ajouter une ligne indiquant qu'il n'y a pas d'encodages récents
            self.encodings_table.setRowCount(1)
            item = QTableWidgetItem("Aucun encodage récent")
            item.setTextAlignment(Qt.AlignCenter)
            self.encodings_table.setSpan(0, 0, 1, 3)  # Fusionner les cellules
            self.encodings_table.setItem(0, 0, item)
            return

        # Désactiver temporairement le tri pendant le remplissage du tableau
        self.encodings_table.setSortingEnabled(False)

        # Remplir le tableau avec les encodages récents
        self.encodings_table.setRowCount(len(recent_encodings))

        for row, encoding in enumerate(recent_encodings):
            # Date et heure de l'encodage
            datetime_str = encoding.get("datetime", "")
            timestamp = encoding.get("timestamp", 0)

            # Formater la date et l'heure avec un tiret entre les deux
            formatted_datetime = datetime_str.replace(" ", " - ")

            # Créer l'élément pour la date/heure
            datetime_item = QTableWidgetItem(formatted_datetime)
            datetime_item.setTextAlignment(Qt.AlignCenter)
            # Stocker le timestamp pour un tri chronologique correct
            datetime_item.setData(Qt.UserRole, timestamp)
            self.encodings_table.setItem(row, 0, datetime_item)

            # Nom du fichier
            filename = encoding.get("filename", "")
            filename_item = QTableWidgetItem(filename)
            self.encodings_table.setItem(row, 1, filename_item)

            # Taille du fichier
            size_mb = encoding.get("file_size", 0)
            size_item = QTableWidgetItem(f"{size_mb:.2f} MB")
            size_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            # Stocker la valeur numérique pour le tri
            size_item.setData(Qt.UserRole, float(size_mb))
            self.encodings_table.setItem(row, 2, size_item)

        # Réactiver le tri après avoir rempli le tableau
        self.encodings_table.setSortingEnabled(True)


class LogsPanel(QWidget):
    """Widget pour afficher les logs dans un panneau latéral"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Layout principal
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # En-tête avec titre et bouton de fermeture
        header_layout = QHBoxLayout()

        log_label = QLabel("Logs:")
        log_label.setFont(QFont("Arial", 10, QFont.Bold))
        header_layout.addWidget(log_label)

        header_layout.addStretch()

        self.close_button = QToolButton()
        self.close_button.setText("×")
        self.close_button.setToolTip("Masquer les logs")
        self.close_button.setStyleSheet("QToolButton { font-size: 16px; }")
        header_layout.addWidget(self.close_button)

        layout.addLayout(header_layout)

        # Zone de texte pour les logs
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setLineWrapMode(QTextEdit.NoWrap)
        self.log_text.setFont(QFont("Consolas", 9))
        layout.addWidget(self.log_text)

        # Définir une largeur minimale pour le panneau
        self.setMinimumWidth(400)


class MainWindow(QMainWindow):
    """Fenêtre principale de l'application"""

    # Signal pour indiquer que la fenêtre est sur le point d'être fermée
    closing = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Encodage Auto Plex")
        self.resize(1400, 800)
        config = load_config()

        # Variable pour suivre si les logs de debug doivent être affichés
        self.show_debug_logs = False
        # Stocker les logs récents pour pouvoir les filtrer
        self.recent_logs = []

        # Créer un splitter comme widget central
        self.splitter = QSplitter(Qt.Horizontal)
        self.setCentralWidget(self.splitter)

        # Widget principal pour le contenu (côté gauche)
        self.main_content = QWidget()
        main_layout = QVBoxLayout(self.main_content)
        main_layout.setContentsMargins(9, 9, 9, 9)  # Marges standard

        # Barre supérieure avec boutons pour les panneaux latéraux
        top_bar = QHBoxLayout()

        # Layout pour les boutons à gauche (historique)
        left_buttons_layout = QVBoxLayout()
        left_buttons_layout.setAlignment(Qt.AlignTop)  # Aligner en haut
        left_buttons_layout.setContentsMargins(0, 0, 0, 0)  # Réduire les marges
        left_buttons_layout.setSpacing(5)  # Espacement entre widgets si plusieurs

        # Bouton pour afficher/masquer l'historique des encodages (à gauche)
        self.show_history_button = QPushButton("Historique\ndes encodages")
        self.show_history_button.setToolTip(
            "Afficher/masquer l'historique des encodages réussis"
        )
        self.show_history_button.clicked.connect(self.toggle_history_panel)

        # Forcer la taille via une feuille de style CSS
        self.show_history_button.setStyleSheet(
            """
            QPushButton {
                min-height: 50px;
                min-width: 140px;
                font-weight: bold;
            }
        """
        )

        left_buttons_layout.addWidget(self.show_history_button)

        # Ajouter d'autres boutons à gauche si nécessaire
        # left_buttons_layout.addWidget(autre_bouton)

        # Ajouter le layout gauche à la barre supérieure
        top_bar.addLayout(left_buttons_layout)

        # Créer un layout vertical pour la checkbox des notifications avec alignement en haut
        notifications_layout = QVBoxLayout()
        notifications_layout.setAlignment(Qt.AlignTop)  # Aligner en haut
        notifications_layout.setContentsMargins(0, 0, 0, 0)  # Réduire les marges
        notifications_layout.setSpacing(5)

        # Checkbox pour activer/désactiver les notifications Windows
        self.notifications_checkbox = QCheckBox("Notifications Windows")
        self.notifications_checkbox.setToolTip(
            "Activer/désactiver les notifications Windows"
        )
        self.notifications_checkbox.setChecked(config["notifications_enabled"])
        self.notifications_checkbox.stateChanged.connect(self.toggle_notifications)
        notifications_layout.addWidget(self.notifications_checkbox)

        # Ajouter le layout des notifications à la barre supérieure
        top_bar.addLayout(notifications_layout)

        top_bar.addStretch()

        # Layout vertical pour les boutons de logs
        logs_buttons_layout = QVBoxLayout()
        logs_buttons_layout.setSpacing(5)  # Espacement entre les boutons

        # Bouton pour afficher/masquer les logs (à droite)
        self.show_logs_button = QPushButton("Afficher\nles logs")
        self.show_logs_button.setToolTip("Afficher/masquer le panneau de logs")
        self.show_logs_button.clicked.connect(self.toggle_logs_panel)
        self.show_logs_button.setMinimumHeight(75)  # Hauteur minimale en pixels
        self.show_logs_button.setMinimumWidth(120)  # Largeur minimale en pixels
        logs_buttons_layout.addWidget(self.show_logs_button)

        # Bouton pour afficher/masquer les logs de debug
        self.toggle_debug_button = QPushButton("Afficher\nlogs debug")
        self.toggle_debug_button.setToolTip("Afficher/masquer les logs de debug")
        self.toggle_debug_button.clicked.connect(self.toggle_debug_logs)
        self.toggle_debug_button.setMinimumHeight(75)  # Hauteur minimale en pixels
        self.toggle_debug_button.setMinimumWidth(120)  # Largeur minimale en pixels
        logs_buttons_layout.addWidget(self.toggle_debug_button)

        # Bouton pour charger les anciens logs
        self.load_old_logs_button = QPushButton("Charger les\nanciens logs")
        self.load_old_logs_button.setToolTip("Charger le dernier fichier de logs")
        self.load_old_logs_button.clicked.connect(self.load_last_log)
        self.load_old_logs_button.setMinimumHeight(75)  # Hauteur minimale en pixels
        self.load_old_logs_button.setMinimumWidth(120)  # Largeur minimale en pixels
        logs_buttons_layout.addWidget(self.load_old_logs_button)

        # Ajouter le layout vertical au layout horizontal
        top_bar.addLayout(logs_buttons_layout)

        main_layout.addLayout(top_bar)

        # Informations sur l'encodage en cours
        encoding_label = QLabel("Encodage en cours:")
        encoding_label.setFont(QFont("Arial", 10, QFont.Bold))
        main_layout.addWidget(encoding_label)

        self.encoding_status = EncodingStatusWidget()
        main_layout.addWidget(self.encoding_status)

        # Boutons de contrôle juste après la barre de chargement
        control_buttons_layout = QHBoxLayout()

        self.pause_button = QPushButton("Pause")
        self.pause_button.setCheckable(True)
        self.is_paused = False
        self.pause_button.clicked.connect(self.toggle_pause)
        control_buttons_layout.addWidget(self.pause_button)

        self.skip_button = QPushButton("Passer")
        control_buttons_layout.addWidget(self.skip_button)

        self.stop_button = QPushButton("Stopper tout")
        self.stop_button.setStyleSheet("background-color: #A94442;")
        control_buttons_layout.addWidget(self.stop_button)

        main_layout.addLayout(control_buttons_layout)

        # Section de la file d'attente
        self.queue_label = QLabel("File d'attente (0):")
        self.queue_label.setFont(QFont("Arial", 10, QFont.Bold))
        main_layout.addWidget(self.queue_label)

        # Remplacer QTextEdit par QListWidget pour permettre la sélection d'éléments
        self.queue_list = QListWidget()
        self.queue_list.setMaximumHeight(100)
        self.queue_list.setSelectionMode(QListWidget.SingleSelection)
        main_layout.addWidget(self.queue_list)

        # Boutons pour manipuler la file d'attente
        queue_buttons_layout = QHBoxLayout()

        # Bouton pour ajouter un fichier ou dossier à la file d'attente
        self.queue_add_btn = QPushButton("Ajouter")
        self.queue_add_btn.setToolTip(
            "Ajouter un fichier ou dossier à la file d'attente"
        )
        self.queue_add_btn.clicked.connect(self.add_to_queue)
        self.queue_add_btn.setStyleSheet("background-color: #3A6EA5;")
        queue_buttons_layout.addWidget(self.queue_add_btn)

        # Ordre des boutons selon la demande: descendre, monter, supprimer, tout en bas, tout en haut, supprimer tout
        self.queue_down_btn = QPushButton("Descendre")
        self.queue_down_btn.setToolTip("Déplacer l'élément sélectionné vers le bas")
        self.queue_down_btn.clicked.connect(self.move_queue_item_down)
        queue_buttons_layout.addWidget(self.queue_down_btn)

        self.queue_up_btn = QPushButton("Monter")
        self.queue_up_btn.setToolTip("Déplacer l'élément sélectionné vers le haut")
        self.queue_up_btn.clicked.connect(self.move_queue_item_up)
        queue_buttons_layout.addWidget(self.queue_up_btn)

        self.queue_bottom_btn = QPushButton("Tout en bas")
        self.queue_bottom_btn.setToolTip(
            "Déplacer l'élément sélectionné tout en bas de la file"
        )
        self.queue_bottom_btn.clicked.connect(self.move_queue_item_to_bottom)
        queue_buttons_layout.addWidget(self.queue_bottom_btn)

        self.queue_top_btn = QPushButton("Tout en haut")
        self.queue_top_btn.setToolTip(
            "Déplacer l'élément sélectionné tout en haut de la file"
        )
        self.queue_top_btn.clicked.connect(self.move_queue_item_to_top)
        queue_buttons_layout.addWidget(self.queue_top_btn)

        self.queue_delete_btn = QPushButton("Supprimer")
        self.queue_delete_btn.setToolTip(
            "Supprimer l'élément sélectionné de la file d'attente"
        )
        self.queue_delete_btn.clicked.connect(self.delete_queue_item)
        self.queue_delete_btn.setStyleSheet("background-color: #A94442;")
        queue_buttons_layout.addWidget(self.queue_delete_btn)

        self.queue_clear_btn = QPushButton("TOUT Supprimer")
        self.queue_clear_btn.setToolTip("Vider la file d'attente")
        self.queue_clear_btn.setStyleSheet("background-color: #A94442;")
        self.queue_clear_btn.clicked.connect(self.clear_queue)
        queue_buttons_layout.addWidget(self.queue_clear_btn)

        main_layout.addLayout(queue_buttons_layout)

        # Section des encodages manuels
        self.manual_encodings_label = QLabel("Encodages manuels (0):")
        self.manual_encodings_label.setFont(QFont("Arial", 10, QFont.Bold))
        main_layout.addWidget(self.manual_encodings_label)

        # Liste des encodages manuels avec possibilité de sélection
        self.manual_list = QListWidget()
        self.manual_list.setMaximumHeight(150)
        self.manual_list.setSelectionMode(QListWidget.SingleSelection)
        main_layout.addWidget(self.manual_list)

        # Boutons pour gérer les encodages manuels
        manual_buttons_layout = QHBoxLayout()

        self.refresh_manual_btn = QPushButton("Rafraîchir")
        self.refresh_manual_btn.clicked.connect(self.load_manual_encodings)

        # Ajouter un bouton Modifier pour éditer les pistes audio et sous-titres
        self.edit_tracks_btn = QPushButton("Modifier")
        self.edit_tracks_btn.setToolTip("Modifier les pistes audio et sous-titres")
        self.edit_tracks_btn.clicked.connect(self.open_track_editor)
        self.edit_tracks_btn.setStyleSheet("background-color: #4A7C59;")

        self.locate_file_btn = QPushButton("Localiser fichier")
        self.locate_file_btn.clicked.connect(self.locate_selected_file)
        self.locate_file_btn.setStyleSheet("background-color: #3A6EA5;")

        self.delete_selected_btn = QPushButton("Supprimer")
        self.delete_selected_btn.clicked.connect(self.delete_selected_encodings)
        self.delete_selected_btn.setStyleSheet("background-color: #A94442;")

        self.delete_all_btn = QPushButton("TOUT supprimer")
        self.delete_all_btn.clicked.connect(self.delete_all_encodings)
        self.delete_all_btn.setStyleSheet("background-color: #A94442;")

        manual_buttons_layout.addWidget(self.refresh_manual_btn)
        manual_buttons_layout.addWidget(self.edit_tracks_btn)
        manual_buttons_layout.addWidget(self.locate_file_btn)
        manual_buttons_layout.addWidget(self.delete_selected_btn)
        manual_buttons_layout.addWidget(self.delete_all_btn)

        main_layout.addLayout(manual_buttons_layout)

        # Ajouter le contenu principal au splitter
        self.splitter.addWidget(self.main_content)

        # Créer le panneau d'historique des encodages (côté gauche)
        self.history_panel = EncodingsHistoryPanel()
        self.history_panel.close_button.clicked.connect(self.hide_history_panel)

        # Créer le panneau de logs (côté droit)
        self.logs_panel = LogsPanel()
        self.logs_panel.close_button.clicked.connect(self.hide_logs_panel)

        # Ajouter les panneaux au splitter (initialement cachés)
        self.splitter.insertWidget(0, self.history_panel)  # Ajouter à gauche
        self.splitter.addWidget(self.logs_panel)  # Ajouter à droite

        # Définir les tailles initiales des widgets dans le splitter
        self.splitter.setSizes([0, 1, 0])  # Les deux panneaux sont initialement masqués

        # Stocker l'état des panneaux
        self.history_panel_visible = False
        self.logs_panel_visible = False

        # Index du dernier fichier de log chargé
        self.current_log_index = -1

        # Indicateur si tous les logs ont été chargés
        self.all_logs_loaded = False

        # État persistant des logs
        self.button_permanently_hidden = False  # Nouvelle variable persistante

        # Ou ajout d'une action dans un menu existant
        # file_menu = menubar.addMenu("Fichier")
        # self.queue_action = QAction("File d'attente (0)", self)
        # file_menu.addAction(self.queue_action)

        # Charger les encodages manuels au démarrage
        self.load_manual_encodings()

        # Référence à la fonction de nettoyage (sera définie par main.py)
        self.cleanup_function = None

    def set_control_flags(self, flags):
        """
        Définit les drapeaux de contrôle pour l'application
        """
        self.control_flags = flags

    def set_cleanup_function(self, cleanup_func):
        """
        Définit la fonction de nettoyage à appeler lors de la fermeture de la fenêtre
        """
        self.cleanup_function = cleanup_func

    def closeEvent(self, event):
        """
        Gestionnaire d'événement appelé lorsque la fenêtre est fermée
        """
        # Émettre le signal de fermeture
        self.closing.emit()

        # Signaler la fermeture de l'application aux processus d'encodage
        if hasattr(self, "control_flags"):
            self.control_flags["closing"] = True
            self.control_flags["app_closing"] = True  # Pour compatibilité

        # Attendre un peu pour que les threads puissent s'arrêter proprement
        import time

        time.sleep(0.5)

        # Appeler la fonction de nettoyage si elle a été définie
        if self.cleanup_function:
            self.cleanup_function()

        # Accepter l'événement de fermeture
        event.accept()

    def toggle_logs_panel(self):
        """Affiche ou masque le panneau de logs"""
        if self.logs_panel_visible:
            self.hide_logs_panel()
        else:
            # Si on ouvre à nouveau le panneau après l'avoir complètement fermé, on réinitialise l'état
            if not self.logs_panel_visible:
                self.reset_log_loading_state()
            self.show_logs_panel()

    def show_logs_panel(self):
        """Affiche le panneau de logs"""
        # Calculer les nouvelles tailles pour le splitter
        total_width = self.splitter.width()
        if self.history_panel_visible:
            # Si le panneau d'historique est visible, ajuster les tailles
            new_sizes = [
                int(total_width * 0.25),
                int(total_width * 0.5),
                int(total_width * 0.25),
            ]
        else:
            # Sinon, juste afficher le panneau de logs à droite
            new_sizes = [0, int(total_width * 0.7), int(total_width * 0.3)]

        self.splitter.setSizes(new_sizes)
        self.logs_panel_visible = True
        self.show_logs_button.setText("Masquer logs")

        # Si le bouton a été caché de façon permanente, ne pas le réafficher
        if self.button_permanently_hidden:
            self.load_old_logs_button.setVisible(False)

    def toggle_history_panel(self):
        """Affiche ou masque le panneau d'historique des encodages"""
        if self.history_panel_visible:
            self.hide_history_panel()
        else:
            self.show_history_panel()

    def show_history_panel(self):
        """Affiche le panneau d'historique des encodages"""
        # Charger les encodages récents
        self.refresh_history_panel()

        # Calculer les nouvelles tailles pour le splitter
        total_width = self.splitter.width()
        if self.logs_panel_visible:
            # Si le panneau de logs est visible, ajuster les tailles
            new_sizes = [
                int(total_width * 0.25),
                int(total_width * 0.5),
                int(total_width * 0.25),
            ]
        else:
            # Sinon, juste afficher le panneau d'historique à gauche
            new_sizes = [int(total_width * 0.3), int(total_width * 0.7), 0]

        self.splitter.setSizes(new_sizes)
        self.history_panel_visible = True
        self.show_history_button.setText("Masquer\nl'historique")

    def hide_history_panel(self):
        """Masque le panneau d'historique des encodages"""
        current_sizes = self.splitter.sizes()
        if self.logs_panel_visible:
            # Si le panneau de logs est visible, ajuster pour ne garder que le contenu principal et les logs
            self.splitter.setSizes(
                [0, current_sizes[1] + current_sizes[0], current_sizes[2]]
            )
        else:
            # Sinon, tout donner au contenu principal
            self.splitter.setSizes([0, sum(current_sizes), 0])

        self.history_panel_visible = False
        self.show_history_button.setText("Historique\ndes encodages")

    def refresh_history_panel(self):
        """Rafraîchit le panneau d'historique des encodages avec les données récentes"""
        self.history_panel.load_recent_encodings()

    def hide_logs_panel(self):
        """Masque le panneau de logs et préserve l'état persistant du bouton"""
        current_sizes = self.splitter.sizes()
        if self.history_panel_visible:
            # Si le panneau d'historique est visible, ajuster pour ne garder que le contenu principal et l'historique
            self.splitter.setSizes(
                [current_sizes[0], current_sizes[1] + current_sizes[2], 0]
            )
        else:
            # Sinon, tout donner au contenu principal
            self.splitter.setSizes([0, sum(current_sizes), 0])

        self.logs_panel_visible = False
        self.show_logs_button.setText("Afficher logs")

        # Ne réinitialiser que si le bouton n'est pas caché de façon permanente
        if not self.button_permanently_hidden:
            self.current_log_index = -1
            self.load_old_logs_button.setVisible(True)
            self.load_old_logs_button.setText("Charger les\nanciens logs")

    def add_log(self, message, level="INFO", custom_color=None):
        """Ajoute un message dans la zone de logs avec coloration selon le niveau ou personnalisée"""
        color_map = {
            "DEBUG": "gray",
            "INFO": "white",
            "WARNING": "orange",
            "ERROR": "red",
            "CRITICAL": "darkred",
        }
        # Utiliser la couleur personnalisée si fournie, sinon celle du niveau
        color = custom_color if custom_color else color_map.get(level, "black")

        # Stocker le log dans notre historique récent
        self.recent_logs.append((message, level, custom_color))
        # Garder seulement les 1000 derniers logs pour éviter une consommation excessive de mémoire
        if len(self.recent_logs) > 1000:
            self.recent_logs.pop(0)

        # Si c'est un log de debug et qu'ils sont masqués, ne pas l'afficher
        if level == "DEBUG" and not self.show_debug_logs:
            return

        # Ajouter le message au panneau de logs
        if hasattr(self, "logs_panel"):
            self.logs_panel.log_text.append(
                f"<span style='color:{color};'>{message}</span>"
            )

            # Auto-scroll to bottom
            sb = self.logs_panel.log_text.verticalScrollBar()
            sb.setValue(sb.maximum())

    def update_queue(self, queue_files):
        """Met à jour la liste des encodages en attente"""
        self.queue_list.clear()

        # Mettre à jour le nombre de fichiers dans le menu (toujours le faire, même si vide)
        queue_count = len(queue_files)
        self.update_queue_count_in_menu(queue_count)

        if not queue_files:
            self.queue_list.addItem("Aucun fichier en attente")
            # Désactiver les boutons de manipulation quand la file est vide
            self.set_queue_buttons_state(False)
            return

        # Activer les boutons de manipulation
        self.set_queue_buttons_state(True)

        for i, item in enumerate(queue_files, 1):
            if isinstance(item, dict):
                # Si l'élément est un dictionnaire
                filename = os.path.basename(item.get("file", "Inconnu"))
                preset = item.get("preset", "Preset inconnu")
                # Stocker l'élément original comme userData pour pouvoir le récupérer plus tard
                list_item = QListWidgetItem(f"{i}. {filename} - {preset}")
                list_item.setData(Qt.UserRole, item)
            elif isinstance(item, tuple) and len(item) >= 2:
                # Si l'élément est un tuple
                filename = os.path.basename(item[0])
                preset = item[1]
                list_item = QListWidgetItem(f"{i}. {filename} - {preset}")
                list_item.setData(Qt.UserRole, item)
            else:
                # Format inconnu
                list_item = QListWidgetItem("Format inconnu")
                list_item.setData(Qt.UserRole, item)

            self.queue_list.addItem(list_item)

    def set_queue_buttons_state(self, enabled):
        """Active ou désactive les boutons de manipulation de la file d'attente"""
        self.queue_delete_btn.setEnabled(enabled)
        self.queue_up_btn.setEnabled(enabled)
        self.queue_top_btn.setEnabled(enabled)
        self.queue_down_btn.setEnabled(enabled)
        self.queue_bottom_btn.setEnabled(enabled)
        self.queue_clear_btn.setEnabled(enabled)

    def delete_queue_item(self):
        """Supprime l'élément sélectionné de la file d'attente"""
        current_row = self.queue_list.currentRow()
        if current_row == -1:
            self.add_log(
                "Aucun élément sélectionné dans la file d'attente", "WARNING", "orange"
            )
            return

        # Récupérer la liste actuelle des fichiers en attente
        queue_files = self.get_current_queue_files()

        # Vérifier si la file contient uniquement le message "Aucun fichier en attente"
        if (
            len(queue_files) == 1
            and self.queue_list.item(0).text() == "Aucun fichier en attente"
        ):
            return

        # Supprimer l'élément de la liste
        if 0 <= current_row < len(queue_files):
            del queue_files[current_row]

            # Mettre à jour la file d'attente
            self.update_queue(queue_files)

            # Sélectionner le même index ou le dernier élément si on a supprimé le dernier
            new_row = min(current_row, self.queue_list.count() - 1)
            if new_row >= 0:
                self.queue_list.setCurrentRow(new_row)

            self.add_log(f"Élément supprimé de la file d'attente", "INFO", "green")

            # Signaler le changement de la file d'attente et forcer la mise à jour immédiate
            if hasattr(self, "control_flags"):
                self.control_flags["queue_modified"] = True
                # Forcer la mise à jour immédiate
                from state_persistence import save_interrupted_encodings

                save_interrupted_encodings(None, queue_files)

    def move_queue_item_up(self):
        """Déplace l'élément sélectionné vers le haut dans la file d'attente"""
        current_row = self.queue_list.currentRow()
        if current_row <= 0:
            return  # Premier élément ou aucun élément sélectionné

        # Récupérer la liste actuelle des fichiers en attente
        queue_files = self.get_current_queue_files()

        # Vérifier si la file contient uniquement le message "Aucun fichier en attente"
        if (
            len(queue_files) == 1
            and self.queue_list.item(0).text() == "Aucun fichier en attente"
        ):
            return

        # Échanger l'élément avec celui au-dessus
        queue_files[current_row], queue_files[current_row - 1] = (
            queue_files[current_row - 1],
            queue_files[current_row],
        )

        # Mettre à jour la file d'attente
        self.update_queue(queue_files)

        # Sélectionner l'élément déplacé
        self.queue_list.setCurrentRow(current_row - 1)

        self.add_log(
            f"Élément déplacé vers le haut dans la file d'attente", "INFO", "green"
        )

        # Signaler le changement de la file d'attente et forcer la mise à jour immédiate
        if hasattr(self, "control_flags"):
            self.control_flags["queue_modified"] = True
            # Forcer la mise à jour immédiate
            from state_persistence import save_interrupted_encodings

            save_interrupted_encodings(None, queue_files)

    def move_queue_item_to_top(self):
        """Déplace l'élément sélectionné tout en haut de la file d'attente"""
        current_row = self.queue_list.currentRow()
        if current_row <= 0:
            return  # Premier élément ou aucun élément sélectionné

        # Récupérer la liste actuelle des fichiers en attente
        queue_files = self.get_current_queue_files()

        # Vérifier si la file contient uniquement le message "Aucun fichier en attente"
        if (
            len(queue_files) == 1
            and self.queue_list.item(0).text() == "Aucun fichier en attente"
        ):
            return

        # Extraire l'élément à déplacer
        item_to_move = queue_files.pop(current_row)

        # L'insérer au début de la liste
        queue_files.insert(0, item_to_move)

        # Mettre à jour la file d'attente
        self.update_queue(queue_files)

        # Sélectionner l'élément déplacé
        self.queue_list.setCurrentRow(0)

        self.add_log(
            f"Élément déplacé tout en haut de la file d'attente", "INFO", "green"
        )

        # Signaler le changement de la file d'attente et forcer la mise à jour immédiate
        if hasattr(self, "control_flags"):
            self.control_flags["queue_modified"] = True
            # Forcer la mise à jour immédiate
            from state_persistence import save_interrupted_encodings

            save_interrupted_encodings(None, queue_files)

    def move_queue_item_down(self):
        """Déplace l'élément sélectionné vers le bas dans la file d'attente"""
        current_row = self.queue_list.currentRow()
        if current_row == -1 or current_row >= self.queue_list.count() - 1:
            return  # Dernier élément ou aucun élément sélectionné

        # Récupérer la liste actuelle des fichiers en attente
        queue_files = self.get_current_queue_files()

        # Vérifier si la file contient uniquement le message "Aucun fichier en attente"
        if (
            len(queue_files) == 1
            and self.queue_list.item(0).text() == "Aucun fichier en attente"
        ):
            return

        # Échanger l'élément avec celui en-dessous
        queue_files[current_row], queue_files[current_row + 1] = (
            queue_files[current_row + 1],
            queue_files[current_row],
        )

        # Mettre à jour la file d'attente
        self.update_queue(queue_files)

        # Sélectionner l'élément déplacé
        self.queue_list.setCurrentRow(current_row + 1)

        self.add_log(
            f"Élément déplacé vers le bas dans la file d'attente", "INFO", "green"
        )

        # Signaler le changement de la file d'attente et forcer la mise à jour immédiate
        if hasattr(self, "control_flags"):
            self.control_flags["queue_modified"] = True
            # Forcer la mise à jour immédiate
            from state_persistence import save_interrupted_encodings

            save_interrupted_encodings(None, queue_files)

    def move_queue_item_to_bottom(self):
        """Déplace l'élément sélectionné tout en bas de la file d'attente"""
        current_row = self.queue_list.currentRow()
        if current_row == -1 or current_row >= self.queue_list.count() - 1:
            return  # Dernier élément ou aucun élément sélectionné

        # Récupérer la liste actuelle des fichiers en attente
        queue_files = self.get_current_queue_files()

        # Vérifier si la file contient uniquement le message "Aucun fichier en attente"
        if (
            len(queue_files) == 1
            and self.queue_list.item(0).text() == "Aucun fichier en attente"
        ):
            return

        # Extraire l'élément à déplacer
        item_to_move = queue_files.pop(current_row)

        # L'ajouter à la fin de la liste
        queue_files.append(item_to_move)

        # Mettre à jour la file d'attente
        self.update_queue(queue_files)

        # Sélectionner l'élément déplacé
        self.queue_list.setCurrentRow(len(queue_files) - 1)

        self.add_log(
            f"Élément déplacé tout en bas de la file d'attente", "INFO", "green"
        )

        # Signaler le changement de la file d'attente et forcer la mise à jour immédiate
        if hasattr(self, "control_flags"):
            self.control_flags["queue_modified"] = True
            # Forcer la mise à jour immédiate
            from state_persistence import save_interrupted_encodings

            save_interrupted_encodings(None, queue_files)

    def clear_queue(self):
        """Vide complètement la file d'attente"""
        # Récupérer la liste actuelle des fichiers en attente
        queue_files = self.get_current_queue_files()

        # Vérifier si la file contient uniquement le message "Aucun fichier en attente"
        if (
            len(queue_files) == 1
            and self.queue_list.item(0).text() == "Aucun fichier en attente"
        ):
            return

        # Vider la file d'attente
        self.update_queue([])

        self.add_log("File d'attente vidée", "INFO", "green")

        # Signaler le changement de la file d'attente et forcer la mise à jour immédiate
        if hasattr(self, "control_flags"):
            self.control_flags["queue_modified"] = True
            self.control_flags["queue_cleared"] = True
            # Forcer la mise à jour immédiate
            from state_persistence import (
                clear_interrupted_encodings,
            )

            clear_interrupted_encodings()

    def get_current_queue_files(self):
        """Récupère la liste actuelle des fichiers en attente à partir du QListWidget"""
        queue_files = []
        for i in range(self.queue_list.count()):
            item = self.queue_list.item(i)
            # Si c'est le message "Aucun fichier en attente", retourner une liste vide
            if item.text() == "Aucun fichier en attente":
                return []
            # Récupérer l'élément original stocké dans userData
            queue_files.append(item.data(Qt.UserRole))
        return queue_files

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
            with open(fichier_encodage_manuel, "r", encoding="utf-8") as f:
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
            with open(fichier_encodage_manuel, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # Filtrer les lignes à conserver
            selected_texts = [item.text() for item in selected_items]
            filtered_lines = [
                line for line in lines if line.strip() not in selected_texts
            ]

            # Réécrire le fichier sans les lignes sélectionnées
            with open(fichier_encodage_manuel, "w", encoding="utf-8") as f:
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
            with open(fichier_encodage_manuel, "w", encoding="utf-8") as f:
                pass

            self.add_log(
                "Tous les encodages manuels ont été supprimés", "INFO", "green"
            )
            self.load_manual_encodings()
        except Exception as e:
            self.add_log(f"Erreur lors de la suppression: {str(e)}", "ERROR")

    def toggle_notifications(self, state):
        """Active ou désactive les notifications Windows"""
        from notifications import set_notifications_enabled
        from config import save_config, load_config

        # Mettre à jour l'état des notifications
        notifications_enabled = state == Qt.Checked
        set_notifications_enabled(notifications_enabled)

        # Sauvegarder la préférence
        config = load_config()
        config["notifications_enabled"] = notifications_enabled
        save_config(config)

        # Ajouter un message dans les logs
        status = "activées" if notifications_enabled else "désactivées"
        self.add_log(f"Notifications Windows {status}", "INFO", "green")

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

        except Exception as e:
            self.add_log(
                f"Erreur lors de la localisation du fichier: {str(e)}",
                "ERROR",
                "red",
            )

    def load_last_log(self):
        """
        Charge les anciens fichiers de logs de façon séquentielle.
        À chaque clic, charge un fichier plus ancien que le précédent.
        Cache le bouton une fois tous les logs chargés.
        """
        import os
        from datetime import datetime

        # Définir le chemin de base en fonction de l'exécution en tant que script ou exécutable
        if getattr(sys, "frozen", False):
            # Mode exécutable - utiliser le dossier où se trouve l'exécutable
            BASE_PATH = os.path.dirname(sys.executable)
        else:
            # Mode développement - utiliser le dossier du script
            BASE_PATH = os.path.dirname(os.path.abspath(__file__))

        # Créer le dossier logs s'il n'existe pas
        logs_dir = os.path.join(BASE_PATH, "logs")

        if not os.path.exists(logs_dir):
            self.add_log("Dossier de logs non trouvé", "WARNING", "orange")
            return

        # Récupérer tous les fichiers de logs (en supposant qu'ils ont l'extension .log)
        log_files = [f for f in os.listdir(logs_dir) if f.endswith(".log")]

        if not log_files:
            self.add_log("Aucun fichier de log archivé trouvé", "INFO", "gray")
            return

        # Trier les fichiers par date de modification (le plus récent d'abord)
        log_files.sort(
            key=lambda x: os.path.getmtime(os.path.join(logs_dir, x)), reverse=True
        )

        # Si le panneau de logs n'est pas visible, l'afficher
        if not self.logs_panel_visible:
            self.show_logs_panel()

        # Avancer à l'index suivant à chaque appel
        self.current_log_index += 1

        # Si on a atteint la fin de la liste
        if self.current_log_index >= len(log_files):
            # Masquer le bouton de chargement des anciens logs de façon permanente
            self.load_old_logs_button.setVisible(False)
            self.button_permanently_hidden = (
                True  # Marquer que le bouton est caché de façon permanente
            )
            self.add_log("Tous les fichiers de logs ont été chargés", "INFO", "green")
            # Marquer que tous les logs ont été chargés
            self.all_logs_loaded = True
            return

        # Sélectionner le fichier de log selon l'index courant
        current_log_file = log_files[self.current_log_index]
        file_path = os.path.join(logs_dir, current_log_file)

        # Afficher l'information sur le fichier qu'on charge
        self.add_log(
            f"Chargement du fichier de logs {self.current_log_index + 1}/{len(log_files)}: {current_log_file}",
            "INFO",
            "cyan",
        )

        # Afficher combien de fichiers de logs restent
        logs_restants = len(log_files) - self.current_log_index - 1
        if logs_restants > 0:
            self.load_old_logs_button.setText(
                f"Charger logs\n({logs_restants} restants)"
            )
        else:
            self.load_old_logs_button.setText("Charger logs\n(dernier)")

        try:
            # Obtenir la date de modification du fichier
            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            mod_time_str = mod_time.strftime("%d/%m/%Y %H:%M:%S")

            # Lire le contenu du fichier
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

                # Prendre uniquement les 600 dernières lignes
                if len(lines) > 600:
                    lines = lines[-600:]
                    truncated_message = f"<i>Affichage des 600 dernières lignes sur {len(lines)} au total...</i>"
                else:
                    truncated_message = (
                        f"<i>Affichage des {len(lines)} lignes du fichier...</i>"
                    )

                # Préparer le HTML pour insérer les anciens logs
                log_html = f"<hr><h3>ANCIEN LOG ({self.current_log_index + 1}/{len(log_files)}): {current_log_file} (modifié le {mod_time_str})</h3>"
                log_html += truncated_message + "<br>"

                # Récupérer l'ancien contenu
                ancien_contenu = self.logs_panel.log_text.toHtml()

                # Formatter les lignes avec coloration
                for line in lines:
                    line_html = line.strip()
                    if "WARNING" in line:
                        log_html += (
                            f"<span style='color:orange;'>{line_html}</span><br>"
                        )
                    elif "ERROR" in line or "CRITICAL" in line:
                        log_html += f"<span style='color:red;'>{line_html}</span><br>"
                    elif "INFO" in line:
                        log_html += f"<span style='color:white;'>{line_html}</span><br>"
                    else:
                        log_html += f"<span style='color:gray;'>{line_html}</span><br>"

                log_html += "<hr>"

                # Extraire le contenu du body
                if "<body" in ancien_contenu and "</body>" in ancien_contenu:
                    debut = ancien_contenu.find("<body")
                    debut = ancien_contenu.find(">", debut) + 1
                    fin = ancien_contenu.find("</body>")
                    contenu_body = ancien_contenu[debut:fin]

                    # Reconstruire le HTML avec les anciens logs au début
                    debut_html = ancien_contenu[:debut]
                    fin_html = ancien_contenu[fin:]
                    nouveau_html = debut_html + log_html + contenu_body + fin_html

                    # Mettre à jour le contenu
                    self.logs_panel.log_text.setHtml(nouveau_html)
                else:
                    # Fallback si la structure HTML n'est pas standard
                    # Insérer au début du texte actuel
                    self.logs_panel.log_text.clear()
                    self.logs_panel.log_text.setHtml(log_html + ancien_contenu)

        except Exception as e:
            self.add_log(
                f"Erreur lors du chargement des logs: {str(e)}",
                "ERROR",
                "red",
            )

    def reset_log_loading_state(self):
        """Réinitialise l'état de chargement des logs"""
        self.current_log_index = -1
        self.all_logs_loaded = False
        self.load_old_logs_button.setVisible(True)
        self.load_old_logs_button.setText("Charger les\nanciens logs")

    def add_to_queue(self):
        """Ajoute un fichier ou dossier à la file d'attente"""
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFiles)  # Permet la multi-sélection
        dialog.setOptions(options)
        dialog.setWindowTitle("Sélectionner fichiers ou dossiers à ajouter")
        dialog.setNameFilter(f"Fichiers vidéo (*{' *'.join(extensions)})")

        if dialog.exec_():
            selected_files = dialog.selectedFiles()

            # Créer une boîte de dialogue pour choisir le preset
            preset_dialog = QMessageBox()
            preset_dialog.setWindowTitle("Sélectionner un preset")
            preset_dialog.setText("Veuillez choisir un preset pour ces fichiers:")
            preset_dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

            # Ajouter une liste déroulante des presets disponibles
            preset_combo = QComboBox(preset_dialog)
            for preset in dossiers_presets.values():
                preset_combo.addItem(preset)

            # Positionner la liste déroulante
            layout = preset_dialog.layout()
            if layout is not None:
                layout.addWidget(preset_combo, 1, 0, 1, layout.columnCount())
            else:
                preset_dialog.setDetailedText("Presets indisponibles")

            # Si on clique sur "Ok", on continue avec le preset sélectionné
            if preset_dialog.exec_() == QMessageBox.Ok:
                selected_preset = preset_combo.currentText()

                # Collecter tous les fichiers à ajouter
                files_to_add = []

                # Parcourir les éléments sélectionnés
                for path in selected_files:
                    if os.path.isdir(path):
                        # Si c'est un dossier, scanner récursivement
                        folder_files = self.scan_folder_recursively(path)
                        for file_path in folder_files:
                            files_to_add.append(
                                {"file": file_path, "preset": selected_preset}
                            )
                    else:
                        # Si c'est un fichier, vérifier l'extension
                        if any(path.lower().endswith(ext) for ext in extensions):
                            files_to_add.append(
                                {"file": path, "preset": selected_preset}
                            )

                # Récupérer la file d'attente actuelle
                current_queue = self.get_current_queue_files()

                # Ajouter les nouveaux fichiers
                for file_info in files_to_add:
                    current_queue.append(file_info)

                # Mettre à jour l'interface
                self.update_queue(current_queue)

                # Signaler le changement à l'encodeur
                if hasattr(self, "control_flags"):
                    self.control_flags["queue_modified"] = True
                    # Forcer la mise à jour immédiate
                    from state_persistence import save_interrupted_encodings

                    save_interrupted_encodings(None, current_queue)

                self.add_log(
                    f"Ajouté {len(files_to_add)} fichier(s) à la file d'attente",
                    "INFO",
                    "green",
                )

    def scan_folder_recursively(self, folder_path):
        """Scanne un dossier récursivement pour trouver tous les fichiers vidéo"""
        found_files = []

        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if any(file.lower().endswith(ext) for ext in extensions):
                    full_path = os.path.join(root, file)
                    found_files.append(full_path)

        return found_files

    def toggle_debug_logs(self):
        """Affiche ou masque les logs de debug"""
        self.show_debug_logs = not self.show_debug_logs

        # Recharger les logs avec le nouveau filtre
        self.refresh_logs_display()

    def refresh_logs_display(self):
        """Rafraîchit l'affichage des logs selon le filtre actuel"""
        if not hasattr(self, "logs_panel") or not self.logs_panel_visible:
            return

        # Sauvegarder la position du curseur actuel
        scrollbar = self.logs_panel.log_text.verticalScrollBar()
        scroll_position = scrollbar.value()

        # Vider le contenu
        self.logs_panel.log_text.clear()

        # Réafficher les logs selon le filtre
        for log_entry in self.recent_logs:
            message, level, custom_color = log_entry

            # Filtrer les logs de debug si nécessaire
            if level == "DEBUG" and not self.show_debug_logs:
                continue

            # Déterminer la couleur du texte
            color_map = {
                "DEBUG": "gray",
                "INFO": "white",
                "WARNING": "orange",
                "ERROR": "red",
                "CRITICAL": "darkred",
            }
            color = custom_color if custom_color else color_map.get(level, "black")

            # Ajouter le message
            self.logs_panel.log_text.append(
                f"<span style='color:{color};'>{message}</span>"
            )

        # Restaurer la position de défilement si elle était en bas
        if scroll_position == scrollbar.maximum():
            # Position tout en bas
            scrollbar.setValue(scrollbar.maximum())
        else:
            # Essayer de restaurer la position précise
            scrollbar.setValue(scroll_position)

    def open_track_editor(self):
        """Ouvre la fenêtre d'édition des pistes audio et sous-titres pour le fichier sélectionné"""
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
                    "Impossible d'ouvrir l'éditeur (chemin complet non disponible)",
                    "ERROR",
                    "red",
                )
                return

            # Vérifier si le fichier existe
            if not os.path.exists(filepath):
                self.add_log(f"Le fichier n'existe pas: {filepath}", "ERROR", "red")
                return

            # Importer la classe éditeur de pistes
            from track_editor import TrackEditorDialog

            # Créer et afficher la fenêtre d'édition
            editor = TrackEditorDialog(filepath, parent=self)
            editor.exec_()

        except Exception as e:
            self.add_log(
                f"Erreur lors de l'ouverture de l'éditeur de pistes: {str(e)}",
                "ERROR",
                "red",
            )
