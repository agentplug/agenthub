"""Cloud provider routed through LiteLLM.

One instance per cloud vendor ("openai", "anthropic", ...). LiteLLM is
imported lazily so ``agenthub.core.llm`` never requires it at import time;
without it (or without an API key) the provider reports unavailable.

JSON mode: whether ``response_format`` is forwarded depends on what LiteLLM
reports the model supports. When it doesn't, the base class's instruction
injection takes over — every provider then still honors ``json_mode``.
"""

import logging
import os
from collections.abc import Sequence
from typing import Any

from ..base import LLMProvider
from ..errors import LLMGenerationError, LLMUnavailableError
from ..types import (
    ChatRequest,
    ChatResponse,
    ModelDescriptor,
    ProviderCapabilities,
)

logger = logging.getLogger(__name__)

# Vendors whose conventional env var differs from {NAME}_API_KEY, or that
# accept several. First present candidate wins.
_API_KEY_VARS: dict[str, tuple[str, ...]] = {
    "gemini": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
}


def _import_litellm() -> Any:
    try:
        import litellm
    except ImportError as e:
        raise LLMUnavailableError(
            "LiteLLM is not installed; cloud providers are unavailable",
            suggestions=["pip install litellm"],
        ) from e
    return litellm


class LiteLLMCloudProvider(LLMProvider):
    """A single cloud vendor behind LiteLLM (e.g. ``openai``, ``anthropic``)."""

    def __init__(self, provider: str, default_models: Sequence[str]) -> None:
        self.name = provider
        self._default_models = tuple(default_models)
        self._api_key_vars = _API_KEY_VARS.get(
            provider, (f"{provider.upper()}_API_KEY",)
        )
        # Tri-state cache: None = not yet checked against LiteLLM.
        self._native_json: bool | None = None

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            native_json=self._supports_response_format(),
            model_listing=False,
            is_local=False,
        )

    def _supports_response_format(self) -> bool:
        if self._native_json is None:
            try:
                litellm = _import_litellm()
                params = litellm.get_supported_openai_params(
                    model=f"{self.name}/{self._default_models[0]}"
                )
                self._native_json = bool(params) and "response_format" in params
            except Exception:
                # Unknown model or LiteLLM missing: instruction injection is
                # the safe universal fallback.
                self._native_json = False
        return self._native_json

    def _resolve_api_key(self) -> str | None:
        for variable in self._api_key_vars:
            if value := os.getenv(variable):
                return value
        return None

    def is_available(self) -> bool:
        # Key presence only — no network call; cloud reachability problems
        # surface as errors at generation time.
        return self._resolve_api_key() is not None

    def list_models(self) -> list[ModelDescriptor]:
        return [
            ModelDescriptor(
                id=model_id,
                provider=self.name,
                is_local=False,
                metadata={"configured_default": True},
            )
            for model_id in self._default_models
        ]

    def _chat(self, request: ChatRequest) -> ChatResponse:
        litellm = _import_litellm()

        kwargs: dict[str, Any] = {
            "model": f"{self.name}/{request.model}",
            "messages": [
                {"role": message.role, "content": message.content}
                for message in request.messages
            ],
            "temperature": request.temperature,
            # Silently drop params a vendor doesn't accept instead of erroring.
            "drop_params": True,
        }
        if request.max_tokens is not None:
            kwargs["max_tokens"] = request.max_tokens
        if request.json_mode and self._supports_response_format():
            kwargs["response_format"] = {"type": "json_object"}
        # Pass the resolved key explicitly so alias variables (e.g.
        # GOOGLE_API_KEY for gemini) work even when LiteLLM would only
        # look up its own conventional name.
        if api_key := self._resolve_api_key():
            kwargs["api_key"] = api_key
        kwargs.update(request.extra)

        try:
            response = litellm.completion(**kwargs)
        except Exception as e:
            raise self._map_error(litellm, e) from e

        try:
            choice = response.choices[0]
            content = choice.message.content
        except (AttributeError, IndexError) as e:
            raise LLMGenerationError(
                f"Unexpected LiteLLM response shape from {self.name}: {e}"
            ) from e

        usage = None
        raw_usage = getattr(response, "usage", None)
        if raw_usage is not None:
            usage = {
                "prompt_tokens": getattr(raw_usage, "prompt_tokens", 0),
                "completion_tokens": getattr(raw_usage, "completion_tokens", 0),
            }

        return ChatResponse(
            content=content or "",
            model=request.model,
            provider=self.name,
            finish_reason=getattr(choice, "finish_reason", None),
            usage=usage,
            raw=response,
        )

    def _map_error(self, litellm: Any, error: Exception) -> Exception:
        """Map LiteLLM exceptions onto the LLM error hierarchy."""
        unavailable_types = tuple(
            exception_type
            for exception_type in (
                getattr(litellm.exceptions, name, None)
                for name in (
                    "AuthenticationError",
                    "APIConnectionError",
                    "Timeout",
                    "ServiceUnavailableError",
                )
            )
            if exception_type is not None
        )
        if isinstance(error, unavailable_types):
            return LLMUnavailableError(f"{self.name} unavailable: {error}")
        return LLMGenerationError(f"{self.name} generation failed: {error}")
