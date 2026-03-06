"""Tests for prompt_design_system.storage.

Covers ProjectStorage save/load operations, path construction, overwrite
semantics, and error handling for missing files.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from prompt_design_system.models import PromptDesign, PromptTier
from prompt_design_system.storage import (
    DESIGNS_SUBDIR_NAME,
    PROMPTS_SUBDIR_NAME,
    SPECS_SUBDIR_NAME,
    ProjectPaths,
)
from tests.fixtures.sample_data import (
    tier1_prompt_design,
    tier2_prompt_design,
)

# ---------------------------------------------------------------------------
# ProjectPaths
# ---------------------------------------------------------------------------


class TestProjectPaths:
    def test_designs_dir_is_subdir_of_root(self, tmp_path: Path):
        """designs_dir is root/designs."""
        paths = ProjectPaths(root=tmp_path)
        assert paths.designs_dir == tmp_path / DESIGNS_SUBDIR_NAME

    def test_prompts_dir_is_subdir_of_root(self, tmp_path: Path):
        """prompts_dir is root/prompts."""
        paths = ProjectPaths(root=tmp_path)
        assert paths.prompts_dir == tmp_path / PROMPTS_SUBDIR_NAME

    def test_specs_dir_is_subdir_of_root(self, tmp_path: Path):
        """specs_dir is root/specs."""
        paths = ProjectPaths(root=tmp_path)
        assert paths.specs_dir == tmp_path / SPECS_SUBDIR_NAME


# ---------------------------------------------------------------------------
# ProjectStorage.get_project_paths()
# ---------------------------------------------------------------------------


class TestGetProjectPaths:
    def test_project_root_under_projects_dir(self, project_storage, app_config, tmp_path):
        """get_project_paths() returns a root under projects_dir."""
        paths = project_storage.get_project_paths("my-agent")
        assert paths.root == app_config.paths.projects_dir / "my-agent"

    def test_returns_project_paths_instance(self, project_storage):
        """get_project_paths() returns a ProjectPaths instance."""
        paths = project_storage.get_project_paths("agent")
        assert isinstance(paths, ProjectPaths)


# ---------------------------------------------------------------------------
# ProjectStorage.ensure_project_dirs()
# ---------------------------------------------------------------------------


class TestEnsureProjectDirs:
    def test_creates_all_subdirectories(self, project_storage):
        """ensure_project_dirs() creates root, designs, prompts, and specs dirs."""
        paths = project_storage.ensure_project_dirs("new-agent")
        assert paths.root.exists()
        assert paths.designs_dir.exists()
        assert paths.prompts_dir.exists()
        assert paths.specs_dir.exists()

    def test_idempotent_when_dirs_exist(self, project_storage):
        """Calling ensure_project_dirs() twice does not raise."""
        project_storage.ensure_project_dirs("agent")
        project_storage.ensure_project_dirs("agent")  # Should not raise.


# ---------------------------------------------------------------------------
# ProjectStorage.save_design()
# ---------------------------------------------------------------------------


class TestSaveDesign:
    def test_creates_design_json_file(self, project_storage):
        """save_design() writes a design.json file to the designs directory."""
        design = tier2_prompt_design()
        path = project_storage.save_design(design)
        assert path.exists()
        assert path.name == "design.json"

    def test_design_json_is_valid(self, project_storage):
        """The written file contains valid JSON."""
        design = tier2_prompt_design()
        path = project_storage.save_design(design)
        content = path.read_text(encoding="utf-8")
        parsed = json.loads(content)
        assert parsed["agent_spec"]["identifier"] == design.agent_spec.identifier

    def test_overwrite_false_preserves_existing(self, project_storage):
        """When overwrite=False, an existing design.json is not replaced."""
        design = tier2_prompt_design()
        project_storage.save_design(design, overwrite=True)

        # Write a sentinel value directly to the file.
        paths = project_storage.get_project_paths(design.agent_spec.identifier)
        sentinel_path = paths.designs_dir / "design.json"
        sentinel_path.write_text('{"sentinel": true}', encoding="utf-8")

        # save_design with overwrite=False should return the path but not overwrite.
        project_storage.save_design(design, overwrite=False)
        content = json.loads(sentinel_path.read_text(encoding="utf-8"))
        assert "sentinel" in content

    def test_overwrite_true_replaces_existing(self, project_storage):
        """When overwrite=True, an existing design.json is replaced."""
        design = tier2_prompt_design()
        project_storage.save_design(design, overwrite=True)

        paths = project_storage.get_project_paths(design.agent_spec.identifier)
        design_file = paths.designs_dir / "design.json"
        design_file.write_text('{"old": true}', encoding="utf-8")

        project_storage.save_design(design, overwrite=True)
        content = json.loads(design_file.read_text(encoding="utf-8"))
        assert "old" not in content

    def test_returns_path_to_written_file(self, project_storage):
        """save_design() returns the Path of the written file."""
        design = tier1_prompt_design()
        path = project_storage.save_design(design)
        assert isinstance(path, Path)
        assert path.exists()


# ---------------------------------------------------------------------------
# ProjectStorage.load_design()
# ---------------------------------------------------------------------------


class TestLoadDesign:
    def test_round_trip_save_and_load(self, project_storage):
        """A saved design can be loaded and equals the original."""
        original = tier2_prompt_design()
        project_storage.save_design(original, overwrite=True)
        loaded = project_storage.load_design(original.agent_spec.identifier)
        assert loaded.agent_spec.identifier == original.agent_spec.identifier
        assert loaded.tier == original.tier
        assert loaded.task.goal == original.task.goal

    def test_load_missing_raises_file_not_found(self, project_storage):
        """Loading a design that does not exist raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Design file not found"):
            project_storage.load_design("nonexistent-agent")

    def test_loaded_design_is_prompt_design_instance(self, project_storage):
        """load_design() returns a PromptDesign."""
        design = tier1_prompt_design()
        project_storage.save_design(design, overwrite=True)
        loaded = project_storage.load_design(design.agent_spec.identifier)
        assert isinstance(loaded, PromptDesign)

    def test_execution_plan_round_trips(self, project_storage):
        """Execution plan (steps, name) survives the save/load cycle."""
        design = tier2_prompt_design()
        project_storage.save_design(design, overwrite=True)
        loaded = project_storage.load_design(design.agent_spec.identifier)
        assert loaded.execution_plan is not None
        assert len(loaded.execution_plan.steps) == len(design.execution_plan.steps)

    def test_tier_enum_round_trips(self, project_storage):
        """Tier enum value is correctly preserved through JSON serialisation."""
        design = tier2_prompt_design()
        project_storage.save_design(design, overwrite=True)
        loaded = project_storage.load_design(design.agent_spec.identifier)
        assert loaded.tier is PromptTier.TIER_2


