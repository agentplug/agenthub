"""LLM service: the one entry point consumers use for generation.

The service does three things — normalize input into messages, memoize the
(provider, model) selection, and delegate to the provider's ``chat()``. All
prompt handling lives in the provider layer; all failures raise
:class:`~agenthub.core.llm.errors.LLMError` subclasses (never fabricated
fallback strings).

Construction performs no network I/O; detection happens lazily on first use.
"""

import json
import logging
import threading
from typing import Any

from .base import LLMProvider
from .config import LLMConfig
from .errors import LLMError, LLMResponseFormatError
from .providers import build_providers
from .selection import ModelSelector
from .structured import extract_json_from_text
from .types import ChatRequest, Message, ModelDescriptor

logger = logging.getLogger(__name__)

_VALID_ROLES = ("system", "user", "assistant")


class LLMService:
    """Unified access to LLM generation across all configured providers.

    Args:
        config: Configuration; defaults to :meth:`LLMConfig.from_env`.
        providers: Explicit provider list (test seam); defaults to
            :func:`build_providers` on the config.
        model: Force a specific model as ``provider:model`` (e.g.
            ``ollama:qwen3:8b``); overrides config.forced_model.
    """

    def __init__(
        self,
        config: LLMConfig | None = None,
        providers: list[LLMProvider] | None = None,
        model: str | None = None,
    ) -> None:
        self._config = config if config is not None else LLMConfig.from_env()
        self._providers = (
            list(providers) if providers is not None else build_providers(self._config)
        )
        self._selector = ModelSelector(self._providers, self._config)
        self._forced_model = model or self._config.forced_model
        self._selected: tuple[LLMProvider, ModelDescriptor] | None = None
        self._selection_lock = threading.Lock()

    def _selection(self) -> tuple[LLMProvider, ModelDescriptor]:
        with self._selection_lock:
            selected = self._selected
            if selected is None:
                if self._forced_model:
                    selected = self._selector.resolve(self._forced_model)
                else:
                    selected = self._selector.select()
                self._selected = selected
            return selected

    def generate(
        self,
        input_data: str | list[dict],
        system_prompt: str | None = None,
        return_json: bool = False,
        temperature: float = 0.0,
        **kwargs: Any,
    ) -> str:
        """Generate a text response.

        Signature-compatible with the legacy ``CoreLLMService.generate``,
        with one intentional change: failures raise instead of returning a
        fabricated string.

        Args:
            input_data: A single prompt string, or a list of
                ``{"role": ..., "content": ...}`` messages.
            system_prompt: Optional system prompt prepended to the messages.
            return_json: Ask the model for a JSON-only response.
            temperature: Sampling temperature (0.0 = deterministic).
            **kwargs: Passed through to the provider transport.

        Raises:
            LLMUnavailableError: No provider/model is usable.
            LLMGenerationError: The request failed.
            ValueError: ``input_data`` is neither str nor list.
        """
        provider, descriptor = self._selection()
        request = ChatRequest(
            model=descriptor.id,
            messages=self._normalize_messages(input_data, system_prompt),
            temperature=temperature,
            json_mode=return_json,
            extra=kwargs,
        )
        return provider.chat(request).content

    def generate_structured(
        self,
        input_data: str | list[dict],
        system_prompt: str | None = None,
        temperature: float = 0.0,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate and parse a JSON object response.

        Raises:
            LLMResponseFormatError: The model's output contained no
                parseable JSON object (``raw_response`` carries the text).
        """
        text = self.generate(
            input_data,
            system_prompt=system_prompt,
            return_json=True,
            temperature=temperature,
            **kwargs,
        )
        try:
            return extract_json_from_text(text)
        except json.JSONDecodeError as e:
            raise LLMResponseFormatError(
                f"Model did not return parseable JSON: {e}", raw_response=text
            ) from e

    def get_current_model(self) -> str:
        """The selected model's qualified id, e.g. ``ollama:qwen3:32b``."""
        _, descriptor = self._selection()
        return descriptor.qualified_id

    def list_available_models(self) -> list[ModelDescriptor]:
        """All usable models across available providers, ranked."""
        return [descriptor for _, descriptor in self._selector.candidates()]

    def is_available(self) -> bool:
        """Whether any provider can serve generation right now."""
        try:
            self._selection()
            return True
        except LLMError:
            return False

    @staticmethod
    def _normalize_messages(
        input_data: object, system_prompt: str | None
    ) -> tuple[Message, ...]:
        # Typed as object: the runtime guard must stay reachable for
        # untyped callers passing the wrong thing.
        messages: list[Message] = []
        if system_prompt:
            messages.append(Message(role="system", content=system_prompt))
        if isinstance(input_data, str):
            messages.append(Message(role="user", content=input_data))
        elif isinstance(input_data, list):
            for entry in input_data:
                role = entry.get("role")
                if role in _VALID_ROLES:
                    messages.append(
                        Message(role=role, content=str(entry.get("content", "")))
                    )
        else:
            raise ValueError("input_data must be a string or a list of messages")
        return tuple(messages)
