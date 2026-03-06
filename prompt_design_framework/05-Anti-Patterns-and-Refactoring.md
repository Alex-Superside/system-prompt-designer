# 05: Anti-Patterns and Refactoring

## Identifying Technical Debt in Prompts

As a prompt system evolves, it often develops "leaky" architectures that create maintenance debt and performance drift. Refactoring is the process of restoring **Structural Orthogonality**.

### 1. The "Policy Echo" (Duplication)
- **Problem**: The **Execution Plan** restates the rules defined in **Rule Blocks**.
- **Smell**: "Step 4: Generate JSON following this schema: {id: string, name: string}."
- **Refactor**: Replace the schema in the Plan with a reference: "Step 4: Generate JSON per JSON Schema Rules."

### 2. The "Mixed Intent" (Procedural Task)
- **Problem**: The **Task** contains procedural steps (HOW instead of WHAT).
- **Smell**: "Objective: Parse the user's input, map it to a brief, and output HTML."
- **Refactor**: Keep the Task declarative ("Objective: Generate a structured brief per Output Contract") and move the steps to the **Execution Plan**.

### 3. The "Dual Ownership" (Unclear Scope)
- **Problem**: Both the **Task** and the **Plan** define the same scope.
- **Smell**: Task: "Must use <mark> tags." Plan: "Validate that <mark> tags are used."
- **Refactor**: Task defines the **contract** (must use tags); Plan defines the **enforcement** (validate that tags are used per Citation Rules).

---

## Behavioral Smells

### 1. "Silent Hallucinations"
- **Problem**: The model estimates missing data instead of flagging it.
- **Refactor**: Add an explicit **"No Inference"** rule to the Task and a **"Check for Gaps"** validation step to the Plan.

### 2. "Category Drift" (Inconsistent Mappings)
- **Problem**: The same source is cited under different category names.
- **Refactor**: Create a strict **"Source-to-Category Mapping"** Rule Block. Remove all mapping logic from the Task and Plan.

### 3. "The Hover Effect" (Frontend Leakage)
- **Problem**: The prompt contains UI-specific language (e.g., "hover over," "colors").
- **Refactor**: Replace UI language with **Semantic Markup** (e.g., `<mark class="highlight" data-type="citation">`). Let the frontend CSS handle the visual behavior.

---

## The Refactoring Workflow

If an agent is failing, follow this order:

1. **Isolation**: Extract the failing section into a separate Tier 1 prompt. Can the model perform this single action correctly?
2. **Hardening**: Add MUST/NEVER statements to the Task and explicit validation to the Plan.
3. **Extraction**: If the failing section is a complex rule, move it into a dedicated **Rule Block**.
4. **Validation**: Add a "Pre-flight Check" to the Execution Plan to catch bad inputs before they trigger the failure.

---
*“If you see a bug, don't just fix the output. Fix the architecture.”*
