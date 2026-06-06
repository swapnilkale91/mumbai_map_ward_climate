# Prompt Engineering

Prompt engineering is the practice of crafting inputs to language models to elicit desired behaviour. It is a fast-moving empirical field.

## System Prompts
The system prompt sets the persona, constraints, and format of responses. Concrete, specific instructions ("Answer in three bullet points. Never mention competitors.") outperform vague ones.

## Few-Shot Prompting
Including examples of input-output pairs in the prompt guides the model's format and reasoning style. Three to five high-quality examples are usually sufficient.

## Chain-of-Thought (CoT)
Asking the model to reason step-by-step ("Let's think through this") before giving a final answer improves performance on multi-step reasoning tasks. Zero-shot CoT: add "Let's think step by step" to the user prompt.

## Instruction Following
Modern instruction-tuned models are sensitive to phrasing. Imperative ("List three examples") works better than interrogative ("Can you list three examples?") for structured outputs.

## Role Prompting
Assigning a role ("You are an expert PostgreSQL DBA") can shift the model's prior toward specialised knowledge and more technical language.

## Output Format Control
Asking for JSON or markdown with a specific schema reduces parsing complexity. Adding an example of the exact output structure ("Return: { 'verdict': 'supported'|'refuted' }") is more reliable than prose description.

## Temperature and Sampling
- **Temperature → 0**: near-deterministic, picks highest-probability tokens. Good for structured extraction.
- **Temperature → 1**: more diverse, creative. Good for brainstorming.
- **Top-p (nucleus sampling)**: restricts sampling to tokens covering p% of the probability mass.

## Prompt Injection
User input that contains instructions can override system-prompt constraints. Always sanitise or delimit user-controlled text (e.g. wrap in XML tags) when it is embedded in a prompt.
