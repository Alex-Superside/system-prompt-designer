# 01: Discovery and Tiering

## The Discovery Process

Before writing a single line of a prompt, you must define the agent's **Mission** and **Operational Constraints**. Discovery is about identifying the "Failure Modes" you are trying to prevent.

### 1. Define the Mission
- **Goal**: What is the single, non-negotiable outcome? (e.g., "Generate a design-ready brief from customer text").
- **Acceptance Criteria**: What are the 3-5 rules that, if broken, mean the agent failed? (e.g., "Must cite sources," "Must output HTML," "Must never infer budget").

### 2. Map the Inputs
- What raw data will the user provide?
- What "Supporting Data" (context) is available?
- Are there attached files (PDFs, docs, links) that require processing?

---

## Tiered Complexity Model

Choose the simplest tier that satisfies the mission. Tier selection is based on **Risk**, not model power.

### Tier 1: Task Only (Creative/Exploratory)
- **Use When**: Low-risk, creative tasks where "hallucination" is just "imagination" (e.g., brainstorming, creative writing).
- **Structure**: Single "Objective" block. No explicit steps or rules.
- **Linguistic Note**: Relies heavily on the model's latent knowledge and inference.

### Tier 2: Task + Minimal Plan (Light Structure)
- **Use When**: Some structure is needed but rules are simple (e.g., customer support, FAQ responders).
- **Structure**: "Task" (WHAT) + "Plan" (HOW).
- **Linguistic Note**: Provides a basic procedural path for the model's attention.

### Tier 3: Task + Plan + Rule Blocks (Production/Deterministic)
- **Use When**: High-risk, schema-bound, or multi-step tasks (e.g., quoting, compliance, brief-writing).
- **Structure**: Full **Orthogonality** (WHAT / HOW / DETAILS).
- **Linguistic Note**: Replaces inference with a strict grammar of rules and validations.

---

## The "Model Selection" Rule

**Non-Reasoning models (Claude Haiku, 4o-mini) always need Tier 3.**

- They cannot "figure it out."
- They need explicit rules and granular, atomic plan steps.
- Even for simple tasks, if the model is "small," use more structure.

### Decision Checklist:
1. Does it need a specific format (JSON/HTML)? → **Tier 2/3**
2. Does it handle sensitive data or brand rules? → **Tier 3**
3. Is it running on a non-reasoning model? → **Tier 3**
4. Does it have multi-step reasoning or validation? → **Tier 3**
5. Is it a one-off creative experiment? → **Tier 1**

---
*“Start with Tier 1 to explore. Move to Tier 3 to ship.”*
