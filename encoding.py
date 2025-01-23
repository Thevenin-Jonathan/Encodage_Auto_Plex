import threading
import os
import subprocess
import re
from tqdm import tqdm
from audio_selection import selectionner_pistes_audio
from subtitle_selection import selectionner_sous_titres
from constants import (
    dossier_sortie,
    debug_mode,
)
from utils import horodatage, tronquer_nom_fichier
from file_operations import (
    obtenir_pistes,
    verifier_dossiers,
    copier_fichier_dossier_encodage_manuel,
)
from command_builder import construire_commande_handbrake
from notifications import (
    notifier_encodage_lancement,
    notifier_encodage_termine,
    notifier_erreur_encodage,
)

# Verrou pour synchroniser l'accès à la console
console_lock = threading.Lock()


def read_output(pipe, process_output):
    """
    Lit les sorties standard (stdout) et les erreurs (stderr) d'un processus en cours
    et les affiche dans la console tout en les ajoutant à une liste.

    Arguments:
    pipe -- Flux de sortie ou d'erreur du processus.
    process_output -- Liste pour stocker les sorties lues.
    """
    for line in iter(pipe.readline, ""):
        with console_lock:
            print(line, end="")
        process_output.append(line)
    pipe.close()


def lancer_encodage(dossier, fichier, preset, file_encodage):
    """
    Lance l'encodage d'un fichier en utilisant HandBrakeCLI avec le preset spécifié.
    Gère les options audio et sous-titres, et met à jour la console et les notifications.

    Arguments:
    dossier -- Chemin du dossier contenant le fichier à encoder.
    fichier -- Nom du fichier à encoder.
    preset -- Preset HandBrakeCLI à utiliser pour l'encodage.
    file_encodage -- Queue pour la file d'attente d'encodage.
    """

    # Récupérer uniquement le nom du fichier à partir du chemin complet
    nom_fichier = os.path.basename(fichier)
    # Tronquer le nom du fichier pour l'affichage
    short_fichier = tronquer_nom_fichier(nom_fichier)

    input_path = os.path.join(dossier, nom_fichier)
    # Vérifier si le fichier a déjà été encodé pour éviter les encodages en boucle
    if "_encoded" in nom_fichier:
        print(
            f"{horodatage()} 🔄 Le fichier {nom_fichier} a déjà été encodé, il est ignoré."
        )
        return

    # Assurez-vous que le chemin de sortie est correctement défini
    output_path = os.path.join(
        dossier_sortie, os.path.splitext(nom_fichier)[0] + "_encoded.mkv"
    )  # Modifier l'extension de sortie en .mkv et le chemin

    # Obtenir les informations des pistes du fichier
    info_pistes = obtenir_pistes(input_path)
    if info_pistes is None:
        print(
            f"{horodatage()} ❌ Erreur lors de l'obtention des informations des pistes audio."
        )
        copier_fichier_dossier_encodage_manuel(input_path)
        return

    # Sélectionner les pistes audio en fonction du preset
    pistes_audio = selectionner_pistes_audio(info_pistes, preset)
    if pistes_audio is None:
        copier_fichier_dossier_encodage_manuel(input_path)
        return

    # Sélectionner les sous-titres en fonction du preset
    sous_titres, sous_titres_burn = selectionner_sous_titres(info_pistes, preset)
    if sous_titres is None:
        copier_fichier_dossier_encodage_manuel(input_path)
        return

    options_audio = f'--audio={",".join(map(str, pistes_audio))}'
    options_sous_titres = f'--subtitle={",".join(map(str, sous_titres))}'
    options_burn = (
        f"--subtitle-burned={sous_titres.index(sous_titres_burn) + 1}"
        if sous_titres_burn is not None
        else ""
    )

    # Construire la commande HandBrakeCLI
    commande = construire_commande_handbrake(
        input_path,
        output_path,
        preset,
        options_audio,
        options_sous_titres,
        options_burn,
    )

    if debug_mode:
        print(f"{horodatage()} 🔧 Commande d'encodage : {' '.join(commande)}")

    with console_lock:
        print(
            f"{horodatage()} � Lancement de l'encodage pour {short_fichier} avec le preset {preset}, pistes audio {pistes_audio}, et sous-titres {sous_titres} - burn {sous_titres_burn}"
        )
        notifier_encodage_lancement(short_fichier, file_encodage)

    try:
        if debug_mode:
            # En mode debug, capturer les sorties stdout et stderr
            process = subprocess.Popen(
                commande, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            stdout = []
            stderr = []

            stdout_thread = threading.Thread(
                target=read_output, args=(process.stdout, stdout)
            )
            stderr_thread = threading.Thread(
                target=read_output, args=(process.stderr, stderr)
            )

            stdout_thread.start()
            stderr_thread.start()

            stdout_thread.join()
            stderr_thread.join()
        else:
            # En mode standard, capturer seulement stdout et combiner stderr avec stdout
            process = subprocess.Popen(
                commande, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )

        last_percent_complete = -1
        percent_pattern = re.compile(r"Encoding:.*?(\d+\.\d+)\s?%")
        with tqdm(
            total=100,
            desc=f"Encodage de {short_fichier}",
            position=0,
            leave=True,
            dynamic_ncols=True,
        ) as pbar:
            while True:
                output = process.stdout.readline()
                if output == "" and process.poll() is not None:
                    break
                if output:
                    if debug_mode:
                        with console_lock:
                            print(output.strip())
                    match = percent_pattern.search(output)
                    if match:
                        percent_complete = float(match.group(1))
                        if percent_complete != last_percent_complete:
                            pbar.n = percent_complete
                            pbar.refresh()
                            last_percent_complete = percent_complete
            # Forcer la barre de progression à atteindre 100% à la fin
            pbar.n = 100
            pbar.refresh()

        process.wait()
        with console_lock:
            if process.returncode == 0:
                print(
                    f"\n{horodatage()} ✅ Encodage terminé pour {short_fichier} avec le preset {preset}, pistes audio {pistes_audio}, et sous-titres {sous_titres}"
                )
                notifier_encodage_termine(nom_fichier, file_encodage)
            else:
                print(f"\n{horodatage()} ❌ Erreur lors de l'encodage de {nom_fichier}")
                notifier_erreur_encodage(nom_fichier)
                if debug_mode:
                    # Affichage des erreurs en mode débogage
                    print(f"{horodatage()} ⚠️ Erreurs: {stderr}")
    except subprocess.CalledProcessError as e:
        with console_lock:
            print(
                f"\n{horodatage()} ❌ Erreur lors de l'encodage de {nom_fichier}: {e}"
            )
            print(f"\n{horodatage()} ⚠️ Erreur de la commande : {e.stderr}")
            notifier_erreur_encodage(nom_fichier)


def traitement_file_encodage(file_encodage):
    """
    Traite les fichiers d'encodage en vérifiant les dossiers, en ajoutant les fichiers à la file d'attente
    et en affichant les informations de progression.

    Arguments:
    file_encodage -- Queue pour la file d'attente d'encodage.
    """
    verifier_dossiers()
    with tqdm(
        total=0,
        position=1,
        leave=False,
        desc="Files en attente",
        bar_format="{desc}: {n_fmt}",
    ) as pbar_queue:
        while True:
            # Mettre à jour la barre de progression avec le nombre de fichiers en attente
            pbar_queue.total = file_encodage.qsize()
            pbar_queue.refresh()
            # Obtenir le prochain fichier de la file d'attente
            dossier, fichier, preset = file_encodage.get()

            # Récupérer uniquement le nom du fichier à partir du chemin complet
            nom_fichier = os.path.basename(fichier)
            # Tronquer le nom du fichier pour l'affichage
            short_fichier = tronquer_nom_fichier(nom_fichier)

            with console_lock:
                print(
                    f"\n{horodatage()} 🔄 Traitement du fichier en cours: {short_fichier} dans le dossier {dossier}"
                )
            # Lancer l'encodage du fichier
            lancer_encodage(dossier, fichier, preset, file_encodage)
            # Marquer la tâche comme terminée
            file_encodage.task_done()
            # Mettre à jour la barre de progression avec le nombre de fichiers restants en attente
            pbar_queue.total = file_encodage.qsize()
            pbar_queue.refresh()
            with console_lock:
                print(f"\n{horodatage()} Files en attente: {file_encodage.qsize()}")
                print(
                    f"\n{horodatage()} 🏁 Fichier traité et encodé: {short_fichier} dans le dossier {dossier}"
                )
