"""Unit tests for the LLM-layer foundations: types, config, base, structured."""

import json

import pytest

from agenthub.core.llm.base import (
    LLMProvider,
    inject_json_instruction,
    strip_reasoning_tags,
)
from agenthub.core.llm.config import (
    DEFAULT_PREFERRED_MODELS,
    DEFAULT_PROVIDER_PRIORITY,
    LLMConfig,
)
from agenthub.core.llm.errors import (
    LLMError,
    LLMGenerationError,
    LLMResponseFormatError,
    LLMUnavailableError,
    ModelNotFoundError,
    NoModelAvailableError,
)
from agenthub.core.llm.structured import extract_json_from_text
from agenthub.core.llm.types import (
    ChatRequest,
    ChatResponse,
    Message,
    ModelDescriptor,
    ProviderCapabilities,
    parse_parameter_count,
)
from agenthub.core.tools.exceptions import AgentHubError


def make_request(**overrides) -> ChatRequest:
    defaults: dict = {
        "model": "test-model",
        "messages": (Message(role="user", content="hello"),),
    }
    defaults.update(overrides)
    return ChatRequest(**defaults)


def make_response(content: str, **overrides) -> ChatResponse:
    defaults: dict = {"content": content, "model": "test-model", "provider": "test"}
    defaults.update(overrides)
    return ChatResponse(**defaults)


class TestErrors:
    def test_hierarchy(self):
        assert issubclass(LLMError, AgentHubError)
        assert issubclass(LLMUnavailableError, LLMError)
        assert issubclass(NoModelAvailableError, LLMUnavailableError)
        assert issubclass(ModelNotFoundError, LLMError)
        assert issubclass(LLMGenerationError, LLMError)
        assert issubclass(LLMResponseFormatError, LLMGenerationError)

    def test_no_model_available_carries_diagnostics(self):
        error = NoModelAvailableError(
            probe_results={"ollama": "unreachable", "cloud": "no API key"}
        )
        assert "ollama: unreachable" in str(error)
        assert "cloud: no API key" in str(error)
        assert error.probe_results["ollama"] == "unreachable"
        # AgentHubError suggestions surface in the message.
        assert "AGENTHUB_LLM_MODEL" in str(error)

    def test_response_format_error_keeps_raw(self):
        error = LLMResponseFormatError("bad json", raw_response="not json at all")
        assert error.raw_response == "not json at all"


class TestTypes:
    def test_qualified_id(self):
        descriptor = ModelDescriptor(id="qwen3:32b", provider="ollama", is_local=True)
        assert descriptor.qualified_id == "ollama:qwen3:32b"

    @pytest.mark.parametrize(
        ("model_id", "expected"),
        [
            ("qwen3:32b", 32.0),
            ("llama-3.1-8B-instruct", 8.0),
            ("/models/qwen3-8b-q4.gguf", 8.0),
            ("gpt-oss:120b", 120.0),
            ("phi-4-0.5b", 0.5),
            ("gemma:latest", None),
            ("nomic-embed-text", None),
        ],
    )
    def test_parse_parameter_count(self, model_id, expected):
        assert parse_parameter_count(model_id) == expected

    def test_request_is_immutable(self):
        request = make_request()
        with pytest.raises(AttributeError):
            request.model = "other"


class TestConfig:
    def test_defaults_from_empty_env(self):
        config = LLMConfig.from_env({})
        assert config.ollama.base_url == "http://localhost:11434"
        assert config.lmstudio.base_url == "http://localhost:1234/v1"
        assert config.llamacpp.base_url == "http://localhost:8080/v1"
        assert config.provider_priority == DEFAULT_PROVIDER_PRIORITY
        assert config.preferred_models == DEFAULT_PREFERRED_MODELS
        assert config.forced_model is None
        assert config.lmstudio_native_json is False

    def test_env_overrides(self):
        config = LLMConfig.from_env(
            {
                "OLLAMA_API_URL": "http://gpu-box:11434",
                "LLAMACPP_API_URL": "http://gpu-box:8080/v1",
                "LLAMACPP_API_KEY": "secret",
                "AGENTHUB_LLM_MODEL": "llamacpp:qwen3-8b",
                "AGENTHUB_LLM_PROVIDER_PRIORITY": "llamacpp, ollama ,cloud",
                "AGENTHUB_LLM_PREFERRED": "*qwen3*,*gpt-oss*",
                "LMSTUDIO_NATIVE_JSON": "1",
            }
        )
        assert config.ollama.base_url == "http://gpu-box:11434"
        assert config.llamacpp.base_url == "http://gpu-box:8080/v1"
        assert config.llamacpp.api_key == "secret"
        assert config.forced_model == "llamacpp:qwen3-8b"
        assert config.provider_priority == ("llamacpp", "ollama", "cloud")
        assert config.preferred_models == ("*qwen3*", "*gpt-oss*")
        assert config.lmstudio_native_json is True

    def test_blank_csv_falls_back_to_default(self):
        config = LLMConfig.from_env({"AGENTHUB_LLM_PROVIDER_PRIORITY": " , "})
        assert config.provider_priority == DEFAULT_PROVIDER_PRIORITY


