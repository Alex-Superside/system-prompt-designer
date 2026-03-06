## Tier Patterns Overview

This directory contains reusable tier pattern templates derived from the prompt design framework docs and brief-agent research.

- **Tier 1**: Task-only patterns for creative or low-risk agents.
- **Tier 2**: Task plus a minimal Execution Plan for light structure and validation.
- **Tier 3**: Full separation of Task, Execution Plan, and Rule Blocks for deterministic, schema-bound agents.

### Summary

Tier 1 templates define only Task (objective, acceptance criteria, output contract) and are suited for creative, low-risk agents. Tier 2 adds a minimal Execution Plan for light structure and validation but keeps rule blocks to a minimum. Tier 3 fully separates Task, Plan, and Rule Blocks and is used when deterministic formats, schemas, guardrails, and multi-step validation are required; the brief-writing agent is a canonical Tier 3 example.

### Pattern Catalog

| ID                   | Tier | Name                              | Primary Use Cases                                  |
|----------------------|------|-----------------------------------|---------------------------------------------------|
| `tier1_generic`      | 1    | `tier1_task_only_pattern`        | Brainstorming, creative writing, exploratory R&D  |
| `tier2_generic`      | 2    | `tier2_task_plus_minimal_plan_pattern` | Sales-like agents, FAQ responders, light recommenders |
| `tier3_generic`      | 3    | `tier3_task_plan_rules_pattern`  | Quoting, code generation, compliance agents       |
| `tier3_brief_writing`| 3    | `tier3_brief_writing_agent_pattern` | Brand-specific brief-writing with citations and guardrails |

