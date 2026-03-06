"""Reusable test data objects for the prompt design system test suite.

Centralising fixtures here avoids duplication across test files and makes
intent clear: these are stable representations of the domain, not
incidentally constructed objects.
"""

from __future__ import annotations

from pathlib import Path

from prompt_design_system.models import (
    AgentSpec,
    EvaluationOutcome,
    EvaluationReport,
    EvaluationResult,
    EvaluationScenario,
    ExecutionPlanBlock,
    ExecutionStep,
    PromptDesign,
    PromptTier,
    RuleBlockRef,
    TaskBlock,
)
from prompt_design_system.rule_blocks import RuleBlock, RuleBlockRegistry

# ---------------------------------------------------------------------------
# AgentSpec fixtures
# ---------------------------------------------------------------------------


def minimal_agent_spec() -> AgentSpec:
    """Minimal valid AgentSpec — no constraints, no determinism."""
    return AgentSpec(
        identifier="test-agent",
        summary="Test agent for testing purposes.",
        role_description="A test agent that processes inputs and produces outputs.",
        primary_inputs=["user message"],
        primary_outputs=["processed response"],
        constraints=[],
        determinism_required=False,
    )


def constrained_agent_spec() -> AgentSpec:
    """AgentSpec with constraints — should select Tier 2."""
    return AgentSpec(
        identifier="constrained-agent",
        summary="Agent with guardrail constraints.",
        role_description="A constrained agent with specific rules.",
        primary_inputs=["document"],
        primary_outputs=["summary"],
        constraints=["Do not include personal data.", "Keep responses under 200 words."],
        determinism_required=False,
    )


def deterministic_agent_spec() -> AgentSpec:
    """AgentSpec with determinism_required=True — should select Tier 3."""
    return AgentSpec(
        identifier="deterministic-agent",
        summary="Agent that must produce deterministic JSON output.",
        role_description="A structured output agent.",
        primary_inputs=["raw data"],
        primary_outputs=["json schema output"],
        constraints=["Output must be schema-compliant JSON."],
        determinism_required=True,
    )


def structured_output_agent_spec() -> AgentSpec:
    """AgentSpec with JSON keyword in outputs — triggers Tier 3."""
    return AgentSpec(
        identifier="json-agent",
        summary="Agent producing JSON reports.",
        role_description="Transforms raw inputs into a JSON report.",
        primary_inputs=["data rows"],
        primary_outputs=["JSON report"],
        constraints=[],
        determinism_required=False,
    )


def brief_agent_spec() -> AgentSpec:
    """AgentSpec with 'brief' in identifier — triggers brief-json-schema rule block."""
    return AgentSpec(
        identifier="brief-writer",
        summary="Writes marketing briefs.",
        role_description="Creates structured marketing briefs from research.",
        primary_inputs=["research documents", "brand guidelines"],
        primary_outputs=["marketing brief with citations and sources"],
        constraints=["Follow brand voice.", "Cite all sources."],
        determinism_required=True,
    )


# ---------------------------------------------------------------------------
# TaskBlock fixtures
# ---------------------------------------------------------------------------


def sample_task_block() -> TaskBlock:
    """A representative TaskBlock for use in design tests."""
    return TaskBlock(
        name="test-agent_task",
        goal="You must process user inputs and return accurate, well-formatted responses.",
        acceptance_criteria=[
            "Each response addresses the user's request directly.",
            "Responses are free from factual errors.",
            "Output format matches the specified structure.",
        ],
        constraints=[
            "You must not include personal user data in responses.",
            "You must stay within the defined scope.",
        ],
        output_format_description="Plain prose, 100-300 words.",
    )


# ---------------------------------------------------------------------------
# ExecutionPlan fixtures
# ---------------------------------------------------------------------------


