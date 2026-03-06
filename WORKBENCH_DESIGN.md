# WORKBENCH_DESIGN.md: Prompt Engineering Workbench

**Version:** 0.1
**Date:** 2026-03-06
**Purpose:** Personal tool for designing and iterating on LLM agent system prompts using the orthogonal framework

---

## What This Is

A command-line workbench that lets you:
1. Write a spec for an agent in Markdown
2. Generate a draft system prompt using OpenAI + your prompt design rules
3. Test the prompt against sample messages
4. Refine and iterate quickly

Not a library. Not a service. Not something for others to use. Just a tool for you to design better prompts faster.

---

## The Workflow

```
You write a spec      Design agent      You test the      You refine
   (.md file)    →   generates        prompt & iterate  →  based on
                    (LLM-powered)       (live testing)      feedback
                        ↓
                   System prompt
                   (ready to use)
```

---

## Five Commands

### 1. `promptctl init-spec <name>`
Scaffolds a new agent spec file with sections for role, context, inputs, outputs, constraints.

**Usage:**
```bash
promptctl init-spec my-analyst
# Creates: projects/my-analyst/specs/my-analyst.agent-spec.md
# Edit it, then run `design`
```

### 2. `promptctl design <spec.md> [--tier 1|2|3]`
Reads your spec and generates a draft system prompt.

The design agent:
- Reads your spec (role, inputs, outputs, constraints)
- Picks the right complexity tier (default: auto-detect)
- Loads applicable rule blocks (formatting, schemas, guardrails)
- Calls OpenAI to generate a substantive Task Block
- Renders the complete system prompt

**Usage:**
```bash
promptctl design projects/my-analyst/specs/my-analyst.agent-spec.md --tier 2
# Outputs to: projects/my-analyst/designs/design.json
# Also prints: projects/my-analyst/prompts/system.md (rendered)
```

**Optional flags:**
- `--tier [1|2|3]` — Override auto tier selection
- `--model [gpt-5.2-mini|gpt-5.4|gpt-5.4-pro|gpt-5-mini|gpt-4o]` — LLM to use (default: gpt-5.2-mini)
- `--verbosity [low|medium|high]` — Reasoning effort for gpt-5.x models (default: medium)
- `--verbose` — Show the prompt sent to OpenAI

### 3. `promptctl run <identifier> --message "your test message"`
Test your generated system prompt against a sample message.

**Usage:**
```bash
promptctl run my-analyst --message "What are the top 3 risks in Q1 financials?"
# Runs system prompt + your message through OpenAI
# Prints the response + metadata (tokens, latency)
```

**Optional flags:**
- `--model [gpt-5.2-mini|gpt-5.4|gpt-5.4-pro|gpt-5-mini|gpt-4o]` — LLM to use (default: gpt-5.2-mini)
- `--verbosity [low|medium|high]` — Reasoning effort for gpt-5.x models (default: medium)

### 4. `promptctl refine <identifier> --feedback "feedback text"`
Takes your saved design and refines it based on feedback.

The refinement agent:
- Reads the saved design
- Takes your feedback (e.g., "add more structure", "focus on risks not opportunities")
- Re-runs through the design agent with your feedback as context
- Generates an improved version

**Usage:**
```bash
promptctl refine my-analyst --feedback "Add a JSON schema section for the output"
# Updates: projects/my-analyst/designs/design.json
# Prints: updated system.md
```

**Optional flags:**
- `--model [gpt-5.2-mini|gpt-5.4|gpt-5.4-pro|gpt-5-mini|gpt-4o]` — LLM to use (default: gpt-5.2-mini)
- `--verbosity [low|medium|high]` — Reasoning effort for gpt-5.x models (default: medium)
- `--verbose` — Show the refinement prompt sent to OpenAI

### 5. `promptctl evaluate <identifier> [--scenarios scenarios.md]`
Runs structured test cases against your prompt.

**Usage:**
```bash
promptctl evaluate my-analyst --scenarios tests/analyst-scenarios.md
# Runs 3-5 test messages
# Prints: pass/fail summary + transcripts
```

---

## Model and Verbosity Control

### Default: GPT-5.2-mini

All LLM-powered commands now default to **gpt-5.2-mini** for cost-efficient reasoning.

### Model Override

Use `--model` to select a different LLM:

