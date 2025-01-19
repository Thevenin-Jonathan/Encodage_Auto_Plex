def selectionner_pistes_audio(info_pistes, preset, criteres_nom_pistes):
    pistes_audio_selectionnees = []

    if preset in ["Dessins animes FR 1000kbps", "1080p HD-Light 1500kbps"]:
        pistes_francaises = [piste for piste in info_pistes['TitleList']
                             [0]['AudioList'] if piste['LanguageCode'] == 'fre']
        if not pistes_francaises:
            print("Aucune piste audio française disponible.")
            return None  # Aucune piste française disponible

        pistes_audio_finales = [piste for piste in pistes_francaises if not any(
            critere in piste['Description'] for critere in criteres_nom_pistes)]
        if len(pistes_audio_finales) != 1:
            print("Il y a soit aucune piste valide, soit plusieurs pistes valides.")
            return None  # Soit aucune piste valide, soit plusieurs pistes valides

        pistes_audio_selectionnees = [pistes_audio_finales[0]['TrackNumber']]

    elif preset == "Mangas MULTI 1000kbps":
        pistes_audio_selectionnees = [piste['TrackNumber']
                                      for piste in info_pistes['TitleList'][0]['AudioList']]
        if any(piste['LanguageCode'] == 'fre' for piste in info_pistes['TitleList'][0]['AudioList']):
            piste_francaise_index = next(
                piste['TrackNumber'] for piste in info_pistes['TitleList'][0]['AudioList'] if piste['LanguageCode'] == 'fre')
            pistes_audio_selectionnees.insert(0, pistes_audio_selectionnees.pop(
                pistes_audio_selectionnees.index(piste_francaise_index)))

    elif preset == "Manga VO":
        pistes_audio_selectionnees = [piste['TrackNumber']
                                      for piste in info_pistes['TitleList'][0]['AudioList']]

    return pistes_audio_selectionnees
