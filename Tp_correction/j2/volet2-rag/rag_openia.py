# /// script
# requires-python = ">=3.10"
# dependencies = ["langchain>=0.3,<1.0", "langchain-community>=0.3,<1.0",
#                 "langchain-text-splitters>=0.3,<1.0", "langchain-chroma>=0.1,<1.0",
#                 "langchain-openai>=0.2,<1.0", "chromadb>=0.5",
#                 "rank-bm25>=0.2", "snowballstemmer>=2.2"]
# ///
"""Jumeau de rag.py branche sur l'API d'OpenAI au lieu d'OpenRouter.

Meme corrige, meme decoupage, memes trois modes de recherche. Seul le
fournisseur change. Les differences avec rag.py, et elles seules :

    cle          OPENAI_API_KEY au lieu d'OPENAI_API_KEY
    base_url     absente : le client vise api.openai.com par defaut
    embedding    text-embedding-3-small, Qwen n'existant pas chez OpenAI
    modele       gpt-4o-mini, MiniMax n'existant pas chez OpenAI
    base         chroma_db_openai, distincte de celle de rag.py

Les deux bases vectorielles sont separees a dessein : les vecteurs d'OpenAI
ont 1536 dimensions contre 2560 pour ceux de Qwen, et Chroma refuse deux
dimensions dans une meme collection. Les deux scripts cohabitent donc sans
se marcher dessus, et une comparaison des deux fournisseurs est possible.

Contrairement a rag.py, ce script n'est pas gratuit : gpt-4o-mini et
text-embedding-3-small sont factures, meme si l'ordre de grandeur du TP
reste de quelques millimes.

    uv run rag_openia.py indexer               etape 1 : decoupe et indexe le corpus
    uv run rag_openia.py demander              etape 2 : interroge avec RAG
    uv run rag_openia.py comparer              etape 3 : sans RAG puis avec RAG
    uv run rag_openia.py demander "..." "..."   les questions du TP, ou les tiennes

Trois modes de recherche, en drapeau sur demander et comparer :

    --dense     defaut, similarite vectorielle seule
    --bm25      lexical seul, sans aucun appel d'embedding
    --hybride   fusion des deux par rang reciproque

Cle lue dans l'environnement, sinon dans le .env voisin, comme les demos du
Jour 2 : y placer OPENAI_API_KEY=sk-...

Les bornes hautes du bloc ci-dessus ne sont pas decoratives : langchain 1.0 a
deplace langchain.chains vers le paquet langchain-classic et ne tire plus
langchain-text-splitters. Sans <1.0, les trois commandes echouent a l'import.
"""

import os
import re
import shutil
import sys
from pathlib import Path

BASE = Path(__file__).parent / "chroma_db_openai"
ENV = Path(__file__).parent / ".env"
CORPUS = Path(__file__).parents[3] / "demos" / "j2" / "corpus"
COLLECTION = "procedures_internes"
EMBEDDING = "text-embedding-3-small"
K = 3  # chunks envoyes au modele
# Poids [dense, lexical] et c=0 de la fusion : mesures sur dix questions melant
# identifiants exacts (PR-045) et langage naturel. Rappel du bon document dans
# le top-3 : 7/10 en dense seul, 9/10 en BM25 seul, 10/10 avec ces valeurs.
# Le c=60 par defaut aplatit les rangs et fait perdre 1 point sur ce corpus.
POIDS = [0.3, 0.7]
MODELE = "gpt-4o-mini"

QUESTIONS = [
    "Combien de jours de télétravail sont autorisés par semaine ?",
    "Quel est le plafond de remboursement pour une nuitée à Paris ?",
    "Quelle est la compensation pour une semaine d'astreinte ?",
]


def cle():
    """Cle lue dans l'environnement, sinon dans le .env voisin."""
    valeur = os.environ.get("OPENAI_API_KEY")
    if not valeur and ENV.exists():
        for ligne in ENV.read_text(encoding="utf-8").splitlines():
            if ligne.startswith("OPENAI_API_KEY="):
                valeur = ligne.split("=", 1)[1].strip().strip("\"'")
    if not valeur:
        raise SystemExit("OPENAI_API_KEY absente : la definir dans %s" % ENV)
    return valeur


def embeddings():
    """Aucun base_url : le client vise api.openai.com par defaut.

    rag.py doit y ajouter check_embedding_ctx_length=False, parce que
    langchain_openai tokenise avec tiktoken et poste des tableaux
    d'identifiants que les fournisseurs tiers refusent. L'endpoint d'OpenAI
    les accepte, le reglage par defaut convient donc ici.
    """
    from langchain_openai import OpenAIEmbeddings

    return OpenAIEmbeddings(model=EMBEDDING, api_key=cle())


def morceaux():
    """Le corpus decoupe. Un seul decoupage pour les deux index.

    L'index vectoriel et l'index BM25 doivent voir exactement le meme texte,
    sinon la fusion compare des rangs portant sur des chunks differents.
    """
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    fichiers = sorted(CORPUS.glob("*.txt"))
    if not fichiers:
        sys.exit("Corpus introuvable : %s" % CORPUS)

    decoupeur = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    textes, metadonnees = [], []
    for fichier in fichiers:
        for morceau in decoupeur.split_text(fichier.read_text(encoding="utf-8")):
            textes.append(morceau)
            metadonnees.append({"source": fichier.stem})
    return fichiers, textes, metadonnees