# ---------------------------------------------------------------------------
# ProjectStorage.save_rendered_prompt()
# ---------------------------------------------------------------------------


class TestSaveRenderedPrompt:
    def test_saves_to_default_system_md(self, project_storage):
        """Without a filename override, the prompt is saved as system.md."""
        design = tier2_prompt_design()
        path = project_storage.save_rendered_prompt(design, "# Task\n\nDo this.", overwrite=True)
        assert path.name == "system.md"
        assert path.exists()

    def test_content_written_correctly(self, project_storage):
        """The written file contains exactly the rendered prompt string."""
        design = tier2_prompt_design()
        rendered = "# Task\n\nDo this thing.\n"
        path = project_storage.save_rendered_prompt(design, rendered, overwrite=True)
        assert path.read_text(encoding="utf-8") == rendered

    def test_custom_filename_relative(self, project_storage):
        """A relative filename is resolved relative to the prompts directory."""
        design = tier2_prompt_design()
        path = project_storage.save_rendered_prompt(
            design, "content", overwrite=True, filename=Path("custom.md")
        )
        assert path.name == "custom.md"
        assert "prompts" in str(path)

    def test_custom_filename_absolute(self, project_storage, tmp_path: Path):
        """An absolute filename is used as-is, not nested under prompts."""
        design = tier2_prompt_design()
        absolute = tmp_path / "my-output.md"
        path = project_storage.save_rendered_prompt(
            design, "content", overwrite=True, filename=absolute
        )
        assert path == absolute
        assert path.exists()

    def test_overwrite_false_preserves_existing(self, project_storage):
        """overwrite=False does not replace an existing system.md."""
        design = tier2_prompt_design()
        project_storage.save_rendered_prompt(design, "first content", overwrite=True)

        paths = project_storage.get_project_paths(design.agent_spec.identifier)
        prompt_path = paths.prompts_dir / "system.md"

        project_storage.save_rendered_prompt(design, "second content", overwrite=False)
        assert prompt_path.read_text(encoding="utf-8") == "first content"

    def test_overwrite_true_replaces_existing(self, project_storage):
        """overwrite=True replaces an existing system.md."""
        design = tier2_prompt_design()
        project_storage.save_rendered_prompt(design, "old content", overwrite=True)
        project_storage.save_rendered_prompt(design, "new content", overwrite=True)

        paths = project_storage.get_project_paths(design.agent_spec.identifier)
        prompt_path = paths.prompts_dir / "system.md"
        assert prompt_path.read_text(encoding="utf-8") == "new content"