class TestInjectJsonInstruction:
    def test_appends_to_last_user_message(self):
        request = make_request(
            messages=(
                Message(role="user", content="first"),
                Message(role="assistant", content="reply"),
                Message(role="user", content="second"),
            )
        )
        result = inject_json_instruction(request)
        assert result.messages[0].content == "first"
        assert "valid JSON only" in result.messages[2].content
        assert result.messages[2].content.startswith("second")

    def test_adds_user_message_when_none_exists(self):
        request = make_request(messages=(Message(role="system", content="sys"),))
        result = inject_json_instruction(request)
        assert result.messages[-1].role == "user"
        assert "valid JSON only" in result.messages[-1].content

    def test_original_request_unchanged(self):
        request = make_request()
        inject_json_instruction(request)
        assert "valid JSON only" not in request.messages[0].content


class TestStripReasoningTags:
    def test_strips_think_block(self):
        response = make_response('<think>step by step...</think>{"answer": 42}')
        result = strip_reasoning_tags(response)
        assert result.content == '{"answer": 42}'
        assert result.reasoning_content == "step by step..."

    def test_multiple_blocks(self):
        response = make_response("<think>a</think>text<think>b</think>more")
        result = strip_reasoning_tags(response)
        assert result.content == "textmore"
        assert result.reasoning_content == "a\nb"

    def test_no_tags_is_identity(self):
        response = make_response("plain answer")
        assert strip_reasoning_tags(response) is response

    def test_unclosed_tag_left_alone(self):
        response = make_response("<think>never closed")
        result = strip_reasoning_tags(response)
        assert result.content == "<think>never closed"


class TestProviderTemplate:
    class RecordingProvider(LLMProvider):
        """Captures the request that reaches the transport."""

        name = "recording"

        def __init__(self, native_json: bool):
            self._native_json = native_json
            self.seen_request: ChatRequest | None = None

        @property
        def capabilities(self) -> ProviderCapabilities:
            return ProviderCapabilities(
                native_json=self._native_json,
                model_listing=True,
                is_local=True,
            )

        def is_available(self) -> bool:
            return True

        def list_models(self):
            return []

        def _chat(self, request: ChatRequest) -> ChatResponse:
            self.seen_request = request
            return make_response(
                "<think>hmm</think>ok", model=request.model, provider=self.name
            )

    def test_json_mode_injected_without_native_support(self):
        provider = self.RecordingProvider(native_json=False)
        provider.chat(make_request(json_mode=True))
        assert "valid JSON only" in provider.seen_request.messages[-1].content

    def test_json_mode_not_injected_with_native_support(self):
        provider = self.RecordingProvider(native_json=True)
        provider.chat(make_request(json_mode=True))
        assert "valid JSON only" not in provider.seen_request.messages[-1].content

    def test_reasoning_stripped_from_transport_output(self):
        provider = self.RecordingProvider(native_json=True)
        response = provider.chat(make_request())
        assert response.content == "ok"
        assert response.reasoning_content == "hmm"

    def test_abstract_methods_enforced(self):
        with pytest.raises(TypeError):

            class Incomplete(LLMProvider):
                name = "incomplete"

            Incomplete()


class TestExtractJson:
    def test_whole_response_is_json(self):
        assert extract_json_from_text('{"a": 1}') == {"a": 1}

    def test_json_with_surrounding_prose(self):
        text = 'Sure! Here is the result:\n{"a": 1, "b": {"c": 2}}\nHope that helps.'
        assert extract_json_from_text(text) == {"a": 1, "b": {"c": 2}}

    def test_json_in_code_fence(self):
        text = '```json\n{"a": 1}\n```'
        assert extract_json_from_text(text) == {"a": 1}

    def test_first_valid_object_wins(self):
        text = '{broken {"a": 1}'
        assert extract_json_from_text(text) == {"a": 1}

    def test_no_json_raises(self):
        with pytest.raises(json.JSONDecodeError):
            extract_json_from_text("no json here")
