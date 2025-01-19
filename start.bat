@echo off
:: Lancer le script Python dans PowerShell

:: Chemin du script Python
set SCRIPT_PATH="C:\Users\warzo\OneDrive\Documents\PLEX\Encodage_handler\main.py"

:: Lancer PowerShell et exécuter le script Python
powershell -Command "python %SCRIPT_PATH%"

:: Ajouter une pause à la fin pour garder la fenêtre ouverte
pause