"""Tests for the local LLM providers over mocked httpx transports.

The contract suite runs identically against every provider; per-provider
classes pin transport details (Ollama's options-nested temperature, the
llama.cpp health probe, LM Studio's JSON-mode default).
"""

import json

import httpx
import pytest

from agenthub.core.llm.base import LLMProvider
from agenthub.core.llm.config import EndpointConfig, LLMConfig
from agenthub.core.llm.errors import LLMGenerationError, LLMUnavailableError
from agenthub.core.llm.providers import (
    LlamaCppProvider,
    LMStudioProvider,
    OllamaProvider,
    OpenAICompatProvider,
    build_providers,
)
from agenthub.core.llm.types import ChatRequest, Message

OLLAMA_TAGS = {"models": [{"name": "qwen3:8b"}, {"name": "nomic-embed-text"}]}
OLLAMA_CHAT = {
    "message": {"role": "assistant", "content": '{"answer": 42}'},
    "done_reason": "stop",
    "prompt_eval_count": 10,
    "eval_count": 5,
}
OPENAI_MODELS = {"data": [{"id": "/models/qwen3-8b-q4.gguf"}, {"id": "phi-4"}]}
OPENAI_CHAT = {
    "model": "qwen3-8b",
    "choices": [
        {"message": {"role": "assistant", "content": "hello"}, "finish_reason": "stop"}
    ],
    "usage": {"prompt_tokens": 10, "completion_tokens": 2},
}


class Recorder:
    """Collects requests seen by a mock transport."""

    def __init__(self) -> None:
        self.requests: list[httpx.Request] = []

    @property
    def last(self) -> httpx.Request:
        return self.requests[-1]

    def last_body(self) -> dict:
        return json.loads(self.requests[-1].content)


def make_transport(
    recorder: Recorder, routes: dict[str, object]
) -> httpx.MockTransport:
    """routes: path -> dict payload | int status | Exception to raise."""

    def handler(request: httpx.Request) -> httpx.Response:
        recorder.requests.append(request)
        for path, result in routes.items():
            if request.url.path == path:
                if isinstance(result, Exception):
                    raise result
                if isinstance(result, int):
                    return httpx.Response(result, text="error body")
                if isinstance(result, str):
                    return httpx.Response(200, text=result)
                return httpx.Response(200, json=result)
        return httpx.Response(404, text="not found")

    return httpx.MockTransport(handler)


ENDPOINT = EndpointConfig("http://test:1")
ENDPOINT_V1 = EndpointConfig("http://test:1/v1")


def make_request(**overrides) -> ChatRequest:
    defaults: dict = {
        "model": "qwen3:8b",
        "messages": (Message(role="user", content="hi"),),
    }
    defaults.update(overrides)
    return ChatRequest(**defaults)


# (factory, happy-routes, chat_path, list_path)
PROVIDER_CASES = {
    "ollama": (
        lambda client: OllamaProvider(ENDPOINT, http_client=client),
        {"/api/tags": OLLAMA_TAGS, "/api/chat": OLLAMA_CHAT},
        "/api/chat",
        "/api/tags",
    ),
    "openai_compat": (
        lambda client: OpenAICompatProvider(ENDPOINT_V1, http_client=client),
        {"/v1/models": OPENAI_MODELS, "/v1/chat/completions": OPENAI_CHAT},
        "/v1/chat/completions",
        "/v1/models",
    ),
    "lmstudio": (
        lambda client: LMStudioProvider(ENDPOINT_V1, http_client=client),
        {"/v1/models": OPENAI_MODELS, "/v1/chat/completions": OPENAI_CHAT},
        "/v1/chat/completions",
        "/v1/models",
    ),
    "llamacpp": (
        lambda client: LlamaCppProvider(ENDPOINT_V1, http_client=client),
        {
            "/health": {"status": "ok"},
            "/v1/models": OPENAI_MODELS,
            "/v1/chat/completions": OPENAI_CHAT,
        },
        "/v1/chat/completions",
        "/v1/models",
    ),
}


