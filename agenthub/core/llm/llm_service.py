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
import os
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS AND CONFIGURATION
# =============================================================================


class ModelConfig:
    """Configuration constants for model selection and scoring."""

    # Preferred models for different use cases
    PREFERRED_MODELS = [
        "gpt-oss:120b",
        "gpt-oss:20b",  # OpenAI open-weight (highest priority)
        "deepseek-r1:70b",
        "deepseek-r1:32b",  # DeepSeek reasoning models
        "gemma:latest",
        "llama3:latest",  # General purpose models
        "qwen:latest",
        "mistral:latest",  # Alternative models
    ]

    # Model family scoring (higher = better for agentic tasks)
    FAMILY_SCORES = {
        "gpt-oss": 60,  # OpenAI's open-weight models (highest priority)
        "deepseek": 50,
        "gemma": 35,
        "llama": 40,
        "qwen": 50,
        "mistral": 35,
        "codellama": 30,
        "phind": 25,
        "wizard": 20,
        "vicuna": 15,
        "claude": 45,
        "gpt": 40,
    }

    # Size scoring (larger is generally better)
    SIZE_SCORES = {
        "120b": 120,
        "70b": 100,
        "65b": 95,
        "32b": 80,
        "latest": 80,
        "20b": 75,
        "13b": 60,
        "7b": 40,
        "3b": 20,
        "1b": 10,
    }

    # Common Ollama URLs for auto-detection
    OLLAMA_URLS = [
        "http://localhost:11434",  # Default Ollama
        "http://127.0.0.1:11434",  # Alternative localhost
        "http://0.0.0.0:11434",  # All interfaces
    ]

    # Cloud provider models (fallback when no local models)
    CLOUD_MODELS = {
        "OPENAI_API_KEY": "openai:gpt-4o",
        "ANTHROPIC_API_KEY": "anthropic:claude-3-5-sonnet-20241022",
        "GOOGLE_API_KEY": "google:gemini-1.5-pro",
        "DEEPSEEK_API_KEY": "deepseek:deepseek-chat",
        "FIREWORKS_API_KEY": (
            "fireworks:accounts/fireworks/models/llama-v3p2-3b-instruct"
        ),
        "COHERE_API_KEY": "cohere:command-r-plus",
        "MISTRAL_API_KEY": "mistral:mistral-large-latest",
        "GROQ_API_KEY": "groq:llama-3.1-70b-versatile",
        "REPLICATE_API_TOKEN": "replicate:meta/llama-2-70b-chat",
        "HUGGINGFACE_API_KEY": "huggingface:microsoft/DialoGPT-large",
        "AZURE_OPENAI_API_KEY": "azure:gpt-4o",
    }

    # Special case for AWS (requires multiple env vars)
    AWS_MODEL = "aws:anthropic.claude-3-5-sonnet-20241022-v2:0"
    AWS_REQUIRED_VARS = ["AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY"]


@dataclass
class LogAnalysis:
    """Structured log analysis result"""

    summary: str
    progress: int
    status: str
    errors: list[str]
    suggestions: list[str]


@dataclass
class ModelInfo:
    """Information about a detected model"""

    name: str
    provider: str
    score: int
    is_local: bool
    is_available: bool


