"""Integration tests for the prompt design system.

These tests exercise the full workflow end-to-end:
  1. Parse a spec from Markdown.
  2. Select a tier via PatternSelector.
  3. Build a PromptDesign via the appropriate TierPattern.
  4. Optionally enrich via a mocked LLM.
  5. Persist design and rendered prompt to disk.
  6. Load from disk and verify round-trip fidelity.
  7. Evaluate against scenarios.
  8. Propose refinements from the report.
  9. Refine via mocked LLM and re-persist.

No real OpenAI calls are made; all LLM interactions are mocked.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from prompt_design_system.agents import DesignAgent, EvaluatorAgent, RefinementAgent
from prompt_design_system.cli import _render_prompt
from prompt_design_system.config import AppConfig, AppPaths
from prompt_design_system.models import (
    EvaluationScenario,
    PromptTier,
)
from prompt_design_system.patterns import PatternSelector
from prompt_design_system.rule_blocks import RuleBlockRegistry
from prompt_design_system.spec_parser import parse_agent_spec_from_markdown
from prompt_design_system.storage import ProjectStorage
from tests.fixtures.sample_data import (
    MINIMAL_MARKDOWN_SPEC,
    VALID_LLM_TASK_RESPONSE,
    VALID_LLM_TASK_WITH_STEPS_RESPONSE,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_storage(tmp_path: Path) -> ProjectStorage:
    config = AppConfig(paths=AppPaths(root_dir=tmp_path))
    return ProjectStorage(config=config)


def _make_registry(tmp_path: Path) -> RuleBlockRegistry:
    rb_dir = tmp_path / "ai_components" / "rule_blocks"
    rb_dir.mkdir(parents=True, exist_ok=True)
    (rb_dir / "citations.md").write_text("# Citation Rules", encoding="utf-8")
    (rb_dir / "html-markup.md").write_text("# HTML Rules", encoding="utf-8")
    (rb_dir / "brief-json-schema.md").write_text("# Brief Schema", encoding="utf-8")
    config = AppConfig(paths=AppPaths(root_dir=tmp_path))
    return RuleBlockRegistry.from_config(config)


def _make_spec_file(tmp_path: Path, content: str, name: str = "test-agent.agent-spec.md") -> Path:
    path = tmp_path / name
    path.write_text(content, encoding="utf-8")
    return path


def _make_mock_llm(response: str) -> MagicMock:
    client = MagicMock()
    client.generate.return_value = response
    return client


# ---------------------------------------------------------------------------
# Workflow 1: Heuristic-only design → persist → load
# ---------------------------------------------------------------------------


class TestHeuristicWorkflow:
    def test_full_heuristic_workflow(self, tmp_path: Path):
        """Parse spec → design (no LLM) → save → load produces a valid PromptDesign."""
        spec_file = _make_spec_file(tmp_path, MINIMAL_MARKDOWN_SPEC)
        registry = _make_registry(tmp_path)
        storage = _make_storage(tmp_path)

        agent_spec = parse_agent_spec_from_markdown(spec_file)
        selector = PatternSelector()
        design_agent = DesignAgent(
            pattern_selector=selector,
            rule_block_registry=registry,
            llm_client=None,
        )
        design = design_agent.create_design(agent_spec)

        # Persist.
        storage.save_design(design, overwrite=True)
        rendered = _render_prompt(design)
        storage.save_rendered_prompt(design, rendered, overwrite=True)

        # Reload and verify.
        loaded = storage.load_design(agent_spec.identifier)
        assert loaded.agent_spec.identifier == agent_spec.identifier
        assert loaded.task.goal == agent_spec.summary  # Heuristic goal equals summary.

    def test_project_directory_structure_created(self, tmp_path: Path):
        """The expected subdirectory layout is created under the project root."""
        spec_file = _make_spec_file(tmp_path, MINIMAL_MARKDOWN_SPEC)
        storage = _make_storage(tmp_path)
        registry = RuleBlockRegistry(rule_blocks={})

        spec = parse_agent_spec_from_markdown(spec_file)
        design_agent = DesignAgent(
            pattern_selector=PatternSelector(),
            rule_block_registry=registry,
            llm_client=None,
        )
        design = design_agent.create_design(spec)
        storage.save_design(design, overwrite=True)
        storage.save_rendered_prompt(design, "# Prompt\n", overwrite=True)
        storage.copy_spec_into_project(spec_file, spec.identifier)

        project_root = tmp_path / "projects" / spec.identifier
        assert (project_root / "designs" / "design.json").exists()
        assert (project_root / "prompts" / "system.md").exists()
        assert (project_root / "specs" / spec_file.name).exists()


# ---------------------------------------------------------------------------
# Workflow 2: LLM-enriched design → persist → load → verify enrichment
# ---------------------------------------------------------------------------


class TestLlmEnrichedWorkflow:
    def test_llm_enriched_design_persists_correctly(self, tmp_path: Path):
        """LLM-enriched goal survives the JSON serialisation round-trip."""
        spec_file = _make_spec_file(tmp_path, MINIMAL_MARKDOWN_SPEC, "test-agent.agent-spec.md")
        registry = RuleBlockRegistry(rule_blocks={})
        storage = _make_storage(tmp_path)
        mock_llm = _make_mock_llm(VALID_LLM_TASK_RESPONSE)

        spec = parse_agent_spec_from_markdown(spec_file)
        design_agent = DesignAgent(
            pattern_selector=PatternSelector(),
            rule_block_registry=registry,
            llm_client=mock_llm,
        )
        design = design_agent.create_design(spec)
        storage.save_design(design, overwrite=True)

        loaded = storage.load_design(spec.identifier)
        # LLM-enriched goal should NOT equal the raw spec summary.
        assert loaded.task.goal != spec.summary
        assert "process user inputs" in loaded.task.goal.lower()

    def test_llm_steps_persisted_for_tier2(self, tmp_path: Path):
        """LLM-suggested execution steps are saved and reloaded correctly."""
        # Use a spec with constraints so Tier 2 is selected.
        markdown = """\
