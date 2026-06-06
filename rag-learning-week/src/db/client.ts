import { Pool } from "pg";
import pgvector from "pgvector/pg";

const pool = new Pool({
  connectionString: process.env.DATABASE_URL ?? "postgresql://raguser:ragpass@localhost:5432/ragdb",
  max: 10,
});

// Register pgvector type so pg returns real JS arrays, not strings
pool.on("connect", (client) => {
  pgvector.registerType(client);
});

export default pool;

export async function query<T = Record<string, unknown>>(
  sql: string,
  params?: unknown[]
): Promise<T[]> {
  const result = await pool.query(sql, params);
  return result.rows as T[];
}
