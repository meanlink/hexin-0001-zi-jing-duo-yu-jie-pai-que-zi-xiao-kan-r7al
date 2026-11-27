from fastapi import HTTPException

from glyph.models import ProofState, required_glyphs


def proof_by_code(db, code, lock=False):
    suffix = " FOR UPDATE" if lock else ""
    proof = db.one("SELECT * FROM proofs WHERE code = %s" + suffix, (code,))
    if proof is None:
        raise HTTPException(404, "未找到铭牌稿")
    return proof


def all_proofs(db):
    return db.all(
        """SELECT code, location, copy_text, use_kind, revision, state
           FROM proofs ORDER BY code"""
    )


def register_proof(db, form):
    changed = db.execute(
        """INSERT INTO proofs (code, location, copy_text, use_kind)
           VALUES (%s, %s, %s, %s) ON CONFLICT (code) DO NOTHING""",
        (form.code, form.location, form.copy_text, form.use_kind),
    )
    if not changed:
        raise HTTPException(409, "铭牌稿编号已登记")
    return proof_by_code(db, form.code)


def require_draft(proof):
    if proof["state"] != ProofState.DRAFT:
        raise HTTPException(409, "已锁稿的铭牌不能改版或更换字体")


def require_revision(proof, revision):
    if proof["revision"] != revision:
        raise HTTPException(409, "稿件已有其他修订，请刷新后操作")


def revise(db, code, form):
    proof = proof_by_code(db, code, lock=True)
    require_draft(proof)
    require_revision(proof, form.revision)
    if form.copy_text == proof["copy_text"]:
        return proof
    db.execute(
        "UPDATE proofs SET copy_text = %s, revision = revision + 1 WHERE code = %s",
        (form.copy_text, code),
    )
    for glyph in set(required_glyphs(proof["copy_text"])) - set(required_glyphs(form.copy_text)):
        db.execute("DELETE FROM font_assignments WHERE proof_code = %s AND glyph = %s", (code, glyph))
    db.execute("DELETE FROM glyph_proposals WHERE proof_code = %s", (code,))
    return proof_by_code(db, code)
