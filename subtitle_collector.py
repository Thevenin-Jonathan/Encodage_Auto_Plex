import os
import json
from datetime import datetime
from logger import setup_logger

# Configuration du logger
logger = setup_logger(__name__)


# Déterminer le chemin du dossier data
def get_data_dir():
    """Retourne le chemin du dossier data"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "datas")

    # Créer le dossier s'il n'existe pas
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        logger.debug(f"Dossier de données créé: {data_dir}")

    return data_dir


class SubtitleTitleCollector:
    """
    Classe qui collecte et enregistre les titres de sous-titres pour analyse future.
    Permet de sauvegarder les titres non encore rencontrés dans un fichier JSON.
    """

    def __init__(self, collection_filename="subtitle_titles_collection.json"):
        """
        Initialise le collecteur avec le fichier de collection spécifié.

        Args:
            collection_file: Chemin vers le fichier JSON de collection des titres
        """
        # Construire le chemin complet vers le fichier dans le dossier data
        data_dir = get_data_dir()
        self.collection_file = os.path.join(data_dir, collection_filename)
        self.titles = self._load_existing_titles()

    def _load_existing_titles(self):
        """Charge les titres existants à partir du fichier de collection"""
        if os.path.exists(self.collection_file):
            try:
                with open(self.collection_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(
                    f"Erreur lors du chargement des titres de sous-titres: {e}"
                )
                return {"titles": [], "metadata": {"last_updated": None}}
        else:
            return {"titles": [], "metadata": {"last_updated": None}}

    def save_title(self, title, language=None, additional_info=None):
        """
        Enregistre un titre de sous-titre s'il n'est pas déjà présent dans la collection.

        Args:
            title: Le titre du sous-titre à enregistrer
            language: La langue du sous-titre (optionnel)
            additional_info: Informations supplémentaires (optionnel)

        Returns:
            bool: True si le titre a été ajouté, False s'il existait déjà
        """
        if not title:
            return False

        # Vérifier si le titre existe déjà
        for item in self.titles["titles"]:
            if item["title"].lower() == title.lower():
                # Le titre existe déjà
                return False

        # Ajouter le nouveau titre
        title_info = {
            "title": title,
            "language": language,
            "first_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "additional_info": additional_info or {},
        }

        self.titles["titles"].append(title_info)
        self.titles["metadata"]["last_updated"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        self.titles["metadata"]["count"] = len(self.titles["titles"])

        # Enregistrer dans le fichier
        try:
            with open(self.collection_file, "w", encoding="utf-8") as f:
                json.dump(self.titles, f, ensure_ascii=False, indent=4)
            logger.debug(
                f"Nouveau titre de sous-titre ajouté à la collection: '{title}'"
            )
            return True
        except Exception as e:
            logger.error(f"Erreur lors de l'enregistrement du titre '{title}': {e}")
            return False


# Fonction simple pour une utilisation directe
def collect_subtitle_title(
    title,
    language=None,
    additional_info=None,
    collection_filename="subtitle_titles_collection.json",
):
    """
    Fonction pratique pour collecter un titre de sous-titre.

    Args:
        title: Le titre du sous-titre
        language: La langue du sous-titre (optionnel)
        additional_info: Informations supplémentaires (optionnel)
        collection_file: Chemin vers le fichier de collection

    Returns:
        bool: True si le titre a été ajouté, False s'il existait déjà ou en cas d'erreur
    """
    collector = SubtitleTitleCollector(collection_filename)
    return collector.save_title(title, language, additional_info)
