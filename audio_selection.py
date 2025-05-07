from utils import horodatage, enlever_accents
from constants import criteres_audios
import json
from logger import setup_logger

# Configuration du logger
logger = setup_logger(__name__)


def selectionner_pistes_audio(info_pistes, preset):
    """
    Sélectionne les pistes audio à inclure en fonction des informations des pistes et du preset spécifié.

    Arguments:
    info_pistes -- Dictionnaire contenant les informations des pistes audio.
    preset -- Chaîne de caractères représentant le preset utilisé pour l'encodage.

    Retourne:
    Une liste des numéros de pistes des pistes audio sélectionnées, ou None si aucune piste valide n'est trouvée.
    """
    pistes_audio_selectionnees = []

    # Log debug de l'analyse des pistes audio
    if "TitleList" not in info_pistes or not info_pistes["TitleList"]:
        logger.debug("Aucune liste de titres trouvée dans les informations des pistes")
        return None

    if "AudioList" not in info_pistes["TitleList"][0]:
        logger.debug("Aucune liste de pistes audio trouvée")
        return None

    # Affichage détaillé de chaque piste audio
    audio_tracks = info_pistes["TitleList"][0]["AudioList"]
    logger.debug(f"Nombre total de pistes audio détectées: {len(audio_tracks)}")

    for i, track in enumerate(audio_tracks):
        # Création d'un dictionnaire propre pour le log
        track_info = {
            "Position": i + 1,
            "TrackNumber": track.get("TrackNumber", "N/A"),
            "LanguageCode": track.get("LanguageCode", "N/A"),
            "Language": track.get("Language", "N/A"),
            "Name": track.get("Name", "N/A"),
            "Format": track.get("Format", "N/A"),
            "SampleRate": track.get("SampleRate", "N/A"),
            "BitRate": track.get("BitRate", "N/A"),
            "Channels": track.get("Channels", "N/A"),
            "Default": track.get("Default", "N/A"),
        }

        # Convertir en JSON pour une meilleure lisibilité
        track_json = json.dumps(track_info, indent=2, ensure_ascii=False)
        logger.debug(f"Piste audio #{i+1}:\n{track_json}")

    if preset in [
        "Dessins animes VF",
        "Films - Series VF",
        "4K - 10bits",
    ]:

        # Sélectionner les pistes audio en français
        pistes_francaises = [
            piste
            for piste in info_pistes["TitleList"][0]["AudioList"]
            if piste.get("LanguageCode", "") == "fra"
        ]
        if not pistes_francaises:
            print(f"{horodatage()} 🚫 Aucune piste audio française disponible.")
            return None

        # Filtrer les pistes selon les critères
        pistes_audio_finales = [
            piste
            for piste in pistes_francaises
            if not any(
                critere in enlever_accents(piste.get("Name", ""))
                for critere in criteres_audios
            )
        ]

        if len(pistes_audio_finales) < 1:
            print(f"{horodatage()} 🚫 Aucune piste audio disponible pour ce média.")
            return None

        if len(pistes_audio_finales) > 1:
            print(
                f"{horodatage()} 🚫 Il y a plus de 2 pistes valides pour ce média. (Pistes : {pistes_audio_finales})"
            )
            return None

        pistes_audio_selectionnees = [pistes_audio_finales[0]["TrackNumber"]]

    elif preset in ["Films - Series MULTI", "Mangas MULTI", "Mangas VO"]:
        # Sélectionner les numéros de piste audio depuis la première entrée de la liste des titres
        pistes_audio_selectionnees = [
            piste["TrackNumber"] for piste in info_pistes["TitleList"][0]["AudioList"]
        ]

        if preset in ["Films - Series MULTI", "Mangas MULTI 1000kbps"]:
            # Vérifier si la liste contient au moins deux entrées
            if len(pistes_audio_selectionnees) < 2:
                print(
                    f"{horodatage()} 🚫 Minimum 2 pistes audios requises pour un média en MULTI."
                )
                return None

        if preset == "Mangas VO":
            if len(pistes_audio_selectionnees) > 2:
                print(
                    f"{horodatage()} 🚫 Il y a plus de 2 pistes valides pour ce média en VO."
                )
                return None

        # Vérifier s'il existe au moins une piste audio en français
        if any(
            piste.get("LanguageCode", "") == "fra"
            for piste in info_pistes["TitleList"][0]["AudioList"]
        ):
            # Trouver le numéro de la première piste audio en français
            piste_francaise_index = next(
                piste["TrackNumber"]
                for piste in info_pistes["TitleList"][0]["AudioList"]
                if piste.get("LanguageCode", "") == "fra"
            )

            # Déplacer la piste audio française en première position dans la liste
            pistes_audio_selectionnees.insert(
                0,
                pistes_audio_selectionnees.pop(
                    pistes_audio_selectionnees.index(piste_francaise_index)
                ),
            )
        else:
            if preset in ["Films - Series MULTI", "Mangas MULTI"]:
                print(
                    f"{horodatage()} 🚫 Aucune piste audio française disponible pour ce média."
                )
                return None

    if pistes_audio_selectionnees == []:
        # Aucun sous-titre français trouvé, retourner une erreur
        print(f"{horodatage()} 🚫 Aucune piste audio disponible pour ce média.")
        return None
    return pistes_audio_selectionnees
