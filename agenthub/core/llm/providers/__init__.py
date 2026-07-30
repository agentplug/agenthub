"""LLM provider implementations.

``build_providers`` is a pure function of config: it constructs the local
providers in ``config.provider_priority`` order. (The cloud provider joins
the registry when the service layer lands.)
"""

from ..base import LLMProvider
from ..config import LLMConfig
from .llamacpp import LlamaCppProvider
from .lmstudio import LMStudioProvider
from .ollama import OllamaProvider
from .openai_compat import OpenAICompatProvider

__all__ = [
    "LMStudioProvider",
    "LlamaCppProvider",
    "OllamaProvider",
    "OpenAICompatProvider",
    "build_providers",
]


def build_providers(config: LLMConfig) -> list[LLMProvider]:
    """Construct configured providers in priority order.

    Unknown names in ``config.provider_priority`` are skipped (``cloud`` is
    handled by the service layer until the cloud provider lands here).
    """
    factories = {
        "ollama": lambda: OllamaProvider(config.ollama),
        "lmstudio": lambda: LMStudioProvider(
            config.lmstudio, native_json=config.lmstudio_native_json
        ),
        "llamacpp": lambda: LlamaCppProvider(config.llamacpp),
    }
    return [factories[name]() for name in config.provider_priority if name in factories]
