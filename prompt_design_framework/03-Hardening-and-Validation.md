# 03: Hardening and Validation

## Hardening the Prompt

Hardening is the process of replacing **probabilistic behavior** (inference) with **deterministic behavior** (instruction).

### 1. Guardrails First
- **Principle**: Guardrails should be the **first** validation step in the Execution Plan, not the last.
- **Why**: Rejection should happen before the agent wastes effort processing or generating data for an out-of-scope request.
- **Action**: Put "Brand Scope Check" at Step 1 of the Execution Plan.

### 2. Gap Highlighting
- **Principle**: Always make missing data explicit.
- **Visual Marker**: Use semantic markup (e.g., `<mark class="highlight" data-type="gap">TBD</mark>`) instead of implicit "missing" text.
- **Why**: Explicit markers prevent the user from ignoring incomplete output and force the model to acknowledge its own uncertainty.

### 3. Factual Traceability (Citations)
- **Principle**: Every claim must have a provenance.
- **Action**: Implement a strict "Citation Formatting Rule" and "Context Source Mapping Table."
- **Benefit**: Reduces hallucinations by forcing the model to find a supporting token in the context before outputting a fact.

---

## Validation Discipline

Who owns the validation of your prompt?

### 1. Task (WHAT) Owns the Criteria
- "MUST include citations for all factual claims."
- "Output MUST be valid JSON per Schema Rules."
- "MUST NEVER estimate budget."

### 2. Execution Plan (HOW) Owns the Enforcement
- **Step 1: Pre-flight Checks** (Validate input).
- **Step 4: Self-Validation** (Model parses its own generated draft to check for rule violations).
- **Step 5: Conditional Branching** (If validation fails, return a draft with markers; if it passes, return the final).

### 3. Rule Blocks (DETAILS) Define the Schema
- The Rule Block doesn't validate; it provides the **blueprint** for the Plan to use during validation.

---

## The "Non-Reasoning" Hardening Strategy

When optimizing for non-reasoning models (Claude Haiku, 4o-mini), apply these "Hyper-Explicit" rules:

- **Atomic Steps**: Break "Generate Brief" into 3-5 smaller, mechanical steps (e.g., "Draft Context Section," "Draft Scope Section," "Check for Gaps").
- **Explicit Schema**: Provide a detailed schema for every section, not just the top-level object.
- **Enumerated Choices**: Instead of "Ask for missing info," use "Choose one: [A] Ask for X, [B] Proceed with TBD, [C] Reject."

---

## Best Practices Checklist

- [ ] Guardrails are Step 1 of the Execution Plan.
- [ ] Every "Acceptance Criterion" in the Task has a corresponding validation step in the Plan.
- [ ] Missing data is highlighted explicitly (not inferred).
- [ ] No "silent fixes"—conflicts are surfaced, not hidden.
- [ ] The prompt is "hardened" with MUST/NEVER language.

---
*“Validation is the only path to finality. What gets validated gets done.”*
