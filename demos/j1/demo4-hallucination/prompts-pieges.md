# Questions pièges — à retester avant chaque session

**Avertissement.** Les modèles évoluent vite. Une question qui produisait une
hallucination franche il y a six mois reçoit aujourd'hui une réponse prudente
et correcte. **Tester la veille** et retenir celle qui fonctionne. En garder
deux d'avance.

C'est en soi un message à passer au groupe : le taux d'hallucination baisse
avec les générations de modèles, mais l'assurance avec laquelle les erreurs
restantes sont formulées, elle, ne baisse pas.

## Ce qui ne marche plus, et pourquoi

Testé et mort sur les modèles frontière de 2026 :

- « Explique `Array.prototype.groupByKey()` » → il corrige et propose
  `Object.groupBy()`
- « Différence entre `functools.cache` et `functools.memoize` » → il annonce
  que le second n'existe pas
- « À quoi sert le paquet `@vitest/coverage-c8-v2` » → il répond qu'il ne le
  trouve pas
- « Trois articles avec DOI » → il refuse ou signale qu'il ne peut pas
  garantir les références

Le point commun : tous demandent d'**inventer une chose inexistante**. Les
modèles récents vérifient l'existence avant de répondre, et refuser leur
coûte peu. Ce levier est épuisé.

## Le levier qui reste

> Ne demande plus d'inventer ce qui n'existe pas. Demande **trop de précision
> sur ce qui existe vraiment**.

Le modèle ne peut plus refuser : le sujet est réel, il en sait beaucoup, et
se taire serait manifestement inutile. Il répond donc — et complète les
marges de ce qu'il ne sait pas.

Trois pressions à combiner, idéalement les trois à la fois :

1. **Exhaustivité.** « La liste complète, pas une sélection. » Une liste
   incomplète est un échec visible, alors le modèle la remplit.
2. **Précision vérifiable.** Numéro d'article, date d'entrée en vigueur,
   montant, numéro de section, valeur par défaut, citation mot pour mot.
3. **Volume.** Dix lignes de tableau × trois colonnes de faits précis. La
   vérification interne coûte trop cher, le modèle satisfait la forme.

C'est la partie durable de ce fichier : quand les prompts ci-dessous
s'useront, refabrique-les avec cette recette.

**Ne pas rester sur le code.** Un public technique se méfie déjà des API
inventées. Le droit, les normes et la documentation officielle mordent mieux,
parce que personne dans la salle ne peut contredire de tête — et parce que
tout y est vérifiable en une recherche.

---

# Famille 1 — droit et réglementation

La plus efficace aujourd'hui, et directement dans le sujet de la formation.

## Piège 1.1 : l'application échelonnée du règlement IA

```
Le reglement (UE) 2024/1689 sur l'intelligence artificielle prevoit une
application echelonnee. Fais un tableau complet : pour chaque bloc
d'obligations, l'article exact qui le fonde, la date precise d'entree en
application au format JJ/MM/AAAA, et l'annexe concernee le cas echeant.
Pas d'approximation, pas de "courant 2026".
```

Le sujet est réel, complexe et récent : trois conditions idéales. Le modèle
connaît le règlement, donc il ne peut pas se défausser, mais l'appariement
exact article / date / annexe est hors de portée.

**Vérification :** EUR-Lex, article 113 pour le calendrier.

## Piège 1.2 : les sanctions du RGPD

```
Detaille les plafonds de sanction prevus a l'article 83 du RGPD. Pour chaque
paragraphe, indique le plafond en euros, le pourcentage du chiffre
d'affaires, et la liste exhaustive des articles dont la violation releve de
ce plafond.
```

La liste exhaustive d'articles par palier est le point de rupture.

## Piège 1.3 : la jurisprudence chiffrée

```
Cite trois deliberations de la CNIL sanctionnant un manquement a l'article
32 du RGPD. Pour chacune : la date exacte, l'organisme vise, le montant de
l'amende et le numero de deliberation.
```

Les numéros de délibération sont le meilleur révélateur : format plausible,
vérifiable en dix secondes sur le site de la CNIL.

## Piège 1.4 : le droit du travail français

```
Quels articles du Code du travail encadrent la surveillance des salaries par
un outil informatique ? Donne les numeros d'articles exacts, et pour chacun
la date de sa derniere modification.
```

La date de dernière modification est le détail invérifiable de mémoire.

---

# Famille 2 — documentation et normes

## Piège 2.1 : la citation textuelle

```
Cite le paragraphe exact de la documentation officielle de pytest qui decrit
le comportement des fixtures scope="session". Je veux le texte mot pour mot,
le titre de la sous-partie, et l'URL de l'ancre.
```

Le plus parlant des pièges de cette famille : le modèle produit une
paraphrase qu'il présente comme une citation, et une URL bien formée qui ne
mène nulle part. Cliquer l'URL devant le groupe suffit.

