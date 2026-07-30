"""Core data types shared by all LLM providers and the service layer."""

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any, Literal

Role = Literal["system", "user", "assistant"]

# Parameter counts like "7b", "0.5B", "70 b" inside a model id.
_PARAM_COUNT_RE = re.compile(r"(\d+(?:\.\d+)?)\s*b\b")


def parse_parameter_count(model_id: str) -> float | None:
    """Extract a parameter count in billions from a model id, if present.

    Works for ids like ``qwen3:32b``, ``llama-3.1-8B-instruct`` and
    file-path-ish ids such as ``/models/qwen3-8b-q4.gguf``.
    """
    match = _PARAM_COUNT_RE.search(model_id.lower())
    return float(match.group(1)) if match else None


@dataclass(frozen=True, slots=True)
class Message:
    """A single chat message."""

    role: Role
    content: str


@dataclass(frozen=True, slots=True)
class ChatRequest:
    """Provider-independent chat generation request.

    ``model`` is the bare provider-local model id (no ``provider:`` prefix).
    ``extra`` is passed through to the provider transport untouched.
    """

    model: str
    messages: tuple[Message, ...]
    temperature: float = 0.0
    json_mode: bool = False
    max_tokens: int | None = None
    extra: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class ChatResponse:
    """Provider-independent chat generation response.

    ``content`` has reasoning tags (``<think>...</think>``) already stripped;
    the stripped text is preserved in ``reasoning_content``.
    """

    content: str
    model: str
    provider: str
    reasoning_content: str | None = None
    finish_reason: str | None = None
    usage: Mapping[str, int] | None = None
    raw: Any = None


@dataclass(frozen=True, slots=True)
class ModelDescriptor:
    """A model offered by a provider."""

    id: str
    provider: str
    is_local: bool
    size_b: float | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def qualified_id(self) -> str:
        """Globally unique id in the established format, e.g. ``ollama:qwen3:32b``."""
        return f"{self.provider}:{self.id}"


@dataclass(frozen=True, slots=True)
class ProviderCapabilities:
    """What a provider supports natively.

    ``native_json`` False means JSON mode is emulated by instruction
    injection in :meth:`agenthub.core.llm.base.LLMProvider.chat`.
    """

    native_json: bool
    model_listing: bool
    is_local: bool
