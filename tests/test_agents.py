"""Tests for prompt_design_system.agents.

Covers DesignAgent (heuristic and LLM-enriched modes), EvaluatorAgent,
RefinementAgent, and the private parsing/composition helpers.
"""

from __future__ import annotations

import json

from prompt_design_system.agents import (
    DesignAgent,
    EvaluatorAgent,
    RefinementAgent,
    _build_llm_prompt,
    _build_refinement_llm_prompt,
    _parse_llm_task_enrichment,
)
from prompt_design_system.models import (
    EvaluationOutcome,
    EvaluationScenario,
    ExecutionStep,
    PromptDesign,
    PromptTier,
    TaskBlock,
)
from prompt_design_system.patterns import PatternSelector
from tests.fixtures.sample_data import (
    EMPTY_GOAL_LLM_RESPONSE,
    INVALID_JSON_LLM_RESPONSE,
    JSON_ARRAY_LLM_RESPONSE,
    MARKDOWN_FENCED_LLM_RESPONSE,
    MISSING_GOAL_LLM_RESPONSE,
    VALID_LLM_TASK_RESPONSE,
    VALID_LLM_TASK_WITH_STEPS_RESPONSE,
    minimal_agent_spec,
    sample_task_block,
    tier2_prompt_design,
)

# ---------------------------------------------------------------------------
# _build_llm_prompt helper
# ---------------------------------------------------------------------------


class TestBuildLlmPrompt:
    def test_contains_role_and_summary(self):
        """Prompt text includes the agent role and summary."""
        spec = minimal_agent_spec()
        prompt = _build_llm_prompt(spec, PromptTier.TIER_1, [])
        assert spec.role_description in prompt
        assert spec.summary in prompt

    def test_tier1_has_no_execution_steps_instruction(self):
        """Tier 1 prompt does not ask the LLM for execution_steps."""
        spec = minimal_agent_spec()
        prompt = _build_llm_prompt(spec, PromptTier.TIER_1, [])
        assert "execution_steps" not in prompt

    def test_tier2_requests_execution_steps(self):
        """Tier 2 prompt explicitly requests execution_steps in JSON."""
        spec = minimal_agent_spec()
        prompt = _build_llm_prompt(spec, PromptTier.TIER_2, [])
        assert "execution_steps" in prompt

    def test_tier3_requests_execution_steps(self):
        """Tier 3 prompt also requests execution_steps."""
        spec = minimal_agent_spec()
        prompt = _build_llm_prompt(spec, PromptTier.TIER_3, [])
        assert "execution_steps" in prompt

    def test_rule_block_names_appear_in_prompt(self):
        """Named rule blocks are listed in the prompt."""
        spec = minimal_agent_spec()
        prompt = _build_llm_prompt(spec, PromptTier.TIER_3, ["citations", "html-markup"])
        assert "citations" in prompt
        assert "html-markup" in prompt

    def test_no_rule_blocks_shows_none(self):
        """When no rule blocks are provided, the prompt says (none)."""
        spec = minimal_agent_spec()
        prompt = _build_llm_prompt(spec, PromptTier.TIER_1, [])
        assert "(none)" in prompt

    def test_returns_string(self):
        """The helper always returns a non-empty string."""
        spec = minimal_agent_spec()
        result = _build_llm_prompt(spec, PromptTier.TIER_2, [])
        assert isinstance(result, str)
        assert len(result) > 0


# ---------------------------------------------------------------------------
# _build_refinement_llm_prompt helper
# ---------------------------------------------------------------------------


class TestBuildRefinementLlmPrompt:
    def test_includes_feedback(self):
        """The refinement prompt contains the user's feedback verbatim."""
        design = tier2_prompt_design()
        feedback = "Make the constraints more specific about data handling."
        prompt = _build_refinement_llm_prompt(design, feedback)
        assert feedback in prompt

    def test_includes_current_goal(self):
        """The current design's goal appears in the refinement prompt."""
        design = tier2_prompt_design()
        prompt = _build_refinement_llm_prompt(design, "some feedback")
        assert design.task.goal in prompt

    def test_tier2_requests_steps(self):
        """Tier 2 refinement prompt requests execution_steps."""
        design = tier2_prompt_design()
        prompt = _build_refinement_llm_prompt(design, "feedback")
        assert "execution_steps" in prompt

    def test_tier1_no_steps(self):
        """Tier 1 refinement prompt does not request execution_steps."""
        from tests.fixtures.sample_data import tier1_prompt_design

        design = tier1_prompt_design()
        prompt = _build_refinement_llm_prompt(design, "feedback")
        assert "execution_steps" not in prompt


