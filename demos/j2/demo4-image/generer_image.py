# /// script
# requires-python = ">=3.10"
# dependencies = ["openai>=1.30"]
# ///
"""Jour 2 - Demo 4 : prompt court contre prompt detaille

Meme idee, deux prompts. Les images restent dans sorties/ et constituent le
plan B : cette demo est la seule qui ne peut pas etre rejouee sans elles,
donc la lancer une fois avant la session est obligatoire. Voir README.md.
"""
import base64
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import commun  # noqa: E402

SORTIES = os.path.join(os.path.dirname(__file__), "sorties")
MODELE = "dall-e-3"
PROMPTS = [
    ("1-prompt-court.png", "Un poste de travail de developpeur."),
    ("2-prompt-detaille.png",
     "Un poste de travail de developpeur photographie de trois quarts, "
     "lumiere naturelle rasante de fin de journee venant d'une fenetre a "
     "gauche, palette sobre en bois clair et gris ardoise, un seul ecran "
     "allume affichant du code, bureau range, faible profondeur de champ, "
     "style photographie editoriale, format paysage."),
]


def collecte():
    from openai import OpenAI
    client = OpenAI(api_key=commun.cle())
    os.makedirs(SORTIES, exist_ok=True)
    revus = {}
    for nom, prompt in PROMPTS:
        r = client.images.generate(model=MODELE, prompt=prompt, n=1,
                                   size="1024x1024", response_format="b64_json")
        open(os.path.join(SORTIES, nom), "wb").write(
            base64.b64decode(r.data[0].b64_json))
        revus[nom] = getattr(r.data[0], "revised_prompt", None)
    return revus


def montre(revus):
    for nom, prompt in PROMPTS:
        commun.bloc("%s (%d caracteres)" % (nom, len(prompt)))
        print("  " + prompt)
        if revus.get(nom):
            print("  prompt reecrit par le service :\n  " + revus[nom])


if __name__ == "__main__":
    # Plan B specifique : des fichiers PNG, pas un rejeu JSON.
    if "--live" in sys.argv:
        commun.lancer(__doc__, os.devnull, collecte, montre, deps=("openai",))
        print("\nImages dans %s" % SORTIES)
    else:
        images = sorted(f for f in os.listdir(SORTIES)) if os.path.isdir(SORTIES) else []
        montre({})
        commun.bloc("Plan B")
        print("  " + ("\n  ".join(images) if images else
                      "Aucune image. Lancer avant la session :\n  "
                      + commun.cmd(" --live")))