def indexer():
    """Etape 1. Seul l'index vectoriel est persiste ; BM25 se reconstruit.

    La base est purgee d'abord : Chroma.from_texts ajoute a une collection
    existante au lieu de la remplacer, donc une seconde indexation doublerait
    le corpus et ferait remonter des doublons dans les k resultats.
    """
    from langchain_chroma import Chroma

    fichiers, textes, metadonnees = morceaux()
    if BASE.exists():
        shutil.rmtree(BASE)

    Chroma.from_texts(
        texts=textes,
        metadatas=metadonnees,
        embedding=embeddings(),
        collection_name=COLLECTION,
        persist_directory=str(BASE),
    )
    print(
        "%d fichiers -> %d chunks indexes dans %s"
        % (len(fichiers), len(textes), BASE.name)
    )


def retrouveur(mode):
    """Le retriever, selon le mode. C'est ici que se joue tout le RAG.

    dense    : plus proches voisins dans l'espace vectoriel. Encaisse la
               paraphrase, aveugle aux identifiants exacts type PR-045, dont
               le vecteur ne porte aucun sens.
    bm25     : ponderation lexicale par frequence inverse. L'exact inverse :
               imbattable sur les tokens rares, aveugle aux synonymes. Aucun
               appel d'embedding : l'index se reconstruit en memoire, seul
               le modele de reponse est appele.
    hybride  : fusion des deux classements par rang reciproque.
    """
    from langchain_chroma import Chroma

    if not BASE.exists():
        sys.exit("Base absente. Lancer d'abord : uv run rag_openia.py indexer")

    dense = Chroma(
        persist_directory=str(BASE),
        embedding_function=embeddings(),
        collection_name=COLLECTION,
    ).as_retriever(search_kwargs={"k": K})
    if mode == "dense":
        return dense

    import snowballstemmer
    from langchain_community.retrievers import BM25Retriever

    racine = snowballstemmer.stemmer("french")

    def decouper(texte):
        """Minuscules, mots, racines.

        Sans racinisation, "conge" ne rejoint pas "conges" et la question du
        TP sur les conges rate sa cible : BM25 compare des chaines, pas du sens.
        """
        return racine.stemWords(re.findall(r"\w+", texte.lower()))

    _, textes, metadonnees = morceaux()
    lexical = BM25Retriever.from_texts(
        textes, metadatas=metadonnees, preprocess_func=decouper
    )
    lexical.k = K
    if mode == "bm25":
        return lexical

    from langchain.retrievers import EnsembleRetriever
    from langchain_core.retrievers import BaseRetriever

    class TronqueAuTopK(BaseRetriever):
        """EnsembleRetriever rend l'union des deux listes, jusqu'a 2*K documents.

        On coupe au rang K : c'est sur le top-K que la fusion a ete calibree, et
        les trois modes doivent envoyer le meme volume de contexte au modele.
        """

        fusion: BaseRetriever

        def _get_relevant_documents(self, query, *, run_manager):
            return self.fusion.invoke(query)[:K]

    return TronqueAuTopK(
        fusion=EnsembleRetriever(retrievers=[dense, lexical], weights=POIDS, c=0)
    )


def chaine(mode):
    """Etape 2. Meme base et meme modele d'embedding qu'a l'indexation."""
    from langchain.chains import create_retrieval_chain
    from langchain.chains.combine_documents import create_stuff_documents_chain
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_openai import ChatOpenAI

    prompt = ChatPromptTemplate.from_template(
        "Reponds uniquement a partir du contexte ci-dessous. Si l'information "
        "n'y figure pas, dis-le explicitement au lieu de deviner.\n\n"
        "Contexte :\n{context}\n\nQuestion : {input}"
    )
    llm = ChatOpenAI(model=MODELE, temperature=0, api_key=cle())
    return create_retrieval_chain(
        retrouveur(mode), create_stuff_documents_chain(llm, prompt)
    )


def demander(questions, mode):
    """Etape 2. Les questions de la ligne de commande, sinon celles du TP."""
    print("recherche : %s" % mode)
    qa = chaine(mode)
    for question in questions:
        resultat = qa.invoke({"input": question})
        print("\n%s\n  %s" % (question, resultat["answer"]))
        print(
            "  sources : %s"
            % ", ".join(sorted({d.metadata["source"] for d in resultat["context"]}))
        )


def comparer(questions, mode):
    """Etape 3. Le livrable du TP : l'ecart entre les deux colonnes."""
    from langchain_openai import ChatOpenAI

    llm = ChatOpenAI(model=MODELE, temperature=0, api_key=cle())
    qa = chaine(mode)
    for question in questions:
        print("\n" + "=" * 74 + "\n" + question)
        print(
            "\n-- sans RAG\n  %s" % llm.invoke(question).content.replace("\n", "\n  ")
        )
        resultat = qa.invoke({"input": question})
        print("\n-- avec RAG\n  %s" % resultat["answer"].replace("\n", "\n  "))
        print(
            "  sources : %s"
            % ", ".join(sorted({d.metadata["source"] for d in resultat["context"]}))
        )


if __name__ == "__main__":
    actions = {"indexer": indexer, "demander": demander, "comparer": comparer}
    action = actions.get(sys.argv[1] if len(sys.argv) > 1 else "")
    if not action:
        sys.exit(__doc__)
    mode, questions = "dense", []
    for argument in sys.argv[2:]:
        if not argument.startswith("--"):
            questions.append(argument)
        elif argument[2:] in ("dense", "bm25", "hybride"):
            mode = argument[2:]
        else:
            sys.exit("mode inconnu : %s (--dense, --bm25 ou --hybride)" % argument)

    cle()  # echoue tot, avant les imports lourds, si la cle manque
    if action is indexer:
        action()
    else:
        action(questions or QUESTIONS, mode)
