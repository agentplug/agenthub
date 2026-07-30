"""Typed configuration for the LLM layer.

One place reads the environment (:meth:`LLMConfig.from_env`); everything
else receives explicit config objects. The env mapping is injectable so
tests never depend on process state.

Environment variables:
    OLLAMA_API_URL                 Ollama endpoint (default http://localhost:11434)
    LMSTUDIO_API_URL               LM Studio endpoint (default http://localhost:1234/v1)
    LLAMACPP_API_URL               llama.cpp llama-server endpoint
                                   (default http://localhost:8080/v1)
    LLAMACPP_API_KEY               API key if llama-server runs with --api-key
    AGENTHUB_LLM_MODEL             Force a model, e.g. "ollama:qwen3:8b"
    AGENTHUB_LLM_PROVIDER_PRIORITY Comma list, e.g. "llamacpp,ollama,cloud"
    AGENTHUB_LLM_PREFERRED         Comma list of model-id globs, e.g. "qwen3*,gpt-oss*"
    LMSTUDIO_NATIVE_JSON           "1" to send response_format to LM Studio
"""

import os
from collections.abc import Mapping
from dataclasses import dataclass, field

# Cloud model ids are config data: they drift with provider releases and are
# overridable per install, so drift is a one-line change, not a refactor.
DEFAULT_CLOUD_MODELS: dict[str, tuple[str, ...]] = {
    "openai": ("gpt-5", "gpt-5-mini", "gpt-4.1-mini"),
    "anthropic": ("claude-sonnet-4-6", "claude-haiku-4-5"),
    "google": ("gemini-2.5-pro", "gemini-2.5-flash"),
    "deepseek": ("deepseek-chat", "deepseek-reasoner"),
    "groq": ("llama-3.3-70b-versatile", "llama-3.1-8b-instant"),
    "mistral": ("mistral-large-latest", "mistral-small-latest"),
    "cohere": ("command-r-plus", "command-r"),
}

# Ordered glob patterns; the first pattern that matches any available model
# decides the preference tier (see selection.py).
DEFAULT_PREFERRED_MODELS: tuple[str, ...] = (
    "*gpt-oss*",
    "*deepseek-r1*",
    "*qwen3*",
    "*qwen*",
    "*llama3*",
    "*gemma*",
)

DEFAULT_PROVIDER_PRIORITY: tuple[str, ...] = (
    "ollama",
    "lmstudio",
    "llamacpp",
    "cloud",
)


@dataclass(frozen=True, slots=True)
class EndpointConfig:
    """HTTP endpoint settings for a local provider."""

    base_url: str
    api_key: str | None = None
    timeout: float = 300.0
    connect_timeout: float = 5.0
    probe_timeout: float = 2.0


@dataclass(frozen=True, slots=True)
class LLMConfig:
    """Complete configuration for providers, selection, and generation."""

    ollama: EndpointConfig = field(
        default_factory=lambda: EndpointConfig("http://localhost:11434")
    )
    lmstudio: EndpointConfig = field(
        default_factory=lambda: EndpointConfig("http://localhost:1234/v1")
    )
    llamacpp: EndpointConfig = field(
        default_factory=lambda: EndpointConfig("http://localhost:8080/v1")
    )
    provider_priority: tuple[str, ...] = DEFAULT_PROVIDER_PRIORITY
    preferred_models: tuple[str, ...] = DEFAULT_PREFERRED_MODELS
    forced_model: str | None = None
    cloud_models: Mapping[str, tuple[str, ...]] = field(
        default_factory=lambda: dict(DEFAULT_CLOUD_MODELS)
    )
    lmstudio_native_json: bool = False

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> "LLMConfig":
        """Build a config from environment variables.

        Args:
            env: Environment mapping; defaults to ``os.environ``. Injectable
                for deterministic tests.
        """
        if env is None:
            env = os.environ

        def csv_tuple(name: str, default: tuple[str, ...]) -> tuple[str, ...]:
            raw = env.get(name)
            if not raw:
                return default
            items = tuple(item.strip() for item in raw.split(",") if item.strip())
            return items or default

        return cls(
            ollama=EndpointConfig(
                base_url=env.get("OLLAMA_API_URL", "http://localhost:11434"),
            ),
            lmstudio=EndpointConfig(
                base_url=env.get("LMSTUDIO_API_URL", "http://localhost:1234/v1"),
                # LM Studio accepts any key; some client stacks require one.
                api_key="lm-studio",
            ),
            llamacpp=EndpointConfig(
                base_url=env.get("LLAMACPP_API_URL", "http://localhost:8080/v1"),
                api_key=env.get("LLAMACPP_API_KEY"),
            ),
            provider_priority=csv_tuple(
                "AGENTHUB_LLM_PROVIDER_PRIORITY", DEFAULT_PROVIDER_PRIORITY
            ),
            preferred_models=csv_tuple(
                "AGENTHUB_LLM_PREFERRED", DEFAULT_PREFERRED_MODELS
            ),
            forced_model=env.get("AGENTHUB_LLM_MODEL") or None,
            lmstudio_native_json=env.get("LMSTUDIO_NATIVE_JSON", "") == "1",
        )
