"""Core LLM component for AgentHub.

A provider-generalized LLM layer: local providers (Ollama, LM Studio,
llama.cpp) speak their native protocols over httpx; cloud vendors route
through LiteLLM. ``LLMService`` is the entry point; ``get_shared_llm_service``
returns the shared process-wide instance.
"""

from .base import LLMProvider
from .config import EndpointConfig, LLMConfig
from .errors import (
    LLMError,
    LLMGenerationError,
    LLMResponseFormatError,
    LLMUnavailableError,
    ModelNotFoundError,
    NoModelAvailableError,
)
from .llm_decision_maker import DecisionResult, LLMDecisionMaker, StructuredDataResult
from .llm_service import (
    CoreLLMService,
    get_shared_llm_service,
    reset_shared_llm_service,
)
from .selection import ModelSelector
from .service import LLMService
from .types import ChatRequest, ChatResponse, Message, ModelDescriptor

# Legacy alias: ModelInfo was the pre-refactor descriptor dataclass.
ModelInfo = ModelDescriptor

__all__ = [
    "ChatRequest",
    "ChatResponse",
    "CoreLLMService",
    "DecisionResult",
    "EndpointConfig",
    "LLMConfig",
    "LLMDecisionMaker",
    "LLMError",
    "LLMGenerationError",
    "LLMProvider",
    "LLMResponseFormatError",
    "LLMService",
    "LLMUnavailableError",
    "Message",
    "ModelDescriptor",
    "ModelInfo",
    "ModelNotFoundError",
    "ModelSelector",
    "NoModelAvailableError",
    "StructuredDataResult",
    "get_shared_llm_service",
    "reset_shared_llm_service",
]
