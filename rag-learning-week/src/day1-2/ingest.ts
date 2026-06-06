/**
 * Day 1-2 — Ingest: chunk → embed → store in pgvector.
 *
 * Run directly: tsx src/day1-2/ingest.ts
 * Or via:       npm run ingest
 */
import fs from "node:fs/promises";
import path from "node:path";
import pool, { query } from "../db/client.js";
import { chunkText } from "./chunk.js";
import { embedBatch } from "./embed.js";
import pgvector from "pgvector/pg";

const DOCS_DIR = path.resolve(import.meta.dirname ?? __dirname, "../../docs/vidya");
const BATCH_SIZE = 32; // chunks per embedding API call

async function ingestFile(filePath: string): Promise<void> {
  const source = path.basename(filePath);
  const text = await fs.readFile(filePath, "utf-8");
  const chunks = chunkText(text);

  // Embed in batches to stay within token limits
  for (let i = 0; i < chunks.length; i += BATCH_SIZE) {
    const batch = chunks.slice(i, i + BATCH_SIZE);
    const embeddings = await embedBatch(batch.map((c) => c.content));

    for (let j = 0; j < batch.length; j++) {
      await query(
        `INSERT INTO documents (source, chunk_index, content, embedding)
         VALUES ($1, $2, $3, $4)
         ON CONFLICT DO NOTHING`,
        [source, batch[j].index, batch[j].content, pgvector.toSql(embeddings[j])]
      );
    }
  }

  console.log(`  ✓ ${source}: ${chunks.length} chunks`);
}

async function main() {
  const files = (await fs.readdir(DOCS_DIR))
    .filter((f) => f.endsWith(".md"))
    .map((f) => path.join(DOCS_DIR, f));

  if (files.length === 0) {
    console.error(`No .md files found in ${DOCS_DIR}`);
    process.exit(1);
  }

  console.log(`Ingesting ${files.length} files from ${DOCS_DIR}…`);
  for (const f of files) await ingestFile(f);
  console.log("Done.");
  await pool.end();
}

main().catch((e) => { console.error(e); process.exit(1); });