# ---------------------------------------------------------------------------
# _parse_llm_task_enrichment helper
# ---------------------------------------------------------------------------


class TestParseLlmTaskEnrichment:
    def _fallback(self) -> TaskBlock:
        return sample_task_block()

    def test_valid_json_extracts_goal(self):
        """Valid JSON response produces a TaskBlock with the LLM goal."""
        task, steps = _parse_llm_task_enrichment(VALID_LLM_TASK_RESPONSE, self._fallback(), False)
        assert "process user inputs" in task.goal.lower()

    def test_valid_json_extracts_criteria(self):
        """Valid JSON response includes acceptance_criteria from the LLM."""
        task, _ = _parse_llm_task_enrichment(VALID_LLM_TASK_RESPONSE, self._fallback(), False)
        assert len(task.acceptance_criteria) > 0

    def test_valid_json_extracts_constraints(self):
        """Valid JSON response includes constraints from the LLM."""
        task, _ = _parse_llm_task_enrichment(VALID_LLM_TASK_RESPONSE, self._fallback(), False)
        assert len(task.constraints) > 0

    def test_steps_extracted_when_wants_steps_true(self):
        """Execution steps are parsed when wants_steps is True."""
        _, steps = _parse_llm_task_enrichment(
            VALID_LLM_TASK_WITH_STEPS_RESPONSE, self._fallback(), True
        )
        assert len(steps) > 0
        assert all(isinstance(s, ExecutionStep) for s in steps)

    def test_steps_not_extracted_when_wants_steps_false(self):
        """Execution steps are ignored when wants_steps is False."""
        _, steps = _parse_llm_task_enrichment(
            VALID_LLM_TASK_WITH_STEPS_RESPONSE, self._fallback(), False
        )
        assert steps == []

    def test_steps_have_sequential_order(self):
        """Extracted steps are numbered starting at 1."""
        _, steps = _parse_llm_task_enrichment(
            VALID_LLM_TASK_WITH_STEPS_RESPONSE, self._fallback(), True
        )
        orders = [s.order for s in steps]
        assert orders == list(range(1, len(orders) + 1))

    def test_markdown_fence_stripped_before_parsing(self):
        """A markdown-fenced JSON response is parsed correctly."""
        task, _ = _parse_llm_task_enrichment(MARKDOWN_FENCED_LLM_RESPONSE, self._fallback(), False)
        assert task.goal == "You must handle the task correctly."

    def test_invalid_json_falls_back(self):
        """Non-JSON response returns the fallback TaskBlock unchanged."""
        fallback = self._fallback()
        task, steps = _parse_llm_task_enrichment(INVALID_JSON_LLM_RESPONSE, fallback, False)
        assert task is fallback
        assert steps == []

    def test_json_array_falls_back(self):
        """A JSON array (not object) returns the fallback TaskBlock."""
        fallback = self._fallback()
        task, steps = _parse_llm_task_enrichment(JSON_ARRAY_LLM_RESPONSE, fallback, False)
        assert task is fallback

    def test_missing_goal_falls_back(self):
        """A JSON object with no 'goal' key returns the fallback TaskBlock."""
        fallback = self._fallback()
        task, _ = _parse_llm_task_enrichment(MISSING_GOAL_LLM_RESPONSE, fallback, False)
        assert task is fallback

    def test_empty_goal_falls_back(self):
        """A goal that is whitespace-only returns the fallback TaskBlock."""
        fallback = self._fallback()
        task, _ = _parse_llm_task_enrichment(EMPTY_GOAL_LLM_RESPONSE, fallback, False)
        assert task is fallback

    def test_fallback_name_preserved(self):
        """Even when LLM enriches content, the original task name is kept."""
        fallback = self._fallback()
        task, _ = _parse_llm_task_enrichment(VALID_LLM_TASK_RESPONSE, fallback, False)
        assert task.name == fallback.name

    def test_fallback_criteria_used_when_missing(self):
        """When 'acceptance_criteria' is absent, fallback list is preserved."""
        raw = json.dumps({"goal": "Some goal.", "constraints": ["c1"]})
        fallback = self._fallback()
        task, _ = _parse_llm_task_enrichment(raw, fallback, False)
        assert task.acceptance_criteria == fallback.acceptance_criteria


# ---------------------------------------------------------------------------
# DesignAgent — heuristic mode
# ---------------------------------------------------------------------------


