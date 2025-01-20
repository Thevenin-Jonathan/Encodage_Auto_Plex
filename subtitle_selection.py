from constants import horodatage, criteres_sous_titres_burn, criteres_sous_titres_supprimer

# Fonction pour sélectionner les sous-titres en fonction du preset


def selectionner_sous_titres(info_pistes, preset):
    sous_titres_selectionnes = []  # Liste des sous-titres à inclure dans la vidéo
    # Liste des sous-titres à incruster (burn) dans la vidéo
    sous_titres_burn = None

    # Traitement pour les presets spécifiés
    if preset in ["Dessins animes FR 1000kbps", "1080p HD-Light 1500kbps", "Mangas MULTI 1000kbps"]:
        # Todo
        return

    # Traitement spécifique pour le preset "Manga_VO"
    elif preset == "Mangas VO 1000kbps":
        for sous_titre in info_pistes['TitleList'][0]['SubtitleList']:
            # S'il n'y a pas déjà un sous titre incrusté
            if sous_titres_burn is None:
                # Garder uniquement les sous-titres en français
                if sous_titre['LanguageCode'] == 'fra':
                    sous_titres_burn = sous_titre['TrackNumber']
                    sous_titres_selectionnes.append(sous_titre['TrackNumber'])
            else:
                print(
                    f"{horodatage()} 🚫 Trop de sous-titres à incruster.")
                return None, None

        # Si un sous-titre français est présent, l'incruster
        if not sous_titres_burn is None:
            return sous_titres_selectionnes, sous_titres_burn
        else:
            print(
                f"{horodatage()} 🚫 Pas de sous-titres français disponible pour manga VO.")
            return None, None
