from __future__ import annotations

from enum import StrEnum
from pathlib import Path

from pydantic import BaseModel, Field


class PromptTier(StrEnum):
    TIER_1 = "tier_1"  # Task only
    TIER_2 = "tier_2"  # Task + minimal plan
    TIER_3 = "tier_3"  # Task + plan + rule blocks


class TaskBlock(BaseModel):
    """Defines WHAT the agent must achieve."""

    name: str = Field(description="Short identifier for the task.")
    goal: str = Field(description="High-level outcome the agent must deliver.")
    acceptance_criteria: list[str] = Field(
        default_factory=list,
        description="List of conditions that define a correct output.",
    )
    constraints: list[str] = Field(
        default_factory=list,
        description="Non-functional constraints, scope limits, and must-not rules.",
    )
    output_format_description: str | None = Field(
        default=None,
        description="Human-readable description of the expected output structure.",
    )


class ExecutionStep(BaseModel):
    """Single atomic step in the execution plan."""

    order: int = Field(description="Order index of the step (1-based).")
    description: str = Field(description="What the agent should do in this step.")


class ExecutionPlanBlock(BaseModel):
    """Defines HOW the agent should proceed."""

    name: str = Field(description="Short identifier for the execution plan.")
    steps: list[ExecutionStep] = Field(
        default_factory=list,
        description="Ordered list of atomic steps.",
    )


class RuleBlockRef(BaseModel):
    """Reference to a named rule block stored externally."""

    name: str = Field(description="Stable name of the rule block.")
    path: Path | None = Field(
        default=None,
        description="Optional file path for the rule block content.",
    )


class AgentSpec(BaseModel):
    """Specification of an agent to be designed."""

    identifier: str = Field(description="Stable identifier for the agent.")
    summary: str = Field(description="Short description of the agent's purpose.")
    role_description: str = Field(description="Narrative role description for the agent.")
    primary_inputs: list[str] = Field(
        default_factory=list,
        description="What the agent receives as inputs (e.g. user messages, documents).",
    )
    primary_outputs: list[str] = Field(
        default_factory=list,
        description="What the agent is expected to produce.",
    )
    constraints: list[str] = Field(
        default_factory=list,
        description="Global constraints that apply across the prompt design.",
    )
    determinism_required: bool = Field(
        default=False,
        description="If true, prefer higher tiers and stronger structure.",
    )


class PromptDesign(BaseModel):
    """Full orthogonal prompt design."""

    agent_spec: AgentSpec
    tier: PromptTier
    task: TaskBlock
    execution_plan: ExecutionPlanBlock | None = None
    rule_blocks: list[RuleBlockRef] = Field(default_factory=list)


class EvaluationOutcome(StrEnum):
    """Coarse-grained outcome for a single evaluation scenario."""

    PASS = "pass"
    FAIL = "fail"
    SKIPPED = "skipped"


class EvaluationScenario(BaseModel):
    """Single evaluation scenario describing expected behaviour."""

    identifier: str = Field(description="Stable identifier for the scenario.")
    description: str = Field(description="Natural language description of the scenario.")
    input_example: str | None = Field(
        default=None,
        description="Representative input snippet or situation.",
    )
    expected_properties: list[str] = Field(
        default_factory=list,
        description="Key properties the output should satisfy in this scenario.",
    )


class EvaluationResult(BaseModel):
    """Result of running a PromptDesign against a scenario."""

    scenario_id: str
    outcome: EvaluationOutcome
    notes: str | None = None


class EvaluationReport(BaseModel):
    """Aggregate report over multiple evaluation scenarios."""

    design_identifier: str
    results: list[EvaluationResult]


class AuditFinding(BaseModel):
    """Specific finding from a linguistic or orthogonality audit."""

    category: str = Field(description="Finding category (e.g. noise, leak, drift).")
    location: str = Field(description="Component where the finding was found (Task, Plan, Rules).")
    evidence: str = Field(description="Specific text snippet or pattern identified.")
    suggestion: str = Field(description="Concrete, orthogonal, DSL-optimized alternative.")


class LinguisticAuditReport(BaseModel):
    """Report on linguistic technical debt and orthogonality leaks."""

    design_identifier: str
    density_score: int = Field(ge=1, le=5, description="1-5 score for semantic signal density.")
    orthogonality_score: int = Field(ge=1, le=5, description="1-5 score for component separation.")
    findings: list[AuditFinding] = Field(default_factory=list)
    summary: str = Field(description="Overall synthesis of the prompt's linguistic health.")