class TestDesignAgentHeuristic:
    def _make_agent(self, registry=None):
        from tests.fixtures.sample_data import empty_registry

        return DesignAgent(
            pattern_selector=PatternSelector(),
            rule_block_registry=registry or empty_registry(),
            llm_client=None,
        )

    def test_returns_prompt_design(self, sample_agent_spec):
        """create_design() returns a PromptDesign regardless of spec."""
        agent = self._make_agent()
        result = agent.create_design(sample_agent_spec)
        assert isinstance(result, PromptDesign)

    def test_tier1_selected_for_minimal_spec(self, sample_agent_spec):
        """A spec with no constraints and no determinism gets Tier 1."""
        agent = self._make_agent()
        result = agent.create_design(sample_agent_spec)
        assert result.tier is PromptTier.TIER_1

    def test_tier2_selected_for_constrained_spec(self, constrained_spec):
        """A spec with constraints gets Tier 2."""
        agent = self._make_agent()
        result = agent.create_design(constrained_spec)
        assert result.tier is PromptTier.TIER_2

    def test_tier3_selected_for_deterministic_spec(self, deterministic_spec):
        """A spec with determinism_required=True gets Tier 3."""
        agent = self._make_agent()
        result = agent.create_design(deterministic_spec)
        assert result.tier is PromptTier.TIER_3

    def test_explicit_tier_overrides_auto(self, sample_agent_spec):
        """Passing explicit_tier bypasses tier auto-selection."""
        agent = self._make_agent()
        result = agent.create_design(sample_agent_spec, explicit_tier="tier_3")
        assert result.tier is PromptTier.TIER_3

    def test_design_task_name_includes_identifier(self, sample_agent_spec):
        """The task name is derived from the agent identifier."""
        agent = self._make_agent()
        result = agent.create_design(sample_agent_spec)
        assert sample_agent_spec.identifier in result.task.name

    def test_no_llm_client_means_heuristic_only(self, sample_agent_spec):
        """Without an LLM client, the design reflects the heuristic scaffold."""
        agent = self._make_agent()
        result = agent.create_design(sample_agent_spec)
        # The heuristic goal is the spec's summary verbatim.
        assert result.task.goal == sample_agent_spec.summary

    def test_stateless_across_calls(self, sample_agent_spec, constrained_spec):
        """Two calls with different specs produce independent results."""
        agent = self._make_agent()
        r1 = agent.create_design(sample_agent_spec)
        r2 = agent.create_design(constrained_spec)
        assert r1.agent_spec.identifier != r2.agent_spec.identifier
        assert r1.tier != r2.tier


# ---------------------------------------------------------------------------
# DesignAgent — LLM-enriched mode
# ---------------------------------------------------------------------------


class TestDesignAgentWithLlm:
    def _make_agent(self, mock_client, registry=None):
        from tests.fixtures.sample_data import empty_registry

        return DesignAgent(
            pattern_selector=PatternSelector(),
            rule_block_registry=registry or empty_registry(),
            llm_client=mock_client,
        )

    def test_llm_generate_is_called(self, sample_agent_spec, mock_llm_client):
        """The LLM client's generate() is invoked exactly once."""
        agent = self._make_agent(mock_llm_client)
        agent.create_design(sample_agent_spec)
        mock_llm_client.generate.assert_called_once()

    def test_llm_enriches_goal(self, constrained_spec, mock_llm_client):
        """The design goal reflects the LLM response, not the raw summary."""
        agent = self._make_agent(mock_llm_client)
        result = agent.create_design(constrained_spec)
        # The mock returns VALID_LLM_TASK_RESPONSE whose goal differs from the spec summary.
        assert result.task.goal != constrained_spec.summary

    def test_llm_enriches_execution_steps_for_tier2(
        self, constrained_spec, mock_llm_client_with_steps
    ):
        """For Tier 2, LLM-suggested steps replace the heuristic steps."""
        agent = self._make_agent(mock_llm_client_with_steps)
        result = agent.create_design(constrained_spec)
        assert result.execution_plan is not None
        # The mock provides 5 steps; verify they were applied.
        assert len(result.execution_plan.steps) == 5

    def test_llm_failure_returns_heuristic_design(self, constrained_spec, mock_llm_client_failing):
        """When the LLM call raises RuntimeError, the heuristic design is returned."""
        agent = self._make_agent(mock_llm_client_failing)
        result = agent.create_design(constrained_spec)
        # Heuristic goal equals the spec summary.
        assert result.task.goal == constrained_spec.summary

    def test_prompt_sent_to_llm_contains_spec_data(self, sample_agent_spec, mock_llm_client):
        """The prompt sent to the LLM references the spec's role and summary."""
        agent = self._make_agent(mock_llm_client)
        agent.create_design(sample_agent_spec)
        call_args = mock_llm_client.generate.call_args
        prompt_text = call_args[0][0]
        assert sample_agent_spec.role_description in prompt_text


