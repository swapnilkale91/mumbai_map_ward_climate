/**
 * Day 4 — LLM extraction step: after each conversation turn, infer user traits
 * and write them to the user_model table.
 *
 * Run: tsx src/day4/extract.ts
 */
import Anthropic from "@anthropic-ai/sdk";
import pool from "../db/client.js";
import { upsertTraits, getUserModel, formatUserContext, UserTrait } from "./userModel.js";

const claude = new Anthropic();
const MODEL = process.env.CLAUDE_MODEL ?? "claude-haiku-4-5-20251001";

const EXTRACT_SYSTEM = `You extract user model traits from conversations.
Return ONLY valid JSON: { "traits": [{ "trait_key": string, "trait_value": string, "confidence": number }] }

Allowed trait_key values:
  - knowledge_level    (beginner / intermediate / advanced)
  - interest           (a topic the user seems curious about)
  - misconception      (a wrong belief the user holds)
  - goal               (what the user is trying to accomplish)
  - preferred_style    (e.g. "wants code examples", "prefers analogies")

confidence: 0.0–1.0, where 1.0 = stated explicitly, 0.5 = inferred.
Only emit traits with confidence >= 0.4. Return an empty array if nothing can be inferred.`;

export async function extractAndSaveTraits(
  userId: string,
  userMessage: string,
  assistantReply: string
): Promise<UserTrait[]> {
  const conversationSnippet = `User: ${userMessage}\nAssistant: ${assistantReply}`;

  const message = await claude.messages.create({
    model: MODEL,
    max_tokens: 512,
    system: EXTRACT_SYSTEM,
    messages: [
      {
        role: "user",
        content: `Extract traits from this exchange:\n\n${conversationSnippet}`,
      },
    ],
  });

  const rawText = message.content
    .filter((b) => b.type === "text")
    .map((b) => (b as Anthropic.TextBlock).text)
    .join("");

  // Extract the first {...} block to handle stray text around the JSON
  const jsonMatch = rawText.match(/\{[\s\S]*\}/);
  if (!jsonMatch) return [];
  const parsed = JSON.parse(jsonMatch[0]) as { traits: UserTrait[] };
  const traits = parsed.traits ?? [];

  if (traits.length > 0) {
    await upsertTraits(userId, traits);
  }

  return traits;
}

/**
 * Full personalised RAG turn:
 *   1. Load current user model
 *   2. Answer with RAG (imports answer.ts lazily to avoid circular deps)
 *   3. Extract new traits from the exchange
 */
export async function personalisedTurn(
  userId: string,
  question: string
): Promise<{ answer: string; newTraits: UserTrait[] }> {
  const { ragAnswer } = await import("../day1-2/answer.js");

  const existingTraits = await getUserModel(userId);
  const userContext = formatUserContext(existingTraits);

  // Prepend user context to the question so the RAG answer can personalise
  const augmentedQuestion = userContext
    ? `${userContext}\n\nQuestion: ${question}`
    : question;

  const { answer } = await ragAnswer(augmentedQuestion);
  const newTraits = await extractAndSaveTraits(userId, question, answer);

  return { answer, newTraits };
}

// ── CLI demo ─────────────────────────────────────────────────────────────────
if (process.argv[1]?.endsWith("extract.ts")) {
  const userId = "demo_user";
  const question = process.argv[2] ?? "I'm new to ML. Can you explain what loss functions do?";

  console.log(`\nUser ${userId}: "${question}"\n`);

  personalisedTurn(userId, question).then(async ({ answer, newTraits }) => {
    console.log("Answer:\n", answer);
    console.log("\nExtracted traits:");
    for (const t of newTraits) {
      console.log(`  ${t.trait_key}: ${t.trait_value} (${t.confidence.toFixed(2)})`);
    }
    const all = await getUserModel(userId);
    console.log(`\nFull user model (${all.length} traits):`);
    for (const t of all) console.log(`  ${t.trait_key}: ${t.trait_value}`);
    pool.end();
  }).catch((e) => { console.error(e); process.exit(1); });
}
