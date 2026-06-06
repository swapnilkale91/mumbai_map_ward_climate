# RAG Learning Week

A working, one-week MVP that takes you from zero to a grounded, truth-checking, user-aware AI tutor. All TypeScript / Node / PostgreSQL.

```
Day 1–2  Toy RAG       embed → pgvector → retrieve → answer with citations
Day 3    Truth layer   claim decomposition + per-claim verification
Day 4    User model    LLM extraction of traits after each turn
Day 5    Hardening     verify-then-remediate + anti-sycophancy constitution + 10 evals
```

---

## Prerequisites

| Tool | Version |
|------|---------|
| Node.js | ≥ 22 |
| Docker + Compose | any recent |
| OpenAI API key | for `text-embedding-3-small` |
| Anthropic API key | for Claude (generation, verification, extraction) |

---

## Quick Start

```bash
# 1. Clone and install
cd rag-learning-week
cp .env.example .env          # fill in OPENAI_API_KEY and ANTHROPIC_API_KEY
npm install

# 2. Start Postgres with pgvector
docker compose up -d
# Wait for: "database system is ready to accept connections"

# 3. Create tables
npm run setup-db

# 4. Embed and store the 20 sample docs
npm run ingest

# 5. Ask a question (Day 1-2 RAG)
npm run day1 "What is backpropagation?"

# 6. Verify an answer (Day 3)
npm run day3 "Backpropagation uses the chain rule to compute gradients."

# 7. Personalised turn with user model (Day 4)
npm run day4 "I'm new to ML. What is a loss function?"

# 8. Verify-then-remediate (Day 5)
npm run day5 "How does gradient descent work?"

# 9. Run the eval suite
npm run eval
```

---

## Project Structure

```
rag-learning-week/
├── docs/vidya/              20 sample markdown docs (the "corpus")
├── src/
│   ├── db/
│   │   ├── client.ts        pg Pool + pgvector registration
│   │   └── schema.sql       all tables (documents, claim_verifications, user_model, turns)
│   ├── day1-2/
│   │   ├── chunk.ts         word-boundary chunking with overlap
│   │   ├── embed.ts         OpenAI text-embedding-3-small batch embedder
│   │   ├── ingest.ts        chunk → embed → pgvector
│   │   ├── retrieve.ts      cosine-similarity search via pgvector <=>
│   │   └── answer.ts        RAG answer with [N] citations  ← npm run day1
│   ├── day3/
│   │   ├── decompose.ts     split answer into atomic checkable claims
│   │   └── verify.ts        per-claim retrieval + verdict + DB log  ← npm run day3
│   ├── day4/
│   │   ├── userModel.ts     CRUD for user_model table
│   │   └── extract.ts       LLM trait extraction + personalised turn  ← npm run day4
│   └── day5/
│       ├── constitution.ts  anti-sycophancy system-prompt block
│       ├── remediate.ts     verify-then-remediate pipeline  ← npm run day5
│       └── evals.ts         10 eval cases with LLM-as-judge  ← npm run eval
└── scripts/
    ├── setup-db.ts          apply schema.sql
    └── ingest-docs.ts       wrapper for ingest
```

---

## Day-by-Day Learning Guide

### Day 1–2: Basic RAG
**What you learn:** embeddings, chunking trade-offs, vector search, grounded generation.

Run `npm run ingest` then experiment with different questions via `npm run day1`.

Key files: `chunk.ts`, `embed.ts`, `retrieve.ts`, `answer.ts`

Questions to explore:
- What happens when you change `CHUNK_SIZE` and `CHUNK_OVERLAP`?
- What happens when `TOP_K=1` vs `TOP_K=10`?
- Ask a question not covered by the corpus — does the model say so?

### Day 3: Claim Verification
**What you learn:** structured LLM output, decomposing complex answers, grounding individual claims.

Run `npm run day3 "your answer text here"`. Look at the `claim_verifications` table.

Questions to explore:
- Feed it a subtly wrong answer. Does it catch the refuted claim?
- What fraction of claims land as "uncertain" vs "supported"?

### Day 4: User Model
**What you learn:** LLM extraction, upserting structured state, personalisation.

Run `npm run day4` twice with different questions from the same "user". Check the `user_model` table with `SELECT * FROM user_model;`.

Questions to explore:
- Does the model accumulate knowledge level correctly across turns?
- What trait confidence thresholds make sense?

### Day 5: Hardening
**What you learn:** anti-sycophancy prompting, remediation loops, eval harness design.

Run `npm run eval`. A pass rate ≥ 70% is a healthy starting point.

Questions to explore:
- Add your own eval case to `evals.ts`.
- Try removing the constitution from `remediate.ts` — does sycophancy increase?

---

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `ANTHROPIC_API_KEY` | — | Claude API (required) |
| `OPENAI_API_KEY` | — | Embeddings API (required) |
| `DATABASE_URL` | `postgresql://raguser:ragpass@localhost:5432/ragdb` | Postgres connection |
| `CLAUDE_MODEL` | `claude-haiku-4-5-20251001` | Which Claude model to use |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | OpenAI embedding model |
| `EMBEDDING_DIMS` | `1536` | Must match `schema.sql` vector size |
| `CHUNK_SIZE` | `400` | Words per chunk |
| `CHUNK_OVERLAP` | `80` | Words shared between adjacent chunks |
| `TOP_K` | `5` | Chunks retrieved per query |

---

## Extending to Your Own Docs

Replace `docs/vidya/` with your own markdown files, then re-run:
```bash
npm run ingest
```
No code changes needed.

---

## Tech Stack

| Layer | Choice | Why |
|-------|--------|-----|
| Language | TypeScript + tsx | Type safety, no compile step for dev |
| LLM | Anthropic Claude | Strong instruction following, JSON mode |
| Embeddings | OpenAI text-embedding-3-small | 1536 dims, cheap, high quality |
| Vector DB | pgvector on PostgreSQL | No new infra; SQL joins with metadata |
| Runtime | Node.js 22 | Familiar, async-first |
