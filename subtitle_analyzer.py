import os
import subprocess
import json

from logger import setup_logger

# Configuration du logger
logger = setup_logger(__name__)


def obtenir_info_mediainfo(fichier_mkv):
    """
    Obtenir des informations sur les pistes de sous-titres d'un fichier MKV.

    Args:
        fichier_mkv: Chemin du fichier MKV à analyser

    Returns:
        Informations JSON des pistes de sous-titres
    """
    try:
        # Options pour éviter la fenêtre
        process_flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0

        # Vérifier si mediainfo est disponible
        try:
            version_check = subprocess.run(
                ["mediainfo", "--Version"],
                capture_output=True,
                text=True,
                creationflags=process_flags,
            )
            print(f"Version MediaInfo: {version_check.stdout.strip()}")
        except Exception as e:
            print(f"Erreur lors de la vérification de MediaInfo: {e}")
            # Si MediaInfo n'est pas dans le PATH, essayer avec un chemin explicite
            mediainfo_paths = [
                r"C:\Program Files\MediaInfo\MediaInfo.exe",
                r"C:\Program Files (x86)\MediaInfo\MediaInfo.exe",
            ]
            for path in mediainfo_paths:
                if os.path.exists(path):
                    print(f"MediaInfo trouvé à: {path}")
                    return obtenir_info_mediainfo_explicit_path(fichier_mkv, path)
            return "MediaInfo non trouvé sur le système"

        # Exécuter MediaInfo avec les options appropriées
        print(f"Exécution de MediaInfo pour le fichier: {fichier_mkv}")
        resultat = subprocess.run(
            [
                "mediainfo",
                "--Output=JSON",
                fichier_mkv,
            ],
            capture_output=True,
            text=True,
            creationflags=process_flags,
        )

        # Vérifier si MediaInfo a renvoyé une erreur
        if resultat.returncode != 0:
            print(f"MediaInfo a retourné un statut d'erreur: {resultat.returncode}")
            if resultat.stderr:
                print(f"Erreur MediaInfo: {resultat.stderr}")
            return f"Erreur MediaInfo (code {resultat.returncode})"

        # Analyser la sortie JSON
        if resultat.stdout:
            try:
                return json.loads(resultat.stdout)
            except json.JSONDecodeError as e:
                print(f"Erreur lors du décodage JSON: {e}")
                return f"Erreur de décodage JSON: {e}"
        else:
            print("Aucune sortie reçue de MediaInfo")
            return "Aucune donnée reçue de MediaInfo"

    except Exception as e:
        print(f"Exception dans obtenir_info_mediainfo: {e}")
        return f"Une erreur s'est produite : {e}"


def obtenir_info_mediainfo_explicit_path(fichier_mkv, mediainfo_path):
    """Version avec chemin explicite vers MediaInfo"""
    try:
        process_flags = subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        resultat = subprocess.run(
            [mediainfo_path, "--Output=JSON", fichier_mkv],
            capture_output=True,
            text=True,
            creationflags=process_flags,
        )
        return json.loads(resultat.stdout)
    except Exception as e:
        return f"Une erreur avec le chemin explicite: {e}"


