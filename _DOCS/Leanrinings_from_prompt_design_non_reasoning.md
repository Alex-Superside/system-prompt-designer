# Learnings from Agent instructions design - non reasoning models

---

### **TL;DR**

- **Task = WHAT** (mission, acceptance criteria, output contract, rule references).
- **Plan = HOW** (ordered steps and validations that *apply* those rules).
- **Rule Blocks = Single source of truth** for syntax, mappings, numbering, and formatting.
    
    Keep them separate, reference by name, and your agent stays predictable, maintainable, and easy to evolve.
    

Below are **three fully worked, practical examples** showing how to apply the **Task / Execution Plan / Rule Blocks** structure to different agent types.

Each is short, orthogonal, and realistic — and each includes a brief **counterpoint** at the end.

---

# **1) Sales AI Agent — System Prompt Example (Practical)**

## **Task (WHAT)**

- Objective: Provide accurate, honest, non-pushy product guidance that increases conversion without fabricating details.
- Acceptance Criteria:
    - MUST ask clarifying questions before recommending a product.
    - MUST provide product suggestions mapped to the official Product Rules.
    - MUST avoid fabricated specs, prices, or promotions; if unknown → ask.
    - Output MUST be in the “Sales Response Format” defined in Output Rules.
- Output Contract:
    - Text-only; no markup except paragraphs and bullet lists.
- Rules to Apply:
    - Product Matching Rules
    - Sales Tone Rules
    - Output Format Rules

## **Execution Plan (HOW)**

```xml
<plan>
  <step><action_name>parse_customer_intent</action_name><description>Extract needs, constraints, and context.</description></step>
  <step><action_name>map_products</action_name><description>Identify product matches per Product Matching Rules.</description></step>
  <step><action_name>generate_recommendations</action_name><description>Craft recommendations using Sales Tone Rules and Output Format Rules.</description></step>
  <step><action_name>validate_response</action_name><description>Check for missing info, rule violations, or hallucinations.</description></step>
  <if_block condition="info_missing"><step><action_name>reply_with_questions</action_name><description>Ask for missing details only.</description></step></if_block>
  <if_block condition="info_complete"><step><action_name>reply_final</action_name><description>Return final sales guidance.</description></step></if_block>
</plan>
```

## **Rule Blocks (Examples)**

- **Product Matching Rules**: Map needs → product categories; never infer price.
- **Sales Tone Rules**: Helpful, consultative, never pushy.
- **Output Format Rules**: Sectioned: “Your Needs → Recommended Options → Why These Fit → Questions.”

**Counterpoint:**

For fast-moving sales tasks, a looser model (Task-only) may outperform a rigid orthogonal design. Complexity is only justified when you need governance and consistency across many agents.

---

# **2) Quoting AI Agent — System Prompt Example (Practical)**

## **Task (WHAT)**

- Objective: Generate precise, compliant quotes without estimating unknown values.
- Acceptance Criteria:
    - MUST follow the Pricing Rules for all costs.
    - MUST insert “TBD” for any missing required input.
    - MUST output in the Quote JSON Schema defined in Schema Rules.
    - MUST not infer quantities, timelines, or discounts.
- Output Contract:
    - JSON only, no text outside the top-level object.
- Rules to Apply:
    - Pricing Rules
    - Quantity/Unit Rules
    - JSON Schema Rules

## **Execution Plan (HOW)**

```xml
<plan>
  <step><action_name>parse_quote_request</action_name><description>Extract items, quantities, constraints.</description></step>
  <step><action_name>apply_pricing_rules</action_name><description>Retrieve prices per Pricing Rules; apply Quantity/Unit Rules.</description></step>
  <step><action_name>generate_quote_json</action_name><description>Assemble JSON strictly per JSON Schema Rules.</description></step>
  <step><action_name>validate_json</action_name><description>Ensure valid JSON; detect missing fields; check numeric types.</description></step>
  <if_block condition="missing_data"><step><action_name>reply_tbd</action_name><description>Return JSON with TBD placeholders.</description></step></if_block>
  <if_block condition="complete"><step><action_name>reply_final</action_name><description>Return validated quote JSON.</description></step></if_block>
</plan>
```

## **Rule Blocks (Examples)**

- **Pricing Rules**: Price tables by SKU; rounding conventions; forbidden discounts.
- **Quantity/Unit Rules**: Must validate units (hours, seats, units).
- **JSON Schema Rules**: Keys, required fields, value types, arrays.

**Counterpoint:**

A quoting agent often needs tight rule blocks, but excessive structural separation may slow iteration when pricing rules update often. Embedding schema inline temporarily can speed prototyping.

---

# **3) Python Coding Agent for Data Science / ETL Pipelines**

## **Task (WHAT)**

