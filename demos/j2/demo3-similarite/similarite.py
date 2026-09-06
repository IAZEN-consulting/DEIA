# /// script
# requires-python = ">=3.10"
# dependencies = ["langchain-chroma>=0.1", "langchain-openai>=0.2", "chromadb>=0.5"]
# ///
"""Jour 2 - Demo 3 : recherche par similarite

Chaque question est formulee sans aucun mot commun avec le document attendu.
Le script l'affiche pour le prouver a l'ecran. Chez Chroma le score est une
distance : plus il est bas, plus le document est proche. Voir README.md.
"""
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
import commun  # noqa: E402

REF = os.path.join(os.path.dirname(__file__), "sortie-enregistree.json")
CORPUS = os.path.join(os.path.dirname(__file__), "..", "corpus")
EMBEDDING = "text-embedding-3-small"

QUESTIONS = [
    ("Combien de temps puis-je rester chez moi pour bosser ?", "teletravail"),
    ("Quel est le montant maximum rembourse pour dormir a l'hotel ?",
     "notes-de-frais"),
    ("Suis-je paye si je dois me lever a 3h du matin pour reparer un serveur ?",
     "astreinte"),
]

VIDES = set("""le la les un une des du de a au aux et ou en dans pour par sur je
tu il on nous vous ils est sont ai as ont que qui quoi quel quelle mon ma mes ce
cette ces se sa son ses puis plus moins si ne pas me te lui leur combien temps
chez suis dois""".split())


def mots(texte):
    return set(m for m in re.findall(r"[a-zA-Zàâçéèêëîïôûùüÿñ]{3,}",
                                     texte.lower()) if m not in VIDES)


def corpus():
    return [(n[:-4], open(os.path.join(CORPUS, n), encoding="utf-8").read())
            for n in sorted(os.listdir(CORPUS)) if n.endswith(".txt")]


def collecte():
    from langchain_chroma import Chroma
    from langchain_openai import OpenAIEmbeddings
    docs = corpus()
    base = Chroma.from_texts(
        texts=[t for _, t in docs],
        metadatas=[{"source": n} for n, _ in docs],
        embedding=OpenAIEmbeddings(model=EMBEDDING, api_key=commun.cle()),
        collection_name="procedures_demo")
    return {"documents": [n for n, _ in docs],
            "questions": [{"question": q, "attendu": a,
                           "resultats": [(d.metadata["source"], float(s))
                                         for d, s in
                                         base.similarity_search_with_score(q, k=3)]}
                          for q, a in QUESTIONS]}


def montre(d):
    commun.bloc("Corpus indexe (%s)" % EMBEDDING)
    print("  " + ", ".join(d["documents"]))
    textes = dict(corpus())
    for q in d["questions"]:
        commun.bloc(q["question"])
        premier = q["resultats"][0][0]
        communs = mots(q["question"]) & mots(textes.get(premier, ""))
        print("  mots partages avec le document trouve : %s"
              % (", ".join(sorted(communs)) or "AUCUN"))
        for source, score in q["resultats"]:
            print("    %-24s %.4f%s"
                  % (source, score, "   <-- attendu" if source == q["attendu"] else ""))


if __name__ == "__main__":
    commun.lancer(__doc__, REF, collecte, montre,
                  deps=("langchain_chroma", "langchain_openai", "chromadb"))
