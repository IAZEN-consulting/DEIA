# Observations - volet 2

> **Modele indicatif.** Le TP demande la comparaison sur trois questions, avec
> les documents sources et une conclusion argumentee.

Produit par `uv run rag.py comparer`.

## Question 1 - jours de teletravail

| | Reponse |
|---|---|
| Sans RAG | Reponse generique sur les pratiques courantes, ou refus poli. Aucun chiffre verifiable. |
| Avec RAG | Trois jours par semaine au maximum, dont un jour sur plage fixe. Mardi obligatoire sur site. |
| Sources | `teletravail` |

## Question 2 - plafond nuitee a Paris

| | Reponse |
|---|---|
| Sans RAG | Fourchette plausible mais inventee, presentee avec assurance. |
| Avec RAG | 160 euros a Paris et petite couronne, 110 en province. |
| Sources | `notes-de-frais` |

## Question 3 - compensation d'astreinte

| | Reponse |
|---|---|
| Sans RAG | Reponse vague renvoyant a la convention collective. |
| Avec RAG | 150 euros par semaine, plus les interventions au taux majore de 50 %. |
| Sources | `astreinte` |

## Conclusion attendue

Sans RAG, le modele n'a aucun moyen de connaitre des procedures internes : il
produit soit un refus, soit une reponse plausible et non verifiable. C'est
exactement l'hallucination vue au Jour 1, mais dans un cas ou elle est
particulierement dangereuse, parce que la reponse ressemble a une politique
d'entreprise credible.

Avec RAG, la reponse est ancree dans le corpus et les documents sources sont
identifiables, donc verifiables par le lecteur.

**Le point a ne pas manquer** : le RAG n'a pas rendu le modele plus
intelligent. Il lui a donne acces a la bonne information au bon moment. Le
modele est identique dans les deux colonnes.

## Piege rencontre

Si les reponses sont hors sujet, verifier dans cet ordre :

1. Le corpus est-il indexe ? (`uv run rag.py indexer` avant `demander`)
2. Le decoupage est-il adapte a la taille des documents ?
3. **Le meme modele d'embedding est-il utilise a l'indexation et a la
   recherche ?** C'est l'erreur la plus frequente et la plus silencieuse :
   rien ne plante, les resultats sont simplement mauvais.
