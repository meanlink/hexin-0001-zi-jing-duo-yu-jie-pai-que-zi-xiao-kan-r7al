const key = "glyph.selected.proof";

export function currentProof(proofs, predicate = () => true) {
  const choices = proofs.filter(predicate);
  const selected = sessionStorage.getItem(key);
  return choices.find(proof => proof.code === selected)
    ?? choices.find(proof => proof.code === "SQ-102")
    ?? choices[0] ?? null;
}

export function selectProof(code) {
  sessionStorage.setItem(key, code);
}