class CoreLLMService:
    """
    Comprehensive LLM Service for AgentHub

    A unified, reusable service that provides:
    - Automatic model detection and selection
    - Multi-provider support (cloud + local)
    - Standardized API for all agents
    - Intelligent model scoring and fallbacks
    - Comprehensive logging and debugging

    Features:
    - Auto-detects best available model (local Ollama or cloud)
    - Supports all major LLM providers via AISuite
    - Intelligent model scoring (size + family + quality)
    - Comprehensive logging for debugging
    - Caching for performance
    - JSON response handling
    """

    def __init__(
        self,
        aisuite_client: Any = None,
        model: str | None = None,
        auto_detect: bool = True,
    ) -> None:
        """
        Initialize Core LLM Service

        Args:
            aisuite_client: Optional AISuite client instance
            model: Model identifier in format "provider:model-name".
                   If None and auto_detect=True, auto-detects best available model.
            auto_detect: Whether to auto-detect model if not provided
        """
        # Initialize caching first (needed by model detection)
        self.cache: dict[str, Any] = {}
        self._model_info: ModelInfo | None = None
        self._ollama_url_cache: str | None = None

        # Model selection
        if model:
            self.model = model
            logger.info(f"🎯 Using specified model: {model}")
        elif auto_detect:
            self.model = self._detect_best_model()
        else:
            self.model = ModelConfig.CLOUD_MODELS.get("OPENAI_API_KEY", "openai:gpt-4o")
            logger.warning(f"⚠️ No model specified, using default: {self.model}")

        # Initialize client with appropriate configuration
        if aisuite_client is None:
            self.client = self._initialize_aisuite_with_config(self.model)
        else:
            self.client = aisuite_client

    def _detect_best_model(self) -> str:
        """
        Automatically detect and return the best available model.
        Follows aisuite provider format: <provider>:<model-name>

        Returns:
            str: Model identifier in aisuite format
        """
        # Priority 1: Check for local models first (auto-detection)
        local_model = self._detect_running_local_model()
        if local_model:
            logger.info(f"🎯 Selected model: {local_model}")
            return local_model

        # Priority 2: Check API keys and return corresponding cloud model
        cloud_model = self._detect_cloud_model()
        if cloud_model:
            logger.info(f"☁️ Selected cloud model: {cloud_model}")
            return cloud_model

        # Default fallback
        default_model = "openai:gpt-4o"
        logger.warning(f"⚠️ No models detected, using default: {default_model}")
        return default_model

    def _detect_cloud_model(self) -> str | None:
        """Detect available cloud model based on API keys."""
        # Check AWS Bedrock (special case - requires multiple env vars)
        if all(os.getenv(var) for var in ModelConfig.AWS_REQUIRED_VARS):
            return ModelConfig.AWS_MODEL

        # Check other cloud providers
        for env_var, model in ModelConfig.CLOUD_MODELS.items():
            if os.getenv(env_var):
                return model

        return None

    def _detect_running_local_model(self) -> str | None:
        """Detect running local models with auto-detection."""
        # Check if Ollama is available
        ollama_url = self._detect_ollama_url()

        if self._check_ollama_available(ollama_url):
            # Get available models
            models = self._get_ollama_models(ollama_url)
            if models:
                best_model = self._select_best_ollama_model(models)
                selected_model = f"ollama:{best_model}"
                logger.info(
                    f"🤖 Local model detected: {selected_model} "
                    f"(from {len(models)} available models)"
                )
                return selected_model

        logger.debug("No local models detected")
        return None

    def _detect_ollama_url(self) -> str:
        """Auto-detect Ollama API URL with fallback options (cached)."""
        # Return cached URL if available
        if self._ollama_url_cache is not None:
            return self._ollama_url_cache

        # 1. Environment variable (user override)
        if os.getenv("OLLAMA_API_URL"):
            url = os.getenv("OLLAMA_API_URL")
            logger.info(f"🔧 Using Ollama URL from environment: {url}")
            self._ollama_url_cache = url
            return url

        # 2. Try to find running Ollama instance
        for url in ModelConfig.OLLAMA_URLS:
            if self._check_ollama_available(url):
                logger.info(f"🔍 Auto-detected Ollama URL: {url}")
                self._ollama_url_cache = url
                return url

        # 3. Default fallback
        logger.debug("Using default Ollama URL: http://localhost:11434")
        url = "http://localhost:11434"
        self._ollama_url_cache = url
        return url

    def _check_ollama_available(self, url: str) -> bool:
        """Check if Ollama is running at the given URL."""
        try:
            import requests

            response = requests.get(f"{url}/api/tags", timeout=1)
            return response.status_code == 200
        except Exception:
            return False

    def _get_ollama_models(self, url: str) -> list[dict]:
        """Get available models from Ollama."""
        try:
            import requests

            response = requests.get(f"{url}/api/tags", timeout=2)
            if response.status_code == 200:
                return response.json().get("models", [])
        except Exception:
            pass
        return []

    def _select_best_ollama_model(self, available_models: list[dict]) -> str:
        """Select the best model from available Ollama models."""
        model_names = [model.get("name", "") for model in available_models]

        if not model_names:
            logger.warning("No Ollama models available, using fallback: llama3:latest")
            return "llama3:latest"

        # If only one model, return it
        if len(model_names) == 1:
            model_name = model_names[0]
            logger.info(f"🎯 Single model available: {model_name}")
            return model_name

        # Score each model and select the best one
        logger.info(
            f"🔍 Evaluating {len(model_names)} models: {', '.join(model_names)}"
        )

        # Log scoring details
        for model_name in model_names:
            score = self._calculate_model_score(model_name)
            logger.debug(f"📊 {model_name}: {score} points")

        best_model = self._score_and_select_best(model_names)
        logger.info(f"🏆 Best model selected: {best_model}")
        return best_model

    def _score_and_select_best(self, model_names: list[str]) -> str:
        """Score models and return the best one."""
        scored_models = []

        for model_name in model_names:
            score = self._calculate_model_score(model_name)
            scored_models.append((model_name, score))

        # Sort by score (highest first) and return the best
        scored_models.sort(key=lambda x: x[1], reverse=True)
        return scored_models[0][0]

    def _calculate_model_score(self, model_name: str) -> int:
        """Calculate a score for a model (higher is better)."""
        score = 0
        model_lower = model_name.lower()

        # Size scoring (larger is better)
        for size, points in ModelConfig.SIZE_SCORES.items():
            if size in model_lower:
                score += points
                break

        # Model family scoring (known good models)
        for family, points in ModelConfig.FAMILY_SCORES.items():
            if family in model_lower:
                score += points
                break

        # Penalty for poor models
        poor_indicators = ["tiny", "small", "test", "demo"]
        for indicator in poor_indicators:
            if indicator in model_lower:
                score -= 30
                break

        # Bonus for latest/stable versions
        if "latest" in model_lower or "stable" in model_lower:
            score += 10

        return score

    # =============================================================================
    # PUBLIC UTILITY METHODS
    # =============================================================================

    def get_model_info(self) -> ModelInfo:
        """Get detailed information about the current model."""
        if self._model_info is None:
            self._model_info = self._create_model_info()
        return self._model_info

    def _create_model_info(self) -> ModelInfo:
        """Create ModelInfo object for current model."""
        provider, model_name = (
            self.model.split(":", 1) if ":" in self.model else ("unknown", self.model)
        )
        is_local = provider == "ollama"
        score = (
            self._calculate_model_score(model_name) if is_local else 100
        )  # Cloud models get default score

        return ModelInfo(
            name=model_name,
            provider=provider,
            score=score,
            is_local=is_local,
            is_available=True,
        )

    def list_available_models(self) -> list[ModelInfo]:
        """List all available models with their information."""
        models = []

        # Check local models
        ollama_url = self._detect_ollama_url()
        if self._check_ollama_available(ollama_url):
            ollama_models = self._get_ollama_models(ollama_url)
            for model_data in ollama_models:
                model_name = model_data.get("name", "")
                score = self._calculate_model_score(model_name)
                models.append(
                    ModelInfo(
                        name=model_name,
                        provider="ollama",
                        score=score,
                        is_local=True,
                        is_available=True,
                    )
                )

        # Check cloud models
        for env_var, model in ModelConfig.CLOUD_MODELS.items():
            if os.getenv(env_var):
                provider, model_name = model.split(":", 1)
                models.append(
                    ModelInfo(
                        name=model_name,
                        provider=provider,
                        score=100,  # Cloud models get default score
                        is_local=False,
                        is_available=True,
                    )
                )

        # Sort by score (highest first)
        models.sort(key=lambda x: x.score, reverse=True)
        return models

    def get_current_model(self) -> str:
        """Get the currently selected model."""
        return self.model

    def is_local_model(self) -> bool:
        """Check if current model is local (Ollama)."""
        return self.model.startswith("ollama:")

    def _initialize_aisuite_with_config(self, model: str) -> Any:
        """Initialize AISuite client with appropriate configuration."""
        import aisuite as ai

        # Check if it's a local model
        if model.startswith("ollama:"):
            return self._initialize_ollama_client(model)
        else:
            # Cloud models - no special config needed
            return ai.Client()

    def _initialize_ollama_client(self, model: str) -> Any:
        """Initialize AISuite client for Ollama."""
        import aisuite as ai

        # Get Ollama configuration
        api_url = self._detect_ollama_url()
        timeout = int(os.getenv("OLLAMA_TIMEOUT", "300"))

        return ai.Client(
            provider_configs={
                "ollama": {
                    "api_url": api_url,
                    "timeout": timeout,
                }
            }
        )

    def generate(
        self,
        input_data: str | list[dict],
        system_prompt: str | None = None,
        return_json: bool = False,
        **kwargs: Any,
    ) -> str:
        """
        Adaptive LLM generation using AISuite

        Args:
            input_data: Either a string (single prompt) or list of messages
            system_prompt: Optional system prompt to define AI behavior
            return_json: If True, request JSON response from AISuite
            **kwargs: Additional parameters for AISuite

        Returns:
            Generated text response from LLM
        """
        if not self.client:
            return self._fallback_response()

        try:
            # Prepare request parameters
            request_kwargs = kwargs.copy()
            if return_json:
                request_kwargs["response_format"] = {"type": "json_object"}

            if isinstance(input_data, str):
                # Single prompt - convert to messages format
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": input_data})

                response = self.client.chat.completions.create(
                    model=self.model, messages=messages, **request_kwargs
                )
                return str(response.choices[0].message.content)

            elif isinstance(input_data, list):
                # Messages - organize into context and focus on current
                messages = self._organize_messages_to_aisuite_format(
                    input_data, system_prompt
                )

                response = self.client.chat.completions.create(
                    model=self.model, messages=messages, **request_kwargs
                )
                return str(response.choices[0].message.content)
            else:
                raise ValueError("input_data must be string or list")
        except Exception as e:
            print(f"AISuite generation failed: {e}")
            return self._fallback_response()

    def _organize_messages_to_aisuite_format(
        self, messages: list[dict], system_prompt: str | None = None
    ) -> list[dict]:
        """
        Convert conversation messages to AISuite messages format with context
        management

        Args:
            messages: List of conversation messages
            system_prompt: Optional system prompt to add

        Returns:
            Formatted messages list for AISuite
        """
        if not messages:
            return []

        # Separate context (previous messages) from current message
        context_messages = messages[:-1] if len(messages) > 1 else []
        current_message = messages[-1]

        # Build messages list for AISuite
        aisuite_messages = []

        # Add system prompt if provided
        if system_prompt:
            aisuite_messages.append({"role": "system", "content": system_prompt})

        # Add context messages (limit to last 3-4 to avoid overwhelming)
        if context_messages:
            recent_messages = (
                context_messages[-3:] if len(context_messages) > 3 else context_messages
            )
            for msg in recent_messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                # Truncate long messages
                if len(content) > 200:
                    content = content[:200] + "..."
                aisuite_messages.append({"role": role, "content": content})

        # Add current message
        current_content = current_message.get("content", "")
        current_role = current_message.get("role", "user")
        aisuite_messages.append({"role": current_role, "content": current_content})

        return aisuite_messages

    def analyze_text(
        self,
        text: str,
        prompt_template: str,
        system_prompt: str | None = None,
        return_json: bool = False,
    ) -> str:
        """
        Analyze any text content using AISuite with custom prompt template

        Args:
            text: Text content to analyze
            prompt_template: Prompt template with {text} placeholder
            system_prompt: Optional system prompt for analysis
            return_json: If True, request JSON response

        Returns:
            Analysis result from LLM
        """
        if not text:
            return self._fallback_response()

        formatted_prompt = prompt_template.format(text=text)
        return self.generate(
            formatted_prompt, system_prompt=system_prompt, return_json=return_json
        )

    def _initialize_aisuite(self) -> Any:
        """
        Initialize AISuite client

        Returns:
            AISuite client instance or None if not available
        """
        try:
            import aisuite as ai  # type: ignore[import-untyped]

            return ai.Client()
        except ImportError:
            print("Warning: AISuite not available, using fallback")
            return None

    def _fallback_response(self) -> str:
        """
        Fallback response when AISuite is not available

        Returns:
            Fallback response string
        """
        return "AISuite not available"


