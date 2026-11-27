import { esc } from "../ui.js";

function candidateNames(row) {
  const options = new Map(row.options.map(face => [face.code, face.family]));
  const candidates = row.proposals.map(item => `<li>${esc(options.get(item.face_code) ?? item.face_code)} · ${(item.similarity * 100).toFixed(1)}%</li>`);
  return candidates.length ? `<ol class="glyph-rank">${candidates.join("")}</ol>` : "<small>暂无检索候选</small>";
}

export function glyphCell(row, editable) {
  const status = row.assigned ? row.eligible ? "许可已核" : "授权不符" : "待指派";
  const options = row.options.map(face => {
    const selection = row.assigned?.face_code === face.code ? " selected" : "";
    return `<option value="${esc(face.code)}"${selection}>${esc(face.family)}${face.eligible ? "" : " · 限公共"}</option>`;
  }).join("");
  return `<article class="glyph-cell">
    <div><strong class="glyph-tile">${esc(row.glyph)}</strong><code>${esc(row.codepoint)}</code></div>
    <div><p class="${row.eligible ? "ok" : "flag"}">${esc(row.assigned?.family ?? "")} ${status}</p>${candidateNames(row)}</div>
    ${editable && options ? `<form data-glyph="${esc(row.glyph)}">
      <select name="face_code" aria-label="${esc(row.glyph)}的字体"><option disabled value=""${row.assigned ? "" : " selected"}>选择字库</option>${options}</select>
      <button type="submit">保存指派</button></form>` : ""}
  </article>`;
}
