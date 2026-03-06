"""Tests for prompt_design_system.patterns.

Covers PatternSelector tier selection logic, all three TierPattern.build()
implementations, and the rule-block auto-attachment heuristic.
"""

from __future__ import annotations

from prompt_design_system.models import (
    AgentSpec,
    ExecutionPlanBlock,
    PromptDesign,
    PromptTier,
)
from prompt_design_system.patterns import (
    PatternSelector,
    Tier1Pattern,
    Tier2Pattern,
    Tier3Pattern,
)
from tests.fixtures.sample_data import (
    brief_agent_spec,
    constrained_agent_spec,
    deterministic_agent_spec,
    empty_registry,
    minimal_agent_spec,
    sample_registry,
    structured_output_agent_spec,
)

# ---------------------------------------------------------------------------
# PatternSelector.choose_tier()
# ---------------------------------------------------------------------------


class TestPatternSelectorChooseTier:
    def test_no_constraints_no_determinism_gives_tier1(self):
        """Minimal spec with no constraints and no structured output selects Tier 1."""
        selector = PatternSelector()
        spec = minimal_agent_spec()
        assert selector.choose_tier(spec) is PromptTier.TIER_1

    def test_constraints_give_tier2(self):
        """Spec with at least one constraint selects Tier 2."""
        selector = PatternSelector()
        spec = constrained_agent_spec()
        assert selector.choose_tier(spec) is PromptTier.TIER_2

    def test_determinism_required_gives_tier3(self):
        """determinism_required=True overrides everything and gives Tier 3."""
        selector = PatternSelector()
        spec = deterministic_agent_spec()
        assert selector.choose_tier(spec) is PromptTier.TIER_3

    def test_json_in_outputs_gives_tier3(self):
        """The word 'json' in primary_outputs selects Tier 3."""
        selector = PatternSelector()
        spec = structured_output_agent_spec()
        assert selector.choose_tier(spec) is PromptTier.TIER_3

    def test_schema_keyword_gives_tier3(self):
        """The word 'schema' in primary_outputs selects Tier 3."""
        selector = PatternSelector()
        spec = AgentSpec(
            identifier="schema-agent",
            summary="s",
            role_description="r",
            primary_outputs=["schema validation result"],
        )
        assert selector.choose_tier(spec) is PromptTier.TIER_3

    def test_yaml_keyword_gives_tier3(self):
        """The word 'yaml' in primary_outputs selects Tier 3."""
        selector = PatternSelector()
        spec = AgentSpec(
            identifier="yaml-agent",
            summary="s",
            role_description="r",
            primary_outputs=["YAML configuration file"],
        )
        assert selector.choose_tier(spec) is PromptTier.TIER_3

    def test_xml_keyword_gives_tier3(self):
        """The word 'xml' triggers Tier 3."""
        selector = PatternSelector()
        spec = AgentSpec(
            identifier="xml-agent",
            summary="s",
            role_description="r",
            primary_outputs=["XML export"],
        )
        assert selector.choose_tier(spec) is PromptTier.TIER_3

    def test_table_keyword_gives_tier3(self):
        """The word 'table' triggers Tier 3."""
        selector = PatternSelector()
        spec = AgentSpec(
            identifier="table-agent",
            summary="s",
            role_description="r",
            primary_outputs=["data table"],
        )
        assert selector.choose_tier(spec) is PromptTier.TIER_3

    def test_determinism_required_overrides_no_structured_output(self):
        """determinism_required=True selects Tier 3 even with plain text outputs."""
        selector = PatternSelector()
        spec = AgentSpec(
            identifier="force-tier3",
            summary="s",
            role_description="r",
            primary_outputs=["plain text response"],
            determinism_required=True,
        )
        assert selector.choose_tier(spec) is PromptTier.TIER_3


# ---------------------------------------------------------------------------
# PatternSelector.get_pattern()
# ---------------------------------------------------------------------------


