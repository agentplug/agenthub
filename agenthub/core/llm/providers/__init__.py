"""LLM provider implementations.

``build_providers`` is a pure function of config: it constructs providers
in ``config.provider_priority`` order. The ``cloud`` priority entry expands
to one LiteLLM-backed provider per configured cloud vendor.
"""

from collections.abc import Callable

from ..base import LLMProvider
from ..config import LLMConfig
from .cloud import LiteLLMCloudProvider
from .llamacpp import LlamaCppProvider
from .lmstudio import LMStudioProvider
from .ollama import OllamaProvider
from .openai_compat import OpenAICompatProvider

__all__ = [
    "LMStudioProvider",
    "LiteLLMCloudProvider",
    "LlamaCppProvider",
    "OllamaProvider",
    "OpenAICompatProvider",
    "build_providers",
]


def build_providers(config: LLMConfig) -> list[LLMProvider]:
    """Construct configured providers in priority order.

    Unknown names in ``config.provider_priority`` are skipped.
    """
    factories: dict[str, Callable[[], list[LLMProvider]]] = {
        "ollama": lambda: [OllamaProvider(config.ollama)],
        "lmstudio": lambda: [
            LMStudioProvider(config.lmstudio, native_json=config.lmstudio_native_json)
        ],
        "llamacpp": lambda: [LlamaCppProvider(config.llamacpp)],
        "cloud": lambda: [
            LiteLLMCloudProvider(vendor, models)
            for vendor, models in config.cloud_models.items()
        ],
    }
    providers: list[LLMProvider] = []
    for name in config.provider_priority:
        if name in factories:
            providers.extend(factories[name]())
    return providers
