from tqdm import tqdm
import threading
from file_operations import obtenir_pistes_audio, verifier_dossiers
from audio_selection import selectionner_pistes_audio
from subtitle_selection import selectionner_sous_titres
from constants import dossier_encodage_manuel, dossier_sortie, criteres_nom_pistes, fichier_presets, horodatage
import os
import subprocess
import re

# Verrou pour synchroniser l'accès à la console
console_lock = threading.Lock()


def lancer_encodage(dossier, fichier, preset):
    input_path = os.path.join(dossier, fichier)
    # Vérifier si le fichier a déjà été encodé pour éviter les encodages en boucle
    if "_encoded" in fichier:
        print(f"{horodatage()} 🔄 Le fichier {
              fichier} a déjà été encodé, il est ignoré.")
        return

    output_path = os.path.join(dossier_sortie, os.path.splitext(fichier)[
                               0] + "_encoded.mkv")  # Modifier l'extension de sortie en .mkv et le chemin

    info_pistes = obtenir_pistes_audio(input_path)
    if info_pistes is None:
        print(
            f"{horodatage()} ❌ Erreur lors de l'obtention des informations des pistes audio.")
        os.rename(input_path, os.path.join(
            dossier_encodage_manuel, os.path.basename(input_path)))
        print(f"{horodatage()} 📁 Fichier déplacé pour encodage manuel: {fichier}")
        return

    pistes_audio = selectionner_pistes_audio(
        info_pistes, preset, criteres_nom_pistes)
    if pistes_audio is None:
        print(f"{horodatage()} 🚫 Aucune piste audio valide trouvée pour l'encodage.")
        os.rename(input_path, os.path.join(
            dossier_encodage_manuel, os.path.basename(input_path)))
        print(f"{horodatage()} 📁 Fichier déplacé pour encodage manuel: {fichier}")
        return

    sous_titres = selectionner_sous_titres(info_pistes, preset)
    options_audio = ','.join([f'--audio={piste}' for piste in pistes_audio])
    options_sous_titres = ','.join(
        [f'--subtitle={sous_titre}' for sous_titre in sous_titres])

    commande = [
        "HandBrakeCLI",
        "--preset-import-file", fichier_presets,
        "-i", input_path,
        "-o", output_path,
        "--preset", preset,
    ] + options_audio.split(',') + options_sous_titres.split(',')
    with console_lock:
        print(f"{horodatage()} 🚀 Lancement de l'encodage pour {fichier} avec le preset {
              preset}, pistes audio {pistes_audio}, et sous-titres {sous_titres}")
    try:
        process = subprocess.Popen(
            commande, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        last_percent_complete = -1
        percent_pattern = re.compile(r'Encoding:.*?(\d+\.\d+)\s?%')
        with tqdm(total=100, desc=f"Encodage de {fichier}", position=0, leave=True, dynamic_ncols=True) as pbar:
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
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
                print(f"\n{horodatage()} ✅ Encodage terminé pour {fichier} avec le preset {
                      preset}, pistes audio {pistes_audio}, et sous-titres {sous_titres}")
            else:
                print(
                    f"\n{horodatage()} ❌ Erreur lors de l'encodage de {fichier}")
    except subprocess.CalledProcessError as e:
        with console_lock:
            print(f"\n{horodatage()} ❌ Erreur lors de l'encodage de {
                  fichier}: {e}")
            print(f"\n{horodatage()} ⚠️ Erreur de la commande : {e.stderr}")


def traitement_file_encodage(file_encodage):
    verifier_dossiers()
    with tqdm(total=0, position=1, leave=False, desc="Files en attente", bar_format="{desc}: {n_fmt}") as pbar_queue:
        while True:
            pbar_queue.total = file_encodage.qsize()
            pbar_queue.refresh()
            dossier, fichier, preset = file_encodage.get()
            with console_lock:
                print(f"\n{horodatage()} 🔄 Traitement du fichier en cours: {
                      fichier} dans le dossier {dossier}")
            lancer_encodage(dossier, fichier, preset)
            file_encodage.task_done()
            pbar_queue.total = file_encodage.qsize()
            pbar_queue.refresh()
            with console_lock:
                print(f"\n{horodatage()} Files en attente: {
                      file_encodage.qsize()}")
                print(f"\n{horodatage()} 🏁 Fichier traité et encodé: {
                      fichier} dans le dossier {dossier}")
