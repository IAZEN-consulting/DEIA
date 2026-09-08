# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "langchain-chroma>=0.1",
#     "langchain-openai>=0.2",
#     "chromadb>=0.5",
#     "python-dotenv>=1.0",
# ]
# ///
"""Jour 2 - Démo 3 : recherche lexicale (BM25) contre recherche vectorielle.

Lancement :
    uv run demo-rag.py --sim     recherche vectorielle seule (défaut)
    uv run demo-rag.py --bm25    recherche lexicale seule, aucun appel API
    uv run demo-rag.py --hyb     les deux, plus une fusion des deux classements

La clé OpenAI est lue dans le fichier .env placé à la racine du projet. Elle
n'est demandée que si le mode choisi en a besoin : --bm25 tourne hors ligne.

Ce que la démo veut montrer
---------------------------
Les questions sont écrites sans reprendre le vocabulaire du document qu'elles
doivent retrouver.

BM25 compte des mots : si la question et le document n'ont aucun terme en
commun, il ne remonte rien du tout. C'est le comportement de Ctrl+F, d'un LIKE
en SQL ou d'un index Elasticsearch classique.

La recherche vectorielle compare du sens : chaque texte devient un vecteur de
nombres, et on cherche les vecteurs les plus proches.

Le mode --hyb affiche les deux côte à côte et les fusionne.

Piège classique du score
------------------------
Les trois classements ne se lisent pas dans le même sens :
    BM25       score élevé  = meilleur (0 = aucun mot commun)
    vectoriel  distance basse = meilleur
    RRF        score élevé  = meilleur
Et aucune de ces valeurs ne se compare d'une question à l'autre.
"""

import argparse
import math
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# 0. Configuration
# ---------------------------------------------------------------------------

DOSSIER = Path(__file__).resolve().parent
CORPUS = DOSSIER.parent / "corpus"  # dossier contenant les .txt
MODELE_EMBEDDING = "text-embedding-3-small"  # 1536 dimensions, peu coûteux
NB_RESULTATS = 3  # top-k affiché

# Paramètres BM25, valeurs standard de la littérature.
# K1 borne l'effet de la répétition d'un mot : au-delà, répéter n'aide plus.
# B règle la pénalité de longueur : 0 = ignorer la longueur, 1 = la corriger
# entièrement. Un document long a mécaniquement plus de chances de contenir le
# mot cherché, B compense ce biais.
BM25_K1 = 1.5
BM25_B = 0.75

# Constante de la fusion RRF. Plus elle est grande, plus l'écart entre le 1er
# et le 2e de chaque classement compte peu. 60 est la valeur de l'article
# d'origine (Cormack et al., 2009).
RRF_K = 60

# Question posée, et nom du document que l'on s'attend à voir remonter.
QUESTIONS = [
    (
        "Combien de jours de télétravail sont autorisés par semaine ?",
        "teletravail",
    ),
    (
        "Quel est le plafond de remboursement pour une nuitée à Paris ?",
        "notes-de-frais",
    ),
    (
        "Quelle est la compensation pour une semaine d'astreinte ?",
        "astreinte",
    ),
]

# Mots outils ignorés à la tokenisation : ils apparaissent partout et ne
# discriminent rien. BM25 leur donnerait de toute façon un poids quasi nul via
# l'IDF, mais les retirer rend la liste des mots partagés lisible.
MOTS_VIDES = set(
    """
    le la les un une des du de a au aux et ou en dans pour par sur je tu il on
    nous vous ils est sont ai as ont que qui quoi quel quelle mon ma mes ce
    cette ces se sa son ses puis plus moins si ne pas me te lui leur combien
    temps chez suis dois
    """.split()
)


# ---------------------------------------------------------------------------
# 1. Utilitaires
# ---------------------------------------------------------------------------


def titre(texte: str) -> None:
    """Affiche un titre de section, pour rendre la sortie console lisible."""
    print("\n" + texte)
    print("-" * len(texte))


