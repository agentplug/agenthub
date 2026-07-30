"""Tests for ModelSelector, LLMService, and the LiteLLM cloud provider.

Selection tests use pure fake providers (no HTTP anywhere) and pin
regressions for every bug in the old scoring tables. Cloud-provider tests
stub the litellm module in sys.modules.
"""

import sys
import types as types_module
from unittest.mock import patch

import pytest

from agenthub.core.interfaces.llm_interfaces import LLMServiceProtocol
from agenthub.core.llm.base import LLMProvider
from agenthub.core.llm.config import LLMConfig
from agenthub.core.llm.errors import (
    LLMResponseFormatError,
    LLMUnavailableError,
    ModelNotFoundError,
    NoModelAvailableError,
)
from agenthub.core.llm.providers.cloud import LiteLLMCloudProvider
from agenthub.core.llm.selection import ModelSelector
from agenthub.core.llm.service import LLMService
from agenthub.core.llm.types import (
    ChatRequest,
    ChatResponse,
    ModelDescriptor,
    ProviderCapabilities,
    parse_parameter_count,
)


class FakeProvider(LLMProvider):
    """Pure in-memory provider for selection and service tests."""

    def __init__(
        self,
        name: str,
        model_ids: list[str],
        available: bool = True,
        reply: str = "ok",
    ):
        self.name = name
        self._model_ids = model_ids
        self._available = available
        self._reply = reply
        self.availability_probes = 0
        self.chat_requests: list[ChatRequest] = []

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(native_json=True, model_listing=True, is_local=True)

    def is_available(self) -> bool:
        self.availability_probes += 1
        return self._available

    def list_models(self):
        if not self._available:
            raise LLMUnavailableError(f"{self.name} down")
        return [
            ModelDescriptor(
                id=model_id,
                provider=self.name,
                is_local=True,
                size_b=parse_parameter_count(model_id),
            )
            for model_id in self._model_ids
        ]

    def _chat(self, request: ChatRequest) -> ChatResponse:
        self.chat_requests.append(request)
        return ChatResponse(
            content=self._reply, model=request.model, provider=self.name
        )


def make_selector(*providers, preferred=()):
    config = LLMConfig.from_env(
        {"AGENTHUB_LLM_PREFERRED": ",".join(preferred)} if preferred else {}
    )
    return ModelSelector(list(providers), config)


class TestModelSelector:
    def test_numeric_size_ranking(self):
        """Regression: the old table scored '4b' (35) above '7b' (30)."""
        provider = FakeProvider("ollama", ["small-4b", "small-7b"])
        selector = make_selector(provider, preferred=("nomatch*",))
        _, best = selector.select()
        assert best.id == "small-7b"

    def test_embedding_models_never_selected(self):
        provider = FakeProvider("ollama", ["nomic-embed-text", "bge-m3"])
        selector = make_selector(provider)
        with pytest.raises(NoModelAvailableError) as exc_info:
            selector.select()
        assert exc_info.value.probe_results["ollama"] == "no usable chat models"

    def test_preference_glob_beats_size(self):
        provider = FakeProvider("ollama", ["huge-70b", "qwen3:4b"])
        selector = make_selector(provider, preferred=("*qwen3*",))
        _, best = selector.select()
        assert best.id == "qwen3:4b"

    def test_provider_priority_beats_size(self):
        first = FakeProvider("ollama", ["tiny-1b"])
        second = FakeProvider("lmstudio", ["huge-70b"])
        selector = make_selector(first, second)
        provider, best = selector.select()
        assert provider is first
        assert best.id == "tiny-1b"

    def test_unavailable_provider_skipped_with_diagnostics(self):
        down = FakeProvider("ollama", ["qwen3:8b"], available=False)
        up = FakeProvider("lmstudio", ["phi-7b"])
        selector = make_selector(down, up)
        provider, best = selector.select()
        assert provider is up
        assert best.id == "phi-7b"

    def test_no_model_error_enumerates_all_providers(self):
        selector = make_selector(
            FakeProvider("ollama", [], available=False),
            FakeProvider("lmstudio", ["nomic-embed-text"]),
        )
        with pytest.raises(NoModelAvailableError) as exc_info:
            selector.select()
        assert set(exc_info.value.probe_results) == {"ollama", "lmstudio"}
        assert "ollama: not available" in str(exc_info.value)

    def test_deterministic_tie_break(self):
        provider = FakeProvider("ollama", ["bbb-7b", "aaa-7b"])
        selector = make_selector(provider, preferred=("nomatch*",))
        _, best = selector.select()
        assert best.id == "aaa-7b"

    def test_resolve_known_provider(self):
        provider = FakeProvider("ollama", [])
        selector = make_selector(provider)
        resolved_provider, descriptor = selector.resolve("ollama:qwen3:32b")
        assert resolved_provider is provider
        # partition on the first colon keeps ollama's model:tag format intact
        assert descriptor.id == "qwen3:32b"
        assert descriptor.size_b == 32.0
        assert descriptor.qualified_id == "ollama:qwen3:32b"

    def test_resolve_unknown_provider_raises(self):
        selector = make_selector(FakeProvider("ollama", []))
        with pytest.raises(ModelNotFoundError, match="anthropic"):
            selector.resolve("anthropic:claude-sonnet-4-6")

    def test_resolve_malformed_id_raises(self):
        selector = make_selector(FakeProvider("ollama", []))
        with pytest.raises(ModelNotFoundError, match="expected 'provider:model'"):
            selector.resolve("just-a-model-name")

    def test_candidates_spans_providers_ranked(self):
        first = FakeProvider("ollama", ["a-4b", "a-7b"])
        second = FakeProvider("lmstudio", ["b-13b"])
        selector = make_selector(first, second, preferred=("nomatch*",))
        candidates = selector.candidates()
        assert [descriptor.id for _, descriptor in candidates] == [
            "a-7b",
            "a-4b",
            "b-13b",
        ]


