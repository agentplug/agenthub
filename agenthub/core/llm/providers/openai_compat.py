"""Provider for any OpenAI-compatible ``/v1`` endpoint over httpx.

One transport serves LM Studio, llama.cpp's llama-server, and any other
server speaking the OpenAI chat-completions dialect; subclasses only carry
a name, capability defaults, and (for llama.cpp) a health probe.
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


class OpenAICompatProvider(LLMProvider):
    """Generic OpenAI-compatible endpoint (``{base}/chat/completions``)."""

    name = "openai_compat"

    def __init__(
        self,
        endpoint: EndpointConfig,
        *,
        native_json: bool = False,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._endpoint = endpoint
        self._base = endpoint.base_url.rstrip("/")
        self._native_json = native_json
        self._client = http_client or httpx.Client()

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            native_json=self._native_json,
            model_listing=True,
            is_local=True,
        )

    def _headers(self) -> dict[str, str]:
        if self._endpoint.api_key:
            return {"Authorization": f"Bearer {self._endpoint.api_key}"}
        return {}

    def is_available(self) -> bool:
        try:
            response = self._client.get(
                f"{self._base}/models",
                headers=self._headers(),
                timeout=self._endpoint.probe_timeout,
            )
            return response.status_code == 200
        except Exception as e:
            logger.debug("%s not reachable at %s: %s", self.name, self._base, e)
            return False

    def list_models(self) -> list[ModelDescriptor]:
        try:
            response = self._client.get(
                f"{self._base}/models",
                headers=self._headers(),
                timeout=self._endpoint.connect_timeout,
            )
        except httpx.HTTPError as e:
            raise LLMUnavailableError(
                f"{self.name} unreachable at {self._base}: {e}"
            ) from e
        if response.status_code != 200:
            raise LLMUnavailableError(
                f"{self.name} at {self._base} returned HTTP {response.status_code}"
            )
        try:
            entries = response.json().get("data", [])
        except json.JSONDecodeError as e:
            raise LLMGenerationError(f"{self.name} returned invalid JSON: {e}") from e

        models = []
        for entry in entries:
            model_id = entry.get("id")
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
        body: dict = {
            "model": request.model,
            "messages": [
                {"role": message.role, "content": message.content}
                for message in request.messages
            ],
            "temperature": request.temperature,
        }
        if request.max_tokens is not None:
            body["max_tokens"] = request.max_tokens
        if request.json_mode and self._native_json:
            body["response_format"] = {"type": "json_object"}
        body.update(request.extra)

        try:
            response = self._client.post(
                f"{self._base}/chat/completions",
                json=body,
                headers=self._headers(),
                timeout=self._endpoint.timeout,
            )
        except httpx.HTTPError as e:
            raise LLMUnavailableError(
                f"{self.name} unreachable at {self._base}: {e}"
            ) from e

        if response.status_code != 200:
            raise LLMGenerationError(
                f"{self.name} chat failed with HTTP {response.status_code}: "
                f"{response.text[:500]}"
            )
        try:
            payload = response.json()
            choice = payload["choices"][0]
            content = choice["message"]["content"]
        except (json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
            raise LLMGenerationError(
                f"Unexpected {self.name} response shape: {e}"
            ) from e

        return ChatResponse(
            content=content or "",
            model=payload.get("model", request.model),
            provider=self.name,
            finish_reason=choice.get("finish_reason"),
            usage=payload.get("usage"),
            raw=payload,
        )
