from constants import fichier_presets


def construire_commande_handbrake(
    input_path, output_path, preset, options_audio, options_sous_titres, options_burn
):
    """
    Construit la commande HandBrakeCLI pour l'encodage.

    Arguments:
    input_path -- Chemin du fichier d'entrée.
    output_path -- Chemin du fichier de sortie.
    preset -- Preset HandBrakeCLI à utiliser pour l'encodage.
    options_audio -- Options audio pour HandBrakeCLI.
    options_sous_titres -- Options de sous-titres pour HandBrakeCLI.
    options_burn -- Options de sous-titres à incruster pour HandBrakeCLI.

    Retourne:
    Une liste représentant la commande HandBrakeCLI.
    """
    return [
        "HandBrakeCLI",
        "--preset-import-file",
        fichier_presets,
        "-i",
        input_path,
        "-o",
        output_path,
        "--preset",
        preset,
        options_audio,
        options_sous_titres,
        options_burn,
        "--aencoder=aac",
        "--ab=192",
        "--mixdown=5point1",
    ]
