/**
 * Split text into overlapping windows so each chunk has context from its
 * neighbours. Word-boundary aware — never cuts mid-word.
 */
export interface Chunk {
  content: string;
  index: number;
}

export function chunkText(
  text: string,
  chunkSize = Number(process.env.CHUNK_SIZE ?? 400),
  overlap = Number(process.env.CHUNK_OVERLAP ?? 80)
): Chunk[] {
  const words = text.split(/\s+/).filter(Boolean);
  const chunks: Chunk[] = [];
  let start = 0;

  while (start < words.length) {
    const end = Math.min(start + chunkSize, words.length);
    chunks.push({ content: words.slice(start, end).join(" "), index: chunks.length });
    if (end === words.length) break;
    start += chunkSize - overlap;
  }

  return chunks;
}
