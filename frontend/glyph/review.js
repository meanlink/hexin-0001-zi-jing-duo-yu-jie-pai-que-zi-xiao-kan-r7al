import { can, esc } from "../ui.js";
import { glyphApi } from "./api.js";
import { currentProof, selectProof } from "./state.js";
import { states } from "./labels.js";
import { doAction, empty, feedback, fields, pilot, proofMark } from "./layout.js";
import { glyphCell } from "./glyph-cell.js";

const feedbackBlock = '<p data-feedback class="glyph-feedback" role="status" hidden></p>';

export async function review(root) {
  const proofs = await glyphApi.proofs();
  const chosen = currentProof(proofs);
  root.classList.add("glyph-work");
  const heading = pilot("字形覆盖与打样许可", "逐字审校", "用样张上下文检索字库，再逐字确认实际字体。");
  if (!chosen) {
    root.innerHTML = heading + empty("没有可审校的稿件。", "/#desk", "去稿台登记");
    return;
  }
  const {proof, glyphs} = await glyphApi.review(chosen.code);
  const revision = proof.revision;
  const editable = proof.state === "draft" && can("operator", "admin");
  const lockable = proof.state === "draft" && can("admin");
  const covered = glyphs.filter(row => row.eligible).length;
  root.innerHTML = heading + `<div class="press-control">
    <label>选择稿件<select data-proof-switch>${proofs.map(item => `<option value="${esc(item.code)}"
      ${item.code === proof.code ? "selected" : ""}>${esc(item.code)} ｜ ${esc(item.location)} · ${states[item.state]}</option>`).join("")}</select></label>
    ${editable ? '<button id="rank" type="button">检索样张候选</button>' : ""}
  </div>${feedbackBlock}
  <div class="press-grid">
    <section><h2>指派清样 · ${covered}/${glyphs.length}</h2>
      <div class="glyph-strip">${glyphs.map(row => glyphCell(row, editable)).join("")}</div>
    </section>
    <aside class="press-side">${proofMark(proof)}
      ${editable ? `<form data-revision><h2>修订抄件</h2>
        <label>铭牌文字<textarea name="copy_text" maxlength="240" required>${esc(proof.copy_text)}</textarea></label>
        <button type="submit">保存新稿</button></form>` : ""}
      ${lockable ? `<div class="signoff"><h2>交给下道工序</h2><p class="press-foot">审校员签字前，每个可见字符都必须有符合用途许可的字体。</p>
        <button id="lock" type="button">锁稿签发</button></div>` : ""}
      ${proof.state === "locked" ? '<a class="press-link" href="/#delivery">查看交付清单</a>' : ""}
    </aside>
  </div>`;
  root.querySelector("[data-proof-switch]").onchange = async event => {
    selectProof(event.target.value);
    try {
      await review(root);
    } catch (error) {
      feedback(root)(error.message);
    }
  };
  const action = (control, work) => doAction(control, async () => {
    const text = await work();
    await review(root);
    feedback(root)(text);
  }, feedback(root));
  const rank = root.querySelector("#rank");
  if (rank) rank.onclick = action(rank, async () => {
    feedback(root)("正在检索样张……");
    const result = await glyphApi.rank(proof.code, revision);
    return result.stale ? "已切换到最新稿件，请重新检索。" : `检索完毕，记录 ${result.candidate_count} 条候选。`;
  });
  const lock = root.querySelector("#lock");
  if (lock) lock.onclick = action(lock, async () => {
    await glyphApi.lock(proof.code, revision);
    return "锁稿成功。交付清单已可下载。";
  });
  const edit = root.querySelector("[data-revision]");
  if (edit) edit.onsubmit = action(edit.querySelector("button"), async () => {
    const revised = await glyphApi.revise(proof.code, {...fields(edit), revision});
    return "已保存 R" + revised.revision + "。";
  });
  root.querySelectorAll("[data-glyph]").forEach(form => {
    form.onsubmit = action(form.querySelector("button"), async () => {
      const result = await glyphApi.assign(proof.code, {glyph: form.dataset.glyph, revision, ...fields(form)});
      return result.eligible ? result.glyph + " 已指派并通过许可校验。" : result.glyph + " 所用字库限公共用途。锁稿前请选择其他字库。";
    });
  });
}
