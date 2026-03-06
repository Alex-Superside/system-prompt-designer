## brand_guardrail_rules

Defines hard brand/account scope boundaries for an agent: how to determine whether a request is in-scope for `{{company_name}}`, what rejection message to use when it is not, and optional topic scoping for allowed request types. This block is applied as the first step in the Execution Plan and ensures no downstream processing occurs if the guardrail fails.

### Source Locations

- `_DOCS/breif-generator-prompt-26-02-2026.md` — `<guardrails> Brand Guardrail`
- `_DOCS/Graph/14-Guardrail-System.md` — Definition, Implementation in Brief-Writing-Agent, Guardrail Enforcement Rules
- `_DOCS/Graph/11-Brief-Writing-Agent.md` — Rule Blocks (DETAILS), Execution Plan – `apply_brand_guardrail`

