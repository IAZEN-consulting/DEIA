function validerEmail(valeur) {
  if (valeur === "") {
    return { valide: false, raison: "La chaîne est vide" };
  }

  if (valeur.trim() !== valeur) {
    return { valide: false, raison: "L'adresse contient des espaces en début ou en fin" };
  }

  if (valeur.length > 254) {
    return { valide: false, raison: "L'adresse dépasse 254 caractères" };
  }

  if (!valeur.includes("@")) {
    return { valide: false, raison: "L'adresse ne contient pas d'arobase" };
  }

  const parties = valeur.split("@");

  if (parties.length !== 2 || parties[0] === "" || parties[1] === "") {
    return { valide: false, raison: "Format d'adresse invalide" };
  }

  const domaine = parties[1];

  if (!domaine.includes(".")) {
    return { valide: false, raison: "Le domaine ne contient pas de point" };
  }

  return { valide: true, raison: null };
}