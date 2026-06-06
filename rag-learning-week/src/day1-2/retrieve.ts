/**
 * Retrieval via Postgres full-text search (ts_rank).
 *
 * This is a lexical retriever — it finds chunks that share keywords with the
 * query.  The interface is identical to the neural (pgvector cosine) version,
 * so swapping back is a one-file change once OpenAI is reachable.
 */
import { query } from "../db/client.js";

export interface RetrievedChunk {
  id: number;
  source: string;
  chunk_index: number;
  content: string;
  score: number;
}

export async function retrieve(
  queryText: string,
  topK = Number(process.env.TOP_K ?? 5)
): Promise<RetrievedChunk[]> {
  const rows = await query<RetrievedChunk>(
    `SELECT id, source, chunk_index, content,
            ts_rank(search_vector, plainto_tsquery('english', $1)) AS score
     FROM documents
     WHERE search_vector @@ plainto_tsquery('english', $1)
     ORDER BY score DESC
     LIMIT $2`,
    [queryText, topK]
  );

  // Fallback: if the strict tsquery matches nothing (e.g. single-word after
  // stop-word stripping), return the top-K by recency so the pipeline always
  // has context to work with.
  if (rows.length === 0) {
    const fallback = await query<RetrievedChunk>(
      `SELECT id, source, chunk_index, content, 0.01 AS score
       FROM documents ORDER BY id LIMIT $1`,
      [topK]
    );
    return fallback.map((r) => ({ ...r, score: Number(r.score) }));
  }

  // pg returns numeric/real columns as strings; coerce to number
  return rows.map((r) => ({ ...r, score: Number(r.score) }));
}
