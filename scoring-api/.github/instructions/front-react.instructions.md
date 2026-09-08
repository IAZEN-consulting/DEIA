---
applyTo: "web/**/*.{ts,tsx}"
description: Conventions du front React
---

# Front React

- Composants fonctionnels uniquement. Pas de classe.
- Un composant par fichier, nomme en PascalCase.
- Props typees explicitement. `any` interdit.

## Etat et donnees

- Etat serveur : TanStack Query. Pas de `useEffect` pour aller chercher des donnees.
- Etat local : `useState`. Pas de store global sans discussion prealable.

## Style

- Tailwind uniquement. Pas de CSS-in-JS, pas de fichier `.css` nouveau.
- Aucune chaine de caracteres visible en dur : passer par `web/src/i18n/`.