```bash
promptctl design spec.md --model gpt-4o               # Use gpt-4o
promptctl run my-agent --message "test" --model gpt-5.4-pro   # Use gpt-5.4-pro
promptctl design spec.md --model gpt-5.2-mini          # Explicitly use the default
```

### Reasoning Effort (GPT-5.x Only)

Use `--verbosity` to control reasoning depth for gpt-5.x models:

```bash
promptctl design spec.md --verbosity low       # Fast, minimal reasoning
promptctl design spec.md --verbosity medium    # Balanced (default)
promptctl design spec.md --verbosity high      # Deep reasoning, longer latency
```

> **Note:** `--verbosity` is only applied to gpt-5.x models. For gpt-4.x models, the flag is silently ignored.

### Configuration via Environment

Set defaults in `.env` or `.env.local`:

```bash
OPENAI_MODEL=gpt-5.4-pro        # Override default model
OPENAI_VERBOSITY=high           # Override default verbosity
OPENAI_MAX_TOKENS=2000          # Override max tokens (auto-selected by model otherwise)
```

---

## The Folder Layout

You interact with this structure:

```
ai_components/
  rule_blocks/
    citations.md           ← Edit these directly; they're your guardrails & schemas
    html-markup.md
    brief-json-schema.md
    [add more .md files as needed]

projects/
  my-analyst/
    specs/
      my-analyst.agent-spec.md       ← You write this; version it in Git
    designs/
      design.json                    ← Generated; tracks Task/Plan/Rule refs
    prompts/
      system.md                      ← Rendered output; ready to use
    tests/
      scenarios.md                   ← Test messages (optional)
  [other agents...]

PROMPT_DESIGN_HANDBOOK.md            ← Read this to understand the framework
WORKBENCH_DESIGN.md                  ← This file; how to use the workbench
```

---

## The Five Core Concepts

These are the building blocks. See PROMPT_DESIGN_HANDBOOK.md for details.

### 1. **AgentSpec**
What you provide: a Markdown file describing the agent's role, inputs, outputs, constraints.

```markdown
# Analyst Agent

## Role
Financial analyst that identifies risks and opportunities.

## Inputs
- Quarterly financial data (JSON)
- Industry benchmarks

## Outputs
- Risk assessment (structured)
- Opportunity matrix

## Constraints
- No speculation; only data-driven conclusions
- Cite all sources
```

### 2. **TaskBlock (WHAT)**
The outcome you want. Generated by the design agent.

"Generate a structured risk assessment of financial data. Return JSON with risks ranked by impact."

### 3. **ExecutionPlanBlock (HOW)**
The steps to get there. Generated for Tier 2+ designs.

1. Parse input data
2. Compare to benchmarks
3. Identify outliers
4. Score each risk
5. Return JSON

### 4. **RuleBlocks (DETAILS)**
Your formatting rules, schemas, guardrails. You edit these as `.md` files.

- `citations.md` — How to cite sources
- `html-markup.md` — HTML formatting rules
- `brief-json-schema.md` — Output schema examples

### 5. **PromptDesign (Complete)**
The final output: Task + Plan + selected Rule Blocks, rendered as a system prompt ready to use.

---

## The Three Tiers

Pick a tier based on what your agent needs to do:

### Tier 1: Task Only
Use when the agent just needs to understand the goal and constraints.

**Example:** "Summarize this text in 3 bullet points."

**What you get:** Goal + constraints + acceptance criteria. No step-by-step plan.

**When to use:** Creative tasks, open-ended outputs, exploratory agents.

### Tier 2: Task + Lightweight Plan
Use when you want some structure but not full formality.

**Example:** "Extract key facts and cite sources" (needs a plan to separate extraction from citation).

**What you get:** Task + 4-6 ordered steps + constraints. Some rule blocks.

**When to use:** Information extraction, analysis, structured reasoning.

### Tier 3: Full Orthogonal Design
Use when you need strict determinism: JSON schemas, rigid formatting, multi-step validation.

**Example:** "Validate financial data and produce a signed JSON report" (needs schemas, validation steps, guardrails).

**What you get:** Task + detailed plan (10+ steps) + multiple rule blocks (schemas, guards, formatting).

**When to use:** Data processing, compliance, any output that must be machine-readable and validated.

