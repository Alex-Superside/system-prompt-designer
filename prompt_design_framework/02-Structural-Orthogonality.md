# 02: Structural Orthogonality

## The Orthogonal Trinity

Structural orthogonality is the practice of separating a prompt into three non-overlapping components: **WHAT**, **HOW**, and **DETAILS**.

### 1. Task (WHAT)
- **Responsibility**: Defines the mission, acceptance criteria, and output contract.
- **Mental Model**: "What does success look like?"
- **Includes**:
  - Mission statement.
  - MUST / NEVER statements.
  - Reference to Rule Blocks (by name).
  - Output format (e.g., HTML/JSON).
- **Prohibited**: Procedural steps (Step 1, Then...), specific syntax/rules.

### 2. Execution Plan (HOW)
- **Responsibility**: Defines the ordered, procedural steps and validations.
- **Mental Model**: "What steps must the agent take to succeed?"
- **Includes**:
  - Sequential steps (e.g., Parse → Identify → Map → Generate → Validate).
  - Conditional logic (if/then).
  - References to Rule Blocks for enforcement.
- **Prohibited**: Rule definitions, syntax, mission-level criteria.

### 3. Rule Blocks (DETAILS)
- **Responsibility**: Single source of truth for syntax, mappings, and formatting.
- **Mental Model**: "Where do changes belong?"
- **Includes**:
  - Schema definitions (JSON, HTML).
  - Formatting and markup rules.
  - Mapping tables (IDs, categories).
  - Minimal examples (for syntax illustration).
- **Prohibited**: Procedural steps, tone rules, acceptance criteria.

---

## The Placement Router

Use these decision questions to ensure your prompt remains orthogonal:

1. **Is it an outcome?** → **Task**
2. **Is it a procedural step or a "how-to"?** → **Execution Plan**
3. **Is it rule text or a syntax specification?** → **Rule Block**
4. **Does it specify order or sequence?** → **Execution Plan**
5. **Is it an example?** → **Rule Block**

### Common Mistake: "Policy Echo"
- **Bad**: Plan repeats rule syntax (e.g., "Step 4: Use <mark> tags").
- **Good**: Plan references the rule (e.g., "Step 4: Apply Highlight Rules").

### Common Mistake: "Mixed Intent"
- **Bad**: Task contains "First," "Then," "Next."
- **Good**: Move all procedural language to the **Execution Plan**.

---

## Why Orthogonality Scales

- **Maintenance**: Update a pricing rule without touching the core task or the execution flow.
- **Team Ownership**: Designers own the Task, Developers own the Plan, and Domain Experts own the Rule Blocks.
- **Linguistic Precision**: By isolating "Instructions" from "Rules," you reduce the model's cognitive load and improve performance on non-reasoning models.

---
*“If you see duplication, the architecture is leaking. Refactor immediately.”*
