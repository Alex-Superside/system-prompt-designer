from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import AppConfig
from .models import PromptDesign

DESIGNS_SUBDIR_NAME = "designs"
PROMPTS_SUBDIR_NAME = "prompts"
SPECS_SUBDIR_NAME = "specs"


@dataclass
class ProjectPaths:
    """Resolved filesystem paths for a single prompt design project."""

    root: Path

    @property
    def designs_dir(self) -> Path:
        return self.root / DESIGNS_SUBDIR_NAME

    @property
    def prompts_dir(self) -> Path:
        return self.root / PROMPTS_SUBDIR_NAME

    @property
    def specs_dir(self) -> Path:
        return self.root / SPECS_SUBDIR_NAME


class ProjectStorage:
    """File-based storage for specs, designs, and rendered prompts.

    Layout (per project identifier):

    projects/
      <identifier>/
        specs/
          *.agent-spec.md
        designs/
          design.json
        prompts/
          system.md
    """

    def __init__(self, config: AppConfig) -> None:
        self._config = config

    def get_project_paths(self, identifier: str) -> ProjectPaths:
        project_root = self._config.paths.projects_dir / identifier
        return ProjectPaths(root=project_root)

    def ensure_project_dirs(self, identifier: str) -> ProjectPaths:
        paths = self.get_project_paths(identifier)
        paths.root.mkdir(parents=True, exist_ok=True)
        paths.designs_dir.mkdir(parents=True, exist_ok=True)
        paths.prompts_dir.mkdir(parents=True, exist_ok=True)
        paths.specs_dir.mkdir(parents=True, exist_ok=True)
        return paths

    def save_design(
        self,
        design: PromptDesign,
        overwrite: bool = False,
    ) -> Path:
        paths = self.ensure_project_dirs(design.agent_spec.identifier)
        design_path = paths.designs_dir / "design.json"

        if design_path.exists() and not overwrite:
            return design_path

        design_path.write_text(design.model_dump_json(indent=2), encoding="utf-8")
        return design_path

    def save_rendered_prompt(
        self,
        design: PromptDesign,
        rendered_prompt: str,
        overwrite: bool = False,
        filename: Path | None = None,
    ) -> Path:
        paths = self.ensure_project_dirs(design.agent_spec.identifier)

        if filename is None:
            prompt_path = paths.prompts_dir / "system.md"
        elif filename.is_absolute():
            prompt_path = filename
        else:
            prompt_path = paths.prompts_dir / filename

        if prompt_path.exists() and not overwrite:
            return prompt_path

        prompt_path.write_text(rendered_prompt, encoding="utf-8")
        return prompt_path

    def copy_spec_into_project(self, spec_path: Path, identifier: str) -> Path:
        """Optionally snapshot the raw spec under the project directory."""
        if not spec_path.exists():
            message = f"Spec file not found: {spec_path}"
            raise FileNotFoundError(message)

        paths = self.ensure_project_dirs(identifier)
        target = paths.specs_dir / spec_path.name

        if target.exists():
            return target

        content = spec_path.read_text(encoding="utf-8")
        target.write_text(content, encoding="utf-8")
        return target

    def load_design(self, identifier: str) -> PromptDesign:
        paths = self.get_project_paths(identifier)
        design_path = paths.designs_dir / "design.json"

        if not design_path.exists():
            message = f"Design file not found for project '{identifier}' at {design_path}"
            raise FileNotFoundError(message)

        content = design_path.read_text(encoding="utf-8")
        return PromptDesign.model_validate_json(content)
