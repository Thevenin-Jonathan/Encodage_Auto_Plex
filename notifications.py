from plyer import notification
from constants import maxsize_message
from utils import horodatage


def notifier_encodage_lancement(fichier, file_encodage):
    """
    Envoie une notification de lancement d'encodage.

    Arguments:
    fichier -- Nom du fichier à encoder.
    file_encodage -- Queue pour la file d'attente d'encodage.
    """
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
