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
