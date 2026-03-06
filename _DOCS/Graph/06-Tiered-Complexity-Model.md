# Tiered Complexity Model

## Overview

Prompts are classified into three tiers based on complexity and structure needs. **Not every agent needs full orthogonality.**

Choose the simplest tier that satisfies requirements. Move up when failure modes appear.

## Tier 1: Task Only

### Use When

- Creative or exploratory agents
- Low-risk outputs
- No strict structure needed
- Fast iteration is prioritized

### Includes

- [[03-Task-Component]] only
- No [[04-Execution-Plan-Component]] or [[05-Rule-Blocks-Component]]

### Pros

- ✅ Fast to write
- ✅ Easy for non-technical teams
- ✅ Flexible and experimental

### Cons

- ❌ Less predictable
- ❌ Harder to scale
- ❌ Difficult to maintain consistency

## Tier 2: Task + Minimal Plan

### Use When

- Light structure is needed
- Some validation required
- Simple workflows
- Balanced clarity

### Includes

- [[03-Task-Component]] with clear acceptance criteria
- [[04-Execution-Plan-Component]] with basic steps
- Rule Blocks only if absolutely necessary

### Pros

- ✅ Balanced clarity
- ✅ Still readable
- ✅ Easier to scale than Tier 1

### Cons

- ⚠️ Rules may become implicit
- ⚠️ Validation logic can blur between Task and Plan

## Tier 3: Task + Plan + Rule Blocks

### Use When

- Deterministic outputs required
- Structured formats (JSON/HTML)
- Multi-step workflows
- Non-reasoning or mini models
- Integration into pipelines or products

### Includes

- [[03-Task-Component]] (WHAT)
- [[04-Execution-Plan-Component]] (HOW)
- [[05-Rule-Blocks-Component]] (DETAILS)
- Full [[02-Orthogonality-Principle]]

### Pros

- ✅ Predictable and reproducible
- ✅ Highly maintainable
- ✅ Scalable across many agents
- ✅ Clear ownership of validation

### Cons

- ❌ Higher upfront cost
- ❌ Requires discipline
- ❌ Slower prototyping

## Choosing the Right Tier

Ask these questions:

1. **Does this agent need deterministic, reproducible output?**
   - Yes → Move up a tier
2. **Does it require schema, markup, or IDs?**
   - Yes → Move up a tier
3. **Does it perform multi-step reasoning or validation?**
   - Yes → Move up a tier
4. **Will it integrate into production pipelines?**
   - Yes → Move to Tier 3

## Real-World Examples

**Tier 1:** Brainstorming agent, creative writing assistant, exploratory research

**Tier 2:** Customer support chatbot, FAQ responder with light context

**Tier 3:** Sales quoting agent, brief-writing agent, data pipeline generator, compliance checker

## Key Insight

Orthogonality is a **scalability pattern**, not a religion.

- Use the simplest structure that satisfies requirements
- Introduce separation when failure modes appear
- Keep responsibilities clean and isolated

## Relates To

- [[01-System-Prompt-Design-Framework]] — Framework overview
- [[02-Orthogonality-Principle]] — When orthogonality matters most
- [[11-Brief-Writing-Agent]] — Example of Tier 3
- [[12-Agent-Types]] — Multiple tier examples
