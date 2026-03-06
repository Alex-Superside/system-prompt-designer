"""Tests for prompt_design_system.models.

Covers Pydantic validation, default values, serialisation round-trips,
and the Enum members used throughout the domain.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

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

# ---------------------------------------------------------------------------
# PromptTier enum
# ---------------------------------------------------------------------------


class TestPromptTier:
    def test_tier_values_are_strings(self):
        """Verify PromptTier members expose stable string values."""
        assert PromptTier.TIER_1.value == "tier_1"
        assert PromptTier.TIER_2.value == "tier_2"
        assert PromptTier.TIER_3.value == "tier_3"

    def test_tier_from_string(self):
        """PromptTier can be constructed from its string value."""
        assert PromptTier("tier_1") is PromptTier.TIER_1
        assert PromptTier("tier_3") is PromptTier.TIER_3

    def test_invalid_tier_raises(self):
        """An unknown string raises ValueError on construction."""
        with pytest.raises(ValueError):
            PromptTier("tier_99")


# ---------------------------------------------------------------------------
# TaskBlock
# ---------------------------------------------------------------------------


class TestTaskBlock:
    def test_required_fields(self):
        """TaskBlock requires 'name' and 'goal'."""
        block = TaskBlock(name="my_task", goal="Achieve something measurable.")
        assert block.name == "my_task"
        assert block.goal == "Achieve something measurable."

    def test_defaults(self):
        """acceptance_criteria and constraints default to empty lists."""
        block = TaskBlock(name="t", goal="g")
        assert block.acceptance_criteria == []
        assert block.constraints == []
        assert block.output_format_description is None

    def test_missing_name_raises(self):
        """Omitting 'name' raises ValidationError."""
        with pytest.raises(ValidationError):
            TaskBlock(goal="A goal without a name.")  # type: ignore[call-arg]

    def test_missing_goal_raises(self):
        """Omitting 'goal' raises ValidationError."""
        with pytest.raises(ValidationError):
            TaskBlock(name="some_task")  # type: ignore[call-arg]

    def test_optional_output_format(self):
        """output_format_description can be set to a non-None string."""
        block = TaskBlock(name="t", goal="g", output_format_description="JSON object.")
        assert block.output_format_description == "JSON object."

    def test_serialisation_round_trip(self):
        """model_dump / model_validate round-trip preserves all field values."""
        original = TaskBlock(
            name="round-trip",
            goal="Test round trip.",
            acceptance_criteria=["Criterion A"],
            constraints=["No personal data."],
            output_format_description="Markdown.",
        )
        data = original.model_dump()
        restored = TaskBlock.model_validate(data)
        assert restored == original

    def test_json_schema_is_generated(self):
        """model_json_schema() returns a non-empty dict."""
        schema = TaskBlock.model_json_schema()
        assert isinstance(schema, dict)
        assert "properties" in schema


# ---------------------------------------------------------------------------
# ExecutionStep
# ---------------------------------------------------------------------------


class TestExecutionStep:
    def test_required_fields(self):
        """ExecutionStep requires 'order' and 'description'."""
        step = ExecutionStep(order=1, description="Do the first thing.")
        assert step.order == 1
        assert step.description == "Do the first thing."

    def test_missing_order_raises(self):
        """Omitting 'order' raises ValidationError."""
        with pytest.raises(ValidationError):
            ExecutionStep(description="step without order")  # type: ignore[call-arg]

    def test_order_must_be_int(self):
        """Providing a non-numeric order raises ValidationError."""
        with pytest.raises(ValidationError):
            ExecutionStep(order="first", description="step")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# ExecutionPlanBlock
# ---------------------------------------------------------------------------


class TestExecutionPlanBlock:
    def test_required_name(self):
        """ExecutionPlanBlock requires a 'name'."""
        plan = ExecutionPlanBlock(name="my_plan")
        assert plan.name == "my_plan"
        assert plan.steps == []

    def test_steps_list(self):
        """Steps list is stored and accessible."""
        steps = [ExecutionStep(order=1, description="Step one.")]
        plan = ExecutionPlanBlock(name="plan", steps=steps)
        assert len(plan.steps) == 1
        assert plan.steps[0].order == 1


# ---------------------------------------------------------------------------
# RuleBlockRef
# ---------------------------------------------------------------------------


class TestRuleBlockRef:
    def test_name_required(self):
        """RuleBlockRef requires a 'name'."""
        ref = RuleBlockRef(name="citations")
        assert ref.name == "citations"
        assert ref.path is None

    def test_optional_path(self):
        """path can be set as a Path object."""
        ref = RuleBlockRef(name="html-markup", path=Path("/some/path.md"))
        assert ref.path == Path("/some/path.md")

    def test_missing_name_raises(self):
        """Omitting 'name' raises ValidationError."""
        with pytest.raises(ValidationError):
            RuleBlockRef()  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# AgentSpec
# ---------------------------------------------------------------------------


class TestAgentSpec:
    def test_required_fields(self):
        """AgentSpec requires identifier, summary, and role_description."""
        spec = AgentSpec(
            identifier="my-agent",
            summary="Does things.",
            role_description="It is an agent.",
        )
        assert spec.identifier == "my-agent"

    def test_defaults(self):
        """List fields and determinism_required default correctly."""
        spec = AgentSpec(
            identifier="a",
            summary="s",
            role_description="r",
        )
        assert spec.primary_inputs == []
        assert spec.primary_outputs == []
        assert spec.constraints == []
        assert spec.determinism_required is False

    def test_determinism_flag(self):
        """determinism_required can be set to True explicitly."""
        spec = AgentSpec(
            identifier="a",
            summary="s",
            role_description="r",
            determinism_required=True,
        )
        assert spec.determinism_required is True

    def test_missing_identifier_raises(self):
        """Omitting identifier raises ValidationError."""
        with pytest.raises(ValidationError):
            AgentSpec(summary="s", role_description="r")  # type: ignore[call-arg]

    def test_json_serialisation(self):
        """model_dump_json produces valid JSON parseable back to a dict."""
        spec = AgentSpec(
            identifier="json-test",
            summary="Test",
            role_description="Role",
            primary_inputs=["input"],
            primary_outputs=["output"],
        )
        raw = spec.model_dump_json()
        parsed = json.loads(raw)
        assert parsed["identifier"] == "json-test"
        assert parsed["primary_inputs"] == ["input"]


# ---------------------------------------------------------------------------
# PromptDesign
# ---------------------------------------------------------------------------


class TestPromptDesign:
    def test_minimal_construction(self, sample_agent_spec):
        """PromptDesign requires agent_spec, tier, and task."""
        task = TaskBlock(name="t", goal="g")
        design = PromptDesign(
            agent_spec=sample_agent_spec,
            tier=PromptTier.TIER_1,
            task=task,
        )
        assert design.tier is PromptTier.TIER_1
        assert design.execution_plan is None
        assert design.rule_blocks == []

    def test_with_all_fields(self, sample_agent_spec):
        """PromptDesign accepts execution_plan and rule_blocks."""
        plan = ExecutionPlanBlock(
            name="plan",
            steps=[ExecutionStep(order=1, description="Step one.")],
        )
        refs = [RuleBlockRef(name="citations")]
        task = TaskBlock(name="t", goal="g")
        design = PromptDesign(
            agent_spec=sample_agent_spec,
            tier=PromptTier.TIER_3,
            task=task,
            execution_plan=plan,
            rule_blocks=refs,
        )
        assert len(design.execution_plan.steps) == 1
        assert design.rule_blocks[0].name == "citations"

    def test_json_round_trip(self, sample_design):
        """model_dump_json / model_validate_json preserves a PromptDesign."""
        raw = sample_design.model_dump_json(indent=2)
        restored = PromptDesign.model_validate_json(raw)
        assert restored.agent_spec.identifier == sample_design.agent_spec.identifier
        assert restored.tier == sample_design.tier
        assert restored.task.goal == sample_design.task.goal

    def test_missing_agent_spec_raises(self):
        """Omitting agent_spec raises ValidationError."""
        with pytest.raises(ValidationError):
            PromptDesign(  # type: ignore[call-arg]
                tier=PromptTier.TIER_1,
                task=TaskBlock(name="t", goal="g"),
            )


# ---------------------------------------------------------------------------
# EvaluationOutcome enum
# ---------------------------------------------------------------------------


class TestEvaluationOutcome:
    def test_outcome_values(self):
        """EvaluationOutcome has the three expected string values."""
        assert EvaluationOutcome.PASS.value == "pass"
        assert EvaluationOutcome.FAIL.value == "fail"
        assert EvaluationOutcome.SKIPPED.value == "skipped"


# ---------------------------------------------------------------------------
# EvaluationScenario
# ---------------------------------------------------------------------------


class TestEvaluationScenario:
    def test_required_fields(self):
        """EvaluationScenario requires identifier and description."""
        scenario = EvaluationScenario(
            identifier="s1",
            description="Test scenario.",
        )
        assert scenario.identifier == "s1"
        assert scenario.expected_properties == []
        assert scenario.input_example is None

    def test_missing_identifier_raises(self):
        """Omitting identifier raises ValidationError."""
        with pytest.raises(ValidationError):
            EvaluationScenario(description="desc")  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# EvaluationReport
# ---------------------------------------------------------------------------


class TestEvaluationReport:
    def test_construction(self):
        """EvaluationReport holds design_identifier and a results list."""
        report = EvaluationReport(
            design_identifier="my-agent",
            results=[
                EvaluationResult(
                    scenario_id="s1",
                    outcome=EvaluationOutcome.PASS,
                    notes="Passed.",
                ),
            ],
        )
        assert report.design_identifier == "my-agent"
        assert len(report.results) == 1
        assert report.results[0].outcome is EvaluationOutcome.PASS

    def test_json_serialisation(self):
        """EvaluationReport round-trips through JSON correctly."""
        report = EvaluationReport(
            design_identifier="agent",
            results=[
                EvaluationResult(
                    scenario_id="s",
                    outcome=EvaluationOutcome.FAIL,
                    notes="Failed.",
                )
            ],
        )
        raw = report.model_dump_json()
        parsed = json.loads(raw)
        assert parsed["design_identifier"] == "agent"
        assert parsed["results"][0]["outcome"] == "fail"