# ---------------------------------------------------------------------------
# DesignAgent.refine_design()
# ---------------------------------------------------------------------------


class TestDesignAgentRefine:
    def _make_agent(self, mock_client):
        from tests.fixtures.sample_data import empty_registry

        return DesignAgent(
            pattern_selector=PatternSelector(),
            rule_block_registry=empty_registry(),
            llm_client=mock_client,
        )

    def test_refine_calls_llm(self, mock_llm_client):
        """refine_design() invokes the LLM client once."""
        agent = self._make_agent(mock_llm_client)
        design = tier2_prompt_design()
        agent.refine_design(design, "Make constraints tighter.")
        mock_llm_client.generate.assert_called_once()

    def test_refine_returns_prompt_design(self, mock_llm_client):
        """refine_design() always returns a PromptDesign."""
        agent = self._make_agent(mock_llm_client)
        result = agent.refine_design(tier2_prompt_design(), "feedback")
        assert isinstance(result, PromptDesign)

    def test_refine_updates_acceptance_criteria(self, mock_llm_client):
        """The refined design's acceptance_criteria comes from the LLM response."""
        agent = self._make_agent(mock_llm_client)
        original = tier2_prompt_design()
        refined = agent.refine_design(original, "feedback")
        # LLM mock returns VALID_LLM_TASK_RESPONSE which has different criteria to the fixture.
        assert refined.task.acceptance_criteria != original.task.acceptance_criteria

    def test_refine_without_llm_returns_original(self):
        """refine_design() without an LLM client returns the design unchanged."""
        from tests.fixtures.sample_data import empty_registry

        agent = DesignAgent(
            pattern_selector=PatternSelector(),
            rule_block_registry=empty_registry(),
            llm_client=None,
        )
        design = tier2_prompt_design()
        result = agent.refine_design(design, "some feedback")
        assert result is design

    def test_refine_on_llm_failure_returns_original(self, mock_llm_client_failing):
        """When the LLM call fails during refinement, the original design is returned."""
        agent = self._make_agent(mock_llm_client_failing)
        design = tier2_prompt_design()
        result = agent.refine_design(design, "feedback")
        assert result.task.goal == design.task.goal

    def test_refinement_prompt_contains_feedback(self, mock_llm_client):
        """The prompt sent to the LLM contains the user's feedback."""
        agent = self._make_agent(mock_llm_client)
        feedback = "Be more specific about the output schema."
        agent.refine_design(tier2_prompt_design(), feedback)
        call_args = mock_llm_client.generate.call_args
        prompt_text = call_args[0][0]
        assert feedback in prompt_text


# ---------------------------------------------------------------------------
# EvaluatorAgent
# ---------------------------------------------------------------------------


