# Anti-Patterns in Prompt Design

## Definition

Common failures in system prompt design that violate [[02-Orthogonality-Principle]] and create duplication, confusion, and maintenance debt.

## Core Anti-Pattern: Duplication

> "If you see duplication, the architecture is leaking."

Content appearing in multiple [[01-System-Prompt-Design-Framework]] components indicates orthogonality failure.

## Specific Anti-Patterns

### 1. Policy Echo

**What:** [[04-Execution-Plan-Component]] repeats rule syntax from [[05-Rule-Blocks-Component]]

**Example:**
```
❌ Plan: "Validate JSON structure per this schema:
   {quote_id: string, items: [...], total: number}"

✅ Correct: "Validate JSON structure per JSON Schema Rules"
```

**Why Bad:**
- Updates require editing two places
- Validation logic drifts from rule definition
- Harder to test rules independently

**Fix:**
Extract to [[05-Rule-Blocks-Component]]: "JSON Schema Rules"

---

### 2. Mixed Intent

**What:** [[03-Task-Component]] contains procedural steps (HOW instead of WHAT)

**Example:**
```
❌ Task: "Objective: Generate quotes.
   1. Parse request
   2. Look up pricing
   3. Assemble JSON"

✅ Correct: "Objective: Generate precise quotes.
   MUST follow Pricing Rules.
   Output: JSON per Schema Rules."
```

**Why Bad:**
- Steps are implementation detail (Plan's job)
- Makes Task unclear and cluttered
- Acceptance criteria get buried

**Fix:**
Move steps to [[04-Execution-Plan-Component]]

---

### 3. Dual Ownership

**What:** [[03-Task-Component]] and [[04-Execution-Plan-Component]] both define the same scope

**Example:**
```
❌ Task: "Output must be valid JSON"
❌ Plan: "Validate JSON structure and types"

(Both trying to "own" JSON validity)

✅ Correct:
   Task: "Output must be valid JSON per Schema Rules"
   Plan: "Validate JSON structure and types per Schema Rules"
```

**Why Bad:**
- Unclear who's responsible
- Inconsistent definitions
- Hard to trace requirements

**Fix:**
Keep scope definition in Task, enforcement in Plan

---

### 4. Schema Leakage

**What:** [[05-Rule-Blocks-Component]] schema repeated in [[04-Execution-Plan-Component]] or [[03-Task-Component]]

**Example:**
```
❌ Plan: "Generate JSON with quote_id, items array, total"
❌ Rule Block: "JSON Schema: {quote_id, items: [...], total}"

(Same structure defined twice)

✅ Correct:
   Plan: "Generate JSON per JSON Schema Rules"
   Rule Block: "JSON Schema Rules: {quote_id, items, total}"
```

**Why Bad:**
- Schema updates require editing multiple places
- Easy to get out of sync
- Violates single source of truth

**Fix:**
Define schema once in [[05-Rule-Blocks-Component]], reference elsewhere

---

### 5. Frontend Language

**What:** System prompt contains UI/visual language that belongs in frontend only

**Example:**
```
❌ Task: "When you hover over this, show the citation tooltip"
❌ Plan: "Color the gaps red and citations blue"

✅ Correct: Use only semantic markup
   <mark class="highlight" data-type="gap">content</mark>
```

**Why Bad:**
- Frontend and backend responsibilities are mixed
- Hard to change UI without changing prompt
- CSS/styling belongs in frontend

**Fix:**
Use semantic markup in prompt; styling controlled by frontend CSS

---

## Detection Checklist

Ask these questions to find anti-patterns:

- [ ] **Does any content appear in 2+ components?** → Duplication
- [ ] **Does [[03-Task-Component]] contain "first", "then", "next"?** → Mixed Intent
- [ ] **Do both [[03-Task-Component]] and [[04-Execution-Plan-Component]] define the same scope?** → Dual Ownership
- [ ] **Is schema or formatting repeated?** → Schema Leakage
- [ ] **Are there UI/visual instructions in the prompt?** → Frontend Language
- [ ] **Are [[05-Rule-Blocks-Component]] rules embedded in Plan steps?** → Policy Echo

## Impact Assessment

| Anti-Pattern | Impact | Severity |
|---|---|---|
| Policy Echo | Maintenance drift, update inconsistency | High |
| Mixed Intent | Confusion about purpose, acceptance criteria hidden | High |
| Dual Ownership | Unclear responsibility, inconsistent enforcement | High |
| Schema Leakage | Single source of truth violated | High |
| Frontend Language | Tight coupling, hard to maintain | Medium |

## Recovery Process

1. **Identify** the duplication using detection checklist
2. **Extract** to [[05-Rule-Blocks-Component]] (or appropriate component)
3. **Reference** by name from other components
4. **Validate** using [[07-Placement-Router]]
5. **Test** that [[02-Orthogonality-Principle]] is restored

## Relates To

- [[10-Orthogonality-Violations]] — How violations manifest
- [[07-Placement-Router]] — Decision tool to prevent anti-patterns
- [[02-Orthogonality-Principle]] — Why these patterns fail
