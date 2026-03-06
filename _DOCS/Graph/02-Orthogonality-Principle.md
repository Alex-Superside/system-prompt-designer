# Orthogonality Principle

## Definition

Design system prompts using **non-overlapping responsibilities** where each component has a distinct, non-redundant role.

## Mental Model

Orthogonality answers: **"Why should responsibilities be separate?"**

Answer: To enable independent testing, modification, and scaling without cascading changes.

## In Prompt Design

| Component | Responsibility | Mental Model |
|-----------|---|---|
| [[03-Task-Component]] | WHAT correct output looks like | What does success look like? |
| [[04-Execution-Plan-Component]] | HOW to proceed with ordered steps | What steps must succeed? |
| [[05-Rule-Blocks-Component]] | DETAILS of syntax and logic | Where do changes belong? |

## Why It Matters

- **Maintainability**: Update a rule block without touching Task or Plan
- **Scalability**: Reuse Rule Blocks across multiple agents
- **Testing**: Validate each component independently
- **Communication**: Different team members own different responsibilities

## Violations

[[10-Orthogonality-Violations]] describes:
- Policy echo (duplication)
- Mixed intent (Task + Plan confusion)
- Dual ownership (unclear responsibility)
- Schema leakage (Rule Blocks repeated in Plan)

## Key Warning

> "If you see duplication, the architecture is leaking."

Always check: Is this content appearing in multiple places? If yes, move it to a single Rule Block.

## Related

- [[07-Placement-Router]] — Tool to enforce orthogonal placement
- [[08-Validation-Discipline]] — Who validates what?
- [[09-Anti-Patterns]] — What breaks orthogonality?
