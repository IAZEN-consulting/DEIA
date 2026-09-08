---
applyTo: "tests/**/*.py"
description: Regles de redaction des tests Python
---

# Regles de test

- Un test verifie un seul comportement. Pas de test qui valide trois choses.
- Nom explicite : `test_<sujet>_<condition>_<resultat_attendu>`.
  Exemple : `test_score_client_sans_historique_retourne_valeur_par_defaut`.
- Structure Arrange / Act / Assert, separee par une ligne vide.

## Isolation

- Aucun appel reseau reel. `httpx` est mocke via `respx`.
- Aucun acces a une base reelle : fixture `session_test` de `conftest.py`.
- Pas de dependance a l'ordre d'execution ni a la date du jour.

## Fixtures

- Toute fixture partagee vit dans `tests/conftest.py`. Jamais dupliquee.
- Les jeux de donnees vont dans `tests/fixtures/`, jamais en dur dans le test.

## Couverture

- Chaque service expose dans `app/services/` a au moins un cas nominal
  et un cas d'erreur.
