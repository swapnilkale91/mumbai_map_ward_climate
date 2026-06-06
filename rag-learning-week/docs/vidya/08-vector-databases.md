# Vector Databases

A vector database stores high-dimensional embedding vectors and supports efficient approximate nearest-neighbour (ANN) search.

## Why Not a Regular Database?
Exact nearest-neighbour search over millions of 1536-dim vectors requires comparing the query to every stored vector — O(N·d). ANN algorithms trade a small accuracy drop for orders-of-magnitude speedup.

## pgvector
A PostgreSQL extension that adds a `vector` column type and distance operators (`<=>` cosine, `<->` L2, `<#>` inner product). Supports IVFFlat and HNSW indices.

### IVFFlat Index
Partitions the vector space into lists (clusters). At query time, searches only the nearest `probes` lists. Fast build, moderate query speed. Needs the table to be populated before building the index.

### HNSW Index
Hierarchical Navigable Small World graph. Faster queries than IVFFlat, especially at high recall, but slower builds and more memory. Available in pgvector ≥ 0.5.

## Dedicated Vector Stores
Pinecone, Weaviate, Qdrant, Chroma, and Milvus are purpose-built for vector search. They offer managed replication, filtering, and higher throughput than pgvector at large scale.

## Metadata Filtering
Combining vector search with structured filters ("only return chunks from documents published after 2023") requires the database to support pre- or post-filtering. pgvector uses SQL `WHERE` clauses alongside the vector operator.

## Distance Metrics
- **Cosine distance**: 1 - cosine similarity. Used when vector magnitude is irrelevant.
- **L2 (Euclidean) distance**: sensitive to magnitude; requires normalised vectors for cosine semantics.
- **Inner product (dot product)**: equivalent to cosine similarity for unit-norm vectors.

## Choosing K
Higher K improves retrieval recall but increases context length and cost. Common starting point: K=5. Tune by measuring retrieval recall on a labelled evaluation set.
