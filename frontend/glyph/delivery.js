import { esc } from "../ui.js";
import { downloadManifest, glyphApi } from "./api.js";
import { currentProof, selectProof } from "./state.js";
import { doAction, empty, feedback, pilot, proofMark } from "./layout.js";

export async function delivery(root) {
  const proofs = (await glyphApi.proofs()).filter(proof => proof.state === "locked");
  const chosen = currentProof(proofs);
  root.classList.add("glyph-work");
  const heading = pilot("审校签收与切割交付", "交付清单", "导出已锁稿的字体文件与字符对应表，供招牌绘制和下料。");
  if (!chosen) {
    root.innerHTML = heading + empty("当前没有已锁稿的铭牌。", "/#review", "前往审校");
    return;
  }
  const manifest = await glyphApi.manifest(chosen.code);
  const signedAt = new Date(manifest.locked_at).toLocaleString("zh-CN", {timeZone: "Asia/Shanghai"});
  root.innerHTML = heading + `<div class="press-grid"><section>
      <h2>字体文件与刻字批次</h2><ol class="glyph-manifest">
      ${manifest.files.map(file => `<li><span><strong>${esc(file.family)}</strong>
        <code>${esc(file.font_file)} · ${esc(file.face_code)}</code></span><span class="manifest-word">${esc(file.glyphs)}</span>
      </li>`).join("")}</ol>
      <button id="export" type="button">下载交付 CSV</button>
      <p data-feedback class="glyph-feedback" role="status" hidden></p>
    </section><aside class="press-side">
      <label>锁稿归档<select data-proof-switch>${proofs.map(proof => `<option value="${esc(proof.code)}"
        ${proof.code === chosen.code ? "selected" : ""}>${esc(proof.code)} ｜ ${esc(proof.location)}</option>`).join("")}</select></label>
      ${proofMark(chosen)}
      <p class="press-foot">审校签字　${esc(manifest.locked_by)}<br>签发时间　${esc(signedAt)}</p>
    </aside></div>`;
  root.querySelector("[data-proof-switch]").onchange = async event => {
    selectProof(event.target.value);
    try {
      await delivery(root);
    } catch (error) {
      feedback(root)(error.message);
    }
  };
  const button = root.querySelector("#export");
  button.onclick = doAction(button, () => downloadManifest(manifest.code, manifest.revision), feedback(root));
}
