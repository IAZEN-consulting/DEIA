# AGENTS.md

Ce fichier est la seule consigne. Tout ce qui est nécessaire pour produire le
livrable est ici : ne rien chercher ailleurs dans le dépôt, ne supposer aucun
énoncé extérieur, ne demander aucune précision avant de commencer.

## Ce qu'il faut produire

Dans ce dossier, trois livrables :

- `generer.py`, un script Python unique ;
- `sortie/`, les fichiers HTML écrits par les exécutions ;
- `observations_volet1.md`, le compte rendu décrit plus bas.

## À quoi sert ce script

C'est un support de formation. Il sert à démontrer trois choses devant un
groupe de stagiaires, dans cet ordre :

1. sans contraintes, un modèle de langage produit un résultat différent à
   chaque appel, et ne tient pas les exigences qu'on ne lui a pas données ;
2. le même besoin, énoncé avec ses contraintes, devient conforme et
   reproductible ;
3. du HTML produit par un modèle ne s'affiche jamais sans avoir été vérifié
   et assaini.

Une commande par démonstration. Le script écrit du HTML dans des fichiers, il
ne le sert pas : ce n'est pas une application web.

## Commandes

- Démonstration 1 : `uv run generer.py libre`
- Démonstration 2 : `uv run generer.py structure`
- Démonstration 3 : `uv run generer.py valider`

Sans argument, le script affiche sa docstring d'usage et s'arrête.

### libre

Envoie trois fois le même prompt vague, à la température par défaut. Pour
chaque appel, affiche le nombre de tokens, la taille du résultat, la liste
des critères non tenus, et écrit le code dans `sortie/etape1-appelN.html`.
C'est la variabilité qu'on vient rendre visible : trois appels, trois
résultats.

### structure

Un seul appel, avec le prompt structuré, à température 0. Affiche oui ou NON
pour chaque critère contrôlé, puis écrit `sortie/etape2-structure.html`.

### valider

Génère avec le prompt structuré, puis, dans cet ordre :

1. retire une éventuelle clôture markdown autour du code ;
2. vérifie les balises et signale celles qui ne sont jamais fermées et celles
   fermées sans avoir été ouvertes ;
3. assainit le code et l'écrit dans `sortie/etape3-assaini.html` ;
4. assainit une charge d'injection écrite en dur dans le script, et affiche
   le avant / après.

## Prompts imposés

Ces deux prompts sont ceux distribués aux stagiaires. Les recopier tels
quels, sans les reformuler ni les traduire.

Prompt vague, pour `libre` :

```
Crée une carte de profil utilisateur
```

Prompt structuré, pour `structure` et `valider` :

```
Génère uniquement le code HTML et CSS (dans une seule balise <style>)
d'une carte de profil utilisateur avec :
- une photo circulaire (placeholder 80x80px)
- un nom et un poste sur deux lignes
- trois boutons alignés horizontalement : Suivre, Message, Bloquer
- une bordure arrondie et une ombre légère
Ne génère aucun texte d'explication, uniquement le code.
```

Les contraintes de format sont portées par un prompt système, jamais
répétées dans le prompt utilisateur : le modèle ne doit produire que du HTML
et du CSS, dans une seule balise `<style>`, sans texte d'explication, sans
commentaire et sans bloc de code markdown.

Les critères contrôlés découlent du prompt structuré, un par exigence : une
seule balise `<style>`, une image, exactement trois boutons, des coins
arrondis, une ombre, et aucun texte avant la première balise.

## Stack

Python 3.12, SDK `openai` pointé sur l'API OpenAI (`https://api.openai.com/v1`,
modèle `gpt-4o-mini`), `nh3` pour l'assainissement, `html.parser` de la
bibliothèque standard pour la vérification des balises. Rien d'autre.

Environnement géré par uv, jamais par `pip` ni par un venv créé à la main.
`requirements.txt` liste les dépendances, `pyproject.toml` et `uv.lock` font
foi une fois le projet initialisé.

## Mise en route

Constater l'état du projet, puis n'exécuter que la branche qui correspond.

Lancer `ls -a` seul, et lire le résultat avant de décider. Ne pas enchaîner
le constat et l'action avec `&&` : le résultat du premier commande le second.

1. Si `pyproject.toml` est absent, le projet n'est pas initialisé :

   ```
   uv init --bare --python 3.12
   uv add -r requirements.txt
   ```

2. Si `pyproject.toml` existe mais que `.venv/` est absent :

   ```
   uv sync
   ```

3. Si les deux existent, ne rien initialiser : le projet est prêt, passer
   directement aux commandes. `uv init` sur un projet déjà initialisé
   s'arrête sur `error: Project is already initialized` ; c'est une
   protection, pas un incident à contourner.

Ne rien installer dans le Python du système. L'environnement du projet est
`.venv/`, créé et peuplé par uv. Si un `VIRTUAL_ENV` étranger est actif dans
le shell, uv l'ignore et le signale : c'est le comportement attendu.

