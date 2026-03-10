"""Tests for prompt_design_system.config."""

from __future__ import annotations

import pytest

from prompt_design_system.config import LLMConfig, ReasoningEffort, VerbosityLevel


class TestReasoningEffort:
    def test_reasoning_effort_values_match_api(self):
        assert ReasoningEffort.NONE.value == "none"
        assert ReasoningEffort.LOW.value == "low"
        assert ReasoningEffort.MEDIUM.value == "medium"
        assert ReasoningEffort.HIGH.value == "high"
        assert ReasoningEffort.XHIGH.value == "xhigh"


class TestVerbosityLevel:
    def test_verbosity_values_match_api(self):
        assert VerbosityLevel.LOW.value == "low"
        assert VerbosityLevel.MEDIUM.value == "medium"
        assert VerbosityLevel.HIGH.value == "high"


class TestLLMConfigDefaults:
    def test_defaults_target_gpt5_responses_usage(self):
        config = LLMConfig()
        assert config.model == "gpt-5-mini"
        assert config.temperature == 0.7
        assert config.reasoning_effort == ReasoningEffort.MEDIUM
        assert config.text_verbosity == VerbosityLevel.MEDIUM
        assert config.max_tokens == 1500

    def test_config_is_frozen(self):
        config = LLMConfig()
        with pytest.raises((AttributeError, TypeError)):
            config.model = "gpt-4o"  # type: ignore[misc]


class TestGetMaxTokensForModel:
    @pytest.mark.parametrize(
        ("model_name", "expected_tokens"),
        [
            ("gpt-5.4", 1500),
            ("gpt-5.4-pro", 1500),
            ("gpt-5.2-mini", 1500),
            ("gpt-5-mini", 1500),
            ("gpt-4o", 2000),
            ("gpt-4-turbo", 2000),
            ("unknown-model", 2000),
            ("", 2000),
        ],
    )
    def test_model_family_token_defaults(self, model_name: str, expected_tokens: int):
        assert LLMConfig.get_max_tokens_for_model(model_name) == expected_tokens


class TestLLMConfigFromEnv:
    def test_defaults_when_environment_is_empty(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.delenv("OPENAI_MODEL", raising=False)
        monkeypatch.delenv("OPENAI_TEMPERATURE", raising=False)
        monkeypatch.delenv("OPENAI_MAX_TOKENS", raising=False)
        monkeypatch.delenv("OPENAI_REASONING_EFFORT", raising=False)
        monkeypatch.delenv("OPENAI_VERBOSITY", raising=False)
        monkeypatch.delenv("OPENAI_TEXT_VERBOSITY", raising=False)

        config = LLMConfig.from_env()

        assert config.model == "gpt-5-mini"
        assert config.temperature == 0.7
        assert config.reasoning_effort == ReasoningEffort.MEDIUM
        assert config.text_verbosity == VerbosityLevel.MEDIUM
        assert config.max_tokens == 1500

    def test_reads_all_supported_env_overrides(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("OPENAI_MODEL", "gpt-5.4")
        monkeypatch.setenv("OPENAI_TEMPERATURE", "0.5")
        monkeypatch.setenv("OPENAI_REASONING_EFFORT", "high")
        monkeypatch.setenv("OPENAI_TEXT_VERBOSITY", "low")
        monkeypatch.setenv("OPENAI_MAX_TOKENS", "3000")

        config = LLMConfig.from_env()

        assert config.model == "gpt-5.4"
        assert config.temperature == 0.5
        assert config.reasoning_effort == ReasoningEffort.HIGH
        assert config.text_verbosity == VerbosityLevel.LOW
        assert config.max_tokens == 3000

    def test_openai_verbosity_alias_maps_to_reasoning_effort(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.delenv("OPENAI_REASONING_EFFORT", raising=False)
        monkeypatch.setenv("OPENAI_VERBOSITY", "low")

        config = LLMConfig.from_env()

        assert config.reasoning_effort == ReasoningEffort.LOW

    def test_max_tokens_follow_model_when_not_explicit(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("OPENAI_MODEL", "gpt-4o")
        monkeypatch.delenv("OPENAI_MAX_TOKENS", raising=False)

        config = LLMConfig.from_env()

        assert config.max_tokens == 2000

    def test_invalid_reasoning_effort_falls_back_to_medium(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setenv("OPENAI_REASONING_EFFORT", "not-a-level")

        config = LLMConfig.from_env()

        assert config.reasoning_effort == ReasoningEffort.MEDIUM

    def test_invalid_text_verbosity_falls_back_to_medium(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setenv("OPENAI_TEXT_VERBOSITY", "not-a-level")

        config = LLMConfig.from_env()

        assert config.text_verbosity == VerbosityLevel.MEDIUM
