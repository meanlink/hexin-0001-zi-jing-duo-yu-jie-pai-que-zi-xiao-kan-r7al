"""Build the cutter's fixed font-file manifest from locked glyph assignments."""
import csv
import io
from collections import defaultdict

from fastapi import HTTPException

from glyph.models import ProofState, required_glyphs
from glyph.review import assignments


def manifest(db, proof):
    if proof["state"] != ProofState.LOCKED:
        raise HTTPException(409, "审校员锁稿后才能出单")
    assigned = assignments(db, proof["code"])
    groups = defaultdict(list)
    for glyph in required_glyphs(proof["copy_text"]):
        groups[assigned[glyph]["face_code"]].append(glyph)
    return {
        "code": proof["code"],
        "copy_text": proof["copy_text"],
        "revision": proof["revision"],
        "locked_by": proof["locked_by"],
        "locked_at": proof["locked_at"],
        "files": [
            {
                "face_code": code,
                "family": assigned[glyphs[0]]["family"],
                "font_file": assigned[glyphs[0]]["font_file"],
                "glyphs": "".join(glyphs),
            }
            for code, glyphs in groups.items()
        ],
    }


def manifest_csv(document):
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(["proof", "revision", "font_code", "font_file", "glyphs"])
    for file in document["files"]:
        glyphs = file["glyphs"]
        if glyphs.startswith(("=", "+", "-", "@", "\t", "\r")):
            glyphs = "'" + glyphs
        writer.writerow([document["code"], document["revision"], file["face_code"], file["font_file"], glyphs])
    return "\ufeff" + stream.getvalue()
