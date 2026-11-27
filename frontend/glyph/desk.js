import { can, esc } from "../ui.js";
import { glyphApi } from "./api.js";
import { currentProof, selectProof } from "./state.js";
import { states, useOptions, uses } from "./labels.js";
import { doAction, empty, feedback, fields, pilot, proofMark } from "./layout.js";

function intakeForm() {
  return `<form data-intake>
    <label>稿件编号<input name="code" pattern="[A-Z][A-Z0-9\\-]+" placeholder="SQ-120" maxlength="20" required></label>
    <label>安放位置<input name="location" placeholder="松桥东巷南口" maxlength="100" required></label>
    <label>铭牌用途<select name="use_kind">${useOptions()}</select></label>
    <label>最终印制文案 <textarea name="copy_text" placeholder="东巷 안내" maxlength="240" required></textarea></label>
    <button type="submit">登记稿件</button>
  </form>`;
}

export async function desk(root) {
  const proofs = await glyphApi.proofs();
  const chosen = currentProof(proofs);
  root.classList.add("glyph-work");
  root.innerHTML = pilot("收稿与登记", "铭牌稿台", "校对现场抄件，登记用途与多语言原文。")
    + `<div class="press-grid"><section>
      ${proofMark(chosen)}
      <h2>稿件索引</h2>
      ${proofs.length ? `<ul class="glyph-ledger">${proofs.map(proof => `<li>
        <span><strong>${esc(proof.location)}</strong><small>${esc(proof.code)} · ${uses[proof.use_kind]} · R${proof.revision} · ${states[proof.state]}</small></span>
        <a class="press-link" data-proof="${esc(proof.code)}" href="/#review">逐字审校</a></li>`).join("")}</ul>`
        : empty("稿台尚无记录。", "/#catalogue", "先查看可选字库")}
    </section><aside class="press-side"><h2>收一份新稿</h2>
      <p class="press-foot">公共路引和商用铭牌使用不同的字体授权。登记后在审校页改字并留住仍适用的指派。</p>
      ${can("operator", "admin") ? intakeForm() : "<p>当前账号可查阅稿件。</p>"}
      <p data-feedback class="glyph-feedback" role="status" hidden></p>
    </aside></div>`;
  root.querySelectorAll("[data-proof]").forEach(link => {
    link.onclick = () => selectProof(link.dataset.proof);
  });
  const form = root.querySelector("[data-intake]");
  if (form) {
    form.onsubmit = doAction(form.querySelector("button"), async () => {
      const proof = await glyphApi.addProof(fields(form));
      selectProof(proof.code);
      location.hash = "review";
    }, feedback(root));
  }
}