class TestPatternSelectorGetPattern:
    def test_tier1_returns_tier1_pattern(self):
        """get_pattern(TIER_1) returns a Tier1Pattern instance."""
        selector = PatternSelector()
        pattern = selector.get_pattern(PromptTier.TIER_1)
        assert isinstance(pattern, Tier1Pattern)

    def test_tier2_returns_tier2_pattern(self):
        """get_pattern(TIER_2) returns a Tier2Pattern instance."""
        selector = PatternSelector()
        pattern = selector.get_pattern(PromptTier.TIER_2)
        assert isinstance(pattern, Tier2Pattern)

    def test_tier3_returns_tier3_pattern(self):
        """get_pattern(TIER_3) returns a Tier3Pattern instance."""
        selector = PatternSelector()
        pattern = selector.get_pattern(PromptTier.TIER_3)
        assert isinstance(pattern, Tier3Pattern)


# ---------------------------------------------------------------------------
# Tier1Pattern.build()
# ---------------------------------------------------------------------------


class TestTier1PatternBuild:
    def test_returns_prompt_design(self):
        """build() returns a PromptDesign."""
        pattern = Tier1Pattern()
        result = pattern.build(minimal_agent_spec(), empty_registry())
        assert isinstance(result, PromptDesign)

    def test_tier_is_tier1(self):
        """The resulting design's tier is TIER_1."""
        pattern = Tier1Pattern()
        result = pattern.build(minimal_agent_spec(), empty_registry())
        assert result.tier is PromptTier.TIER_1

    def test_no_execution_plan(self):
        """Tier 1 designs have no execution plan."""
        pattern = Tier1Pattern()
        result = pattern.build(minimal_agent_spec(), empty_registry())
        assert result.execution_plan is None

    def test_no_rule_blocks(self):
        """Tier 1 designs have no rule block references."""
        pattern = Tier1Pattern()
        result = pattern.build(minimal_agent_spec(), empty_registry())
        assert result.rule_blocks == []

    def test_goal_is_spec_summary(self):
        """The task goal defaults to the spec summary."""
        spec = minimal_agent_spec()
        pattern = Tier1Pattern()
        result = pattern.build(spec, empty_registry())
        assert result.task.goal == spec.summary

    def test_task_name_derived_from_identifier(self):
        """The task name contains the agent identifier."""
        spec = minimal_agent_spec()
        pattern = Tier1Pattern()
        result = pattern.build(spec, empty_registry())
        assert spec.identifier in result.task.name

    def test_agent_spec_preserved(self):
        """The agent_spec on the design matches the input spec."""
        spec = minimal_agent_spec()
        pattern = Tier1Pattern()
        result = pattern.build(spec, empty_registry())
        assert result.agent_spec is spec


# ---------------------------------------------------------------------------
# Tier2Pattern.build()
# ---------------------------------------------------------------------------


class TestTier2PatternBuild:
    def test_returns_prompt_design(self):
        """build() returns a PromptDesign."""
        pattern = Tier2Pattern()
        result = pattern.build(constrained_agent_spec(), empty_registry())
        assert isinstance(result, PromptDesign)

    def test_tier_is_tier2(self):
        """The resulting design's tier is TIER_2."""
        pattern = Tier2Pattern()
        result = pattern.build(constrained_agent_spec(), empty_registry())
        assert result.tier is PromptTier.TIER_2

    def test_has_execution_plan(self):
        """Tier 2 designs include an execution plan."""
        pattern = Tier2Pattern()
        result = pattern.build(constrained_agent_spec(), empty_registry())
        assert result.execution_plan is not None
        assert isinstance(result.execution_plan, ExecutionPlanBlock)

    def test_execution_plan_has_three_steps(self):
        """The default Tier 2 heuristic plan has exactly three steps."""
        pattern = Tier2Pattern()
        result = pattern.build(constrained_agent_spec(), empty_registry())
        assert len(result.execution_plan.steps) == 3

    def test_steps_are_ordered_sequentially(self):
        """Steps are numbered 1, 2, 3."""
        pattern = Tier2Pattern()
        result = pattern.build(constrained_agent_spec(), empty_registry())
        orders = [s.order for s in result.execution_plan.steps]
        assert orders == [1, 2, 3]

    def test_no_rule_blocks(self):
        """Tier 2 designs do not auto-attach rule blocks."""
        pattern = Tier2Pattern()
        result = pattern.build(constrained_agent_spec(), empty_registry())
        assert result.rule_blocks == []

    def test_plan_name_derived_from_identifier(self):
        """The execution plan name contains the agent identifier."""
        spec = constrained_agent_spec()
        pattern = Tier2Pattern()
        result = pattern.build(spec, empty_registry())
        assert spec.identifier in result.execution_plan.name


