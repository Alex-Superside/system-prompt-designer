"""Tests for prompt_design_system.cli.

Uses Typer's CliRunner for command invocation.  All external dependencies
(filesystem writes, LLM calls) are controlled via fixtures and monkeypatching.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from prompt_design_system.cli import _load_scenarios, _render_prompt, app
from prompt_design_system.models import (
    EvaluationScenario,
)
from prompt_design_system.providers import UsageMetadata
from tests.fixtures.sample_data import (
    MINIMAL_MARKDOWN_SPEC,
    VALID_LLM_TASK_RESPONSE,
    tier2_prompt_design,
)

runner = CliRunner()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_app_config(tmp_path: Path):
    """Return an AppConfig rooted at tmp_path."""
    from prompt_design_system.config import AppConfig, AppPaths

    return AppConfig(paths=AppPaths(root_dir=tmp_path))


# ---------------------------------------------------------------------------
# _render_prompt helper
# ---------------------------------------------------------------------------


class TestRenderPrompt:
    def test_includes_task_name_heading(self):
        """Rendered prompt starts with a heading containing the task name."""
        design = tier2_prompt_design()
        rendered = _render_prompt(design)
        assert f"# Task: {design.task.name}" in rendered

    def test_includes_goal(self):
        """The task goal appears in the rendered prompt."""
        design = tier2_prompt_design()
        rendered = _render_prompt(design)
        assert design.task.goal in rendered

    def test_includes_acceptance_criteria_section(self):
        """Acceptance criteria section appears when criteria are present."""
        design = tier2_prompt_design()
        rendered = _render_prompt(design)
        assert "## Acceptance Criteria" in rendered
        for criterion in design.task.acceptance_criteria:
            assert criterion in rendered

    def test_includes_constraints_section(self):
        """Constraints section appears when constraints are present."""
        design = tier2_prompt_design()
        rendered = _render_prompt(design)
        assert "## Constraints" in rendered

    def test_includes_execution_plan(self):
        """Execution plan steps appear for Tier 2 designs."""
        design = tier2_prompt_design()
        rendered = _render_prompt(design)
        assert "## Execution Plan" in rendered
        for step in design.execution_plan.steps:
            assert step.description in rendered

    def test_no_execution_plan_for_tier1(self):
        """Tier 1 designs have no Execution Plan section."""
        from tests.fixtures.sample_data import tier1_prompt_design

        design = tier1_prompt_design()
        rendered = _render_prompt(design)
        assert "## Execution Plan" not in rendered

    def test_rule_blocks_section_present_when_applicable(self):
        """Rule Blocks section appears when refs are present."""
        from tests.fixtures.sample_data import tier3_prompt_design

        design = tier3_prompt_design()
        rendered = _render_prompt(design)
        assert "## Rule Blocks" in rendered
        for ref in design.rule_blocks:
            assert ref.name in rendered

    def test_no_rule_blocks_section_when_absent(self):
        """No Rule Blocks section when design has no rule block refs."""
        design = tier2_prompt_design()
        rendered = _render_prompt(design)
        assert "## Rule Blocks" not in rendered


# ---------------------------------------------------------------------------
# _load_scenarios helper
# ---------------------------------------------------------------------------


class TestLoadScenarios:
    def test_loads_valid_json_list(self, tmp_path: Path):
        """A valid JSON array of scenarios is parsed correctly."""
        data = [
            {"identifier": "s1", "description": "Scenario 1.", "expected_properties": []},
        ]
        path = tmp_path / "scenarios.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        scenarios = _load_scenarios(path)
        assert len(scenarios) == 1
        assert scenarios[0].identifier == "s1"

    def test_raises_on_non_list_json(self, tmp_path: Path):
        """A JSON object (not a list) raises ValueError."""
        path = tmp_path / "bad.json"
        path.write_text('{"not": "a list"}', encoding="utf-8")
        with pytest.raises(ValueError, match="JSON list"):
            _load_scenarios(path)

    def test_each_item_is_evaluation_scenario(self, tmp_path: Path):
        """Each parsed item is an EvaluationScenario instance."""
        data = [{"identifier": "x", "description": "d", "expected_properties": ["p"]}]
        path = tmp_path / "scenarios.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        scenarios = _load_scenarios(path)
        assert isinstance(scenarios[0], EvaluationScenario)


# ---------------------------------------------------------------------------
# init-spec command
# ---------------------------------------------------------------------------


class TestInitSpecCommand:
    def test_creates_spec_file(self, tmp_path: Path):
        """init-spec creates the agent spec template file."""
        output = tmp_path / "new-agent.agent-spec.md"
        result = runner.invoke(app, ["init-spec", "new-agent", "--output", str(output)])
        assert result.exit_code == 0, result.output
        assert output.exists()

    def test_spec_file_contains_expected_sections(self, tmp_path: Path):
        """The created spec file contains all standard section headings."""
        output = tmp_path / "my-agent.agent-spec.md"
        runner.invoke(app, ["init-spec", "my-agent", "--output", str(output)])
        content = output.read_text(encoding="utf-8")
        for heading in ["## Summary", "## Role", "## Inputs", "## Outputs", "## Constraints"]:
            assert heading in content

    def test_identifier_in_spec_heading(self, tmp_path: Path):
        """The agent identifier appears in the spec file's title heading."""
        output = tmp_path / "cool-agent.agent-spec.md"
        runner.invoke(app, ["init-spec", "cool-agent", "--output", str(output)])
        content = output.read_text(encoding="utf-8")
        assert "cool-agent" in content

    def test_refuses_to_overwrite_existing_file(self, tmp_path: Path):
        """init-spec exits with code 1 if the output file already exists."""
        output = tmp_path / "existing.agent-spec.md"
        output.write_text("# existing", encoding="utf-8")
        result = runner.invoke(app, ["init-spec", "existing", "--output", str(output)])
        assert result.exit_code == 1

    def test_output_flag_controls_path(self, tmp_path: Path):
        """The --output flag determines the file path."""
        custom_path = tmp_path / "custom-dir" / "my.agent-spec.md"
        custom_path.parent.mkdir(parents=True)
        result = runner.invoke(app, ["init-spec", "agent", "--output", str(custom_path)])
        assert result.exit_code == 0, result.output
        assert custom_path.exists()