def sans_accents(texte: str) -> str:
    """Retire les accents : "remboursé" et "rembourse" deviennent le même mot.

    Sans cette normalisation, la comparaison lexicale serait artificiellement
    favorable : elle compterait "payé" et "paye" comme deux mots
    différents, et conclurait à tort qu'aucun terme n'est partagé.
    """
    decompose = unicodedata.normalize("NFD", texte)
    return "".join(c for c in decompose if unicodedata.category(c) != "Mn")


def tokeniser(texte: str) -> list[str]:
    """Découpe un texte en mots comparables : minuscules, sans accents,
    au moins 3 lettres, hors mots outils.

    C'est la vision qu'un moteur lexical a d'un texte. Aucune racinisation
    n'est appliquée : "serveur" et "serveurs" restent deux tokens distincts,
    ce qui est une des faiblesses de l'approche.
    """
    mots = re.findall(r"[a-z]{3,}", sans_accents(texte.lower()))
    return [mot for mot in mots if mot not in MOTS_VIDES]


def charger_env() -> Path | None:
    """Charge le .env du projet et renvoie son chemin, ou None s'il n'existe pas.

    On part du dossier du script et on remonte les parents un à un.
    """
    from dotenv import load_dotenv

    for dossier in (DOSSIER, *DOSSIER.parents):
        fichier = dossier / ".env"
        if fichier.is_file():
            # override=False : une variable déjà exportée dans le shell garde
            # la priorité sur celle du fichier.
            load_dotenv(fichier, override=False)
            return fichier
    return None


def verifier_cle() -> None:
    """Vérifie la présence de la clé OpenAI, ou s'arrête avec un message clair."""
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit(
            "Clé OPENAI_API_KEY introuvable.\n"
            "Ajouter cette ligne dans le fichier .env à la racine du projet :\n"
            "    OPENAI_API_KEY=sk-...\n"
            "Ou lancer la démo en mode hors ligne : uv run demo-rag.py --bm25"
        )


def charger_corpus() -> list[tuple[str, str]]:
    """Lit tous les .txt du dossier corpus et renvoie [(nom, contenu), ...]."""
    if not CORPUS.is_dir():
        sys.exit(f"Dossier corpus introuvable : {CORPUS}")
    fichiers = sorted(CORPUS.glob("*.txt"))
    if not fichiers:
        sys.exit(f"Aucun fichier .txt dans {CORPUS}")
    return [(f.stem, f.read_text(encoding="utf-8")) for f in fichiers]


# ---------------------------------------------------------------------------
# 2. Moteur lexical : BM25
# ---------------------------------------------------------------------------


def indexer_bm25(documents: list[tuple[str, str]]) -> dict:
    """Construit l'index lexical : tokens par document, longueur moyenne, IDF.

    L'IDF (inverse document frequency) donne du poids aux mots rares. Un mot
    présent dans les six documents n'aide à distinguer personne, un mot présent
    dans un seul document est très discriminant.

        idf(mot) = ln(1 + (N - n + 0.5) / (n + 0.5))

    où N est le nombre de documents et n le nombre de documents contenant le
    mot. Le +1 dans le logarithme garantit un IDF toujours positif.
    """
    tokenises = [(nom, tokeniser(contenu)) for nom, contenu in documents]
    nb_documents = len(tokenises)
    longueur_moyenne = sum(len(t) for _, t in tokenises) / nb_documents

    frequence_documentaire = Counter()
    for _, tokens in tokenises:
        frequence_documentaire.update(set(tokens))

    idf = {
        mot: math.log(1 + (nb_documents - n + 0.5) / (n + 0.5))
        for mot, n in frequence_documentaire.items()
    }
    return {
        "documents": tokenises,
        "idf": idf,
        "longueur_moyenne": longueur_moyenne,
    }


