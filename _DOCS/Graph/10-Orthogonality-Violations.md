# Orthogonality Violations

## Definition

When [[02-Orthogonality-Principle]] breaks down—components overlap, duplication spreads, and maintenance becomes difficult.

## How Violations Manifest

### Symptom 1: Duplication Spread

**Pattern:** Same content in multiple [[01-System-Prompt-Design-Framework]] components

**Example:**
```
Task mentions: "JSON format with quote_id, items, total"
Rule Block defines: "JSON Schema: quote_id, items, total"
Plan references: "Assemble JSON with quote_id, items, total"

→ Triple definition, triple maintenance burden
```

**Cost:**
- Update one place, miss two others → inconsistency
- Three copies to review instead of one
- Harder to find canonical definition

### Symptom 2: Unclear Ownership

**Pattern:** Multiple components claiming responsibility for the same validation

**Example:**
```
Task: "Output MUST be JSON"
Plan: "Validate JSON structure and types"
→ Who decides if output is valid? Both? Neither clear.
```

**Cost:**
- Inconsistent validation
- Hard to trace requirements back to acceptance criteria
- Difficult to assign responsibility for changes

### Symptom 3: Tight Coupling

**Pattern:** [[05-Rule-Blocks-Component]] embedded in [[04-Execution-Plan-Component]]

**Example:**
```
Plan: "Validate using this regex: \d{3}-\d{4}"

→ Regex is tightly coupled to plan step
→ Change regex, must understand plan step
→ Change plan, might break regex
```

**Cost:**
- Can't update rules independently
- Rules aren't reusable
- Changes have wide blast radius

### Symptom 4: Implicit Rules

**Pattern:** Rules not explicitly defined, just assumed in Plan/Task

**Example:**
```
Plan: "Generate quote in standard format"
→ What is "standard"? Nowhere defined.
```

**Cost:**
- Difficult to onboard new contributors
- Rules discovered only when output is wrong
- Hard to test rule compliance independently

## Breaking [[02-Orthogonality-Principle]]

### Violation Type 1: Content Overlaps

Responsibility | Should Be Single | Actual |
|---|---|---|
Task owns acceptance criteria | Define it once | Mentioned in Task, Plan, Rule Blocks |
Plan owns validation | Validate it once | Validation logic scattered |
Rule Blocks own syntax | Define it once | Embedded in multiple places |

**Fix:** Extract to single authoritative source, reference elsewhere

### Violation Type 2: Responsibility Ambiguity

**Pattern:** Multiple components trying to enforce the same constraint

```
❌ Task: "Output MUST be valid JSON"
❌ Plan: "Ensure output is valid JSON"
❌ Rule Block: "Valid JSON structure: {...}"

(Who's responsible? All three? Just Plan?)

✅ Task: "Output MUST be valid JSON per Schema Rules"
✅ Plan: "Validate JSON structure and types per Schema Rules"
✅ Rule Block: "JSON Schema Rules: {...}"

(Clear: Task defines, Plan enforces, Rules define syntax)
```

**Fix:** Clarify ownership using [[08-Validation-Discipline]]

## Recovery: Restoring Orthogonality

### Step 1: Map Content

Create a table of what exists where:

| Content | Task | Plan | Rules |
|---|---|---|---|
| "JSON format" | X | X | X |
| "Pricing logic" | X | - | X |
| "Validation steps" | - | X | - |

### Step 2: Identify Authority

For each duplicated item, choose **one** authoritative home:

| Content | Authoritative Home | Why |
|---|---|---|
| JSON format | Rule Blocks | It's syntax (definition) |
| Validation steps | Plan | It's procedural (implementation) |
| Format acceptance criteria | Task | It's requirement (outcome) |

### Step 3: Extract & Consolidate

```
Before:
Task + Plan + Rule Blocks all mention JSON format

After:
Task: "Output: JSON per JSON Schema Rules"
Plan: "Assemble JSON per JSON Schema Rules; validate per schema"
Rule Blocks: "JSON Schema Rules: {...}"
```

### Step 4: Reference Only

Ensure non-authoritative locations **reference only**, not define:

```
✅ Good:
  Plan: "per JSON Schema Rules"

❌ Bad:
  Plan: "with these fields: {quote_id, items, total}"
```

### Step 5: Validate Restoration

Run [[07-Placement-Router]] over the result. Each piece of content should have exactly one home.

## Cost of Violations

| Violation | Cost | Example |
|---|---|---|
| Duplication | Maintenance debt | Update schema 3 places instead of 1 |
| Unclear ownership | Inconsistency | Different validation logic in Plan vs Task |
| Tight coupling | Limited reusability | Can't use rule in another agent |
| Implicit rules | Poor onboarding | New contributor must reverse-engineer rules |

## Relates To

- [[02-Orthogonality-Principle]] — What it means to be orthogonal
- [[09-Anti-Patterns]] — How violations appear
- [[07-Placement-Router]] — Tool to prevent violations
- [[08-Validation-Discipline]] — Clear ownership prevents violations
