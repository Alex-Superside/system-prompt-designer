"""Tests for prompt_design_system.config.

Tests for LLMConfig, VerbosityLevel, and model-specific defaults.
"""

from __future__ import annotations

import pytest

from prompt_design_system.config import LLMConfig, VerbosityLevel


# ---------------------------------------------------------------------------
# VerbosityLevel Enum
# ---------------------------------------------------------------------------


class TestVerbosityLevel:
    """Test VerbosityLevel enum and its string values."""

    def test_low_value(self):
        """VerbosityLevel.LOW has value 'low'."""
        assert VerbosityLevel.LOW.value == "low"

    def test_medium_value(self):
        """VerbosityLevel.MEDIUM has value 'medium'."""
        assert VerbosityLevel.MEDIUM.value == "medium"

    def test_high_value(self):
        """VerbosityLevel.HIGH has value 'high'."""
        assert VerbosityLevel.HIGH.value == "high"

    def test_create_from_string(self):
        """VerbosityLevel can be created from string values."""
        assert VerbosityLevel("low") == VerbosityLevel.LOW
        assert VerbosityLevel("medium") == VerbosityLevel.MEDIUM
        assert VerbosityLevel("high") == VerbosityLevel.HIGH

    def test_invalid_string_raises_error(self):
        """Creating VerbosityLevel from invalid string raises ValueError."""
        with pytest.raises(ValueError):
            VerbosityLevel("invalid")  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# LLMConfig Defaults
# ---------------------------------------------------------------------------


class TestLLMConfigDefaults:
    """Test LLMConfig default values and initialization."""

    def test_default_model_is_gpt52_mini(self):
        """Default model is gpt-5.2-mini."""
        config = LLMConfig()
        assert config.model == "gpt-5.2-mini"

    def test_default_temperature(self):
        """Default temperature is 0.7."""
        config = LLMConfig()
        assert config.temperature == 0.7

    def test_default_max_tokens_is_1500(self):
        """Default max_tokens is 1500 (reduced from 2000 for gpt-5.2-mini)."""
        config = LLMConfig()
        assert config.max_tokens == 1500

    def test_default_verbosity_is_medium(self):
        """Default verbosity is MEDIUM."""
        config = LLMConfig()
        assert config.verbosity == VerbosityLevel.MEDIUM

    def test_custom_model(self):
        """Custom model can be set during initialization."""
        config = LLMConfig(model="gpt-4o")
        assert config.model == "gpt-4o"

    def test_custom_verbosity(self):
        """Custom verbosity can be set during initialization."""
        config = LLMConfig(verbosity=VerbosityLevel.HIGH)
        assert config.verbosity == VerbosityLevel.HIGH

    def test_custom_max_tokens(self):
        """Custom max_tokens can be set during initialization."""
        config = LLMConfig(max_tokens=2000)
        assert config.max_tokens == 2000


# ---------------------------------------------------------------------------
# Model-Specific Max Tokens Logic
# ---------------------------------------------------------------------------


class TestGetMaxTokensForModel:
    """Test the get_max_tokens_for_model() static method."""

    def test_gpt54_returns_1500(self):
        """gpt-5.4 returns 1500 tokens."""
        assert LLMConfig.get_max_tokens_for_model("gpt-5.4") == 1500

    def test_gpt54_pro_returns_1500(self):
        """gpt-5.4-pro returns 1500 tokens."""
        assert LLMConfig.get_max_tokens_for_model("gpt-5.4-pro") == 1500

    def test_gpt5_mini_returns_1500(self):
        """gpt-5-mini returns 1500 tokens."""
        assert LLMConfig.get_max_tokens_for_model("gpt-5-mini") == 1500

    def test_gpt52_mini_returns_1500(self):
        """gpt-5.2-mini returns 1500 tokens."""
        assert LLMConfig.get_max_tokens_for_model("gpt-5.2-mini") == 1500

    def test_gpt4o_returns_2000(self):
        """gpt-4o returns 2000 tokens."""
        assert LLMConfig.get_max_tokens_for_model("gpt-4o") == 2000

    def test_gpt4_turbo_returns_2000(self):
        """gpt-4-turbo returns 2000 tokens."""
        assert LLMConfig.get_max_tokens_for_model("gpt-4-turbo") == 2000

    def test_unknown_model_defaults_to_2000(self):
        """Unknown model names default to 2000 tokens."""
        assert LLMConfig.get_max_tokens_for_model("unknown-model") == 2000

    def test_empty_string_defaults_to_2000(self):
        """Empty model name defaults to 2000 tokens."""
        assert LLMConfig.get_max_tokens_for_model("") == 2000


# ---------------------------------------------------------------------------
# LLMConfig.from_env()
# ---------------------------------------------------------------------------


class TestLLMConfigFromEnv:
    """Test loading LLMConfig from environment variables."""

    def test_defaults_when_no_env_vars(self, monkeypatch: pytest.MonkeyPatch):
        """from_env() returns defaults when no environment variables are set."""
        monkeypatch.delenv("OPENAI_MODEL", raising=False)
        monkeypatch.delenv("OPENAI_TEMPERATURE", raising=False)
        monkeypatch.delenv("OPENAI_MAX_TOKENS", raising=False)
        monkeypatch.delenv("OPENAI_VERBOSITY", raising=False)

        config = LLMConfig.from_env()

        assert config.model == "gpt-5.2-mini"
        assert config.temperature == 0.7
        assert config.max_tokens == 1500
        assert config.verbosity == VerbosityLevel.MEDIUM

    def test_overrides_from_env_vars(self, monkeypatch: pytest.MonkeyPatch):
        """from_env() reads environment variable overrides."""
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
        monkeypatch.setenv("OPENAI_TEMPERATURE", "0.5")
        monkeypatch.setenv("OPENAI_VERBOSITY", "low")

        config = LLMConfig.from_env()

        assert config.model == "gpt-4o"
        assert config.temperature == 0.5
        assert config.verbosity == VerbosityLevel.LOW

    def test_max_tokens_from_env_variable(self, monkeypatch: pytest.MonkeyPatch):
        """from_env() reads OPENAI_MAX_TOKENS when explicitly set."""
        monkeypatch.setenv("OPENAI_MAX_TOKENS", "3000")

        config = LLMConfig.from_env()

        assert config.max_tokens == 3000

    def test_max_tokens_auto_selected_for_model(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        """from_env() auto-selects max_tokens based on model when not explicitly set."""
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
        monkeypatch.delenv("OPENAI_MAX_TOKENS", raising=False)

        config = LLMConfig.from_env()

        assert config.max_tokens == 2000  # gpt-4o default

    def test_invalid_verbosity_falls_back_to_default(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        """from_env() falls back to MEDIUM if OPENAI_VERBOSITY is invalid."""
        monkeypatch.setenv("OPENAI_VERBOSITY", "invalid_level")

        config = LLMConfig.from_env()

        assert config.verbosity == VerbosityLevel.MEDIUM

    def test_frozen_dataclass(self):
        """LLMConfig is immutable (frozen dataclass)."""
        config = LLMConfig()
        with pytest.raises((AttributeError, TypeError)):
            config.model = "gpt-4o"  # type: ignore[misc]
