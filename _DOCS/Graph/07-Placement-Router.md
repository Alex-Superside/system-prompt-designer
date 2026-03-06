# Placement Router

## Definition

A decision filter that determines where each instruction belongs: [[03-Task-Component]], [[04-Execution-Plan-Component]], or [[05-Rule-Blocks-Component]].

## Decision Questions

Use these questions in order:

### Q1: Is it an outcome or a method?

- **Outcome** (success condition, acceptance criteria) → [[03-Task-Component]]
- **Method** (procedural step, how to achieve) → [[04-Execution-Plan-Component]]

### Q2: Is it rule text or syntax?

- **Rule text or syntax** (format specs, schema, mappings) → [[05-Rule-Blocks-Component]]
- **Other** → Re-evaluate with next question

### Q3: Does it specify order, sequence, or branching?

- **Yes** (if/then, step 1→2→3) → [[04-Execution-Plan-Component]]
- **No** → Continue

### Q4: Is it a format or schema contract?

- **Yes** (output format, structure, scope limits) → [[03-Task-Component]]
- **No** → Continue

### Q5: Is it a validation or check?

- **Yes** (preflight, schema validation, ID integrity) → [[04-Execution-Plan-Component]]
- **No** → Continue

### Q6: Is it about where markup is allowed?

- **Scope definition** (what can be marked) → [[03-Task-Component]]
- **Scope enforcement** (how to mark, validation) → [[04-Execution-Plan-Component]]

### Q7: Is it an example?

- **Yes** → [[05-Rule-Blocks-Component]] only (minimal examples in rules)
- **No, a large example or reference** → [[05-Rule-Blocks-Component]]

## Quick Reference Table

| Content | Belongs In | Why |
|---------|-----------|-----|
| "Output must be JSON" | [[03-Task-Component]] | Acceptance criteria |
| "Parse the JSON with validator X" | [[04-Execution-Plan-Component]] | Procedural step |
| "JSON schema definition" | [[05-Rule-Blocks-Component]] | Syntax/schema |
| "MUST ask before recommending" | [[03-Task-Component]] | Acceptance criteria |
| "First, extract user intent" | [[04-Execution-Plan-Component]] | Step/sequencing |
| "Tone is consultative, never pushy" | [[05-Rule-Blocks-Component]] | Rules/style |
| "Format quotes with section headers" | [[05-Rule-Blocks-Component]] | Formatting rules |

## Common Mistakes

**Mistake 1: Tone rules in Task**
- ❌ Task: "Use a friendly, consultative tone"
- ✅ Move to [[05-Rule-Blocks-Component]]: "Tone Rules: Friendly, consultative, never pushy"

**Mistake 2: Examples in Plan**
- ❌ Plan: "Generate output like: [big example]"
- ✅ Move to [[05-Rule-Blocks-Component]]: "Example Output: [minimal]"

**Mistake 3: Rule syntax in Plan**
- ❌ Plan: "Apply this regex: \d{3}-\d{4}"
- ✅ Move to [[05-Rule-Blocks-Component]]: "Phone Format Rules: \d{3}-\d{4}"

## Testing Your Placement

Before finalizing a prompt:

1. Does [[03-Task-Component]] contain ANY procedural steps?
   - Yes → Move to [[04-Execution-Plan-Component]]

2. Does [[04-Execution-Plan-Component]] contain ANY rule syntax or formatting?
   - Yes → Move to [[05-Rule-Blocks-Component]]

3. Does [[05-Rule-Blocks-Component]] contain ANY procedural steps?
   - Yes → Move to [[04-Execution-Plan-Component]]

If all answers are "No", your placement is orthogonal.

## Relates To

- [[02-Orthogonality-Principle]] — Why placement matters
- [[07-Placement-Router]] — This page
- [[09-Anti-Patterns]] — What goes wrong when placement is bad
