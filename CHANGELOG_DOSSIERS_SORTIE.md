# Modifications apportées : Dossiers de sortie par dossier source

## Résumé des changements

Cette modification permet maintenant d'avoir un dossier de sortie différent pour chaque dossier surveillé, au lieu d'un seul dossier global. Chaque dossier dans `D:/Torrents` a son propre dossier correspondant dans `D:/Ripped`.

## Principe de fonctionnement

- `D:/Torrents/Film VF` → `D:/Ripped/Film VF`
- `D:/Torrents/Dessins animes VF` → `D:/Ripped/Dessins animes VF`
- `D:/Torrents/Mangas VO` → `D:/Ripped/Mangas VO`
- etc.

## Fichiers modifiés

### 1. `constants.py`

- **Modification** : `dossiers_sortie_presets` remplacé par `dossiers_sortie_surveillance`
- **Ajout** : Dictionnaire associant chaque dossier source à son dossier de sortie correspondant

### 2. `utils.py`

- **Ajout** : `obtenir_dossier_sortie_dossier_source(dossier_source)` - Fonction principale pour obtenir le dossier de sortie
- **Modification** : `obtenir_dossier_sortie_preset()` marquée comme DEPRECATED

### 3. `config.py`

- **Modification** : `DEFAULT_CONFIG` inclut maintenant `dossiers_sortie_surveillance`
- **Ajout** : `get_output_directories_for_surveillance()` - Récupère tous les dossiers de sortie configurés
- **Ajout** : `update_output_directory_for_source()` - Met à jour le dossier d'un dossier source
- **Ajout** : `get_output_directory_for_source_folder()` - Récupère le dossier d'un dossier source spécifique
- **Modification** : Anciennes fonctions basées sur les presets marquées comme DEPRECATED

### 4. `encoding.py`

- **Modification** : `lancer_encodage_avec_gui()` utilise maintenant le dossier source au lieu du preset
- **Ajout** : Paramètre `dossier_source` dans la fonction
- **Modification** : Import de `obtenir_dossier_sortie_dossier_source` au lieu de `obtenir_dossier_sortie_preset`

### 5. `file_operations.py`

- **Modification** : `verifier_dossiers()` crée maintenant tous les dossiers basés sur `dossiers_sortie_surveillance`
- **Modification** : Import de `dossiers_sortie_surveillance` au lieu de `dossiers_sortie_presets`

### 6. `gui.py`

- **Modification** : `OutputDirectoriesDialog` affiche maintenant les dossiers sources au lieu des presets
- **Modification** : Interface mise à jour avec "Dossier source" au lieu de "Preset"
- **Modification** : Utilisation des nouvelles fonctions de configuration

### 7. `datas/config.json`

- **Modification** : Section `dossiers_sortie_surveillance` remplace `dossiers_sortie_presets`
- **Ajout** : Configuration de tous les dossiers sources avec leurs dossiers de sortie correspondants

### 8. `readme.md`

- **Mise à jour** : Documentation complète de la nouvelle fonctionnalité basée sur les dossiers sources

## Fonctionnalités ajoutées

### Interface graphique

- **Mise à jour du bouton** dans l'interface principale pour configurer les dossiers de sortie
- **Fenêtre de configuration mise à jour** avec :
  - Liste de tous les dossiers sources et leurs dossiers de sortie
  - Boutons "Parcourir" pour changer chaque dossier
  - Bouton "Réinitialiser" pour revenir aux valeurs par défaut
  - Sauvegarde automatique de la configuration

### Gestion automatique

- **Création automatique** des dossiers de sortie basés sur les dossiers sources
- **Mapping direct** entre dossier source et dossier de sortie
- **Fallback intelligent** vers le dossier par défaut si un dossier source n'a pas de configuration
- **Persistance** de la configuration dans `config.json`

## Compatibilité

### Rétrocompatibilité

- ✅ L'ancien système continue de fonctionner via les fonctions DEPRECATED
- ✅ Le dossier `D:/Ripped` reste le fallback par défaut
- ✅ Aucune modification de l'interface utilisateur existante (à part la fenêtre de configuration)

### Configuration par défaut

Les dossiers suivants sont créés automatiquement :

- `D:/Ripped/Dessins animes VF` ← `D:/Torrents/Dessins animes VF`
- `D:/Ripped/Film VF` ← `D:/Torrents/Film VF`
- `D:/Ripped/Film Jeunes VF` ← `D:/Torrents/Film Jeunes VF`
- `D:/Ripped/Series VF` ← `D:/Torrents/Series VF`
- `D:/Ripped/Film MULTI` ← `D:/Torrents/Film MULTI`
- `D:/Ripped/Film Jeunes MULTI` ← `D:/Torrents/Film Jeunes MULTI`
- `D:/Ripped/Series MULTI` ← `D:/Torrents/Series MULTI`
- `D:/Ripped/Mangas MULTI` ← `D:/Torrents/Mangas MULTI`
- `D:/Ripped/Mangas VO` ← `D:/Torrents/Mangas VO`
- `D:/Ripped/Film 4K` ← `D:/Torrents/Film 4K`
- `D:/Ripped/Serie 4K` ← `D:/Torrents/Serie 4K`

## Utilisation

1. **Interface graphique** : Cliquer sur "Configurer dossiers sortie" dans l'interface principale
2. **Configuration manuelle** : Modifier le fichier `datas/config.json`
3. **Par code** : Utiliser les nouvelles fonctions dans `config.py` et `utils.py`

## Tests

La fonctionnalité a été testée et validée :

- ✅ Création automatique des dossiers basés sur les dossiers sources
- ✅ Sauvegarde et chargement de la configuration
- ✅ Interface graphique fonctionnelle
- ✅ Encodage avec les bons dossiers de sortie
- ✅ Mapping correct dossier source → dossier sortie
- ✅ Gestion du fallback

---

_Modification terminée - L'application utilise maintenant un mapping direct entre dossiers source et dossiers de sortie !_