def analyser_sous_titres_francais(fichier_mkv, preset, verbose=False):
    """
    Analyse les sous-titres français d'un fichier MKV, détermine leur type et détecte les variantes régionales

    Args:
        fichier_mkv: Chemin du fichier MKV à analyser
        verbose: Afficher les messages de débogage

    Returns:
        Tuple (index_verbal, index_non_verbal, resultat_complet)
        - index_verbal: Index du sous-titre verbal recommandé (None si non disponible)
        - index_non_verbal: Index du sous-titre non verbal recommandé (None si non disponible)
        - resultat_complet: Dictionnaire contenant toutes les informations d'analyse
    """
    try:
        info = obtenir_info_mediainfo(fichier_mkv)

        # Valeurs par défaut pour les index de sous-titres recommandés
        index_verbal_recommande = None
        index_non_verbal_recommande = None

        if isinstance(info, str):
            return None, None, {"erreur": info}

        if (
            not isinstance(info, dict)
            or "media" not in info
            or "track" not in info["media"]
        ):
            return None, None, {"erreur": "Format de données non reconnu"}

        # Extraire les pistes de sous-titres français et similaires
        sous_titres_fr = []

        # Dictionnaire pour mapper les IDs de piste aux numéros de sous-titres
        sous_titres_index = {}
        index_sous_titre = 1

        # Créer d'abord un index de tous les sous-titres
        for track in info["media"].get("track", []):
            if track.get("@type") == "Text":
                sous_titres_index[track.get("ID", "")] = index_sous_titre
                index_sous_titre += 1

        # Langues françaises reconnues (en minuscules)
        langues_francaises = ["fr", "fre", "fra", "french", "fr-fr"]

        # Dictionnaire des priorités pour les variantes régionales du français
        # Ces termes ne sont pris en compte QUE SI la langue est déjà identifiée comme française
        priorites_variantes = {
            # Français de France: priorité maximale
            "vff": 10,
            "french": 9,
            "fre": 9,
            "fra": 9,
            "fr-fr": 9,
            "france": 9,
            "european": 9,
            "europe": 9,
            # Français international: priorité haute
            "français": 8,
            "francais": 8,
            "fr": 8,
            "piste": 8,
            # Français belge, suisse: priorité moyenne-haute
            "be": 7,
            "ch": 7,
            "belgique": 7,
            "suisse": 7,
            "wallonie": 7,
            # Français québécois: priorité moyenne
            "vfq": 6,
            "québécois": 6,
            "quebecois": 6,
            "quebec": 6,
            "qc": 6,
            "canadian": 5,
            "canada": 5,
            "ca": 5,
        }

        # Mots-clés pour identifier les sous-titres pour malentendants
        # (uniquement utilisés après identification de la langue)
        mots_cles_malentendants = [
            "sdh",
            "malentendant",
            "sourd",
            "hearing",
            "impaired",
            "deaf",
        ]

        for track in info["media"].get("track", []):
            # Vérifier si c'est une piste de sous-titres
            if track.get("@type") == "Text":
                # Obtenir la langue principale (convertir en minuscule)
                langue = track.get("Language", "").lower()

                # Obtenir le titre (convertir en minuscule)
                titre = track.get("Title", "").lower() if track.get("Title") else ""

                # PREMIÈRE VÉRIFICATION RIGOUREUSE: La langue doit être explicitement française
                # ou contenir des mots-clés français très spécifiques dans le titre
                est_francais = False
                priorite_variante = 0
                variante_detectee = "standard"

                # 1. Vérifier si la langue est explicitement française
                if langue in langues_francaises:
                    est_francais = True
                    # Attribuer une priorité standard pour les pistes avec code langue français
                    priorite_variante = 8
                    variante_detectee = "standard"

                    if verbose:
                        print(
                            f"Piste française identifiée par code langue '{langue}': {track}"
                        )

                    # Vérifier si la piste contient des mots-clés de variante française particulière
                    if "france" in titre or "vff" in titre:
                        priorite_variante = 10
                        variante_detectee = "france"
                        if verbose:
                            print(f"Variante France identifiée par titre: {titre}")
                    # Vérifier si c'est explicitement une piste canadienne (qui doit avoir une priorité inférieure)
                    elif "canad" in titre:
                        priorite_variante = 5
                        variante_detectee = "canadien"
                        if verbose:
                            print(
                                f"Variante canadienne identifiée par titre (priorité réduite): {titre}"
                            )
                    # Autres variantes potentielles
                    elif "quebec" in titre or "québec" in titre or "vfq" in titre:
                        priorite_variante = 6
                        variante_detectee = "québécois"
                    elif "belg" in titre:
                        priorite_variante = 7
                        variante_detectee = "belge"
                    elif "suisse" in titre:
                        priorite_variante = 7
                        variante_detectee = "suisse"

                # 2. Si la langue n'est pas explicitement française, chercher des mots-clés très spécifiques
                elif any(
                    mot in titre
                    for mot in ["vff", "français", "francais", "french", "france"]
                ):
                    est_francais = True
                    priorite_variante = (
                        9  # Haute priorité pour les mots-clés français explicites
                    )
                    variante_detectee = "france"

                    if verbose:
                        print(
                            f"Piste française identifiée par mot-clé explicite dans le titre: {titre}"
                        )

                # 3. Vérifier les variantes francophones avec priorité inférieure
                elif any(
                    mot in titre for mot in ["vfq", "québécois", "quebecois", "quebec"]
                ):
                    est_francais = True
                    priorite_variante = 6
                    variante_detectee = "québécois"

                    if verbose:
                        print(
                            f"Piste québécoise identifiée par mot-clé dans le titre: {titre}"
                        )

                # 4. Vérifier les variantes canadiennes avec priorité encore plus basse
                elif "canad" in titre:
                    est_francais = True
                    priorite_variante = 5
                    variante_detectee = "canadien"

                    if verbose:
                        print(
                            f"Piste canadienne identifiée par mot-clé dans le titre: {titre}"
                        )

                # 5. Traiter les cas génériques (uniquement si la langue est française)
                elif est_francais and any(mot in titre for mot in ["piste", "track"]):
                    # Déjà traité comme français par le code langue, juste confirmer que c'est générique
                    if verbose:
                        print(f"Piste française générique détectée: {titre}")

                # Si ce n'est pas du français après toutes ces vérifications, ignorer cette piste
                if not est_francais:
                    if verbose:
                        print(f"Piste ignorée (non française): {langue} - {titre}")
                    continue

                # ANALYSE DÉTAILLÉE DES SOUS-TITRES FRANÇAIS

                # Déterminer la variante régionale
                est_malentendant = False

                # Rechercher les variantes régionales dans le titre
                for variante, prio in priorites_variantes.items():
                    if variante in titre:
                        if prio > priorite_variante:
                            priorite_variante = prio
                            if "vff" in titre or "france" in titre:
                                variante_detectee = "france"
                            elif (
                                "vfq" in titre
                                or "québécois" in titre
                                or "quebecois" in titre
                            ):
                                variante_detectee = "québécois"
                            elif "canadian" in titre or "canada" in titre:
                                variante_detectee = "canadien"
                            elif "belg" in titre:
                                variante_detectee = "belge"
                            elif "suisse" in titre:
                                variante_detectee = "suisse"
                            elif "european" in titre or "europe" in titre:
                                variante_detectee = "européen"
                            else:
                                variante_detectee = variante

                            if verbose:
                                print(
                                    f"Variante détectée: {variante_detectee} (priorité {prio})"
                                )

                # Vérifier si c'est un sous-titre pour malentendants
                if any(mot in titre for mot in mots_cles_malentendants):
                    est_malentendant = True
                    if verbose:
                        print(f"Sous-titre pour malentendants détecté: {titre}")

                # Calculer des métriques pour aider à déterminer le type
                try:
                    taille = int(track.get("StreamSize", "0"))
                    elements = int(track.get("ElementCount", "0"))
                    est_force = track.get("Forced") == "Yes"
                    duree = float(track.get("Duration", "0"))

                    # Densité d'éléments par minute
                    elements_par_minute = elements / (duree / 60) if duree > 0 else 0

                    # Taille moyenne par élément
                    taille_par_element = taille / elements if elements > 0 else 0

                except (ValueError, ZeroDivisionError):
                    elements = 0
                    taille = 0
                    elements_par_minute = 0
                    taille_par_element = 0

                # Classifier le type de sous-titre
                type_sous_titre = "inconnu"

                # Sous-titres forcés (typiquement peu d'éléments, petite taille, marqués comme forcés)
                if est_force or (elements < 20 and taille < 1000):
                    type_sous_titre = "non_verbal"
                # Sous-titres verbaux complets (beaucoup d'éléments, grande taille)
                elif elements > 100 or taille > 10000:
                    type_sous_titre = "verbal"
                # Cas intermédiaires
                else:
                    # Analyser la densité d'éléments et la taille moyenne
                    if elements_par_minute > 5:
                        type_sous_titre = "verbal"
                    else:
                        type_sous_titre = "non_verbal"

                # Récupérer l'index du sous-titre (à partir de 1)
                track_id = track.get("ID", "")
                index = sous_titres_index.get(track_id, 0)

                sous_titres_fr.append(
                    {
                        "ID": track.get("@typeorder", ""),
                        "ID_Track": track_id,
                        "Index_Sous_Titre": index,
                        "Format": track.get("Format", "Non spécifié"),
                        "Taille": taille,
                        "Elements": elements,
                        "Elements_Par_Minute": round(elements_par_minute, 2),
                        "Taille_Par_Element": round(taille_par_element, 2),
                        "Durée": duree,
                        "Est_forcé": est_force,
                        "Est_Malentendant": est_malentendant,
                        "Type": type_sous_titre,
                        "Titre": track.get("Title", ""),
                        "Variante": variante_detectee,
                        "Priorité_Variante": priorite_variante,
                        "Langue_Code": langue,
                    }
                )

        # MODIFICATION DU TRI: Pénaliser les sous-titres pour malentendants
        sous_titres_fr.sort(
            key=lambda x: (
                -x[
                    "Priorité_Variante"
                ],  # D'abord par priorité de variante (décroissant)
                (
                    0 if x["Est_Malentendant"] else 1
                ),  # Pénaliser les sous-titres pour malentendants
                (
                    -1 if x["Type"] == "verbal" else 1
                ),  # Ensuite par type (verbal en premier)
                -x["Taille"],  # Enfin par taille (décroissant)
            )
        )

        # Préparer le résultat
        resultat = {
            "sous_titres_verbaux": [],
            "sous_titres_non_verbaux": [],
            "tous_sous_titres": sous_titres_fr,
            "variantes": {},
        }

        # Répartir les sous-titres selon leur type et variante
        variantes_trouvees = set()

        # D'abord, séparons les sous-titres standards et pour malentendants
        sous_titres_standards_verbaux = []
        sous_titres_malentendants_verbaux = []
        sous_titres_standards_non_verbaux = []
        sous_titres_malentendants_non_verbaux = []

        for st in sous_titres_fr:
            variantes_trouvees.add(st["Variante"])

            if st["Type"] == "verbal":
                if st["Est_Malentendant"]:
                    sous_titres_malentendants_verbaux.append(st)
                else:
                    sous_titres_standards_verbaux.append(st)
            elif st["Type"] == "non_verbal":
                if st["Est_Malentendant"]:
                    sous_titres_malentendants_non_verbaux.append(st)
                else:
                    sous_titres_standards_non_verbaux.append(st)

            # Grouper également par variante
            if st["Variante"] not in resultat["variantes"]:
                resultat["variantes"][st["Variante"]] = []
            resultat["variantes"][st["Variante"]].append(st)

        # Prioriser les sous-titres standards, et n'utiliser les malentendants que s'il n'y a pas d'alternative
        if sous_titres_standards_verbaux:
            resultat["sous_titres_verbaux"] = (
                sous_titres_standards_verbaux + sous_titres_malentendants_verbaux
            )
        else:
            resultat["sous_titres_verbaux"] = sous_titres_malentendants_verbaux

        if sous_titres_standards_non_verbaux:
            resultat["sous_titres_non_verbaux"] = (
                sous_titres_standards_non_verbaux
                + sous_titres_malentendants_non_verbaux
            )
        else:
            resultat["sous_titres_non_verbaux"] = sous_titres_malentendants_non_verbaux

        # Ajouter des informations supplémentaires et recommandations
        resultat["recommandations"] = {}

        # Recommandation pour les sous-titres verbaux (préférer les standards)
        if sous_titres_standards_verbaux:
            # Trier par priorité de variante
            st = sorted(
                sous_titres_standards_verbaux, key=lambda x: -x["Priorité_Variante"]
            )[0]
            resultat["recommandations"]["piste_verbale"] = st["ID_Track"]
            resultat["recommandations"]["index_verbal"] = st["Index_Sous_Titre"]
            index_verbal_recommande = st["Index_Sous_Titre"]
        elif sous_titres_malentendants_verbaux:
            # S'il n'y a que des malentendants, prendre le meilleur
            st = sous_titres_malentendants_verbaux[0]
            resultat["recommandations"]["piste_verbale"] = st["ID_Track"]
            resultat["recommandations"]["index_verbal"] = st["Index_Sous_Titre"]
            index_verbal_recommande = st["Index_Sous_Titre"]

        # Recommandation pour les sous-titres non verbaux
        if sous_titres_standards_non_verbaux:
            st = sorted(
                sous_titres_standards_non_verbaux, key=lambda x: -x["Priorité_Variante"]
            )[0]
            resultat["recommandations"]["piste_non_verbale"] = st["ID_Track"]
            resultat["recommandations"]["index_non_verbal"] = st["Index_Sous_Titre"]
            index_non_verbal_recommande = st["Index_Sous_Titre"]
        elif sous_titres_malentendants_non_verbaux:
            st = sous_titres_malentendants_non_verbaux[0]
            resultat["recommandations"]["piste_non_verbale"] = st["ID_Track"]
            resultat["recommandations"]["index_non_verbal"] = st["Index_Sous_Titre"]
            index_non_verbal_recommande = st["Index_Sous_Titre"]

        # Générer un résumé textuel
        resume = "Analyse des sous-titres français:\n\n"

        if not sous_titres_fr:
            resume += "Aucun sous-titre français trouvé dans le fichier.\n"
        else:
            resume += f"Nombre total de pistes de sous-titres français: {len(sous_titres_fr)}\n"
            resume += f"Variantes détectées: {', '.join(variantes_trouvees)}\n\n"

            if resultat["sous_titres_verbaux"]:
                st = resultat["sous_titres_verbaux"][0]
                resume += f"Sous-titre verbal recommandé (dialogues complets):\n"
                resume += f"- Sous-titre #{st['Index_Sous_Titre']} (Track ID: {st['ID_Track']})\n"
                resume += f"- Variante: {st['Variante'].capitalize()}\n"
                if st["Titre"]:
                    resume += f"- Titre: {st['Titre']}\n"
                if st["Est_Malentendant"]:
                    resume += f"- Type: Pour malentendants (SDH)\n"
                resume += f"- Éléments: {st['Elements']} ({st['Elements_Par_Minute']} par minute)\n"
                resume += (
                    f"- Taille: {st['Taille']} octets ({st['Taille']/1024:.2f} KB)\n\n"
                )

                titre = f" - Titre: {st['Titre']}" if st["Titre"] else ""
                est_malentendant = (
                    f" - Type: Pour malentendants (SDH)"
                    if st["Est_Malentendant"]
                    else ""
                )
                if "VO" in preset:
                    logger.debug(
                        f"Sous-titre forcé #{st['Index_Sous_Titre']} - Variante: {st['Variante'].capitalize()}{titre}{est_malentendant} - Taille: {st['Taille']/1024:.2f} KB"
                    )
                else:
                    logger.debug(
                        f"Sous-titre #{st['Index_Sous_Titre']} - Variante: {st['Variante'].capitalize()}{titre}{est_malentendant} - Taille: {st['Taille']/1024:.2f} KB"
                    )

                # S'il y a d'autres sous-titres verbaux, les mentionner
                if len(resultat["sous_titres_verbaux"]) > 1:
                    resume += "Autres pistes verbales disponibles:\n"
                    for i, st in enumerate(resultat["sous_titres_verbaux"][1:], 1):
                        resume += f"{i}. Sous-titre #{st['Index_Sous_Titre']} (Track ID: {st['ID_Track']})"
                        if st["Est_Malentendant"]:
                            resume += " (SDH)"
                        resume += f", Variante: {st['Variante'].capitalize()}"
                        if st["Titre"]:
                            resume += f", Titre: {st['Titre']}"
                        resume += f", Taille: {st['Taille']/1024:.2f} KB\n"
                    resume += "\n"
            else:
                resume += "Aucun sous-titre verbal français identifié.\n\n"
                logger.warning(
                    f"Aucun sous-titre verbal français identifié pour : {fichier_mkv}"
                )

            if resultat["sous_titres_non_verbaux"] and "VO" not in preset:
                st = resultat["sous_titres_non_verbaux"][0]
                resume += (
                    f"Sous-titre non verbal recommandé (forcé/traductions/effets):\n"
                )
                resume += f"- Sous-titre #{st['Index_Sous_Titre']} (Track ID: {st['ID_Track']})\n"
                resume += f"- Variante: {st['Variante'].capitalize()}\n"
                if st["Titre"]:
                    resume += f"- Titre: {st['Titre']}\n"
                if st["Est_Malentendant"]:
                    resume += f"- Type: Pour malentendants (SDH)\n"
                resume += f"- Éléments: {st['Elements']} ({st['Elements_Par_Minute']} par minute)\n"
                resume += (
                    f"- Taille: {st['Taille']} octets ({st['Taille']/1024:.2f} KB)\n\n"
                )

                titre = f" - Titre: {st['Titre']}" if st["Titre"] else ""
                est_malentendant = (
                    f" - Type: Pour malentendants (SDH)"
                    if st["Est_Malentendant"]
                    else ""
                )
                logger.debug(
                    f"Sous-titre forcé #{st['Index_Sous_Titre']} - Variante: {st['Variante'].capitalize()}{titre}{est_malentendant} - Taille: {st['Taille']/1024:.2f} KB"
                )

                # S'il y a d'autres sous-titres non verbaux, les mentionner
                if len(resultat["sous_titres_non_verbaux"]) > 1:
                    resume += "Autres pistes non verbales disponibles:\n"
                    for i, st in enumerate(resultat["sous_titres_non_verbaux"][1:], 1):
                        resume += f"{i}. Sous-titre #{st['Index_Sous_Titre']} (Track ID: {st['ID_Track']})"
                        if st["Est_Malentendant"]:
                            resume += " (SDH)"
                        resume += f", Variante: {st['Variante'].capitalize()}"
                        if st["Titre"]:
                            resume += f", Titre: {st['Titre']}"
                        resume += f", Taille: {st['Taille']/1024:.2f} KB\n"
                    resume += "\n"
            elif "VO" in preset:
                resume += "Pistes non verbales ignorées pour les encodages VO.\n\n"
            else:
                resume += "Aucun sous-titre non verbal français identifié.\n\n"
                logger.warning(f"Aucun sous-titre forcé identifié pour : {fichier_mkv}")

            # Inclure les recommandations de pistes
            resume += "Recommandations pour l'extraction:\n"
            if index_verbal_recommande:
                resume += f"- Sous-titre verbal recommandé: #{index_verbal_recommande} (Track ID: {resultat['recommandations'].get('piste_verbale', 'N/A')})\n"
            if index_non_verbal_recommande:
                resume += f"- Sous-titre non verbal recommandé: #{index_non_verbal_recommande} (Track ID: {resultat['recommandations'].get('piste_non_verbale', 'N/A')})\n"

        resultat["resume"] = resume
        return index_verbal_recommande, index_non_verbal_recommande, resultat

    except Exception as e:
        if verbose:
            print(f"Exception dans analyser_sous_titres_francais: {e}")
        return None, None, {"erreur": f"Une erreur s'est produite : {e}"}
