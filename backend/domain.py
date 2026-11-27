from fastapi import APIRouter, Depends
from fastapi.responses import Response

from glyph.benchmark import latest_summary, measure, start_batch
from glyph.catalogue import all_faces, register_face
from glyph.delivery import manifest, manifest_csv
from glyph.demo import seed
from glyph.proofs import all_proofs, proof_by_code, register_proof, require_draft, require_revision, revise
from glyph.proposals import generate
from glyph.review import assign, lock_proof, review_rows
from glyph.schemas import AssignmentForm, ProofForm, ProofRevision, ReviewVersion, TypefaceForm
from infra.auth import access
from infra.db import tx
from infra.queue import enqueue

router = APIRouter(dependencies=[Depends(access())])
editor = access("operator", "admin")
reviewer = access("admin")
JOBS = {"glyph_proposals": generate, "glyph_benchmark": measure}


@router.get("/proofs")
def proofs():
    with tx() as db:
        return all_proofs(db)


@router.post("/proofs", status_code=201, dependencies=[Depends(editor)])
def add_proof(form: ProofForm):
    with tx() as db:
        return register_proof(db, form)


@router.patch("/proofs/{code}", dependencies=[Depends(editor)])
def edit_proof(code: str, form: ProofRevision):
    with tx() as db:
        return revise(db, code, form)


@router.get("/typefaces")
def faces():
    with tx() as db:
        return all_faces(db)


@router.post("/typefaces", status_code=201, dependencies=[Depends(editor)])
def add_face(form: TypefaceForm):
    with tx() as db:
        return register_face(db, form)


@router.get("/proofs/{code}/review")
def review(code: str):
    with tx() as db:
        proof = proof_by_code(db, code, lock=True)
        return {"proof": proof, "glyphs": review_rows(db, proof)}


@router.post("/proofs/{code}/proposals", status_code=202, dependencies=[Depends(editor)])
def propose(code: str, form: ReviewVersion):
    with tx() as db:
        proof = proof_by_code(db, code)
        require_draft(proof)
        require_revision(proof, form.revision)
    return {"job_id": enqueue("glyph_proposals", {"code": code, "revision": form.revision})}


@router.put("/proofs/{code}/assignments", dependencies=[Depends(editor)])
def place(code: str, form: AssignmentForm):
    with tx() as db:
        return assign(db, code, form.glyph, form)


@router.post("/proofs/{code}/lock")
def lock(code: str, form: ReviewVersion, user=Depends(reviewer)):
    with tx() as db:
        return lock_proof(db, code, form.revision, user["email"])


@router.get("/proofs/{code}/manifest")
def delivery(code: str):
    with tx() as db:
        return manifest(db, proof_by_code(db, code))


@router.get("/proofs/{code}/manifest.csv")
def export_delivery(code: str):
    document = delivery(code)
    return Response(
        manifest_csv(document),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{document["code"]}-r{document["revision"]}.csv"'},
    )


@router.get("/benchmarks/latest")
def benchmark():
    with tx() as db:
        return {"batch": latest_summary(db)}


@router.post("/benchmarks", status_code=202, dependencies=[Depends(editor)])
def measure_batch():
    with tx() as db:
        batch, fresh = start_batch(db)
    return {
        "job_id": enqueue("glyph_benchmark", {"batch_id": batch["id"]}),
        "batch_id": batch["id"],
        "resumed": not fresh,
    }
