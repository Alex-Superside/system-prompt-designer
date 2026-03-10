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


class ReasoningEffort(StrEnum):
    """Supported reasoning effort levels for GPT-5 Responses API calls."""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    XHIGH = "xhigh"


class VerbosityLevel(StrEnum):
    """Supported output verbosity levels for GPT-5 Responses API calls."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass(frozen=True)
class LLMConfig:
    """Centralized LLM API parameters and model-family defaults."""

    GPT5_DEFAULT_MAX_TOKENS: ClassVar[int] = 1500
    LEGACY_DEFAULT_MAX_TOKENS: ClassVar[int] = 2000

    model: str = "gpt-5-mini"
    temperature: float = 0.7
    reasoning_effort: ReasoningEffort = ReasoningEffort.MEDIUM
    text_verbosity: VerbosityLevel = VerbosityLevel.MEDIUM
    max_tokens: int = GPT5_DEFAULT_MAX_TOKENS

    @staticmethod
    def get_max_tokens_for_model(model: str) -> int:
        """Return a sensible default max token budget for the model family."""
        if model.startswith("gpt-5"):
            return LLMConfig.GPT5_DEFAULT_MAX_TOKENS
        return LLMConfig.LEGACY_DEFAULT_MAX_TOKENS

    @classmethod
    def from_env(cls) -> LLMConfig:
        """Load overrides from environment when set."""
        model = os.getenv("OPENAI_MODEL", cls.model)
        temperature = float(os.getenv("OPENAI_TEMPERATURE", cls.temperature))

        max_tokens_str = os.getenv("OPENAI_MAX_TOKENS")
        if max_tokens_str is not None:
            max_tokens = int(max_tokens_str)
        else:
            max_tokens = cls.get_max_tokens_for_model(model)

        reasoning_effort_str = os.getenv("OPENAI_REASONING_EFFORT")
        if reasoning_effort_str is None:
            reasoning_effort_str = os.getenv("OPENAI_VERBOSITY")

        try:
            reasoning_effort = (
                ReasoningEffort(reasoning_effort_str)
                if reasoning_effort_str is not None
                else ReasoningEffort.MEDIUM
            )
        except ValueError:
            reasoning_effort = ReasoningEffort.MEDIUM

        text_verbosity_str = os.getenv("OPENAI_TEXT_VERBOSITY")
        try:
            text_verbosity = (
                VerbosityLevel(text_verbosity_str)
                if text_verbosity_str is not None
                else VerbosityLevel.MEDIUM
            )
        except ValueError:
            text_verbosity = VerbosityLevel.MEDIUM

        return cls(
            model=model,
            temperature=temperature,
            reasoning_effort=reasoning_effort,
            text_verbosity=text_verbosity,
            max_tokens=max_tokens,
        )


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
