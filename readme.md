# Encodage_Auto_Plex

![Logo de l'application](images/ico.ico)

## Description

**Encodage_Auto_Plex** est une application de bureau qui automatise le processus de ré-encodage des fichiers vidéo pour une utilisation optimale avec Plex. Elle surveille les dossiers configurés, détecte automatiquement les fichiers vidéo et les encode selon des préréglages spécifiques adaptés à différents types de contenus (films, séries, dessins animés, mangas).

L'application offre une analyse intelligente des sous-titres et des pistes audio, une interface utilisateur intuitive et une surveillance automatique des dossiers pour un flux de travail sans intervention.

## Fonctionnalités principales

- **Surveillance automatique de dossiers** : Analyse les dossiers configurés à la recherche de nouveaux fichiers vidéo à encoder
- **Préréglages par type de contenu** : Applique des paramètres d'encodage spécifiques selon le type de contenu (films, séries, dessins animés, mangas)
- **Analyse intelligente des sous-titres** : Détecte et traite correctement les sous-titres français dans différentes variantes (France, Québec, Suisse, Belgique)
- **Sélection intelligente des pistes audio** : Identifie et sélectionne automatiquement les meilleures pistes audio françaises et originales
- **Interface graphique moderne** : Interface intuitive avec thème sombre et visualisation en temps réel du processus d'encodage
- **Historique d'encodage** : Suivi des encodages précédents avec informations détaillées (taille, date, paramètres)
- **File d'attente personnalisable** : Possibilité de réorganiser, suspendre ou annuler les encodages en attente
- **Encodage manuel** : Ajout de fichiers spécifiques à la file d'attente d'encodage avec préréglage au choix
- **Notifications système** : Alertes intégrées pour les événements importants (début/fin d'encodage, erreurs)
- **Journalisation détaillée** : Système de logs complet pour le suivi et le dépannage
- **Reprise après interruption** : Capacité à reprendre les encodages interrompus lors d'une fermeture imprévue

## Prérequis

- Windows 10 ou supérieur
- Python 3.12 ou supérieur
- HandBrake CLI (doit être installé et accessible via le PATH système)
- MediaInfo (inclus ou accessible via le PATH système)

## Installation

### Installation via l'exécutable

1. Téléchargez la dernière version de l'exécutable depuis la section Releases
2. Exécutez le fichier d'installation et suivez les instructions
3. Lancez l'application depuis le menu Démarrer ou le raccourci créé sur le bureau

### Installation depuis les sources

1. Clonez le dépôt Git :

```bash
git clone https://github.com/votre-username/Encodage_handler.git
```

2. Installez les dépendances requises :

```bash
cd Encodage_handler
pip install -r requirements.txt
```

3. Lancez l'application :

```bash
python main.py
```

## Configuration

### Configuration des dossiers

La configuration des dossiers surveillés et de leurs préréglages associés s'effectue dans le fichier constants.py :

```python
dossiers_presets = {
    "D:/Torrents/Dessins animes VF": "Dessins animes VF",
    "D:/Torrents/Films": "1080p HD-Light 1500kbps",
    "D:/Torrents/Manga": "Mangas MULTI 1000kbps",
    "D:/Torrents/Manga_VO": "Mangas VO 1000kbps",
    "D:/Torrents/Series": "1080p HD-Light 1500kbps",
}
```

### Configuration des dossiers de sortie par dossier source

**🆕 NOUVELLE FONCTIONNALITÉ** : Chaque dossier surveillé peut maintenant avoir son propre dossier de sortie correspondant !

#### Principe de fonctionnement

Le système fonctionne maintenant avec une correspondance directe entre les dossiers surveillés et les dossiers de sortie :

- `D:/Torrents/Film VF` → `D:/Ripped/Film VF`
- `D:/Torrents/Dessins animes VF` → `D:/Ripped/Dessins animes VF`
- `D:/Torrents/Mangas VO` → `D:/Ripped/Mangas VO`
- etc.

#### Via l'interface graphique (Recommandé)

1. Lancez l'application
2. Cliquez sur le bouton **"Configurer dossiers sortie"** dans l'interface principale
3. Dans la fenêtre qui s'ouvre :
   - Chaque dossier source surveillé est listé avec son dossier de sortie actuel
   - Cliquez sur **"Parcourir"** pour changer le dossier de sortie d'un dossier source
   - Utilisez **"Réinitialiser"** pour revenir aux valeurs par défaut
   - Cliquez sur **"Sauvegarder"** pour appliquer les changements

#### Configuration manuelle

La configuration est stockée dans le fichier `datas/config.json` :

```json
{
  "notifications_enabled": true,
  "dossiers_sortie_surveillance": {
    "D:/Torrents/Dessins animes VF": "D:/Ripped/Dessins animes VF",
    "D:/Torrents/Film VF": "D:/Ripped/Film VF",
    "D:/Torrents/Film Jeunes VF": "D:/Ripped/Film Jeunes VF",
    "D:/Torrents/Series VF": "D:/Ripped/Series VF",
    "D:/Torrents/Film MULTI": "D:/Ripped/Film MULTI",
    "D:/Torrents/Film Jeunes MULTI": "D:/Ripped/Film Jeunes MULTI",
    "D:/Torrents/Series MULTI": "D:/Ripped/Series MULTI",
    "D:/Torrents/Mangas MULTI": "D:/Ripped/Mangas MULTI",
    "D:/Torrents/Mangas VO": "D:/Ripped/Mangas VO",
    "D:/Torrents/Film 4K": "D:/Ripped/Film 4K",
    "D:/Torrents/Serie 4K": "D:/Ripped/Serie 4K"
  }
}
```

#### Configuration par défaut

Si aucune configuration spécifique n'est définie, les valeurs par défaut dans `constants.py` sont utilisées :

```python
# Configuration des dossiers de sortie pour chaque dossier surveillé
dossiers_sortie_surveillance = {
    "D:/Torrents/Dessins animes VF": "D:/Ripped/Dessins animes VF",
    "D:/Torrents/Film VF": "D:/Ripped/Film VF",
    "D:/Torrents/Film Jeunes VF": "D:/Ripped/Film Jeunes VF",
    "D:/Torrents/Series VF": "D:/Ripped/Series VF",
    "D:/Torrents/Film MULTI": "D:/Ripped/Film MULTI",
    "D:/Torrents/Film Jeunes MULTI": "D:/Ripped/Film Jeunes MULTI",
    "D:/Torrents/Series MULTI": "D:/Ripped/Series MULTI",
    "D:/Torrents/Mangas MULTI": "D:/Ripped/Mangas MULTI",
    "D:/Torrents/Mangas VO": "D:/Ripped/Mangas VO",
    "D:/Torrents/Film 4K": "D:/Ripped/Film 4K",
    "D:/Torrents/Serie 4K": "D:/Ripped/Serie 4K",
}

# Dossier de sortie par défaut (pour compatibilité)
dossier_sortie = "D:/Ripped"
```

⚠️ **Important** : Les dossiers de sortie sont créés automatiquement au démarrage de l'application.### Préréglages d'encodage

Les préréglages d'encodage sont définis dans le fichier custom_presets.json. Ils peuvent être modifiés directement dans ce fichier ou créés via l'interface HandBrake GUI puis exportés et intégrés à l'application.

## Utilisation

### Interface principale

L'interface principale comporte plusieurs zones fonctionnelles :

- **Panneau central** : Affichage de la file d'attente et de l'encodage en cours
- **Panneau d'historique** : Visualisation des encodages précédents (accessible via le bouton "Historique des encodages")
- **Panneau de logs** : Affichage des messages système et des informations de débogage
- **Barre de contrôles** : Boutons pour suspendre, sauter ou annuler les encodages

### Contrôles d'encodage

- **Pause** : Suspend temporairement l'encodage en cours
- **Ignorer** : Passe à l'élément suivant dans la file d'attente
- **Arrêter tout** : Annule tous les encodages et vide la file d'attente

### Gestion de la file d'attente

- **Réorganiser** : Déplacez les éléments dans la file d'attente en utilisant les boutons fléchés
- **Supprimer** : Retirez un élément spécifique de la file d'attente
- **Vider** : Supprimez tous les éléments de la file d'attente

### Encodage manuel

Pour ajouter manuellement un fichier à la file d'attente :

1. Placez le fichier dans le dossier configuré pour l'encodage manuel (Encodage_manuel par défaut)
2. Le fichier sera détecté et ajouté à la liste des encodages manuels dans l'interface
3. Sélectionnez le préréglage souhaité et lancez l'encodage

## Fonctionnalités détaillées

### Analyse des sous-titres

L'application analyse en profondeur les pistes de sous-titres pour :

- Identifier les sous-titres français dans leurs différentes variantes régionales
- Distinguer les sous-titres standards des sous-titres pour malentendants (SDH)
- Différencier les sous-titres verbaux (dialogues complets) des sous-titres non-verbaux (traductions, effets)
- Prioriser les sous-titres selon leur pertinence pour le contenu

### Sélection des pistes audio

Le système sélectionne intelligemment les meilleures pistes audio en :

- Priorisant les pistes françaises pour les préréglages FR
- Priorisant les pistes originales pour les préréglages VO
- Excluant les pistes d'audiodescription et autres pistes spéciales
- Conservant plusieurs pistes audio lorsque cela est pertinent

### Journalisation

L'application maintient plusieurs types de journaux :

- **Logs en temps réel** : Affichés dans l'interface pendant l'exécution
- **Logs archivés** : Accessibles via le bouton "Charger ancien log" dans l'interface
- **Fichiers de logs** : Stockés dans le dossier logs pour référence ultérieure

## Dépannage

### HandBrakeCLI non trouvé

Si l'application signale que HandBrakeCLI n'est pas installé :

1. Téléchargez HandBrakeCLI depuis [le site officiel](https://handbrake.fr/downloads2.php)
2. Installez-le et assurez-vous qu'il est accessible via le PATH système
3. Redémarrez l'application

### Problèmes d'analyse des sous-titres

Si l'analyse des sous-titres ne fonctionne pas correctement :

1. Vérifiez que MediaInfo est correctement installé
2. Assurez-vous que le fichier contient des sous-titres dans des formats standards
3. Consultez les logs pour des informations détaillées sur l'analyse

### Encodages interrompus

Si l'application se ferme de manière inattendue pendant un encodage :

1. Redémarrez l'application
2. Une boîte de dialogue vous proposera de reprendre les encodages interrompus
3. Choisissez "Oui" pour continuer là où vous vous étiez arrêté

## Structure du projet

```
Encodage_handler/
├── datas/
│   ├── config.json                # Configuration utilisateur
│   ├── custom_presets.json        # Préréglages d'encodage HandBrake
│   ├── fichiers_detectes.json     # Suivi des fichiers détectés
│   ├── fichiers_encodes.json      # Suivi des fichiers encodés
│   └── successful_encodings.json  # Historique des encodages réussis
├── images/
│   └── ico.ico                    # Icône de l'application
├── logs/                          # Dossier des fichiers de logs
├── tests/                         # Tests unitaires
├── audio_selection.py             # Module de sélection des pistes audio
├── command_builder.py             # Constructeur de commandes HandBrake
├── config.py                      # Gestion de la configuration
├── constants.py                   # Constantes et chemins
├── encoding.py                    # Logique d'encodage
├── file_handling.py               # Gestion des fichiers
├── file_operations.py             # Opérations sur les fichiers
├── gui.py                         # Interface utilisateur
├── initialization.py              # Initialisation de l'application
├── logger.py                      # Configuration des logs
├── main.py                        # Point d'entrée principal
├── notifications.py               # Système de notifications
├── resume_dialog.py               # Dialogue de reprise des encodages
├── state_persistence.py           # Persistance de l'état
├── subtitle_analyzer.py           # Analyse des sous-titres
├── subtitle_selection.py          # Sélection des sous-titres
├── surveillance.py                # Surveillance des dossiers
├── successful_encodings.py        # Gestion des encodages réussis
├── utils.py                       # Fonctions utilitaires
└── requirements.txt               # Dépendances Python
```

## Contribution

Les contributions sont les bienvenues ! Pour contribuer au projet :

1. Forkez le dépôt
2. Créez une branche pour votre fonctionnalité (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Committez vos changements (`git commit -m 'Ajout d'une nouvelle fonctionnalité'`)
4. Poussez vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Ouvrez une Pull Request

## Licence

Ce projet est distribué sous licence MIT. Voir le fichier `LICENSE` pour plus d'informations.

## Remerciements

- [HandBrake](https://handbrake.fr/) pour leur excellent outil d'encodage vidéo
- [MediaInfo](https://mediaarea.net/fr/MediaInfo) pour l'analyse des fichiers médias
- [PyQt5](https://www.riverbankcomputing.com/software/pyqt/) pour le framework d'interface graphique
- [QDarkStyle](https://github.com/ColinDuquesnoy/QDarkStyle) pour le thème sombre de l'interface

---

_Développé avec ❤️ pour optimiser votre médiathèque Plex_
