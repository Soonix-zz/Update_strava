#!/bin/bash
# Aller dans le répertoire du script
cd "$(dirname "$0")"

# Charger l'environnement virtuel (si vous en créez un sur le NAS)
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Lancer la synchro
python3 main.py
