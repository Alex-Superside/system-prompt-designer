"""LLM provider implementations for the prompt design system.

Each provider implements the LLMClient Protocol defined in agents.py, which
requires a single ``generate(prompt, *, model=None) -> str`` method.

Adding a new provider means creating a class here and wiring it in cli.py.
Nothing else in the package needs to change (open/closed against the Protocol).
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from .config import LLMConfig, VerbosityLevel


@dataclass(frozen=True)
class UsageMetadata:
    """Token usage reported by the provider after a completion call."""

    input_tokens: int
    output_tokens: int
    total_tokens: int


class OpenAIProvider:
    """LLMClient implementation backed by the OpenAI Chat Completions API.

    The provider is intentionally thin: it owns authentication, model
    selection, and a single blocking HTTP round-trip.  All prompt composition
    stays in the caller (DesignAgent) so that this class has no awareness of
    domain concepts.

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
        verbosity: VerbosityLevel | None = None,
        llm_config: LLMConfig | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        config = llm_config or LLMConfig.from_env()
        self.model = model or config.model
        self.verbosity = verbosity or config.verbosity
        self._config = config

    def _get_api_params(self, effective_model: str) -> dict:
        """Build API parameters, conditionally including reasoning_effort for gpt-5.x models."""
        params = {
            "model": effective_model,
            "messages": [],  # Will be set by caller
            "temperature": self._config.temperature,
            "max_tokens": self._config.max_tokens,
        }

        # Add reasoning_effort only for gpt-5.x models
        if effective_model.startswith("gpt-5"):
            params["reasoning_effort"] = self.verbosity.value

        return params

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
            params = self._get_api_params(effective_model)
            params["messages"] = [{"role": "user", "content": prompt}]
            response = client.chat.completions.create(**params)
        except OpenAIError as exc:
            raise RuntimeError(f"OpenAI API call failed: {exc}") from exc

        return response.choices[0].message.content or ""

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
            params = self._get_api_params(effective_model)
            params["messages"] = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ]
            response = client.chat.completions.create(**params)
        except OpenAIError as exc:
            raise RuntimeError(f"OpenAI API call failed: {exc}") from exc

        text = response.choices[0].message.content or ""
        usage = response.usage
        metadata = UsageMetadata(
            input_tokens=usage.prompt_tokens if usage else 0,
            output_tokens=usage.completion_tokens if usage else 0,
            total_tokens=usage.total_tokens if usage else 0,
        )
        return text, metadata
