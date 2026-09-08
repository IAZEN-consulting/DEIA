# AGENTS.md

Support de formation DIEA (IA generative et agents LLM), anime en francais.
Le depot contient des demonstrations projetees en session et les corrections
de TP. Tout commentaire, docstring et document produit ici est en francais,
sauf dans les demos du jour 2 deja redigees en anglais.

## Structure

- `demos/j1/` : jour 1 (tokenisation, ChatGPT vs Copilot, cadrage, hallucinations)
- `demos/j2/` : jour 2 (appel API, LangChain/LangGraph, similarite, image) +
  `demos/j2/corpus/` (six procedures internes fictives, partage avec le TP)
- `Tp_correction/` : corrections attendues des TP

## Commandes

- Script Python : `uv run <script>.py` depuis son dossier. Jamais `pip`,
  jamais de venv cree a la main.
- Projet Node (`demo3-cadrage/projet/`, `Tp_correction/j1/parcours-a-react/`) :
  `npm install` si `node_modules/` absent, `npm test` avant toute fin de tache.

## Conventions Python

- Chaque script est autonome : dependances declarees dans le bloc d'en-tete
  PEP 723 (`# /// script ... # ///`), pas de `requirements.txt` sauf dossier
  qui en contient deja un.
- SDK `openai` pointe sur OpenRouter (`https://openrouter.ai/api/v1`).
- Cles API lues depuis l'environnement ou un fichier `.env`
  (voir [.env.example](.env.example)) : `OPENROUTER_API_KEY`, `OPENAI_API_KEY`.
  Ne jamais ecrire une cle dans le code ni la committer ; `.env` est ignore
  par git.
- Les scripts de demo ont souvent un mode preparation (`--live` /
  `--enregistrer`) a lancer la veille, et un mode par defaut sans reseau pour
  le jour J. Ne pas « simplifier » ce fonctionnement.

## Conventions JavaScript

- JavaScript ES2022, modules ES, pas de TypeScript, tests Vitest.
- Nommage en francais dans les dossiers pedagogiques.
- Les details (interdits, ordre de travail, definition de terminee) sont dans
  les AGENTS.md de chaque dossier concerne — ce sont des artefacts
  pedagogiques avec des contraintes volontaires, les respecter tels quels et
  ne pas les fusionner ici :

  - [demos/j1/demo3-cadrage/projet/AGENTS.md](demos/j1/demo3-cadrage/projet/AGENTS.md)
  - [Tp_correction/j1/parcours-a-react/AGENTS.md](Tp_correction/j1/parcours-a-react/AGENTS.md)
  - [Tp_correction/j2/volet1-html/AGENTS.md](Tp_correction/j2/volet1-html/AGENTS.md)

## Pièges

- Chaque demo a son propre README avec le deroule attendu : le lire avant de
  modifier le script. Les demos sont concues pour montrer un point precis
  (variabilite, similarite sans mot commun, prompt reecrit par l'API...) ;
  un « correctif » qui fait disparaitre le phenomene demontre casse la demo.
- Les sorties produites vont dans un sous-dossier `sortie/` ou `sorties/` du
  dossier courant, pas a la racine.