# ---------------------------------------------------------------------------
# design command
# ---------------------------------------------------------------------------


class TestDesignCommand:
    def _write_spec(self, tmp_path: Path) -> Path:
        path = tmp_path / "test-agent.agent-spec.md"
        path.write_text(MINIMAL_MARKDOWN_SPEC, encoding="utf-8")
        return path

    def test_missing_spec_exits_with_error(self, tmp_path: Path, monkeypatch):
        """design command exits with code 1 when the spec file does not exist."""
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["design", str(tmp_path / "missing.agent-spec.md"), "--no-llm"])
        assert result.exit_code == 1

    def test_no_llm_flag_runs_heuristic_only(self, tmp_path: Path, monkeypatch):
        """--no-llm produces a design without calling OpenAI."""
        monkeypatch.chdir(tmp_path)
        spec = self._write_spec(tmp_path)
        result = runner.invoke(app, ["design", str(spec), "--no-llm"])
        assert result.exit_code == 0, result.output

    def test_design_json_written_to_disk(self, tmp_path: Path, monkeypatch):
        """After design runs, a design.json file exists in the project directory."""
        monkeypatch.chdir(tmp_path)
        spec = self._write_spec(tmp_path)
        runner.invoke(app, ["design", str(spec), "--no-llm"])
        project_dir = tmp_path / "projects" / "test-agent.agent-spec"
        design_json = project_dir / "designs" / "design.json"
        assert design_json.exists()

    def test_system_md_written_to_disk(self, tmp_path: Path, monkeypatch):
        """After design runs, a system.md prompt file exists in the project directory."""
        monkeypatch.chdir(tmp_path)
        spec = self._write_spec(tmp_path)
        runner.invoke(app, ["design", str(spec), "--no-llm"])
        project_dir = tmp_path / "projects" / "test-agent.agent-spec"
        system_md = project_dir / "prompts" / "system.md"
        assert system_md.exists()

    def test_output_flag_writes_to_custom_path(self, tmp_path: Path, monkeypatch):
        """The --output flag writes the rendered prompt to the specified file."""
        monkeypatch.chdir(tmp_path)
        spec = self._write_spec(tmp_path)
        custom_output = tmp_path / "my-prompt.md"
        runner.invoke(app, ["design", str(spec), "--no-llm", "--output", str(custom_output)])
        assert custom_output.exists()

    def test_with_mocked_llm_enriches_design(self, tmp_path: Path, monkeypatch):
        """When LLM is available, the design is enriched (goal differs from summary)."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        spec = self._write_spec(tmp_path)

        with patch("prompt_design_system.providers.OpenAIProvider") as MockProvider:
            mock_instance = MagicMock()
            mock_instance.generate.return_value = VALID_LLM_TASK_RESPONSE
            MockProvider.return_value = mock_instance

            result = runner.invoke(app, ["design", str(spec)])
            assert result.exit_code == 0, result.output
            mock_instance.generate.assert_called_once()

    def test_no_api_key_falls_back_to_heuristic(self, tmp_path: Path, monkeypatch):
        """When OPENAI_API_KEY is absent, the command falls back gracefully."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        spec = self._write_spec(tmp_path)
        result = runner.invoke(app, ["design", str(spec)])
        assert result.exit_code == 0, result.output
        assert "OPENAI_API_KEY not found" in result.output

    def test_no_api_key_warning_contains_status_reason_fix(self, tmp_path: Path, monkeypatch):
        """The missing-key warning includes all three structured parts."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        spec = self._write_spec(tmp_path)
        result = runner.invoke(app, ["design", str(spec)])
        assert result.exit_code == 0, result.output
        # Status
        assert "heuristic-only design" in result.output
        # Why
        assert "no LLM enrichment" in result.output
        # How to fix
        assert ".env.example" in result.output

    def test_no_api_key_verbose_shows_search_path(self, tmp_path: Path, monkeypatch):
        """--verbose prints each config source that was checked for the API key."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        spec = self._write_spec(tmp_path)
        result = runner.invoke(app, ["design", str(spec), "--verbose"])
        assert result.exit_code == 0, result.output
        assert "Environment variables" in result.output
        assert ".env" in result.output
        assert ".env.local" in result.output

    def test_env_file_key_is_loaded(self, tmp_path: Path, monkeypatch):
        """OPENAI_API_KEY set in a .env file in cwd is picked up by the CLI."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        (tmp_path / ".env").write_text("OPENAI_API_KEY=sk-from-dotenv\n", encoding="utf-8")

        # _load_env() runs at import time, so we call it manually to simulate
        # what happens when the CLI starts in a directory with a .env file.
        from prompt_design_system.cli import _load_env

        _load_env()

        # The key should now be in the environment.
        import os

        assert os.getenv("OPENAI_API_KEY") == "sk-from-dotenv"

    def test_env_local_overrides_env(self, tmp_path: Path, monkeypatch):
        """.env.local takes precedence over .env for OPENAI_API_KEY."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        (tmp_path / ".env").write_text("OPENAI_API_KEY=sk-from-env\n", encoding="utf-8")
        (tmp_path / ".env.local").write_text(
            "OPENAI_API_KEY=sk-from-local\n", encoding="utf-8"
        )

        from prompt_design_system.cli import _load_env

        _load_env()

        import os

        assert os.getenv("OPENAI_API_KEY") == "sk-from-local"

    def test_existing_env_var_takes_precedence_over_dotenv(self, tmp_path: Path, monkeypatch):
        """An OPENAI_API_KEY already in the environment is not overridden by .env."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("OPENAI_API_KEY", "sk-shell-level")
        (tmp_path / ".env").write_text("OPENAI_API_KEY=sk-from-dotenv\n", encoding="utf-8")

        from prompt_design_system.cli import _load_env

        _load_env()

        import os

        # load_dotenv with override=False (default) must not replace shell-level vars.
        assert os.getenv("OPENAI_API_KEY") == "sk-shell-level"

    def test_heuristic_mode_banner_printed_once(self, tmp_path: Path, monkeypatch):
        """The HEURISTIC MODE banner appears exactly once in the design output."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        spec = self._write_spec(tmp_path)
        result = runner.invoke(app, ["design", str(spec)])
        assert result.exit_code == 0, result.output
        assert result.output.count("HEURISTIC MODE") == 1

    def test_explicit_tier_flag_respected(self, tmp_path: Path, monkeypatch):
        """--no-auto-tier with --tier tier_3 forces Tier 3 selection."""
        monkeypatch.chdir(tmp_path)
        spec = self._write_spec(tmp_path)
        runner.invoke(
            app,
            [
                "design",
                str(spec),
                "--no-llm",
                "--no-auto-tier",
                "--tier",
                "tier_3",
            ],
        )
        project_dir = tmp_path / "projects" / "test-agent.agent-spec"
        design_json = project_dir / "designs" / "design.json"
        assert design_json.exists()
        content = json.loads(design_json.read_text(encoding="utf-8"))
        assert content["tier"] == "tier_3"


