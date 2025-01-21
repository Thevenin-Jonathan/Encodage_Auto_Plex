from constants import horodatage, criteres_audios, enlever_accents

# Fonction pour sélectionner les pistes audios en fonction du preset


def selectionner_pistes_audio(info_pistes, preset):
    pistes_audio_selectionnees = []

    if preset in ["Dessins animés FR 1000kbps", "1080p HD-Light 1500kbps"]:
        # Sélectionner les pistes audio en français
        pistes_francaises = [
            piste
            for piste in info_pistes["TitleList"][0]["AudioList"]
            if piste["LanguageCode"] == "fra"
        ]
        if not pistes_francaises:
            print(f"{horodatage()} 🚫 Aucune piste audio française disponible.")
            return None  # Aucune piste française disponible

        # Filtrer les pistes selon les critères
        pistes_audio_finales = [
            piste
            for piste in pistes_francaises
            if "Name" not in piste
            or not any(
                critere in enlever_accents(piste["Name"]) for critere in criteres_audios
            )
        ]
        if len(pistes_audio_finales) != 1:
            print(
                f"{horodatage()} 🚫 Il y a soit aucune piste valide, soit plusieurs pistes valides."
            )
            return None  # Soit aucune piste valide, soit plusieurs pistes valides

        pistes_audio_selectionnees = [pistes_audio_finales[0]["TrackNumber"]]

    elif preset == "Mangas MULTI 1000kbps":
        # Sélectionner les numéros de piste audio depuis la première entrée de la liste des titres
        pistes_audio_selectionnees = [
            piste["TrackNumber"] for piste in info_pistes["TitleList"][0]["AudioList"]
        ]

        # Vérifier si la liste contient au moins deux entrées
        if len(pistes_audio_selectionnees) < 2:
            # Afficher un message d'erreur si la liste des pistes audio contient moins de deux entrées
            print(
                f"{horodatage(
            )} 🚫 La liste des pistes audio sélectionnées contient moins de deux entrées."
            )
            return None

        # Vérifier s'il existe au moins une piste audio en français
        if any(
            piste["LanguageCode"] == "fra"
            for piste in info_pistes["TitleList"][0]["AudioList"]
        ):
            # Trouver le numéro de la première piste audio en français
            piste_francaise_index = next(
                piste["TrackNumber"]
                for piste in info_pistes["TitleList"][0]["AudioList"]
                if piste["LanguageCode"] == "fra"
            )

            # Déplacer la piste audio française en première position dans la liste
            pistes_audio_selectionnees.insert(
                0,
                pistes_audio_selectionnees.pop(
                    pistes_audio_selectionnees.index(piste_francaise_index)
                ),
            )
        else:
            # Afficher un message d'erreur si aucune piste audio française n'est disponible
            print(f"{horodatage()} 🚫 Aucune piste audio française disponible.")
            return None

    elif preset == "Mangas VO 1000kbps":
        # Sélectionner toutes les pistes audio
        pistes_audio_selectionnees = [
            piste["TrackNumber"] for piste in info_pistes["TitleList"][0]["AudioList"]
        ]

    return pistes_audio_selectionnees
