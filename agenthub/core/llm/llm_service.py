"""
Comprehensive LLM Service for AgentHub

A unified, reusable LLM service that provides:
- Automatic model detection and selection
- Multi-provider support (cloud + local)
- Standardized API for all agents
- Intelligent model scoring and fallbacks
- Comprehensive logging and debugging

Usage:
    from agenthub.core.llm.llm_service import CoreLLMService, get_shared_llm_service

    # Auto-detect best available model (creates new instance)
    service = CoreLLMService()

    # Use shared instance (recommended to avoid duplicate model detection logs)
    service = get_shared_llm_service()

    # Use specific model
    service = CoreLLMService(model="ollama:gpt-oss:120b")

    # Generate responses
    response = service.generate("Hello, world!")
"""

import logging
from typing import Any

from .client_manager import ClientManager
from .model_config import ModelInfo
from .model_detector import ModelDetector

logger = logging.getLogger(__name__)

# Global shared instance
_shared_llm_service: "CoreLLMService | None" = None


class CoreLLMService:
    """
    Comprehensive LLM service providing unified access to multiple LLM providers.

    Features:
    - Automatic model detection and selection
    - Multi-provider support (Ollama, LM Studio, cloud providers)
    - Intelligent model scoring and fallbacks
    - Shared instance management
    - Comprehensive logging and debugging
    """

    def __init__(self, model: str | None = None, auto_detect: bool = True):
        """
        Initialize the LLM service.

        Args:
            model: Specific model to use (e.g., "ollama:gpt-oss:20b")
            auto_detect: Whether to auto-detect the best model if none specified
        """
        self.model_detector = ModelDetector()
        self.client_manager = ClientManager()
        self.cache: dict[str, Any] = {}
        self._model_info: ModelInfo | None = None

        # Determine model to use
        if model:
            self.model = model
            logger.info(f"🎯 Using specified model: {model}")
        elif auto_detect:
            self.model = self.model_detector.detect_best_model()
            logger.info(f"🎯 Selected model: {self.model}")
        else:
            self.model = "fallback"
            logger.info("🎯 Using fallback model")

        # Initialize client
        self.client = self.client_manager.initialize_client(self.model)

    def generate(
        self,
        input_data: str | list[dict],
        system_prompt: str | None = None,
        return_json: bool = False,
        temperature: float = 0.0,
        **kwargs: Any,
    ) -> str:
        """
        Adaptive LLM generation using AISuite

        Args:
            input_data: Either a string (single prompt) or list of messages
            system_prompt: Optional system prompt to define AI behavior
            return_json: If True, request JSON response from AISuite
            temperature: Controls randomness (0.0 = deterministic, 1.0 = creative).
                        Default: 0.0 (deterministic responses)
            **kwargs: Additional parameters for AISuite (excluding temperature)

        Returns:
            Generated text response from LLM
        """
        if not self.client:
            return self._fallback_response()

        try:
            # Prepare request parameters
            request_kwargs = kwargs.copy()

            # Handle JSON response format for different providers
            if return_json:
                if self.is_local_model():
                    # For local models (Ollama/LM Studio), ask for JSON in prompt
                    # instead of response_format
                    if isinstance(input_data, str):
                        input_data = (
                            f"{input_data}\n\nPlease respond with valid JSON only, "
                            "no additional text."
                        )
                    elif isinstance(input_data, list):
                        # Add JSON instruction to the last user message
                        if input_data and input_data[-1].get("role") == "user":
                            input_data[-1]["content"] += (
                                "\n\nPlease respond with valid JSON only, "
                                "no additional text."
                            )
                else:
                    # For cloud models, use response_format
                    request_kwargs["response_format"] = {"type": "json_object"}

            # Set temperature parameter (default: 0.0 for deterministic responses)
            request_kwargs["temperature"] = temperature

            if isinstance(input_data, str):
                # Single prompt - convert to messages format
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": input_data})

                response = self.client.chat.completions.create(
                    model=self.client_manager.get_actual_model_name(self.model),
                    messages=messages,
                    **request_kwargs,
                )
                logger.debug(f"Response type: {type(response)}")
                logger.debug(f"Response: {response}")
                if hasattr(response, "choices") and response.choices:
                    return str(response.choices[0].message.content)
                else:
                    logger.error(f"Invalid response format: {response}")
                    return self._fallback_response()

            elif isinstance(input_data, list):
                # Messages - organize into context and focus on current
                messages = self._organize_messages_to_aisuite_format(
                    input_data, system_prompt
                )

                response = self.client.chat.completions.create(
                    model=self.client_manager.get_actual_model_name(self.model),
                    messages=messages,
                    **request_kwargs,
                )
                logger.debug(f"Response type: {type(response)}")
                logger.debug(f"Response: {response}")
                if hasattr(response, "choices") and response.choices:
                    return str(response.choices[0].message.content)
                else:
                    logger.error(f"Invalid response format: {response}")
                    return self._fallback_response()
            else:
                raise ValueError("input_data must be string or list")
        except Exception as e:
            logger.error(f"AISuite generation failed: {e}")
            return self._fallback_response()

    def _organize_messages_to_aisuite_format(
        self, messages: list[dict], system_prompt: str | None = None
    ) -> list[dict]:
        """Organize messages for AISuite format."""
        organized_messages = []

        # Add system prompt if provided
        if system_prompt:
            organized_messages.append({"role": "system", "content": system_prompt})

        # Add user messages
        for message in messages:
            if message.get("role") in ["user", "assistant", "system"]:
                organized_messages.append(message)

        return organized_messages

    def get_model_info(self) -> ModelInfo:
        """Get information about the current model."""
        if not self._model_info:
            self._model_info = self._create_model_info()
        return self._model_info

    def _create_model_info(self) -> ModelInfo:
        """Create ModelInfo object for the current model."""
        return self.model_detector.create_model_info(
            self.model, is_local=self.is_local_model()
        )

    def list_available_models(self) -> list[ModelInfo]:
        """List all available models with their information."""
        # This would require implementing model listing for each provider
        # For now, return current model info
        return [self.get_model_info()]

    def get_current_model(self) -> str:
        """Get the current model identifier."""
        return self.model

    def is_local_model(self) -> bool:
        """Check if the current model is a local model."""
        return self.model.startswith(("ollama:", "lmstudio:"))

    def _fallback_response(self) -> str:
        """Provide fallback response when LLM is unavailable."""
        return "AISuite not available"


# =============================================================================
# SHARED INSTANCE MANAGEMENT
# =============================================================================


def get_shared_llm_service(
    model: str | None = None, auto_detect: bool = True
) -> CoreLLMService:
    """
    Get or create a shared LLM service instance.

    This prevents duplicate model detection and reduces initialization overhead.

    Args:
        model: Specific model to use
        auto_detect: Whether to auto-detect model

    Returns:
        Shared CoreLLMService instance
    """
    global _shared_llm_service

    if _shared_llm_service is None:
        logger.debug("Created shared CoreLLMService instance")
        _shared_llm_service = CoreLLMService(model=model, auto_detect=auto_detect)
    else:
        logger.debug("Reusing shared CoreLLMService instance")

    return _shared_llm_service


def reset_shared_llm_service() -> None:
    """Reset the shared LLM service instance."""
    global _shared_llm_service
    _shared_llm_service = None
    logger.debug("Reset shared CoreLLMService instance")
