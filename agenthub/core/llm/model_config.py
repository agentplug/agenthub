"""
Model Configuration for AgentHub LLM Service

This module contains configuration constants and data classes for model selection,
scoring, and management across different LLM providers.
"""

from dataclasses import dataclass
from typing import Any


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
        "qwen3:latest",
        "qwen:latest",  # Qwen models
    ]

    # Cloud model providers and their models
    CLOUD_MODELS = {
        "openai": ["gpt-4.1-mini", "gpt-4.1", "gpt-4o-mini", "gpt-3.5-turbo"],
        "anthropic": ["claude-3-5-sonnet-20241022", "claude-3-5-haiku-20241022"],
        "google": ["gemini-1.5-pro", "gemini-1.5-flash"],
        "deepseek": ["deepseek-chat", "deepseek-coder"],
        "groq": ["llama-3.1-70b-versatile", "llama-3.1-8b-instant"],
        "mistral": ["mistral-large-latest", "mistral-small-latest"],
        "cohere": ["command-r-plus", "command-r"],
    }

    # Model size scoring (larger models get higher scores)
    SIZE_SCORES = {
        "1b": 10,
        "2b": 15,
        "3b": 20,
        "4b": 35,
        "7b": 30,
        "8b": 40,
        "13b": 50,
        "20b": 60,
        "32b": 70,
        "70b": 80,
        "120b": 90,
        "latest": 40,  # Default for "latest" models
    }

    # Model family scoring (quality indicators)
    FAMILY_SCORES = {
        "gpt-oss": 50,  # OpenAI open-weight models
        "deepseek": 60,  # DeepSeek reasoning models
        "qwen": 60,  # Qwen models
        "gemma": 45,
        "llama": 40,
        "mistral": 45,
        "claude": 55,
        "gpt": 50,
    }

    # Quality indicators that boost scores
    QUALITY_INDICATORS = {
        "reasoning": 10,
        "thinking": 5,
        "instruct": 5,
        "chat": 3,
        "latest": 5,
        "stable": 3,
    }

    # Poor model indicators that reduce scores
    POOR_INDICATORS = {
        "embedding": -50,  # Embedding models are not for generation
        "instruct": -5,  # Some instruct models are outdated
        "old": -10,
        "deprecated": -20,
    }

    # Default URLs for local providers
    OLLAMA_URLS = [
        "http://localhost:11434",
        "http://127.0.0.1:11434",
        "http://0.0.0.0:11434",
    ]

    LMSTUDIO_URLS = [
        "http://localhost:1234/v1",
        "http://127.0.0.1:1234/v1",
        "http://0.0.0.0:1234/v1",
    ]


@dataclass
class LogAnalysis:
    """Data class for log analysis results."""

    summary: str
    key_insights: list[str]
    recommendations: list[str]
    confidence: float


@dataclass
class ModelInfo:
    """Data class for model information."""

    name: str
    provider: str
    size: str | None
    family: str | None
    score: int
    is_local: bool
    is_available: bool
    url: str | None = None
    parameters: dict[str, Any] | None = None
