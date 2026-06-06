# Transformers

The transformer architecture, introduced in "Attention Is All You Need" (Vaswani et al., 2017), replaced recurrent networks as the dominant architecture for sequence modelling. It relies entirely on attention mechanisms and has no recurrence.

## Encoder-Decoder Structure
The original transformer has an encoder (reads the input sequence) and a decoder (generates the output sequence). Many modern models use only the encoder (BERT) or only the decoder (GPT).

## Multi-Head Self-Attention
Self-attention allows each position in a sequence to attend to all other positions. The query (Q), key (K), and value (V) matrices are linear projections of the input.

`Attention(Q, K, V) = softmax(QKᵀ / √d_k) · V`

Multi-head attention runs h independent attention heads, concatenates their outputs, and projects. Each head can learn different relational patterns.

## Positional Encoding
Transformers have no built-in notion of position. Positional encodings (sinusoidal or learned) are added to token embeddings to give the model positional information.

## Feed-Forward Sublayer
Each transformer block has a position-wise feed-forward network (two linear layers with a ReLU/GELU in between), applied identically to each position.

## Residual Connections and LayerNorm
Each sublayer is wrapped with a residual connection (`x + sublayer(x)`) and layer normalisation. This stabilises training in very deep networks.

## Scaling Laws
Transformer performance on language tasks improves predictably as a power law with compute, dataset size, and model size. This is the empirical basis for scaling large language models.

## Context Window
The attention computation is O(n²) in sequence length n, which limits the context window. Techniques like FlashAttention, sliding window attention, and ALiBi extend effective context length.
