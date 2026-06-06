/**
 * Day 3 — Claim decomposition.
 *
 * Splits an LLM answer into atomic, independently verifiable claims.
 * Returns structured JSON from Claude so we can loop over claims in verify.ts.
 */
import Anthropic from "@anthropic-ai/sdk";

const claude = new Anthropic();
const MODEL = process.env.CLAUDE_MODEL ?? "claude-haiku-4-5-20251001";

export interface Claim {
  text: string;        // e.g. "Gradient descent minimises a loss function"
  checkable: boolean;  // false for opinions/hedges ("it is generally believed…")
}

const SYSTEM = `You decompose text into atomic factual claims.
Return ONLY valid JSON: { "claims": [{ "text": string, "checkable": boolean }] }
Each claim must be a single, self-contained factual statement.
Mark checkable=false for vague opinions or purely definitional tautologies.`;

export async function decomposeClaims(answerText: string): Promise<Claim[]> {
  const message = await claude.messages.create({
    model: MODEL,
    max_tokens: 1024,
    system: SYSTEM,
    messages: [
      {
        role: "user",
        content: `Decompose this answer into atomic claims:\n\n${answerText}`,
      },
    ],
  });

  const raw = message.content
    .filter((b) => b.type === "text")
    .map((b) => (b as Anthropic.TextBlock).text)
    .join("")
    .trim();

  const jsonMatch = raw.match(/\{[\s\S]*\}/);
  if (!jsonMatch) return [];
  const parsed = JSON.parse(jsonMatch[0]) as { claims: Claim[] };
  return parsed.claims ?? [];
}