# Agent Spec: step-agent

## Summary
Agent that tests execution steps.

## Role
A testing agent.

## Inputs
- input data

## Outputs
- summary report

## Constraints
- Keep responses concise.
"""
        spec_file = _make_spec_file(tmp_path, markdown, "step-agent.agent-spec.md")
        registry = RuleBlockRegistry(rule_blocks={})
        storage = _make_storage(tmp_path)
        mock_llm = _make_mock_llm(VALID_LLM_TASK_WITH_STEPS_RESPONSE)

        spec = parse_agent_spec_from_markdown(spec_file)
        design_agent = DesignAgent(
            pattern_selector=PatternSelector(),
            rule_block_registry=registry,
            llm_client=mock_llm,
        )
        design = design_agent.create_design(spec)
        storage.save_design(design, overwrite=True)

        loaded = storage.load_design(spec.identifier)
        assert loaded.execution_plan is not None
        assert len(loaded.execution_plan.steps) == 5  # LLM mock provides 5 steps.


# ---------------------------------------------------------------------------
# Workflow 3: Design → Evaluate → Propose Refinements
# ---------------------------------------------------------------------------


class TestEvaluationWorkflow:
    def test_evaluation_produces_report(self, tmp_path: Path):
        """Evaluating a design against scenarios returns a populated report."""
        registry = RuleBlockRegistry(rule_blocks={})
        design_agent = DesignAgent(
            pattern_selector=PatternSelector(),
            rule_block_registry=registry,
            llm_client=None,
        )
        spec_file = _make_spec_file(tmp_path, MINIMAL_MARKDOWN_SPEC)
        spec = parse_agent_spec_from_markdown(spec_file)
        design = design_agent.create_design(spec)

        scenarios = [
            EvaluationScenario(
                identifier="s1",
                description="Scenario with property in design.",
                expected_properties=["test"],
            ),
            EvaluationScenario(
                identifier="s2",
                description="Scenario with absent property.",
                expected_properties=["completely-absent-xyz"],
            ),
        ]

        evaluator = EvaluatorAgent(llm_client=None, rule_block_registry=registry)
        report = evaluator.evaluate(design, scenarios)

        assert report.design_identifier == spec.identifier
        assert len(report.results) == 2

    def test_refinement_proposal_after_failed_scenario(self, tmp_path: Path):
        """RefinementAgent proposes changes when evaluation has failures."""
        registry = RuleBlockRegistry(rule_blocks={})
        design_agent = DesignAgent(
            pattern_selector=PatternSelector(),
            rule_block_registry=registry,
            llm_client=None,
        )
        spec_file = _make_spec_file(tmp_path, MINIMAL_MARKDOWN_SPEC)
        spec = parse_agent_spec_from_markdown(spec_file)
        design = design_agent.create_design(spec)

        scenarios = [
            EvaluationScenario(
                identifier="fail-scenario",
                description="Will fail.",
                expected_properties=["impossible-requirement-abc"],
            ),
        ]

        evaluator = EvaluatorAgent(llm_client=None, rule_block_registry=registry)
        report = evaluator.evaluate(design, scenarios)

        refinement_agent = RefinementAgent()
        suggestion = refinement_agent.propose_refinements(design, report)

        assert "fail-scenario" in suggestion
        assert "impossible-requirement-abc" in suggestion

    def test_all_pass_produces_clean_message(self, tmp_path: Path):
        """RefinementAgent returns a clean message when all scenarios pass."""
        registry = RuleBlockRegistry(rule_blocks={})
        design_agent = DesignAgent(
            pattern_selector=PatternSelector(),
            rule_block_registry=registry,
            llm_client=None,
        )
        spec_file = _make_spec_file(tmp_path, MINIMAL_MARKDOWN_SPEC)
        spec = parse_agent_spec_from_markdown(spec_file)
        design = design_agent.create_design(spec)

        # Scenario with empty expected_properties always skips.
        scenarios = [
            EvaluationScenario(
                identifier="skip",
                description="No assertions.",
                expected_properties=[],
            ),
        ]

        evaluator = EvaluatorAgent(llm_client=None, rule_block_registry=registry)
        report = evaluator.evaluate(design, scenarios)

        refinement_agent = RefinementAgent()
        suggestion = refinement_agent.propose_refinements(design, report)

        assert "No structural refinements" in suggestion


# ---------------------------------------------------------------------------
# Workflow 4: Full iteration loop (design → evaluate → refine → re-evaluate)
# ---------------------------------------------------------------------------


class TestIterationWorkflow:
    def test_refine_changes_design_task(self, tmp_path: Path):
        """Refinement with a mocked LLM produces a design with a different goal."""
        spec_file = _make_spec_file(tmp_path, MINIMAL_MARKDOWN_SPEC)
        registry = RuleBlockRegistry(rule_blocks={})
        storage = _make_storage(tmp_path)

        spec = parse_agent_spec_from_markdown(spec_file)

        # Step 1: initial heuristic design.
        design_agent_heuristic = DesignAgent(
            pattern_selector=PatternSelector(),
            rule_block_registry=registry,
            llm_client=None,
        )
        original_design = design_agent_heuristic.create_design(spec)
        original_goal = original_design.task.goal
        storage.save_design(original_design, overwrite=True)

        # Step 2: refine with mocked LLM.
        mock_llm = _make_mock_llm(VALID_LLM_TASK_RESPONSE)
        design_agent_llm = DesignAgent(
            pattern_selector=PatternSelector(),
            rule_block_registry=registry,
            llm_client=mock_llm,
        )
        loaded = storage.load_design(spec.identifier)
        refined_design = design_agent_llm.refine_design(loaded, "Be more specific.")

        storage.save_design(refined_design, overwrite=True)

        # Step 3: reload refined design and verify the goal changed.
        final = storage.load_design(spec.identifier)
        assert final.task.goal != original_goal

    def test_state_does_not_leak_between_agents(self, tmp_path: Path):
        """Two separate DesignAgent instances produce independent designs."""
        spec_file_a = _make_spec_file(tmp_path, MINIMAL_MARKDOWN_SPEC, "agent-a.agent-spec.md")
        spec_b_content = MINIMAL_MARKDOWN_SPEC.replace("Test agent", "Another agent")
        spec_file_b = _make_spec_file(tmp_path, spec_b_content, "agent-b.agent-spec.md")

        registry = RuleBlockRegistry(rule_blocks={})
        selector = PatternSelector()

        agent_a = DesignAgent(
            pattern_selector=selector,
            rule_block_registry=registry,
            llm_client=None,
        )
        agent_b = DesignAgent(
            pattern_selector=selector,
            rule_block_registry=registry,
            llm_client=None,
        )

        spec_a = parse_agent_spec_from_markdown(spec_file_a)
        spec_b = parse_agent_spec_from_markdown(spec_file_b)

        design_a = agent_a.create_design(spec_a)
        design_b = agent_b.create_design(spec_b)

        assert design_a.agent_spec.identifier != design_b.agent_spec.identifier
        assert design_a.task.goal != design_b.task.goal


# ---------------------------------------------------------------------------
# Workflow 5: Tier 3 design with rule block attachment
# ---------------------------------------------------------------------------


class TestTier3WithRuleBlocks:
    def test_tier3_design_has_rule_block_refs(self, tmp_path: Path):
        """A spec that triggers Tier 3 gets rule blocks attached from the registry."""
        markdown = """\
