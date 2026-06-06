/**
 * Day 4 — User model: read/write traits to the user_model table.
 *
 * Traits are open-ended key-value pairs the LLM extracts from conversation.
 * Examples:
 *   { trait_key: "knowledge_level",  trait_value: "intermediate" }
 *   { trait_key: "interest",         trait_value: "transformer architecture" }
 *   { trait_key: "misconception",    trait_value: "thinks attention is just pooling" }
 */
import { query } from "../db/client.js";

export interface UserTrait {
  trait_key: string;
  trait_value: string;
  confidence: number;
}

export interface UserModelRow extends UserTrait {
  id: number;
  user_id: string;
  updated_at: Date;
}

export async function getUserModel(userId: string): Promise<UserModelRow[]> {
  return query<UserModelRow>(
    `SELECT * FROM user_model WHERE user_id = $1 ORDER BY updated_at DESC`,
    [userId]
  );
}

/** Upsert a batch of traits for a user. */
export async function upsertTraits(userId: string, traits: UserTrait[]): Promise<void> {
  for (const t of traits) {
    await query(
      `INSERT INTO user_model (user_id, trait_key, trait_value, confidence, updated_at)
       VALUES ($1, $2, $3, $4, NOW())
       ON CONFLICT (user_id, trait_key, trait_value)
       DO UPDATE SET confidence = EXCLUDED.confidence, updated_at = NOW()`,
      [userId, t.trait_key, t.trait_value, t.confidence]
    );
  }
}

/** Build a short context string for injecting into prompts. */
export function formatUserContext(traits: UserModelRow[]): string {
  if (traits.length === 0) return "";
  const lines = traits.map(
    (t) => `  - ${t.trait_key}: ${t.trait_value} (confidence ${t.confidence.toFixed(2)})`
  );
  return `Known user traits:\n${lines.join("\n")}`;
}
