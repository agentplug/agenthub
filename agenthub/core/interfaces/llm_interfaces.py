"""LLM-related interfaces to break circular dependencies.

``LLMServiceProtocol`` mirrors the real surface of
``agenthub.core.llm.service.LLMService`` so consumers and DI can type
against it without importing the LLM package.
"""

from typing import Any, Protocol

from typing_extensions import runtime_checkable


@runtime_checkable
class LLMServiceProtocol(Protocol):
    """Protocol for the LLM service."""

    def generate(
        self,
        input_data: str | list[dict],
        system_prompt: str | None = None,
        return_json: bool = False,
        temperature: float = 0.0,
        **kwargs: Any,
    ) -> str:
        """Generate a text response. Raises LLMError on failure."""
        ...

    def generate_structured(
        self,
        input_data: str | list[dict],
        system_prompt: str | None = None,
        temperature: float = 0.0,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Generate and parse a JSON object response."""
        ...

    def get_current_model(self) -> str:
        """The selected model's qualified id."""
        ...

    def is_available(self) -> bool:
        """Whether any provider can serve generation right now."""
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
