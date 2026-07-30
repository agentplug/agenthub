"""Native Ollama provider over httpx.

Talks to Ollama's own API (``/api/chat``, ``/api/tags``) directly. Sampling
parameters go under the ``options`` key — the AISuite Ollama provider
splatted them at the top level of the body, where Ollama silently ignores
them (``temperature`` never reached the model).
"""

import json
import logging

import httpx

from ..base import LLMProvider
from ..config import EndpointConfig
from ..errors import LLMGenerationError, LLMUnavailableError
from ..types import (
    ChatRequest,
    ChatResponse,
    ModelDescriptor,
    ProviderCapabilities,
    parse_parameter_count,
)

logger = logging.getLogger(__name__)

_CAPABILITIES = ProviderCapabilities(
    native_json=True,  # Ollama's format:"json"
    model_listing=True,
    is_local=True,
)


class OllamaProvider(LLMProvider):
    """Ollama server provider (default http://localhost:11434)."""

    name = "ollama"

    def __init__(
        self,
        endpoint: EndpointConfig,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._endpoint = endpoint
        self._base = endpoint.base_url.rstrip("/")
        self._client = http_client or httpx.Client()

    @property
    def capabilities(self) -> ProviderCapabilities:
        return _CAPABILITIES

    def is_available(self) -> bool:
        try:
            response = self._client.get(
                f"{self._base}/api/tags", timeout=self._endpoint.probe_timeout
            )
            return bool(response.status_code == 200)
        except Exception as e:
            logger.debug("Ollama not reachable at %s: %s", self._base, e)
            return False

    def list_models(self) -> list[ModelDescriptor]:
        try:
            response = self._client.get(
                f"{self._base}/api/tags", timeout=self._endpoint.connect_timeout
            )
        except httpx.HTTPError as e:
            raise LLMUnavailableError(f"Ollama unreachable at {self._base}: {e}") from e
        if response.status_code != 200:
            raise LLMUnavailableError(
                f"Ollama at {self._base} returned HTTP {response.status_code}"
            )
        try:
            entries = response.json().get("models", [])
        except json.JSONDecodeError as e:
            raise LLMGenerationError(f"Ollama returned invalid JSON: {e}") from e

        models = []
        for entry in entries:
            model_id = entry.get("name")
            if not model_id:
                continue
            models.append(
                ModelDescriptor(
                    id=model_id,
                    provider=self.name,
                    is_local=True,
                    size_b=parse_parameter_count(model_id),
                )
            )
        return models

    def _chat(self, request: ChatRequest) -> ChatResponse:
        options: dict = {"temperature": request.temperature}
        if request.max_tokens is not None:
            options["num_predict"] = request.max_tokens
        # Provider passthrough: Ollama expects sampling params under options.
        options.update(request.extra)

        body: dict = {
            "model": request.model,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in request.messages
            ],
            "stream": False,
            "options": options,
        }
        if request.json_mode:
            body["format"] = "json"

        try:
            response = self._client.post(
                f"{self._base}/api/chat", json=body, timeout=self._endpoint.timeout
            )
        except httpx.HTTPError as e:
            raise LLMUnavailableError(f"Ollama unreachable at {self._base}: {e}") from e

        if response.status_code != 200:
            raise LLMGenerationError(
                f"Ollama chat failed with HTTP {response.status_code}: "
                f"{response.text[:500]}"
            )
        try:
            payload = response.json()
            content = payload["message"]["content"]
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            raise LLMGenerationError(f"Unexpected Ollama response shape: {e}") from e

        usage = None
        if "prompt_eval_count" in payload or "eval_count" in payload:
            usage = {
                "prompt_tokens": payload.get("prompt_eval_count", 0),
                "completion_tokens": payload.get("eval_count", 0),
            }

        return ChatResponse(
            content=content,
            model=request.model,
            provider=self.name,
            finish_reason=payload.get("done_reason"),
            usage=usage,
            raw=payload,
        )
