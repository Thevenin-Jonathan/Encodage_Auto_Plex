import os
import subprocess
import re
from datetime import datetime
from tqdm import tqdm
import threading
import json

# Chemin du dossier de sortie pour les fichiers encodés
dossier_sortie = "D:/Ripped"

# Fichier de presets personnalisés
fichier_presets = 'custom_presets.json'

# Critères pour filtrer les pistes françaises indésirables
criteres_nom_pistes = ["VFQ", "CA", "AD", "audiodescription"]

# Dossiers pour encodage manuel
dossier_encodage_manuel = "D:/Torrents/Encodage_manuel"

# Vérifier l'existence des dossiers
if not os.path.exists(dossier_sortie):
    os.makedirs(dossier_sortie)
if not os.path.exists(dossier_encodage_manuel):
    os.makedirs(dossier_encodage_manuel)

# Obtenir l'horodatage actuel


def horodatage():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Verrou pour synchroniser l'accès à la console
console_lock = threading.Lock()

# Fonction pour obtenir les informations des pistes audio d'un fichier


def obtenir_pistes_audio(filepath):
    commande = ["HandBrakeCLI", "-i", filepath, "--scan", "--json"]
    result = subprocess.run(commande, capture_output=True, text=True)
    if result.returncode != 0:
        print(
            f"{horodatage()} ❌ **Erreur** lors de l'exécution de HandBrakeCLI: {result.stderr}")
        return None
    if not result.stdout.strip():  # Vérification supplémentaire
        print(f"{horodatage()} ❌ **Erreur** : la sortie de HandBrakeCLI est vide.")
        return None
    try:
        # Extraire uniquement la partie JSON correcte de la sortie
        json_start = result.stdout.find(
            '{', result.stdout.find('JSON Title Set:'))
        json_end = result.stdout.rfind('}') + 1
        json_str = result.stdout[json_start:json_end]
        info_pistes = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"{horodatage()} ❌ **Erreur** de décodage JSON: {e}")
        return None
    return info_pistes

# Fonction pour sélectionner les pistes audio selon les critères spécifiés


def selectionner_pistes_audio(info_pistes, preset):
    pistes_audio_selectionnees = []

    if preset in ["Dessins animes FR 1000kbps", "1080p HD-Light 1500kbps"]:
        pistes_francaises = [piste for piste in info_pistes['TitleList']
                             [0]['AudioList'] if piste['LanguageCode'] == 'fre']
        if not pistes_francaises:
            print(f"{horodatage()} ❌ **Aucune piste audio française disponible.**")
            return None  # Aucune piste française disponible

        pistes_audio_finales = [piste for piste in pistes_francaises if not any(
            critere in piste['Description'] for critere in criteres_nom_pistes)]
        if len(pistes_audio_finales) != 1:
            print(f"{horodatage(
            )} ❌ **Il y a soit aucune piste valide, soit plusieurs pistes valides.**")
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

# Lancer l'encodage HandBrakeCLI pour un fichier


def lancer_encodage(dossier, fichier, preset):
    input_path = os.path.join(dossier, fichier)
    # Vérifier si le fichier a déjà été encodé pour éviter les encodages en boucle
    if "_encoded" in fichier:
        print(
            f"{horodatage()} ℹ️ **Le fichier {fichier} a déjà été encodé, il est ignoré.**")
        return

    output_path = os.path.join(dossier_sortie, os.path.splitext(fichier)[
                               0] + "_encoded.mkv")  # Modifier l'extension de sortie en .mkv et le chemin

    info_pistes = obtenir_pistes_audio(input_path)
    if info_pistes is None:
        print(
            f"{horodatage()} ❌ **Erreur lors de l'obtention des informations des pistes audio.**")
        os.rename(input_path, os.path.join(
            dossier_encodage_manuel, os.path.basename(input_path)))
        print(f"{horodatage()} 📁 **Fichier déplacé pour encodage manuel: {fichier}**")
        return

    pistes_audio = selectionner_pistes_audio(info_pistes, preset)
    if pistes_audio is None:
        print(f"{horodatage()} 📁 **Fichier déplacé pour encodage manuel: {fichier}**")
        os.rename(input_path, os.path.join(
            dossier_encodage_manuel, os.path.basename(input_path)))
        return

    options_audio = ','.join([f'--audio={piste}' for piste in pistes_audio])

    commande = [
        "HandBrakeCLI",
        "--preset-import-file", fichier_presets,
        "-i", input_path,
        "-o", output_path,
        "--preset", preset,
    ] + options_audio.split(',')
    with console_lock:
        print(f"{horodatage()} 🚀 **Lancement de l'encodage pour {
              fichier} avec le preset {preset} et pistes audio {pistes_audio}**")
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
                print(f"\n{horodatage()} ✅ **Encodage terminé pour {
                      fichier} avec le preset {preset} et pistes audio {pistes_audio}**")
            else:
                print(
                    f"\n{horodatage()} ❌ **Erreur lors de l'encodage de {fichier}**")
    except subprocess.CalledProcessError as e:
        with console_lock:
            print(
                f"\n{horodatage()} ❌ **Erreur lors de l'encodage de {fichier}: {e}**")
            print(f"\n{horodatage()} ⚠️ **Erreur de la commande : {e.stderr}**")

# Fonction pour traiter la file d'attente d'encodage


def traitement_file_encodage(file_encodage):
    with tqdm(total=0, position=1, leave=False, desc="Files en attente", bar_format="{desc}: {n_fmt}") as pbar_queue:
        while True:
            pbar_queue.total = file_encodage.qsize()
            pbar_queue.refresh()
            dossier, fichier, preset = file_encodage.get()
            with console_lock:
                print(f"\n{horodatage(
                )} 🔄 **Traitement du fichier en cours: {fichier} dans le dossier {dossier}**")
            lancer_encodage(dossier, fichier, preset)
            file_encodage.task_done()
            pbar_queue.total = file_encodage.qsize()
            pbar_queue.refresh()
            with console_lock:
                print(
                    f"\n{horodatage()} **Files en attente: {file_encodage.qsize()}**")
                print(f"\n{horodatage(
                )} 🏁 **Fichier traité et encodé: {fichier} dans le dossier {dossier}**")