# =============================================================================
# SHARED INSTANCE MANAGEMENT
# =============================================================================

# Global shared instance to prevent duplicate model detection logs
_shared_llm_service: CoreLLMService | None = None


def get_shared_llm_service(
    model: str | None = None, auto_detect: bool = True
) -> CoreLLMService:
    """
    Get a shared CoreLLMService instance to avoid duplicate model detection logs.

    This function helps prevent the repetitive Ollama model detection logs that
    occur when multiple components create their own CoreLLMService instances.

    Args:
        model: Model identifier in format "provider:model-name".
               If None and auto_detect=True, auto-detects best available model.
        auto_detect: Whether to auto-detect model if not provided

    Returns:
        Shared CoreLLMService instance

    Note:
        If you need a service with a specific model that differs from the shared
        instance, create a new CoreLLMService instance directly.
    """
    global _shared_llm_service

    # If no shared instance exists, create one
    if _shared_llm_service is None:
        _shared_llm_service = CoreLLMService(model=model, auto_detect=auto_detect)
        logger.debug("Created shared CoreLLMService instance")
        return _shared_llm_service

    # If shared instance exists but different model requested, create new instance
    if model and model != _shared_llm_service.model:
        logger.debug(
            f"Creating new CoreLLMService for model {model} "
            f"(shared has {_shared_llm_service.model})"
        )
        return CoreLLMService(model=model, auto_detect=auto_detect)

    # Return existing shared instance
    logger.debug("Reusing shared CoreLLMService instance")
    return _shared_llm_service


def reset_shared_llm_service() -> None:
    """
    Reset the shared LLM service instance.

    Useful for testing or when you want to force re-detection of models.
    """
    global _shared_llm_service
    _shared_llm_service = None
    logger.debug("Reset shared CoreLLMService instance")
