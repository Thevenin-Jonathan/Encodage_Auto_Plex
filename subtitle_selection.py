from constants import (
    criteres_sous_titres_burn,
    criteres_sous_titres_supprimer,
)
from utils import horodatage, enlever_accents


def selectionner_sous_titres(info_pistes, preset):
    """
    Sélectionne les sous-titres à inclure et détermine s'il y a un sous-titre à incruster (burn-in)
    en fonction des informations des pistes et du preset spécifié.

    Arguments:
    info_pistes -- Dictionnaire contenant les informations de sous-titres.
    preset -- Chaîne de caractères représentant le preset utilisé pour l'encodage.

    Retourne:
    Une liste des numéros de pistes des sous-titres sélectionnés et le numéro de la piste
    du sous-titre à incruster (ou None si aucun).
    """
    sous_titres_selectionnes = []  # Liste des sous-titres à inclure dans la vidéo
    sous_titres_burn = None  # Sous-titre à incruster (burn-in)

    def add_sous_titre(sous_titre):
        """
        Ajoute un sous-titre à la liste des sous-titres sélectionnés et détermine
        s'il doit être incrusté en fonction de critères spécifiques.

        Arguments:
        sous_titre -- Dictionnaire contenant les informations du sous-titre.
        """
        nonlocal sous_titres_selectionnes, sous_titres_burn
        name_normalisee = enlever_accents(sous_titre.get("Name", ""))
        # Vérifier si le sous-titre correspond aux critères pour être incrusté
        if sous_titres_burn is None and any(
            critere in name_normalisee for critere in criteres_sous_titres_burn
        ):
            sous_titres_burn = sous_titre["TrackNumber"]
        # Ajouter le numéro de piste du sous-titre à la liste des sélectionnés
        sous_titres_selectionnes.append(sous_titre["TrackNumber"])

    # Traitement pour certains presets spécifiés
    if preset in [
        "Dessins animes FR 1000kbps",
        "1080p HD-Light 1500kbps",
        "Mangas MULTI 1000kbps",
    ]:
        # Parcourir les sous-titres du premier titre (assumant qu'il n'y en a qu'un)
        for sous_titre in info_pistes["TitleList"][0]["SubtitleList"]:
            # Garder uniquement les sous-titres en français
            if sous_titre.get("LanguageCode", "") == "fra":
                name_normalisee = enlever_accents(sous_titre.get("Name", ""))
                # Exclure les sous-titres qui contiennent des critères à supprimer
                if name_normalisee == "" or not any(
                    critere in name_normalisee
                    for critere in criteres_sous_titres_supprimer
                ):
                    add_sous_titre(sous_titre)

        # Vérification des conditions d'erreur
        if (sous_titres_burn is None and len(sous_titres_selectionnes) > 1) or (
            sous_titres_burn is not None and len(sous_titres_selectionnes) > 2
        ):
            # Trop de sous-titres à inclure, retourner une erreur
            print(f"{horodatage()} 🚫 Trop de sous-titres à inclure.")
            return None, None
        elif sous_titres_selectionnes == []:
            # Aucun sous-titre français trouvé, retourner une erreur
            print(f"{horodatage()} 🚫 Pas de sous-titres français disponibles.")
            return None, None

        # Retourner les sous-titres sélectionnés et le sous-titre à incruster
        return sous_titres_selectionnes, sous_titres_burn

    # Traitement spécifique pour le preset "Mangas VO 1000kbps"
    elif preset == "Mangas VO 1000kbps":
        # Parcourir les sous-titres du premier titre
        for sous_titre in info_pistes["TitleList"][0]["SubtitleList"]:
            # Garder uniquement les sous-titres en français
            if sous_titre.get("LanguageCode", "") == "fra":
                if sous_titres_burn is None:
                    # Définir le sous-titre à incruster
                    sous_titres_burn = sous_titre["TrackNumber"]
                    sous_titres_selectionnes.append(sous_titre["TrackNumber"])
                else:
                    # Si plus d'un sous-titre à incruster est présent, retourner une erreur
                    print(f"{horodatage()} 🚫 Trop de sous-titres à incruster.")
                    return None, None

        # Si un sous-titre français est présent, le retourner
        if sous_titres_burn is not None:
            return sous_titres_selectionnes, sous_titres_burn
        else:
            # Aucun sous-titre français trouvé, retourner une erreur
            print(f"{horodatage()} 🚫 Pas de sous-titres français disponibles.")
            return None, None
    else:
        # Si le preset ne correspond à aucun cas géré, retourner une erreur
        print(f"{horodatage()} 🚫 Preset non reconnu: {preset}")
        return None, None
