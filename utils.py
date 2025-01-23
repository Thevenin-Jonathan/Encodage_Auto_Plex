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