**Auto-selection:** The design agent detects tier based on your spec:
- If outputs include "JSON", "schema", "format" → Tier 3
- If constraints include "structure", "validate" → Tier 2-3
- Otherwise → Tier 1

**Override:** `--tier 2` flag forces a tier if you disagree.

---

## Anti-Patterns to Avoid

Read these. They're common mistakes that make prompts brittle.

**Policy Echo:** Stating the same constraint in multiple places (rule block AND task description AND plan step).

✅ **Fix:** State it once, in the right place. Reference it elsewhere.

**Mixed Intent:** Task block says "be concise", plan says "be detailed". Conflicting signals.

✅ **Fix:** Reconcile. Usually move detail to plan, concision to task.

**Dual Ownership:** Both the rule block AND the task say "output as JSON". Who's in charge?

✅ **Fix:** Task says "follow the JSON schema in Rule Block X". Rule block owns the schema.

**Schema Leakage:** Task says "output: {name: string, age: int}". But the schema is in a rule block.

✅ **Fix:** Task says "output: [see rule block: person-schema]". Leakage fixed.

For more, see PROMPT_DESIGN_HANDBOOK.md, Part 4.

---

## The Design Agent (How It Works)

When you run `promptctl design`, here's what happens:

1. **Read spec** — Parse your `.agent-spec.md` file
2. **Select tier** — Auto-detect or use `--tier` flag
3. **Load rule blocks** — Scan `ai_components/rule_blocks/` for relevant ones
4. **Build scaffold** — Create initial TaskBlock + ExecutionPlanBlock structure
5. **LLM refinement** — Call OpenAI with:
   - Your AgentSpec
   - Selected tier
   - Rule block contents (as context)
   - Instruction: "Generate a substantive Task Block with specific outcomes, constraints, and acceptance criteria"
6. **Render** — Convert the PromptDesign to a readable system prompt
7. **Save** — Write to `projects/<name>/designs/design.json` and `prompts/system.md`
8. **Output** — Print the rendered prompt to stdout

**Why LLM-powered?** Because "generate a good task description" is a job for a language model. The orthogonal framework gives structure; the LLM fills in the substance.

---

## The Iteration Loop

This is where the real work happens.

### Step 1: Generate
```bash
promptctl design spec.md
# Outputs: system.md
```

### Step 2: Test (Manual)
Open the rendered system prompt. Try it:
- Ask your test question
- See if the response looks right
- Note what's missing or wrong

### Step 3: Refine
Two options:

**Option A: Quick feedback**
```bash
promptctl refine my-analyst --feedback "Add guardrail: never speculate"
# Re-runs design agent with your feedback
```

**Option B: Direct edit**
Edit the rule blocks in `ai_components/rule_blocks/` directly. Re-run design.

### Step 4: Test Live (Automated)
```bash
promptctl run my-analyst --message "test question"
# Calls OpenAI with your new prompt
# Prints response
```

### Step 5: Repeat
Refine → test → observe → refine. Usually 3-5 iterations to get it right.

---

## Rule Blocks (Editable Reference Files)

Rule blocks live in two locations and are merged at load time:

| Location | Purpose | Priority |
|---|---|---|
| `ai_components/rule_blocks/` | Your custom and override rules | High (wins on conflict) |
| `prompt_design_system/rule_blocks/` | Reference implementations shipped with the package | Low (base layer) |

When the same filename stem exists in both places the `ai_components/` version is used.  Never edit `prompt_design_system/rule_blocks/` directly — those files are reference implementations.

### Example: `citations.md`
```markdown
# Citation Rules

When the agent references a source:

1. Include the source name or ID
2. Add a footnote with the date accessed
3. Use format: [source](date)

Example:
"According to Q1 earnings [2024-03-15], revenue grew 12%."
```

### Adding a Custom Rule Block

1. Create `ai_components/rule_blocks/my-rule.md`
2. Write your rule in clear language
3. Run design — it auto-loads all `.md` files from both directories
4. Reference it in the spec if needed: `See rule block: my-rule`

### Overriding a Package Rule Block

1. Find the block stem you want to replace (e.g. `citation_formatting_rules`)
2. Create `ai_components/rule_blocks/citation_formatting_rules.md` with your version
3. Your copy takes priority — the package version is ignored for that name

### Built-in Rule Blocks (in `ai_components/rule_blocks/`)
- `citations.md` — Citation and source formatting
- `html-markup.md` — HTML tag usage and styling
- `brief-json-schema.md` — JSON output schema examples

