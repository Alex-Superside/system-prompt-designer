"""Tests for prompt_design_system.providers.

All tests mock the OpenAI SDK so no network calls are made.  The goal is
to verify that OpenAIProvider correctly assembles API requests, parses
responses, wraps errors, and reads the API key from the environment.
"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from prompt_design_system.providers import OpenAIProvider, UsageMetadata

# ---------------------------------------------------------------------------
# UsageMetadata
# ---------------------------------------------------------------------------


class TestUsageMetadata:
    def test_fields_are_accessible(self):
        """All three token count fields can be read after construction."""
        meta = UsageMetadata(input_tokens=10, output_tokens=5, total_tokens=15)
        assert meta.input_tokens == 10
        assert meta.output_tokens == 5
        assert meta.total_tokens == 15

    def test_frozen_dataclass(self):
        """UsageMetadata is immutable — attribute assignment raises."""
        meta = UsageMetadata(input_tokens=1, output_tokens=1, total_tokens=2)
        with pytest.raises((AttributeError, TypeError)):
            meta.input_tokens = 99  # type: ignore[misc]


# ---------------------------------------------------------------------------
# OpenAIProvider initialisation
# ---------------------------------------------------------------------------


class TestOpenAIProviderInit:
    def test_default_model(self):
        """Default model is gpt-5-mini."""
        provider = OpenAIProvider(api_key="sk-test")
        assert provider.model == "gpt-5-mini"

    def test_custom_model(self):
        """A custom model name is stored and used."""
        provider = OpenAIProvider(api_key="sk-test", model="gpt-3.5-turbo")
        assert provider.model == "gpt-3.5-turbo"

    def test_api_key_from_argument(self):
        """api_key passed directly is stored on the instance."""
        provider = OpenAIProvider(api_key="sk-explicit")
        assert provider.api_key == "sk-explicit"

    def test_api_key_from_environment(self, monkeypatch: pytest.MonkeyPatch):
        """api_key falls back to OPENAI_API_KEY environment variable."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-from-env")
        provider = OpenAIProvider()
        assert provider.api_key == "sk-from-env"

    def test_no_api_key_resolves_to_none(self, monkeypatch: pytest.MonkeyPatch):
        """When neither argument nor env var is set, api_key is None."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        provider = OpenAIProvider()
        assert provider.api_key is None


# ---------------------------------------------------------------------------
# OpenAIProvider.generate()
# ---------------------------------------------------------------------------


class TestOpenAIProviderGenerate:
    def _make_mock_response(self, content: str):
        """Build the minimal mock OpenAI response object."""
        choice = MagicMock()
        choice.message.content = content
        response = MagicMock()
        response.choices = [choice]
        return response

    def test_returns_content_string(self):
        """generate() returns the text content from the first choice."""
        provider = OpenAIProvider(api_key="sk-test")
        mock_response = self._make_mock_response("Hello from the model.")

        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_cls.return_value = mock_client

            result = provider.generate("Test prompt.")

        assert result == "Hello from the model."

    def test_passes_prompt_as_user_message(self):
        """generate() sends the prompt as a user role message."""
        provider = OpenAIProvider(api_key="sk-test")
        mock_response = self._make_mock_response("ok")

        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_cls.return_value = mock_client

            provider.generate("My special prompt.")

            call_kwargs = mock_client.chat.completions.create.call_args
            messages = call_kwargs.kwargs["messages"]
            assert messages[0]["role"] == "user"
            assert messages[0]["content"] == "My special prompt."

    def test_uses_instance_model_by_default(self):
        """generate() uses the model set at construction time."""
        provider = OpenAIProvider(api_key="sk-test", model="gpt-3.5-turbo")
        mock_response = self._make_mock_response("ok")

        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_cls.return_value = mock_client

            provider.generate("prompt")

            call_kwargs = mock_client.chat.completions.create.call_args
            assert call_kwargs.kwargs["model"] == "gpt-3.5-turbo"

    def test_model_override_per_call(self):
        """The model keyword argument overrides the instance model for one call."""
        provider = OpenAIProvider(api_key="sk-test", model="gpt-4o")
        mock_response = self._make_mock_response("ok")

        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_cls.return_value = mock_client

            provider.generate("prompt", model="gpt-3.5-turbo")

            call_kwargs = mock_client.chat.completions.create.call_args
            assert call_kwargs.kwargs["model"] == "gpt-3.5-turbo"

    def test_openai_error_raises_runtime_error(self):
        """Any OpenAIError is caught and re-raised as RuntimeError."""
        from openai import OpenAIError

        provider = OpenAIProvider(api_key="sk-test")

        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = OpenAIError("API down")
            mock_openai_cls.return_value = mock_client

            with pytest.raises(RuntimeError, match="OpenAI API call failed"):
                provider.generate("prompt")

    def test_empty_content_returns_empty_string(self):
        """When the model returns None content, generate() returns an empty string."""
        provider = OpenAIProvider(api_key="sk-test")
        mock_response = self._make_mock_response(None)  # type: ignore[arg-type]

        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_cls.return_value = mock_client

            result = provider.generate("prompt")

        assert result == ""


# ---------------------------------------------------------------------------
# OpenAIProvider.generate_with_system()
# ---------------------------------------------------------------------------


class TestOpenAIProviderGenerateWithSystem:
    def _make_mock_response(self, content: str, input_t=100, output_t=50):
        """Build a mock response with usage metadata."""
        choice = MagicMock()
        choice.message.content = content
        usage = MagicMock()
        usage.prompt_tokens = input_t
        usage.completion_tokens = output_t
        usage.total_tokens = input_t + output_t
        response = MagicMock()
        response.choices = [choice]
        response.usage = usage
        return response

    def test_returns_text_and_metadata(self):
        """generate_with_system() returns (text, UsageMetadata) tuple."""
        provider = OpenAIProvider(api_key="sk-test")
        mock_response = self._make_mock_response("System reply.", 100, 50)

        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_cls.return_value = mock_client

            text, meta = provider.generate_with_system("System.", "User message.")

        assert text == "System reply."
        assert isinstance(meta, UsageMetadata)
        assert meta.input_tokens == 100
        assert meta.output_tokens == 50
        assert meta.total_tokens == 150

    def test_sends_system_and_user_messages(self):
        """generate_with_system() sends both roles in the correct order."""
        provider = OpenAIProvider(api_key="sk-test")
        mock_response = self._make_mock_response("ok")

        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_cls.return_value = mock_client

            provider.generate_with_system("Be helpful.", "Hello.")

            call_kwargs = mock_client.chat.completions.create.call_args
            messages = call_kwargs.kwargs["messages"]
            assert messages[0] == {"role": "system", "content": "Be helpful."}
            assert messages[1] == {"role": "user", "content": "Hello."}

    def test_openai_error_raises_runtime_error(self):
        """OpenAIError in generate_with_system() raises RuntimeError."""
        from openai import OpenAIError

        provider = OpenAIProvider(api_key="sk-test")

        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = OpenAIError("timeout")
            mock_openai_cls.return_value = mock_client

            with pytest.raises(RuntimeError, match="OpenAI API call failed"):
                provider.generate_with_system("sys", "user")

    def test_missing_usage_defaults_to_zero(self):
        """When response.usage is None, all token counts default to 0."""
        provider = OpenAIProvider(api_key="sk-test")

        choice = MagicMock()
        choice.message.content = "reply"
        mock_response = MagicMock()
        mock_response.choices = [choice]
        mock_response.usage = None

        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_cls.return_value = mock_client

            _, meta = provider.generate_with_system("sys", "user")

        assert meta.input_tokens == 0
        assert meta.output_tokens == 0
        assert meta.total_tokens == 0


# ---------------------------------------------------------------------------
# Reasoning Effort (GPT-5.x Feature)
# ---------------------------------------------------------------------------


class TestReasoningEffort:
    """Test reasoning_effort parameter handling for gpt-5.x models."""

    def _make_mock_response(self, content: str):
        """Build the minimal mock OpenAI response object."""
        choice = MagicMock()
        choice.message.content = content
        response = MagicMock()
        response.choices = [choice]
        return response

    def test_gpt5_4_includes_reasoning_effort_in_generate(self):
        """generate() includes reasoning_effort for gpt-5.4 models."""
        from prompt_design_system.config import VerbosityLevel

        provider = OpenAIProvider(
            api_key="sk-test",
            model="gpt-5.4",
            verbosity=VerbosityLevel.HIGH,
        )
        mock_response = self._make_mock_response("ok")

        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_cls.return_value = mock_client

            provider.generate("prompt")

            call_kwargs = mock_client.chat.completions.create.call_args
            assert call_kwargs.kwargs["reasoning_effort"] == "high"

    def test_gpt5_4pro_includes_reasoning_effort(self):
        """generate() includes reasoning_effort for gpt-5.4-pro models."""
        from prompt_design_system.config import VerbosityLevel

        provider = OpenAIProvider(
            api_key="sk-test",
            model="gpt-5.4-pro",
            verbosity=VerbosityLevel.MEDIUM,
        )
        mock_response = self._make_mock_response("ok")

        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_cls.return_value = mock_client

            provider.generate("prompt")

            call_kwargs = mock_client.chat.completions.create.call_args
            assert call_kwargs.kwargs["reasoning_effort"] == "medium"

    def test_gpt5_mini_includes_reasoning_effort(self):
        """generate() includes reasoning_effort for gpt-5-mini models."""
        from prompt_design_system.config import VerbosityLevel

        provider = OpenAIProvider(
            api_key="sk-test",
            model="gpt-5-mini",
            verbosity=VerbosityLevel.LOW,
        )
        mock_response = self._make_mock_response("ok")

        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_cls.return_value = mock_client

            provider.generate("prompt")

            call_kwargs = mock_client.chat.completions.create.call_args
            assert call_kwargs.kwargs["reasoning_effort"] == "low"

    def test_gpt4o_omits_reasoning_effort(self):
        """generate() does NOT include reasoning_effort for gpt-4o models."""
        from prompt_design_system.config import VerbosityLevel

        provider = OpenAIProvider(
            api_key="sk-test",
            model="gpt-4o",
            verbosity=VerbosityLevel.HIGH,
        )
        mock_response = self._make_mock_response("ok")

        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_cls.return_value = mock_client

            provider.generate("prompt")

            call_kwargs = mock_client.chat.completions.create.call_args
            assert "reasoning_effort" not in call_kwargs.kwargs

    def test_gpt4_turbo_omits_reasoning_effort(self):
        """generate() does NOT include reasoning_effort for gpt-4-turbo models."""
        from prompt_design_system.config import VerbosityLevel

        provider = OpenAIProvider(
            api_key="sk-test",
            model="gpt-4-turbo",
            verbosity=VerbosityLevel.MEDIUM,
        )
        mock_response = self._make_mock_response("ok")

        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_cls.return_value = mock_client

            provider.generate("prompt")

            call_kwargs = mock_client.chat.completions.create.call_args
            assert "reasoning_effort" not in call_kwargs.kwargs

    def test_reasoning_effort_in_generate_with_system(self):
        """generate_with_system() also includes reasoning_effort for gpt-5.x."""
        from prompt_design_system.config import VerbosityLevel

        provider = OpenAIProvider(
            api_key="sk-test",
            model="gpt-5.4",
            verbosity=VerbosityLevel.HIGH,
        )

        choice = MagicMock()
        choice.message.content = "reply"
        usage = MagicMock()
        usage.prompt_tokens = 100
        usage.completion_tokens = 50
        usage.total_tokens = 150
        mock_response = MagicMock()
        mock_response.choices = [choice]
        mock_response.usage = usage

        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_cls.return_value = mock_client

            provider.generate_with_system("sys", "user")

            call_kwargs = mock_client.chat.completions.create.call_args
            assert call_kwargs.kwargs["reasoning_effort"] == "high"


# ---------------------------------------------------------------------------
# Model Variants
# ---------------------------------------------------------------------------


class TestModelVariants:
    """Test that different gpt-5.x model variants are accepted."""

    def _make_mock_response(self, content: str):
        """Build the minimal mock OpenAI response object."""
        choice = MagicMock()
        choice.message.content = content
        response = MagicMock()
        response.choices = [choice]
        return response

    def test_gpt54_model_accepted(self):
        """gpt-5.4 is accepted as a valid model name."""
        provider = OpenAIProvider(api_key="sk-test", model="gpt-5.4")
        assert provider.model == "gpt-5.4"

    def test_gpt54_pro_model_accepted(self):
        """gpt-5.4-pro is accepted as a valid model name."""
        provider = OpenAIProvider(api_key="sk-test", model="gpt-5.4-pro")
        assert provider.model == "gpt-5.4-pro"

    def test_gpt5_mini_model_accepted(self):
        """gpt-5-mini is accepted as a valid model name."""
        provider = OpenAIProvider(api_key="sk-test", model="gpt-5-mini")
        assert provider.model == "gpt-5-mini"
