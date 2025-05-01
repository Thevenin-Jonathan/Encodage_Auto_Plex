from utils import horodatage, enlever_accents
from constants import criteres_audios


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

    if preset in [
        "Dessins animes VF",
        "Films - Series VF",
        "4K - 10bits",
    ]:
        # Marquer les pistes de langue inconnue comme françaises
        for piste in info_pistes["TitleList"][0]["AudioList"]:
            if (
                piste.get("LanguageCode", "") == ""
                or piste.get("LanguageCode", "") == "und"
            ):
                print(
                    f"{horodatage()} ℹ️ Piste audio de langue inconnue considérée comme française: {piste.get('Name', 'Sans nom')}"
                )
                piste["LanguageCode"] = "fra"

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
