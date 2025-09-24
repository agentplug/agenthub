"""
Model Detection and Scoring for AgentHub LLM Service

This module handles automatic detection of available LLM models and intelligent
scoring to select the best model for use.
"""

import logging
import os

import httpx

from .model_config import ModelConfig, ModelInfo

logger = logging.getLogger(__name__)


class ModelDetector:
    """Handles model detection and scoring for optimal model selection."""

    def __init__(self):
        """Initialize the model detector."""
        self.cache = {}
        self._ollama_url_cache = None

    def detect_best_model(self) -> str:
        """
        Detect the best available model across all providers.

        Returns:
            Model identifier string (e.g., "ollama:gpt-oss:20b")
        """
        # Try cloud models first (if API keys available)
        cloud_model = self._detect_cloud_model()
        if cloud_model:
            logger.info(f"🎯 Selected cloud model: {cloud_model}")
            return cloud_model

        # Fallback to local models
        local_model = self._detect_running_local_model()
        if local_model:
            logger.info(f"🎯 Selected local model: {local_model}")
            return local_model

        # Final fallback
        logger.warning("No suitable model found, using fallback")
        return "fallback"

    def _detect_cloud_model(self) -> str | None:
        """Detect available cloud models based on API keys."""
        for provider, models in ModelConfig.CLOUD_MODELS.items():
            api_key = os.getenv(f"{provider.upper()}_API_KEY")
            if api_key:
                logger.info(f"🔑 Found {provider} API key")
                return f"{provider}:{models[0]}"
        return None

    def _detect_running_local_model(self) -> str | None:
        """Detect running local models (Ollama preferred, LM Studio fallback)."""
        # Try Ollama first
        ollama_model = self._detect_ollama_model()
        if ollama_model:
            return ollama_model

        # Fallback to LM Studio
        lmstudio_model = self._detect_lmstudio_model()
        if lmstudio_model:
            return lmstudio_model

        return None

    def _detect_ollama_model(self) -> str | None:
        """Detect available Ollama models."""
        url = self._detect_ollama_url()
        if not self._check_ollama_available(url):
            return None

        available_models = self._get_ollama_models(url)
        if not available_models:
            return None

        best_model = self._select_best_ollama_model(available_models)
        if best_model:
            logger.info(
                f"🤖 Ollama model detected: ollama:{best_model} "
                f"(from {len(available_models)} available models)"
            )
            return f"ollama:{best_model}"

        return None

    def _detect_lmstudio_model(self) -> str | None:
        """Detect available LM Studio models."""
        url = self._detect_lmstudio_url()
        if not self._check_lmstudio_available(url):
            return None

        available_models = self._get_lmstudio_models(url)
        if not available_models:
            return None

        best_model = self._select_best_model(available_models, is_lmstudio=True)
        if best_model:
            logger.info(
                f"🤖 LM Studio model detected: lmstudio:{best_model} "
                f"(from {len(available_models)} available models)"
            )
            return f"lmstudio:{best_model}"

        return None

    def _detect_ollama_url(self) -> str:
        """Detect Ollama API URL."""
        if self._ollama_url_cache:
            return self._ollama_url_cache

        # Check environment variable first
        env_url = os.getenv("OLLAMA_API_URL")
        if env_url:
            self._ollama_url_cache = env_url
            return env_url

        # Try common URLs
        for url in ModelConfig.OLLAMA_URLS:
            if self._check_ollama_available(url):
                self._ollama_url_cache = url
                return url

        # Fallback to default
        return ModelConfig.OLLAMA_URLS[0]

    def _check_ollama_available(self, url: str) -> bool:
        """Check if Ollama is running at the given URL."""
        try:
            response = httpx.get(f"{url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def _get_ollama_models(self, url: str) -> list[dict]:
        """Get available models from Ollama."""
        try:
            response = httpx.get(f"{url}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("models", [])
        except Exception as e:
            logger.debug(f"Failed to get Ollama models: {e}")
        return []

    def _check_lmstudio_available(self, url: str) -> bool:
        """Check if LM Studio is running at the given URL."""
        try:
            response = httpx.get(f"{url}/models", timeout=5)
            return response.status_code == 200
        except Exception:
            return False

    def _get_lmstudio_models(self, url: str) -> list[str]:
        """Get available models from LM Studio."""
        try:
            response = httpx.get(f"{url}/models", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = []
                for model in data.get("data", []):
                    model_id = model.get("id", "")
                    if model_id:
                        models.append(model_id)
                return models
        except Exception as e:
            logger.debug(f"Failed to get LM Studio models: {e}")
        return []

    def _select_best_ollama_model(self, available_models: list[dict]) -> str:
        """Select the best model from available Ollama models."""
        if not available_models:
            return ""

        # Extract model names
        model_names = [
            model.get("name", "") for model in available_models if model.get("name")
        ]
        if not model_names:
            return ""

        # Score and select best
        return self._score_and_select_best(model_names)

    def _select_best_model(
        self, available_models: list[str], is_lmstudio: bool = False
    ) -> str:
        """Select the best model from available models."""
        if not available_models:
            return ""

        return self._score_and_select_best(available_models)

    def _score_and_select_best(self, model_names: list[str]) -> str:
        """Score models and return the best one."""
        if not model_names:
            return ""

        if len(model_names) == 1:
            return model_names[0]

        # Score all models
        scored_models = [
            (name, self._calculate_model_score(name)) for name in model_names
        ]

        # Sort by score (highest first)
        scored_models.sort(key=lambda x: x[1], reverse=True)

        best_model, best_score = scored_models[0]
        logger.info(
            f"🔍 Evaluating {len(model_names)} models: {', '.join(model_names)}"
        )
        logger.info(f"🏆 Best model selected: {best_model}")

        # Log scores for debugging
        for model, score in scored_models[:3]:  # Top 3
            logger.debug(f"📊 {model}: {score} points")

        return best_model

    def _calculate_model_score(self, model_name: str) -> int:
        """Calculate a score for a model based on various factors."""
        score = 0

        # Size scoring
        for size, points in ModelConfig.SIZE_SCORES.items():
            if size in model_name.lower():
                score += points
                break

        # Family scoring
        for family, points in ModelConfig.FAMILY_SCORES.items():
            if family in model_name.lower():
                score += points
                break

        # Quality indicators
        for indicator, points in ModelConfig.QUALITY_INDICATORS.items():
            if indicator in model_name.lower():
                score += points

        # Poor indicators
        for indicator, points in ModelConfig.POOR_INDICATORS.items():
            if indicator in model_name.lower():
                score += points

        # Platform bonus (prefer Ollama over LM Studio)
        if "ollama:" in model_name.lower():
            score += 5

        return score

    def create_model_info(
        self, model_name: str, is_local: bool = True, url: str | None = None
    ) -> ModelInfo:
        """Create ModelInfo object for a given model."""
        # Extract provider
        if ":" in model_name:
            provider = model_name.split(":")[0]
        else:
            provider = "unknown"

        # Extract size and family
        size = None
        family = None

        for size_key in ModelConfig.SIZE_SCORES.keys():
            if size_key in model_name.lower():
                size = size_key
                break

        for family_key in ModelConfig.FAMILY_SCORES.keys():
            if family_key in model_name.lower():
                family = family_key
                break

        # Calculate score
        score = self._calculate_model_score(model_name)

        return ModelInfo(
            name=model_name,
            provider=provider,
            size=size,
            family=family,
            score=score,
            is_local=is_local,
            is_available=True,
            url=url,
        )
