# Evaluation Metrics for ML Systems

Choosing the right metric is as important as choosing the right model. Metrics must align with the business goal.

## Classification Metrics
- **Accuracy**: fraction of correct predictions. Misleading on imbalanced classes.
- **Precision**: TP / (TP + FP). Of all positive predictions, how many are correct?
- **Recall**: TP / (TP + FN). Of all actual positives, how many did we catch?
- **F1**: harmonic mean of precision and recall. Balances both.
- **AUC-ROC**: area under the receiver operating characteristic curve. Measures ranking quality across thresholds.

## Regression Metrics
- **MAE** (Mean Absolute Error): average absolute difference. Robust to outliers.
- **RMSE** (Root Mean Squared Error): penalises large errors more. Sensitive to outliers.
- **R²**: fraction of variance explained by the model.

## Language Model Metrics
- **Perplexity**: 2^(-average log-probability per token). Lower is better.
- **BLEU**: n-gram overlap with reference translations. Widely used but correlates poorly with human judgement.
- **BERTScore**: embedding-based similarity between generated and reference text.
- **LLM-as-judge**: use a capable LLM (e.g. GPT-4) to score outputs on a rubric. More expensive but more flexible.

## RAG-Specific Metrics
- **Faithfulness**: are all claims in the answer grounded in retrieved context?
- **Answer relevance**: does the answer address the question?
- **Context precision**: of retrieved chunks, how many are actually relevant?
- **Context recall**: of all relevant chunks, how many were retrieved?

## Evaluation Anti-patterns
- Testing on training data (data leakage).
- Optimising for a metric without checking correlated harms.
- Using the same LLM as both generator and judge without safeguards.
