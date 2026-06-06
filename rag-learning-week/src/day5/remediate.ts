/**
 * Day 5 — Verify-then-remediate pipeline.
 *
 * Flow:
 *   1. Generate RAG answer (with constitution in system prompt)
 *   2. Decompose into claims → verify each claim
 *   3. If any claim is REFUTED: regenerate answer, injecting counter-evidence
 *   4. Return final answer + audit trail
 *
 * Run: tsx src/day5/remediate.ts "What optimiser should I use for training?"
 */
import Anthropic from "@anthropic-ai/sdk";
import pool from "../db/client.js";
import { retrieve } from "../day1-2/retrieve.js";
import { verifyAnswer, VerificationResult } from "../day3/verify.js";
import { withConstitution, ANTI_SYCOPHANCY_CONSTITUTION } from "./constitution.js";

const claude = new Anthropic();
const MODEL = process.env.CLAUDE_MODEL ?? "claude-haiku-4-5-20251001";

export interface RemediatedAnswer {
  answer: string;
  verifications: VerificationResult[];
  wasRemediated: boolean;
  remediationReason?: string;
}

const BASE_SYSTEM = `You are a precise tutor. Answer using ONLY the provided context.
Cite sources with [N] notation. If unsure, say so.`;

async function generateAnswer(question: string, extraContext = ""): Promise<string> {
  const chunks = await retrieve(question);
  const contextBlock = chunks
    .map((c, i) => `[${i + 1}] (${c.source})\n${c.content}`)
    .join("\n\n---\n\n");

  const system = withConstitution(BASE_SYSTEM);

  const userContent = extraContext
    ? `${extraContext}\n\nContext:\n${contextBlock}\n\nQuestion: ${question}`
    : `Context:\n${contextBlock}\n\nQuestion: ${question}`;

  const msg = await claude.messages.create({
    model: MODEL,
    max_tokens: 1024,
    system,
    messages: [{ role: "user", content: userContent }],
  });

  return msg.content
    .filter((b) => b.type === "text")
    .map((b) => (b as Anthropic.TextBlock).text)
    .join("");
}

export async function remediateAnswer(
  question: string,
  sessionId = `session_${Date.now()}`
): Promise<RemediatedAnswer> {
  const draft = await generateAnswer(question);
  const verifications = await verifyAnswer(draft, sessionId);

  const refuted = verifications.filter((v) => v.verdict === "refuted");

  if (refuted.length === 0) {
    return { answer: draft, verifications, wasRemediated: false };
  }

  // Build remediation context: tell the model which claims failed and why
  const corrections = refuted
    .map((v) => `- INCORRECT CLAIM: "${v.claim}"\n  Reason: ${v.explanation}`)
    .join("\n");

  const extraContext = `CORRECTION NOTES (do not repeat these claims):\n${corrections}\n`;
  const remediated = await generateAnswer(question, extraContext);

  return {
    answer: remediated,
    verifications,
    wasRemediated: true,
    remediationReason: `${refuted.length} claim(s) refuted: ${refuted.map((v) => v.claim).join("; ")}`,
  };
}

// ── CLI ──────────────────────────────────────────────────────────────────────
if (process.argv[1]?.endsWith("remediate.ts")) {
  const question = process.argv[2] ?? "How does gradient descent work?";
  console.log(`\nQuestion: ${question}\n${"─".repeat(60)}`);

  remediateAnswer(question).then(({ answer, verifications, wasRemediated, remediationReason }) => {
    console.log(`Answer${wasRemediated ? " (REMEDIATED)" : ""}:\n${answer}`);
    console.log(`\n${"─".repeat(60)}\nVerification results:`);
    for (const v of verifications) {
      const icon = v.verdict === "supported" ? "✓" : v.verdict === "refuted" ? "✗" : "?";
      console.log(`  ${icon} [${v.verdict}] ${v.claim}`);
    }
    if (remediationReason) console.log(`\nRemediated because: ${remediationReason}`);
    pool.end();
  }).catch((e) => { console.error(e); process.exit(1); });
}
