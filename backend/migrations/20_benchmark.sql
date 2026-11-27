CREATE TABLE IF NOT EXISTS benchmark_batches (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    state VARCHAR(12) NOT NULL DEFAULT 'running' CHECK (state IN ('running', 'done')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS benchmark_single_running
    ON benchmark_batches (state) WHERE state = 'running';

CREATE TABLE IF NOT EXISTS benchmark_batch_proofs (
    batch_id INTEGER NOT NULL REFERENCES benchmark_batches(id),
    proof_code VARCHAR(20) NOT NULL REFERENCES proofs(code),
    PRIMARY KEY (batch_id, proof_code)
);

CREATE TABLE IF NOT EXISTS benchmark_batch_faces (
    batch_id INTEGER NOT NULL REFERENCES benchmark_batches(id),
    face_code VARCHAR(20) NOT NULL REFERENCES typefaces(code),
    PRIMARY KEY (batch_id, face_code)
);

CREATE TABLE IF NOT EXISTS benchmark_results (
    batch_id INTEGER NOT NULL,
    proof_code VARCHAR(20) NOT NULL,
    method VARCHAR(8) NOT NULL CHECK (method IN ('line', 'glyph')),
    tested INTEGER NOT NULL CHECK (tested >= 0),
    hits INTEGER NOT NULL CHECK (hits >= 0),
    PRIMARY KEY (batch_id, proof_code, method),
    FOREIGN KEY (batch_id, proof_code) REFERENCES benchmark_batch_proofs(batch_id, proof_code)
);