class TestLLMService:
    def make_service(self, *providers, model=None):
        return LLMService(
            config=LLMConfig.from_env({}),
            providers=list(providers),
            model=model,
        )

    def test_construction_performs_no_probing(self):
        provider = FakeProvider("ollama", ["qwen3:8b"])
        self.make_service(provider)
        assert provider.availability_probes == 0

    def test_string_input_normalized(self):
        provider = FakeProvider("ollama", ["qwen3:8b"])
        service = self.make_service(provider)
        result = service.generate("hello", system_prompt="be brief")
        assert result == "ok"
        request = provider.chat_requests[0]
        assert [(m.role, m.content) for m in request.messages] == [
            ("system", "be brief"),
            ("user", "hello"),
        ]

    def test_message_list_filters_invalid_roles(self):
        provider = FakeProvider("ollama", ["qwen3:8b"])
        service = self.make_service(provider)
        service.generate(
            [
                {"role": "user", "content": "hi"},
                {"role": "tool", "content": "dropped"},
                {"role": "assistant", "content": "there"},
            ]
        )
        request = provider.chat_requests[0]
        assert [m.role for m in request.messages] == ["user", "assistant"]

    def test_invalid_input_type_raises_value_error(self):
        service = self.make_service(FakeProvider("ollama", ["qwen3:8b"]))
        with pytest.raises(ValueError):
            service.generate(42)  # type: ignore[arg-type]

    def test_kwargs_pass_through_as_extra(self):
        provider = FakeProvider("ollama", ["qwen3:8b"])
        service = self.make_service(provider)
        service.generate("hi", temperature=0.5, top_p=0.9)
        request = provider.chat_requests[0]
        assert request.temperature == 0.5
        assert request.extra == {"top_p": 0.9}

    def test_failure_raises_never_fabricates(self):
        service = self.make_service(FakeProvider("ollama", [], available=False))
        with pytest.raises(LLMUnavailableError):
            service.generate("hi")
        # The legacy behavior returned this literal string as a response.
        assert not service.is_available()

    def test_forced_model_skips_detection(self):
        provider = FakeProvider("ollama", [])
        service = self.make_service(provider, model="ollama:qwen3:8b")
        service.generate("hi")
        assert provider.chat_requests[0].model == "qwen3:8b"
        assert service.get_current_model() == "ollama:qwen3:8b"

    def test_selection_is_memoized(self):
        provider = FakeProvider("ollama", ["qwen3:8b"])
        service = self.make_service(provider)
        service.generate("one")
        service.generate("two")
        assert provider.availability_probes == 1

    def test_generate_structured_parses(self):
        provider = FakeProvider(
            "ollama", ["qwen3:8b"], reply='prose {"answer": 42} more'
        )
        service = self.make_service(provider)
        assert service.generate_structured("hi") == {"answer": 42}
        assert provider.chat_requests[0].json_mode is True

    def test_generate_structured_error_carries_raw(self):
        provider = FakeProvider("ollama", ["qwen3:8b"], reply="not json")
        service = self.make_service(provider)
        with pytest.raises(LLMResponseFormatError) as exc_info:
            service.generate_structured("hi")
        assert exc_info.value.raw_response == "not json"

    def test_conforms_to_protocol(self):
        service = self.make_service(FakeProvider("ollama", ["qwen3:8b"]))
        assert isinstance(service, LLMServiceProtocol)


