"""Exception hierarchy for the LLM layer.

Generation never fabricates content on failure: providers and the service
raise these exceptions and consumers decide their own degraded behavior
(fall back, retry, or surface the error).
"""

from typing import Any

from agenthub.core.tools.exceptions import AgentHubError


class LLMError(AgentHubError):
    """Base exception for all LLM-layer errors."""


class LLMUnavailableError(LLMError):
    """No usable LLM: endpoint unreachable, library missing, or no API key."""


class NoModelAvailableError(LLMUnavailableError):
    """Model detection exhausted every provider.

    Carries per-provider diagnostics so the error message explains what was
    probed and why each provider was skipped.
    """

    def __init__(
        self,
        message: str = "No LLM model available from any provider",
        probe_results: dict[str, str] | None = None,
        suggestions: list[str] | None = None,
    ):
        self.probe_results = probe_results or {}
        if self.probe_results:
            details = "; ".join(
                f"{provider}: {reason}"
                for provider, reason in self.probe_results.items()
            )
            message = f"{message} ({details})"
        super().__init__(
            message,
            suggestions=suggestions
            or [
                "Start a local model server (ollama serve, LM Studio, or llama-server)",
                "Or set a cloud API key, e.g. OPENAI_API_KEY or ANTHROPIC_API_KEY",
                "Or pin a model explicitly via AGENTHUB_LLM_MODEL",
            ],
        )


class ModelNotFoundError(LLMError):
    """An explicitly requested model is not served by any configured provider."""


class LLMGenerationError(LLMError):
    """A generation request failed: HTTP error, malformed payload, provider error."""


class LLMResponseFormatError(LLMGenerationError):
    """JSON-mode output could not be parsed into the expected structure."""

    def __init__(self, message: str, raw_response: Any = None):
        super().__init__(message)
        self.raw_response = raw_response
