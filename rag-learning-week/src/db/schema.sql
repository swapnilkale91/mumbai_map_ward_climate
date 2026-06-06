-- ────────────────────────────────────────────────
-- 0. Extension
-- ────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS vector;

-- ────────────────────────────────────────────────
-- 1. Day 1-2: document chunks + embeddings
-- ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS documents (
  id          BIGSERIAL PRIMARY KEY,
  source      TEXT NOT NULL,          -- filename, e.g. "01-ml-basics.md"
  chunk_index INT  NOT NULL,          -- 0-based within source
  content     TEXT NOT NULL,          -- raw chunk text
  embedding   vector(1536),           -- text-embedding-3-small
  created_at  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS documents_embedding_idx
  ON documents USING ivfflat (embedding vector_cosine_ops)
  WITH (lists = 50);

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
