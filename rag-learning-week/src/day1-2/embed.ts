import OpenAI from "openai";

const openai = new OpenAI({ apiKey: process.env.OPENAI_API_KEY });

const MODEL = process.env.EMBEDDING_MODEL ?? "text-embedding-3-small";

/**
 * Embed a batch of texts. Returns one float[] per input string.
 * Batches of ≤ 2048 are sent in a single API call.
 */
export async function embedBatch(texts: string[]): Promise<number[][]> {
  if (texts.length === 0) return [];

  const response = await openai.embeddings.create({
    model: MODEL,
    input: texts,
    encoding_format: "float",
  });

  // Sort by index to preserve order (OpenAI guarantees order but belt-and-suspenders)
  return response.data
    .sort((a, b) => a.index - b.index)
    .map((d) => d.embedding);
}

export async function embedOne(text: string): Promise<number[]> {
  const [vec] = await embedBatch([text]);
  return vec;
}