def sample_execution_plan() -> ExecutionPlanBlock:
    """A three-step execution plan for Tier 2 designs."""
    return ExecutionPlanBlock(
        name="test-agent_plan",
        steps=[
            ExecutionStep(order=1, description="Read and understand the task and inputs."),
            ExecutionStep(order=2, description="Plan the response at a high level."),
            ExecutionStep(order=3, description="Produce the output and verify criteria."),
        ],
    )


# ---------------------------------------------------------------------------
# PromptDesign fixtures
# ---------------------------------------------------------------------------


def tier1_prompt_design() -> PromptDesign:
    """Tier 1 PromptDesign: task only, no plan, no rule blocks."""
    spec = minimal_agent_spec()
    return PromptDesign(
        agent_spec=spec,
        tier=PromptTier.TIER_1,
        task=TaskBlock(
            name=f"{spec.identifier}_task",
            goal=spec.summary,
            acceptance_criteria=[],
            constraints=[],
        ),
        execution_plan=None,
        rule_blocks=[],
    )


def tier2_prompt_design() -> PromptDesign:
    """Tier 2 PromptDesign: task + execution plan."""
    spec = constrained_agent_spec()
    return PromptDesign(
        agent_spec=spec,
        tier=PromptTier.TIER_2,
        task=sample_task_block(),
        execution_plan=sample_execution_plan(),
        rule_blocks=[],
    )


def tier3_prompt_design() -> PromptDesign:
    """Tier 3 PromptDesign: task + plan + rule block references."""
    spec = deterministic_agent_spec()
    return PromptDesign(
        agent_spec=spec,
        tier=PromptTier.TIER_3,
        task=sample_task_block(),
        execution_plan=sample_execution_plan(),
        rule_blocks=[
            RuleBlockRef(name="citations", path=None),
            RuleBlockRef(name="html-markup", path=None),
        ],
    )


# ---------------------------------------------------------------------------
# Evaluation fixtures
# ---------------------------------------------------------------------------


def sample_evaluation_scenario_pass() -> EvaluationScenario:
    """Scenario whose expected properties exist in a typical design."""
    return EvaluationScenario(
        identifier="scenario-pass",
        description="Agent handles standard input correctly.",
        input_example="Process this document.",
        expected_properties=["process", "accurate"],
    )


def sample_evaluation_scenario_fail() -> EvaluationScenario:
    """Scenario whose expected properties are absent from the design."""
    return EvaluationScenario(
        identifier="scenario-fail",
        description="Agent handles an edge case not covered by the design.",
        input_example="Handle this unusual case.",
        expected_properties=["quantum-entanglement-handling"],
    )


def sample_evaluation_scenario_skipped() -> EvaluationScenario:
    """Scenario with no expected properties — always skipped."""
    return EvaluationScenario(
        identifier="scenario-skipped",
        description="Placeholder scenario with no assertions.",
        input_example=None,
        expected_properties=[],
    )


def sample_evaluation_report() -> EvaluationReport:
    """Representative EvaluationReport with mixed results."""
    return EvaluationReport(
        design_identifier="test-agent",
        results=[
            EvaluationResult(
                scenario_id="scenario-pass",
                outcome=EvaluationOutcome.PASS,
                notes="All expected properties appear in task or constraints.",
            ),
            EvaluationResult(
                scenario_id="scenario-fail",
                outcome=EvaluationOutcome.FAIL,
                notes="Missing expected properties in design: quantum-entanglement-handling",
            ),
        ],
    )


# ---------------------------------------------------------------------------
# RuleBlockRegistry fixtures
# ---------------------------------------------------------------------------


def empty_registry() -> RuleBlockRegistry:
    """Registry with no rule blocks loaded."""
    return RuleBlockRegistry(rule_blocks={})


