from fastapi import HTTPException

from glyph.models import permitted


def all_faces(db):
    return db.all("SELECT * FROM typefaces ORDER BY code")


def face_by_code(db, code):
    face = db.one("SELECT * FROM typefaces WHERE code = %s", (code,))
    if face is None:
        raise HTTPException(404, "未找到所选字库")
    return face


def register_face(db, form):
    changed = db.execute(
        """INSERT INTO typefaces (code, family, license_kind, coverage, specimen, font_file)
           VALUES (%s, %s, %s, %s, %s, %s) ON CONFLICT (code) DO NOTHING""",
        (form.code, form.family, form.license_kind, form.coverage, form.specimen, form.font_file),
    )
    if not changed:
        raise HTTPException(409, "字库包编号已登记")
    return face_by_code(db, form.code)


def options(faces, glyph, use_kind):
    return [
        {
            "code": face["code"],
            "family": face["family"],
            "eligible": permitted(use_kind, face["license_kind"]),
        }
        for face in faces
        if glyph in face["coverage"]
    ]
