# Jour 2 - Demo 4 : prompt court contre prompt detaille

**Diapositive 17. Duree : 8 minutes.**

```bash
uv run generer_image.py --live   # avant la session : produit les deux images
uv run generer_image.py          # le jour J : affiche les prompts et liste
                                 # les images generees lors de la repetition
```

## Particularite de cette demo

C'est la seule dont le plan B n'est pas un rejeu de texte : ce sont les deux
fichiers PNG produits lors de la repetition, conserves dans `sorties/`.

**Faire tourner cette demo la veille est donc obligatoire**, sinon il n'y a
rien a montrer en cas de coupure.

## Deroule

1. Projeter les deux prompts cote a cote. Faire remarquer le rapport de
   longueur avant meme de montrer les images.
2. Ouvrir les deux images cote a cote.
3. Demander au groupe quels elements du prompt detaille se retrouvent
   visiblement dans la seconde image.

## Le point technique souvent ignore

Certains services de generation **reecrivent le prompt** avant de generer.
Le script affiche ce prompt reecrit quand il est renvoye par l'API. Le
montrer : le prompt execute n'est pas toujours celui qu'on a ecrit, ce qui
change tout quand on industrialise.

## La chute

Meme principe qu'au Jour 1 sur le code : la contrainte n'appauvrit pas le
resultat, elle le rend reproductible.
