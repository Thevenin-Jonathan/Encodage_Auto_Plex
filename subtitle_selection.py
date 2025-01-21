from constants import (
    horodatage,
    criteres_sous_titres_burn,
    criteres_sous_titres_supprimer,
    enlever_accents,
)

# Fonction pour sélectionner les sous-titres en fonction du preset


def selectionner_sous_titres(info_pistes, preset):
    sous_titres_selectionnes = []  # Liste des sous-titres à inclure dans la vidéo
    sous_titres_burn = None  # Sous-titre à incruster (burn)

    def add_sous_titre(sous_titre):
        nonlocal sous_titres_selectionnes, sous_titres_burn
        name_normalisee = enlever_accents(sous_titre.get("Name", ""))
        if sous_titres_burn is None and any(
            critere in name_normalisee for critere in criteres_sous_titres_burn
        ):
            sous_titres_burn = sous_titre["TrackNumber"]
        sous_titres_selectionnes.append(sous_titre["TrackNumber"])

    # Traitement pour les presets spécifiés
    if preset in [
        "Dessins animes FR 1000kbps",
        "1080p HD-Light 1500kbps",
        "Mangas MULTI 1000kbps",
    ]:
        for sous_titre in info_pistes["TitleList"][0]["SubtitleList"]:
            # Garder uniquement les sous-titres en français
            if sous_titre["LanguageCode"] == "fra":
                name_normalisee = enlever_accents(sous_titre.get("Name", ""))
                if name_normalisee == "" or not any(
                    critere in name_normalisee
                    for critere in criteres_sous_titres_supprimer
                ):
                    add_sous_titre(sous_titre)

        # Vérification des conditions d'erreur
        if (sous_titres_burn is None and len(sous_titres_selectionnes) > 1) or (
            sous_titres_burn is not None and len(sous_titres_selectionnes) > 2
        ):
            print(f"{horodatage()} 🚫 Trop de sous-titres à inclure.")
            return None, None

        return sous_titres_selectionnes, sous_titres_burn

    # Traitement spécifique pour le preset "Manga_VO"
    elif preset == "Mangas VO 1000kbps":
        for sous_titre in info_pistes["TitleList"][0]["SubtitleList"]:
            # Garder uniquement les sous-titres en français
            if sous_titre["LanguageCode"] == "fra":
                if sous_titres_burn is None:
                    sous_titres_burn = sous_titre["TrackNumber"]
                    sous_titres_selectionnes.append(sous_titre["TrackNumber"])
                else:
                    # Trop de sous-titres à incruster, retourner une erreur
                    print(f"{horodatage()} 🚫 Trop de sous-titres à incruster.")
                    return None, None

        # Si un sous-titre français est présent, l'incruster
        if sous_titres_burn is not None:
            return sous_titres_selectionnes, sous_titres_burn
        else:
            print(
                f"{horodatage()} 🚫 Pas de sous-titres français disponible pour manga VO."
            )
            return None, None