def sample_registry() -> RuleBlockRegistry:
    """Registry pre-loaded with a small set of test rule blocks."""
    blocks = {
        "citations": RuleBlock(
            name="citations",
            path=Path("/fake/rule_blocks/citations.md"),
            content="# Citation Rules\n\nUse <sup> tags for inline citations.",
        ),
        "html-markup": RuleBlock(
            name="html-markup",
            path=Path("/fake/rule_blocks/html-markup.md"),
            content="# HTML Markup Rules\n\nAllow only the listed tags.",
        ),
        "brief-json-schema": RuleBlock(
            name="brief-json-schema",
            path=Path("/fake/rule_blocks/brief-json-schema.md"),
            content="# Brief JSON Schema\n\n```json\n{}\n```",
        ),
    }
    return RuleBlockRegistry(rule_blocks=blocks)


# ---------------------------------------------------------------------------
# Markdown spec fixtures
# ---------------------------------------------------------------------------

MINIMAL_MARKDOWN_SPEC = """\
# Agent Spec: test-agent

## Summary

Test agent for testing purposes.

## Role

A test agent that processes inputs and produces outputs.

## Inputs

- user message

## Outputs

- processed response

## Constraints

- Do not include personal data.
"""

FULL_MARKDOWN_SPEC = """\
# Agent Spec: full-agent

## Summary

A fully-specified agent for comprehensive testing.

## Role

Senior analyst agent that reads research documents and produces JSON reports.

## Inputs

- Research documents in PDF or Markdown format
- Brand guidelines document
- User query string

## Outputs

- JSON schema output
- Citation list

## Constraints

- Output must be schema-compliant JSON.
- Do not fabricate citations.
- Stay within the defined topic scope.
"""

EMPTY_SECTIONS_MARKDOWN_SPEC = """\
# Agent Spec: sparse-agent

## Summary

## Role

## Inputs

## Outputs

## Constraints
"""

DETERMINISM_TRIGGER_MARKDOWN_SPEC = """\
# Agent Spec: structured-agent

## Summary

Generates stable format reports.

## Role

Produces deterministic, schema-compliant YAML output.

## Inputs

- raw data

## Outputs

- YAML report with stable format
"""

# ---------------------------------------------------------------------------
# LLM response fixtures (raw JSON strings as the LLM would return them)
# ---------------------------------------------------------------------------

VALID_LLM_TASK_RESPONSE = """\
{
  "goal": "You must process user inputs and return accurate, well-formatted responses.",
  "acceptance_criteria": [
    "Each response addresses the user request directly.",
    "Output is free from factual errors.",
    "Response format matches specifications.",
    "All constraints are respected."
  ],
  "constraints": [
    "You must not include personal data in any response.",
    "You must limit responses to the defined scope."
  ]
}"""

VALID_LLM_TASK_WITH_STEPS_RESPONSE = """\
{
  "goal": "You must produce a complete and accurate summary from the provided documents.",
  "acceptance_criteria": [
    "The summary covers all key points from the source documents.",
    "The summary is between 100 and 300 words.",
    "All factual claims are traceable to a source.",
    "The output satisfies the acceptance criteria defined in the task."
  ],
  "constraints": [
    "You must not fabricate information not present in the source documents.",
    "You must not exceed the defined word limit."
  ],
  "execution_steps": [
    "Read all provided documents fully before starting.",
    "Identify the top three key claims in each document.",
    "Draft a summary that integrates those claims coherently.",
    "Verify the word count and adjust if necessary.",
    "Check that every claim maps to a source before returning."
  ]
}"""

MARKDOWN_FENCED_LLM_RESPONSE = """\
```json
{
  "goal": "You must handle the task correctly.",
  "acceptance_criteria": ["Criteria one.", "Criteria two."],
  "constraints": ["Constraint one."]
}
```"""

INVALID_JSON_LLM_RESPONSE = "This is not valid JSON at all."

MISSING_GOAL_LLM_RESPONSE = """\
{
  "acceptance_criteria": ["Criteria one."],
  "constraints": ["Constraint one."]
}"""

EMPTY_GOAL_LLM_RESPONSE = """\
{
  "goal": "   ",
  "acceptance_criteria": ["Criteria one."],
  "constraints": ["Constraint one."]
}"""

JSON_ARRAY_LLM_RESPONSE = """["not", "an", "object"]"""
