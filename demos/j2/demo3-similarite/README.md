# Jour 2 - Demo 3 : recherche par similarite

**Diapositive 13. Duree : 10 minutes.** C'est la demo qui rend le RAG concret.

```bash
uv run similarite.py --live --enregistrer   # avant la session
uv run similarite.py                        # le jour J
```

## Le dispositif

Le corpus (`../corpus/`, six procedures internes fictives) est indexe, puis
interroge avec trois questions formulees **sans aucun mot en commun** avec le
document attendu.

Le script le prouve a l'ecran : pour chaque question il affiche les mots
significatifs partages avec le document trouve. La reponse attendue est
`AUCUN`.

C'est la seule chose a montrer. Si un participant pense que la recherche se
fait par mots-cles, cette ligne repond a l'objection sans discussion.

## Deux precisions a donner

- **Le score est une distance.** Chez Chroma, plus il est bas, plus le
  document est proche. Un participant qui lit « 0,32 » comme une note sur 1
  comprendra l'inverse de la realite.
- **Le corpus est volontairement minuscule.** Six documents courts, indexes
  entiers, sans decoupage. Le decoupage devient necessaire des que les
  documents depassent la taille de contexte utile ; c'est le sujet du TP.

## Lien avec le TP

Le meme corpus sert au volet 2 du TP. Les participants le retrouveront, ce
qui leur evite de decouvrir a la fois l'outil et les donnees.
