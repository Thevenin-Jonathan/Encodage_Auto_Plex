import os
import sys
import json
import subprocess
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QComboBox,
    QLineEdit,
    QCheckBox,
    QMessageBox,
    QHeaderView,
    QTabWidget,
    QWidget,
    QApplication,
    QDialogButtonBox,
    QGridLayout,  # Ajouté pour un meilleur contrôle de la mise en page
    QSizePolicy,  # Ajouté pour le contrôle de la taille
)
from PyQt5.QtCore import Qt
from logger import setup_logger, colored_log
from constants import BASE_PATH, dossiers_presets

# Configuration du logger
logger = setup_logger(__name__)

# Chemin vers ffmpeg.exe
FFMPEG_PATH = os.path.join(BASE_PATH, "bin", "ffmpeg.exe")
FFPROBE_PATH = os.path.join(BASE_PATH, "bin", "ffprobe.exe")

# Liste des codes de langues courantes
LANGUAGE_CODES = {
    "Français": "fra",
    "Anglais": "eng",
    "Allemand": "ger",
    "Espagnol": "spa",
    "Italien": "ita",
    "Japonais": "jpn",
    "Russe": "rus",
    "Chinois": "chi",
    "Coréen": "kor",
    "Arabe": "ara",
    "Néerlandais": "dut",
    "Portugais": "por",
    "Suédois": "swe",
    "Turc": "tur",
    "Polonais": "pol",
    "Danois": "dan",
    "Finnois": "fin",
    "Norvégien": "nor",
    "Tchèque": "cze",
    "Hongrois": "hun",
    "Grec": "gre",
    "Hébreu": "heb",
    "Hindi": "hin",
    "Thaï": "tha",
    "Ukrainien": "ukr",
    "Bulgare": "bul",
    "Croate": "hrv",
    "Serbe": "srp",
    "Roumain": "rum",
    "Slovaque": "slo",
    "Slovène": "slv",
    "Islandais": "ice",
    "Estonien": "est",
    "Letton": "lav",
    "Lituanien": "lit",
    "Vietnamien": "vie",
    "Catalan": "cat",
    "Basque": "baq",
    "Gallois": "wel",
    "Irlandais": "gle",
    "Maltais": "mlt",
    "Non spécifié": "und",
}