def recherche_bm25(index: dict, question: str) -> list[tuple[str, float]]:
    """Classe les documents par score BM25 décroissant.

        score(D, Q) = somme sur les mots q de Q de
                      idf(q) * f * (k1 + 1)
                      / (f + k1 * (1 - b + b * longueur(D) / longueur_moyenne))

    où f est le nombre d'occurrences de q dans D.

    Les documents de score nul sont écartés : un score de 0 signifie qu'aucun
    mot de la question n'apparaît dans le document. Un moteur lexical ne les
    renverrait tout simplement pas.
    """
    mots_question = tokeniser(question)
    classement = []

    for nom, tokens in index["documents"]:
        occurrences = Counter(tokens)
        score = 0.0
        for mot in mots_question:
            frequence = occurrences.get(mot, 0)
            if frequence == 0:
                continue
            numerateur = frequence * (BM25_K1 + 1)
            denominateur = frequence + BM25_K1 * (
                1 - BM25_B + BM25_B * len(tokens) / index["longueur_moyenne"]
            )
            score += index["idf"].get(mot, 0.0) * numerateur / denominateur
        if score > 0:
            classement.append((nom, score))

    classement.sort(key=lambda couple: -couple[1])
    return classement


# ---------------------------------------------------------------------------
# 3. Moteur vectoriel : embeddings + Chroma
# ---------------------------------------------------------------------------


def indexer_vecteurs(documents: list[tuple[str, str]]):
    """Vectorise le corpus et renvoie (base Chroma, vecteur d'exemple).

    from_texts fait trois choses d'un coup : appeler l'API d'embedding sur
    chaque texte, stocker les vecteurs, et garder les métadonnées associées.

    La clé n'est pas passée en argument : OpenAIEmbeddings lit OPENAI_API_KEY
    dans l'environnement, que charger_env() a rempli depuis le .env.
    """
    from langchain_chroma import Chroma
    from langchain_openai import OpenAIEmbeddings

    embedding = OpenAIEmbeddings(model=MODELE_EMBEDDING)
    exemple = embedding.embed_query(documents[0][1])

    base = Chroma.from_texts(
        texts=[contenu for _, contenu in documents],
        metadatas=[{"source": nom} for nom, _ in documents],
        embedding=embedding,
        collection_name="procedures_demo",
    )
    return base, exemple


def recherche_vectorielle(base, question: str, k: int) -> list[tuple[str, float]]:
    """Classe les documents par distance croissante (plus bas = plus proche)."""
    resultats = base.similarity_search_with_score(question, k=k)
    return [(doc.metadata["source"], float(score)) for doc, score in resultats]


# ---------------------------------------------------------------------------
# 4. Fusion des deux classements : RRF
# ---------------------------------------------------------------------------


def fusion_rrf(classements: list[list[str]]) -> list[tuple[str, float]]:
    """Fusionne plusieurs classements par Reciprocal Rank Fusion.

        score(D) = somme sur les classements de 1 / (RRF_K + rang(D))

    Le point clé : la fusion n'utilise que les RANGS, jamais les scores. Un
    score BM25 vaut quelques unités, une distance Chroma vaut environ 1 : les
    additionner directement n'aurait aucun sens, et normaliser les échelles
    demanderait un calibrage propre à chaque corpus. Le rang, lui, est
    toujours comparable.

    Un document absent d'un classement ne reçoit simplement rien de ce
    classement. La fusion se dégrade donc proprement quand BM25 ne renvoie
    rien : elle redonne l'ordre vectoriel.
    """
    scores = defaultdict(float)
    for classement in classements:
        for rang, nom in enumerate(classement, start=1):
            scores[nom] += 1.0 / (RRF_K + rang)
    return sorted(scores.items(), key=lambda couple: -couple[1])


# ---------------------------------------------------------------------------
# 5. Affichage
# ---------------------------------------------------------------------------


def afficher_classement(
    intitule: str,
    unite: str,
    classement: list[tuple[str, float]],
    attendu: str,
) -> None:
    """Affiche un classement, ou le signale vide."""
    print(f"    {intitule}")
    if not classement:
        print("      aucun document ne contient un mot de la question")
        return
    for rang, (nom, valeur) in enumerate(classement[:NB_RESULTATS], start=1):
        marque = "   <-- attendu" if nom == attendu else ""
        print(f"      {rang}. {nom:<24} {unite} {valeur:.4f}{marque}")