### Reference Rule Blocks (in `prompt_design_system/rule_blocks/`)
These are loaded automatically and available to DesignAgent without any action on your part.  Override any of them by placing a same-named file in `ai_components/rule_blocks/`.

---

## Configuration

Minimal setup. Two files:

### `prompt_design_system/config.py`
```python
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o"
WORKBENCH_ROOT = Path(__file__).parent.parent
RULE_BLOCKS_DIR = WORKBENCH_ROOT / "ai_components" / "rule_blocks"
PROJECTS_DIR = WORKBENCH_ROOT / "projects"
```

### Environment
```bash
export OPENAI_API_KEY="sk-..."
```

That's it. No config files to manage.

---

## Storage (Git-Tracked)

Everything is a file. Version control is built-in:

- `specs/*.agent-spec.md` — Your spec. Change it, commit it.
- `designs/design.json` — Derived from spec. Can be regenerated.
- `prompts/system.md` — Rendered output. Can be regenerated.
- `ai_components/rule_blocks/*.md` — Your guardrails. Commit changes.

**Workflow:**
```bash
# Edit spec
vim projects/my-analyst/specs/my-analyst.agent-spec.md

# Generate design
promptctl design projects/my-analyst/specs/my-analyst.agent-spec.md

# Test it
promptctl run my-analyst --message "test"

# Commit the spec (and optionally the design)
git add projects/my-analyst/specs/my-analyst.agent-spec.md
git commit -m "Update analyst agent spec: add risk thresholds"
```

No databases. No migrations. Just files and Git.

---

## Evaluation (Optional)

For structured testing, create a `tests/scenarios.md` file with test cases:

```markdown
# Test Scenarios: Analyst Agent

## Scenario 1: Normal Input
Input: Q1 2024 financials (JSON)
Expected: Risk assessment with 3-5 risks ranked by impact

## Scenario 2: Edge Case
Input: Missing Q4 2023 baseline
Expected: Error message explaining missing data

## Scenario 3: Guardrail
Input: Request for speculation on future pricing
Expected: Decline, explain data-only mandate
```

Run evaluation:
```bash
promptctl evaluate my-analyst --scenarios tests/analyst-scenarios.md
# Runs each scenario
# Prints: pass/fail + transcript
```

---

## Troubleshooting

### "Design took too long"
The LLM call to OpenAI is slow. This is normal (~5-10s for gpt-4o).
- Use `--verbose` to see the prompt being sent
- If the prompt is huge, you've loaded too many rule blocks (trim them)

### "Generated prompt is too generic"
The design agent needs better feedback in the spec.
- Be specific: "Should output only in JSON" vs. "Structured output"
- List constraints clearly, not as prose
- Provide an example of desired output in the spec

### "How do I know if it's working?"
Run a real test:
```bash
promptctl run my-agent --message "your real question"
# If the response is useful, it's working
```

---

## Next: What to Build

**Week 1:**
- [ ] Wire OpenAI into `DesignAgent.create_design()` (design agent actually calls LLM)
- [ ] Test end-to-end: spec → design → rendered prompt

**Week 2:**
- [ ] Implement `promptctl refine` command (feedback loop)
- [ ] Implement `promptctl run` command (live testing)
- [ ] Test iteration loop: generate → test → refine → test

**Week 3:**
- [ ] Polish CLI output and help text
- [ ] Add `promptctl evaluate` for structured test scenarios
- [ ] Document your rule blocks

---

## Further Reading

- **PROMPT_DESIGN_HANDBOOK.md** — Complete practitioner guide. Start here for deep understanding.
- **CLAUDE.md** (project instructions) — Framework principles and conventions.
- **Graph/ folder** — 21-file knowledge base on system prompt design (referenced by handbook).

---

## Summary

You have a personal prompt engineering workbench. The key idea: **specs in, system prompts out, fast iteration**.

Five commands. Git-tracked. No infrastructure. No plugins. Just a tool that makes designing agent prompts faster and more systematic.

The orthogonal framework (Task/Plan/Rule Blocks) keeps designs clean and reusable. The LLM-powered design agent generates substance, not just scaffolding. The quick test loop lets you iterate in minutes, not days.

Start with `promptctl init-spec`, write your first agent, run `design`, and iterate. That's the workbench.
