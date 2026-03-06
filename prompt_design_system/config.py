from __future__ import annotations

import os
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import ClassVar


@dataclass
class AppPaths:
    """Centralized application paths."""

    root_dir: Path
    ai_components_dirname: ClassVar[str] = "ai_components"
    projects_dirname: ClassVar[str] = "projects"

    @property
    def ai_components_dir(self) -> Path:
        return self.root_dir / self.ai_components_dirname

    @property
    def projects_dir(self) -> Path:
        """Root directory for prompt design projects."""
        return self.root_dir / self.projects_dirname

    @property
    def system_prompts_dir(self) -> Path:
        return self.ai_components_dir / "prompts" / "system"

    @property
    def user_templates_dir(self) -> Path:
        return self.ai_components_dir / "prompts" / "user"

    @property
    def rule_blocks_dir(self) -> Path:
        return self.ai_components_dir / "rule_blocks"

    @property
    def eval_datasets_dir(self) -> Path:
        return self.ai_components_dir / "evals"


class VerbosityLevel(StrEnum):
    """Reasoning effort level for GPT-5.x models."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class LLMConfig:
    """Centralized LLM API parameters (model, temperature, max_tokens, reasoning_effort)."""

    model: str = "gpt-5-mini"
    temperature: float = 0.7
    max_tokens: int = 1500
    verbosity: VerbosityLevel = VerbosityLevel.MEDIUM

    @classmethod
    def from_env(cls) -> LLMConfig:
        """Load overrides from environment when set."""
        model = os.getenv("OPENAI_MODEL", cls.model)
        max_tokens_env = os.getenv("OPENAI_MAX_TOKENS")
        if max_tokens_env:
            max_tokens = int(max_tokens_env)
        else:
            max_tokens = cls.get_max_tokens_for_model(model)

        verbosity_str = os.getenv("OPENAI_VERBOSITY", cls.verbosity.value)
        try:
            verbosity = VerbosityLevel(verbosity_str)
        except ValueError:
            verbosity = cls.verbosity

        return cls(
            model=model,
            temperature=float(os.getenv("OPENAI_TEMPERATURE", cls.temperature)),
            max_tokens=max_tokens,
            verbosity=verbosity,
        )

    @staticmethod
    def get_max_tokens_for_model(model: str) -> int:
        """Return model-specific max_tokens defaults."""
        if model.startswith("gpt-5"):
            return 1500
        elif model.startswith("gpt-4"):
            return 2000
        return 2000


@dataclass
class AppConfig:
    """Top-level application configuration."""

    paths: AppPaths
    llm: LLMConfig | None = None

    @classmethod
    def from_cwd(cls) -> AppConfig:
        root_dir = Path.cwd()
        return cls(
            paths=AppPaths(root_dir=root_dir),
            llm=LLMConfig.from_env(),
        )
