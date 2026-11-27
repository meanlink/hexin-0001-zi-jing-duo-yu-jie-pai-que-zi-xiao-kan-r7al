"""A/B scoring of retrieval contexts against locked font assignments.

Starting a batch circles the locked proofs and the catalogue as they stand;
proofs locked or faces registered afterwards wait for the next batch. Locked
copy, locked assignments, and face rows never change afterwards, so batch
membership alone pins every input. Each (proof, method) score commits on its
own, letting an interrupted batch resume without counting a proof twice.
"""
from fastapi import HTTPException

from glyph.models import required_glyphs
from glyph.retrieval import glyph_context, line_context, retrieve
from infra.db import tx

METHODS = {"line": line_context, "glyph": glyph_context}


def open_batch(db):
    return db.one("SELECT * FROM benchmark_batches WHERE state = 'running'")


def start_batch(db):
    """Return the running batch, creating and populating it when none exists."""
    created = db.one(
        "INSERT INTO benchmark_batches (state) VALUES ('running') ON CONFLICT DO NOTHING RETURNING *"
    )
    if created is None:
        return open_batch(db), False
    for proof in db.all("SELECT code FROM proofs WHERE state = 'locked' ORDER BY code"):
        db.execute(
            "INSERT INTO benchmark_batch_proofs (batch_id, proof_code) VALUES (%s, %s)",
            (created["id"], proof["code"]),
        )
    for face in db.all("SELECT code FROM typefaces ORDER BY code"):
        db.execute(
            "INSERT INTO benchmark_batch_faces (batch_id, face_code) VALUES (%s, %s)",
            (created["id"], face["code"]),
        )
    return created, True


def score_proof(proof, faces, assigned, context):
    """Count each glyph once; the locked font must rank in the top three."""
    ranked = {}
    for row in retrieve(proof["copy_text"], proof["use_kind"], faces, context):
        ranked.setdefault(row["glyph"], []).append(row["face_code"])
    tested, hits = 0, 0
    for glyph in required_glyphs(proof["copy_text"]):
        tested += 1
        if assigned.get(glyph) in ranked.get(glyph, []):
            hits += 1
    return tested, hits


def next_task(db, batch_id):
    return db.one(
        """SELECT bp.proof_code, m.method
           FROM benchmark_batch_proofs bp
           CROSS JOIN (SELECT 'line' AS method UNION ALL SELECT 'glyph') AS m
           WHERE bp.batch_id = %s AND NOT EXISTS (
               SELECT 1 FROM benchmark_results r
               WHERE r.batch_id = bp.batch_id AND r.proof_code = bp.proof_code
                 AND r.method = m.method)
           ORDER BY bp.proof_code, m.method
           LIMIT 1""",
        (batch_id,),
    )


def measure(payload):
    """Score one batch member per commit until both methods cover the batch."""
    batch_id = payload["batch_id"]
    while True:
        with tx() as db:
            if db.one("SELECT id FROM benchmark_batches WHERE id = %s", (batch_id,)) is None:
                raise HTTPException(404, "测评批次不存在")
            task = next_task(db, batch_id)
            if task is None:
                db.execute("UPDATE benchmark_batches SET state = 'done' WHERE id = %s", (batch_id,))
                return summary(db, batch_id)
            proof = db.one(
                "SELECT code, copy_text, use_kind FROM proofs WHERE code = %s",
                (task["proof_code"],),
            )
            faces = db.all(
                """SELECT t.* FROM benchmark_batch_faces bf
                   JOIN typefaces t ON t.code = bf.face_code
                   WHERE bf.batch_id = %s ORDER BY t.code""",
                (batch_id,),
            )
            assigned = {
                row["glyph"]: row["face_code"]
                for row in db.all(
                    "SELECT glyph, face_code FROM font_assignments WHERE proof_code = %s",
                    (proof["code"],),
                )
            }
            tested, hits = score_proof(proof, faces, assigned, METHODS[task["method"]])
            db.execute(
                """INSERT INTO benchmark_results (batch_id, proof_code, method, tested, hits)
                   VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
                (batch_id, proof["code"], task["method"], tested, hits),
            )


def summary(db, batch_id):
    batch = db.one("SELECT * FROM benchmark_batches WHERE id = %s", (batch_id,))
    counts = db.one(
        """SELECT
               (SELECT COUNT(*) FROM benchmark_batch_proofs WHERE batch_id = %s) AS proofs,
               (SELECT COUNT(*) FROM benchmark_batch_faces WHERE batch_id = %s) AS faces,
               (SELECT COUNT(*) FROM benchmark_results WHERE batch_id = %s) AS finished""",
        (batch_id, batch_id, batch_id),
    )
    methods = None
    if batch["state"] == "done":
        totals = {
            row["method"]: {"tested": row["tested"], "hits": row["hits"]}
            for row in db.all(
                """SELECT method, SUM(tested) AS tested, SUM(hits) AS hits
                   FROM benchmark_results WHERE batch_id = %s GROUP BY method""",
                (batch_id,),
            )
        }
        methods = {name: totals.get(name, {"tested": 0, "hits": 0}) for name in METHODS}
    return {
        "id": batch["id"],
        "state": batch["state"],
        "created_at": batch["created_at"],
        **counts,
        "methods": methods,
    }


def latest_summary(db):
    batch = db.one("SELECT id FROM benchmark_batches ORDER BY id DESC LIMIT 1")
    return summary(db, batch["id"]) if batch else None
