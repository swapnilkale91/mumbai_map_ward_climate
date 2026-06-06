# Fine-tuning Language Models

Fine-tuning adapts a pre-trained model to a specific task or domain by continuing training on task-specific data.

## Full Fine-tuning
Updates all parameters of the model. Requires significant GPU memory and compute. Can cause catastrophic forgetting of pre-trained knowledge if the dataset is too small.

## Parameter-Efficient Fine-tuning (PEFT)
Updates only a small fraction of parameters:
- **LoRA** (Low-Rank Adaptation): inserts low-rank weight matrices into attention layers. Only these are updated. Typical rank r=8–64; trains 0.1–1% of parameters.
- **Prefix tuning**: prepends trainable "virtual tokens" to the context.
- **Adapters**: small bottleneck modules inserted between transformer layers.

## Instruction Fine-tuning
Training on (instruction, response) pairs teaches the model to follow instructions. FLAN, Alpaca, and OpenAI's RLHF process all use this approach.

## RLHF (Reinforcement Learning from Human Feedback)
1. Supervised fine-tuning on demonstration data.
2. Train a reward model on human preference comparisons.
3. Fine-tune with PPO, using the reward model as the reward signal.

Produces models that are more helpful, harmless, and honest but can amplify sycophancy if the reward model rewards agreeableness.

## When to Fine-tune vs RAG
- Fine-tune for **style, tone, format, and task behaviour**.
- RAG for **factual knowledge that changes or grows**.
- Combining both is common for production systems.

## Dataset Quality Over Quantity
A few hundred high-quality examples often beat thousands of noisy ones. Data cleaning and deduplication have outsized impact.

## Evaluation After Fine-tuning
Measure on a held-out test set. Watch for regressions on the base model's capabilities (especially instruction following). MMLU or HellaSwag can detect capability degradation.
