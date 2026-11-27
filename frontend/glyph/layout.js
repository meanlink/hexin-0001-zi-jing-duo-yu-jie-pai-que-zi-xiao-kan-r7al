import { esc } from "../ui.js";
import { states, uses } from "./labels.js";

export function pilot(kicker, heading, description) {
  return `<header class="glyph-pilot"><p>${esc(kicker)}</p><h1>${esc(heading)}</h1><div>${esc(description)}</div></header>`;
}

export function proofMark(proof) {
  if (!proof) return "";
  return `<figure class="press-proof">
    <figcaption><span>${esc(proof.code)} · R${proof.revision}</span><span>${states[proof.state]}</span></figcaption>
    <div class="press-proof-copy">${esc(proof.copy_text)}</div>
    <p>${esc(proof.location)} · ${uses[proof.use_kind]}</p>
  </figure>`;
}

export function empty(text, link, label) {
  return `<p class="glyph-empty">${esc(text)} <a href="${link}">${esc(label)}</a></p>`;
}

export function fields(form) {
  return Object.fromEntries(new FormData(form).entries());
}

export function doAction(button, work, notify) {
  return async event => {
    event.preventDefault();
    button.disabled = true;
    try {
      await work();
    } catch (error) {
      notify(error.message);
    } finally {
      button.disabled = false;
    }
  };
}

export function feedback(root) {
  return text => {
    const node = root.querySelector("[data-feedback]");
    node.textContent = text;
    node.hidden = !text;
  };
}
