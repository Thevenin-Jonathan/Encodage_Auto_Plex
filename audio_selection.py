import json
from utils import horodatage, enlever_accents
from constants import criteres_audios
from logger import setup_logger

# Configuration du logger
logger = setup_logger(__name__)


def noter_piste_audio(piste, langues_prioritaires):
    """
    Attribue une note à une piste audio en fonction de critères spécifiques.

    Args:
        piste: Dictionnaire contenant les informations de la piste audio.
        langues_prioritaires: Liste des codes de langue prioritaires.

    Returns:
        Une note (int) pour la piste audio.
    """
    note = 0

    # Priorité pour les langues spécifiques
    if piste.get("LanguageCode", "").lower() in langues_prioritaires:
        note += 100

    # Bonus pour les pistes avec un language code
    if piste.get("LanguageCode"):
        note += 20

    # Priorité pour les pistes avec un nom vide ou contenant des mots-clés français
    nom_piste = enlever_accents(piste.get("Name", "none").lower())
    if piste.get("Name", "none").strip() == "" or any(
        mot in nom_piste
        for mot in [
            "vff",
            "fr",
        ]
    ):
        note += 60

    # Pénalité pour les pistes canadiennes
    if any(mot in nom_piste for mot in ["vfq", "cana", "queb"]):
        note -= 20

    # Éviter les pistes malentendantes, descriptives, etc.
    if any(
        critere in enlever_accents(piste.get("Name", "").lower())
        for critere in [
            "malentendant",
            "sdh",
            "descriptive",
            "audio description",
            "ad",
            "audiodescription",
            "description",
        ]
    ):
        note -= 100

    # Priorité pour les pistes par défaut
    if piste.get("Default", False):
        note += 10

    return note


def filtrer_pistes_audio(info_pistes, preset, verbose=False):
    """
    Filtre et sélectionne les meilleures pistes audio en fonction du preset.

    Args:
        info_pistes: Dictionnaire contenant les informations des pistes audio.
        preset: Chaîne de caractères représentant le preset utilisé pour l'encodage.
        verbose: Afficher les messages de débogage.

    Returns:
        Une liste des numéros de pistes audio sélectionnées ou None si aucune piste valide n'est trouvée.
    """
    if "TitleList" not in info_pistes or not info_pistes["TitleList"]:
        logger.warning(
            "Aucune liste de titres trouvée dans les informations des pistes"
        )
        return None

    if "AudioList" not in info_pistes["TitleList"][0]:
        logger.warning("Aucune liste de pistes audio trouvée")
        return None

    audio_tracks = info_pistes["TitleList"][0]["AudioList"]
    logger.debug(f"Nombre total de pistes audio détectées : {len(audio_tracks)}")

    # Si une seule piste audio est présente et que le preset n'est pas MULTI
    if len(audio_tracks) == 1 and "MULTI" not in preset and "VO" not in preset:
        piste_unique = audio_tracks[0]
        if piste_unique.get("LanguageCode", "").lower() != "fra":
            logger.warning(
                f"{horodatage()} 🚫 La seule piste audio n'est pas en français : "
                f"{piste_unique.get('LanguageCode', 'inconnu')}"
            )
        return [piste_unique.get("TrackNumber")]

    langues_prioritaires = ["fra", "fre", "fr", "french"]
    pistes_notees = []

    # Noter chaque piste audio
    for piste in audio_tracks:
        note = noter_piste_audio(piste, langues_prioritaires)
        pistes_notees.append(
            {"TrackNumber": piste.get("TrackNumber"), "Note": note, **piste}
        )

    # Trier les pistes par note décroissante
    pistes_notees = sorted(pistes_notees, key=lambda x: x["Note"], reverse=True)
    logger.debug(
        f"Pistes notées : {json.dumps(pistes_notees, indent=2, ensure_ascii=False)}"
    )

    pistes_selectionnees = []

    # Logique de sélection en fonction du preset
    if preset in ["Dessins animes VF", "Films - Series VF", "4K - 10bits"]:
        # Garder uniquement la meilleure piste française non malentendante
        for piste in pistes_notees:
            if (
                piste.get("LanguageCode", "").lower() in langues_prioritaires
                and piste["Note"] > 0
            ):
                pistes_selectionnees = [piste["TrackNumber"]]
                break

    elif preset in ["Films - Series MULTI", "Mangas MULTI"]:
        # Garder une seule piste par langue, en évitant les pistes malentendantes
        langues_vues = set()
        for piste in pistes_notees:
            if (
                piste.get("LanguageCode", "").lower() not in langues_vues
                and piste["Note"] > 0
            ):
                pistes_selectionnees.append(piste["TrackNumber"])
                langues_vues.add(piste.get("LanguageCode", "").lower())

        # Vérifier si le nombre de pistes sélectionnées est inférieur à deux
        if len(pistes_selectionnees) < 2:
            logger.warning(
                f"{horodatage()} 🚫 Moins de deux pistes valides trouvées pour le preset MULTI."
            )
            return None

    elif preset == "Mangas VO":
        # Collecter toutes les pistes valides
        pistes_valides = [
            piste["TrackNumber"] for piste in pistes_notees if piste["Note"] > 0
        ]

        # Vérifier si plus d'une piste valide est sélectionnée
        if len(pistes_valides) > 1:
            logger.warning(
                f"{horodatage()} 🚫 Trop de pistes valides trouvées pour le preset VO."
            )
            return None

        # Garder uniquement la meilleure piste si une seule est valide
        if pistes_valides:
            pistes_selectionnees = [pistes_valides[0]]

    # Si aucune piste valide n'est trouvée, retourner None
    if not pistes_selectionnees:
        logger.warning(f"{horodatage()} 🚫 Aucune piste audio valide sélectionnée.")
        return None

    logger.debug(
        f"Pistes sélectionnées pour le preset '{preset}' : {pistes_selectionnees}"
    )
    return pistes_selectionnees