- Objective: Generate clean, production-grade Python code for data pipelines.
- Acceptance Criteria:
    - MUST follow the Python Coding Rules and Data Pipeline Rules.
    - MUST output a single code block only (Python), no explanations unless asked.
    - Code MUST be modular: functions-only, no hardcoded paths, clear main entry point.
    - MUST avoid hallucinated library names; if needed library is unknown → ask.
    - MUST follow PEP8, docstrings required.
- Output Contract:
    - Single Python code block; no text outside.
- Rules to Apply:
    - Python Coding Rules
    - ETL Naming Rules
    - Error-Handling Rules

## **Execution Plan (HOW)**

```xml
<plan>
  <step><action_name>parse_ds_request</action_name>
    <description>Identify input data sources, transformations, outputs, and constraints.</description>
  </step>

  <step><action_name>resolve_requirements</action_name>
    <description>Identify needed libraries; if unknown, prompt the user.</description>
  </step>

  <step><action_name>generate_code</action_name>
    <description>Build modular functions following Python Coding Rules and ETL Naming Rules.</description>
  </step>

  <step><action_name>validate_code</action_name>
    <description>Check structure, main entrypoint, modularity, prohibited patterns, error handling.</description>
  </step>

  <if_block condition="missing_info">
    <step><action_name>reply_with_questions</action_name>
      <description>Ask for required missing parameters.</description>
    </step>
  </if_block>

  <if_block condition="complete">
    <step><action_name>reply_final_code</action_name>
      <description>Return the final Python code block.</description>
    </step>
  </if_block>
</plan>
```

## **Rule Blocks (Examples)**

- **Python Coding Rules**: Functions-only, dependency imports at top, no unused vars, guard-first error handling.
- **ETL Naming Rules**: load_*, transform_*, write_*.
- **Error-Handling Rules**: Log-and-raise patterns, explicit exceptions.

**Counterpoint:**

For exploratory data analysis (EDA), rigid structure adds friction. A hybrid mode (Task + very short Plan) can be more productive when the user wants quick experiments rather than production pipelines.

---

## **5) Validation Discipline (Who owns what)**

**Task owns Acceptance Criteria**

- “HTML only with tags X.”
- “Inline citations required for all factual claims.”
- “Highlights for gaps per Highlight Rules.”
- “No trailing Citations section; all provenance is inline.”

**Plan owns Preflight Checks**

- “Schema is valid JSON/HTML; no code fences.”
- “All <mark>/<sup> only where allowed by the output contract.”
- “Sequential superscripts; unique data-citation-id; data-id matches regex.”
- “If fragment edit: continue numbering from current maxima.”

---

## **6) Anti-Patterns & Smells**

- **Policy Echo:** Plan restates Highlight/Citation syntax → move to Rule Blocks.
- **Dual Ownership:** Both Task and Plan say where markup is allowed → keep in Task (contract) and only *validate* in Plan.
- **Mixed Intent:** Task contains steps (parse, map, generate) → move to Plan.
- **Verbose Examples Everywhere:** Keep examples close to rules; Task/Plan link by name.
- **FE Language:** Any mention of hover/visibility/colors → remove from both.

---

## **7) Change Management (Future-Proofing)**

- **Rules change often; flow changes rarely.** Keep rules isolated so updates don’t touch Task/Plan.
- **Introduce new rules** by adding a named block, then only *reference* it in Task/Plan.
- **Regression safety:** Maintain a tiny “golden” example per rule block; Plan’s validations should conceptually enforce them.

---

## **8) Practical Patterns for GPT (non-reasoning)**

- Use **MUST/NEVER** verbs; avoid soft language.
- Keep **Task** short; **Plan** 5–10 steps, each yielding a checkable artifact.
- Use **regex constraints** and **global numbering** rules in the rule blocks; Plan just validates.
- Put **variables at the end** of the full system prompt for KV efficiency.
- Add a **one-line scoping guard** in Task (where markup is allowed) and a **final checklist** step in Plan.

---

## **9) When Limited Duplication Helps (Rare, Controlled)**

- If a model keeps violating a *critical* constraint (e.g., markup scoping), add a **one-line reminder** in Task **and** a **single validation line** in Plan.
- Keep this duplication minimal and verbatim; remove once behavior stabilizes.

---

## **10) One-Screen Example (Before → After)**

**Before (mixed):**

- Task: “Always use <mark class='highlight' data-type='gap'>TBD</mark>; parse inputs; then generate; then check numbering…”
- Plan: Repeats highlight/citation syntax and also steps.

**After (orthogonal):**

- Task: “Output HTML; follow Highlight/Citation rules; provenance inline; markup only inside ACTION.value; never estimate.”
- Plan: Steps to parse → map → generate → validate → reply. No rule prose anywhere.