class FakeLiteLLMResponse:
    class Choice:
        class Message:
            content = "cloud says hi"

        message = Message()
        finish_reason = "stop"

    choices = [Choice()]

    class Usage:
        prompt_tokens = 3
        completion_tokens = 4

    usage = Usage()


def make_fake_litellm(recorder: dict, supports_response_format=True, error_type=None):
    """Build a stub litellm module. error_type: None | 'auth' | 'generic'.

    Raised exceptions come from this module's own exception classes so the
    provider's isinstance-based mapping sees the types it imported.
    """
    module = types_module.ModuleType("litellm")

    class AuthenticationError(Exception):
        pass

    class APIConnectionError(Exception):
        pass

    exceptions = types_module.ModuleType("litellm.exceptions")
    exceptions.AuthenticationError = AuthenticationError
    exceptions.APIConnectionError = APIConnectionError
    module.exceptions = exceptions

    def completion(**kwargs):
        recorder.update(kwargs)
        if error_type == "auth":
            raise AuthenticationError("bad key")
        if error_type == "generic":
            raise RuntimeError("boom")
        return FakeLiteLLMResponse()

    def get_supported_openai_params(model):
        if supports_response_format:
            return ["temperature", "response_format"]
        return ["temperature"]

    module.completion = completion
    module.get_supported_openai_params = get_supported_openai_params
    return module


class TestLiteLLMCloudProvider:
    def run_with_fake_litellm(self, provider, request, **fake_kwargs):
        recorder: dict = {}
        module = make_fake_litellm(recorder, **fake_kwargs)
        with patch.dict(sys.modules, {"litellm": module}):
            response = provider.chat(request)
        return response, recorder

    def make_request(self, **overrides):
        from agenthub.core.llm.types import Message

        defaults: dict = {
            "model": "gpt-5",
            "messages": (Message(role="user", content="hi"),),
        }
        defaults.update(overrides)
        return ChatRequest(**defaults)

    def test_model_gets_vendor_prefix_and_drop_params(self):
        provider = LiteLLMCloudProvider("openai", ["gpt-5"])
        response, recorder = self.run_with_fake_litellm(provider, self.make_request())
        assert recorder["model"] == "openai/gpt-5"
        assert recorder["drop_params"] is True
        assert response.content == "cloud says hi"
        assert response.provider == "openai"
        assert response.usage == {"prompt_tokens": 3, "completion_tokens": 4}

    def test_json_mode_uses_response_format_when_supported(self):
        provider = LiteLLMCloudProvider("openai", ["gpt-5"])
        _, recorder = self.run_with_fake_litellm(
            provider, self.make_request(json_mode=True)
        )
        assert recorder["response_format"] == {"type": "json_object"}

    def test_json_mode_injects_when_not_supported(self):
        provider = LiteLLMCloudProvider("legacyvendor", ["old-model"])
        _, recorder = self.run_with_fake_litellm(
            provider,
            self.make_request(json_mode=True),
            supports_response_format=False,
        )
        assert "response_format" not in recorder
        assert "valid JSON only" in recorder["messages"][-1]["content"]

    def test_is_available_is_key_presence(self):
        provider = LiteLLMCloudProvider("openai", ["gpt-5"])
        with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
            assert provider.is_available() is True
        with patch.dict("os.environ", {}, clear=True):
            assert provider.is_available() is False

    def test_list_models_returns_configured_defaults(self):
        provider = LiteLLMCloudProvider("anthropic", ["claude-sonnet-4-6"])
        models = provider.list_models()
        assert [m.qualified_id for m in models] == ["anthropic:claude-sonnet-4-6"]
        assert not models[0].is_local

    def test_auth_error_maps_to_unavailable(self):
        provider = LiteLLMCloudProvider("openai", ["gpt-5"])
        recorder: dict = {}
        module = make_fake_litellm(recorder, error_type="auth")
        with patch.dict(sys.modules, {"litellm": module}):
            with pytest.raises(LLMUnavailableError):
                provider.chat(self.make_request())

    def test_generic_error_maps_to_generation_error(self):
        from agenthub.core.llm.errors import LLMGenerationError

        provider = LiteLLMCloudProvider("openai", ["gpt-5"])
        recorder: dict = {}
        module = make_fake_litellm(recorder, error_type="generic")
        with patch.dict(sys.modules, {"litellm": module}):
            with pytest.raises(LLMGenerationError):
                provider.chat(self.make_request())

    def test_missing_litellm_raises_unavailable(self):
        provider = LiteLLMCloudProvider("openai", ["gpt-5"])
        with patch.dict(sys.modules, {"litellm": None}):
            with pytest.raises(LLMUnavailableError, match="not installed"):
                provider.chat(self.make_request())