# ---------------------------------------------------------------------------
# Tier3Pattern.build()
# ---------------------------------------------------------------------------


class TestTier3PatternBuild:
    def test_returns_prompt_design(self):
        """build() returns a PromptDesign."""
        pattern = Tier3Pattern()
        result = pattern.build(deterministic_agent_spec(), empty_registry())
        assert isinstance(result, PromptDesign)

    def test_tier_is_tier3(self):
        """The resulting design's tier is TIER_3."""
        pattern = Tier3Pattern()
        result = pattern.build(deterministic_agent_spec(), empty_registry())
        assert result.tier is PromptTier.TIER_3

    def test_has_execution_plan(self):
        """Tier 3 designs include an execution plan."""
        pattern = Tier3Pattern()
        result = pattern.build(deterministic_agent_spec(), empty_registry())
        assert result.execution_plan is not None

    def test_execution_plan_has_five_steps(self):
        """The default Tier 3 heuristic plan has exactly five steps."""
        pattern = Tier3Pattern()
        result = pattern.build(deterministic_agent_spec(), empty_registry())
        assert len(result.execution_plan.steps) == 5

    def test_steps_ordered_1_through_5(self):
        """Steps are numbered 1 through 5."""
        pattern = Tier3Pattern()
        result = pattern.build(deterministic_agent_spec(), empty_registry())
        orders = [s.order for s in result.execution_plan.steps]
        assert orders == [1, 2, 3, 4, 5]

    def test_no_rule_blocks_for_empty_registry(self):
        """When the registry is empty, no rule block refs are attached."""
        pattern = Tier3Pattern()
        result = pattern.build(deterministic_agent_spec(), empty_registry())
        assert result.rule_blocks == []

    def test_citation_rule_block_attached_for_source_output(self):
        """'source' in outputs triggers citations rule block attachment."""
        spec = AgentSpec(
            identifier="source-agent",
            summary="s",
            role_description="r",
            primary_outputs=["document with sources"],
        )
        pattern = Tier3Pattern()
        result = pattern.build(spec, sample_registry())
        names = [ref.name for ref in result.rule_blocks]
        assert "citations" in names

    def test_html_markup_rule_block_attached_for_html_output(self):
        """'html' in outputs triggers html-markup rule block attachment."""
        spec = AgentSpec(
            identifier="html-agent",
            summary="s",
            role_description="r",
            primary_outputs=["html document"],
        )
        pattern = Tier3Pattern()
        result = pattern.build(spec, sample_registry())
        names = [ref.name for ref in result.rule_blocks]
        assert "html-markup" in names

    def test_brief_schema_rule_block_attached_for_brief_identifier(self):
        """'brief' in the identifier triggers brief-json-schema attachment."""
        spec = brief_agent_spec()
        pattern = Tier3Pattern()
        result = pattern.build(spec, sample_registry())
        names = [ref.name for ref in result.rule_blocks]
        assert "brief-json-schema" in names

    def test_markdown_keyword_triggers_html_markup_block(self):
        """'markdown' in outputs also triggers html-markup attachment."""
        spec = AgentSpec(
            identifier="md-agent",
            summary="s",
            role_description="r",
            primary_outputs=["markdown formatted report"],
        )
        pattern = Tier3Pattern()
        result = pattern.build(spec, sample_registry())
        names = [ref.name for ref in result.rule_blocks]
        assert "html-markup" in names
