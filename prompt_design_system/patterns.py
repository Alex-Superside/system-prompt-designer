from __future__ import annotations

from dataclasses import dataclass

from .models import (
    AgentSpec,
    ExecutionPlanBlock,
    ExecutionStep,
    PromptDesign,
    PromptTier,
    RuleBlockRef,
    TaskBlock,
)
from .rule_blocks import RuleBlockRegistry

STRUCTURED_KEYWORDS = ["json", "schema", "table", "yaml", "xml"]


def _build_base_task(agent_spec: AgentSpec) -> TaskBlock:
    return TaskBlock(
        name=f"{agent_spec.identifier}_task",
        goal=agent_spec.summary,
        acceptance_criteria=[],
        constraints=agent_spec.constraints,
        output_format_description=None,
    )


def _default_rule_block_refs(
    agent_spec: AgentSpec,
    registry: RuleBlockRegistry,
) -> list[RuleBlockRef]:
    """Attach default rule blocks based on structured output needs."""
    available_names = set(registry.list_names())
    refs: list[RuleBlockRef] = []

    lower_outputs = " ".join(agent_spec.primary_outputs).lower()

    if "citation" in lower_outputs or "source" in lower_outputs:
        if "citations" in available_names:
            block = registry.get("citations")
            refs.append(RuleBlockRef(name=block.name, path=block.path))

    if any(keyword in lower_outputs for keyword in ("html", "markdown")):
        if "html-markup" in available_names:
            block = registry.get("html-markup")
            refs.append(RuleBlockRef(name=block.name, path=block.path))

    if "brief" in agent_spec.identifier.lower() or "brief" in lower_outputs:
        if "brief-json-schema" in available_names:
            block = registry.get("brief-json-schema")
            refs.append(RuleBlockRef(name=block.name, path=block.path))

    return refs


@dataclass
class TierPattern:
    """Base pattern that knows how to build a PromptDesign."""

    tier: PromptTier

    def build(self, agent_spec: AgentSpec, registry: RuleBlockRegistry) -> PromptDesign:
        raise NotImplementedError


@dataclass
class Tier1Pattern(TierPattern):
    """Tier 1 – Task only."""

    tier: PromptTier = PromptTier.TIER_1

    def build(self, agent_spec: AgentSpec, registry: RuleBlockRegistry) -> PromptDesign:
        task = _build_base_task(agent_spec)
        return PromptDesign(
            agent_spec=agent_spec,
            tier=self.tier,
            task=task,
            execution_plan=None,
            rule_blocks=[],
        )


@dataclass
class Tier2Pattern(TierPattern):
    """Tier 2 – Task + minimal execution plan."""

    tier: PromptTier = PromptTier.TIER_2

    def build(self, agent_spec: AgentSpec, registry: RuleBlockRegistry) -> PromptDesign:
        task = _build_base_task(agent_spec)
        steps: list[ExecutionStep] = [
            ExecutionStep(
                order=1,
                description="Read and understand the task, inputs, and constraints.",
            ),
            ExecutionStep(
                order=2,
                description="Plan the response at a high level before writing.",
            ),
            ExecutionStep(
                order=3,
                description="Produce the output, checking that it satisfies the acceptance criteria.",
            ),
        ]

        execution_plan = ExecutionPlanBlock(
            name=f"{agent_spec.identifier}_plan",
            steps=steps,
        )

        return PromptDesign(
            agent_spec=agent_spec,
            tier=self.tier,
            task=task,
            execution_plan=execution_plan,
            rule_blocks=[],
        )


@dataclass
class Tier3Pattern(TierPattern):
    """Tier 3 – Task + plan + rule block references."""

    tier: PromptTier = PromptTier.TIER_3

    def build(self, agent_spec: AgentSpec, registry: RuleBlockRegistry) -> PromptDesign:
        task = _build_base_task(agent_spec)

        steps: list[ExecutionStep] = [
            ExecutionStep(
                order=1,
                description="Read the full task and constraints. Do not start writing the final answer yet.",
            ),
            ExecutionStep(
                order=2,
                description="Identify which rule blocks apply and how they constrain formatting and structure.",
            ),
            ExecutionStep(
                order=3,
                description="Sketch an outline or intermediate representation that will satisfy the rule blocks.",
            ),
            ExecutionStep(
                order=4,
                description="Render the final output strictly following the rule blocks and outline.",
            ),
            ExecutionStep(
                order=5,
                description="Self-check the output against acceptance criteria and rule blocks before returning.",
            ),
        ]

        execution_plan = ExecutionPlanBlock(
            name=f"{agent_spec.identifier}_plan",
            steps=steps,
        )

        rule_block_refs = _default_rule_block_refs(agent_spec, registry)

        return PromptDesign(
            agent_spec=agent_spec,
            tier=self.tier,
            task=task,
            execution_plan=execution_plan,
            rule_blocks=rule_block_refs,
        )


class PatternSelector:
    """Select an appropriate tier/pattern given an AgentSpec."""

    def __init__(self) -> None:
        self._tier1 = Tier1Pattern()
        self._tier2 = Tier2Pattern()
        self._tier3 = Tier3Pattern()

    def choose_tier(self, agent_spec: AgentSpec) -> PromptTier:
        outputs_text = " ".join(agent_spec.primary_outputs).lower()

        if agent_spec.determinism_required:
            return PromptTier.TIER_3

        if any(keyword in outputs_text for keyword in STRUCTURED_KEYWORDS):
            return PromptTier.TIER_3

        if agent_spec.constraints:
            return PromptTier.TIER_2

        return PromptTier.TIER_1

    def get_pattern(self, tier: PromptTier) -> TierPattern:
        if tier is PromptTier.TIER_1:
            return self._tier1
        if tier is PromptTier.TIER_2:
            return self._tier2
        if tier is PromptTier.TIER_3:
            return self._tier3

        message = f"Unsupported tier: {tier}"
        raise ValueError(message)
