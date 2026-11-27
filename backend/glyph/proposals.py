from infra.db import tx

from glyph.catalogue import all_faces
from glyph.proofs import proof_by_code
from glyph.retrieval import retrieve


def generate(payload):
    code, revision = payload["code"], payload["revision"]
    with tx() as db:
        proof = proof_by_code(db, code)
        faces = all_faces(db)
    if proof["revision"] != revision or proof["state"] != "draft":
        return {"stale": True, "candidate_count": 0}
    rows = retrieve(proof["copy_text"], proof["use_kind"], faces)
    with tx() as db:
        latest = proof_by_code(db, code, lock=True)
        if latest["revision"] != revision or latest["state"] != "draft":
            return {"stale": True, "candidate_count": 0}
        db.execute("DELETE FROM glyph_proposals WHERE proof_code = %s AND revision = %s", (code, revision))
        for row in rows:
            db.execute(
                """INSERT INTO glyph_proposals
                   (proof_code, revision, glyph, face_code, rank, similarity)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (code, revision, row["glyph"], row["face_code"], row["rank"], row["similarity"]),
            )
    return {"stale": False, "candidate_count": len(rows)}
