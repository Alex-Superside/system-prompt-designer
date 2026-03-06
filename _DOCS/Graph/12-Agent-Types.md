# Agent Types & Framework Application

## Overview

The [[01-System-Prompt-Design-Framework]] applies across different agent types. This page maps specific agents to their recommended tier and design patterns.

## Agent Type Comparison

| Agent | Tier | Structure | Output | Complexity |
|---|---|---|---|---|
| [[#Sales-Agent]] | Tier 2-3 | Task + Plan + Minimal Rules | Text | Medium |
| [[#Quoting-Agent]] | Tier 3 | Task + Plan + Schema Rules | JSON | High |
| [[#Python-Code-Agent]] | Tier 3 | Task + Plan + Code Rules | Python | High |
| [[#Brainstorming-Agent]] | Tier 1 | Task only | Text | Low |
| [[#FAQ-Responder]] | Tier 2 | Task + Plan | Text | Low-Medium |

---

## Sales Agent

### Tier: Tier 2-3

### Purpose
Provide accurate product guidance that increases conversion without fabrication.

### Task (WHAT)

- **Objective:** Provide accurate, honest, non-pushy product guidance
- **Acceptance Criteria:**
  - MUST ask clarifying questions before recommending
  - MUST map suggestions to official Product Rules
  - MUST avoid fabricated specs or prices
  - If unknown → ask, don't guess
- **Output:** Text-only; paragraphs and bullet lists; no markup

### Execution Plan (HOW)

1. parse_customer_intent — Extract needs, constraints, context
2. validate_intent — Check sufficient information for recommendation
3. map_products — Identify matches per Product Matching Rules
4. generate_recommendations — Craft response using Sales Tone Rules
5. validate_response — Check for fabrication or missing info
6. if incomplete → reply_with_questions
7. if complete → reply_final_recommendation

### Rule Blocks

- **Product Matching Rules** — Map needs → product categories; never infer price
- **Sales Tone Rules** — Helpful, consultative, never pushy
- **Output Format Rules** — "Your Needs → Recommended Options → Why These Fit → Questions"

---

## Quoting Agent

### Tier: Tier 3 (Strict Determinism)

### Purpose
Generate precise, compliant quotes without estimating unknown values.

### Task (WHAT)

- **Objective:** Generate precise, compliant quotes from exact specifications
- **Acceptance Criteria:**
  - MUST follow Pricing Rules for all costs
  - MUST insert "TBD" for any missing required input
  - MUST output in JSON Schema format
  - MUST NOT infer quantities, timelines, or discounts
- **Output:** JSON only; no text outside top-level object

### Execution Plan (HOW)

1. parse_quote_request — Extract items, quantities, constraints
2. validate_request_completeness — Check all required fields present
3. apply_pricing_rules — Retrieve exact prices per Pricing Rules
4. apply_quantity_rules — Validate units and quantities
5. generate_quote_json — Assemble JSON per JSON Schema Rules
6. validate_json — Check structure, types, required fields
7. if missing_data → reply_with_tbd_json
8. if complete → reply_final_quote

### Rule Blocks

- **Pricing Rules** — Price tables by SKU; rounding conventions; forbidden discounts
- **Quantity/Unit Rules** — Valid units (hours, seats, units); validation logic
- **JSON Schema Rules** — Required fields, data types, structure

---

## Python Code Agent

### Tier: Tier 3 (Complex Validation)

### Purpose
Generate clean, production-grade Python code for data pipelines.

### Task (WHAT)

- **Objective:** Generate modular, production-grade Python for ETL/data pipelines
- **Acceptance Criteria:**
  - MUST follow Python Coding Rules and Data Pipeline Rules
  - Output MUST be single Python code block only (no explanations unless asked)
  - MUST be modular: functions-only, no hardcoded paths, clear main()
  - MUST avoid hallucinated libraries; if unknown → ask
  - MUST include docstrings (PEP8)
- **Output:** Single Python code block; no text outside

### Execution Plan (HOW)

1. parse_ds_request — Identify data sources, transformations, outputs, constraints
2. resolve_requirements — Identify needed libraries; if unknown, prompt user
3. generate_code — Build modular functions per Python Coding Rules
4. validate_code — Check structure, main entrypoint, modularity, error handling
5. if missing_info → reply_with_questions
6. if complete → reply_final_code

### Rule Blocks

- **Python Coding Rules** — Functions-only, imports at top, no unused vars, guard-first error handling
- **ETL Naming Rules** — load_*, transform_*, write_*
- **Error-Handling Rules** — Log-and-raise patterns, explicit exceptions

---

## Brainstorming Agent

### Tier: Tier 1 (Creative Freedom)

### Purpose
Generate creative ideas without strict structure.

### Task (WHAT)

- **Objective:** Generate diverse, actionable ideas for [topic]
- **Acceptance Criteria:**
  - MUST provide at least 5 distinct ideas
  - MUST explain why each is relevant
  - Ideas SHOULD be unconventional but feasible

### Execution Plan
None (Task only)

### Rule Blocks
None (Task only)

**Why Tier 1:** Creative output doesn't need rigid structure or validation.

---

## FAQ Responder

### Tier: Tier 2 (Light Structure)

### Purpose
Answer customer questions using a knowledge base.

### Task (WHAT)

- **Objective:** Provide accurate answers from FAQ database
- **Acceptance Criteria:**
  - MUST cite FAQ source
  - MUST not answer outside FAQ scope
  - If not in FAQ → politely decline and offer human support
- **Output:** Text with citations

### Execution Plan (HOW)

1. parse_question — Extract intent and keywords
2. search_faq — Find matching FAQ entries
3. if found → generate_answer_with_citation
4. if not_found → reply_offer_support

### Rule Blocks

- **Citation Format** — [See FAQ: Section Name]

**Why Tier 2:** Some validation (FAQ matching) needed, but no strict schema or complex rules.

---

## Choosing Tier by Agent Type

### Use Tier 1 (Task Only)

- Brainstorming, ideation, creative exploration
- Open-ended research tasks
- Low-risk outputs
- Fast iteration priority

### Use Tier 2 (Task + Plan)

- Question answering with light validation
- Customer support with context
- Recommendation engines
- Simple content generation

### Use Tier 3 (Task + Plan + Rules)

- Structured outputs (JSON, code, schemas)
- High-risk/compliance scenarios
- Production pipelines
- Deterministic accuracy required
- Integration with other systems

---

## Pattern Recognition: Rule Block Reusability

Some Rule Blocks are reusable across agents:

**Citation Rules** → Used in FAQ Responder, Brief-Writing Agent

**JSON Schema Rules** → Reusable for any JSON-producing agent

**Naming Rules** → Python Agent, Java Agent, etc. (language-specific)

**Tone Rules** → Sales Agent, Support Agent, etc.

Orthogonal design enables this reusability.

---

## Relates To

- [[01-System-Prompt-Design-Framework]] — Underlying architecture
- [[06-Tiered-Complexity-Model]] — Tier selection criteria
- [[11-Brief-Writing-Agent]] — Detailed example (Tier 3)
- [[18-Design-Patterns-by-Agent]] — Concrete examples with full prompts