class TrackEditorDialog(QDialog):
    """Fenêtre de dialogue pour éditer les pistes audio et sous-titres"""

    def __init__(self, filepath, parent=None):
        super().__init__(parent)
        self.filepath = filepath
        self.filename = os.path.basename(filepath)
        self.setWindowTitle(f"Édition des pistes - {self.filename}")
        self.setMinimumSize(800, 600)

        # Pour stocker les données des pistes
        self.audio_tracks = []
        self.subtitle_tracks = []
        self.modified = False  # Flag pour suivre les modifications

        # Initialiser l'interface
        self.init_ui()

        # Charger les informations des pistes
        self.load_track_info()

    def init_ui(self):
        """Initialiser l'interface utilisateur"""
        layout = QVBoxLayout(self)

        # Label du fichier
        file_label = QLabel(f"Fichier: {self.filename}")
        file_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(file_label)

        # Onglets pour séparer les pistes audio et sous-titres
        tabs = QTabWidget()

        # Onglet pour les pistes audio
        audio_tab = QWidget()
        audio_layout = QVBoxLayout(audio_tab)

        # Tableau pour les pistes audio
        self.audio_table = QTableWidget()
        self.audio_table.setColumnCount(6)
        self.audio_table.setHorizontalHeaderLabels(
            ["N°", "Type", "Langue", "Titre", "Codec", "Actions"]
        )
        self.audio_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.audio_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents
        )
        self.audio_table.horizontalHeader().setSectionResizeMode(
            5, QHeaderView.ResizeToContents
        )
        audio_layout.addWidget(self.audio_table)

        # Boutons pour les pistes audio
        audio_buttons = QHBoxLayout()
        self.save_audio_btn = QPushButton("Appliquer les changements audio")
        self.save_audio_btn.clicked.connect(lambda: self.apply_changes("audio"))
        self.save_audio_btn.setEnabled(False)

        audio_buttons.addStretch()
        audio_buttons.addWidget(self.save_audio_btn)
        audio_layout.addLayout(audio_buttons)

        tabs.addTab(audio_tab, "Pistes Audio")

        # Onglet pour les pistes de sous-titres
        subtitle_tab = QWidget()
        subtitle_layout = QVBoxLayout(subtitle_tab)

        # Tableau pour les pistes de sous-titres
        self.subtitle_table = QTableWidget()
        self.subtitle_table.setColumnCount(7)
        self.subtitle_table.setHorizontalHeaderLabels(
            ["N°", "Type", "Langue", "Titre", "Forcé", "Défaut", "Actions"]
        )
        self.subtitle_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.subtitle_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeToContents
        )
        self.subtitle_table.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.ResizeToContents
        )
        self.subtitle_table.horizontalHeader().setSectionResizeMode(
            5, QHeaderView.ResizeToContents
        )
        self.subtitle_table.horizontalHeader().setSectionResizeMode(
            6, QHeaderView.ResizeToContents
        )
        subtitle_layout.addWidget(self.subtitle_table)

        # Boutons pour les pistes de sous-titres
        subtitle_buttons = QHBoxLayout()
        self.save_subtitle_btn = QPushButton("Appliquer les changements de sous-titres")
        self.save_subtitle_btn.clicked.connect(lambda: self.apply_changes("subtitle"))
        self.save_subtitle_btn.setEnabled(False)

        subtitle_buttons.addStretch()
        subtitle_buttons.addWidget(self.save_subtitle_btn)
        subtitle_layout.addLayout(subtitle_buttons)

        tabs.addTab(subtitle_tab, "Sous-titres")

        layout.addWidget(tabs)

        # Bouton pour appliquer toutes les modifications en une seule fois
        self.apply_all_btn = QPushButton("Appliquer toutes les modifications")
        self.apply_all_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #3A6EA5;
                color: white;
                font-weight: bold;
                min-height: 40px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #4A8FD5;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
        """
        )
        self.apply_all_btn.clicked.connect(self.apply_all_changes)
        self.apply_all_btn.setEnabled(False)
        layout.addWidget(self.apply_all_btn)

        # Boutons de fermeture
        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.close_with_check)
        layout.addWidget(buttons)

    def load_track_info(self):
        """Charge les informations sur les pistes audio et sous-titres"""
        try:
            # Vérifier si ffprobe existe
            if not os.path.exists(FFPROBE_PATH):
                logger.error(f"ffprobe introuvable à l'emplacement: {FFPROBE_PATH}")
                QMessageBox.critical(
                    self,
                    "Erreur",
                    f"ffprobe introuvable à l'emplacement: {FFPROBE_PATH}\nVérifiez que ffprobe.exe est présent dans le dossier bin.",
                )
                return

            # Utiliser ffprobe pour obtenir les informations du fichier
            cmd = [
                FFPROBE_PATH,
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                self.filepath,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Erreur lors de l'exécution de ffprobe: {result.stderr}")
                QMessageBox.critical(
                    self,
                    "Erreur",
                    "Impossible d'obtenir des informations sur le fichier.",
                )
                return

            # Analyser les données JSON
            file_info = json.loads(result.stdout)

            # Vider les tableaux
            self.audio_table.setRowCount(0)
            self.subtitle_table.setRowCount(0)

            # Réinitialiser les listes
            self.audio_tracks = []
            self.subtitle_tracks = []

            # Parcourir les flux
            for i, stream in enumerate(file_info.get("streams", [])):
                codec_type = stream.get("codec_type")

                if codec_type == "audio":
                    self.add_audio_track(stream, i)
                elif codec_type == "subtitle":
                    self.add_subtitle_track(stream, i)

            # Mettre à jour les tableaux
            self.update_audio_table()
            self.update_subtitle_table()

            # Désactiver les boutons s'il n'y a pas de pistes
            self.save_audio_btn.setEnabled(bool(self.audio_tracks))
            self.save_subtitle_btn.setEnabled(bool(self.subtitle_tracks))

        except Exception as e:
            logger.error(
                f"Erreur lors du chargement des informations de piste: {str(e)}"
            )
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors du chargement des informations de piste:\n{str(e)}",
            )

    def add_audio_track(self, stream, index):
        """Ajoute une piste audio à la liste"""
        track = {
            "index": stream.get("index", index),
            "codec_name": stream.get("codec_name", "Unknown"),
            "language": stream.get("tags", {}).get("language", "und"),
            "title": stream.get("tags", {}).get("title", ""),
            "stream_index": stream.get("index"),
            "original_language": stream.get("tags", {}).get("language", "und"),
            "original_title": stream.get("tags", {}).get("title", ""),
            "modified": False,
        }
        self.audio_tracks.append(track)

    def add_subtitle_track(self, stream, index):
        """Ajoute une piste de sous-titres à la liste"""
        track = {
            "index": stream.get("index", index),
            "codec_name": stream.get("codec_name", "Unknown"),
            "language": stream.get("tags", {}).get("language", "und"),
            "title": stream.get("tags", {}).get("title", ""),
            "disposition": stream.get("disposition", {}),
            "forced": stream.get("disposition", {}).get("forced", 0) == 1,
            "default": stream.get("disposition", {}).get("default", 0) == 1,
            "stream_index": stream.get("index"),
            "original_language": stream.get("tags", {}).get("language", "und"),
            "original_title": stream.get("tags", {}).get("title", ""),
            "original_forced": stream.get("disposition", {}).get("forced", 0) == 1,
            "original_default": stream.get("disposition", {}).get("default", 0) == 1,
            "modified": False,
        }
        self.subtitle_tracks.append(track)

    def update_audio_table(self):
        """Met à jour le tableau des pistes audio"""
        self.audio_table.setRowCount(len(self.audio_tracks))

        for row, track in enumerate(self.audio_tracks):
            # Numéro de piste
            index_item = QTableWidgetItem(str(row + 1))
            index_item.setFlags(index_item.flags() & ~Qt.ItemIsEditable)
            self.audio_table.setItem(row, 0, index_item)

            # Type (codec)
            codec_item = QTableWidgetItem(track["codec_name"])
            codec_item.setFlags(codec_item.flags() & ~Qt.ItemIsEditable)
            self.audio_table.setItem(row, 4, codec_item)

            # Type de piste
            type_item = QTableWidgetItem("Audio")
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.audio_table.setItem(row, 1, type_item)

            # Langue (combobox)
            language_combo = QComboBox()
            for name, code in LANGUAGE_CODES.items():
                language_combo.addItem(f"{name} ({code})", code)

            # Sélectionner la langue actuelle
            current_lang = track["language"]
            for i in range(language_combo.count()):
                if language_combo.itemData(i) == current_lang:
                    language_combo.setCurrentIndex(i)
                    break

            language_combo.currentIndexChanged.connect(
                lambda idx, r=row: self.update_audio_lang(r, idx)
            )
            self.audio_table.setCellWidget(row, 2, language_combo)

            # Titre (éditable)
            title_edit = QLineEdit(track["title"])
            title_edit.textChanged.connect(
                lambda text, r=row: self.update_audio_title(r, text)
            )
            self.audio_table.setCellWidget(row, 3, title_edit)

            # Actions (bouton)
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(5, 2, 5, 2)

            # Bouton de suppression
            delete_btn = QPushButton("Supprimer")
            delete_btn.setStyleSheet("background-color: #A94442;")
            delete_btn.clicked.connect(lambda _, r=row: self.remove_audio_track(r))

            actions_layout.addWidget(delete_btn)

            # Widget container pour le layout des actions
            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            self.audio_table.setCellWidget(row, 5, actions_widget)

    def update_subtitle_table(self):
        """Met à jour le tableau des pistes de sous-titres"""
        self.subtitle_table.setRowCount(len(self.subtitle_tracks))

        for row, track in enumerate(self.subtitle_tracks):
            # Numéro de piste
            index_item = QTableWidgetItem(str(row + 1))
            index_item.setFlags(index_item.flags() & ~Qt.ItemIsEditable)
            self.subtitle_table.setItem(row, 0, index_item)

            # Type de piste
            type_item = QTableWidgetItem("Sous-titre")
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)
            self.subtitle_table.setItem(row, 1, type_item)

            # Langue (combobox)
            language_combo = QComboBox()
            for name, code in LANGUAGE_CODES.items():
                language_combo.addItem(f"{name} ({code})", code)

            # Sélectionner la langue actuelle
            current_lang = track["language"]
            for i in range(language_combo.count()):
                if language_combo.itemData(i) == current_lang:
                    language_combo.setCurrentIndex(i)
                    break

            language_combo.currentIndexChanged.connect(
                lambda idx, r=row: self.update_subtitle_lang(r, idx)
            )
            self.subtitle_table.setCellWidget(row, 2, language_combo)

            # Titre (éditable)
            title_edit = QLineEdit(track["title"])
            title_edit.textChanged.connect(
                lambda text, r=row: self.update_subtitle_title(r, text)
            )
            self.subtitle_table.setCellWidget(row, 3, title_edit)

            # Case à cocher pour "forcé"
            forced_check = QCheckBox()
            forced_check.setChecked(track["forced"])
            forced_check.stateChanged.connect(
                lambda state, r=row: self.update_subtitle_forced(r, state)
            )
            forced_check_container = QWidget()
            forced_check_layout = QHBoxLayout(forced_check_container)
            forced_check_layout.addWidget(forced_check)
            forced_check_layout.setAlignment(Qt.AlignCenter)
            forced_check_layout.setContentsMargins(0, 0, 0, 0)
            self.subtitle_table.setCellWidget(row, 4, forced_check_container)

            # Case à cocher pour "par défaut"
            default_check = QCheckBox()
            default_check.setChecked(track["default"])
            default_check.stateChanged.connect(
                lambda state, r=row: self.update_subtitle_default(r, state)
            )
            default_check_container = QWidget()
            default_check_layout = QHBoxLayout(default_check_container)
            default_check_layout.addWidget(default_check)
            default_check_layout.setAlignment(Qt.AlignCenter)
            default_check_layout.setContentsMargins(0, 0, 0, 0)
            self.subtitle_table.setCellWidget(row, 5, default_check_container)

            # Actions (bouton)
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(5, 2, 5, 2)

            # Bouton de suppression
            delete_btn = QPushButton("Supprimer")
            delete_btn.setStyleSheet("background-color: #A94442;")
            delete_btn.clicked.connect(lambda _, r=row: self.remove_subtitle_track(r))

            actions_layout.addWidget(delete_btn)

            # Widget container pour le layout des actions
            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            self.subtitle_table.setCellWidget(row, 6, actions_widget)

    def update_audio_lang(self, row, combo_index):
        """Met à jour la langue d'une piste audio"""
        combo = self.audio_table.cellWidget(row, 2)
        lang_code = combo.itemData(combo_index)

        if self.audio_tracks[row]["language"] != lang_code:
            self.audio_tracks[row]["language"] = lang_code
            self.audio_tracks[row]["modified"] = True
            self.modified = True
            self.save_audio_btn.setEnabled(True)
            self.apply_all_btn.setEnabled(True)  # Activer le bouton global
            logger.debug(f"Langue de la piste audio {row+1} modifiée à {lang_code}")

    def update_audio_title(self, row, title):
        """Met à jour le titre d'une piste audio"""
        if self.audio_tracks[row]["title"] != title:
            self.audio_tracks[row]["title"] = title
            self.audio_tracks[row]["modified"] = True
            self.modified = True
            self.save_audio_btn.setEnabled(True)
            self.apply_all_btn.setEnabled(True)  # Activer le bouton global
            logger.debug(f"Titre de la piste audio {row+1} modifié à '{title}'")

    def remove_audio_track(self, row):
        """Marque une piste audio pour suppression"""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Êtes-vous sûr de vouloir supprimer la piste audio {row+1} ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # Supprimer la piste du tableau et de la liste
            self.audio_tracks.pop(row)
            self.update_audio_table()
            self.modified = True
            self.save_audio_btn.setEnabled(True)
            self.apply_all_btn.setEnabled(True)  # Activer le bouton global
            logger.debug(f"Piste audio {row+1} supprimée")

    def update_subtitle_lang(self, row, combo_index):
        """Met à jour la langue d'une piste de sous-titres"""
        combo = self.subtitle_table.cellWidget(row, 2)
        lang_code = combo.itemData(combo_index)

        if self.subtitle_tracks[row]["language"] != lang_code:
            self.subtitle_tracks[row]["language"] = lang_code
            self.subtitle_tracks[row]["modified"] = True
            self.modified = True
            self.save_subtitle_btn.setEnabled(True)
            self.apply_all_btn.setEnabled(True)  # Activer le bouton global
            logger.debug(f"Langue du sous-titre {row+1} modifiée à {lang_code}")

    def update_subtitle_title(self, row, title):
        """Met à jour le titre d'une piste de sous-titres"""
        if self.subtitle_tracks[row]["title"] != title:
            self.subtitle_tracks[row]["title"] = title
            self.subtitle_tracks[row]["modified"] = True
            self.modified = True
            self.save_subtitle_btn.setEnabled(True)
            self.apply_all_btn.setEnabled(True)  # Activer le bouton global
            logger.debug(f"Titre du sous-titre {row+1} modifié à '{title}'")

    def update_subtitle_forced(self, row, state):
        """Met à jour l'état 'forcé' d'une piste de sous-titres"""
        forced = state == Qt.Checked

        if self.subtitle_tracks[row]["forced"] != forced:
            self.subtitle_tracks[row]["forced"] = forced
            self.subtitle_tracks[row]["modified"] = True
            self.modified = True
            self.save_subtitle_btn.setEnabled(True)
            self.apply_all_btn.setEnabled(True)  # Activer le bouton global
            logger.debug(f"État forcé du sous-titre {row+1} modifié à {forced}")

    def update_subtitle_default(self, row, state):
        """Met à jour l'état 'par défaut' d'une piste de sous-titres"""
        default = state == Qt.Checked

        if self.subtitle_tracks[row]["default"] != default:
            self.subtitle_tracks[row]["default"] = default
            self.subtitle_tracks[row]["modified"] = True
            self.modified = True
            self.save_subtitle_btn.setEnabled(True)
            self.apply_all_btn.setEnabled(True)  # Activer le bouton global
            logger.debug(f"État par défaut du sous-titre {row+1} modifié à {default}")

    def remove_subtitle_track(self, row):
        """Marque une piste de sous-titres pour suppression"""
        reply = QMessageBox.question(
            self,
            "Confirmation",
            f"Êtes-vous sûr de vouloir supprimer la piste de sous-titres {row+1} ?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            # Supprimer la piste du tableau et de la liste
            self.subtitle_tracks.pop(row)
            self.update_subtitle_table()
            self.modified = True
            self.save_subtitle_btn.setEnabled(True)
            self.apply_all_btn.setEnabled(True)  # Activer le bouton global
            logger.debug(f"Piste de sous-titres {row+1} supprimée")

    def apply_changes(self, track_type):
        """Applique les changements aux pistes"""
        if track_type == "audio" and not self.audio_tracks:
            QMessageBox.warning(self, "Avertissement", "Aucune piste audio à modifier.")
            return

        if track_type == "subtitle" and not self.subtitle_tracks:
            QMessageBox.warning(
                self, "Avertissement", "Aucune piste de sous-titres à modifier."
            )
            return

        # Vérifier si ffmpeg existe
        if not os.path.exists(FFMPEG_PATH):
            logger.error(f"ffmpeg introuvable à l'emplacement: {FFMPEG_PATH}")
            QMessageBox.critical(
                self,
                "Erreur",
                f"ffmpeg introuvable à l'emplacement: {FFMPEG_PATH}\nVérifiez que ffmpeg.exe est présent dans le dossier bin.",
            )
            return

        # Variable pour la boîte de dialogue de progression
        progress_dialog = None

        try:
            # Créer un fichier temporaire pour la sortie
            output_dir = os.path.dirname(self.filepath)
            base_name = os.path.splitext(os.path.basename(self.filepath))[0]
            temp_output = os.path.join(output_dir, f"{base_name}_edited.mkv")

            # Vérifier si le fichier de sortie existe déjà
            if os.path.exists(temp_output):
                reply = QMessageBox.question(
                    self,
                    "Fichier existant",
                    f"Le fichier {os.path.basename(temp_output)} existe déjà. Voulez-vous le remplacer ?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )

                if reply == QMessageBox.No:
                    return

            # Construire la commande ffmpeg
            cmd = [FFMPEG_PATH, "-i", self.filepath]

            # Ajouter les options de mappage
            map_options = []
            metadata_options = []

            if track_type == "audio":
                # Cartographier toutes les pistes vidéo
                cmd.extend(["-map", "0:v"])

                # Cartographier les pistes audio restantes avec leurs métadonnées
                for i, track in enumerate(self.audio_tracks):
                    stream_index = track["stream_index"]
                    cmd.extend(["-map", f"0:{stream_index}"])

                    # Ajouter les métadonnées modifiées
                    if track.get("modified", False):
                        metadata_options.extend(
                            [
                                f"-metadata:s:a:{i}",
                                f"language={track['language']}",
                                f"-metadata:s:a:{i}",
                                f"title={track['title']}",
                            ]
                        )

                # Cartographier toutes les pistes de sous-titres
                cmd.extend(
                    ["-map", "0:s?"]
                )  # Le ? rend la présence de sous-titres optionnelle

            elif track_type == "subtitle":
                # Cartographier toutes les pistes vidéo et audio
                cmd.extend(["-map", "0:v", "-map", "0:a"])

                # Cartographier les pistes de sous-titres restantes avec leurs métadonnées
                for i, track in enumerate(self.subtitle_tracks):
                    stream_index = track["stream_index"]
                    cmd.extend(["-map", f"0:{stream_index}"])

                    # Ajouter les métadonnées modifiées
                    if track.get("modified", False):
                        metadata_options.extend(
                            [
                                f"-metadata:s:s:{i}",
                                f"language={track['language']}",
                                f"-metadata:s:s:{i}",
                                f"title={track['title']}",
                            ]
                        )

                        # Disposition (forcé/défaut)
                        disposition = []
                        if track["forced"]:
                            disposition.append("forced")
                        if track["default"]:
                            disposition.append("default")

                        if disposition:
                            cmd.extend([f"-disposition:s:{i}", "+".join(disposition)])

            # Ajouter les options de métadonnées
            cmd.extend(metadata_options)

            # Ajouter les options de copie des codecs et le chemin de sortie
            cmd.extend(["-c", "copy", temp_output])

            # Afficher la commande
            cmd_str = " ".join(cmd)
            logger.debug(f"Commande ffmpeg: {cmd_str}")

            # Créer une boîte de dialogue de progression avec un bouton d'annulation
            progress_dialog = QMessageBox(self)
            progress_dialog.setWindowTitle("Traitement en cours")
            progress_dialog.setText(
                f"Modification des pistes {track_type}...\nMerci de patienter."
            )
            progress_dialog.setStandardButtons(QMessageBox.Cancel)
            progress_dialog.setModal(True)

            # Connexion du bouton d'annulation à une fonction qui termine le processus
            cancel_button = progress_dialog.button(QMessageBox.Cancel)
            cancel_button.setText("Annuler")
            process = None  # Variable pour stocker la référence au processus

            def cancel_process():
                nonlocal process
                if process:
                    try:
                        process.terminate()
                        logger.info("Processus ffmpeg annulé par l'utilisateur")
                    except:
                        logger.error("Impossible de terminer le processus ffmpeg")
                progress_dialog.reject()

            cancel_button.clicked.disconnect()  # Déconnecte les connexions existantes
            cancel_button.clicked.connect(cancel_process)

            # Montrer la boîte de dialogue sans bloquer
            progress_dialog.show()
            QApplication.processEvents()

            # Exécuter la commande ffmpeg
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )

            # Attendre que le processus se termine
            stdout, stderr = process.communicate()

            # Fermer la boîte de dialogue de progression
            if progress_dialog and progress_dialog.isVisible():
                progress_dialog.close()
                progress_dialog = None

            # Vérifier si le processus a réussi
            if process.returncode != 0:
                # Tronquer stderr s'il est trop long
                if len(stderr) > 1000:
                    stderr = stderr[:500] + "\n...\n" + stderr[-500:]

                logger.error(f"Erreur ffmpeg: {stderr}")
                error_dialog = QMessageBox(self)
                error_dialog.setWindowTitle("Erreur")
                error_dialog.setText("Erreur lors de la modification des pistes")
                error_dialog.setDetailedText(stderr)
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setStandardButtons(QMessageBox.Ok)
                error_dialog.exec_()
                return

            # Nouvelle boîte de dialogue personnalisée avec des boutons plus larges pour les options de sauvegarde
            replace_dialog = QDialog(self)
            replace_dialog.setWindowTitle("Modifications réussies")
            replace_dialog.setMinimumWidth(
                400
            )  # Largeur minimale pour la boîte de dialogue

            layout = QVBoxLayout(replace_dialog)

            # Message principal
            message_label = QLabel("Les modifications ont été appliquées avec succès.")
            message_label.setStyleSheet("font-weight: bold;")
            layout.addWidget(message_label)

            # Message secondaire
            question_label = QLabel("Que souhaitez-vous faire ?")
            layout.addWidget(question_label)

            # Boutons avec une taille minimale
            buttons_layout = QVBoxLayout()

            replace_btn = QPushButton("Remplacer l'original")
            replace_btn.setMinimumWidth(250)  # Largeur minimale du bouton
            replace_btn.setMinimumHeight(40)  # Hauteur minimale du bouton

            backup_btn = QPushButton("Remplacer avec sauvegarde")
            backup_btn.setMinimumWidth(250)
            backup_btn.setMinimumHeight(40)

            keep_btn = QPushButton("Garder les deux fichiers")
            keep_btn.setMinimumWidth(250)
            keep_btn.setMinimumHeight(40)
            keep_btn.setDefault(True)  # Option par défaut

            buttons_layout.addWidget(replace_btn)
            buttons_layout.addWidget(backup_btn)
            buttons_layout.addWidget(keep_btn)

            layout.addLayout(buttons_layout)

            # Connecter les boutons à leurs actions
            option_selected = {"choice": None}

            def on_replace_clicked():
                option_selected["choice"] = "replace"
                replace_dialog.accept()

            def on_backup_clicked():
                option_selected["choice"] = "backup"
                replace_dialog.accept()

            def on_keep_clicked():
                option_selected["choice"] = "keep"
                replace_dialog.accept()

            replace_btn.clicked.connect(on_replace_clicked)
            backup_btn.clicked.connect(on_backup_clicked)
            keep_btn.clicked.connect(on_keep_clicked)

            # Afficher la boîte de dialogue et attendre la sélection
            replace_dialog.exec_()

            # Traiter en fonction du choix de l'utilisateur
            final_path = ""

            if option_selected["choice"] == "replace":
                # Remplacer sans backup
                try:
                    os.remove(self.filepath)
                    os.rename(temp_output, self.filepath)
                    QMessageBox.information(
                        self,
                        "Succès",
                        f"Le fichier original a été remplacé sans sauvegarde.",
                    )
                    final_path = self.filepath
                except Exception as e:
                    logger.error(f"Erreur lors du remplacement du fichier: {e}")
                    QMessageBox.critical(
                        self, "Erreur", f"Erreur lors du remplacement du fichier: {e}"
                    )
                    return

            elif option_selected["choice"] == "backup":
                # Remplacer avec backup
                backup_file = f"{self.filepath}.bak"
                try:
                    # Supprimer un ancien backup s'il existe
                    if os.path.exists(backup_file):
                        os.remove(backup_file)

                    os.rename(self.filepath, backup_file)
                    os.rename(temp_output, self.filepath)
                    QMessageBox.information(
                        self,
                        "Succès",
                        f"Le fichier original a été remplacé. Une sauvegarde a été créée: {os.path.basename(backup_file)}",
                    )
                    final_path = self.filepath
                except Exception as e:
                    logger.error(
                        f"Erreur lors de la sauvegarde et du remplacement: {e}"
                    )
                    QMessageBox.critical(
                        self,
                        "Erreur",
                        f"Erreur lors de la sauvegarde et du remplacement: {e}",
                    )
                    return

            elif option_selected["choice"] == "keep":
                # Garder les deux fichiers
                QMessageBox.information(
                    self,
                    "Succès",
                    f"Les modifications ont été enregistrées dans un nouveau fichier: {os.path.basename(temp_output)}",
                )
                final_path = temp_output
            else:
                # Si l'utilisateur a fermé la boîte de dialogue sans faire de choix
                # Considérer comme "garder les deux fichiers" par défaut
                QMessageBox.information(
                    self,
                    "Succès",
                    f"Les modifications ont été enregistrées dans un nouveau fichier: {os.path.basename(temp_output)}",
                )
                final_path = temp_output

            # Nouvelle boîte de dialogue avec liste déroulante pour choisir un preset
            if final_path:
                queue_dialog = QDialog(self)
                queue_dialog.setWindowTitle("Ajouter à la file d'attente")
                queue_dialog.setMinimumWidth(400)

                queue_layout = QVBoxLayout(queue_dialog)

                # Message
                queue_label = QLabel(
                    "Souhaitez-vous ajouter le fichier modifié à la file d'attente d'encodage ?"
                )
                queue_label.setWordWrap(True)
                queue_layout.addWidget(queue_label)

                # Groupe pour contenir la liste et le bouton
                option_layout = QHBoxLayout()

                # Liste déroulante des presets
                preset_combo = QComboBox()
                preset_combo.setMinimumHeight(30)
                for preset in dossiers_presets.values():
                    preset_combo.addItem(preset)
                option_layout.addWidget(preset_combo, 1)  # 1 = stretch factor

                # Bouton Ajouter
                add_btn = QPushButton("Ajouter")
                add_btn.setMinimumHeight(30)
                option_layout.addWidget(add_btn)

                queue_layout.addLayout(option_layout)

                # Bouton pour fermer sans ajouter
                cancel_btn = QPushButton("Ne pas ajouter")
                cancel_btn.setMinimumHeight(40)
                queue_layout.addWidget(cancel_btn)

                # Variable pour stocker le choix de l'utilisateur
                queue_choice = {"add": False, "preset": ""}

                # Connecter les boutons
                def on_add_clicked():
                    queue_choice["add"] = True
                    queue_choice["preset"] = preset_combo.currentText()
                    queue_dialog.accept()

                def on_cancel_clicked():
                    queue_choice["add"] = False
                    queue_dialog.reject()

                add_btn.clicked.connect(on_add_clicked)
                cancel_btn.clicked.connect(on_cancel_clicked)

                # Afficher la boîte de dialogue
                queue_dialog.exec_()

                # Si l'utilisateur a choisi d'ajouter à la file d'attente
                if queue_choice["add"] and queue_choice["preset"]:
                    selected_preset = queue_choice["preset"]

                    # Vérifier si la fenêtre parente est la MainWindow
                    if hasattr(self.parent(), "control_flags"):
                        # Récupérer la liste actuelle des fichiers en attente
                        current_queue = []

                        if hasattr(self.parent(), "get_current_queue_files"):
                            current_queue = self.parent().get_current_queue_files()

                        # Ajouter le fichier à la file d'attente
                        new_item = {"file": final_path, "preset": selected_preset}
                        current_queue.append(new_item)

                        # Mettre à jour la file d'attente
                        if hasattr(self.parent(), "update_queue"):
                            self.parent().update_queue(current_queue)

                        # Signaler le changement
                        self.parent().control_flags["queue_modified"] = True

                        # Forcer la mise à jour immédiate
                        try:
                            from state_persistence import save_interrupted_encodings

                            save_interrupted_encodings(None, current_queue)
                            logger.info(
                                f"Fichier ajouté à la file d'attente avec le preset {selected_preset}"
                            )
                        except Exception as e:
                            logger.error(
                                f"Erreur lors de l'ajout à la file d'attente: {e}"
                            )

                    QMessageBox.information(
                        self,
                        "File d'attente",
                        f"Le fichier a été ajouté à la file d'attente avec le preset {selected_preset}",
                    )

            # Recharger les informations des pistes
            self.load_track_info()

            # Réinitialiser l'état modifié
            self.modified = False
            self.save_audio_btn.setEnabled(False)
            self.save_subtitle_btn.setEnabled(False)

            logger.info(f"Modifications appliquées avec succès pour {track_type}")

        except Exception as e:
            logger.error(f"Erreur lors de l'application des modifications: {str(e)}")

            # S'assurer que la boîte de dialogue de progression est fermée
            if progress_dialog and progress_dialog.isVisible():
                progress_dialog.close()

            # Afficher l'erreur
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de l'application des modifications:\n{str(e)}",
            )

    def apply_all_changes(self):
        """Applique toutes les modifications (audio et sous-titres) en une seule fois"""
        # Vérifier s'il y a des modifications à appliquer
        audio_modified = any(
            track.get("modified", False) for track in self.audio_tracks
        )
        subtitle_modified = any(
            track.get("modified", False) for track in self.subtitle_tracks
        )

        if not audio_modified and not subtitle_modified:
            QMessageBox.information(
                self,
                "Information",
                "Aucune modification à appliquer.",
            )
            return

        # Créer un fichier temporaire pour la sortie
        output_dir = os.path.dirname(self.filepath)
        base_name = os.path.splitext(os.path.basename(self.filepath))[0]
        temp_output = os.path.join(output_dir, f"{base_name}_edited.mkv")

        # Vérifier si le fichier de sortie existe déjà
        if os.path.exists(temp_output):
            reply = QMessageBox.question(
                self,
                "Fichier existant",
                f"Le fichier {os.path.basename(temp_output)} existe déjà. Voulez-vous le remplacer ?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply == QMessageBox.No:
                return

        # Vérifier si ffmpeg existe
        if not os.path.exists(FFMPEG_PATH):
            logger.error(f"ffmpeg introuvable à l'emplacement: {FFMPEG_PATH}")
            QMessageBox.critical(
                self,
                "Erreur",
                f"ffmpeg introuvable à l'emplacement: {FFMPEG_PATH}\nVérifiez que ffmpeg.exe est présent dans le dossier bin.",
            )
            return

        # Variable pour la boîte de dialogue de progression
        progress_dialog = None

        try:
            # Construire la commande ffmpeg
            cmd = [FFMPEG_PATH, "-i", self.filepath]

            # Ajouter les options de mappage
            cmd.extend(["-map", "0:v"])  # Cartographier toutes les pistes vidéo

            # Cartographier et configurer les pistes audio avec leurs métadonnées
            for i, track in enumerate(self.audio_tracks):
                stream_index = track["stream_index"]
                cmd.extend(["-map", f"0:{stream_index}"])

                # Ajouter les métadonnées modifiées
                if track.get("modified", False):
                    cmd.extend(
                        [
                            f"-metadata:s:a:{i}",
                            f"language={track['language']}",
                            f"-metadata:s:a:{i}",
                            f"title={track['title']}",
                        ]
                    )

            # Cartographier et configurer les pistes de sous-titres
            for i, track in enumerate(self.subtitle_tracks):
                stream_index = track["stream_index"]
                cmd.extend(["-map", f"0:{stream_index}"])

                # Ajouter les métadonnées modifiées
                if track.get("modified", False):
                    cmd.extend(
                        [
                            f"-metadata:s:s:{i}",
                            f"language={track['language']}",
                            f"-metadata:s:s:{i}",
                            f"title={track['title']}",
                        ]
                    )

                    # Disposition (forcé/défaut)
                    disposition = []
                    if track["forced"]:
                        disposition.append("forced")
                    if track["default"]:
                        disposition.append("default")

                    if disposition:
                        cmd.extend([f"-disposition:s:{i}", "+".join(disposition)])

            # Ajouter les options de copie des codecs et le chemin de sortie
            cmd.extend(["-c", "copy", temp_output])

            # Afficher la commande
            cmd_str = " ".join(cmd)
            logger.debug(f"Commande ffmpeg: {cmd_str}")

            # Créer une boîte de dialogue de progression avec un bouton d'annulation
            progress_dialog = QMessageBox(self)
            progress_dialog.setWindowTitle("Traitement en cours")
            progress_dialog.setText(
                "Application de toutes les modifications...\nMerci de patienter."
            )
            progress_dialog.setStandardButtons(QMessageBox.Cancel)
            progress_dialog.setModal(True)

            # Connexion du bouton d'annulation à une fonction qui termine le processus
            cancel_button = progress_dialog.button(QMessageBox.Cancel)
            cancel_button.setText("Annuler")
            process = None  # Variable pour stocker la référence au processus

            def cancel_process():
                nonlocal process
                if process:
                    try:
                        process.terminate()
                        logger.info("Processus ffmpeg annulé par l'utilisateur")
                    except:
                        logger.error("Impossible de terminer le processus ffmpeg")
                progress_dialog.reject()

            cancel_button.clicked.disconnect()  # Déconnecte les connexions existantes
            cancel_button.clicked.connect(cancel_process)

            # Montrer la boîte de dialogue sans bloquer
            progress_dialog.show()
            QApplication.processEvents()

            # Exécuter la commande ffmpeg
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )

            # Attendre que le processus se termine
            stdout, stderr = process.communicate()

            # Fermer la boîte de dialogue de progression
            if progress_dialog and progress_dialog.isVisible():
                progress_dialog.close()
                progress_dialog = None

            # Vérifier si le processus a réussi
            if process.returncode != 0:
                # Tronquer stderr s'il est trop long
                if len(stderr) > 1000:
                    stderr = stderr[:500] + "\n...\n" + stderr[-500:]

                logger.error(f"Erreur ffmpeg: {stderr}")
                error_dialog = QMessageBox(self)
                error_dialog.setWindowTitle("Erreur")
                error_dialog.setText("Erreur lors de la modification des pistes")
                error_dialog.setDetailedText(stderr)
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setStandardButtons(QMessageBox.Ok)
                error_dialog.exec_()
                return

            # Nouvelle boîte de dialogue pour les options de sauvegarde
            replace_dialog = QDialog(self)
            replace_dialog.setWindowTitle("Modifications réussies")
            replace_dialog.setMinimumWidth(
                400
            )  # Largeur minimale pour la boîte de dialogue

            layout = QVBoxLayout(replace_dialog)

            # Message principal
            message_label = QLabel(
                "Toutes les modifications ont été appliquées avec succès."
            )
            message_label.setStyleSheet("font-weight: bold;")
            layout.addWidget(message_label)

            # Message secondaire
            question_label = QLabel("Que souhaitez-vous faire ?")
            layout.addWidget(question_label)

            # Boutons avec une taille minimale
            buttons_layout = QVBoxLayout()

            replace_btn = QPushButton("Remplacer l'original")
            replace_btn.setMinimumWidth(250)  # Largeur minimale du bouton
            replace_btn.setMinimumHeight(40)  # Hauteur minimale du bouton

            backup_btn = QPushButton("Remplacer avec sauvegarde")
            backup_btn.setMinimumWidth(250)
            backup_btn.setMinimumHeight(40)

            keep_btn = QPushButton("Garder les deux fichiers")
            keep_btn.setMinimumWidth(250)
            keep_btn.setMinimumHeight(40)
            keep_btn.setDefault(True)  # Option par défaut

            buttons_layout.addWidget(replace_btn)
            buttons_layout.addWidget(backup_btn)
            buttons_layout.addWidget(keep_btn)

            layout.addLayout(buttons_layout)

            # Connecter les boutons à leurs actions
            option_selected = {"choice": None}

            def on_replace_clicked():
                option_selected["choice"] = "replace"
                replace_dialog.accept()

            def on_backup_clicked():
                option_selected["choice"] = "backup"
                replace_dialog.accept()

            def on_keep_clicked():
                option_selected["choice"] = "keep"
                replace_dialog.accept()

            replace_btn.clicked.connect(on_replace_clicked)
            backup_btn.clicked.connect(on_backup_clicked)
            keep_btn.clicked.connect(on_keep_clicked)

            # Afficher la boîte de dialogue et attendre la sélection
            replace_dialog.exec_()

            # Traiter en fonction du choix de l'utilisateur
            final_path = ""

            if option_selected["choice"] == "replace":
                # Remplacer sans backup
                try:
                    os.remove(self.filepath)
                    os.rename(temp_output, self.filepath)
                    QMessageBox.information(
                        self,
                        "Succès",
                        f"Le fichier original a été remplacé sans sauvegarde.",
                    )
                    final_path = self.filepath
                except Exception as e:
                    logger.error(f"Erreur lors du remplacement du fichier: {e}")
                    QMessageBox.critical(
                        self, "Erreur", f"Erreur lors du remplacement du fichier: {e}"
                    )
                    return

            elif option_selected["choice"] == "backup":
                # Remplacer avec backup
                backup_file = f"{self.filepath}.bak"
                try:
                    # Supprimer un ancien backup s'il existe
                    if os.path.exists(backup_file):
                        os.remove(backup_file)

                    os.rename(self.filepath, backup_file)
                    os.rename(temp_output, self.filepath)
                    QMessageBox.information(
                        self,
                        "Succès",
                        f"Le fichier original a été remplacé. Une sauvegarde a été créée: {os.path.basename(backup_file)}",
                    )
                    final_path = self.filepath
                except Exception as e:
                    logger.error(
                        f"Erreur lors de la sauvegarde et du remplacement: {e}"
                    )
                    QMessageBox.critical(
                        self,
                        "Erreur",
                        f"Erreur lors de la sauvegarde et du remplacement: {e}",
                    )
                    return

            elif option_selected["choice"] == "keep":
                # Garder les deux fichiers
                QMessageBox.information(
                    self,
                    "Succès",
                    f"Les modifications ont été enregistrées dans un nouveau fichier: {os.path.basename(temp_output)}",
                )
                final_path = temp_output
            else:
                # Si l'utilisateur a fermé la boîte de dialogue sans faire de choix
                # Considérer comme "garder les deux fichiers" par défaut
                QMessageBox.information(
                    self,
                    "Succès",
                    f"Les modifications ont été enregistrées dans un nouveau fichier: {os.path.basename(temp_output)}",
                )
                final_path = temp_output

            # Proposer d'ajouter le fichier à la file d'attente d'encodage
            queue_dialog = QDialog(self)
            queue_dialog.setWindowTitle("Ajouter à la file d'attente")
            queue_dialog.setMinimumWidth(400)

            queue_layout = QVBoxLayout(queue_dialog)

            # Message
            queue_label = QLabel(
                "Souhaitez-vous ajouter le fichier modifié à la file d'attente d'encodage ?"
            )
            queue_label.setWordWrap(True)
            queue_layout.addWidget(queue_label)

            # Groupe pour contenir la liste et le bouton
            option_layout = QHBoxLayout()

            # Liste déroulante des presets
            preset_combo = QComboBox()
            preset_combo.setMinimumHeight(30)
            for preset in dossiers_presets.values():
                preset_combo.addItem(preset)
            option_layout.addWidget(preset_combo, 1)  # 1 = stretch factor

            # Bouton Ajouter
            add_btn = QPushButton("Ajouter")
            add_btn.setMinimumHeight(30)
            option_layout.addWidget(add_btn)

            queue_layout.addLayout(option_layout)

            # Bouton pour fermer sans ajouter
            cancel_btn = QPushButton("Ne pas ajouter")
            cancel_btn.setMinimumHeight(40)
            queue_layout.addWidget(cancel_btn)

            # Variable pour stocker le choix de l'utilisateur
            queue_choice = {"add": False, "preset": ""}

            # Connecter les boutons
            def on_add_clicked():
                queue_choice["add"] = True
                queue_choice["preset"] = preset_combo.currentText()
                queue_dialog.accept()

            def on_cancel_clicked():
                queue_choice["add"] = False
                queue_dialog.reject()

            add_btn.clicked.connect(on_add_clicked)
            cancel_btn.clicked.connect(on_cancel_clicked)

            # Afficher la boîte de dialogue
            queue_dialog.exec_()

            # Si l'utilisateur a choisi d'ajouter à la file d'attente
            if queue_choice["add"] and queue_choice["preset"]:
                selected_preset = queue_choice["preset"]

                # Vérifier si la fenêtre parente est la MainWindow
                if hasattr(self.parent(), "control_flags"):
                    # Récupérer la liste actuelle des fichiers en attente
                    current_queue = []

                    if hasattr(self.parent(), "get_current_queue_files"):
                        current_queue = self.parent().get_current_queue_files()

                    # Ajouter le fichier à la file d'attente
                    new_item = {"file": final_path, "preset": selected_preset}
                    current_queue.append(new_item)

                    # Mettre à jour la file d'attente
                    if hasattr(self.parent(), "update_queue"):
                        self.parent().update_queue(current_queue)

                    # Signaler le changement
                    self.parent().control_flags["queue_modified"] = True

                    # Forcer la mise à jour immédiate
                    try:
                        from state_persistence import save_interrupted_encodings

                        save_interrupted_encodings(None, current_queue)
                        logger.info(
                            f"Fichier ajouté à la file d'attente avec le preset {selected_preset}"
                        )
                    except Exception as e:
                        logger.error(f"Erreur lors de l'ajout à la file d'attente: {e}")

                QMessageBox.information(
                    self,
                    "File d'attente",
                    f"Le fichier a été ajouté à la file d'attente avec le preset {selected_preset}",
                )

            # Recharger les informations des pistes
            self.load_track_info()

            # Réinitialiser l'état modifié
            self.modified = False
            self.save_audio_btn.setEnabled(False)
            self.save_subtitle_btn.setEnabled(False)
            self.apply_all_btn.setEnabled(False)  # Désactiver le bouton global

            logger.info(f"Toutes les modifications ont été appliquées avec succès")

        except Exception as e:
            logger.error(f"Erreur lors de l'application des modifications: {str(e)}")

            # S'assurer que la boîte de dialogue de progression est fermée
            if progress_dialog and progress_dialog.isVisible():
                progress_dialog.close()

            # Afficher l'erreur
            QMessageBox.critical(
                self,
                "Erreur",
                f"Erreur lors de l'application des modifications:\n{str(e)}",
            )

    def close_with_check(self):
        """Vérifie s'il y a des modifications non sauvegardées avant de fermer"""
        if self.modified:
            reply = QMessageBox.question(
                self,
                "Modifications non sauvegardées",
                "Vous avez des modifications non sauvegardées. Êtes-vous sûr de vouloir fermer ?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )

            if reply == QMessageBox.No:
                return

        self.close()


if __name__ == "__main__":
    # Pour les tests directs
    app = QApplication(sys.argv)
    # Vérifier les arguments de ligne de commande
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
        if os.path.exists(filepath):
            dialog = TrackEditorDialog(filepath)
            dialog.exec_()
        else:
            print(f"Le fichier {filepath} n'existe pas")
    else:
        print("Usage: python track_editor.py <chemin_du_fichier>")
    sys.exit()
