# 00: Linguistic Foundations

## Human Intent vs. LLM Perception

Prompt engineering is not "talking" to an AI; it is **encoding a state machine** using a shared token-based language. To design effective prompts, you must bridge the gap between how humans use language and how LLMs process tokens.

### 1. Words as Tokens, Not Concepts
- **Humans**: Use words as pointers to complex, shared abstract concepts (e.g., "be helpful").
- **LLMs**: Process words as statistical tokens. "Helpful" is a probability cluster, not a value system.
- **Framework Rule**: Replace abstract adjectives (e.g., "brief," "polite") with **explicit constraints** (e.g., "maximum 120 words," "use first-person plural").

### 2. Semantic Density vs. Word Count
- **The LLM "reads" for density**: Redundant fluff in a prompt dilutes the attention (softmax) the model pays to critical rules.
- **Middle-Term DSL Strategy**: Use a hybrid language—human-readable but highly structured (like YAML or KeyTokenDSL)—to maximize the **semantic signal per token**.
- **Efficiency**: A prompt is "better" when it says the same thing in fewer, higher-signal tokens.

### 3. Structural Grammar as "Sense-Making"
- **Reasoning**: Larger models (Claude 3.5, o1) can "reason" through ambiguous prose, but smaller/non-reasoning models (Haiku, 4o-mini) cannot.
- **Orthogonality as Logic**: By separating **WHAT** (Task), **HOW** (Plan), and **DETAILS** (Rules), you create a structural "grammar" that the LLM's attention mechanism can follow deterministically.
- **Validation**: LLMs "perceive" the successful completion of a task by checking the output against the "Acceptance Criteria" defined in the Task component.

### 4. Language as "Constraints," not "Ideas"
- A prompt is a **boundary box**. Every word that doesn't define a constraint is noise.
- **The "Boring" Mandate**: A "good" system prompt is intentionally boring. It avoids creative prose in favor of prescriptive rules.
- **Explicitness**: "Infer as appropriate" is a linguistic failure. "If X is missing, insert TBD" is a linguistic success.

### 5. Context Caching and Token Stability
- **Static vs. Dynamic**: LLMs cache the "prefix" of a prompt. If the first 500 tokens of your prompt change between calls (e.g., injecting a dynamic timestamp at the top), the model must re-process the entire prompt.
- **Framework Rule**: Place all static rules (System Prompt) at the top and push all dynamic data (User Input) to the end to maximize KV-cache reuse.

---
*“Structure is more important than raw capability. A well-defined constraint beats raw intelligence every time.”*
