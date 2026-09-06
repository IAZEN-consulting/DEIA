# Enonce a utiliser pour les deux outils

Utiliser exactement le meme enonce des deux cotes, mot pour mot. Toute
difference de formulation fausserait la comparaison.

---

Ecris une fonction JavaScript `validerEmail(valeur)` qui verifie qu'une
chaine est une adresse electronique plausible. Elle retourne un objet
`{ valide: boolean, raison: string | null }`. Traite les cas suivants :
chaine vide, espaces en debut ou fin, absence d'arobase, domaine sans point,
et longueur superieure a 254 caracteres.

---

## Pourquoi cette tache

- Assez courte pour tenir en une suggestion, donc lisible a l'ecran.
- Assez precise pour que les cas limites soient verifiables en direct.
- Le sujet est archi-represente dans les corpus d'entrainement : les deux
  outils produiront quelque chose de correct, ce qui evite de transformer la
  demo en debat sur la qualite du modele et garde le focus sur le contexte.

## Variante si le groupe est plutot Python

Meme enonce, en remplacant la signature par `valider_email(valeur)` et le
retour par un tuple `(valide, raison)`.
