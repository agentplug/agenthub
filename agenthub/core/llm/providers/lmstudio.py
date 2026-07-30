"""LM Studio provider: OpenAI-compatible transport with LM Studio defaults.

``native_json`` defaults to False: plain ``{"type": "json_object"}``
response_format support is version-dependent in LM Studio, so instruction
injection is the reliable default. Enable native mode per install with
``LMSTUDIO_NATIVE_JSON=1``.
"""

import httpx

from ..config import EndpointConfig
from .openai_compat import OpenAICompatProvider


class LMStudioProvider(OpenAICompatProvider):
    """LM Studio server provider (default http://localhost:1234/v1)."""

    name = "lmstudio"

    def __init__(
        self,
        endpoint: EndpointConfig,
        *,
        native_json: bool = False,
        http_client: httpx.Client | None = None,
    ) -> None:
        super().__init__(endpoint, native_json=native_json, http_client=http_client)
