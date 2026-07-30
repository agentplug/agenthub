"""Model detection and selection across providers.

Replaces the name-scoring tables of the old ``ModelDetector``: selection is
a pure function of provider probe results —

1. filter out non-chat models (embeddings, rerankers, ...),
2. rank by preference globs from config (first matching pattern wins),
3. then by numeric parameter count (descending), then id for determinism.

Provider priority stays what it always was: the first available provider in
``config.provider_priority`` order wins; ranking happens within a provider.
"""

import fnmatch
import logging
import re

from .base import LLMProvider
from .config import LLMConfig
from .errors import LLMError, ModelNotFoundError, NoModelAvailableError
from .types import ModelDescriptor, parse_parameter_count

logger = logging.getLogger(__name__)

# Models that can never serve chat generation.
_NON_CHAT_RE = re.compile(
    r"embed|embedding|rerank|whisper|clip|bge-|nomic-embed", re.IGNORECASE
)


class ModelSelector:
    """Selects a (provider, model) pair from priority-ordered providers."""

    def __init__(self, providers: list[LLMProvider], config: LLMConfig) -> None:
        self._providers = list(providers)
        self._config = config

    def select(self) -> tuple[LLMProvider, ModelDescriptor]:
        """Pick the best model on the first available provider.

        Raises:
            NoModelAvailableError: With per-provider diagnostics when every
                provider is unavailable or has no usable chat model.
        """
        probe_results: dict[str, str] = {}
        for provider in self._providers:
            if not provider.is_available():
                probe_results[provider.name] = "not available"
                continue
            try:
                models = provider.list_models()
            except LLMError as e:
                probe_results[provider.name] = str(e)
                continue
            usable = [model for model in models if self._is_chat_model(model)]
            if not usable:
                probe_results[provider.name] = "no usable chat models"
                continue
            best = self.rank(usable)[0]
            logger.info("Selected model %s", best.qualified_id)
            return provider, best
        raise NoModelAvailableError(probe_results=probe_results)

    def candidates(self) -> list[tuple[LLMProvider, ModelDescriptor]]:
        """All usable (provider, model) pairs from available providers,
        provider-priority first, ranked within each provider."""
        pairs: list[tuple[LLMProvider, ModelDescriptor]] = []
        for provider in self._providers:
            if not provider.is_available():
                continue
            try:
                models = provider.list_models()
            except LLMError:
                continue
            usable = [model for model in models if self._is_chat_model(model)]
            pairs.extend((provider, model) for model in self.rank(usable))
        return pairs

    def resolve(self, qualified_id: str) -> tuple[LLMProvider, ModelDescriptor]:
        """Resolve an explicit ``provider:model`` id to a provider and model.

        The model id is trusted without probing (the provider may be slow to
        start or the model pulled on demand); errors surface at generation.

        Raises:
            ModelNotFoundError: If the id is malformed or no configured
                provider carries that name.
        """
        provider_name, separator, model_id = qualified_id.partition(":")
        if not separator or not model_id:
            raise ModelNotFoundError(
                f"Invalid model id {qualified_id!r}; expected 'provider:model', "
                f"e.g. 'ollama:qwen3:8b' or 'anthropic:claude-sonnet-4-6'"
            )
        for provider in self._providers:
            if provider.name == provider_name:
                descriptor = ModelDescriptor(
                    id=model_id,
                    provider=provider_name,
                    is_local=provider.capabilities.is_local,
                    size_b=parse_parameter_count(model_id),
                )
                return provider, descriptor
        raise ModelNotFoundError(
            f"No configured provider named {provider_name!r} "
            f"(configured: {[provider.name for provider in self._providers]})"
        )

    def rank(self, models: list[ModelDescriptor]) -> list[ModelDescriptor]:
        """Rank models: preference-glob tier, then size desc, then id."""
        preferred = [pattern.lower() for pattern in self._config.preferred_models]

        def tier(model: ModelDescriptor) -> int:
            for index, pattern in enumerate(preferred):
                if fnmatch.fnmatch(model.id.lower(), pattern):
                    return index
            return len(preferred)

        return sorted(
            models, key=lambda model: (tier(model), -(model.size_b or 0.0), model.id)
        )

    @staticmethod
    def _is_chat_model(model: ModelDescriptor) -> bool:
        return not _NON_CHAT_RE.search(model.id)
