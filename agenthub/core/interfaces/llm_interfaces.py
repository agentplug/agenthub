"""LLM-related interfaces to break circular dependencies."""

from typing import Any, Protocol

from typing_extensions import runtime_checkable


@runtime_checkable
class LLMServiceProtocol(Protocol):
    """Protocol for LLM service."""

    def generate_response(
        self, prompt: str, model: str | None = None, **kwargs: Any
    ) -> str:
        """Generate response from LLM."""
        ...

    def generate_structured_response(
        self,
        prompt: str,
        response_format: dict[str, Any],
        model: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate structured response from LLM."""
        ...


@runtime_checkable
class LLMDecisionMakerProtocol(Protocol):
    """Protocol for LLM decision maker."""

    def make_decision(
        self, options: list[dict[str, Any]], context: str, **kwargs: Any
    ) -> Any:
        """Make decision using LLM."""
        ...

    def extract_structured_data(
        self, text: str, schema: dict[str, Any], **kwargs: Any
    ) -> Any:
        """Extract structured data using LLM."""
        ...
