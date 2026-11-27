from collections import defaultdict

from fastapi import HTTPException

from glyph.catalogue import all_faces, face_by_code, options
from glyph.models import permitted, required_glyphs
from glyph.proofs import proof_by_code, require_draft, require_revision


def assignments(db, code):
    rows = db.all(
        """SELECT a.glyph, f.code AS face_code, f.family, f.font_file, f.license_kind
           FROM font_assignments a JOIN typefaces f ON f.code = a.face_code
           WHERE a.proof_code = %s""",
        (code,),
    )
    return {row["glyph"]: row for row in rows}


def review_rows(db, proof):
    assigned = assignments(db, proof["code"])
    faces = all_faces(db)
    proposed = defaultdict(list)
    for row in db.all(
        """SELECT glyph, face_code, rank, similarity FROM glyph_proposals
           WHERE proof_code = %s AND revision = %s ORDER BY rank""",
        (proof["code"], proof["revision"]),
    ):
        proposed[row["glyph"]].append(row)
    return [
        {
            "glyph": glyph,
            "codepoint": f"U+{ord(glyph):04X}",
            "assigned": assigned.get(glyph),
            "eligible": glyph in assigned and permitted(proof["use_kind"], assigned[glyph]["license_kind"]),
            "options": options(faces, glyph, proof["use_kind"]),
            "proposals": proposed[glyph],
        }
        for glyph in required_glyphs(proof["copy_text"])
    ]


def assign(db, code, glyph, form):
    proof = proof_by_code(db, code, lock=True)
    require_draft(proof)
    require_revision(proof, form.revision)
    if glyph not in required_glyphs(proof["copy_text"]):
        raise HTTPException(409, "该字符不在当前铭牌稿上")
    face = face_by_code(db, form.face_code)
    if glyph not in face["coverage"]:
        raise HTTPException(409, "字库覆盖表中没有该字符")
    db.execute(
        """INSERT INTO font_assignments (proof_code, glyph, face_code) VALUES (%s, %s, %s)
           ON CONFLICT (proof_code, glyph) DO UPDATE SET face_code = EXCLUDED.face_code""",
        (code, glyph, face["code"]),
    )
    return {
        "glyph": glyph,
        "face_code": face["code"],
        "eligible": permitted(proof["use_kind"], face["license_kind"]),
    }


def lock_proof(db, code, revision, reviewer):
    proof = proof_by_code(db, code, lock=True)
    require_draft(proof)
    require_revision(proof, revision)
    assigned = assignments(db, code)
    glyphs = required_glyphs(proof["copy_text"])
    missing = [glyph for glyph in glyphs if glyph not in assigned]
    restricted = [
        glyph for glyph in glyphs
        if glyph in assigned and not permitted(proof["use_kind"], assigned[glyph]["license_kind"])
    ]
    if missing or restricted:
        reasons = []
        if missing:
            reasons.append("未指派：" + " ".join(missing))
        if restricted:
            reasons.append("无商用许可：" + " ".join(restricted))
        raise HTTPException(409, "；".join(reasons))
    db.execute(
        "UPDATE proofs SET state = 'locked', locked_by = %s, locked_at = CURRENT_TIMESTAMP WHERE code = %s",
        (reviewer, code),
    )
    return proof_by_code(db, code)
