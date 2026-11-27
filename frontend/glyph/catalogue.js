import { can, esc } from "../ui.js";
import { glyphApi } from "./api.js";
import { licenses } from "./labels.js";
import { doAction, feedback, fields, pilot } from "./layout.js";

function specimen(face) {
  return `<figure class="face-specimen">
    <figcaption><span>${esc(face.code)}</span><span>${licenses[face.license_kind]}</span></figcaption>
    <h3>${esc(face.family)}</h3>
    <div class="specimen-run">${esc(face.specimen)}</div>
    <details><summary>覆盖表 · ${Array.from(face.coverage).length} 个字符</summary><p>${esc(face.coverage)}</p></details>
    <p class="press-foot"><code>${esc(face.font_file)}</code></p>
  </figure>`;
}

function faceForm() {
  return `<form data-face>
    <label>包编号<input name="code" maxlength="20" pattern="[A-Z][A-Z0-9\\-]+" placeholder="HAN-N" required></label>
    <label>字库名<input name="family" maxlength="100" required></label>
    <label>用途许可<select name="license_kind">
      ${Object.entries(licenses).map(([key, name]) => `<option value="${key}">${name}</option>`).join("")}</select></label>
    <label>覆盖字表<textarea name="coverage" maxlength="8000" placeholder="松桥东巷안내" required></textarea></label>
    <label>权威样张文字<textarea name="specimen" maxlength="3000" placeholder="松桥东巷 안내" required></textarea></label>
    <label>字体文件名<input name="font_file" maxlength="100" placeholder="songqiao.otf" required></label>
    <button type="submit">登记字库包</button>
  </form>`;
}

export async function catalogue(root) {
  const faces = await glyphApi.faces();
  root.classList.add("glyph-work");
  root.innerHTML = pilot("字体库与使用许可", "铅字柜", "登记印制方确认过的字符覆盖、样张与字体文件名。")
    + `<div class="press-grid">
      <section aria-label="字库样册" class="face-shelf">${faces.map(specimen).join("") || "<p>请先登记一个字库包。</p>"}</section>
      <aside class="press-side"><h2>登记新字库包</h2>
        <p class="press-foot">已登记的包会保留其授权和文件名。许可变更或新增覆盖时，请登记新编号。</p>
        ${can("operator", "admin") ? faceForm() : "<p>当前账号可查阅样册。</p>"}
        <p data-feedback class="glyph-feedback" role="status" hidden></p>
      </aside>
    </div>`;
  const form = root.querySelector("[data-face]");
  if (form) {
    form.onsubmit = doAction(form.querySelector("button"), async () => {
      const face = await glyphApi.addFace(fields(form));
      await catalogue(root);
      feedback(root)(face.family + " 已登记。建议回到逐字审校更新候选。");
    }, feedback(root));
  }
}
