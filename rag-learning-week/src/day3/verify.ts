/**
 * Day 3 — Claim verification layer.
 *
 * For each checkable claim:
 *   1. Retrieve top-K chunks relevant to the claim.
 *   2. Ask Claude: is this claim supported, refuted, or uncertain given the evidence?
 *   3. Log the verdict to claim_verifications.
 *
 * Run: tsx src/day3/verify.ts "Backpropagation uses the chain rule."
 */
import Anthropic from "@anthropic-ai/sdk";
import pool, { query } from "../db/client.js";
import { retrieve } from "../day1-2/retrieve.js";
import { decomposeClaims, Claim } from "./decompose.js";

const claude = new Anthropic();
const MODEL = process.env.CLAUDE_MODEL ?? "claude-haiku-4-5-20251001";

export type Verdict = "supported" | "refuted" | "uncertain";

export interface VerificationResult {
  claim: string;
  verdict: Verdict;
  explanation: string;
  evidence_sources: string[];
}

const VERIFY_SYSTEM = `You are a strict fact-checker.
Given a claim and evidence passages, return ONLY valid JSON:
{ "verdict": "supported"|"refuted"|"uncertain", "explanation": string }
- supported: the evidence clearly supports the claim
- refuted:   the evidence clearly contradicts the claim
- uncertain: evidence is missing, ambiguous, or partial`;

async function verifyClaim(
  claim: Claim,
  sessionId: string
): Promise<VerificationResult> {
  if (!claim.checkable) {
    return {
      claim: claim.text,
      verdict: "uncertain",
      explanation: "Claim marked non-checkable (opinion/hedge).",
      evidence_sources: [],
    };
  }

  const chunks = await retrieve(claim.text, 4);
  const evidence = chunks
    .map((c, i) => `[${i + 1}] ${c.source}:\n${c.content}`)
    .join("\n\n");

  const message = await claude.messages.create({
    model: MODEL,
    max_tokens: 512,
    system: VERIFY_SYSTEM,
    messages: [
      {
        role: "user",
        content: `Claim: "${claim.text}"\n\nEvidence:\n${evidence}`,
      },
    ],
  });

  const rawText = message.content
    .filter((b) => b.type === "text")
    .map((b) => (b as Anthropic.TextBlock).text)
    .join("");

  const jsonMatch = rawText.match(/\{[\s\S]*\}/);
  if (!jsonMatch) return { claim: claim.text, verdict: "uncertain" as Verdict, explanation: "Parse error", evidence_sources: [] };
  const parsed = JSON.parse(jsonMatch[0]) as { verdict: Verdict; explanation: string };

  // Persist to DB
  await query(
    `INSERT INTO claim_verifications (session_id, claim, verdict, evidence)
     VALUES ($1, $2, $3, $4)`,
    [sessionId, claim.text, parsed.verdict, chunks.map((c) => c.id).join(",")]
  );

  return {
    claim: claim.text,
    verdict: parsed.verdict,
    explanation: parsed.explanation,
    evidence_sources: chunks.map((c) => c.source),
  };
}

export async function verifyAnswer(
  answerText: string,
  sessionId = `session_${Date.now()}`
): Promise<VerificationResult[]> {
  const claims = await decomposeClaims(answerText);
  const results: VerificationResult[] = [];

  for (const claim of claims) {
    const result = await verifyClaim(claim, sessionId);
    results.push(result);
  }

  return results;
}

// ── CLI ──────────────────────────────────────────────────────────────────────
if (process.argv[1]?.endsWith("verify.ts")) {
  const text = process.argv[2] ?? "Backpropagation uses the chain rule to compute gradients.";
  console.log(`\nVerifying: "${text}"\n`);

  verifyAnswer(text).then((results) => {
    for (const r of results) {
      const icon = r.verdict === "supported" ? "✓" : r.verdict === "refuted" ? "✗" : "?";
      console.log(`${icon} [${r.verdict}] ${r.claim}`);
      console.log(`  ${r.explanation}\n`);
    }
    pool.end();
  }).catch((e) => { console.error(e); process.exit(1); });
}
