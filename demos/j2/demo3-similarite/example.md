
# Fusion par rang réciproque (Reciprocal Rank Fusion - RRF)



**Formule** :
```
score_RRF(document) = somme sur toutes les listes de : poids / (constante + rang)
```

Où :
- **rang** = position du document dans la liste (1, 2, 3...)
- **constante** = un paramètre (souvent 60) qui réduit l'impact des différences extrêmes entre les premières places.
- **poids** = importance accordée à chaque méthode (souvent 1 pour commencer).

## Exemple 

Imaginons que vous cherchiez "procédure astreinte serveur" et que vous ayez deux méthodes de recherche :

**Recherche lexicale (BM25)** :
1. Document A (score BM25 : 15,2)
2. Document B (score BM25 : 12,8)
3. Document C (score BM25 : 9,1)

**Recherche sémantique (vecteurs)** :
1. Document B (score cosinus : 0,94)
2. Document C (score cosinus : 0,89)
3. Document A (score cosinus : 0,76)

**Calcul RRF** (avec constante = 60, poids = 1) :

```
Document A :
  - Rang 1 en BM25 : 1 / (60 + 1) = 0,0164
  - Rang 3 en sémantique : 1 / (60 + 3) = 0,0159
  - Score RRF total = 0,0164 + 0,0159 = 0,0323

Document B :
  - Rang 2 en BM25 : 1 / (60 + 2) = 0,0161
  - Rang 1 en sémantique : 1 / (60 + 1) = 0,0164
  - Score RRF total = 0,0161 + 0,0164 = 0,0325

Document C :
  - Rang 3 en BM25 : 1 / (60 + 3) = 0,0159
  - Rang 2 en sémantique : 1 / (60 + 2) = 0,0161
  - Score RRF total = 0,0159 + 0,0161 = 0,0320
```

**Classement final** :
1. Document B (score RRF : 0,0325)
2. Document A (score RRF : 0,0323)
3. Document C (score RRF : 0,0320)

## Pourquoi ça marche

**Avantage 1** : Cela mélange les forces des deux méthodes. Le Document B était premier en sémantique et deuxième en lexical, donc il remporte le classement final grâce à sa régularité.

**Avantage 2** : La constante (60) évite qu'un document en première position domine trop. Sans la constante, le rang 1 donnerait 1/1 = 1,0, le rang 2 donnerait 1/2 = 0,5... la différence serait énorme. Avec la constante, 1/61 contre 1/62, la différence est plus douce et permet aux documents bien classés dans les deux listes de remonter.

**Avantage 3** : C'est simple et robuste. Pas besoin de normaliser les scores ou de comprendre leur échelle mathématique respective.

## Les paramètres à régler

**La constante** : 
- Valeur typique : 60.
- Plus petite = la première place compte beaucoup plus que les suivantes.
- Plus grande = les différences entre les rangs sont atténuées.

**Les poids** :
- Si vous voulez privilégier la recherche sémantique : poids_sémantique = 1,5, poids_lexical = 1,0.
- Si vous voulez privilégier la recherche lexicale (pour des termes techniques très précis) : poids_lexical = 1,5, poids_sémantique = 1,0.

## En résumé

La fusion par rang réciproque, c'est comme un vote : chaque méthode de recherche "vote" pour ses documents préférés, et le document qui cumule le plus de bons rangs remporte l'élection. C'est élégant parce que cela évite le problème insoluble de comparer des scores mathématiquement incomparables.

***

Souhaitez-vous que je régénère également l'intégralité du script de la journée avec les accents correctement restaurés ?