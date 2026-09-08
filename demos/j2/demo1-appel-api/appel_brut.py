# /// script
# requires-python = ">=3.10"
# dependencies = ["openai>=1.30"]
# ///
"""Jour 2 - Démo 1 : appel API brut
uv run appel_brut.py
"""

import json
import os
from pathlib import Path

from openai import OpenAI

MODELE = "gpt-4.1-nano-2025-04-14"
TEMPERATURE = 0.2
MESSAGES = [
    {"role": "system", "content": "Tu es concis. Trois phrases maximum."},
    {
        "role": "user",
        "content": "Explique ce qu'est une fenêtre de contexte à un développeur.",
    },
]
ENV = Path(__file__).resolve().parents[3] / ".env"
SORTIE = Path(__file__).with_name("sortie-enregistree.json")


def cle():
    """Clé lue dans l'environnement, sinon dans le .env à la racine du projet."""
    valeur = os.environ.get("OPENAI_API_KEY")
    if not valeur and ENV.exists():
        for ligne in ENV.read_text(encoding="utf-8").splitlines():
            if ligne.startswith("OPENAI_API_KEY="):
                valeur = ligne.split("=", 1)[1].strip().strip("\"'")
    if not valeur:
        raise SystemExit("OPENAI_API_KEY absente : la définir dans le .env à la racine")
    return valeur


def bloc(titre):
    print("\n-- %s %s" % (titre, "-" * max(0, 72 - len(titre))))


REQUETE = {"model": MODELE, "temperature": TEMPERATURE, "messages": MESSAGES}

bloc("Requête envoyée")
print(json.dumps(REQUETE, ensure_ascii=False, indent=2))

reponse = OpenAI(api_key=cle()).chat.completions.create(**REQUETE).model_dump()

bloc("Réponse brute")
print(json.dumps(reponse, ensure_ascii=False, indent=2, default=str)[:1800])

usage = reponse["usage"]

SORTIE.write_text(
    json.dumps(reponse, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
)
print("\nRéponse enregistrée dans %s" % SORTIE.name)