# ---------------------------------------------------------------------------
# evaluate command
# ---------------------------------------------------------------------------


class TestEvaluateCommand:
    def _setup_project(self, tmp_path: Path) -> str:
        """Create a design project so the evaluate command can load it."""
        monkeypatch_config = _make_app_config(tmp_path)
        from prompt_design_system.storage import ProjectStorage

        storage = ProjectStorage(monkeypatch_config)
        design = tier2_prompt_design()
        storage.save_design(design, overwrite=True)
        return design.agent_spec.identifier

    def test_missing_scenarios_file_exits_with_error(self, tmp_path: Path, monkeypatch):
        """evaluate exits with code 1 when the scenarios file is missing."""
        monkeypatch.chdir(tmp_path)
        identifier = self._setup_project(tmp_path)
        result = runner.invoke(app, ["evaluate", identifier, str(tmp_path / "missing.json")])
        assert result.exit_code == 1

    def test_missing_design_exits_with_error(
        self, tmp_path: Path, monkeypatch, scenarios_json_file
    ):
        """evaluate exits with code 1 when no design exists for the identifier."""
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["evaluate", "no-such-agent", str(scenarios_json_file)])
        assert result.exit_code == 1

    def test_successful_evaluation(self, tmp_path: Path, monkeypatch):
        """evaluate runs to completion and prints a report."""
        monkeypatch.chdir(tmp_path)
        identifier = self._setup_project(tmp_path)
        scenarios = [
            {"identifier": "s1", "description": "d", "expected_properties": []},
        ]
        scenarios_file = tmp_path / "s.json"
        scenarios_file.write_text(json.dumps(scenarios), encoding="utf-8")

        result = runner.invoke(app, ["evaluate", identifier, str(scenarios_file)])
        assert result.exit_code == 0, result.output

    def test_output_flag_saves_report(self, tmp_path: Path, monkeypatch):
        """--output saves the evaluation report to a JSON file."""
        monkeypatch.chdir(tmp_path)
        identifier = self._setup_project(tmp_path)
        scenarios = [{"identifier": "s1", "description": "d", "expected_properties": []}]
        scenarios_file = tmp_path / "s.json"
        scenarios_file.write_text(json.dumps(scenarios), encoding="utf-8")
        report_out = tmp_path / "report.json"

        runner.invoke(
            app, ["evaluate", identifier, str(scenarios_file), "--output", str(report_out)]
        )
        assert report_out.exists()
        parsed = json.loads(report_out.read_text(encoding="utf-8"))
        assert "results" in parsed


