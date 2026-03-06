# 04: DSL and Token Optimization

## Maximizing Semantic Density

As a prompt grows, its "noise-to-signal" ratio often increases. Optimization is the process of compressing the **static prefix** of your prompt using **Domain-Specific Languages (DSLs)** and **Context Caching** strategies.

### 1. The "Middle-Term DSL" (RuleScript)
- **Concept**: A hybrid language—human-readable but highly structured—that reduces token count by 30-50% without losing nuance.
- **Example**:
  - **Natural**: "Never include budget information in any section of the brief."
  - **DSL**: `BAN:BUDGET` (Define `BAN` once in the dictionary).

### 2. KeyTokenDSL (Ultra-Compact)
- **Concept**: A token-level shorthand for high-frequency commands and rules.
- **Use Case**: Multi-agent internal pipelines where tokens are expensive and humans are not the primary audience.
- **Example**:
  - `B1:GUARD` (Block 1: Guardrail)
  - `ELSE:"Refusal message"`
  - `BAN:prior_brand_knowledge`

---

## Strategy: Optimization Without Loss

### Rule 1: Use a Decoder Dictionary
- If you use custom abbreviations (e.g., `OOS`, `BRF`), define them **once** in a `B0:DICT` at the top of the prompt.
- **Why**: This ensures the model maps the shorthand to the correct "full" semantic meaning every time.

### Rule 2: Compress Examples, Not Inputs
- **Few-Shot Examples**: Keep the "Input" verbatim (to teach tone mapping) but compress the "Output" into DSL.
- **Benefit**: You can fit 2-3x more examples in the same context window.

---

## Context Caching Efficiency

To maximize **KV-cache reuse**, follow these structural rules:

### 1. Static Content at the Top
- Place all static rules (Task, Plan, Rule Blocks, Dictionary) at the very beginning of the prompt.
- **Why**: LLM caches are prefix-based. If the prefix is identical between calls, the model processes it only once.

### 2. Move Dynamic Data to the End
- Place user input, current date, and dynamic timestamps at the **end** of the full prompt.
- **Why**: Injecting a dynamic field at the top breaks the prefix cache for everything below it.

### 3. Stable "Supporting Data"
- If you have a large library of supporting data (e.g., guidelines, brief pairs), keep them in a stable order.
- **Why**: This allows the model to cache the data as part of the prefix.

---

## Comparison: Token ROI

| **Format** | **Token Count** | **Readability** | **ROI** |
| --- | --- | --- | --- |
| Natural Markdown | 100% | High | Baseline |
| Middle-Term DSL | 60-70% | Medium | **High** (Production Sweet Spot) |
| KeyTokenDSL | 30-50% | Low | High (Internal Pipelines Only) |

---
*“Token efficiency is not about brevity. It is about semantic signal per token.”*
