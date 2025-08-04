import unicodedata
from datetime import datetime


def horodatage():
    """
    Retourne l'horodatage actuel sous forme de chaîne de caractères.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def enlever_accents(input_str):
    """
    Enlève les accents d'une chaîne de caractères et convertit en minuscules.
    """
    nfkd_form = unicodedata.normalize("NFKD", input_str.lower())
    return "".join([c for c in nfkd_form if not unicodedata.combining(c)])


def tronquer_nom_fichier(nom_fichier, debut=40, fin=20):
    """
    Tronque le nom du fichier pour conserver les 40 premiers caractères,
    ajouter "..." au milieu, puis conserver les 20 derniers caractères.

    Arguments:
    nom_fichier -- Le nom du fichier à tronquer.
    debut -- Le nombre de caractères à conserver au début (par défaut 40).
    fin -- Le nombre de caractères à conserver à la fin (par défaut 20).

    Retourne:
    Le nom de fichier tronqué.
    """
    nom_fichier = nom_fichier.strip()
    debut_part = nom_fichier[:debut].strip()
    fin_part = nom_fichier[-fin:].strip()
    if len(nom_fichier) <= debut + fin:
        return nom_fichier
    return f"{debut_part}...{fin_part}"


def obtenir_dossier_sortie_dossier_source(dossier_source):
    """
    Retourne le dossier de sortie correspondant à un dossier source surveillé.

    Arguments:
    dossier_source -- Le chemin du dossier source surveillé

    Retourne:
    Le chemin du dossier de sortie pour ce dossier source, ou le dossier par défaut si non trouvé
    """
    try:
        from config import get_output_directory_for_source_folder

        return get_output_directory_for_source_folder(dossier_source)
    except ImportError:
        # Fallback vers les constantes si le module config n'est pas disponible
        from constants import dossiers_sortie_surveillance, dossier_sortie

        return dossiers_sortie_surveillance.get(dossier_source, dossier_sortie)


def obtenir_dossier_sortie_preset(preset):
    """
    Retourne le dossier de sortie correspondant à un preset donné.

    Arguments:
    preset -- Le nom du preset

    Retourne:
    Le chemin du dossier de sortie pour ce preset, ou le dossier par défaut si non trouvé

    DEPRECATED: Utilisez obtenir_dossier_sortie_dossier_source() à la place
    """
    try:
        from config import get_output_directory_for_preset

        return get_output_directory_for_preset(preset)
    except ImportError:
        # Fallback vers les constantes si le module config n'est pas disponible
        from constants import dossier_sortie

        return dossier_sortie
