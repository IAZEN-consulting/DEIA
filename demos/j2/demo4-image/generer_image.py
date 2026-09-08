# /// script
# requires-python = ">=3.10"
# dependencies = ["openai>=1.30"]
# ///
"""Jour 2 - Demo 4 : prompt court contre prompt detaille

Meme idee, deux prompts. Les images restent dans sorties/ et constituent le
plan B : cette demo est la seule qui ne peut pas etre rejouee sans elles,
donc la lancer une fois avant la session est obligatoire.
"""

import base64
import os
import sys
from pathlib import Path

SORTIES = os.path.join(os.path.dirname(__file__), "sorties")
MODELE = "gpt-image-1-mini"
ENV = Path(__file__).resolve().parents[3] / ".env"
PROMPTS = [
    (
        "1-prompt-detaille.png",
        "Photographie éditoriale réaliste d'un développeur d'environ 28 ans, attentif, codant sur un ordinateur portable avec un second écran affichant des workflows d'intégration d'IA, assis dans une salle de formation tech moderne et lumineuse. En arrière-plan flou, un formateur présente des schémas techniques sur un grand écran interactif. Plan moyen, objectif 50mm, f/2.2, faible profondeur de champ, lumière naturelle douce complétée par la lueur subtile des écrans, couleurs neutres et modernes. Rendu très détaillé, textures naturelles de peau et de tissu, ambiance professionnelle et crédible. Sans hologrammes futuristes, sans néons criards, sans déformations des mains ni sourires artificiels de banque d'images.",
    ),
]


def cle():
    """Cle lue dans l'environnement, sinon dans le .env a la racine du projet."""
    valeur = os.environ.get("OPENAI_API_KEY")
    if not valeur and ENV.exists():
        for ligne in ENV.read_text(encoding="utf-8").splitlines():
            if ligne.startswith("OPENAI_API_KEY="):
                valeur = ligne.split("=", 1)[1].strip().strip("\"'")
    if not valeur:
        raise SystemExit("OPENAI_API_KEY absente : la definir dans le .env a la racine")
    return valeur


def bloc(titre):
    print("\n-- %s %s" % (titre, "-" * max(0, 72 - len(titre))))


def collecte():
    from openai import OpenAI

    client = OpenAI(api_key=cle())
    os.makedirs(SORTIES, exist_ok=True)
    revus = {}
    for nom, prompt in PROMPTS:
        # quality="low" + 1024x1024 : tarif minimal de gpt-image-1-mini.
        # Ce modele repond toujours en b64_json, sans revised_prompt.
        r = client.images.generate(
            model=MODELE,
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="low",
        )
        image = r.data[0]
        open(os.path.join(SORTIES, nom), "wb").write(base64.b64decode(image.b64_json))
        revus[nom] = getattr(image, "revised_prompt", None)
    return revus


def montre(revus):
    for nom, prompt in PROMPTS:
        bloc("%s (%d caracteres)" % (nom, len(prompt)))
        print("  " + prompt)
        if revus.get(nom):
            print("  prompt reecrit par le service :\n  " + revus[nom])


if __name__ == "__main__":
    # Plan B specifique : des fichiers PNG, pas un rejeu JSON.
    if "--live" in sys.argv:
        montre(collecte())
        print("\nImages dans %s" % SORTIES)
    else:
        images = (
            sorted(f for f in os.listdir(SORTIES)) if os.path.isdir(SORTIES) else []
        )
        montre({})
        bloc("Plan B")
        print(
            "  "
            + (
                "\n  ".join(images)
                if images
                else "Aucune image. Lancer avant la session :\n  "
                "uv run generer_image.py --live"
            )
        )
