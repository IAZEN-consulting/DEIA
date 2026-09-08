/**
 * Verifie qu'une chaine est une adresse electronique plausible.
 * @param {string} valeur - La chaine a valider.
 * @returns {{ valide: boolean, raison: string | null }}
 */
function validerEmail(valeur) {
  if (typeof valeur !== "string" || valeur.length === 0) {
    return { valide: false, raison: "La chaine est vide." };
  }

  if (valeur !== valeur.trim()) {
    return {
      valide: false,
      raison: "La chaine contient des espaces en debut ou en fin.",
    };
  }

  if (valeur.length > 254) {
    return {
      valide: false,
      raison: "La chaine depasse 254 caracteres.",
    };
  }

  const positionArobase = valeur.indexOf("@");
  if (positionArobase === -1) {
    return { valide: false, raison: "La chaine ne contient pas d'arobase." };
  }

  const domaine = valeur.slice(positionArobase + 1);
  if (!domaine.includes(".")) {
    return { valide: false, raison: "Le domaine ne contient pas de point." };
  }

  return { valide: true, raison: null };
}

module.exports = { validerEmail };
