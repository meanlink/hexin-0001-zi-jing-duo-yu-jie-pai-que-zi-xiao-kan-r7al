CREATE TABLE IF NOT EXISTS proofs (
    code VARCHAR(20) PRIMARY KEY,
    location VARCHAR(100) NOT NULL,
    copy_text VARCHAR(240) NOT NULL,
    use_kind VARCHAR(15) NOT NULL CHECK (use_kind IN ('commercial', 'public')),
    revision INTEGER NOT NULL DEFAULT 1 CHECK (revision > 0),
    state VARCHAR(12) NOT NULL DEFAULT 'draft' CHECK (state IN ('draft', 'locked')),
    locked_by VARCHAR(120),
    locked_at TIMESTAMPTZ,
    CHECK (
        (state = 'draft' AND locked_by IS NULL AND locked_at IS NULL) OR
        (state = 'locked' AND locked_by IS NOT NULL AND locked_at IS NOT NULL)
    )
);

CREATE TABLE IF NOT EXISTS typefaces (
    code VARCHAR(20) PRIMARY KEY,
    family VARCHAR(100) NOT NULL,
    license_kind VARCHAR(15) NOT NULL CHECK (license_kind IN ('open', 'public_only')),
    coverage TEXT NOT NULL CHECK (LENGTH(coverage) > 0),
    specimen TEXT NOT NULL CHECK (LENGTH(specimen) > 0),
    font_file VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS font_assignments (
    proof_code VARCHAR(20) NOT NULL REFERENCES proofs(code),
    glyph VARCHAR(1) NOT NULL,
    face_code VARCHAR(20) NOT NULL REFERENCES typefaces(code),
    PRIMARY KEY (proof_code, glyph)
);

CREATE TABLE IF NOT EXISTS glyph_proposals (
    proof_code VARCHAR(20) NOT NULL REFERENCES proofs(code),
    revision INTEGER NOT NULL CHECK (revision > 0),
    glyph VARCHAR(1) NOT NULL,
    face_code VARCHAR(20) NOT NULL REFERENCES typefaces(code),
    rank INTEGER NOT NULL CHECK (rank > 0),
    similarity DOUBLE PRECISION NOT NULL CHECK (similarity >= 0 AND similarity <= 1),
    PRIMARY KEY (proof_code, revision, glyph, face_code),
    UNIQUE (proof_code, revision, glyph, rank)
);
