# AGENTS.md

## Stack

JavaScript ES2022, modules ES natifs, tests avec Vitest. Pas de TypeScript.

## Commandes

- Tests : `npm test`
- Test unique : `npx vitest run src/validation.test.js`

## Conventions

- Fonctions pures : ne jamais muter un paramètre reçu.
- Toute fonction exportée a une JSDoc d'une ligne indiquant le type de retour.
- Nommage en français, comme le reste du module (`validerEmail`, pas
  `validateEmail`).
- Les constantes partagées sont exportées et réutilisées, jamais recopiées en
  littéral dans le corps d'une fonction.
- Un validateur retourne toujours `{ valide, raison }` : `raison` vaut `null`
  quand `valide` est `true`, une chaîne explicative sinon.
- Les tests vivent à côté du code, en `*.test.js`.

## Interdits

- Aucune dépendance externe : ni `validator`, ni `zod`, ni `yup`.
- Une regex unique et opaque ne remplace pas des vérifications nommées. Chaque
  cas rejeté doit être identifiable à la lecture du code.
- Pas de `var`, pas de `function` anonyme passée en callback sans nom explicite.
- Ne jamais modifier un test pour le faire passer. Si un test échoue, c'est
  l'implémentation qui change.

## Ordre de travail imposé

1. Écrire le fichier de test AVANT toute implémentation.
2. Lancer `npm test` et constater l'échec.
3. Implémenter jusqu'au vert.
4. Ne rien annoncer comme terminé avant que `npm test` ne passe.

## Définition de terminée

Une fonction de validation n'est terminée que si les tests couvrent au minimum
une entrée par catégorie :

- entrée qui n'est pas une chaîne
- chaîne vide
- bornes de longueur : la limite exacte, et la limite plus un
- structure du séparateur : absent, présent plusieurs fois
- structure du domaine : sans point, point en tête, points consécutifs, point
  final
- espacement : en début, en fin, à l'intérieur
- au moins une entrée valide, pour vérifier que le validateur ne rejette pas
  tout

Chaque `raison` retournée désigne la cause réelle du rejet, jamais une cause
approchante. Un domaine vide n'est pas un « domaine sans point ».
