#!/bin/bash

# Créer un environnement virtuel
python3 -m venv venv

# Activer l'environnement virtuel
source venv/bin/activate

# Installer les bibliothèques Python
pip install -r requirements.txt

