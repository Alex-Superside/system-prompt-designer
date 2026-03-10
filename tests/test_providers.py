"""Tests for prompt_design_system.providers."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from prompt_design_system.config import ReasoningEffort, VerbosityLevel
from prompt_design_system.providers import OpenAIProvider, UsageMetadata


class TestUsageMetadata:
    def test_fields_are_accessible(self):
        meta = UsageMetadata(input_tokens=10, output_tokens=5, total_tokens=15)
        assert meta.input_tokens == 10
        assert meta.output_tokens == 5
        assert meta.total_tokens == 15

    def test_frozen_dataclass(self):
        meta = UsageMetadata(input_tokens=1, output_tokens=1, total_tokens=2)
        with pytest.raises((AttributeError, TypeError)):
            meta.input_tokens = 99  # type: ignore[misc]


class TestOpenAIProviderInit:
    def test_defaults_come_from_llm_config(self):
        provider = OpenAIProvider(api_key="sk-test")
        assert provider.model == "gpt-5-mini"
        assert provider.reasoning_effort == ReasoningEffort.MEDIUM
        assert provider.text_verbosity == VerbosityLevel.MEDIUM

    def test_api_key_can_come_from_environment(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setenv("OPENAI_API_KEY", "sk-from-env")
        provider = OpenAIProvider()
        assert provider.api_key == "sk-from-env"


class ProviderResponseFactory:
    @staticmethod
    def chat_response(content: str | None, input_tokens: int = 100, output_tokens: int = 50):
        choice = MagicMock()
        choice.message.content = content

        usage = MagicMock()
        usage.prompt_tokens = input_tokens
        usage.completion_tokens = output_tokens
        usage.total_tokens = input_tokens + output_tokens

        response = MagicMock()
        response.choices = [choice]
        response.usage = usage
        return response

    @staticmethod
    def responses_api_response(
        content: str,
        input_tokens: int = 100,
        output_tokens: int = 50,
    ):
        usage = MagicMock()
        usage.input_tokens = input_tokens
        usage.output_tokens = output_tokens
        usage.total_tokens = input_tokens + output_tokens

        response = MagicMock()
        response.output_text = content
        response.usage = usage
        return response


class TestGenerateWithResponsesApi:
    def test_gpt5_models_use_responses_api(self):
        provider = OpenAIProvider(
            api_key="sk-test",
            model="gpt-5.4",
            reasoning_effort=ReasoningEffort.HIGH,
            text_verbosity=VerbosityLevel.LOW,
        )
        mock_response = ProviderResponseFactory.responses_api_response("Hello from responses.")

        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.responses.create.return_value = mock_response
            mock_openai_cls.return_value = mock_client

            result = provider.generate("Test prompt.")

        assert result == "Hello from responses."
        call_kwargs = mock_client.responses.create.call_args.kwargs
        assert call_kwargs["model"] == "gpt-5.4"
        assert call_kwargs["input"] == "Test prompt."
        assert call_kwargs["reasoning"] == {"effort": "high"}
        assert call_kwargs["text"] == {"verbosity": "low"}
        assert call_kwargs["max_output_tokens"] == 1500

    def test_reasoning_none_includes_temperature(self):
        provider = OpenAIProvider(
            api_key="sk-test",
            model="gpt-5.4",
            reasoning_effort=ReasoningEffort.NONE,
        )
        mock_response = ProviderResponseFactory.responses_api_response("ok")

        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.responses.create.return_value = mock_response
            mock_openai_cls.return_value = mock_client

            provider.generate("prompt")

        call_kwargs = mock_client.responses.create.call_args.kwargs
        assert call_kwargs["temperature"] == 0.7

    def test_openai_error_raises_runtime_error(self):
        from openai import OpenAIError

        provider = OpenAIProvider(api_key="sk-test", model="gpt-5.4")

        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.responses.create.side_effect = OpenAIError("API down")
            mock_openai_cls.return_value = mock_client

            with pytest.raises(RuntimeError, match="OpenAI API call failed"):
                provider.generate("prompt")


class TestGenerateWithChatCompletions:
    def test_non_gpt5_models_stay_on_chat_completions(self):
        provider = OpenAIProvider(api_key="sk-test", model="gpt-4o")
        mock_response = ProviderResponseFactory.chat_response("Hello from chat.")

        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_cls.return_value = mock_client

            result = provider.generate("Test prompt.")

        assert result == "Hello from chat."
        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["model"] == "gpt-4o"
        assert call_kwargs["messages"] == [{"role": "user", "content": "Test prompt."}]
        assert "reasoning" not in call_kwargs
        assert "text" not in call_kwargs

    def test_none_chat_content_returns_empty_string(self):
        provider = OpenAIProvider(api_key="sk-test", model="gpt-4o")
        mock_response = ProviderResponseFactory.chat_response(None)

        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_cls.return_value = mock_client

            result = provider.generate("prompt")

        assert result == ""


class TestGenerateWithSystemUsingResponsesApi:
    def test_generate_with_system_uses_message_items_for_gpt5(self):
        provider = OpenAIProvider(
            api_key="sk-test",
            model="gpt-5.4",
            reasoning_effort=ReasoningEffort.HIGH,
            text_verbosity=VerbosityLevel.HIGH,
        )
        mock_response = ProviderResponseFactory.responses_api_response("System reply.")

        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.responses.create.return_value = mock_response
            mock_openai_cls.return_value = mock_client

            text, metadata = provider.generate_with_system("System.", "User message.")

        assert text == "System reply."
        assert metadata == UsageMetadata(input_tokens=100, output_tokens=50, total_tokens=150)

        call_kwargs = mock_client.responses.create.call_args.kwargs
        assert call_kwargs["reasoning"] == {"effort": "high"}
        assert call_kwargs["text"] == {"verbosity": "high"}
        assert call_kwargs["input"] == [
            {"role": "system", "type": "message", "content": "System."},
            {"role": "user", "type": "message", "content": "User message."},
        ]

    def test_missing_usage_defaults_to_zero(self):
        provider = OpenAIProvider(api_key="sk-test", model="gpt-5.4")
        mock_response = MagicMock()
        mock_response.output_text = "reply"
        mock_response.usage = None

        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.responses.create.return_value = mock_response
            mock_openai_cls.return_value = mock_client

            _, metadata = provider.generate_with_system("sys", "user")

        assert metadata == UsageMetadata(input_tokens=0, output_tokens=0, total_tokens=0)


class TestGenerateWithSystemUsingChatCompletions:
    def test_generate_with_system_keeps_chat_path_for_gpt4o(self):
        provider = OpenAIProvider(api_key="sk-test", model="gpt-4o")
        mock_response = ProviderResponseFactory.chat_response("System reply.")

        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create.return_value = mock_response
            mock_openai_cls.return_value = mock_client

            text, metadata = provider.generate_with_system("Be helpful.", "Hello.")

        assert text == "System reply."
        assert metadata == UsageMetadata(input_tokens=100, output_tokens=50, total_tokens=150)

        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["messages"] == [
            {"role": "system", "content": "Be helpful."},
            {"role": "user", "content": "Hello."},
        ]

    def test_chat_openai_error_raises_runtime_error(self):
        from openai import OpenAIError

        provider = OpenAIProvider(api_key="sk-test", model="gpt-4o")

        with patch("openai.OpenAI") as mock_openai_cls:
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = OpenAIError("timeout")
            mock_openai_cls.return_value = mock_client

            with pytest.raises(RuntimeError, match="OpenAI API call failed"):
                provider.generate_with_system("sys", "user")
