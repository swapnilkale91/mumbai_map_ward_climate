-- ────────────────────────────────────────────────
-- 0. Extension (kept for when neural embeddings are re-enabled)
-- ────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS vector;

-- ────────────────────────────────────────────────
-- 1. Day 1-2: document chunks + full-text search
--    search_vector is a generated tsvector column — Postgres FTS replaces
--    neural embeddings when the OpenAI endpoint is not reachable.
--    To switch back to pgvector: add `embedding vector(1536)` and update
--    retrieve.ts to use cosine distance instead of ts_rank.
-- ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS documents (
  id             BIGSERIAL PRIMARY KEY,
  source         TEXT NOT NULL,
  chunk_index    INT  NOT NULL,
  content        TEXT NOT NULL,
  search_vector  tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
  created_at     TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS documents_fts_idx
  ON documents USING GIN (search_vector);

-- ────────────────────────────────────────────────
-- 2. Day 3: claim verification log
-- ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS claim_verifications (
  id            BIGSERIAL PRIMARY KEY,
  session_id    TEXT NOT NULL,
  claim         TEXT NOT NULL,
  verdict       TEXT NOT NULL CHECK (verdict IN ('supported', 'refuted', 'uncertain')),
  evidence      TEXT,                 -- chunk ids used as evidence
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

-- ────────────────────────────────────────────────
-- 3. Day 4: user model
-- ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_model (
  id          BIGSERIAL PRIMARY KEY,
  user_id     TEXT NOT NULL,
  trait_key   TEXT NOT NULL,          -- e.g. "knowledge_level", "interest", "misconception"
  trait_value TEXT NOT NULL,
  confidence  REAL NOT NULL DEFAULT 0.7 CHECK (confidence BETWEEN 0 AND 1),
  updated_at  TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (user_id, trait_key, trait_value)
);

CREATE INDEX IF NOT EXISTS user_model_user_idx ON user_model (user_id);

-- ────────────────────────────────────────────────
-- 4. Day 5: conversation turns (for eval harness)
-- ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS turns (
  id           BIGSERIAL PRIMARY KEY,
  session_id   TEXT NOT NULL,
  role         TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content      TEXT NOT NULL,
  created_at   TIMESTAMPTZ DEFAULT NOW()
);
