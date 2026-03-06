# Execution Plan Component (HOW)

## Definition

**Execution Plan** defines HOW the agent should proceed: ordered steps, parsing logic, validation, and branching.

## Responsibility

Answers: **"What steps must succeed for the output to be valid?"**

## Includes

- **Ordered, atomic steps** (parse, validate, generate, etc.)
- **Parsing and mapping logic**
- **Validation and preflight checks**
- **Conditional branching** (if/else blocks)
- **Application of Rule Blocks** (by name reference, not definition)

## Never Includes

- Rule definitions or syntax
- Output schema text (referenced by name only)
- Formatting or tone rules
- Examples
- Acceptance criteria

## Recommended Structure

```xml
<plan>
  <step><action_name>parse_input</action_name></step>
  <step><action_name>apply_rules</action_name></step>
  <step><action_name>generate_output</action_name></step>
  <step><action_name>validate_output</action_name></step>

  <if_block condition="invalid">
    <step><action_name>reply_with_issues</action_name></step>
  </if_block>

  <if_block condition="valid">
    <step><action_name>reply_final</action_name></step>
  </if_block>
</plan>
```

## Examples

**Python Agent Plan:**
1. parse_ds_request — Extract data sources and transformations
2. resolve_requirements — Identify needed libraries
3. generate_code — Build modular functions
4. validate_code — Check structure and naming
5. if missing → reply_with_questions
6. if complete → reply_final_code

**Quoting Agent Plan:**
1. parse_quote_request — Extract items, quantities
2. apply_pricing_rules — Retrieve prices
3. generate_quote_json — Assemble JSON
4. validate_json — Check structure and types

## Validation Ownership

[[08-Validation-Discipline]] — Plan owns preflight checks, schema validation, and numbering integrity.

## Relates To

- [[01-System-Prompt-Design-Framework]] — Part of orthogonal trinity
- [[02-Orthogonality-Principle]] — Ensures Plan stays focused on HOW
- [[03-Task-Component]] — WHAT is separate from HOW
- [[05-Rule-Blocks-Component]] — Plan applies rules, doesn't define them
- [[07-Placement-Router]] — Decide when content belongs here

## Anti-Pattern Alert

[[09-Anti-Patterns]] — "Policy Echo" when Plan duplicates Rule Block syntax. Move to [[05-Rule-Blocks-Component]].
