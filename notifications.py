from plyer import notification
from constants import maxsize_message
from utils import horodatage
from config import load_config

# Variable globale pour l'état des notifications

config = load_config()
notifications_enabled = config["notifications_enabled"]


def set_notifications_enabled(enabled):
    """
    Active ou désactive les notifications Windows.

    Arguments:
    enabled -- True pour activer les notifications, False pour les désactiver
    """
    global notifications_enabled
    notifications_enabled = enabled


def notifier_encodage_lancement(fichier, file_encodage):
    """
    Envoie une notification de lancement d'encodage.

    Arguments:
    fichier -- Nom du fichier à encoder.
    file_encodage -- Queue pour la file d'attente d'encodage.
    """
    # Vérifier si les notifications sont activées
    if not notifications_enabled:
        return

    short_fichier = (
        fichier
        if len(fichier) <= maxsize_message
        else fichier[: maxsize_message - 3] + "..."
    )
    try:
        notification.notify(
            title="Encodage Lancement",
            message=f"L'encodage pour {short_fichier} a été lancé.\nFiles en attente: {file_encodage.qsize()}",
            app_name="Encoder App",
            timeout=5,
        )
    except Exception as e:
        # Ignorer les erreurs de notification pour ne pas bloquer l'encodage
        print(f"{horodatage()} ⚠️ Notification non disponible: {str(e)}")


def notifier_encodage_termine(fichier, file_encodage):
    """
    Envoie une notification de fin d'encodage.

    Arguments:
    fichier -- Nom du fichier encodé.
    file_encodage -- Queue pour la file d'attente d'encodage.
    """
    # Vérifier si les notifications sont activées
    if not notifications_enabled:
        return

    short_fichier = (
        fichier
        if len(fichier) <= maxsize_message
        else fichier[: maxsize_message - 3] + "..."
    )
    try:
        notification.notify(
            title="Encodage Terminé",
            message=f"L'encodage pour {short_fichier} est terminé.\nFiles en attente: {file_encodage.qsize()}",
            app_name="Encoder App",
            timeout=5,
        )
    except Exception as e:
        # Ignorer les erreurs de notification pour ne pas bloquer l'encodage
        print(f"{horodatage()} ⚠️ Notification non disponible: {str(e)}")


def notifier_erreur_encodage(fichier):
    """
    Envoie une notification d'erreur d'encodage.

    Arguments:
    fichier -- Nom du fichier pour lequel l'encodage a échoué.
    """
    # Vérifier si les notifications sont activées
    if not notifications_enabled:
        return

    short_fichier = (
        fichier
        if len(fichier) <= maxsize_message
        else fichier[: maxsize_message - 3] + "..."
    )
    try:
        notification.notify(
            title="Erreur d'Encodage",
            message=f"Une erreur est survenue lors de l'encodage de {short_fichier}.",
            app_name="Encoder App",
            timeout=5,
        )
    except Exception as e:
        # Ignorer les erreurs de notification pour ne pas bloquer l'encodage
        print(f"{horodatage()} ⚠️ Notification non disponible: {str(e)}")
