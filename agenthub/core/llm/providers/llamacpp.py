"""llama.cpp provider: OpenAI-compatible transport with llama-server defaults.

llama-server implements ``response_format: json_object`` via grammar
constraints, which is strictly better than instruction injection, so
``native_json`` is True. Availability prefers the ``/health`` endpoint
(200 = ready, 503 = still loading the model) and falls back to
``/v1/models`` for proxies that don't expose ``/health``.
"""

import logging

import httpx

from ..config import EndpointConfig
from .openai_compat import OpenAICompatProvider

logger = logging.getLogger(__name__)


class LlamaCppProvider(OpenAICompatProvider):
    """llama.cpp llama-server provider (default http://localhost:8080/v1)."""

    name = "llamacpp"

    def __init__(
        self,
        endpoint: EndpointConfig,
        *,
        http_client: httpx.Client | None = None,
    ) -> None:
        super().__init__(endpoint, native_json=True, http_client=http_client)

    def is_available(self) -> bool:
        # /health lives at the server root, not under /v1.
        health_url = f"{self._base.removesuffix('/v1')}/health"
        try:
            response = self._client.get(
                health_url, timeout=self._endpoint.probe_timeout
            )
        except Exception as e:
            logger.debug("llama.cpp not reachable at %s: %s", health_url, e)
            return False
        if response.status_code == 200:
            return True
        if response.status_code == 503:
            # Server up but model still loading: not usable yet.
            logger.debug("llama.cpp at %s is still loading its model", health_url)
            return False
        # No /health (e.g. a proxy): fall back to the OpenAI-compatible probe.
        return super().is_available()
