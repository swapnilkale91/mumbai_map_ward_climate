/**
 * Day 1-2 — RAG answer with citations.
 *
 * Flow: user question → retrieve top-K chunks → prompt Claude with context
 *        → return answer + source list.
 *
 * Run: tsx src/day1-2/answer.ts "What is gradient descent?"
 */
import Anthropic from "@anthropic-ai/sdk";
import pool from "../db/client.js";
import { retrieve, RetrievedChunk } from "./retrieve.js";

const claude = new Anthropic();
const MODEL = process.env.CLAUDE_MODEL ?? "claude-haiku-4-5-20251001";

export interface RAGAnswer {
  answer: string;
  sources: Array<{ source: string; chunk_index: number; score: number }>;
}

function buildContext(chunks: RetrievedChunk[]): string {
  return chunks
    .map((c, i) => `[${i + 1}] (${c.source}, chunk ${c.chunk_index})\n${c.content}`)
    .join("\n\n---\n\n");
}

export async function ragAnswer(question: string): Promise<RAGAnswer> {
  const chunks = await retrieve(question);

  const context = buildContext(chunks);

  const systemPrompt = `You are a knowledgeable tutor. Answer questions using ONLY the provided context.
Cite sources using [N] notation matching the numbered context blocks.
If the context doesn't contain the answer, say so — do not hallucinate.`;

  const userPrompt = `Context:\n${context}\n\nQuestion: ${question}`;

  const message = await claude.messages.create({
    model: MODEL,
    max_tokens: 1024,
    messages: [{ role: "user", content: userPrompt }],
    system: systemPrompt,
  });

  const answer = message.content
    .filter((b) => b.type === "text")
    .map((b) => (b as Anthropic.TextBlock).text)
    .join("");

  return {
    answer,
    sources: chunks.map((c) => ({
      source: c.source,
      chunk_index: c.chunk_index,
      score: Number(c.score.toFixed(4)),
    })),
  };
}

// ── CLI entry point ──────────────────────────────────────────────────────────
if (process.argv[1]?.endsWith("answer.ts")) {
  const question = process.argv[2] ?? "What is a neural network?";
  console.log(`\nQuestion: ${question}\n`);

  ragAnswer(question).then(({ answer, sources }) => {
    console.log("Answer:\n", answer);
    console.log("\nSources:");
    sources.forEach((s, i) => console.log(`  [${i + 1}] ${s.source} (score: ${s.score})`));
    pool.end();
  }).catch((e) => { console.error(e); process.exit(1); });
}
