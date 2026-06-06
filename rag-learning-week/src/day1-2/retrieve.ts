import { query } from "../db/client.js";
import { embedOne } from "./embed.js";
import pgvector from "pgvector/pg";

export interface RetrievedChunk {
  id: number;
  source: string;
  chunk_index: number;
  content: string;
  score: number; // cosine similarity 0–1 (higher = more relevant)
}

/**
 * Embed the query, then return the top-k most similar document chunks.
 * Uses pgvector's <=> operator (cosine distance); score = 1 - distance.
 */
export async function retrieve(
  queryText: string,
  topK = Number(process.env.TOP_K ?? 5)
): Promise<RetrievedChunk[]> {
  const vec = await embedOne(queryText);
  const sql = pgvector.toSql(vec);

  const rows = await query<RetrievedChunk & { distance: number }>(
    `SELECT id, source, chunk_index, content,
            1 - (embedding <=> $1::vector) AS score
     FROM documents
     ORDER BY embedding <=> $1::vector
     LIMIT $2`,
    [sql, topK]
  );

  return rows.map(({ distance: _d, ...r }) => r);
}
