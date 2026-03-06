# Rule Blocks Component (DETAILS)

## Definition

**Rule Blocks** are the single source of truth for all syntax and logic that may change over time.

## Responsibility

Answers: **"Where do future changes belong?"**

## Includes

- **Formatting and markup rules**
- **Schema definitions** (JSON, HTML, XML)
- **Mapping rules** (IDs, keys, transforms)
- **Numbering and sequencing rules**
- **Citation and highlight rules**
- **Regex constraints**
- **Minimal examples** (to illustrate syntax)

## Never Includes

- Procedural steps
- Tone or voice rules
- Acceptance criteria
- Large example outputs

## Characteristics

- Contain syntax and rule text
- May include tiny minimal examples to illustrate
- Are referenced by name from Task and Plan
- **Never duplicated elsewhere in the prompt**
- Self-contained and independently modifiable

## Examples

**Product Matching Rules**
- Map needs → product categories
- Never infer price
- Always consult official product catalog

**JSON Schema Rules**
```json
{
  "quote_id": "string",
  "items": [{"sku": "string", "quantity": "number"}],
  "total": "number"
}
```

**Citation Formatting Rules**
```html
<mark data-type="citation">cited text</mark><sup>1</sup>
```

**Python Naming Rules**
- load_* for data loading functions
- transform_* for transformation functions
- write_* for output functions

## Stability & Naming

Rule Block names are **referenced from Task and Plan**. Keep names stable. If a Rule Block becomes >150 lines, consider splitting by semantic purpose.

## Relates To

- [[01-System-Prompt-Design-Framework]] — Part of orthogonal trinity
- [[02-Orthogonality-Principle]] — Rule Blocks prevent duplication
- [[04-Execution-Plan-Component]] — Plan applies rules, doesn't define them
- [[13-Citation-System]] — Example Rule Block for citations
- [[17-Markup-and-Highlighting]] — Example Rule Blocks for markup

## Anti-Pattern Alert

[[09-Anti-Patterns]] — "Schema Leakage" when Rule Block content is repeated in Plan or Task. Extract immediately.
