"""
Core LLM Service for AgentHub

Provides a unified interface for LLM operations using AISuite.
Supports multiple providers with consistent API and JSON response handling.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class LogAnalysis:
    """Structured log analysis result"""

    summary: str
    progress: int
    status: str
    errors: list[str]
    suggestions: list[str]


class CoreLLMService:
    """
    Core LLM service using AISuite for unified LLM operations.

    Provides adaptive generation that handles both single prompts and
    conversations, with proper system prompt management and JSON response
    support.
    """

    def __init__(
        self, aisuite_client: Any = None, model: str = "openai:gpt-3.5-turbo"
    ) -> None:
        """
        Initialize Core LLM Service

        Args:
            aisuite_client: Optional AISuite client instance
            model: Model identifier in format "provider:model-name"
        """
        self.client = aisuite_client or self._initialize_aisuite()
        self.model = model
        self.cache: dict[str, Any] = {}

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
            import aisuite as ai

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