class TestEvaluatorAgent:
    def _make_evaluator(self, registry=None):
        from tests.fixtures.sample_data import empty_registry

        return EvaluatorAgent(
            llm_client=None,
            rule_block_registry=registry or empty_registry(),
        )

    def test_evaluate_returns_report(self, sample_design, sample_scenarios):
        """evaluate() returns an EvaluationReport."""
        evaluator = self._make_evaluator()
        report = evaluator.evaluate(sample_design, sample_scenarios)
        from prompt_design_system.models import EvaluationReport

        assert isinstance(report, EvaluationReport)

    def test_report_design_identifier_matches(self, sample_design, sample_scenarios):
        """The report's design_identifier matches the spec identifier."""
        evaluator = self._make_evaluator()
        report = evaluator.evaluate(sample_design, sample_scenarios)
        assert report.design_identifier == sample_design.agent_spec.identifier

    def test_result_count_matches_scenario_count(self, sample_design, sample_scenarios):
        """One EvaluationResult is produced per scenario."""
        evaluator = self._make_evaluator()
        report = evaluator.evaluate(sample_design, sample_scenarios)
        assert len(report.results) == len(sample_scenarios)

    def test_skipped_outcome_for_empty_properties(self, sample_design):
        """A scenario with no expected_properties yields SKIPPED."""
        evaluator = self._make_evaluator()
        scenario = EvaluationScenario(
            identifier="empty",
            description="No assertions.",
            expected_properties=[],
        )
        report = evaluator.evaluate(sample_design, [scenario])
        assert report.results[0].outcome is EvaluationOutcome.SKIPPED

    def test_fail_outcome_for_absent_property(self, sample_design):
        """A scenario whose expected property is absent in the design yields FAIL."""
        evaluator = self._make_evaluator()
        scenario = EvaluationScenario(
            identifier="absent",
            description="Missing property.",
            expected_properties=["absolutely-not-in-the-design-xyz"],
        )
        report = evaluator.evaluate(sample_design, [scenario])
        assert report.results[0].outcome is EvaluationOutcome.FAIL

    def test_pass_outcome_when_property_present(self, sample_design):
        """A scenario whose property appears in the design's task yields PASS."""
        evaluator = self._make_evaluator()
        # Use a word that appears in the standard task block goal.
        keyword = sample_design.task.goal.split()[0].lower()
        scenario = EvaluationScenario(
            identifier="present",
            description="Property exists.",
            expected_properties=[keyword],
        )
        report = evaluator.evaluate(sample_design, [scenario])
        assert report.results[0].outcome is EvaluationOutcome.PASS

    def test_empty_scenario_list_returns_empty_results(self, sample_design):
        """evaluate() with no scenarios returns an empty results list."""
        evaluator = self._make_evaluator()
        report = evaluator.evaluate(sample_design, [])
        assert report.results == []

    def test_fail_notes_identify_missing_property(self, sample_design):
        """FAIL notes mention the specific missing property name."""
        evaluator = self._make_evaluator()
        scenario = EvaluationScenario(
            identifier="fail-notes",
            description="Missing property.",
            expected_properties=["unicorn-feature"],
        )
        report = evaluator.evaluate(sample_design, [scenario])
        assert "unicorn-feature" in report.results[0].notes


# ---------------------------------------------------------------------------
# RefinementAgent
# ---------------------------------------------------------------------------


class TestRefinementAgent:
    def _make_refinement_agent(self) -> RefinementAgent:
        return RefinementAgent()

    def test_all_passed_returns_clean_message(self):
        """No failures returns the 'no refinements suggested' message."""
        from prompt_design_system.models import EvaluationReport, EvaluationResult

        report = EvaluationReport(
            design_identifier="agent",
            results=[
                EvaluationResult(
                    scenario_id="s1",
                    outcome=EvaluationOutcome.PASS,
                    notes="Passed.",
                )
            ],
        )
        agent = self._make_refinement_agent()
        message = agent.propose_refinements(tier2_prompt_design(), report)
        assert "No structural refinements" in message

    def test_failed_scenarios_appear_in_output(self):
        """Failed scenario IDs and notes appear in the refinement suggestion."""
        from prompt_design_system.models import EvaluationReport, EvaluationResult

        report = EvaluationReport(
            design_identifier="agent",
            results=[
                EvaluationResult(
                    scenario_id="bad-scenario",
                    outcome=EvaluationOutcome.FAIL,
                    notes="Missing: some-property",
                )
            ],
        )
        agent = self._make_refinement_agent()
        message = agent.propose_refinements(tier2_prompt_design(), report)
        assert "bad-scenario" in message
        assert "some-property" in message

    def test_suggests_criteria_update(self):
        """Refinement message recommends updating acceptance criteria."""
        from prompt_design_system.models import EvaluationReport, EvaluationResult

        report = EvaluationReport(
            design_identifier="a",
            results=[
                EvaluationResult(
                    scenario_id="s",
                    outcome=EvaluationOutcome.FAIL,
                    notes="Missing.",
                )
            ],
        )
        agent = self._make_refinement_agent()
        message = agent.propose_refinements(tier2_prompt_design(), report)
        assert "acceptance criteria" in message.lower()

    def test_only_failed_mentioned(self):
        """Passed and skipped scenarios do not appear in refinement output."""
        from prompt_design_system.models import EvaluationReport, EvaluationResult

        report = EvaluationReport(
            design_identifier="a",
            results=[
                EvaluationResult(
                    scenario_id="pass-scenario",
                    outcome=EvaluationOutcome.PASS,
                    notes="ok",
                ),
                EvaluationResult(
                    scenario_id="fail-scenario",
                    outcome=EvaluationOutcome.FAIL,
                    notes="Missing something.",
                ),
            ],
        )
        agent = self._make_refinement_agent()
        message = agent.propose_refinements(tier2_prompt_design(), report)
        assert "pass-scenario" not in message
        assert "fail-scenario" in message