# Agent Spec: brief-writer

## Summary
Writes marketing briefs with citations.

## Role
Produces structured marketing briefs.

## Inputs
- research data

## Outputs
- JSON schema output with citations and sources

## Constraints
- Cite all sources.
"""
        spec_file = _make_spec_file(tmp_path, markdown, "brief-writer.agent-spec.md")
        registry = _make_registry(tmp_path)
        spec = parse_agent_spec_from_markdown(spec_file)

        design_agent = DesignAgent(
            pattern_selector=PatternSelector(),
            rule_block_registry=registry,
            llm_client=None,
        )
        design = design_agent.create_design(spec)

        assert design.tier is PromptTier.TIER_3
        rule_names = {ref.name for ref in design.rule_blocks}
        assert "citations" in rule_names

    def test_rendered_tier3_prompt_includes_rule_block_names(self, tmp_path: Path):
        """The rendered prompt for a Tier 3 design lists all rule block names."""
        markdown = """\
# Agent Spec: brief-writer

## Summary
Writes briefs.

## Role
Brief writer.

## Inputs
- data

## Outputs
- JSON schema output with citations

## Constraints
- Cite everything.
"""
        spec_file = _make_spec_file(tmp_path, markdown, "brief-writer.agent-spec.md")
        registry = _make_registry(tmp_path)
        spec = parse_agent_spec_from_markdown(spec_file)

        design_agent = DesignAgent(
            pattern_selector=PatternSelector(),
            rule_block_registry=registry,
            llm_client=None,
        )
        design = design_agent.create_design(spec)
        rendered = _render_prompt(design)

        assert "## Rule Blocks" in rendered
        for ref in design.rule_blocks:
            assert ref.name in rendered
