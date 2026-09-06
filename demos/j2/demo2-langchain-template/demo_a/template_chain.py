# /// script
# requires-python = ">=3.10"
# dependencies = ["langchain>=0.3", "langchain-openai>=0.2"]
# ///
"""Jour 2 - Démo 2 : prompt template et chaîne

Un gabarit écrit une fois, trois jeux de paramètres. Les appels 1 et 2 ne
diffèrent que par le ton, les appels 1 et 3 que par le produit. Voir README.md.

    uv run template_chain.py
"""

import json
import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# OpenRouter expose une API compatible OpenAI : même client, autre base_url.
BASE_URL = "https://openrouter.ai/api/v1"
MODELE = "minimax/minimax-m3:free"
GABARIT = (
    "Rédige une description commerciale de deux phrases pour ce produit.\n"
    "Ton : {ton}.\nProduit : {nom}\nCaractéristiques : {caracteristiques}"
)
JEUX = [
    {
        "nom": "Sac à dos Trek 30L",
        "ton": "sobre et factuel",
        "caracteristiques": "imperméable, 30 litres, 900 grammes",
    },
    {
        "nom": "Sac à dos Trek 30L",
        "ton": "enthousiaste",
        "caracteristiques": "imperméable, 30 litres, 900 grammes",
    },
    {
        "nom": "Lampe frontale Nyx",
        "ton": "sobre et factuel",
        "caracteristiques": "350 lumens, autonomie 40 heures, 78 grammes",
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


bloc("Gabarit, écrit une seule fois")
print(GABARIT)

# Le gabarit et le modèle sont assemblés une fois : c'est la chaîne. Seuls
# les paramètres changent ensuite, jamais le texte du prompt.
chaine = ChatPromptTemplate.from_template(GABARIT) | ChatOpenAI(
    model=MODELE, temperature=0, api_key=cle(), base_url=BASE_URL
)

resultats = []
for numero, jeu in enumerate(JEUX, 1):
    reponse = chaine.invoke(jeu).content
    resultats.append({"parametres": jeu, "reponse": reponse})
    bloc("Appel %d : %s, ton %s" % (numero, jeu["nom"], jeu["ton"]))
    print("  " + reponse.replace("\n", "\n  "))

json.dump(
    {"resultats": resultats},
    open(SORTIE, "w", encoding="utf-8"),
    ensure_ascii=False,
    indent=2,
)
print("\nRéponses enregistrées dans %s" % os.path.basename(SORTIE))
