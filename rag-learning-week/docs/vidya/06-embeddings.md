# Embeddings

An embedding is a dense, low-dimensional vector representation of a discrete object (word, sentence, document, user, product). Embeddings encode semantic meaning: similar objects are close in vector space.

## Word Embeddings
Word2Vec (2013) learns word embeddings by predicting surrounding words (Skip-gram) or predicting a word from its context (CBOW). GloVe combines global co-occurrence statistics with local context windows.

## Sentence and Document Embeddings
Models like Sentence-BERT produce a single fixed-size vector for an entire sentence by pooling token embeddings. These are used for semantic similarity, clustering, and retrieval.

## Embedding Dimensions
Typical dimensions range from 128 to 3072. Larger dimensions capture more nuance but cost more compute and storage. `text-embedding-3-small` produces 1536-dimensional vectors.

## Cosine Similarity
The standard measure of similarity between two embedding vectors:
`cos(θ) = (A · B) / (|A| |B|)`

Values range from -1 (opposite) to 1 (identical). In practice, normalised embeddings allow dot product as a proxy.

## Contextualised Embeddings
Unlike static embeddings, contextualised models (BERT, GPT) produce different vectors for the same word depending on its context. "Bank" in "river bank" and "bank account" have different embeddings.

## Embedding Spaces
Arithmetic often holds: `king - man + woman ≈ queen`. This linearity arises from the distributional training objective and is a useful property for analogy tasks.

## Fine-tuning Embeddings
Pre-trained embeddings can be fine-tuned on task-specific data (e.g. a retrieval dataset of query-document pairs) using contrastive losses like InfoNCE.
