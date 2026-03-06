Below is a ready-to-share Markdown file you can drop into your repo or wiki.
It’s written as team-facing system prompt design guidelines, neutral in tone, opinionated where it matters, and aligned with everything we’ve discussed.

You can copy-paste this verbatim into SYSTEM_PROMPT_DESIGN_GUIDELINES.md.

⸻


# System Prompt Design Guidelines
**Task / Execution Plan / Rule Blocks Architecture**

---

## Purpose

This document defines a **shared, scalable approach** for designing system prompts for LLM-based agents.

The goal is to:
- Reduce ambiguity and prompt drift
- Improve predictability and maintainability
- Enable safe scaling across different agent types
- Support both creative and deterministic use cases

This is **not** a one-size-fits-all rulebook.  
It is a **tiered framework** that matches prompt structure to agent complexity.

---

## Core Principle: Orthogonality

Design system prompts using **non-overlapping responsibilities**.

| Component | Responsibility |
|---------|----------------|
| **Task** | WHAT the agent must achieve |
| **Execution Plan** | HOW the agent should proceed |
| **Rule Blocks** | DETAILS: syntax, schemas, mappings, constraints |

Each component must be:
- Independent
- Reference-only (no duplication)
- Single-purpose

---

## Component Definitions

### 1. Task (WHAT)

**Purpose**  
Defines outcomes, constraints, and success conditions.

**Includes**
- Objective (1 sentence)
- Acceptance criteria (MUST / NEVER)
- Output contract (format, scoping, allowed elements)
- References to rule blocks (by name only)

**Never Includes**
- Steps or sequencing
- Procedural logic
- Examples
- Rule text or syntax

**Mental Model**  
> “What does a *correct* output look like?”

---

### 2. Execution Plan (HOW)

**Purpose**  
Operationalizes the Task using procedural steps.

**Includes**
- Ordered, atomic steps
- Parsing and mapping logic
- Validation and preflight checks
- Conditional branching (if/else)

**Never Includes**
- Rule definitions
- Output schema text
- Formatting or tone rules
- Examples

**Structure (Recommended)**
```xml
<plan>
  <step><action_name>parse_input</action_name><description>…</description></step>
  <step><action_name>map_rules</action_name><description>…</description></step>
  <step><action_name>generate_output</action_name><description>…</description></step>
  <step><action_name>validate_output</action_name><description>…</description></step>

  <if_block condition="missing_or_invalid">
    <step><action_name>reply_with_issues</action_name></step>
  </if_block>

  <if_block condition="valid">
    <step><action_name>reply_final</action_name></step>
  </if_block>
</plan>

Mental Model

“What steps must succeed for the output to be valid?”

⸻

3. Rule Blocks (DETAILS)

Purpose
Single source of truth for all syntax and logic that may change over time.

Typical Rule Blocks
	•	Formatting / markup rules
	•	Schema definitions (JSON / HTML)
	•	Mapping rules (IDs, keys, transforms)
	•	Numbering rules
	•	Citation / highlight rules
	•	Regex constraints

Characteristics
	•	Contain rule text and syntax
	•	May include tiny minimal examples
	•	Are referenced by name from Task and Plan
	•	Never duplicated elsewhere

Mental Model

“Where do future changes belong?”

⸻

Placement Router (Decision Filter)

Use these questions to decide where an instruction belongs:
	1.	Is it an outcome or a method?
	•	Outcome → Task
	•	Method → Plan
	2.	Is it rule text or syntax?
→ Rule Block
	3.	Does it specify order, sequence, or branching?
→ Plan
	4.	Is it a format or schema contract?
→ Task
	5.	Is it a validation or check?
→ Plan
	6.	Is it about where markup is allowed?
	•	Scope definition → Task
	•	Scope enforcement → Plan
	7.	Is it an example?
→ Rule Block only

⸻

Validation Discipline (Ownership)

Task Owns
	•	Acceptance criteria
	•	Output format guarantees
	•	High-level constraints

Plan Owns
	•	Preflight checks
	•	Schema validation
	•	Numbering and ID integrity
	•	Conditional responses

Rule blocks define how validation works — the Plan only applies them.

⸻

Anti-Patterns (Common Failures)
	•	Policy Echo: Plan repeats rule syntax → move to Rule Blocks
	•	Mixed Intent: Task contains steps → move to Plan
	•	Dual Ownership: Task and Plan both define scope → keep in Task, validate in Plan
	•	Schema Leakage: Output schema repeated in Plan → remove
	•	Frontend Language: Visual/UI terms (hover, color, visibility) → remove everywhere

If you see duplication, the architecture is leaking.

⸻

Tiered Usage Model (Important)

Not every agent needs full orthogonality.

Tier 1 — Task Only

Use when
	•	Creative or exploratory agents
	•	Low-risk outputs
	•	No strict structure

Pros
	•	Fast to write
	•	Easy for non-technical teams

Cons
	•	Less predictable
	•	Harder to scale

⸻

Tier 2 — Task + Minimal Plan

Use when
	•	Light structure needed
	•	Some validation required
	•	Simple workflows

Pros
	•	Balanced clarity
	•	Still readable

Cons
	•	Rules may become implicit

⸻

Tier 3 — Task + Plan + Rule Blocks

Use when
	•	Deterministic outputs required
	•	Structured formats (JSON/HTML)
	•	Multi-step workflows
	•	Non-reasoning or mini models
	•	Integration into pipelines or products

Pros
	•	Predictable
	•	Maintainable
	•	Scalable

Cons
	•	Higher upfront cost
	•	Requires discipline

⸻

Choosing the Right Tier

Ask:
	1.	Does this agent need deterministic, reproducible output?
	2.	Does it require schema, markup, or IDs?
	3.	Does it perform multi-step reasoning or validation?

If yes to any → move up a tier.

⸻

Key Takeaway

Orthogonality is a scalability pattern, not a religion.
	•	Use the simplest structure that satisfies requirements
	•	Introduce separation when failure modes appear
	•	Keep responsibilities clean and isolated

Good system prompts are boring, predictable, and easy to change.

⸻

TL;DR
	•	Task = WHAT
	•	Plan = HOW
	•	Rule Blocks = DETAILS
	•	Keep them separate
	•	Match structure to complexity
	•	Avoid duplication at all costs

---

If you want next:
- A **repo folder structure** (`/prompts/task/plan/rules`)
- A **bad → good annotated example**
- A **code-based prompt loader** pattern
- Or a **review checklist** for prompt PRs

Just say the word.