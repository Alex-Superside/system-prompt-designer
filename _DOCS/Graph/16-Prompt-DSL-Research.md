# Prompt DSL Research

## Definition

Research into Domain-Specific Language (DSL) approaches for designing and generating system prompts programmatically.

## Motivation

Traditional prompt design (Tier 1-3) works well but:
- Written manually (time-consuming)
- Hard to version and diff (unstructured text)
- Difficult to test components independently
- Scales poorly with many agents

**Question:** Can we treat prompts like code?

## DSL Approach

Instead of free-form text, use structured language to **generate** prompts:

```dsl
agent "Brief-Writer"
  brand: "{{company_name}}"
  model: "claude-haiku"
  tier: 3

  task:
    objective: "Generate creative briefs with citations"
    accepts: [supporting_data, user_request]
    outputs: html
    constraints: [
      "MUST include citations",
      "MUST mark gaps with GAP/TBD"
    ]

  plan:
    step apply_brand_guardrail:
      input: user_request
      rules: BrandGuardrailRules
      on_fail: reject

    step parse_supporting_data:
      input: supporting_data
      rules: ContextSourceMappingRules

    step generate_brief:
      input: [supporting_data, user_request]
      rules: [CitationFormattingRules, GapHighlightingRules]

  rules:
    CitationFormattingRules: {
      markup: "<mark data-type='citation'>text</mark>",
      superscript: "<sup>number</sup>",
      numbering: sequential
    }
```

**Benefit:** Language is declarative, structured, version-able, testable.

## DSL Advantages

| Aspect | Traditional Text | DSL |
|---|---|---|
| Version control | Diff is entire text | Diff is specific fields |
| Reusability | Copy-paste Rule Blocks | Compose rules into libraries |
| Validation | Manual review | Can validate syntax/structure |
| Generation | Write all agents manually | Generate variants (e.g., for different models) |
| Testing | Test entire prompt | Test individual rules |

## DSL Disadvantages

| Aspect | Cost |
|---|---|
| Learning curve | Users must learn DSL syntax |
| Tooling | Need parser, validator, generator |
| Flexibility | DSL may not support all pattern variations |
| Integration | Must output to text prompt afterward |

## Current Research Artifacts

The repository contains preliminary DSL research:

- `prompt-dsl-language-research.md` — Syntax exploration
- `prompt-TKDSL-workframe.prompt-design.md` — Workframe approach

**Status:** Research-phase exploration, not yet production-ready.

## Potential DSL Features

### 1. Rule Libraries

```dsl
library CitationRules:
  template CitationFormat:
    markup: "<mark data-type='citation'>%text%</mark>"
    superscript: "<sup>%number%</sup>"
    numbering: sequential
    validation: check_sequential_numbers

rule BriefCitations extends CitationFormat:
  categories: [CreativeStandards, WorkflowPreferences, RecurrentProjects]
  validation: [check_sequential, check_categories]
```

### 2. Agent Composition

```dsl
agent "GenericQuoter":
  tier: 3
  plan: [parse_input, apply_rules, generate_output, validate, respond]
  rules: [PricingRules, SchemaRules, ValidationRules]

agent "SalesQuoter" extends "GenericQuoter":
  rules: override PricingRules with SalesPricingRules
```

### 3. Model Variants

```dsl
agent "Brief-Writer":
  variants:
    - model: "claude-opus"
      tier: 2  # Can use simpler structure
    - model: "claude-haiku"
      tier: 3  # Needs explicit rules
      rules: EnhanceExplicitness()
```

## Implementation Challenges

1. **DSL Design:** What syntax is intuitive?
2. **Parsing:** How to handle variations?
3. **Code Generation:** How to reliably output prompts from AST?
4. **Integration:** How to test generated prompts?
5. **Debugging:** How to help users fix broken generated prompts?

## Relationship to Framework

DSL approach assumes [[01-System-Prompt-Design-Framework]] (Tier 3 structure).

**Without orthogonal framework:** DSL is harder (more variations to handle).

**With orthogonal framework:** DSL can be simpler (Task, Plan, Rules are regular).

## Future Directions

1. **Stabilize core syntax** — Make DSL stable enough for production
2. **Build tooling** — Parser, validator, generator, test framework
3. **Create rule libraries** — Pre-built rules for common agents
4. **Document patterns** — How to compose agents from rules
5. **Integration layer** — Connect DSL tools to model APIs

## Current Status

This is **research**, not production-ready. Use [[01-System-Prompt-Design-Framework]] manually until DSL matures.

## Relates To

- [[01-System-Prompt-Design-Framework]] — Foundation for DSL
- [[02-Orthogonality-Principle]] — Enables DSL composition
- [[05-Rule-Blocks-Component]] — DSL's Rule Blocks are reusable units
