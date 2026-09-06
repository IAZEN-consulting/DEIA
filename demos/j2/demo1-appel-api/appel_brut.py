# /// script
# requires-python = ">=3.10"
# dependencies = ["openai>=1.30"]
# ///
"""Jour 2 - Démo 1 : appel API brut

Affiche la requête minimale et la réponse non mise en forme. L'intérêt est
dans les métadonnées : le bloc usage et finish_reason. Voir README.md.

    uv run appel_brut.py
"""

import json
import os

from openai import OpenAI

# OpenRouter expose une API compatible OpenAI : même SDK, autre base_url.
BASE_URL = "https://openrouter.ai/api/v1"
MODELE = "openai/gpt-4o-mini"
MESSAGES = [
    {"role": "system", "content": "Tu es concis. Trois phrases maximum."},
    {
        "role": "user",
        "content": "Explique ce qu'est une fenêtre de contexte à un développeur.",
    },
]
ENV = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
SORTIE = os.path.join(os.path.dirname(__file__), "sortie-enregistree.json")


def cle():
    """Clé lue dans l'environnement, sinon dans demos/.env."""
    valeur = os.environ.get("OPENROUTER_API_KEY")
    if not valeur and os.path.exists(ENV):
        for ligne in open(ENV, encoding="utf-8"):
            if ligne.startswith("OPENROUTER_API_KEY="):
                valeur = ligne.split("=", 1)[1].strip().strip("\"'")
    if not valeur:
        raise SystemExit("OPENROUTER_API_KEY absente : la définir dans demos/.env")
    return valeur


def bloc(titre):
    print("\n-- %s %s" % (titre, "-" * max(0, 72 - len(titre))))


bloc("Requête envoyée")
print(json.dumps({"model": MODELE, "messages": MESSAGES}, ensure_ascii=False, indent=2))

reponse = (
    OpenAI(api_key=cle(), base_url=BASE_URL)
    .chat.completions.create(model=MODELE, messages=MESSAGES)
    .model_dump()
)

bloc("Réponse brute")
print(json.dumps(reponse, ensure_ascii=False, indent=2, default=str)[:1800])

usage = reponse["usage"]
bloc("Ce qu'il faut regarder")
print(
    "  entrée %s + sortie %s = %s tokens facturés"
    % (usage["prompt_tokens"], usage["completion_tokens"], usage["total_tokens"])
)
print(
    "  finish_reason : %s   (stop = terminé, length = tronqué)"
    % reponse["choices"][0]["finish_reason"]
)

json.dump(
    reponse,
    open(SORTIE, "w", encoding="utf-8"),
    ensure_ascii=False,
    indent=2,
    default=str,
)
print("\nRéponse enregistrée dans %s" % os.path.basename(SORTIE))