def analyser_arguments() -> str:
    """Lit le mode demandé sur la ligne de commande."""
    parseur = argparse.ArgumentParser(
        description="Recherche lexicale (BM25) contre recherche vectorielle.",
    )
    groupe = parseur.add_mutually_exclusive_group()
    groupe.add_argument(
        "--sim",
        dest="mode",
        action="store_const",
        const="sim",
        help="recherche vectorielle seule (défaut)",
    )
    groupe.add_argument(
        "--bm25",
        dest="mode",
        action="store_const",
        const="bm25",
        help="recherche lexicale seule, aucun appel API",
    )
    groupe.add_argument(
        "--hyb",
        dest="mode",
        action="store_const",
        const="hyb",
        help="les deux classements plus leur fusion RRF",
    )
    parseur.set_defaults(mode="sim")
    return parseur.parse_args().mode


# ---------------------------------------------------------------------------
# 6. Déroulé de la démo
# ---------------------------------------------------------------------------


def main() -> None:
    mode = analyser_arguments()
    besoin_lexical = mode in ("bm25", "hyb")
    besoin_vectoriel = mode in ("sim", "hyb")

    documents = charger_corpus()
    par_nom = dict(documents)

    titre(f"1. Corpus à indexer ({len(documents)} documents)")
    for nom, contenu in documents:
        print(f"  {nom:<24} {len(contenu):>5} caractères")

    titre(f"2. Préparation des index (mode {mode})")

    index_bm25 = None
    if besoin_lexical:
        index_bm25 = indexer_bm25(documents)
        print(
            f"  BM25 : {len(index_bm25['idf'])} termes distincts, "
            f"{index_bm25['longueur_moyenne']:.0f} mots utiles par document"
        )
        print("  BM25 : aucun appel réseau, index construit en mémoire")

    base = None
    if besoin_vectoriel:
        # La clé n'est réclamée que maintenant : le mode --bm25 ne la lit jamais.
        fichier_env = charger_env()
        verifier_cle()
        print(
            f"  clé OpenAI lue dans {fichier_env}"
            if fichier_env
            else "  clé OpenAI lue dans les variables d'environnement"
        )
        base, exemple = indexer_vecteurs(documents)
        print(
            f"  vectoriel : chaque texte devient un vecteur de "
            f"{len(exemple)} nombres ({MODELE_EMBEDDING})"
        )
        print("  vectoriel : index Chroma en mémoire, prêt")

    titre("3. Interrogation")

    for question, attendu in QUESTIONS:
        print(f"\n  Question : {question}")

        classement_lexical = []
        if besoin_lexical:
            classement_lexical = recherche_bm25(index_bm25, question)

        classement_vectoriel = []
        if besoin_vectoriel:
            # On demande tout le corpus : la fusion a besoin de rangs complets,
            # l'affichage ne gardera que les premiers.
            classement_vectoriel = recherche_vectorielle(base, question, len(documents))

        # Mots réellement partagés entre la question et le document attendu.
        # C'est ce qui explique le résultat de BM25, dans un sens comme dans
        # l'autre.
        partages = set(tokeniser(question)) & set(tokeniser(par_nom.get(attendu, "")))
        print(
            "    mots partagés avec le document attendu : "
            + (", ".join(sorted(partages)) if partages else "AUCUN")
        )

        if besoin_lexical:
            afficher_classement("BM25 (lexical)", "score", classement_lexical, attendu)
        if besoin_vectoriel:
            afficher_classement(
                "Vectoriel (embeddings)", "distance", classement_vectoriel, attendu
            )
        if mode == "hyb":
            fusion = fusion_rrf([
                [nom for nom, _ in classement_lexical],
                [nom for nom, _ in classement_vectoriel],
            ])
            afficher_classement("Hybride (RRF)", "score", fusion, attendu)

    titre("4. À retenir")
    if besoin_lexical:
        print("  - BM25 ne renvoie rien quand la question ne partage aucun mot")
        print("    avec le corpus : ce n'est pas un mauvais classement, c'est")
        print("    une absence de résultat")
    if besoin_vectoriel:
        print("  - le vectoriel classe correctement sans partage de vocabulaire")
        print("  - sa distance ne se compare pas d'une question à l'autre")
    if mode == "hyb":
        print("  - la fusion RRF n'additionne que des rangs, jamais des scores")
        print("    d'échelles différentes")
    if mode != "hyb":
        print("  - relancer avec --hyb pour voir les deux moteurs côte à côte")


if __name__ == "__main__":
    main()
