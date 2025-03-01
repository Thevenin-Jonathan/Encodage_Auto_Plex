import os
from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon


class RestartEncodingDialog(QDialog):
    """
    Boîte de dialogue qui s'affiche au démarrage si un encodage a été interrompu.
    Demande à l'utilisateur s'il souhaite recommencer l'encodage ou l'ignorer.
    """

    def __init__(self, state, parent=None):
        super().__init__(parent)
        self.state = state
        self.setWindowTitle("Encodage interrompu détecté")
        self.setMinimumWidth(500)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        # Créer le layout principal
        layout = QVBoxLayout(self)

        # Titre
        title_label = QLabel("Encodage interrompu détecté")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # Message d'information
        info_label = QLabel(
            "L'application a été fermée ou a planté alors qu'un encodage était en cours. "
            "Voulez-vous recommencer l'encodage interrompu et la file d'attente depuis le début, "
            "ou ignorer ces encodages ?"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Cadre pour les détails de l'encodage
        details_frame = QFrame()
        details_frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        details_layout = QVBoxLayout(details_frame)

        # Informations sur l'encodage en cours
        current_encoding = state.get("current_encoding")
        if current_encoding:
            file_path = current_encoding.get("file", "")
            file_name = os.path.basename(file_path) if file_path else "Inconnu"
            preset = current_encoding.get("preset", "Inconnu")

            current_label = QLabel(f"<b>Fichier interrompu:</b> {file_name}")
            preset_label = QLabel(f"<b>Preset:</b> {preset}")

            details_layout.addWidget(current_label)
            details_layout.addWidget(preset_label)

        # Informations sur la file d'attente
        queue = state.get("encoding_queue", [])
        queue_count = len(queue)
        queue_label = QLabel(f"<b>Fichiers en attente:</b> {queue_count}")
        details_layout.addWidget(queue_label)

        # Ajouter le cadre de détails au layout principal
        layout.addWidget(details_frame)

        # Boutons
        buttons_layout = QHBoxLayout()

        self.restart_button = QPushButton("Recommencer")
        self.restart_button.setStyleSheet("background-color: #4dabf7;")
        self.restart_button.clicked.connect(self.accept)

        self.ignore_button = QPushButton("Annuler et ignorer")
        self.ignore_button.clicked.connect(self.reject)

        buttons_layout.addWidget(self.restart_button)
        buttons_layout.addWidget(self.ignore_button)

        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    @staticmethod
    def show_dialog(state, parent=None):
        """
        Affiche la boîte de dialogue et retourne True si l'utilisateur choisit de recommencer l'encodage,
        False s'il choisit de l'ignorer.

        Args:
            state (dict): État des encodages interrompus
            parent (QWidget, optional): Widget parent

        Returns:
            bool: True si l'utilisateur choisit de recommencer, False sinon
        """
        dialog = RestartEncodingDialog(state, parent)
        result = dialog.exec_()
        return result == QDialog.Accepted