# ---------------------------------------------------------------------------
# ProjectStorage.copy_spec_into_project()
# ---------------------------------------------------------------------------


class TestCopySpecIntoProject:
    def test_copies_file_to_specs_directory(self, project_storage, tmp_path: Path):
        """copy_spec_into_project() places the spec file under specs/."""
        spec_file = tmp_path / "my-agent.agent-spec.md"
        spec_file.write_text("# Spec\n\nContent.", encoding="utf-8")

        target = project_storage.copy_spec_into_project(spec_file, "my-agent")
        assert target.exists()
        assert "specs" in str(target)

    def test_content_matches_source(self, project_storage, tmp_path: Path):
        """The copied file has identical content to the source."""
        original_content = "# Agent Spec\n\nSome content.\n"
        spec_file = tmp_path / "spec.agent-spec.md"
        spec_file.write_text(original_content, encoding="utf-8")

        target = project_storage.copy_spec_into_project(spec_file, "spec")
        assert target.read_text(encoding="utf-8") == original_content

    def test_copy_missing_file_raises_file_not_found(self, project_storage, tmp_path: Path):
        """Trying to copy a non-existent spec raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError, match="Spec file not found"):
            project_storage.copy_spec_into_project(tmp_path / "missing.md", "agent")

    def test_does_not_overwrite_existing_copy(self, project_storage, tmp_path: Path):
        """If the target already exists, copy_spec_into_project() skips the write."""
        spec_file = tmp_path / "agent.agent-spec.md"
        spec_file.write_text("original", encoding="utf-8")

        # First copy.
        target = project_storage.copy_spec_into_project(spec_file, "agent")

        # Overwrite target with a sentinel.
        target.write_text("sentinel", encoding="utf-8")

        # Second copy should NOT overwrite.
        project_storage.copy_spec_into_project(spec_file, "agent")
        assert target.read_text(encoding="utf-8") == "sentinel"

    def test_filename_preserved_in_destination(self, project_storage, tmp_path: Path):
        """The destination filename matches the source filename."""
        spec_file = tmp_path / "my-special-agent.agent-spec.md"
        spec_file.write_text("content", encoding="utf-8")

        target = project_storage.copy_spec_into_project(spec_file, "my-special-agent")
        assert target.name == "my-special-agent.agent-spec.md"
