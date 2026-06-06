/**
 * Day 1-2 — Ingest: chunk → store in Postgres with tsvector FTS.
 * (Neural embedding variant: add embedBatch call and an `embedding` column.)
 *
 * Run: tsx src/day1-2/ingest.ts  or  npm run ingest
 */
import fs from "node:fs/promises";
import path from "node:path";
import pool, { query } from "../db/client.js";
import { chunkText } from "./chunk.js";

const DOCS_DIR = path.resolve(import.meta.dirname ?? __dirname, "../../docs/vidya");

async function ingestFile(filePath: string): Promise<void> {
  const source = path.basename(filePath);
  const text = await fs.readFile(filePath, "utf-8");
  const chunks = chunkText(text);

  for (const chunk of chunks) {
    await query(
      `INSERT INTO documents (source, chunk_index, content)
       VALUES ($1, $2, $3)
       ON CONFLICT DO NOTHING`,
      [source, chunk.index, chunk.content]
    );
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
