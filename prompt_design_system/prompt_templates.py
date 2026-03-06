"""Load LLM prompt templates from external files or built-in defaults.

Templates are stored under ai_components/prompts/system/ so prompt designers
can edit them without changing Python code (Rules 4, 17, 18). When a file is
missing (e.g. in tests), built-in defaults are used.
"""

from __future__ import annotations

from pathlib import Path

from .config import AppPaths

DESIGN_ENRICHMENT_TEMPLATE_NAME = "design_enrichment"
REFINEMENT_TEMPLATE_NAME = "refinement"
AUDIT_TEMPLATE_NAME = "audit"


def _default_design_enrichment_template() -> str:
    """Built-in template when design_enrichment.txt is not present."""
    return """You are a senior prompt engineer applying the orthogonal prompt design framework.

## Agent Specification

Role: {role_description}
Summary: {summary}
Tier: {tier_value}

Inputs:
{inputs_section}

Outputs:
{outputs_section}

Constraints:
{constraints_section}

Rule Blocks attached:
{rule_block_section}

## Task

Generate a substantive Task Block for this agent.  The output must be valid JSON
with the following keys:

- "goal": a single sentence describing the specific, measurable outcome the
  agent must deliver.  Do NOT repeat the summary verbatim; rewrite it as a
  clear, agent-facing directive.
- "acceptance_criteria": list of exactly 3-4 conditions that define a correct
  output.  Each item must be a concrete, verifiable statement.
- "constraints": list of exactly 2-3 guardrail constraints the agent must
  never violate.  These must be narrower and more actionable than the spec
  constraints above — not paraphrases.{steps_instruction}

## Rules

- Write every string in second person ("You must …", "Each output …").
- Do not introduce examples inside the JSON values.
- Do not add any prose outside the JSON object.
- Return only the JSON object — no markdown fences, no commentary."""


def _default_refinement_template() -> str:
    """Built-in template when refinement.txt is not present."""
    return """You are a senior prompt engineer applying the orthogonal prompt design framework.

## Current Design

Goal: {goal}

Acceptance Criteria:
{criteria_lines}

Constraints:
{constraint_lines}
{steps_section}

## Feedback

{feedback}

## Task

Revise the design based on the feedback above.  Return valid JSON with:

- "goal": revised single-sentence agent-facing directive.
- "acceptance_criteria": list of exactly 3-4 concrete, verifiable conditions.
- "constraints": list of exactly 2-3 actionable guardrail constraints.{steps_instruction}

## Rules

- Write every string in second person ("You must …", "Each output …").
- Do not introduce examples inside the JSON values.
- Return only the JSON object — no markdown fences, no commentary."""


def _default_audit_template() -> str:
    """Built-in template when audit.txt is not present."""
    return """You are a senior linguistic engineer and prompt architect.

## Task: Linguistic Audit

Audit the following Prompt Design for "technical debt" (semantic noise, orthogonality leaks, and linguistic drift).

## Current Design

Goal (WHAT): {goal}

Acceptance Criteria:
{criteria_lines}

Constraints:
{constraint_lines}
{steps_section}

Rule Blocks Referenced:
{rule_blocks_section}

## Audit Rules

- **Semantic Signal Density**: Identify abstract adjectives ("polite", "brief") and replace with explicit constraints ("use first-person plural", "max 100 words").
- **Orthogonality Trinity**: Identify Task logic (outcome-based) in Rule Blocks or Rule syntax (regex, JSON schemas) in the Execution Plan.
- **Silent Hallucinations**: Identify where the model is left to infer intent (e.g. "ask for missing info") instead of instructed on exactly how to handle it (e.g. "If X is missing, return TBD").

## Output Format

Return valid JSON with:
- "density_score": 1-5
- "orthogonality_score": 1-5
- "findings": list of objects with "category" (noise|leak|drift), "location" (Task|Plan|Rules), "evidence" (text snippet), and "suggestion" (DSL-optimized alternative).
- "summary": 1-2 sentence overall synthesis.

Return ONLY JSON. No markdown fences."""


def load_template(paths: AppPaths, name: str) -> str:
    """Load a system prompt template by name; fall back to built-in default if missing.

    Args:
        paths: Application paths (system_prompts_dir is used).
        name: Base name without extension (e.g. "design_enrichment", "refinement", "audit").

    Returns:
        Template string with .format() placeholders.
    """
    path = paths.system_prompts_dir / f"{name}.txt"
    if path.exists():
        return path.read_text(encoding="utf-8").strip()

    return get_default_template(name)


def get_default_template(name: str) -> str:
    """Return built-in template content by name (for tests or when files missing)."""
    defaults = {
        DESIGN_ENRICHMENT_TEMPLATE_NAME: _default_design_enrichment_template,
        REFINEMENT_TEMPLATE_NAME: _default_refinement_template,
        AUDIT_TEMPLATE_NAME: _default_audit_template,
    }
    loader = defaults.get(name)
    if loader is None:
        raise ValueError(f"Unknown template name: {name}")
    return loader().strip()
