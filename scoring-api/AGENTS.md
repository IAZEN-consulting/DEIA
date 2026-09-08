# scoring-api

API de scoring client. Backend Python, front React embarque dans web/.

## Stack

- Python 3.12, FastAPI, SQLAlchemy, Pydantic v2
- Gestion des dependances : uv
- Tests : pytest
- Front : React 18 + TypeScript, Vite
- Base : PostgreSQL 16

## Commandes

| Action | Commande |
|---|---|
| Installer | `uv sync` |
| Ajouter une dependance | `uv add <paquet>` |
| Lancer l'API | `uv run uvicorn app.main:app --reload` |
| Tests | `uv run pytest` |
| Lint et format | `uv run ruff check . && uv run ruff format .` |
| Front | `cd web && npm run dev` |

## Interdits

- Jamais `pip`, `poetry` ou `conda`. `uv` uniquement.
- Aucune nouvelle dependance sans validation explicite en revue.
- Aucun secret en dur : tout passe par les variables d'environnement.
- Aucun acces direct a la base de production, meme en lecture.
- Ne pas modifier `uv.lock` a la main.

## Conventions

- Une PR = un sujet. Messages en conventional commits (`feat:`, `fix:`).
- Type hints obligatoires sur toute fonction publique.
- Les erreurs metier levent une exception dediee dans `app/errors.py`.
- Toute modification de code s'accompagne de ses tests.
- Ne jamais proposer de valider une modification sans avoir lance `uv run pytest`.

## Structure

- `app/api/` : routes FastAPI, aucune logique metier
- `app/services/` : logique metier, testable sans HTTP
- `app/models/` : modeles SQLAlchemy
- `tests/` : miroir de `app/`
- `web/` : front, autonome
