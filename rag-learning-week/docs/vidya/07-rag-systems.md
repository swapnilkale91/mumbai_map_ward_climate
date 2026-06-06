# Retrieval-Augmented Generation (RAG)

RAG combines a retriever (finds relevant documents) with a generator (produces an answer conditioned on those documents). This grounds the LLM in external knowledge and reduces hallucination.

## The Basic Pipeline
1. **Ingest**: chunk documents, embed each chunk, store in a vector database.
2. **Retrieve**: embed the user query, find the top-K most similar chunks.
3. **Augment**: concatenate retrieved chunks as context in the prompt.
4. **Generate**: the LLM produces an answer conditioned on the context.

## Why RAG Reduces Hallucination
The LLM's parametric memory is augmented with retrieved evidence. If the model is instructed to answer only from context and cite sources, fabrication is bounded by the quality of retrieval.

## Chunking Strategy
Chunk size trades off recall (smaller chunks are more precise) against coherence (larger chunks retain more context). Common sizes: 256–512 tokens with 10–20% overlap.

## Retrieval Methods
- **Dense retrieval**: embed query and documents, find nearest neighbours by cosine similarity.
- **Sparse retrieval**: BM25 / TF-IDF keyword matching.
- **Hybrid**: combine dense and sparse scores (e.g. via RRF — Reciprocal Rank Fusion).

## Re-ranking
A cross-encoder re-ranker scores each (query, chunk) pair jointly after the initial retrieval, improving precision at the cost of latency.

## Limitations
RAG is only as good as the ingested corpus. Stale data, missing coverage, and poor chunking all degrade answer quality. The generator can still hallucinate details not present in retrieved chunks.

## Evaluation
- **Retrieval recall@K**: fraction of ground-truth relevant chunks in top-K.
- **Faithfulness**: does the answer contain only claims supported by retrieved context?
- **Answer relevance**: does the answer address the question?
