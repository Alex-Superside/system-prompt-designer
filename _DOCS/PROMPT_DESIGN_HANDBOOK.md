---
title: Prompt Design Handbook
version: "1.0"
date: "2026-03-04"
status: Canonical Reference
audience: AI Engineers, Prompt Engineers, Product Teams
description: >
  The single source of truth for orthogonal prompt architecture and tiered
  complexity modeling. Synthesizes all research, frameworks, and production
  learnings from the _DOCS knowledge base.
---

# Prompt Design Handbook

**Version 1.0 | March 2026**

---

## Table of Contents

- [Introduction](#introduction)
- [Part 1: Foundations](#part-1-foundations)
  - [1.1 Linguistic Foundations](#11-linguistic-foundations)
  - [1.2 The Orthogonal Design Principle](#12-the-orthogonal-design-principle)
  - [1.3 Why Orthogonality Matters](#13-why-orthogonality-matters)
  - [1.4 The Placement Router](#14-the-placement-router)
- [Part 2: Design Components](#part-2-design-components)
  - [2.1 The Task Block (WHAT)](#21-the-task-block-what)
  - [2.2 The Execution Plan (HOW)](#22-the-execution-plan-how)
  - [2.3 Rule Blocks (DETAILS)](#23-rule-blocks-details)
  - [2.4 How Components Interact](#24-how-components-interact)
- [Part 3: The Tiered Complexity Model](#part-3-the-tiered-complexity-model)
  - [3.1 Overview](#31-overview)
  - [3.2 Tier 1 — Task Only](#32-tier-1--task-only)
  - [3.3 Tier 2 — Task + Minimal Plan](#33-tier-2--task--minimal-plan)
  - [3.4 Tier 3 — Full Orthogonal Design](#34-tier-3--full-orthogonal-design)
  - [3.5 Decision Framework: Choosing the Right Tier](#35-decision-framework-choosing-the-right-tier)
- [Part 4: Anti-Patterns](#part-4-anti-patterns)
  - [4.1 Policy Echo](#41-policy-echo)
  - [4.2 Mixed Intent](#42-mixed-intent)
  - [4.3 Dual Ownership](#43-dual-ownership)
  - [4.4 Schema Leakage](#44-schema-leakage)
  - [4.5 Frontend Language](#45-frontend-language)
  - [4.6 Detection and Recovery](#46-detection-and-recovery)
  - [4.7 When to Break the Rules](#47-when-to-break-the-rules)
- [Part 5: Applied Examples](#part-5-applied-examples)
  - [5.1 The Brief-Writing Agent (Flagship Tier 3 Example)](#51-the-brief-writing-agent-flagship-tier-3-example)
  - [5.2 Guardrail Patterns](#52-guardrail-patterns)
  - [5.3 Citation and Highlight Patterns](#53-citation-and-highlight-patterns)
  - [5.4 Real-World Prompt Evolution (Before vs After)](#54-real-world-prompt-evolution-before-vs-after)
  - [5.5 Agent Patterns by Type](#55-agent-patterns-by-type)
- [Part 6: Designing for Non-Reasoning Models](#part-6-designing-for-non-reasoning-models)
  - [6.1 Why This Matters](#61-why-this-matters)
  - [6.2 Design Principles](#62-design-principles)
  - [6.3 Four Design Patterns](#63-four-design-patterns)
  - [6.4 Non-Reasoning Readiness Checklist](#64-non-reasoning-readiness-checklist)
- [Part 7: DSL and Programmatic Approaches](#part-7-dsl-and-programmatic-approaches)
  - [7.1 The Three Prompt Layers](#71-the-three-prompt-layers)
  - [7.2 Format Options and Trade-offs](#72-format-options-and-trade-offs)
  - [7.3 DSL Design Principles](#73-dsl-design-principles)
  - [7.4 When DSL Makes Sense](#74-when-dsl-makes-sense)
  - [7.5 Current Status and Future Directions](#75-current-status-and-future-directions)
- [Part 8: Evaluation and Iteration](#part-8-evaluation-and-iteration)
  - [8.1 Quality Gates](#81-quality-gates)
  - [8.2 The Orthogonality Checklist](#82-the-orthogonality-checklist)
  - [8.3 Testing Prompt Quality](#83-testing-prompt-quality)
  - [8.4 Feedback Loops and Refinement](#84-feedback-loops-and-refinement)
- [Part 9: Practical Workflow](#part-9-practical-workflow)
  - [9.1 Day-to-Day Design Process](#91-day-to-day-design-process)
  - [9.2 Repository and File Organization](#92-repository-and-file-organization)
  - [9.3 Collaboration Patterns](#93-collaboration-patterns)
  - [9.4 Integration with LLM Applications](#94-integration-with-llm-applications)
- [Appendix A: Glossary of Terms](#appendix-a-glossary-of-terms)
- [Appendix B: Template Library](#appendix-b-template-library)
- [Appendix C: Decision Trees](#appendix-c-decision-trees)
- [Appendix D: Further Reading](#appendix-d-further-reading)

---

## Introduction

This handbook is the canonical reference for prompt design methodology in this organization. It synthesizes all research, production learnings, and framework documentation from the `_DOCS` knowledge base into a single, actionable guide.

**Who this is for**: AI engineers, prompt engineers, and product teams building LLM-based agents. No prior knowledge of this framework is assumed, but familiarity with LLM concepts is expected.

**How to use this handbook**:
- New practitioners: Read Part 1, Part 2, and Part 3 in sequence, then work through Part 5 examples.
- Experienced practitioners: Use Part 4 (Anti-Patterns) and the Appendix checklists for review and debugging.
- Teams onboarding to the framework: Use Part 9 (Practical Workflow) and Appendix B (Templates) as starting points.

**What this methodology achieves**:

Traditional prompt engineering produces "walls of text" that work until they do not. As agents grow in complexity, the same rules get restated in the objective, in the instructions, and in examples. When the rules change, every copy must be found and updated — and inconsistencies between them cause unpredictable failures. This methodology solves that problem by applying a single organizing principle: **orthogonality**.

Four concrete outcomes follow from this approach:

1. Reduced ambiguity: non-overlapping components eliminate contradictory instructions.
2. Improved predictability: structured components allow non-reasoning models to achieve error rates below 2%.
3. Safe scaling: centralized rule sets allow changes to propagate across multiple agents by updating one file.
4. Faster onboarding: team members read Task, then Plan, then Rule Blocks — each serves a clear purpose.

> "Good system prompts are boring, predictable, and easy to change."

---

## Part 1: Foundations

### 1.1 Linguistic Foundations

Prompt engineering is not "talking" to an AI; it is **encoding a state machine** using a shared token-based language. To design effective prompts, you must bridge the gap between how humans use language and how LLMs process tokens.

#### 1.1.1 Words as Tokens, Not Concepts
- **Humans**: Use words as pointers to complex, shared abstract concepts (e.g., "be helpful").
- **LLMs**: Process words as statistical tokens. "Helpful" is a probability cluster, not a value system.
- **Rule**: Replace abstract adjectives (e.g., "brief," "polite") with **explicit constraints** (e.g., "maximum 120 words," "use first-person plural").

#### 1.1.2 Semantic Density vs. Word Count
- **The LLM "reads" for density**: Redundant fluff in a prompt dilutes the attention (softmax) the model pays to critical rules.
- **Middle-Term DSL Strategy**: Use a hybrid language—human-readable but highly structured (like YAML or KeyTokenDSL)—to maximize the **semantic signal per token**.
- **Efficiency**: A prompt is "better" when it says the same thing in fewer, higher-signal tokens.

#### 1.1.3 Structural Grammar as "Sense-Making"
- **Reasoning**: Larger models (Claude 3.5, o1) can "reason" through ambiguous prose, but smaller/non-reasoning models (Haiku, 4o-mini) cannot.
- **Orthogonality as Logic**: By separating **WHAT** (Task), **HOW** (Plan), and **DETAILS** (Rules), you create a structural "grammar" that the LLM's attention mechanism can follow deterministically.

#### 1.1.4 Language as "Constraints," not "Ideas"
- A prompt is a **boundary box**. Every word that doesn't define a constraint is noise.
- **The "Boring" Mandate**: A "good" system prompt is intentionally boring. It avoids creative prose in favor of prescriptive rules.
- **Explicitness**: "Infer as appropriate" is a linguistic failure. "If X is missing, insert TBD" is a linguistic success.

#### 1.1.5 Context Caching and Token Stability
- **Static vs. Dynamic**: LLMs cache the "prefix" of a prompt. If the first 500 tokens of your prompt change between calls (e.g., injecting a dynamic timestamp at the top), the model must re-process the entire prompt.
- **Rule**: Place all static rules (System Prompt) at the top and push all dynamic data (User Input) to the end to maximize KV-cache reuse.

### 1.2 The Orthogonal Design Principle

A system prompt built on this framework is divided into three non-overlapping components. **Orthogonal** means that each component has exactly one responsibility and that responsibility does not belong anywhere else.

```
  +-----------------------------------------------------------+
  |                     SYSTEM PROMPT                         |
  +-----------------------------------------------------------+
         |                      |                     |
  +------v------+      +--------v-------+    +--------v--------+
  |    TASK     |      |  EXECUTION     |    |  RULE BLOCKS    |
  |   (WHAT)    |      |    PLAN        |    |   (DETAILS)     |
  |             |      |    (HOW)       |    |                 |
  +-------------+      +----------------+    +-----------------+
  | Outcomes,   |      | Ordered steps, |    | Syntax, schemas,|
  | acceptance  |      | validation,    |    | mappings,       |
  | criteria,   |      | branching      |    | formatting,     |
  | output      |      | logic          |    | regex, examples |
  | contract    |      |                |    |                 |
  +-------------+      +----------------+    +-----------------+
         |                      |                     |
         +--------REFERENCES----+---------------------+
                (by name only, no duplication)
```

| Component | Responsibility | Mental Model |
|---|---|---|
| **Task** | WHAT the agent must achieve | "What does a correct output look like?" |
| **Execution Plan** | HOW the agent should proceed | "What steps must succeed for the output to be valid?" |
| **Rule Blocks** | DETAILS: syntax and logic that may change over time | "Where do future changes belong?" |

Each component must be:
- **Independent**: understandable without reading the others.
- **Reference-only**: when Task or Plan need to invoke a rule, they name it — they never restate it.
- **Single-purpose**: no component owns two different kinds of content.

The principle is grounded in practical engineering: if a rule lives in one place and is referenced everywhere else, updating it requires one edit. If it lives in three places, updates require three edits — and the inconsistency risk multiplies, not adds.

### 1.3 Why Orthogonality Matters

The cost of duplication in prompt design is not linear. Two copies of a rule create double the review burden. But three copies do not create triple the risk — they create compounding inconsistency risk: the model may receive contradictory signals from different copies that drift apart over time, leading to hallucinations that are difficult to trace.

**Maintenance comparison**:

| Scenario | Without Framework | With Framework |
|---|---|---|
| Change a formatting rule | Edit 3+ places, review 3+ times | Edit 1 Rule Block, review once |
| Onboard a new contributor | "Read the entire prompt and good luck" | "Read Task, then Plan, then Rule Blocks — clear path" |
| Debug an output error | Search entire prompt for the relevant instruction | Check the specific validation step in the Plan |
| Add a new agent with shared rules | Copy-paste, hope nothing drifts | Reuse the Rule Blocks, write a new Task and Plan |
| Scale from 3 agents to 30 agents | Maintenance exponentially increases | Rule Block changes propagate across all agents |

From empirical testing on the Brief-Writing Agent, the cost-benefit becomes clear almost immediately: the framework pays back after 2-3 agents or 2-3 rule changes.

**The deeper argument**: Structure is more important than raw model capability.

There is a common assumption that larger, more capable models reduce the need for careful prompt design. The evidence from production deployments contradicts this. A Tier 3 orthogonal prompt on a smaller model (Claude Haiku) outperforms a Tier 1 narrative prompt on a larger model (Claude 3) for any structured, deterministic task. The reason is that structure prevents hallucination. A model using its "best effort" to infer intent from a poorly designed prompt is not just less reliable — it is wasteful: expensive capability is being used to compensate for an avoidable design failure.

> "You can't scale without structure. Tier 1 prompts stop scaling at 2-3 agents. Tier 3 scales to hundreds."

### 1.4 The Placement Router

The **Placement Router** is the authoritative decision filter for where any given instruction belongs. It is not a heuristic — it is a systematic tool. Apply these questions in order to every line of a prompt before shipping.

**The seven decision questions**:

1. **Is it an outcome or a method?**
   - Outcome (success condition, acceptance criterion) → **Task**
   - Method (procedural step, how to achieve the outcome) → **Plan**

2. **Is it rule text or syntax?**
   - Rule text or syntax (format specs, schema definitions, regex, mapping tables) → **Rule Block**
   - Not purely rule text → continue to Q3

3. **Does it specify order, sequence, or branching?**
   - Yes (if/then, step 1 then step 2, conditional logic) → **Plan**
   - No → continue to Q4

4. **Is it a format or schema contract?**
   - Yes (output must be JSON, output must use HTML, scope of what is allowed) → **Task**
   - No → continue to Q5

5. **Is it a validation or a check?**
   - Yes (preflight check, schema validation, ID integrity, final verification) → **Plan**
   - No → continue to Q6

6. **Is it about where markup is allowed?**
   - Scope definition (what can be marked) → **Task**
   - Scope enforcement (validate that markup is applied correctly) → **Plan**

7. **Is it an example?**
   - Yes → **Rule Block only** (minimal examples, kept close to the rule they illustrate)
   - No, it is a large reference or template → **Rule Block**

**Quick reference table**:

| Content | Belongs In | Why |
|---|---|---|
| "Output must be valid JSON" | Task | Acceptance criteria |
| "Validate JSON structure against schema" | Plan | Procedural validation step |
| `{ "quote_id": "string", "items": [...] }` | Rule Block | Syntax definition (JSON schema) |
| "MUST ask before recommending" | Task | Acceptance criteria |
| "Step 1: Extract user intent from request" | Plan | Step / sequencing |
| "Tone is consultative, never pushy" | Rule Block | Rules / style definition |
| "Format quotes with these section headers" | Rule Block | Formatting rules |
| `<mark class="highlight" data-type="gap">` | Rule Block | Markup syntax example |

**Testing placement**:

Before shipping, answer three yes/no questions:
1. Does the Task contain any procedural steps ("first", "then", "next")? If yes → move to Plan.
2. Does the Plan contain any rule syntax or schema definitions? If yes → move to Rule Block.
3. Do the Rule Blocks contain any procedural steps? If yes → move to Plan.

If all three answers are "no", the placement is orthogonal.

---

## Part 2: Design Components

### 2.1 The Task Block (WHAT)

The Task block is the mission statement and output contract of the agent. It is entirely declarative: it defines what the agent must achieve, not how.

**What it includes**:
- **Objective**: One sentence defining the agent's purpose.
- **Acceptance Criteria**: Explicit MUST and NEVER statements that define success and failure.
- **Output Contract**: The format, scope, and allowed elements of the final output.
- **Rule References**: Named references to Rule Blocks (names only, no rule text).

**What it never includes**:
- Steps or sequencing (that is the Plan's job).
- Procedural logic of any kind.
- Examples (those belong in Rule Blocks).
- Rule text, syntax, or schema definitions.

**Example: Task block for the Brief-Writing Agent**:

```
## Task Overview

Objective: Generate a complete, internally consistent creative brief for {{company_name}}.

You will receive:
- A customer request (which may be short or detailed).
- A Supporting Data section containing brand guidelines, past brief pairs,
  account DOs & DON'Ts, and template project files.

Acceptance Criteria:

1. MUST use only information from the user input and Supporting Data.
2. MUST accurately map all factual statements to their source using
   Citation Formatting Rules.
3. MUST mark all missing, uncertain, or pending information using
   Highlight Formatting Rules.
4. MUST apply the Brand Guardrail before any other processing.
5. MUST output all text in clean, valid HTML using only:
   <h1>–<h3>, <p>, <ul>, <li>, <mark>, <sup>, <br>, <hr>.
6. NEVER fabricate information, estimate values, or hallucinate sources.
7. NEVER include a separate trailing Citations section — all provenance
   is expressed through inline citation metadata.
8. NEVER produce content for brands other than {{company_name}} unless
   they appear as factual mentions in provided Supporting Data.

Output Contract:
- HTML only (no Markdown)
- Semantic markup using <mark> tags with data-type attributes
- Sequential global citation numbering
- No trailing Citations list

Governing Rules:
- Brand Guardrail
- Context Source Mapping Rules
- Citation Formatting Rules
- Highlight Formatting Rules
```

**Common mistake: Tone rules in Task**

A frequent error is placing tone or style guidelines in the Task block. Tone is HOW the agent communicates, not WHAT it achieves. It belongs in a Rule Block.

```
# Wrong
Task: "Use a friendly, consultative tone in all responses."

# Correct
Rule Block — Tone Rules:
"Friendly: Address customer needs directly. Consultative: Explore options,
do not push one choice. Never pushy: No urgency or scarcity language."

Task: "Follow Tone Rules throughout all responses."
```

### 2.2 The Execution Plan (HOW)

The Execution Plan operationalizes the Task. It is the procedural workflow: an ordered sequence of atomic steps that collectively produce a valid output. It applies Rule Blocks by referencing them; it never defines them.

**What it includes**:
- Ordered, atomic steps — each step should be small enough to be a single function.
- Parsing and mapping logic.
- Validation and preflight checks.
- Conditional branching (if/else blocks).

**What it never includes**:
- Rule definitions or schema text.
- Formatting or tone rules.
- Output schema structure.
- Examples of any kind.

**Recommended structure**: XML-style tags that provide unambiguous structural cues to the model.

```xml
<plan>
  <step>
    <action_name>step_name</action_name>
    <description>What this step does, expressed as an atomic action.</description>
  </step>

  <if_block condition="condition_name">
    <step>
      <action_name>conditional_step</action_name>
      <description>Action taken when condition is met.</description>
    </step>
  </if_block>
</plan>
```

**Key insight: Guardrails as Step 1**

Guardrail checks must always be the first step in the Plan. If an agent processes a request — queries databases, interprets data, generates output — and then discovers the request is out of scope, all that work is wasted. Fail fast: check scope first, then proceed only when the guardrail passes.

**Key insight: Budget for validation**

30–40% of Plan steps should be validation steps. From empirical testing on the Quoting Agent: without validation, 15% of incorrect quotes reached users; with explicit validation steps, this dropped to below 0.5%. Validation is not overhead — it is what makes the output trustworthy.

**Example: Execution Plan for the Brief-Writing Agent (full production version)**:

```xml
<plan>

  <step>
    <action_name>parse_user_input</action_name>
    <description>
      Extract all input sections from the user prompt:
      - Customer request and contextual notes
      - Supporting Data subsections and their visible headers
      - Attached files or references for contextual grounding
    </description>
  </step>

  <step>
    <action_name>interpret_supporting_data</action_name>
    <description>
      Analyze all sections within the Supporting Data to determine:
      - Their conceptual category using Context Source Mapping Rules.
      - Their relative importance for each brief section.
      - The balance between user-provided input and contextual knowledge.
    </description>
  </step>

  <step>
    <action_name>identify_request_type_and_brief_pairs</action_name>
    <description>
      Identify the Customer Request Type and map it to relevant brief pairs
      within the Supporting Data. Select applicable brand, template, and
      tone references needed to construct the brief.
    </description>
  </step>

  <step>
    <action_name>map_context_citations</action_name>
    <description>
      Parse visible Markdown headers within the Supporting Data to determine
      source categories per Context Source Mapping Rules. Generate global,
      sequential citation numbering and metadata fields (data-citation-id,
      data-id, data-type, data-reasoning) per Citation Formatting Rules.
    </description>
  </step>

  <step>
    <action_name>generate_brief</action_name>
    <description>
      Compose the full creative brief using the HTML structure defined in
      the Output schema. Apply all rule systems in coordination:
      - Cite every factual or derived statement with correct metadata.
      - Highlight all uncertain or missing data per Highlight Formatting Rules.
      - Weight and interpret contextual content per Context Source Mapping Rules.
      - Follow {{company_name}} tone, brand guidelines, and deliverable standards.
    </description>
  </step>

  <step>
    <action_name>validate_brief_consistency</action_name>
    <description>
      Perform final checks to ensure:
      - Sequential citation numbering across the entire document.
      - All placeholders and gaps are properly highlighted.
      - No unreferenced factual statements remain.
      - Structural hierarchy and logical coherence are preserved.
    </description>
  </step>

  <step>
    <action_name>validate_tone_and_style</action_name>
    <description>
      Compare the generated brief's tone and style to:
      - The Customer Tone of Voice and Writing Style section in Supporting Data.
      - The tone implied by the customer's initial prompt.
      Ensure alignment in phrasing, readability, and emotional tone.
    </description>
  </step>

  <step>
    <action_name>crosscheck_highlight_citation_links</action_name>
    <description>
      Verify that every highlighted placeholder corresponds to a recognized
      contextual category. Ensure all cited statements have valid mapped
      sources. Flag inconsistencies for user confirmation.
    </description>
  </step>

  <step>
    <action_name>verify_rule_compliance</action_name>
    <description>
      Confirm full adherence to all governing rule systems:
      - Brand Guardrail
      - Context Source Mapping Rules
      - Citation Formatting Rules
      - Highlight Formatting Rules
      Any deviation or missing structure must trigger a self-correction
      pass before output.
    </description>
  </step>

  <if_block condition="missing information or critical gaps">
    <step>
      <action_name>reply</action_name>
      <description>
        Return a draft brief that clearly highlights missing or uncertain
        areas using highlight markup. Request clarification from the user.
      </description>
    </step>
  </if_block>

  <if_block condition="no conflicts or missing information">
    <step>
      <action_name>reply</action_name>
      <description>
        Return the completed, verified creative brief ready for internal
        or client review.
      </description>
    </step>
  </if_block>

</plan>
```

**Common mistake: Implicit validation**

Stating an acceptance criterion in the Task without a corresponding validation step in the Plan is a silent failure waiting to happen.

```
# Wrong
Task: "Output MUST be valid JSON."
Plan: [no validation step anywhere]

→ How does the model check validity? It doesn't. It guesses.

# Correct
Task: "Output MUST be valid JSON per JSON Schema Rules."
Plan: Step 5 — validate_json: "Check JSON validity. Verify all required
fields present or TBD. Check numeric types match schema."
```

### 2.3 Rule Blocks (DETAILS)

Rule Blocks are the single source of truth for all syntax, schemas, formatting requirements, mapping logic, and constraints that may change over time. They are what the Task and Plan refer to by name.

**Typical Rule Block types**:
- Formatting and markup rules (HTML tag structure, CSS class conventions)
- Schema definitions (JSON schemas, output HTML templates)
- Mapping rules (how to categorize inputs, how to assign IDs)
- Numbering and sequencing rules (citation counters, ID generation)
- Citation and highlight rules (data attribute structure)
- Regex constraints and validation patterns
- Guardrail rules (scope boundaries, rejection messages)
- Tone and style rules (voice, register, phrasing constraints)

**Characteristics**:
- Contain the actual rule text and syntax — this is the one place this text exists.
- May include minimal examples (one or two concrete illustrations of the rule, kept close to the rule).
- Referenced by name from Task and Plan; never duplicated.
- Names must be stable — they are used as identifiers throughout the system.

**Mental model**: Every time you face a choice between writing the same instruction twice or creating a Rule Block, create the Rule Block.

**Example: Citation Formatting Rules (from Brief-Writing Agent production system)**:

```html
## [START] Citation Formatting Rules

All citations in the generated brief must use structured HTML markup with
embedded metadata for provenance, reasoning, and consistency. Every
factual, stylistic, or procedural statement derived from Supporting Data
or user input must include at least one <mark> + <sup> pair.

### Core Structure

Each citation consists of:
1. A <mark> tag wrapping the cited text (data-type="citation").
2. One or more <sup> tags immediately following — each representing a
   distinct source.

#### General Format

<mark data-type="citation" data-citation-id="1">
  [Referenced text]
</mark>
<sup
  data-citation-id="1"
  data-id="contextItem_103"
  data-type="brand_brain"
  data-title="Account DOs and DON'Ts"
  data-reasoning="Derived from Account DOs and DON'Ts section (contextItem_103)."
>1</sup>

### Metadata Attribute Definitions

| Attribute         | Example              | Description                                      |
|-------------------|----------------------|--------------------------------------------------|
| data-citation-id  | "1"                  | Unique sequential global ID. Never reused.       |
| data-id           | "contextItem_103"    | Source identifier from Supporting Data.          |
| data-type         | "brand_brain"        | Provenance: brand_brain (Supporting Data) or     |
|                   |                      | initial_prompt (user-supplied info).             |
| data-title        | "Account DOs & DON'Ts" | Human-readable title of referenced section.    |
| data-reasoning    | "Derived from..."    | Short (8–20 words) factual justification.        |

### Numbering Rules

- All <sup> numbers must increment continuously across the entire brief.
- Never restart numbering. Each <mark> + <sup> group has a unique id.

### Zero Nesting Rule

Citation <mark> elements MUST NOT contain another <mark>.
If source text contains inner <mark> elements, strip them and keep only
their plain text.

## [END] Citation Formatting Rules
```

**Naming convention**: Use descriptive names in Title Case with "Rules" suffix: `Citation Formatting Rules`, `JSON Schema Rules`, `Brand Guardrail`, `Highlight Formatting Rules`, `ETL Naming Rules`. Keep names stable — they are used as identifiers.

**On examples in Rule Blocks**: Examples belong exclusively in Rule Blocks. Never put examples in Task or Plan. The reason: models generalize from examples (creative behavior), while Rule Blocks are prescriptive (deterministic behavior). An example in the Task block causes the model to invent variations. An example in a Rule Block, adjacent to the rule it illustrates, anchors behavior precisely.

**When to split a Rule Block**: When a single Rule Block exceeds approximately 150 lines, split it by semantic purpose. One block for citation structure, a separate block for citation numbering. Smaller blocks are easier to reference accurately and easier to update.

### 2.4 How Components Interact

The reference-only principle governs all interaction between components. A non-authoritative component invokes a rule by name — it never restates the rule text.

```
# Correct interaction pattern

Task:    "...apply Citation Formatting Rules."
Plan:    "Step 3: Assign citation metadata per Citation Formatting Rules."
Rules:   "## Citation Formatting Rules
          [full rule text lives here and only here]"

# Violation pattern

Task:    "...use <mark data-type='citation'> tags..."
Plan:    "Step 3: Wrap cited text in <mark data-type='citation'>..."
Rules:   "## Citation Formatting Rules
          [full rule text also here]"

→ Same markup defined in three places.
→ Any change requires three edits.
→ Architecture is leaking.
```

**The validation chain**:

```
Task (defines what is valid)
  |
  | defines acceptance criteria
  v
Rule Blocks (define the syntax for what "valid" means)
  |
  | define rules that Plan applies
  v
Execution Plan (validates and acts)
  |-- Preflight checks
  |-- Parse / map input
  |-- Apply Rule Blocks (by reference)
  |-- Validate output against rules
  |-- Return valid response or error
```

**The linking pattern**: At the start of the Execution Plan, include a short preamble listing the governing rules. This makes the dependency explicit and ensures the Plan is always read in the context of its rules.

```
## Execution Plan

This plan operates in accordance with the following rules:
- Brand Guardrail
- Context Source Mapping Rules
- Highlight Formatting Rules
- Citation Formatting Rules
```

---

## Part 3: The Tiered Complexity Model

### 3.1 Overview

Not every agent needs full orthogonality. The framework is a scalability pattern, not a mandatory overhead. The guiding principle is simple: **use the simplest structure that satisfies the requirements. Move up when failure modes appear.**

This creates a natural evolution path:

```
Phase 1: Discover (Tier 1)
  Explore what the agent needs to do.
  Iterate rapidly with Task only.
  Document learnings.
        |
        | failure modes appear: inconsistency, unpredictability
        v
Phase 2: Structure (Tier 2)
  Add light structure as requirements clarify.
  Introduce Task + minimal Plan.
  Identify core rules.
        |
        | rules become implicit, validation blurs
        v
Phase 3: Optimize (Tier 3)
  Formalize rules, enable scaling.
  Full Task + Plan + Rule Blocks.
  Ready for production.
```

Do not skip Phase 1. A Tier 3 prompt cannot be designed without understanding requirements, and requirements are discovered in Phase 1.

### 3.2 Tier 1 — Task Only

**Use when**:
- The agent is creative or exploratory in nature.
- Outputs are low-risk (mistakes have no downstream consequences).
- Fast iteration is more important than consistency.
- The agent is not integrated into a production pipeline.

**Structure**:

```
Objective: [1 sentence]
Acceptance Criteria:
- MUST [constraint 1]
- NEVER [constraint 2]
Output: [format description]
```

**Pros**: Fast to write. Accessible to non-technical teams. Flexible and experimental.

**Cons**: Less predictable, especially on non-reasoning models. Hard to maintain consistency across sessions. Harder to scale to multiple similar agents. High hallucination risk for structured tasks.

**Real examples**: Brainstorming agents, creative writing assistants, exploratory research summarizers, internal ideation tools.

**When to move up to Tier 2**: When outputs become inconsistent, when the model starts inventing behavior beyond the Task, or when validation logic is needed.

### 3.3 Tier 2 — Task + Minimal Plan

**Use when**:
- Light structure is needed but full rule separation is not yet warranted.
- Some validation is required (e.g., "ask for clarification if information is missing").
- Simple, linear workflows with 3–5 steps.
- Rules are few and stable enough to live implicitly in Plan steps.

**Structure**:

```
## Task
Objective: [1 sentence]
Acceptance Criteria:
- MUST [constraint 1]
- MUST [constraint 2]
Output: [format]

## Execution Plan
<plan>
  <step><action_name>parse_input</action_name><description>...</description></step>
  <step><action_name>generate_output</action_name><description>...</description></step>
  <step><action_name>validate_response</action_name><description>...</description></step>
  <if_block condition="missing_info">
    <step><action_name>ask_for_clarification</action_name></step>
  </if_block>
  <if_block condition="complete">
    <step><action_name>reply_final</action_name></step>
  </if_block>
</plan>
```

**Pros**: Balanced clarity. Prevents "wandering" behavior. More predictable than Tier 1. Still readable and easy to write.

**Cons**: Rules can become implicit in Plan step descriptions. Validation logic risks blurring between Task and Plan. May require promotion to Tier 3 as complexity grows.

**Real examples**: Customer support chatbots with light context, FAQ responders, simple content summarizers.

**When to move up to Tier 3**: When rule syntax needs to change independently of the steps, when the output requires a specific schema or markup, when non-reasoning models are involved, or when this agent will be integrated into a product pipeline.

### 3.4 Tier 3 — Full Orthogonal Design

**Use when**:
- Deterministic, reproducible outputs are required.
- Output format requires a specific schema, markup, or ID system (JSON, HTML with data attributes).
- Multi-step workflows with validation at each stage.
- The agent runs on non-reasoning or mini models.
- The agent integrates into production pipelines or front-end rendering systems.
- Rules are expected to change over time and must be updated centrally.

**Structure**:

```
## Task (WHAT)
[Objective + Acceptance Criteria + Output Contract + Rule References]

## Execution Plan (HOW)
<plan>
  [Atomic ordered steps + validation steps + conditional branching]
</plan>

## Rule Blocks (DETAILS)
### Rule Block Name 1
[Rule text, syntax, schema, examples]

### Rule Block Name 2
[Rule text, syntax, schema, examples]
```

**Pros**: Predictable and reproducible. Highly maintainable (one change in one Rule Block). Scalable across many agents that share rule sets. Clear ownership of validation. Production-ready.

**Cons**: Higher upfront design cost. Requires discipline to maintain orthogonality. Slower to prototype for experimental use cases.

**Real-world cost-benefit**:

| Upfront Cost | Long-Term Benefit |
|---|---|
| Time to design Task / Plan / Rules | Edit one place when rules change |
| Discipline to avoid shortcuts | Clear onboarding path for contributors |
| Learning curve for framework | Isolated debugging (check validation step) |
| Schema-first design workflow | Reuse Rule Blocks across agents |

The framework pays back after approximately 2–3 agents or 2–3 rule changes.

### 3.5 Decision Framework: Choosing the Right Tier

Each of the following conditions, if met, is a signal to move up one tier:

```
START
  |
  v
Is the output creative / narrative / low-risk?
  YES ---> Consider Tier 1
  NO  ---> continue
  |
  v
Is a workflow sequence needed (even a simple one)?
  YES ---> Move to at least Tier 2
  NO  ---> Tier 1 may suffice
  |
  v
Does the output require a specific schema, markup, or ID system?
  YES ---> Move to Tier 3
  NO  ---> continue
  |
  v
Does the agent require multi-step validation?
  YES ---> Move to Tier 3
  NO  ---> continue
  |
  v
Will this run on a non-reasoning model (Haiku, GPT-4o mini, etc.)?
  YES ---> Tier 3 is non-negotiable
  NO  ---> continue
  |
  v
Is this a production-grade automated agent in a pipeline?
  YES ---> Tier 3
  NO  ---> Tier 1 or 2 may be sufficient
```

**Real-world Tier assignments**:

| Agent Type | Tier | Rationale |
|---|---|---|
| Brainstorming assistant | 1 | Creative, low-risk, no schema |
| Creative writing helper | 1 | Exploratory, outcome varies by intent |
| Customer support chatbot | 2 | Some validation, no strict schema |
| FAQ responder with context | 2 | Light structure, simple workflow |
| Sales recommendation agent | 2–3 | Depends on whether product catalog schema is required |
| Quoting agent | 3 | JSON output, pricing schema, no estimation allowed |
| Brief-writing agent | 3 | HTML output, citations, highlights, non-reasoning model |
| Data pipeline generator | 3 | Code output, strict validation, naming conventions |
| Compliance checker | 3 | Deterministic, schema-critical, audit trail required |

---

## Part 4: Anti-Patterns

Anti-patterns are recurring structural failures in prompt design. Each one violates orthogonality in a specific way and creates a specific kind of maintenance or behavioral problem. The diagnostic rule is simple:

> "If you see duplication, the architecture is leaking."

All five core anti-patterns are symptoms of duplication or misplaced ownership.

### 4.1 Policy Echo

**Definition**: The Execution Plan repeats rule syntax or rule content from a Rule Block.

**What it looks like**:

```
# Bad — Policy Echo
Rule Block (JSON Schema Rules):
  { "quote_id": "string", "items": [...], "total": "number" }

Plan Step:
  "Validate JSON structure per this schema:
   {quote_id: string, items: [...], total: number}"

→ Schema defined twice. If the schema changes, both places must change.
→ They will drift apart.
```

```
# Correct
Rule Block (JSON Schema Rules):
  { "quote_id": "string", "items": [...], "total": "number" }

Plan Step:
  "Validate JSON structure per JSON Schema Rules."
```

**Why it happens**: Engineers add the schema inline to the Plan "so it's easy to find," creating a shortcut that becomes technical debt.

**Impact**: High. Every schema change requires editing two places. Validation logic drifts from the rule definition. Testing Rule Blocks independently becomes impossible.

**Fix**: Extract all syntax to a named Rule Block. The Plan step references the block by name only.

### 4.2 Mixed Intent

**Definition**: The Task block contains procedural steps (HOW) rather than purely declarative outcomes (WHAT).

**What it looks like**:

```
# Bad — Mixed Intent
Task:
  "Objective: Generate quotes.
   1. Parse the request from the user.
   2. Look up pricing in the database.
   3. Assemble the JSON response."

→ Steps are implementation detail — that is the Plan's job.
→ Acceptance criteria are now buried among procedure.
→ When the procedure changes, the Task must be rewritten.
```

```
# Correct
Task:
  "Objective: Generate precise, compliant quotes from exact specifications.
   MUST follow Pricing Rules for all costs.
   MUST insert 'TBD' for any missing required input.
   MUST output valid JSON per JSON Schema Rules.
   MUST NOT infer quantities, timelines, or discounts."

Plan: [the numbered steps go here]
```

**Why it happens**: Early drafts often read as prose instructions: "do this, then that." The procedural language creeps into the Task before components are separated.

**Impact**: High. Acceptance criteria get buried and hard to audit. Task becomes a mixed document that is unclear to both the model and the engineer.

**Fix**: Move all steps (anything with sequential or procedural language) to the Plan. The Task describes what success looks like, not the path to get there.

### 4.3 Dual Ownership

**Definition**: Both Task and Plan define or enforce the same scope, creating two overlapping authorities.

**What it looks like**:

```
# Bad — Dual Ownership
Task:    "Output MUST be valid JSON."
Plan:    "Validate JSON structure and types."
Rules:   "JSON Schema: {quote_id: string, items: [...], total: number}"

→ Who owns JSON validity? Task? Plan? Both are asserting it.
→ If they disagree (in a future edit), which one wins?
```

```
# Correct
Task:    "Output MUST be valid JSON per JSON Schema Rules."
         (Task defines the contract — references the rule)
Plan:    "Validate JSON structure and types per JSON Schema Rules."
         (Plan enforces the contract — also references the rule)
Rules:   "JSON Schema Rules: {quote_id: string, items: [...], total: number}"
         (Rules define the syntax — the single authoritative source)
```

The resolution is clear: **Task defines (contract), Plan enforces (validation), Rule Block defines syntax.** All three reference the same Rule Block by name; none duplicate the content.

**Impact**: High. Inconsistent enforcement when Task and Plan descriptions diverge. Hard to trace requirements back to their source. Responsibility is ambiguous.

### 4.4 Schema Leakage

**Definition**: The output schema or markup syntax is defined or restated in the Plan or Task rather than existing exclusively in a Rule Block.

**What it looks like**:

```
# Bad — Schema Leakage
Plan:
  "Step 4: Generate JSON with fields: quote_id, items array, total."

Rule Block (JSON Schema Rules):
  "{ quote_id: string, items: [...], total: number }"

→ Same structure defined twice.
→ Single source of truth violated.
```

```
# Correct
Plan:
  "Step 4: Generate JSON per JSON Schema Rules."

Rule Block (JSON Schema Rules):
  "{ quote_id: string, items: [...], total: number }"
```

**Why it happens**: Engineers add inline reminders to help the model "remember" the schema while generating. This is unnecessary with proper Rule Block design and creates debt.

**Impact**: High. Schema updates require editing multiple places. Easy to get out of sync. Violates the single source of truth principle.

### 4.5 Frontend Language

**Definition**: System prompt contains UI/visual language that belongs in the frontend, not the prompt.

**What it looks like**:

```
# Bad — Frontend Language
Task:  "When hovering over a citation number, show the citation tooltip."
Plan:  "Color the gaps red and the citations yellow."
Rules: "<mark style='background-color: yellow;'>cited text</mark>"

→ Frontend responsibilities mixed with prompt logic.
→ If the UI team changes the color scheme, the prompt must be rewritten.
→ CSS belongs in stylesheets, not in system prompts.
```

```
# Correct
Rules:  "<mark class='highlight' data-type='citation'>cited text</mark>"

→ Semantic markup only — class and data attributes convey meaning.
→ Frontend CSS controls all visual appearance.
→ Prompt never changes when UI design evolves.
```

**Why it happens**: Prompts are sometimes written by people who also work on the UI, and they conflate the two concerns.

**Impact**: Medium-High. Frontend and backend responsibilities are tightly coupled. UI changes require prompt changes. CSS and styling belong in the frontend.

### 4.6 Detection and Recovery

**Detection checklist** — run this before shipping any prompt:

- [ ] Does any content appear in two or more components?
- [ ] Does the Task contain the words "first", "then", "next", "step", or "parse"?
- [ ] Does the Plan contain schema definitions, markup syntax, or regex?
- [ ] Do both Task and Plan define the same scope condition?
- [ ] Are there HTML/CSS style attributes in the prompt?
- [ ] Are there examples in the Task or Plan (not in Rule Blocks)?

**Recovery process**:

1. **Map content**: Create a table of what exists in Task, Plan, and each Rule Block. Identify every piece of content that appears in more than one component.

2. **Identify authority**: For each duplicated item, choose one authoritative home using the Placement Router.

   | Content Type | Authoritative Home |
   |---|---|
   | Acceptance criteria | Task |
   | Schema / syntax / regex | Rule Block |
   | Procedural steps | Plan |
   | Validation logic | Plan |
   | Examples | Rule Block |

3. **Extract and consolidate**: Move the content to its authoritative home. Remove it from all other locations.

4. **Reference only**: In the non-authoritative locations, replace the content with a named reference. "per JSON Schema Rules" instead of the schema itself.

5. **Validate**: Run the Placement Router on every line of the revised prompt. If every question has a clean answer, orthogonality is restored.

### 4.7 When to Break the Rules

There is one valid exception to the no-duplication principle. It is narrow, controlled, and temporary.

If a non-reasoning model (Claude Haiku, GPT-4o mini) consistently violates a single critical constraint despite a well-designed Rule Block, one may add a one-line reminder in the Task AND a single validation line in the Plan. This is controlled technical debt, used as a stabilization technique.

**Rules for acceptable duplication**:
- Keep it minimal: one line in each location, not a paragraph.
- Keep it verbatim: both copies must be identical — not paraphrased.
- Track it explicitly: note in comments that this duplication is intentional and temporary.
- Remove it: once the model behavior stabilizes or the model is updated, remove the duplication and rely solely on the Rule Block.

```
# Controlled duplication example

Task (one-line reminder):
  "Markup is only allowed inside ACTION.value fields — NEVER outside."

Plan (single validation line):
  "Verify markup scope: confirm no markup exists outside ACTION.value fields."

Rule Block (full definition):
  "Markup Scope Rules:
   <mark> and <sup> tags are only permitted inside the value field of
   ACTION objects. No markup may appear in top-level text or in section
   headers."
```

This is the only sanctioned form of duplication in the framework.

---

## Part 5: Applied Examples

### 5.1 The Brief-Writing Agent (Flagship Tier 3 Example)

The Brief-Writing Agent is the most comprehensive real-world implementation of this framework. It generates creative briefs for brand accounts, requiring deterministic HTML output, multi-step validation, semantic citation markup, gap highlighting, and brand scope enforcement.

**Why Tier 3**:
1. Deterministic HTML output required — clients need predictable, structurally consistent briefs.
2. Multi-step validation — citations, highlights, and brand guardrails must all pass validation before output.
3. Non-reasoning model deployment — the agent runs on a compact fast model that cannot infer implicit rules.
4. Frontend integration — the HTML output is rendered by a React application that relies on specific data attributes for tooltip and highlight behavior.
5. Frequently-updated rules — brand guidelines change, citation formats evolve, mapping rules expand.

**Full architecture**:

```
Task Block: Defines the brief generation contract
  - Acceptance criteria: MUST/NEVER statements
  - Output contract: HTML with semantic markup
  - References: Brand Guardrail, Context Source Mapping Rules,
                Citation Formatting Rules, Highlight Formatting Rules

Execution Plan: 9 steps + 2 conditional branches
  - parse_user_input
  - interpret_supporting_data
  - identify_request_type_and_brief_pairs
  - map_context_citations
  - generate_brief
  - validate_brief_consistency
  - validate_tone_and_style
  - crosscheck_highlight_citation_links
  - verify_rule_compliance
  - if_block: missing information → reply with draft + highlights
  - if_block: no conflicts → reply with final brief

Rule Blocks:
  - Brand Guardrail (scope restriction, fail-fast rejection)
  - Context Source Mapping Rules (header keyword → citation category)
  - Citation Formatting Rules (HTML structure, data attributes, numbering)
  - Highlight Formatting Rules (gap marks, default marks, prohibited syntax)
```

**Real-world output sample**:

The agent produces HTML that the frontend renders as interactive content:

```html
<p>
  All deliverables must adhere to
  <mark data-type="citation" data-citation-id="3">
    Brand Guidelines
  </mark>
  <sup
    data-citation-id="3"
    data-id="contextItem_201"
    data-type="brand_brain"
    data-title="Brand Guidelines"
    data-reasoning="Extracted from Brand Guidelines section (contextItem_201)."
  >3</sup>
  as established in previous campaigns.
</p>

<p>
  Timeline: <mark class="highlight" data-type="gap">TBD</mark>
</p>
```

The frontend receives this HTML and:
- Renders citation highlights as interactive yellow markers.
- Renders gap highlights as red/pink placeholders.
- Shows citation tooltips on `<sup>` hover — all controlled by CSS, never by the prompt.

### 5.2 Guardrail Patterns

A **Guardrail** is a Rule Block that restricts the agent's scope to a specific brand, account, or context. It prevents the agent from processing out-of-scope requests.

**Where guardrails belong**: Always the first step in the Execution Plan. Never process content before validating scope.

**The hard rejection principle**: Guardrails always reject. Never use a soft fallback ("I can try my best for..."). Hard rejection ("Sorry, I can only assist with X") is more honest, more efficient, and prevents mediocre out-of-scope outputs from reaching users.

**Standard guardrail Rule Block**:

```
## [START] Brand Guardrail

You are an AI brief-writer strictly for the account: {{company_name}}.

Before taking any other action:
1. Analyze the user's request.
2. If the request is about another brand, project, or product not related
   to {{company_name}}, do not proceed further.
3. Respond: "Sorry, I can only assist with requests related to
   {{company_name}}. Please provide an account-specific project or
   brief request."
4. Do not use any general or prior LLM knowledge about other brands.
5. Only if the request is {{company_name}}-specific, continue.

## [END] Brand Guardrail
```

**Execution Plan step for the guardrail**:

```xml
<step>
  <action_name>apply_brand_guardrail</action_name>
  <description>
    Verify the request is for {{company_name}}. If not, reject with
    the standard rejection message from Brand Guardrail and stop all
    further processing.
  </description>
</step>
```

**Three guardrail patterns**:

| Pattern | Use When | Scope |
|---|---|---|
| Single-brand guardrail | Agent serves exactly one client | One company name, hard reject all others |
| Multi-brand with scope | Agent serves several brands but limited to specific topics | List of brands + list of allowed topics, reject combinations outside both |
| No guardrail | Agent is general-purpose or public-facing | None (not recommended for brand-specific agents) |

**Guardrail test cases**: Every guardrail must pass all five scenarios:

1. In-scope request → process normally.
2. Out-of-scope request (different brand) → hard rejection.
3. Multi-brand request ("Can you do this for Brand A and Brand B?") → rejection.
4. Unrelated topic (HR, finance, unrelated product) → rejection.
5. Ambiguous but clearly scoped ("help me with the Booking.com campaign") → process normally.

### 5.3 Citation and Highlight Patterns

The semantic markup system used in the Brief-Writing Agent applies broadly to any agent that produces cited or reviewed content. The underlying principle is the same for all cases.

**The semantic markup principle**: Markup is structural, CSS is visual. Agents output data attributes that convey meaning. Frontend CSS controls all colors, borders, and hover states.

```
Agent outputs: <mark class="highlight" data-type="gap">TBD</mark>
Frontend CSS:  mark[data-type="gap"] { background-color: #f8d7da; }

If the design team changes the gap color from red to orange:
  → Edit CSS only.
  → The system prompt is unchanged.
```

**Gap highlights**: Used when information is missing or incomplete.

```html
<!-- Missing deadline -->
<mark class="highlight" data-type="gap">GAP</mark>

<!-- Unknown timeline -->
<mark class="highlight" data-type="gap">TBD</mark>

<!-- Missing volume information -->
<mark class="highlight" data-type="gap">No data provided</mark>
```

**Default highlights**: Used for information that is uncertain or needs human verification.

```html
<!-- Recommended but not confirmed -->
<mark class="highlight">Need to double check with client</mark>

<!-- Estimated but not specified -->
<mark class="highlight">Estimated budget range</mark>
```

**Citation markup** (full structure with metadata):

```html
<!-- Single-source citation -->
<mark data-type="citation" data-citation-id="5">
  Creative direction follows UEFA brand standards.
</mark>
<sup
  data-citation-id="5"
  data-id="contextItem_302"
  data-type="brand_brain"
  data-title="Creative Standards"
  data-reasoning="Derived from Creative Standards section (contextItem_302)."
>5</sup>

<!-- Multi-source citation (same content, two sources) -->
<mark data-type="citation" data-citation-id="6">
  Campaign tone is energetic and inclusive.
</mark>
<sup
  data-citation-id="6"
  data-id="contextItem_101"
  data-type="brand_brain"
  data-title="Workflow Preferences"
  data-reasoning="Mentioned in Customer Tone of Voice section (id: 101)."
>6</sup>
<sup
  data-citation-id="6"
  data-id="initial_prompt"
  data-type="initial_prompt"
  data-reasoning="Reinforced in user's original request description."
>7</sup>
```

**Zero nesting rule**: Citation `<mark>` elements must never contain another `<mark>`. If source text contains inner marks, strip the inner marks and keep only their plain text.

**Common citation mistakes**:

```html
<!-- Wrong: nested marks -->
<mark data-type="citation">
  <mark class="highlight" data-type="gap">TBD</mark>
</mark>

<!-- Correct: flat, one type per mark -->
<mark class="highlight" data-type="gap">TBD</mark>

<!-- Wrong: non-sequential numbering -->
<sup data-citation-id="103">103</sup>

<!-- Correct: always sequential from 1 -->
<sup data-citation-id="3">3</sup>
```

### 5.4 Real-World Prompt Evolution (Before vs After)

This section documents the refactor of the Brief-Writing Agent system prompt from a mixed, redundant design to a clean orthogonal structure. The overlap problem that triggered the refactor:

| Function | In Task | Also in Plan | Problem |
|---|---|---|---|
| Input parsing | "You will receive from the user..." | `<action_name>parse_user_input` | Defined twice, different tone |
| Request type identification | "Identify the Customer Request Type..." | `<action_name>identify_request_type` | Repeated logic |
| Placeholder handling | "Always use TBD for missing values..." | Repeated in execution description | Unnecessary duplication |
| Highlight/Citation rules | Explicitly mentioned multiple times | Re-mentioned in `<generate_brief>` | Redundant, should be referenced once |
| Validation behavior | "If missing, insert placeholder" | "If missing, ask for clarification" | Overlapping but slightly contradictory |
| Output structure | "Write using HTML tags..." | "Follow Output structure defined below" | Same directive in two places |

**Before (mixed Task)**:

```
Task: "Always use <mark class='highlight' data-type='gap'>TBD</mark>
       for missing fields; parse inputs from the user; then generate
       the brief; then check numbering and citation IDs..."
Plan: [Repeats highlight/citation syntax AND procedural steps]
```

The model was receiving instructions for WHAT, HOW, and the DETAILS of markup syntax all mixed together. Maintenance required searching the entire prompt for every change.

**After (orthogonal Task)**:

```
## Task Overview

Objective: Generate a complete, internally consistent creative brief
for {{company_name}}.

Acceptance Criteria:
1. Output HTML only; use only semantic tags: <h1>-<h3>, <p>, <ul>,
   <li>, <mark>, <sup>, <br>, <hr>.
2. Follow Citation Formatting Rules for all Supporting Data references.
3. Follow Highlight Formatting Rules for all gaps and uncertainties.
4. Follow Context Source Mapping Rules for citation categorization.
5. Follow Brand Guardrail before any other processing.
6. Never fabricate information; never estimate unknown values.
7. Never include a trailing Citations section.

Dependencies:
- Brand Guardrail
- Context Source Mapping Rules
- Highlight Formatting Rules
- Citation Formatting Rules
```

**After (orthogonal Plan)**:

```
## Execution Plan

This plan operates in accordance with the governing rules listed in Task.

<plan>
  <step><action_name>parse_user_input</action_name>
    <description>Extract customer request, supporting data subsections,
    and attached files.</description></step>

  <step><action_name>identify_request_type_and_brief_pairs</action_name>
    <description>Detect the project type, map it to known brief pairs,
    and select relevant context items.</description></step>

  <step><action_name>map_context_citations</action_name>
    <description>Assign global sequential citation numbering and metadata
    per Citation Formatting Rules.</description></step>

  <step><action_name>generate_brief</action_name>
    <description>Generate the full HTML brief applying structure,
    highlights, and citations as defined in Task and Rules.</description></step>

  <step><action_name>validate_brief_consistency</action_name>
    <description>Ensure logical coherence, source traceability, and no
    unhighlighted gaps remain.</description></step>
</plan>
```

**Benefits comparison**:

| Before | After |
|---|---|
| Verbose, slightly repetitive | Clean, modular, purpose-driven |
| Rules duplicated across Task and Plan | Rules centralized and referenced |
| Model reasoning sometimes jumps between blocks | Deterministic execution flow |
| Hard to maintain when formatting logic changes | One place per logic type |
| LLM confused between WHAT and HOW | Clean separation of responsibilities |

### 5.5 Agent Patterns by Type

Three fully-worked agent patterns illustrate how the framework applies across different output types.

**Sales Agent (Tier 2–3)**

| Aspect | Detail |
|---|---|
| Purpose | Product recommendations without fabrication |
| Output | Text (paragraphs + lists) |
| Tier | 2–3 depending on whether product catalog schema is required |
| Rule Blocks | Product Matching Rules, Sales Tone Rules, Output Format Rules |

Key Rule Block excerpts:
```
# Product Matching Rules
- Map needs to product categories using official catalog only.
- Never infer price, availability, or features.
- If details unknown → mark TBD.

# Sales Tone Rules
- Helpful: address customer needs directly.
- Consultative: explore options, do not push one choice.
- Never pushy: no urgency or scarcity language.
- No jargon: use the customer's language.

# Output Format Rules
Section structure:
  Your Needs / [one paragraph summary]
  Recommended Options / [Product: why this fits]
  Why These Fit / [one paragraph]
  Questions for You / [clarifying questions if any]
```

Counterpoint: For fast-moving, conversational sales tasks, a looser Tier 1 model may outperform a rigid orthogonal design. Orthogonal complexity is only justified when governance, consistency, or scale requires it.

---

**Quoting Agent (Tier 3)**

| Aspect | Detail |
|---|---|
| Purpose | Precise quotes without estimation |
| Output | JSON only |
| Tier | 3 (high determinism required) |
| Rule Blocks | Pricing Rules, Quantity/Unit Rules, JSON Schema Rules |

Key Rule Block excerpts:
```json
// JSON Schema Rules
{
  "quote_id": { "type": "string", "required": true },
  "items": {
    "type": "array",
    "items": {
      "sku": { "type": "string", "required": true },
      "quantity": { "type": "number", "required": true },
      "unit_price": { "type": "number", "required": true },
      "line_total": { "type": "number", "required": true }
    }
  },
  "subtotal": { "type": "number", "required": true },
  "discount": { "type": "number or null", "required": false },
  "total": { "type": "number", "required": true }
}
```

Counterpoint: Excessive structural separation may slow iteration when pricing rules update frequently. Embedding the schema inline temporarily can speed prototyping — but this is technical debt that must be resolved before production.

---

**Python ETL Agent (Tier 3)**

| Aspect | Detail |
|---|---|
| Purpose | Production-grade Python for data pipelines |
| Output | Single Python code block |
| Tier | 3 (strict validation of code structure) |
| Rule Blocks | Python Coding Rules, ETL Naming Rules, Error-Handling Rules |

Key Rule Block excerpts:
```
# ETL Naming Rules
load_*  : Data loading functions  (e.g., load_csv, load_database)
transform_* : Transformation functions (e.g., transform_data, clean_nulls)
write_* : Output functions         (e.g., write_csv, write_database)

# Error-Handling Rules — Guard-first, log-and-raise pattern:

def load_file(filepath):
    if not os.path.exists(filepath):
        logging.error(f"File not found: {filepath}")
        raise FileNotFoundError(filepath)
    try:
        data = read(filepath)
        return data
    except Exception as e:
        logging.error(f"Failed to load {filepath}: {e}")
        raise
```

Counterpoint: For exploratory data analysis (EDA), rigid structure adds friction. Tier 1–2 is more productive when the user wants quick experiments rather than production pipelines.

---

**Pattern selection guide**:

| Agent Type | Tier | Output | Key Rule Blocks | Primary Risk |
|---|---|---|---|---|
| Sales | 2–3 | Text | Products, Tone, Format | Hallucinated specs |
| Quoting | 3 | JSON | Pricing, Schema, Units | Wrong pricing, missing fields |
| Python ETL | 3 | Code | Coding, Naming, Error-Handling | Unsafe code, hallucinated libraries |
| Brief-writing | 3 | HTML | Guardrail, Citations, Highlights, Mapping | Wrong citations, missing gaps, wrong brand |

---

## Part 6: Designing for Non-Reasoning Models

### 6.1 Why This Matters

**Non-reasoning models** (Claude Haiku, smaller fine-tuned models, GPT-4o mini) are optimized for speed and cost. They are excellent at executing explicit instructions. They are not equipped to infer intent from ambiguous or implicit prompts. If a rule is implied rather than stated, a non-reasoning model will guess — and guess wrong at a predictable rate.

**The capability distinction**:

| Model Type | Can infer rules from examples | Handles ambiguous instructions | "Figures out" the right approach |
|---|---|---|---|
| Reasoning models (Claude 3 Opus, o1) | Yes | Yes, often | Sometimes |
| Non-reasoning models (Haiku, GPT-4o mini) | Rarely | No | No — needs explicit guidance |

**Empirical evidence** from Brief-Writing Agent deployments:

| Tier | Error Rate on Non-Reasoning Model |
|---|---|
| Tier 1 (Task only) | ~40% hallucination / structural failure rate |
| Tier 2 (Task + Plan) | ~15% error rate (missing validation steps) |
| Tier 3 (Task + Plan + Rule Blocks) | <2% error rate |

**The key insight**: A Tier 3 prompt on Claude Haiku outperforms a Tier 1 prompt on Claude 3 Opus for structured tasks. Structure is more important than raw model capability.

There is a common belief that better models require less prompt engineering. The evidence inverts this: better models can compensate for poor prompts, but that compensation wastes expensive capability on inference that should be handled by design. Non-reasoning models simply cannot compensate — they need explicit guidance or they fail.

### 6.2 Design Principles

**Principle 1: Explicit over implicit**

Every rule that a reasoning model can infer must be stated explicitly for a non-reasoning model.

```
# Implicit (fails with non-reasoning)
Task: "Generate helpful customer responses."

→ Model must infer: what is "helpful"? what tone? what format? what scope?
→ Non-reasoning model guesses wrong.

# Explicit (works with non-reasoning)
Task: "Generate customer responses that are polite, concise, and address
       one issue per response."

Rule Block — Response Format Rules:
  "Start with a greeting.
   Address the specific issue raised (one issue only).
   Offer one resolution option.
   End with a contact invitation.
   Maximum 3 sentences total."
```

**Principle 2: Narrow, atomic procedural steps**

Each Plan step should be small enough to be a Python function. Vague steps cause models to invent sub-steps, and the invented sub-steps are often wrong.

```
# Vague step (non-reasoning models invent behavior)
<step>
  <action_name>process_data</action_name>
  <description>Process the user data.</description>
</step>

# Narrow, atomic steps (non-reasoning models execute precisely)
<step>
  <action_name>identify_issue_type</action_name>
  <description>Classify user issue as one of: billing, technical,
  shipping, other. If unclear, ask for clarification.</description>
</step>

<step>
  <action_name>select_response_template</action_name>
  <description>Choose template from Response Template Rules matching
  the classified issue type.</description>
</step>

<step>
  <action_name>fill_template</action_name>
  <description>Fill template with specific details from user message.
  Do not deviate from template structure.</description>
</step>
```

**Principle 3: Schema-first output**

Define the exact output structure in a Rule Block before writing the Plan. Non-reasoning models perform better with explicit schemas than with structural descriptions.

**Principle 4: Enumerated choices**

Replace open-ended instructions with closed option lists.

```
# Open-ended (fails with non-reasoning)
"Choose an appropriate action based on context."

# Enumerated (works with non-reasoning)
"Choose one of the following:
 1. Answer the question directly.
 2. Ask for clarification (when information is missing).
 3. Escalate to a human agent (when question is out of scope).
Each choice maps to a specific action defined in Response Routing Rules."
```

### 6.3 Four Design Patterns

**Pattern 1: Hyper-explicit Rule Blocks**

Instead of a brief directive, provide a numbered specification:

```
# Normal Rule Block
Output Format: "Brief intro + bullet list"

# Non-Reasoning Rule Block (hyper-explicit)
Output Format Rules:
1. Start with 1–2 sentence intro summarizing the issue concisely.
2. Follow with a bulleted list of items using "- " prefix.
3. Each bullet is 1 sentence maximum.
4. No sub-bullets.
5. No additional text after the final bullet.
6. Use only plain text in the list — no bold, italic, or markup.
```

**Pattern 2: Narrow procedural steps**

(Demonstrated in Principle 2 above — use the issue-type classification example as the model.)

**Pattern 3: Schema-first output**

```json
// Define this in a Rule Block before writing any Plan steps.
// JSON Response Schema Rules:
{
  "issue_type": "string (billing | technical | shipping | other)",
  "response": "string (response text, max 150 words)",
  "followup_question": "string or null (optional clarifying question)"
}
```

**Pattern 4: Closed-loop option sets**

(Demonstrated in Principle 4 above — use the numbered choices example as the model.)

### 6.4 Non-Reasoning Readiness Checklist

Before deploying to a non-reasoning model, answer all questions. Any "no" except the last indicates the prompt is not ready.

- [ ] Are all rules explicit, not inferred?
- [ ] Can each Plan step be executed mechanically, like a function?
- [ ] Are all outputs schema-defined in a Rule Block?
- [ ] Are examples placed in Rule Blocks only (not Task or Plan)?
- [ ] Could a non-technical person follow the Plan step by step?
- [ ] Is "figure out what is appropriate" absent from all steps?

---

## Part 7: DSL and Programmatic Approaches

### 7.1 The Three Prompt Layers

System prompts exist in an architecture with three distinct layers, each with different stability and caching characteristics:

| Layer | Content | Stability | Cache Impact |
|---|---|---|---|
| **System Prompt** | Rules, invariants, output schema | Static | High — prefix must be stable |
| **Few-Shot Examples** | Input/output pairs that teach behavior | Semi-static | Medium — fewer is more cacheable |
| **User Prompt** | Dynamic task data, user request | Dynamic | Always new — no caching |

**The golden rule**:
- Static logic goes in the system prompt.
- Dynamic procedure and task-specific data go in the user prompt.
- Examples teach mapping (input → output style), not output format. Output format is enforced by the system prompt.

**KV cache implications**: Prompt caching activates after approximately 1,024 tokens of identical prefix. If the system prompt changes between calls (e.g., timestamps injected, account names swapped inline), caching breaks. Keep the static prefix of the system prompt stable. Inject dynamic variables (account name, current date, user-specific data) in the user prompt.

```
# Cache-efficient design
System prompt (stable):
  [Full Task + Plan + Rule Blocks — identical every call]

User prompt (dynamic):
  account: {{company_name}}
  date: {{current_date}}
  request: [user's request]
  supporting_data: [injected brand data]

→ System prompt cached after first call.
→ Token cost reduced significantly for high-volume agents.
```

### 7.2 Format Options and Trade-offs

There are three ways to write system prompts, each with different trade-offs between readability, token efficiency, and expressiveness.

**Option 1: Full Natural Markdown**

Long-form, natural language prose with Markdown formatting.

```
Strengths:
- High redundancy improves model reliability
- Stable tone preserved through natural phrasing
- Strong behavioral reinforcement
- Low misinterpretation risk for nuanced instructions
- Easy to read and debug

Weaknesses:
- Token-heavy (higher API costs at volume)
- Repetitive rules across sections
- Cache-inefficient if not carefully structured
- Hard to maintain at scale

Best for: Early prototyping, sensitive tone requirements, human-facing agents
```

**Option 2: Ultra-Condensed DSL (KeyTokenDSL)**

Heavily abbreviated tokens mapped to a dictionary at the top of the prompt.

```
Strengths:
- 40–70% token reduction
- Highly cache-efficient (dense, stable prefix)
- Modular and scalable across agent variants

Weaknesses:
- Requires a dictionary block the model must decode
- Risk of "lossy compression" — dropping nuance that matters
- Produces blunt outputs if tone/politeness not preserved as flags

Best for: Multi-agent internal pipelines, structured transformation agents
```

**Option 3: Middle-Term Procedural DSL (Recommended for production)**

Structured but natural-language steps, using a consistent syntax like STEP/DESC or YAML-style blocks.

```
STEP:generate_brief
DESC:
  - Use request + supporting_data
  - Apply brand_style rules
  - Insert TBD when missing
  - Preserve all formatting
```

```
Strengths:
- ~30–40% token reduction vs. full natural language
- Still natural enough for model interpretation without a dictionary
- Retains nuance and tone cues
- Retains politeness and conditional logic
- High interpretability for engineers
- Cache-friendly

Best for: Standard production agents, single-agent user-facing systems
```

**Decision table**:

| Context | Best Format |
|---|---|
| Single-agent, user-facing output | Middle-Term DSL |
| Multi-agent internal pipeline | KeyTokenDSL + dictionary |
| Rapid prototyping or exploration | Plain Markdown |
| Highly constrained structured transformation | Ultra DSL |
| Tone-sensitive marketing or creative outputs | Markdown or Middle-Term |

### 7.3 DSL Design Principles

**Rule 1: No invented abbreviations without a dictionary**

```
# Bad — invented abbreviation
SENT=short

# Safe — dictionary-backed token
B0:DICT
SENT → "Sentence length must be short (max 15 words)"
```

**Rule 2: Preserve behavior as named flags**

Rather than compressing rich instructions into unrecoverable tokens, use named flags with dictionary definitions:

```
B0:DICT
TBD     → "Insert this placeholder when information is missing or unknown"
VERBATIM → "Copy input text or URLs exactly without modification"
BAN:BUDGET → "Never include, infer, or reference budget or pricing information"
POLITE  → "Request clarifications courteously; acknowledge the user"
CONFLICTING → "Explicitly mark when information from two sources contradicts"
```

**Rule 3: Make DSL familiar**

LLMs are trained on YAML, JSON, config files, and pseudocode. DSL syntax that resembles these formats is more reliably interpreted than invented syntax.

```
# Less familiar (custom syntax)
##REQ##--a,b,c--##END##

# More familiar (YAML-like)
REQ:
  - a
  - b
  - c
```

**Lossless vs. lossy compression**:

| Lossless (preserve) | Lossy (drops critical signal) |
|---|---|
| Style flags (TONE=friendly) | Politeness cues |
| Structure flags (STRUCT=sections+bullets) | Tone reinforcement language |
| Conflict markers (CONFLICTING) | Conflict escalation rules |
| Deadline logic (TBD, MISSING) | Formatting preservation |
| Budget bans (BAN:BUDGET) | Edge-case clarification instructions |
| Verbatim rules (VERBATIM) | Output structure constraints |

Never compress tone without preserving it through flags. Lossy DSL produces blunt, inconsistent, and potentially misaligned outputs.

**Few-shot example compression**: Keep customer input verbatim (teaches the model tone, style, and phrasing). Compress the output (internal brief) into DSL structure, since the system prompt already enforces the final output format.

```
PAIR_EXAMPLE

INPUT (Customer Request):
"[verbatim customer text — full natural language]"

OUTPUT (Internal Brief, compressed):
BRF:
  ProblemOverview: "UEFA Euros 2024 bumpers; brand awareness"
  Audience: "European football fans"
  CreativeGuidance:
    - playful, energetic branding
    - reference deck=VERBATIM:url

SCP:
  DELIV:
    - 3 explorations (motion studies)
    - long=10s, short=2s versions
  TL: IR1=2023-12-05
  OOS: [no final animations, copy excluded]
```

This achieves ~40% token reduction per example pair while preserving the tone signal from the customer input.

### 7.4 When DSL Makes Sense

DSL is worth the added complexity in these contexts:

- **Multi-agent pipelines**: DSL tokens are consistent across agents. Rule changes propagate through the dictionary.
- **Internal logic agents**: No user-facing tone required. Efficiency matters more than warmth.
- **Structured transformations**: Input → Output mappings that are primarily structural, not creative.
- **High-volume, cost-sensitive deployments**: Token reduction compounds at scale.

DSL is not appropriate for:
- **Early prototyping**: Plain Markdown is faster to write and easier to debug.
- **Tone-sensitive user-facing agents**: Compression risks flattening the nuance that makes the output feel correct.
- **Small or exploratory agents**: The overhead of defining a dictionary is not justified.

### 7.5 Current Status and Future Directions

The DSL and KeyTokenDSL approaches documented here are **research-phase**, not production-ready as standalone systems. The middle-term procedural DSL format (STEP/DESC) is the closest to production use.

**Critical prerequisite**: A DSL approach assumes a Tier 3 orthogonal framework. Without the Task/Plan/Rule Block separation, DSL becomes harder because there are more structural variations to handle. Orthogonal framework first, then DSL compression.

**Future directions under active exploration**:
1. **Rule libraries**: Pre-built, version-controlled Rule Blocks reusable across agents.
2. **Agent composition**: Agents inherit base configurations and override specific rules.
3. **Model variants**: Same agent definition compiled into different tiers for different models.
4. **Tooling**: Parser, validator, and generator for DSL prompts.
5. **Integration layer**: Direct connection from DSL tools to model APIs.

For current production work: use the Tier 3 orthogonal framework with plain or middle-term structured Markdown.

---

## Part 8: Evaluation and Iteration

### 8.1 Quality Gates

Before shipping any prompt to production, it must pass six quality gates:

1. **Orthogonality**: Does every line pass the Placement Router? Does any content appear in more than one component?

2. **Testability**: Is the prompt testable in isolation? Can each Rule Block be validated independently?

3. **Graceful error handling**: Does the Execution Plan handle missing inputs, out-of-scope requests, and invalid data gracefully?

4. **Convention consistency**: Does the prompt follow project naming conventions and reference patterns?

5. **Scalability**: Will this design handle 10x current load without structural changes?

6. **Maintainability**: Can a new team member understand and extend the prompt by following the Task → Plan → Rule Blocks reading order?

All six gates must pass. A "no" on any gate requires revision before shipping.

### 8.2 The Orthogonality Checklist

Run this checklist on every prompt before shipping. All answers should be "yes" for orthogonality to hold.

**Task checklist**:
- [ ] Does it define acceptance criteria (MUST/NEVER statements)?
- [ ] Does it specify the output format as a contract?
- [ ] Does it reference Rule Blocks by name only (no rule text inline)?
- [ ] Does it contain NO steps, procedural language, or sequencing words?

**Execution Plan checklist**:
- [ ] Are all steps ordered and atomic (each step is a single action)?
- [ ] Does it apply Rule Blocks by reference (names only, no inline rule text)?
- [ ] Does it contain explicit validation logic?
- [ ] Does it contain NO rule definitions, schema text, or formatting rules?

**Rule Blocks checklist**:
- [ ] Do they define syntax and formatting rules as the single source of truth?
- [ ] Do they contain examples (if any) only in minimal form, adjacent to the rule?
- [ ] Are they referenced (never duplicated) in Task and Plan?
- [ ] Are their names stable (not changed with every edit)?

**Cross-component checklist**:
- [ ] Is any content duplicated between components?
- [ ] Is ownership clear for every validation (who checks what)?
- [ ] Can the Placement Router be applied to every line without ambiguity?
- [ ] Are guardrails placed as the first step in the Plan?

### 8.3 Testing Prompt Quality

**Structural testing**: Automated validation of output structure.

For agents that produce JSON, write a schema validator that parses the output and confirms field presence, types, and required values. For HTML agents, run an HTML parser and verify required tags and data attributes are present. This catches structural failures programmatically.

**Golden example testing**: Maintain a small set (5–10) of known-good input/output pairs for each Rule Block. These "golden examples" serve two purposes:
1. During development: confirm that the Rule Block produces the expected output.
2. After changes: regression test — rerun golden examples after any Rule Block change to verify no behavioral drift.

**Regression testing**: When changing a Rule Block, run the full golden example set. Any output that changes should be reviewed. If the change was intentional (rule update), update the golden examples. If the change was accidental (rule drift), investigate and fix before deployment.

**Stress testing for non-reasoning models**: Provide intentionally incomplete or ambiguous inputs. Verify that the Plan's validation steps and if/else branching handle them correctly (ask for clarification, mark TBD, reject out-of-scope) rather than hallucinating a response.

### 8.4 Feedback Loops and Refinement

**The failure mode signal**: When an agent produces a structurally incorrect output at an unacceptable rate, that is a signal that the current tier is insufficient. Move up one tier and re-evaluate.

**Change management principle**: Rules change often; execution flow changes rarely. When a business rule changes (new pricing table, updated brand guidelines, revised citation format), only the relevant Rule Block should change. The Task and Plan remain stable. This is the core value of orthogonal design.

**Introducing new rules**:
1. Create a new named Rule Block with the rule text.
2. Add a reference to the Rule Block name in the Task (under "Governing Rules").
3. Add a step or validation reference in the Plan.
4. Run the golden example set to confirm correct behavior.

Do not add the rule text inline to the Task or Plan, even temporarily. Create the Rule Block first.

**When to split Rule Blocks**: If a Rule Block exceeds approximately 150 lines, consider splitting it by semantic purpose. A single "Citation Rules" block that covers structure, numbering, metadata, and validation should become four separate blocks: "Citation Structure Rules", "Citation Numbering Rules", "Citation Metadata Rules", "Citation Validation Rules". Smaller blocks are more precisely referenceable and easier to update.

---

## Part 9: Practical Workflow

### 9.1 Day-to-Day Design Process

Follow these six steps in order for every new agent:

**Step 1: Determine tier**

Answer the escalation trigger questions from Section 3.5. Start at Tier 1 and escalate only when a trigger applies. Do not begin at Tier 3 unless the requirements clearly demand it.

**Step 2: Start with Task**

Write WHAT before HOW. Draft the objective, then the acceptance criteria (MUST/NEVER statements), then the output contract. Do not write the Plan or Rule Blocks yet. A clean Task forces clarity about what success actually looks like.

**Step 3: Create Rule Blocks for details**

Before writing the Execution Plan, identify what syntax, schemas, or formatting the Plan will need to reference. Create those Rule Blocks first. This is "schema-first" design: defining the rules before defining the steps that apply them.

From empirical testing: schema-first design achieves 98% structural consistency in output, versus 60% when schema is defined after the Plan is written.

**Step 4: Add the Execution Plan**

Now write HOW. Create atomic steps that apply the Rule Blocks by name. Include validation steps. Include conditional branching for incomplete inputs and invalid outputs. Guardrails go in Step 1.

**Step 5: Validate orthogonality**

Run the Placement Router on every line of the prompt. For each line, ask: does this belong in Task (outcome), Plan (method), or Rule Block (syntax)? If content is in the wrong component, move it.

**Step 6: Test for anti-patterns**

Run the detection checklist from Section 4.6. Resolve any duplication or misplaced ownership before deployment.

### 9.2 Repository and File Organization

A clean repository structure makes Rule Block reuse across agents straightforward:

```
/prompts
  /agents
    brief_writer.md        (Task + Plan — references rules by name)
    quoting_agent.md       (Task + Plan — references rules by name)
    sales_agent.md         (Task + Plan — references rules by name)

  /rules
    brand_guardrail.md     (single brand restriction template)
    citation_formatting.md (full citation HTML structure rules)
    highlight_formatting.md (gap and default mark rules)
    context_source_mapping.md (header → category mapping table)
    json_schema_rules.md   (quote JSON schema definition)
    pricing_rules.md       (SKU prices, rounding, discounts)

  /templates
    tier_1_template.md     (minimal Task structure)
    tier_2_template.md     (Task + minimal Plan)
    tier_3_template.md     (full Task + Plan + Rule Block references)

  /golden_examples
    brief_writer/          (input/output pairs for regression testing)
    quoting_agent/
```

**Naming conventions**:
- Rule Block files: `kebab-case.md` for files, `Title Case Rules` for block names referenced in prompts.
- Agent files: `snake_case.md`.
- Keep Rule Block names stable — they are identifiers in the Task and Plan. Rename with care.

**Version control**: Rule Block changes should be small and isolated. A single commit should change one Rule Block. This makes the change history auditable: "Citation Formatting Rules: added zero-nesting constraint" is a meaningful commit message. "Updated prompts" is not.

### 9.3 Collaboration Patterns

**Review checklist for prompt pull requests**: Before merging a prompt change, reviewers should verify:

- [ ] No content duplicated across components.
- [ ] All Rule Blocks referenced by name (no inline rule text in Task or Plan).
- [ ] Guardrails are Step 1 in the Plan.
- [ ] Validation steps cover all acceptance criteria in the Task.
- [ ] No examples in Task or Plan (only in Rule Blocks).
- [ ] Golden examples still pass after the change.

**Onboarding pattern**: Teach new team members to read prompts in component order: Task first (understand WHAT), then Rule Blocks (understand DETAILS), then Execution Plan (understand HOW). This is the canonical reading order. The Task alone should give a clear picture of what the agent does; the Plan alone should give a clear picture of how it executes; Rule Blocks alone should give a complete specification of each rule.

**Schema-first workflow in team settings**: When multiple people contribute to a prompt (one person owns the business rules, another owns the output format), agree on the Rule Blocks first. The Task and Plan can be drafted independently once Rule Block names are stable.

### 9.4 Integration with LLM Applications

**Standard API pattern**: The full system prompt (Task + Plan + Rule Blocks concatenated) maps to the `system` message in most LLM APIs. User input maps to the `user` message. Keep this separation clean.

```python
# Example: assembling a system prompt from components
task = read_file("prompts/agents/brief_writer.md")
rules = "\n\n".join([
    read_file("prompts/rules/brand_guardrail.md"),
    read_file("prompts/rules/context_source_mapping.md"),
    read_file("prompts/rules/citation_formatting.md"),
    read_file("prompts/rules/highlight_formatting.md"),
])

system_prompt = task + "\n\n" + rules

response = llm_client.chat(
    system=system_prompt,
    user=user_message
)
```

**Parameterization**: Use template variables (e.g., `{{company_name}}`) for account-specific values that change between deployments. Substitute these at runtime, not by editing the prompt file.

**KV cache optimization**: Keep the system prompt prefix identical across calls for the same agent configuration. Inject dynamic data (company name, current date, supporting data) into the user message. Prompt caching activates at approximately 1,024 tokens of matching prefix — stable system prompts at this scale provide meaningful latency and cost reductions.

**Multi-agent rule sharing**: The key advantage of orthogonal design in multi-agent systems is Rule Block reuse. If a `Citation Formatting Rules` block is used by three agents, a single update to that file propagates to all three agents on the next deployment. This is the production-scale benefit that justifies the upfront design cost.

---

## Appendix A: Glossary of Terms

**Acceptance Criteria**: Explicit MUST and NEVER statements in the Task block that define what constitutes a valid output and what constitutes a failure.

**Atomic Step**: A Plan step that performs a single, well-defined action that could be implemented as a single function. Steps are atomic when they cannot be split into smaller meaningful actions.

**Citation Markup**: Structured HTML markup using `<mark>` and `<sup>` tags with data attributes (`data-citation-id`, `data-id`, `data-type`, `data-title`, `data-reasoning`) to embed provenance information inline in the output.

**Controlled Duplication**: The one sanctioned exception to the no-duplication rule — a single-line reminder in Task and a single validation line in Plan for critical constraints that a non-reasoning model consistently violates. Temporary, minimal, verbatim.

**Dual Ownership**: Anti-pattern where both Task and Plan define or enforce the same scope or constraint, creating overlapping authority.

**Execution Plan**: The HOW component. An ordered sequence of atomic steps that operationalize the Task. Applies Rule Blocks by reference. Contains validation logic and conditional branching.

**Frontend Language**: Anti-pattern where visual or UI-specific terms (hover, color, visibility, CSS) appear in the system prompt. CSS belongs in frontend stylesheets, not prompts.

**Gap Highlight**: Semantic HTML markup using `<mark class="highlight" data-type="gap">` to indicate missing or incomplete information in the output.

**Guardrail**: A Rule Block that enforces scope boundaries, typically restricting the agent to a specific brand or context. Always the first step in the Execution Plan. Always hard rejection.

**Hard Rejection**: The guardrail response pattern that refuses out-of-scope requests without fallback. Contrast with soft fallback ("I can try my best").

**KV Cache**: Key-value cache in LLM inference systems that stores and reuses identical prompt prefixes across calls, reducing latency and cost. Stable system prompts benefit from this optimization.

**Lossless Compression**: DSL compression that preserves all semantic signals — style flags, structure flags, conflict markers, behavior flags — such that full behavior can be recovered from the compressed form.

**Lossy Compression**: DSL compression that drops critical signals (politeness cues, tone reinforcement, conflict escalation rules), producing blunt and inconsistent outputs.

**Middle-Term Procedural DSL**: A structured but natural-language prompt format using STEP/DESC or YAML-like syntax. Achieves 30–40% token reduction while retaining interpretability and nuance. The recommended format for production agents.

**Mixed Intent**: Anti-pattern where the Task block contains procedural steps (HOW), causing acceptance criteria to be buried among procedure.

**Non-Reasoning Model**: LLMs optimized for speed and cost that cannot infer implicit rules or intent. Examples: Claude Haiku, GPT-4o mini, smaller fine-tuned models. Require Tier 3 design.

**Orthogonality**: The property of having non-overlapping responsibilities. In prompt design: Task, Plan, and Rule Blocks each have exactly one responsibility with no overlap or duplication between them.

**Output Contract**: The portion of the Task block that defines the format, scope, and allowed elements of the final output (e.g., HTML only, JSON per schema, single code block).

**Placement Router**: The seven-question decision filter for determining where any given instruction belongs (Task, Plan, or Rule Block).

**Policy Echo**: Anti-pattern where the Execution Plan repeats rule syntax from a Rule Block, creating duplicate definitions.

**Rule Block**: The DETAILS component. The single source of truth for syntax, schemas, mapping rules, formatting requirements, and constraints. Referenced by name from Task and Plan. Never duplicated.

**Schema Leakage**: Anti-pattern where output schema or markup syntax is defined or restated in the Plan or Task rather than exclusively in a Rule Block.

**Semantic Markup**: HTML markup that conveys structural meaning through tag types and data attributes rather than visual styling. CSS controls appearance; the prompt controls semantics.

**Task Block**: The WHAT component. Defines the objective, acceptance criteria, output contract, and rule references. Declarative, not procedural.

**Tier 1**: Task-only prompt structure. Suitable for creative, exploratory, low-risk agents.

**Tier 2**: Task + minimal Execution Plan. Suitable for light structure with some validation.

**Tier 3**: Full orthogonal design: Task + Execution Plan + Rule Blocks. Required for production, deterministic output, non-reasoning models, and pipeline integration.

**TKDSL (KeyTokenDSL)**: An ultra-condensed DSL format using single-token abbreviations backed by a dictionary. Achieves 40–70% token reduction. Best for multi-agent internal pipelines.

**Validation Discipline**: The clear ownership model for validation: Task owns acceptance criteria, Plan owns enforcement (validation steps), Rule Blocks define the syntax that validation enforces.

---

## Appendix B: Template Library

### Template B1: Tier 1 Task-Only Prompt

```markdown
## Objective
[One sentence defining what the agent must achieve.]

## Acceptance Criteria
- MUST [explicit requirement 1]
- MUST [explicit requirement 2]
- NEVER [explicit prohibition 1]

## Output
[Describe the expected output format: text, list, paragraphs, etc.]
```

### Template B2: Tier 2 Task + Minimal Plan

```markdown
## Task

### Objective
[One sentence defining the agent's purpose.]

### Acceptance Criteria
- MUST [requirement 1]
- MUST [requirement 2]
- NEVER [prohibition]

### Output Contract
[Output format: text only, JSON, HTML, etc.]

---

## Execution Plan

```xml
<plan>
  <step>
    <action_name>parse_input</action_name>
    <description>[What this step extracts from the input.]</description>
  </step>

  <step>
    <action_name>generate_output</action_name>
    <description>[What this step generates, applying which rules.]</description>
  </step>

  <step>
    <action_name>validate_response</action_name>
    <description>[What this step checks before responding.]</description>
  </step>

  <if_block condition="missing_info">
    <step>
      <action_name>ask_for_clarification</action_name>
      <description>[Ask for what is missing.]</description>
    </step>
  </if_block>

  <if_block condition="valid">
    <step>
      <action_name>reply_final</action_name>
      <description>[Return the completed output.]</description>
    </step>
  </if_block>
</plan>
```
```

### Template B3: Tier 3 Full Orthogonal Prompt

```markdown
## Task Overview

### Objective
[One sentence.]

### Acceptance Criteria
- MUST [requirement referencing a Rule Block by name]
- MUST [requirement referencing a Rule Block by name]
- NEVER [prohibition]
- NEVER [prohibition]

### Output Contract
[Format description — e.g., HTML only using semantic tags X, Y, Z]

### Governing Rules
- [Rule Block Name A]
- [Rule Block Name B]
- [Rule Block Name C]

---

## Execution Plan

This plan operates in accordance with: [Rule Block A], [Rule Block B], [Rule Block C].

```xml
<plan>

  <step>
    <action_name>apply_guardrail</action_name>
    <description>Verify request is within scope per [Guardrail Rule Block].
    If out of scope, reject and stop.</description>
  </step>

  <step>
    <action_name>parse_input</action_name>
    <description>[What to extract from input.]</description>
  </step>

  <step>
    <action_name>[processing_step]</action_name>
    <description>[Processing logic, referencing rule blocks by name.]</description>
  </step>

  <step>
    <action_name>generate_output</action_name>
    <description>Generate output per [Output Rules]. Apply [Rule Block A]
    and [Rule Block B] per the governing rules.</description>
  </step>

  <step>
    <action_name>validate_output</action_name>
    <description>Verify: [criterion 1 per Rule Block A]. Verify:
    [criterion 2 per Rule Block B].</description>
  </step>

  <if_block condition="invalid_or_missing">
    <step>
      <action_name>reply_with_issues</action_name>
      <description>[How to handle failures: request clarification,
      mark gaps, return error.]</description>
    </step>
  </if_block>

  <if_block condition="valid">
    <step>
      <action_name>reply_final</action_name>
      <description>Return the validated, complete output.</description>
    </step>
  </if_block>

</plan>
```

---

## Rule Blocks

### [Rule Block Name A]

## [START] [Rule Block Name A]

[Full rule text, syntax definitions, mapping tables, or schema.]

[Optional: minimal example — one or two concrete illustrations of the rule.]

## [END] [Rule Block Name A]

---

### [Rule Block Name B]

## [START] [Rule Block Name B]

[Full rule text.]

## [END] [Rule Block Name B]
```

### Template B4: Generic Rule Block

```markdown
## [START] [Rule Name] Rules

[One sentence explaining the purpose of this rule block.]

### General Principles
- [Principle 1 — always/never statement]
- [Principle 2 — always/never statement]

### Specification
[Detailed rule text: syntax, schema, mapping table, or regex.]

### Examples
[Minimal: one or two concrete illustrations of correct usage.]

[Optional: one example of incorrect usage followed by the correct form.]

## [END] [Rule Name] Rules
```

---

## Appendix C: Decision Trees

### C1: Tier Selection Decision Tree

```
START: What is this agent for?
  |
  +---> Creative, exploratory, low-risk, no schema needed?
  |       YES ---> TIER 1 (Task only)
  |       NO  ---> continue
  |
  +---> Does it need a workflow sequence (even a simple 3-step one)?
  |       YES ---> at least TIER 2
  |       NO  ---> TIER 1 may be sufficient
  |
  +---> Does it produce structured output (JSON, HTML with schema)?
  |       YES ---> TIER 3
  |       NO  ---> continue
  |
  +---> Does it require multi-step validation?
  |       YES ---> TIER 3
  |       NO  ---> continue
  |
  +---> Will it run on a non-reasoning model?
  |       YES ---> TIER 3 (non-negotiable)
  |       NO  ---> continue
  |
  +---> Is this a production agent in a product pipeline?
          YES ---> TIER 3
          NO  ---> TIER 1 or 2 likely sufficient
```

### C2: Placement Router Flowchart

```
START: Where does this instruction belong?
  |
  Q1: Is it an outcome (success condition, acceptance criterion)?
  |     YES ---> TASK
  |     NO  ---> continue
  |
  Q2: Is it rule text, syntax, schema, or regex?
  |     YES ---> RULE BLOCK
  |     NO  ---> continue
  |
  Q3: Does it specify order, sequence, or conditional branching?
  |     YES ---> PLAN
  |     NO  ---> continue
  |
  Q4: Is it a format or schema contract (output must be X)?
  |     YES ---> TASK
  |     NO  ---> continue
  |
  Q5: Is it a validation check or preflight?
  |     YES ---> PLAN
  |     NO  ---> continue
  |
  Q6: Is it about where markup is allowed?
  |     Scope definition (what CAN be marked)  ---> TASK
  |     Scope enforcement (validate markup)    ---> PLAN
  |     NO  ---> continue
  |
  Q7: Is it an example?
        YES ---> RULE BLOCK only (minimal)
        NO  ---> Re-examine with Q1; if still unclear, default to TASK
```

### C3: Anti-Pattern Detection Tree

```
START: Review the prompt for these failures.
  |
  +---> Does any text appear in two or more components?
  |       YES ---> DUPLICATION detected. Use recovery process (Section 4.6).
  |
  +---> Does the Task contain "step", "then", "first", "next", "parse"?
  |       YES ---> MIXED INTENT. Move procedural language to Plan.
  |
  +---> Does the Plan contain a schema, regex, or markup syntax definition?
  |       YES ---> POLICY ECHO or SCHEMA LEAKAGE.
  |               Extract to Rule Block, reference by name in Plan.
  |
  +---> Do both Task and Plan define the same constraint?
  |       YES ---> DUAL OWNERSHIP. Task defines (contract),
  |               Plan enforces (validation step), Rules define syntax.
  |
  +---> Does the prompt contain style attributes, colors, or hover behavior?
          YES ---> FRONTEND LANGUAGE. Replace with semantic markup.
                  CSS belongs in the frontend, not the prompt.
```

---

## Appendix D: Further Reading

The following documents in the `_DOCS` knowledge base provide additional depth on specific topics. They are the primary sources for this handbook.

| Document | Content |
|---|---|
| `_DOCS/Prompt_Design_Framework.md` | Foundational framework definition, all three components, tiered model, anti-patterns, Placement Router. Start here. |
| `_DOCS/Extended_Prompt_Design_Ortogonality.md` | Fully worked examples for Sales Agent, Quoting Agent, and Python ETL Agent with Task, Plan, and Rule Blocks. |
| `_DOCS/Brief_agent_prompt_design_learnings.md` | Production learnings from the Brief-Writing Agent refactor, including the overlap problem analysis and before/after comparison. |
| `_DOCS/brief-agent-master-promtp.md` | The full production Brief-Writing Agent system prompt, including all four Rule Blocks in their current form. |
| `_DOCS/Leanrinings_from_prompt_design_non_reasoning.md` | Practical patterns for GPT and non-reasoning models, validation discipline examples, anti-pattern summaries. |
| `_DOCS/prompt-dsl-language-research.md` | Full research transcript on DSL approaches, KV cache implications, token compression strategies, and TKDSL format. |
| `_DOCS/prompt-TKDSL-workframe.prompt-design.md` | The DSL workbook: three prompt layers, compression strategies, lossless/lossy comparison, decision framework for format selection. |
| `_DOCS/Graph/00-Index.md` | Knowledge graph index — entry point for all interconnected concept nodes. |
| `_DOCS/Graph/06-Tiered-Complexity-Model.md` | Detailed escalation triggers and real-world tier assignments. |
| `_DOCS/Graph/07-Placement-Router.md` | All seven Placement Router questions with examples and testing protocol. |
| `_DOCS/Graph/08-Validation-Discipline.md` | Validation ownership model, anti-patterns for validation, the validation chain. |
| `_DOCS/Graph/09-Anti-Patterns.md` | Detailed descriptions and concrete examples of all five anti-patterns with detection and fix guidance. |
| `_DOCS/Graph/10-Orthogonality-Violations.md` | How violations manifest in production, recovery process step by step. |
| `_DOCS/Graph/11-Brief-Writing-Agent.md` | Architecture of the flagship Tier 3 example with lessons from real-world use. |
| `_DOCS/Graph/14-Guardrail-System.md` | Full guardrail patterns, hard rejection principle, test cases. |
| `_DOCS/Graph/15-Non-Reasoning-Model-Design.md` | Four design patterns for non-reasoning models with detailed code examples. |
| `_DOCS/Graph/16-Prompt-DSL-Research.md` | DSL approach advantages, disadvantages, potential features, and current status. |
| `_DOCS/Graph/18-Design-Patterns-by-Agent.md` | Sales, Quoting, and Python ETL patterns with complete Task/Plan/Rule Block implementations. |
| `_DOCS/Graph/19-Learnings-and-Insights.md` | 13 empirical insights with evidence, lessons, and best practices checklist. |
| `_DOCS/Graph/20-Key-Takeaways.md` | Summary of core principles, the orthogonality checklist, common mistakes, cost-benefit analysis. |