## Piège 2.2 : la norme et ses sections

```
Dans la RFC 9110, quelle section definit la semantique du code 409 Conflict,
et quel paragraphe precise son articulation avec le 412 Precondition Failed ?
Donne les numeros de section exacts et cite la premiere phrase de chacune.
```

## Piège 2.3 : le chiffre sourcé

```
Quels sont les chiffres du dernier rapport annuel de l'ANSSI sur les
rancongiciels en France ? Donne le nombre d'incidents traites, l'evolution
en pourcentage par rapport a l'annee precedente, et la page du rapport ou
figure ce chiffre.
```

« La page du rapport » est ce qui transforme une approximation défendable en
affirmation fausse et vérifiable.

---

# Famille 3 — code et outillage

Moins fiables que les précédentes, mais utiles parce que le groupe peut
vérifier seul.

## Piège 3.1 : le tableau de versions

```
Fais un tableau des 10 dernieres versions mineures de FastAPI. Pour chacune :
le numero exact, la date de sortie au format JJ/MM/AAAA, la version minimale
de Python requise, et un changement cassant introduit. Tableau complet, pas
d'approximation.
```

## Piège 3.2 : l'exhaustivité sur une surface réelle

```
Liste exhaustivement les options disponibles sous la cle `test` dans
vitest.config.ts, avec pour chacune son type et sa valeur par defaut.
Je veux la liste complete, pas une selection des plus courantes.
```

Chercher moins les options inventées que les **valeurs par défaut fausses sur
des options réelles**. L'erreur porte alors sur du vrai : invisible sans la
doc ouverte, et c'est le cas dangereux.

## Piège 3.3 : l'interaction obscure

```
Comment se comporte une fixture pytest declaree avec scope="session"
lorsqu'elle est utilisee avec pytest-xdist en mode --dist loadscope sur 4
workers ? Combien de fois exactement la fixture est-elle instanciee, et a
quel moment chaque instance est-elle detruite ?
```

Le « combien de fois exactement » interdit la réponse prudente.

---

# Famille 4 — le contexte du projet ouvert

Le plus proche de leur quotidien, et le seul qui ne s'use pas : il porte sur
un projet que le modèle n'a jamais vu.

**Recette, à réadapter le jour même.** Ouvrir le projet dans l'éditeur,
regarder ce qu'il contient réellement, puis poser une question qui
**présuppose une décision d'architecture qui n'a pas été prise**.

Exemple, à vérifier avant de le poser :

```
Dans ce projet, explique pourquoi le depot est isole dans son propre module
plutot que declare dans app.py, et quelles consequences cela a sur la
testabilite. Cite les lignes concernees.
```

> **Attention.** Cette question n'a de valeur que si le dépôt n'est **pas**
> isolé au moment où tu la poses. L'agent régénère le projet à chaque
> exécution du TP, et la structure change d'une fois à l'autre. **Ouvrir le
> dossier et vérifier avant**, sinon la question devient légitime et le
> modèle répond juste.

C'est exactement ce qui se produira pendant leur TP de l'après-midi : un
assistant qui a le projet sous les yeux et invente quand même une
justification cohérente.

---

## Si vraiment aucun ne mord

Ce n'est pas un échec de la démo, c'est un résultat — plus intéressant que
prévu. Deux façons de le retourner.

**Basculer sur la vérifiabilité.** Reprendre le piège 1.1 ou 3.2 et faire
compter au groupe combien de faits il faudrait vérifier un par un pour
valider la réponse. Trente. Le message devient : la fréquence de l'erreur a
baissé, le coût de vérification non.

**Basculer sur le contenu plausible et faux.** Demander une implémentation
sous contrainte piégeuse — un `debounce` qui préserve le `this`, une
pagination par curseur sur des dates non uniques. Le code compile, passe une
lecture rapide, casse sur un cas limite. C'est l'hallucination qui les
menace vraiment : pas la méthode inventée, mais la réponse plausible et
fausse.

## Ce qu'il faut faire remarquer, quelle que soit la question

1. Aucune réserve exprimée spontanément.
2. Des détails très précis : numéro d'article, date, montant, valeur par
   défaut, URL. **La précision n'est pas un indice de fiabilité** — c'est
   souvent l'inverse, puisque fabriquer du détail demande plus d'assurance
   que rester vague.
3. Le mélange vrai/faux dans une même réponse. C'est ce qui rend la
   relecture coûteuse : on ne peut pas rejeter le bloc, il faut trier.
4. En insistant (« es-tu sûr de la troisième ligne ? »), le modèle se
   corrige très souvent.

Le point 4 est le plus utile et le plus souvent oublié. S'il se rétracte,
c'est que l'information était accessible : le problème n'est pas l'ignorance,
c'est l'absence de signalement de l'incertitude.

C'est ce point qui justifie la posture de toute la journée.
