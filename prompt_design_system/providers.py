"""LLM provider implementations for the prompt design system.

Each provider implements the LLMClient Protocol defined in agents.py, which
requires a single ``generate(prompt, *, model=None) -> str`` method.

Adding a new provider means creating a class here and wiring it in cli.py.
Nothing else in the package needs to change (open/closed against the Protocol).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from .config import LLMConfig, ReasoningEffort, VerbosityLevel


@dataclass(frozen=True)
class UsageMetadata:
    """Token usage reported by the provider after a completion call."""

    input_tokens: int
    output_tokens: int
    total_tokens: int


class OpenAIProvider:
    """LLMClient implementation backed by OpenAI APIs.

    The provider is intentionally thin: it owns authentication, model
    selection, and a single blocking HTTP round-trip.  All prompt composition
    stays in the caller (DesignAgent) so that this class has no awareness of
    domain concepts. GPT-5.x models use the Responses API so they can honor
    reasoning effort and text verbosity. Older models remain on Chat
    Completions for backward compatibility.

    Common model names (as of March 2026):
        gpt-5-mini      — default; cost-efficient reasoning with gpt-5 quality
        gpt-5.4         — full gpt-5 reasoning model
        gpt-5.4-pro     — professional variant with enhanced capacity
        gpt-4o          — previous generation; no reasoning_effort support

    A ``NotFoundError`` from OpenAI most often means the model name is wrong
    or your account does not have access to that model tier.

    Usage::

        provider = OpenAIProvider()          # reads OPENAI_API_KEY from env
        text = provider.generate("Hello?")
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        reasoning_effort: ReasoningEffort | None = None,
        text_verbosity: VerbosityLevel | None = None,
        llm_config: LLMConfig | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        config = llm_config or LLMConfig.from_env()
        self.model = model or config.model
        self.reasoning_effort = reasoning_effort or config.reasoning_effort
        self.text_verbosity = text_verbosity or config.text_verbosity
        self._config = config

    @staticmethod
    def _uses_responses_api(model_name: str) -> bool:
        """Return True when the model should use the Responses API."""
        return model_name.startswith("gpt-5")

    def _create_responses_api_response(
        self,
        client: Any,
        *,
        effective_model: str,
        input_value: str | list[dict[str, str]],
    ) -> Any:
        """Send a Responses API request for GPT-5 family models."""
        if self.reasoning_effort == ReasoningEffort.NONE:
            return client.responses.create(
                model=effective_model,
                input=input_value,
                reasoning={"effort": self.reasoning_effort.value},
                text={"verbosity": self.text_verbosity.value},
                max_output_tokens=self._config.max_tokens,
                temperature=self._config.temperature,
            )

        return client.responses.create(
            model=effective_model,
            input=input_value,
            reasoning={"effort": self.reasoning_effort.value},
            text={"verbosity": self.text_verbosity.value},
            max_output_tokens=self._config.max_tokens,
        )

    def _create_chat_completion_response(
        self,
        client: Any,
        *,
        effective_model: str,
        messages: list[dict[str, str]],
    ) -> Any:
        """Send a Chat Completions request for legacy-compatible models."""
        return client.chat.completions.create(
            model=effective_model,
            messages=messages,
            temperature=self._config.temperature,
            max_tokens=self._config.max_tokens,
        )

    @staticmethod
    def _extract_response_text(response: object) -> str:
        """Extract plain text from either API response shape."""
        output_text = getattr(response, "output_text", None)
        if isinstance(output_text, str):
            return output_text

        choices = getattr(response, "choices", None)
        if choices:
            return choices[0].message.content or ""

        return ""

    @staticmethod
    def _build_usage_metadata(usage: object | None) -> UsageMetadata:
        """Normalize token usage from either API surface."""
        if usage is None:
            return UsageMetadata(input_tokens=0, output_tokens=0, total_tokens=0)

        input_tokens = getattr(usage, "input_tokens", None)
        output_tokens = getattr(usage, "output_tokens", None)

        if not isinstance(input_tokens, int):
            input_tokens = getattr(usage, "prompt_tokens", 0)
        if not isinstance(output_tokens, int):
            output_tokens = getattr(usage, "completion_tokens", 0)

        total_tokens = getattr(usage, "total_tokens", input_tokens + output_tokens)
        if not isinstance(total_tokens, int):
            total_tokens = input_tokens + output_tokens

        return UsageMetadata(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
        )

    def generate(self, prompt: str, *, model: str | None = None) -> str:
        """Send *prompt* to OpenAI and return the assistant's reply as a string.

        Args:
            prompt: The full prompt text to send as a user message.
            model: Override the instance-level model for this call only.

        Returns:
            The raw text content of the first completion choice.

        Raises:
            RuntimeError: Wraps any OpenAI API error with a clean message so
                callers can distinguish API failures from other exceptions.
        """
        from openai import OpenAI, OpenAIError

        effective_model = model or self.model
        client = OpenAI(api_key=self.api_key)

        try:
            if self._uses_responses_api(effective_model):
                response = self._create_responses_api_response(
                    client,
                    effective_model=effective_model,
                    input_value=prompt,
                )
            else:
                response = self._create_chat_completion_response(
                    client,
                    effective_model=effective_model,
                    messages=[{"role": "user", "content": prompt}],
                )
        except OpenAIError as exc:
            raise RuntimeError(f"OpenAI API call failed: {exc}") from exc

        return self._extract_response_text(response)

    def generate_with_system(
        self,
        system_prompt: str,
        user_message: str,
        *,
        model: str | None = None,
    ) -> tuple[str, UsageMetadata]:
        """Send a two-role conversation to OpenAI and return the reply with usage data.

        Unlike ``generate``, this method separates the system and user roles so
        callers can test a saved system prompt against an arbitrary user message
        without conflating the two into a single prompt string.

        Args:
            system_prompt: Content for the ``system`` role message.
            user_message: Content for the ``user`` role message.
            model: Override the instance-level model for this call only.

        Returns:
            A tuple of (response text, UsageMetadata).

        Raises:
            RuntimeError: Wraps any OpenAI API error with a clean message.
        """
        from openai import OpenAI, OpenAIError

        effective_model = model or self.model
        client = OpenAI(api_key=self.api_key)

        try:
            if self._uses_responses_api(effective_model):
                response = self._create_responses_api_response(
                    client,
                    effective_model=effective_model,
                    input_value=[
                        {"role": "system", "type": "message", "content": system_prompt},
                        {"role": "user", "type": "message", "content": user_message},
                    ],
                )
            else:
                response = self._create_chat_completion_response(
                    client,
                    effective_model=effective_model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message},
                    ],
                )
        except OpenAIError as exc:
            raise RuntimeError(f"OpenAI API call failed: {exc}") from exc

        text = self._extract_response_text(response)
        metadata = self._build_usage_metadata(getattr(response, "usage", None))
        return text, metadata
