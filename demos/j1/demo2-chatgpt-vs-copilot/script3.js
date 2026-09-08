function validerEmail(valeur) {
  if (typeof valeur !== "string" || valeur.length === 0) {
    return { valide: false, raison: "La chaine est vide." };
  }
// 
  if (valeur !== valeur.trim()) {
    return { valide: false, raison: "La chaine contient des espaces en debut ou fin." };
  }

  if (valeur.length > 254) {
    return { valide: false, raison: "La chaine depasse 254 caracteres." };
  }

  // Recherche la position du premier "@" dans la chaine.
  // indexOf renvoie -1 si le caractere n'est pas trouve.
  const indexArobase = valeur.indexOf("@");
  if (indexArobase === -1) {
    return { valide: false, raison: "L'adresse ne contient pas d'arobase." };
  }

  const domaine = valeur.slice(indexArobase + 1);
  if (!domaine.includes(".")) {
    return { valide: false, raison: "Le domaine ne contient pas de point." };
  }

  return { valide: true, raison: null };
}
