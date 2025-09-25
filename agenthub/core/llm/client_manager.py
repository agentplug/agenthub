"""
AISuite Client Management for AgentHub LLM Service

This module handles the initialization and configuration of AISuite clients
for different LLM providers (cloud and local).
"""

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


class ClientManager:
    """Manages AISuite client initialization for different providers."""

    def __init__(self) -> None:
        """Initialize the client manager."""
        pass

    def initialize_client(self, model: str) -> Any:
        """
        Initialize AISuite client for the given model.

        Args:
            model: Model identifier (e.g., "ollama:gpt-oss:20b")

        Returns:
            Initialized AISuite client
        """
        try:
            import aisuite as ai  # type: ignore[import-untyped]
        except ImportError:
            logger.warning("AISuite not available, using fallback")
            return None

        if self._is_ollama_model(model):
            return self._initialize_ollama_client(model, ai)
        elif self._is_lmstudio_model(model):
            return self._initialize_lmstudio_client(model, ai)
        else:
            return self._initialize_cloud_client(model, ai)

    def _is_ollama_model(self, model: str) -> bool:
        """Check if model is an Ollama model."""
        return model.startswith("ollama:")

    def _is_lmstudio_model(self, model: str) -> bool:
        """Check if model is an LM Studio model."""
        return model.startswith("lmstudio:")

    def _initialize_ollama_client(self, model: str, ai: Any) -> Any:
        """Initialize AISuite client for Ollama."""
        try:

            # Extract Ollama URL
            ollama_url = os.getenv("OLLAMA_API_URL", "http://localhost:11434")

            # Configure provider configs for Ollama
            provider_configs = {
                "ollama": {
                    "api_url": ollama_url,
                    "timeout": 300,
                }
            }

            return ai.Client(provider_configs=provider_configs)
        except Exception as e:
            logger.error(f"Failed to initialize Ollama client: {e}")
            return None

    def _initialize_lmstudio_client(self, model: str, ai: Any) -> Any:
        """Initialize AISuite client for LM Studio."""
        try:

            # Extract LM Studio URL
            lmstudio_url = os.getenv("LMSTUDIO_API_URL", "http://localhost:1234/v1")

            # Use OpenAI provider with custom base URL for LM Studio
            provider_configs = {
                "openai": {
                    "base_url": lmstudio_url,
                    "api_key": "lm-studio",  # LM Studio doesn't require real API key
                }
            }

            return ai.Client(provider_configs=provider_configs)
        except Exception as e:
            logger.error(f"Failed to initialize LM Studio client: {e}")
            return None

    def _initialize_cloud_client(self, model: str, ai: Any) -> Any:
        """Initialize AISuite client for cloud providers."""
        try:

            # For cloud models, use standard initialization
            return ai.Client()
        except Exception as e:
            logger.error(f"Failed to initialize cloud client: {e}")
            return None

    def get_actual_model_name(self, model: str) -> str:
        """
        Get the actual model name to use with AISuite.

        Args:
            model: Model identifier (e.g., "ollama:gpt-oss:20b")

        Returns:
            Actual model name for AISuite (e.g., "gpt-oss:20b")
        """
        if self._is_ollama_model(model):
            # For Ollama, keep the full format
            return model
        elif self._is_lmstudio_model(model):
            # For LM Studio, strip the prefix and use OpenAI format
            model_name = model.replace("lmstudio:", "")
            return f"openai:{model_name}"
        else:
            # For cloud models, use as-is
            return model
