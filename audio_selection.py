from constants import horodatage, criteres_audios

# Fonction pour sélectionner les pistes audios en fonction du preset


def selectionner_pistes_audio(info_pistes, preset):
    pistes_audio_selectionnees = []

    if preset in ["Dessins animes FR 1000kbps", "1080p HD-Light 1500kbps"]:
        pistes_francaises = [piste for piste in info_pistes['TitleList']
                             [0]['AudioList'] if piste['LanguageCode'] == 'fra']
        if not pistes_francaises:
            print(f"{horodatage()} 🚫 Aucune piste audio française disponible.")
            return None  # Aucune piste française disponible

        pistes_audio_finales = [piste for piste in pistes_francaises if not any(
            critere in piste['Description'] for critere in criteres_audios)]
        if len(pistes_audio_finales) != 1:
            print(
                f"{horodatage()} 🚫 Il y a soit aucune piste valide, soit plusieurs pistes valides.")
            return None  # Soit aucune piste valide, soit plusieurs pistes valides

        pistes_audio_selectionnees = [pistes_audio_finales[0]['TrackNumber']]

    elif preset == "Mangas MULTI 1000kbps":
        pistes_audio_selectionnees = [piste['TrackNumber']
                                      for piste in info_pistes['TitleList'][0]['AudioList']]
        if any(piste['LanguageCode'] == 'fra' for piste in info_pistes['TitleList'][0]['AudioList']):
            piste_francaise_index = next(
                piste['TrackNumber'] for piste in info_pistes['TitleList'][0]['AudioList'] if piste['LanguageCode'] == 'fra')
            pistes_audio_selectionnees.insert(0, pistes_audio_selectionnees.pop(
                pistes_audio_selectionnees.index(piste_francaise_index)))

    elif preset == "Mangas VO 1000kbps":
        pistes_audio_selectionnees = [piste['TrackNumber']
                                      for piste in info_pistes['TitleList'][0]['AudioList']]

    return pistes_audio_selectionnees
