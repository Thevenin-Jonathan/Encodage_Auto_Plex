def selectionner_sous_titres(info_pistes, preset):
    sous_titres_selectionnes = []

    if preset in ["Dessins animes FR 1000kbps", "1080p HD-Light 1500kbps", "Mangas MULTI 1000kbps"]:
        sous_titres_francais = [sous_titre for sous_titre in info_pistes['TitleList']
                                [0]['SubtitleList'] if sous_titre['LanguageCode'] == 'fre']
        if sous_titres_francais:
            sous_titres_selectionnes = [sous_titre['TrackNumber']
                                        for sous_titre in sous_titres_francais]

    elif preset == "Manga VO":
        sous_titres_selectionnes = [sous_titre['TrackNumber']
                                    for sous_titre in info_pistes['TitleList'][0]['SubtitleList']]

    return sous_titres_selectionnes
