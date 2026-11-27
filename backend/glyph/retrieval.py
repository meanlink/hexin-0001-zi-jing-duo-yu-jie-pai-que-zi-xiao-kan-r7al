"""Character n-gram retrieval for font packages.

Each font's specimen text is a document. Fits IDF across this catalogue,
transforms the per-glyph line context, and ranks eligible packages by cosine.
"""
from collections import Counter
from math import log, sqrt

from glyph.models import permitted, required_glyphs


def grams(text: str) -> Counter:
    cleaned = " ".join(text.casefold().split())
    return Counter(
        cleaned[offset:offset + length]
        for length in (1, 2, 3)
        for offset in range(len(cleaned) - length + 1)
    )


def weighted(counter: Counter, inverse: dict) -> dict:
    values = {
        gram: (1 + log(count)) * inverse[gram]
        for gram, count in counter.items()
        if gram in inverse
    }
    magnitude = sqrt(sum(weight ** 2 for weight in values.values()))
    return {gram: weight / magnitude for gram, weight in values.items()} if magnitude else {}


def retrieve(copy_text: str, use_kind: str, faces: list[dict]) -> list[dict]:
    corpus = [grams(face["specimen"]) for face in faces]
    frequency = Counter(gram for document in corpus for gram in document)
    inverse = {
        gram: 1 + log((1 + len(corpus)) / (1 + count))
        for gram, count in frequency.items()
    }
    vectors = [weighted(document, inverse) for document in corpus]
    candidates = []
    for glyph in required_glyphs(copy_text):
        context = " ".join(line for line in copy_text.splitlines() if glyph in line)
        query = weighted(grams(context), inverse)
        scored = [
            (min(1.0, sum(weight * vector.get(gram, 0) for gram, weight in query.items())), face["code"])
            for face, vector in zip(faces, vectors)
            if glyph in face["coverage"] and permitted(use_kind, face["license_kind"])
        ]
        for rank, (score, face_code) in enumerate(sorted(scored, key=lambda row: (-row[0], row[1]))[:3], 1):
            candidates.append({"glyph": glyph, "face_code": face_code, "rank": rank, "similarity": round(score, 5)})
    return candidates
