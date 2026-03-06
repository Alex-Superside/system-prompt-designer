# Task Component (WHAT)

## Definition

**Task** defines WHAT the agent must achieve: objectives, constraints, and success conditions.

## Responsibility

Answers: **"What does a correct output look like?"**

## Includes

- **Objective** (1 sentence)
- **Acceptance criteria** (MUST / NEVER statements)
- **Output contract** (format, scope, allowed elements)
- **References to rule blocks** (by name only, not their content)

## Never Includes

- Steps or sequencing
- Procedural logic
- Examples
- Rule text or syntax
- Formatting rules

## Examples

**Sales Agent Task:**
- Objective: Provide accurate, honest guidance
- MUST ask clarifying questions before recommending
- MUST map suggestions to official Product Rules
- Output: text-only, no markup except paragraphs and lists

**Quoting Agent Task:**
- Objective: Generate precise quotes without estimating
- MUST follow Pricing Rules
- MUST insert 'TBD' for missing required input
- Output: JSON only

## Design Pattern

1. State the objective clearly
2. List acceptance criteria as MUST/NEVER statements
3. Define output format (text, JSON, HTML, etc.)
4. Reference Rule Blocks by name
5. **Do not** include the actual rule content

## Relates To

- [[01-System-Prompt-Design-Framework]] — Part of orthogonal trinity
- [[02-Orthogonality-Principle]] — Ensures Task stays focused on WHAT
- [[04-Execution-Plan-Component]] — HOW is separate from WHAT
- [[07-Placement-Router]] — Decide when content belongs here
- [[08-Validation-Discipline]] — Task owns acceptance criteria

## Anti-Pattern Alert

[[09-Anti-Patterns]] — "Mixed Intent" when Task contains steps. If describing HOW, move to [[04-Execution-Plan-Component]].