def build(name: str, routes: dict | None = None) -> tuple[LLMProvider, Recorder]:
    factory, happy_routes, _, _ = PROVIDER_CASES[name]
    recorder = Recorder()
    transport = make_transport(recorder, happy_routes if routes is None else routes)
    return factory(httpx.Client(transport=transport)), recorder


@pytest.mark.parametrize("name", list(PROVIDER_CASES))
class TestProviderContract:
    def test_implements_interface(self, name):
        provider, _ = build(name)
        assert isinstance(provider, LLMProvider)
        assert provider.name == name
        assert provider.capabilities.is_local

    def test_is_available_true_on_200(self, name):
        provider, _ = build(name)
        assert provider.is_available() is True

    def test_is_available_false_on_connect_error_and_never_raises(self, name):
        provider, _ = build(
            name,
            routes={
                path: httpx.ConnectError("refused") for path in PROVIDER_CASES[name][1]
            },
        )
        assert provider.is_available() is False

    def test_is_available_false_on_500(self, name):
        provider, _ = build(name, routes=dict.fromkeys(PROVIDER_CASES[name][1], 500))
        assert provider.is_available() is False

    def test_list_models_parses_ids_and_sizes(self, name):
        provider, _ = build(name)
        models = provider.list_models()
        assert models, "expected at least one model from fixtures"
        assert all(model.provider == name for model in models)
        assert all(model.is_local for model in models)
        # Both fixture sets contain one 8b model parseable from the id.
        assert any(model.size_b == 8.0 for model in models)

    def test_list_models_raises_unavailable_when_down(self, name):
        provider, _ = build(
            name,
            routes={
                path: httpx.ConnectError("refused") for path in PROVIDER_CASES[name][1]
            },
        )
        with pytest.raises(LLMUnavailableError):
            provider.list_models()

    def test_chat_returns_content(self, name):
        provider, _ = build(name)
        response = provider.chat(make_request())
        assert response.content
        assert response.provider == name

    def test_chat_raises_generation_error_on_500(self, name):
        provider, _ = build(name, routes=dict.fromkeys(PROVIDER_CASES[name][1], 500))
        with pytest.raises(LLMGenerationError):
            provider.chat(make_request())

    def test_chat_raises_generation_error_on_malformed_body(self, name):
        provider, _ = build(
            name, routes=dict.fromkeys(PROVIDER_CASES[name][1], "not json {")
        )
        with pytest.raises(LLMGenerationError):
            provider.chat(make_request())

    def test_chat_raises_unavailable_on_connect_error(self, name):
        provider, _ = build(
            name,
            routes={
                path: httpx.ConnectError("refused") for path in PROVIDER_CASES[name][1]
            },
        )
        with pytest.raises(LLMUnavailableError):
            provider.chat(make_request())

    def test_json_mode_is_native_or_injected(self, name):
        provider, recorder = build(name)
        provider.chat(make_request(json_mode=True))
        body = recorder.last_body()
        if provider.capabilities.native_json:
            assert body.get("format") == "json" or body.get("response_format") == {
                "type": "json_object"
            }
            assert "valid JSON only" not in body["messages"][-1]["content"]
        else:
            assert "response_format" not in body and "format" not in body
            assert "valid JSON only" in body["messages"][-1]["content"]

    def test_reasoning_tags_stripped(self, name):
        _, happy_routes, chat_path, _ = PROVIDER_CASES[name]
        thinking = "<think>plan</think>done"
        if chat_path == "/api/chat":
            payload = {**OLLAMA_CHAT, "message": {"content": thinking}}
        else:
            payload = {
                **OPENAI_CHAT,
                "choices": [
                    {"message": {"content": thinking}, "finish_reason": "stop"}
                ],
            }
        provider, _ = build(name, routes={**happy_routes, chat_path: payload})
        response = provider.chat(make_request())
        assert response.content == "done"
        assert response.reasoning_content == "plan"


