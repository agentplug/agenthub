"""
Core LLM Component for AgentHub

This module provides a unified interface for LLM operations across the system.
It uses AISuite to support multiple LLM providers with a consistent API.
"""

from .client_manager import ClientManager
from .llm_decision_maker import DecisionResult, LLMDecisionMaker, StructuredDataResult
from .llm_service import (
    CoreLLMService,
    get_shared_llm_service,
    reset_shared_llm_service,
)
from .model_config import ModelConfig, ModelInfo
from .model_detector import ModelDetector

__all__ = [
    "ClientManager",
    "CoreLLMService",
    "DecisionResult",
    "LLMDecisionMaker",
    "ModelConfig",
    "ModelDetector",
    "ModelInfo",
    "StructuredDataResult",
    "get_shared_llm_service",
    "reset_shared_llm_service",
]
