"""Provider interface for the LLM layer.

``LLMProvider`` is an ABC rather than a Protocol: all providers are
first-party, and the template method :meth:`LLMProvider.chat` is the single
home for behavior every provider must share — JSON-mode emulation for
providers without native JSON support, and reasoning-tag stripping for
models that emit ``<think>...</think>`` blocks (deepseek-r1, qwen3, ...).
"""

import re
from abc import ABC, abstractmethod
from dataclasses import replace
from typing import ClassVar

from .types import (
    ChatRequest,
    ChatResponse,
    Message,
    ModelDescriptor,
    ProviderCapabilities,
)

_JSON_INSTRUCTION = "Please respond with valid JSON only, no additional text."

_THINK_BLOCK_RE = re.compile(r"<think>(.*?)</think>\s*", re.DOTALL)


def inject_json_instruction(request: ChatRequest) -> ChatRequest:
    """Append the JSON-only instruction to the last user message.

    Fallback for providers without native JSON mode. If the conversation has
    no user message, a new one carrying the instruction is appended.
    """
    messages = list(request.messages)
    for index in range(len(messages) - 1, -1, -1):
        if messages[index].role == "user":
            messages[index] = Message(
                role="user",
                content=f"{messages[index].content}\n\n{_JSON_INSTRUCTION}",
            )
            break
    else:
        messages.append(Message(role="user", content=_JSON_INSTRUCTION))
    return replace(request, messages=tuple(messages))


def strip_reasoning_tags(response: ChatResponse) -> ChatResponse:
    """Move ``<think>...</think>`` blocks out of content into reasoning_content.

    Local reasoning models emit their chain of thought inline; downstream
    JSON parsing must see only the answer.
    """
    blocks = _THINK_BLOCK_RE.findall(response.content)
    if not blocks:
        return response
    content = _THINK_BLOCK_RE.sub("", response.content).strip()
    reasoning = "\n".join(block.strip() for block in blocks if block.strip())
    existing = response.reasoning_content
    if existing:
        reasoning = f"{existing}\n{reasoning}" if reasoning else existing
    return replace(response, content=content, reasoning_content=reasoning or None)


class LLMProvider(ABC):
    """Interface every LLM provider implements.

    Subclasses implement the transport (:meth:`_chat`, :meth:`list_models`,
    :meth:`is_available`); shared generation behavior lives in :meth:`chat`.
    """

    name: ClassVar[str]

    @property
    @abstractmethod
    def capabilities(self) -> ProviderCapabilities:
        """What this provider supports natively."""

    @abstractmethod
    def is_available(self) -> bool:
        """Cheap availability probe (a couple of seconds at most).

        Never raises; returns False on any failure.
        """

    @abstractmethod
    def list_models(self) -> list[ModelDescriptor]:
        """List models this provider can serve right now.

        Returns an empty list when the provider is reachable but has no
        models loaded.

        Raises:
            LLMUnavailableError: If the provider cannot be reached.
        """

    def chat(self, request: ChatRequest) -> ChatResponse:
        """Generate a chat response. The only public generation entry point.

        Raises:
            LLMGenerationError: If the request fails.
            LLMUnavailableError: If the provider became unreachable.
        """
        if request.json_mode and not self.capabilities.native_json:
            request = inject_json_instruction(request)
        response = self._chat(request)
        return strip_reasoning_tags(response)

    @abstractmethod
    def _chat(self, request: ChatRequest) -> ChatResponse:
        """Provider-specific transport for a single chat request.

        Raises:
            LLMGenerationError: If the request fails.
            LLMUnavailableError: If the provider became unreachable.
        """