class TestOllamaRequestShape:
    def test_temperature_lands_under_options(self):
        """Regression: AISuite splatted temperature at the top level, where
        Ollama silently ignores it."""
        provider, recorder = build("ollama")
        provider.chat(make_request(temperature=0.7))
        body = recorder.last_body()
        assert body["options"]["temperature"] == 0.7
        assert "temperature" not in body

    def test_stream_disabled_and_max_tokens_mapped(self):
        provider, recorder = build("ollama")
        provider.chat(make_request(max_tokens=128))
        body = recorder.last_body()
        assert body["stream"] is False
        assert body["options"]["num_predict"] == 128

    def test_extra_merges_into_options(self):
        provider, recorder = build("ollama")
        provider.chat(make_request(extra={"top_p": 0.9}))
        assert recorder.last_body()["options"]["top_p"] == 0.9

    def test_usage_mapped(self):
        provider, _ = build("ollama")
        response = provider.chat(make_request())
        assert response.usage == {"prompt_tokens": 10, "completion_tokens": 5}


class TestOpenAICompatRequestShape:
    def test_no_auth_header_without_key(self):
        provider, recorder = build("openai_compat")
        provider.chat(make_request())
        assert "authorization" not in recorder.last.headers

    def test_auth_header_with_key(self):
        recorder = Recorder()
        transport = make_transport(recorder, {"/v1/chat/completions": OPENAI_CHAT})
        provider = OpenAICompatProvider(
            EndpointConfig("http://test:1/v1", api_key="secret"),
            http_client=httpx.Client(transport=transport),
        )
        provider.chat(make_request())
        assert recorder.last.headers["authorization"] == "Bearer secret"

    def test_temperature_at_top_level(self):
        provider, recorder = build("openai_compat")
        provider.chat(make_request(temperature=0.3))
        assert recorder.last_body()["temperature"] == 0.3


class TestLMStudioDefaults:
    def test_no_response_format_by_default(self):
        provider, recorder = build("lmstudio")
        provider.chat(make_request(json_mode=True))
        body = recorder.last_body()
        assert "response_format" not in body
        assert "valid JSON only" in body["messages"][-1]["content"]

    def test_native_json_opt_in(self):
        recorder = Recorder()
        transport = make_transport(recorder, {"/v1/chat/completions": OPENAI_CHAT})
        provider = LMStudioProvider(
            ENDPOINT_V1, native_json=True, http_client=httpx.Client(transport=transport)
        )
        provider.chat(make_request(json_mode=True))
        assert recorder.last_body()["response_format"] == {"type": "json_object"}


class TestLlamaCppHealthProbe:
    def test_ready(self):
        provider, recorder = build("llamacpp")
        assert provider.is_available() is True
        assert recorder.last.url.path == "/health"

    def test_loading_model_is_unavailable(self):
        provider, _ = build(
            "llamacpp",
            routes={"/health": 503, "/v1/models": OPENAI_MODELS},
        )
        assert provider.is_available() is False

    def test_missing_health_falls_back_to_models(self):
        # No /health route: 404 → fall back to /v1/models, which succeeds.
        provider, recorder = build("llamacpp", routes={"/v1/models": OPENAI_MODELS})
        assert provider.is_available() is True
        assert recorder.last.url.path == "/v1/models"

    def test_native_json_default(self):
        provider, recorder = build("llamacpp")
        provider.chat(make_request(json_mode=True))
        assert recorder.last_body()["response_format"] == {"type": "json_object"}


class TestBuildProviders:
    def test_priority_order_and_unknown_skipped(self):
        config = LLMConfig.from_env(
            {"AGENTHUB_LLM_PROVIDER_PRIORITY": "llamacpp,ollama,bogus"}
        )
        providers = build_providers(config)
        assert [provider.name for provider in providers] == ["llamacpp", "ollama"]

    def test_default_order_expands_cloud_vendors(self):
        providers = build_providers(LLMConfig.from_env({}))
        names = [provider.name for provider in providers]
        assert names[:3] == ["ollama", "lmstudio", "llamacpp"]
        # "cloud" expands to one provider per configured vendor, in order.
        assert names[3:5] == ["openai", "anthropic"]
        assert len(names) > 5