## La clé API

Elle est lue dans le fichier `.env` de la racine du dépôt, sous le nom
`OPENAI_API_KEY`. Le script accepte aussi la variable d'environnement du même
nom, et cherche dans cet ordre : l'environnement d'abord, le fichier ensuite.

Deux constats qui n'indiquent aucun problème, et qu'il est inutile
d'instruire :

- un `ls` de la racine ne montre pas ce fichier. Il commence par un point,
  donc `ls -a` est nécessaire pour le voir.
- `env | grep OPENAI_API_KEY` ne renvoie rien. La clé vit dans le fichier,
  pas dans l'environnement du shell ; le script lit les deux.

Ne jamais afficher le contenu de ce fichier, ne jamais recopier la clé dans
une sortie, un commentaire ou un fichier de travail. Le script s'arrête avec
un message explicite si la clé manque, avant tout appel réseau.

## Conventions

- Une sous-commande par démonstration, une fonction par sous-commande,
  nommée comme la démonstration qu'elle porte.
- Français accentué partout : docstrings, commentaires, sorties écran. Les
  identifiants restent sans accent.
- Noms de fonctions, de variables et de fichiers en français.
- Les critères exigés par le prompt structuré sont vérifiés mécaniquement,
  pas affirmés en commentaire : un dictionnaire de contrôles, un résultat par
  critère à l'écran.
- La température sépare les deux premières démonstrations : défaut pour
  `libre`, 0 pour `structure` et `valider`. C'est la variabilité qu'on montre
  d'abord, la reproductibilité ensuite.
- Tout code produit est écrit dans `sortie/`, un fichier par appel, nommé
  d'après la démonstration qui l'a produit.
- Les imports de dépendances tierces sont locaux à la fonction qui les
  utilise, pour que `uv run generer.py` sans argument reste instantané.
- Pas d'emoji, nulle part.

## Interdits

- Aucun serveur : ni Flask, ni FastAPI, ni `http.server`, ni Express.
- Aucun JavaScript, aucun fichier servi à un navigateur par le script,
  aucune balise `<script>` écrite par le script.
- **Jamais d'assainissement par expression régulière.** Un filtrage maison ne
  protège de rien : seule une bibliothèque éprouvée fait ce travail. Les
  expressions régulières ne servent qu'au nettoyage markdown et aux contrôles
  de forme, jamais à la sécurité.
- Pas de clé API en dur, pas de clé écrite dans une sortie ou un fichier.
- Pas de dépendance ajoutée sans nécessité démontrée : la vérification des
  balises se fait avec la bibliothèque standard.
- Ne pas installer de dépendance avec `pip install` en dehors de `uv add` :
  `pyproject.toml` et `uv.lock` doivent rester la seule source de vérité.

## Points de vigilance

Quatre pièges déjà rencontrés sur ce livrable.

- Le modèle ajoute parfois une clôture markdown malgré la consigne. Le
  nettoyage reste nécessaire : une consigne de prompt réduit un comportement,
  elle ne le supprime pas.
- L'assainisseur vide le contenu de `<style>` dans sa configuration par
  défaut, ce qui effacerait tout le CSS généré. Seul `<script>` doit voir son
  contenu supprimé.
- Les balises autofermantes (`img`, `br`, `meta`, `input`, ...) ne doivent pas
  être empilées par le vérificateur, sans quoi il signale des balises non
  fermées qui n'existent pas.
- Retirer les balises `<script>` ne protégerait de rien : elles ne sont pas
  exécutées lors d'une injection dans une page. Les vecteurs réels sont les
  attributs d'événement (`onerror`, `onload`) et les `<iframe>`. La charge de
  démonstration doit contenir les deux.

## Le compte rendu

`observations_volet1.md` rend compte de ce qui a réellement été obtenu. Il
contient :

- les deux prompts, et ce que chacun a produit ;
- un tableau comparant les deux premières démonstrations sur quatre critères :
  structure respectée, texte parasite autour du code, HTML valide,
  reproductibilité sur trois appels ;
- les chiffres relevés à l'exécution : tailles obtenues, critères non tenus,
  tailles avant et après assainissement ;
- le avant / après de la charge d'injection ;
- les corrections manuelles qu'il a fallu apporter au code généré.

Les sorties d'un modèle varient d'un appel à l'autre : décrire ce qui a été
obtenu, jamais ce qui aurait dû l'être. Aucun chiffre d'illustration.

## Définition de terminée

Le livrable n'est terminé que si, dans cet ordre :

1. les trois commandes s'exécutent sans erreur ;
2. `structure` affiche oui sur tous ses critères ;
3. `valider` ne signale aucune balise non fermée sur un code correct, et la
   charge de démonstration ressort sans attribut d'événement ni `<iframe>` ;
4. un HTML légitime traverse l'assainissement sans perte de contenu ;
5. `observations_volet1.md` ne contient que des chiffres réellement observés.

Annoncer terminé avant d'avoir exécuté les trois commandes n'est pas permis.
