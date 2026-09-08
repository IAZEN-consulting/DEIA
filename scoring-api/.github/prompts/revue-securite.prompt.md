---
mode: revue
description: Revue de securite d'un fichier ou d'une PR
---

# Revue de securite

Analyse le code fourni sur les points ci-dessous, et uniquement ceux-la.

## Points de controle

1. **Secrets** : cle, token, mot de passe, URL de connexion en dur.
   Verifier aussi les valeurs par defaut dans les `Settings` Pydantic.
2. **Injection SQL** : toute requete construite par concatenation ou f-string.
   Le projet utilise SQLAlchemy : signaler tout `text()` non parametre.
3. **Validation des entrees** : chaque route FastAPI recoit-elle un modele
   Pydantic, ou des parametres bruts ?
4. **Autorisation** : la route verifie-t-elle que l'appelant a le droit
   d'acceder a la ressource demandee, et pas seulement qu'il est authentifie ?
5. **Fuite d'information** : trace d'exception, identifiant interne ou
   requete SQL renvoyes dans une reponse HTTP ou un log.
6. **Dependances** : import d'un paquet absent de `pyproject.toml`.

## Forme de la reponse

Un tableau : Severite | Fichier:ligne | Probleme | Correction proposee.

Severite : critique, majeur, mineur.

Si un point de controle ne s'applique pas au fichier, ecris "non applicable"
plutot que de l'omettre.

Ne signale rien en dehors de ces six points.
