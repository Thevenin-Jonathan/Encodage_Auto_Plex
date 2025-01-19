import os
import subprocess
import re
from datetime import datetime
from tqdm import tqdm
import threading

# Fichier de presets personnalisés
fichier_presets = 'custom_presets.json'

# Obtenir l'horodatage actuel


def horodatage():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# Verrou pour synchroniser l'accès à la console
console_lock = threading.Lock()

# Lancer l'encodage HandBrakeCLI pour un fichier


def lancer_encodage(dossier, fichier, preset):
    input_path = os.path.join(dossier, fichier)
    output_path = os.path.splitext(input_path)[0] + "_encoded.mp4"
    commande = [
        "HandBrakeCLI",
        "--preset-import-file", fichier_presets,
        "-i", input_path,
        "-o", output_path,
        "--preset", preset
    ]
    with console_lock:
        print(f"{horodatage()} 🚀 Lancement de l'encodage pour {
              fichier} avec le preset {preset}")
    try:
        process = subprocess.Popen(
            commande, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        last_percent_complete = -1
        percent_pattern = re.compile(r'Encoding:.*?(\d+\.\d+)\s?%')
        print("")  # Ajout d'une ligne avant la barre de progression
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
        print("")  # Ajout d'une ligne après la barre de progression
        process.wait()
        with console_lock:
            if process.returncode == 0:
                print(f"\n{horodatage()} ✅ Encodage terminé pour {
                      fichier} avec le preset {preset}")
            else:
                print(
                    f"\n{horodatage()} ❌ Erreur lors de l'encodage de {fichier}")
    except subprocess.CalledProcessError as e:
        with console_lock:
            print(f"\n{horodatage()} ❌ Erreur lors de l'encodage de {
                  fichier}: {e}")
            print(f"\n{horodatage()} ⚠️ Erreur de la commande : {e.stderr}")

# Fonction pour traiter la file d'attente d'encodage


def traitement_file_encodage(file_encodage):
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
