"""Shared fixtures, mocks, and helpers for the test suite.

This module is loaded automatically by pytest before any test file runs.
All fixtures defined here are available to every test without explicit import.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from prompt_design_system.config import AppConfig, AppPaths
from prompt_design_system.models import (
    AgentSpec,
    EvaluationScenario,
    PromptDesign,
)
from prompt_design_system.patterns import PatternSelector
from prompt_design_system.providers import OpenAIProvider, UsageMetadata
from prompt_design_system.rule_blocks import RuleBlockRegistry
from prompt_design_system.storage import ProjectStorage
from tests.fixtures.sample_data import (
    MINIMAL_MARKDOWN_SPEC,
    VALID_LLM_TASK_RESPONSE,
    VALID_LLM_TASK_WITH_STEPS_RESPONSE,
    constrained_agent_spec,
    deterministic_agent_spec,
    minimal_agent_spec,
    sample_registry,
    tier2_prompt_design,
)

# ---------------------------------------------------------------------------
# Core domain fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_agent_spec() -> AgentSpec:
    """A minimal but valid AgentSpec usable across most tests."""
    return minimal_agent_spec()


@pytest.fixture
def constrained_spec() -> AgentSpec:
    """AgentSpec with constraints — drives Tier 2 selection."""
    return constrained_agent_spec()


@pytest.fixture
def deterministic_spec() -> AgentSpec:
    """AgentSpec with determinism_required=True — drives Tier 3 selection."""
    return deterministic_agent_spec()


@pytest.fixture
def sample_design() -> PromptDesign:
    """A Tier 2 PromptDesign ready for use in agent and storage tests."""
    return tier2_prompt_design()


@pytest.fixture
def sample_scenarios() -> list[EvaluationScenario]:
    """A small set of evaluation scenarios covering pass, fail, and skipped."""
    return [
        EvaluationScenario(
            identifier="s-pass",
            description="Standard scenario with matching properties.",
            input_example="test input",
            expected_properties=["process", "test"],
        ),
        EvaluationScenario(
            identifier="s-fail",
            description="Scenario with absent property.",
            input_example="edge case input",
            expected_properties=["nonexistent-property-xyz"],
        ),
        EvaluationScenario(
            identifier="s-skip",
            description="Empty scenario with no assertions.",
            expected_properties=[],
        ),
    ]


# ---------------------------------------------------------------------------
# Registry and config fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def registry() -> RuleBlockRegistry:
    """Pre-populated RuleBlockRegistry for pattern and agent tests."""
    return sample_registry()


@pytest.fixture
def empty_registry() -> RuleBlockRegistry:
    """Empty RuleBlockRegistry for edge-case tests."""
    return RuleBlockRegistry(rule_blocks={})


@pytest.fixture
def app_config(tmp_path: Path) -> AppConfig:
    """AppConfig rooted at a temporary directory for isolated storage tests."""
    return AppConfig(paths=AppPaths(root_dir=tmp_path))


@pytest.fixture
def project_storage(app_config: AppConfig) -> ProjectStorage:
    """ProjectStorage backed by a temp directory."""
    return ProjectStorage(config=app_config)


@pytest.fixture
def pattern_selector() -> PatternSelector:
    """A default PatternSelector with no customisation."""
    return PatternSelector()


# ---------------------------------------------------------------------------
# Filesystem fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def spec_file(tmp_path: Path) -> Path:
    """Write MINIMAL_MARKDOWN_SPEC to a temp file and return its path."""
    spec_path = tmp_path / "test-agent.agent-spec.md"
    spec_path.write_text(MINIMAL_MARKDOWN_SPEC, encoding="utf-8")
    return spec_path


@pytest.fixture
def rule_blocks_dir(tmp_path: Path) -> Path:
    """Create a temporary rule_blocks directory with two Markdown files."""
    rb_dir = tmp_path / "ai_components" / "rule_blocks"
    rb_dir.mkdir(parents=True)
    (rb_dir / "citations.md").write_text(
        "# Citation Rules\n\nUse numbered references.", encoding="utf-8"
    )
    (rb_dir / "html-markup.md").write_text(
        "# HTML Markup Rules\n\nAllow only safe tags.", encoding="utf-8"
    )
    return rb_dir


@pytest.fixture
def app_config_with_rule_blocks(tmp_path: Path, rule_blocks_dir: Path) -> AppConfig:
    """AppConfig rooted at tmp_path with real rule block files present."""
    return AppConfig(paths=AppPaths(root_dir=tmp_path))


# ---------------------------------------------------------------------------
# LLM mock fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_llm_client():
    """A mock LLM client that returns deterministic JSON for task enrichment."""
    client = MagicMock()
    client.generate.return_value = VALID_LLM_TASK_RESPONSE
    return client


@pytest.fixture
def mock_llm_client_with_steps():
    """A mock LLM client that returns JSON including execution_steps."""
    client = MagicMock()
    client.generate.return_value = VALID_LLM_TASK_WITH_STEPS_RESPONSE
    return client


@pytest.fixture
def mock_llm_client_failing():
    """A mock LLM client that always raises RuntimeError on generate()."""
    client = MagicMock()
    client.generate.side_effect = RuntimeError("Simulated API failure")
    return client


@pytest.fixture
def mock_openai_provider(monkeypatch: pytest.MonkeyPatch):
    """Monkeypatched OpenAIProvider that never makes real HTTP calls."""

    def fake_generate(self, prompt: str, *, model: str | None = None) -> str:
        return VALID_LLM_TASK_RESPONSE

    def fake_generate_with_system(
        self,
        system_prompt: str,
        user_message: str,
        *,
        model: str | None = None,
    ) -> tuple[str, UsageMetadata]:
        metadata = UsageMetadata(input_tokens=100, output_tokens=50, total_tokens=150)
        return "Mocked assistant response.", metadata

    monkeypatch.setattr(OpenAIProvider, "generate", fake_generate)
    monkeypatch.setattr(OpenAIProvider, "generate_with_system", fake_generate_with_system)


# ---------------------------------------------------------------------------
# Scenarios file fixture for CLI tests
# ---------------------------------------------------------------------------


@pytest.fixture
def scenarios_json_file(tmp_path: Path) -> Path:
    """Write a small JSON scenarios file suitable for the evaluate CLI command."""
    scenarios = [
        {
            "identifier": "s1",
            "description": "Basic scenario.",
            "input_example": "some input",
            "expected_properties": ["test"],
        },
        {
            "identifier": "s2",
            "description": "Scenario with no properties.",
            "expected_properties": [],
        },
    ]
    path = tmp_path / "scenarios.json"
    path.write_text(json.dumps(scenarios), encoding="utf-8")
    return path