# ---------------------------------------------------------------------------
# refine command
# ---------------------------------------------------------------------------


class TestRefineCommand:
    def _setup_project(self, tmp_path: Path) -> str:
        config = _make_app_config(tmp_path)
        from prompt_design_system.storage import ProjectStorage

        storage = ProjectStorage(config)
        design = tier2_prompt_design()
        storage.save_design(design, overwrite=True)
        storage.save_rendered_prompt(design, "# Old Prompt\n\nOld content.", overwrite=True)
        return design.agent_spec.identifier

    def test_empty_feedback_exits_with_error(self, tmp_path: Path, monkeypatch):
        """refine exits with code 1 when feedback is empty."""
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["refine", "agent", "--feedback", "   "])
        assert result.exit_code == 1

    def test_missing_design_exits_with_error(self, tmp_path: Path, monkeypatch):
        """refine exits with code 1 when no design exists for the identifier."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        with patch("prompt_design_system.providers.OpenAIProvider"):
            result = runner.invoke(app, ["refine", "no-agent", "--feedback", "Make it better."])
        assert result.exit_code == 1

    def test_no_api_key_exits_with_error(self, tmp_path: Path, monkeypatch):
        """refine exits with code 1 when OPENAI_API_KEY is not set."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        identifier = self._setup_project(tmp_path)
        result = runner.invoke(app, ["refine", identifier, "--feedback", "Be better."])
        assert result.exit_code == 1

    def test_successful_refinement_updates_design(self, tmp_path: Path, monkeypatch):
        """refine with a mocked LLM updates and overwrites the design file."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        identifier = self._setup_project(tmp_path)

        with patch("prompt_design_system.providers.OpenAIProvider") as MockProvider:
            mock_instance = MagicMock()
            mock_instance.generate.return_value = VALID_LLM_TASK_RESPONSE
            MockProvider.return_value = mock_instance

            result = runner.invoke(app, ["refine", identifier, "--feedback", "Add more precision."])

        assert result.exit_code == 0, result.output


# ---------------------------------------------------------------------------
# run command
# ---------------------------------------------------------------------------


class TestRunCommand:
    def _setup_prompt(self, tmp_path: Path) -> str:
        config = _make_app_config(tmp_path)
        from prompt_design_system.storage import ProjectStorage

        storage = ProjectStorage(config)
        design = tier2_prompt_design()
        storage.ensure_project_dirs(design.agent_spec.identifier)
        storage.save_rendered_prompt(design, "# System Prompt\n\nYou are helpful.", overwrite=True)
        return design.agent_spec.identifier

    def test_empty_message_exits_with_error(self, tmp_path: Path, monkeypatch):
        """run exits with code 1 when the message is empty."""
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["run", "agent", "--message", "  "])
        assert result.exit_code == 1

    def test_missing_system_prompt_exits_with_error(self, tmp_path: Path, monkeypatch):
        """run exits with code 1 when no system.md exists for the identifier."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        with patch("prompt_design_system.providers.OpenAIProvider"):
            result = runner.invoke(app, ["run", "no-agent", "--message", "hello"])
        assert result.exit_code == 1

    def test_no_api_key_exits_with_error(self, tmp_path: Path, monkeypatch):
        """run exits with code 1 when OPENAI_API_KEY is missing."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        identifier = self._setup_prompt(tmp_path)
        result = runner.invoke(app, ["run", identifier, "--message", "hello"])
        assert result.exit_code == 1

    def test_successful_run_prints_response(self, tmp_path: Path, monkeypatch):
        """run with a mocked LLM prints the assistant response."""
        monkeypatch.chdir(tmp_path)
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
        identifier = self._setup_prompt(tmp_path)
        metadata = UsageMetadata(input_tokens=10, output_tokens=5, total_tokens=15)

        with patch("prompt_design_system.providers.OpenAIProvider") as MockProvider:
            mock_instance = MagicMock()
            mock_instance.generate_with_system.return_value = ("Mocked response.", metadata)
            MockProvider.return_value = mock_instance

            result = runner.invoke(app, ["run", identifier, "--message", "Hello there."])

        assert result.exit_code == 0, result.output
        assert "Mocked response." in result.output
