/**
 * Run once: creates the pgvector extension and all tables.
 *
 * Usage: tsx scripts/setup-db.ts
 */
import fs from "node:fs/promises";
import path from "node:path";
import pool from "../src/db/client.js";

async function main() {
  const schemaPath = path.resolve(import.meta.dirname ?? __dirname, "../src/db/schema.sql");
  const sql = await fs.readFile(schemaPath, "utf-8");

  console.log("Running schema.sql…");
  await pool.query(sql);
  console.log("Schema applied ✓");
  await pool.end();
}

main().catch((e) => { console.error(e); process.exit(1); });
