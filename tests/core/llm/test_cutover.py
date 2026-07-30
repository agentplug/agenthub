"""Tests for the legacy-shim cutover: CoreLLMService, shared instance,
migrated consumers, and the removal of fabricated fallback strings."""

import inspect
import threading

import pytest

from agenthub.core.agents.solve.framework_handler import FrameworkSolveHandler
from agenthub.core.llm import (
    CoreLLMService,
    LLMService,
    ModelDescriptor,
    ModelInfo,
    get_shared_llm_service,
    reset_shared_llm_service,
)
from agenthub.core.llm.errors import LLMUnavailableError
from agenthub.monitoring.llm_analyzer import LLMAnalyzer, LogAnalysis


class RaisingService:
    """LLM service stand-in whose generation always fails."""

    def generate(self, *args, **kwargs):
        raise LLMUnavailableError("no model")

    def generate_structured(self, *args, **kwargs):
        raise LLMUnavailableError("no model")

    def get_current_model(self):
        return "none"

    def is_available(self):
        return False


class AnsweringService:
    """LLM service stand-in returning canned output."""

    def __init__(self, text="", structured=None):
        self._text = text
        self._structured = structured or {}

    def generate(self, *args, **kwargs):
        return self._text

    def generate_structured(self, *args, **kwargs):
        return self._structured

    def get_current_model(self):
        return "fake:model"

    def is_available(self):
        return True


class TestCoreLLMServiceShim:
    def test_warns_and_is_llmservice(self):
        with pytest.warns(DeprecationWarning, match="CoreLLMService is deprecated"):
            service = CoreLLMService()
        assert isinstance(service, LLMService)

    def test_legacy_signature_unchanged(self):
        parameters = inspect.signature(CoreLLMService.__init__).parameters
        assert list(parameters) == ["self", "model", "auto_detect"]

    def test_generate_signature_compatible(self):
        parameters = list(inspect.signature(LLMService.generate).parameters)
        assert parameters[:5] == [
            "self",
            "input_data",
            "system_prompt",
            "return_json",
            "temperature",
        ]

    def test_model_info_alias(self):
        assert ModelInfo is ModelDescriptor


class TestSharedInstance:
    def setup_method(self):
        reset_shared_llm_service()

    def teardown_method(self):
        reset_shared_llm_service()

    def test_singleton_identity_and_reset(self):
        first = get_shared_llm_service()
        assert get_shared_llm_service() is first
        assert isinstance(first, LLMService)
        reset_shared_llm_service()
        assert get_shared_llm_service() is not first

    def test_thread_safety_smoke(self):
        instances = []

        def grab():
            instances.append(get_shared_llm_service())

        threads = [threading.Thread(target=grab) for _ in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        assert len(set(map(id, instances))) == 1


class TestFrameworkHandlerFallback:
    def make_handler(self, service):
        class WrapperStub:
            pass

        return FrameworkSolveHandler(WrapperStub(), llm_service=service)

    def test_llm_failure_falls_back_to_first_method(self):
        handler = self.make_handler(RaisingService())
        methods = [{"name": "run", "description": "", "parameters": {}}]
        result = handler._combined_method_selection_and_extraction(
            "do something", methods, {}
        )
        method_name, params, method_confidence, *_ = result
        assert method_name == "run"
        assert params == {}
        assert method_confidence == 0.5

    def test_llm_failure_with_no_methods(self):
        handler = self.make_handler(RaisingService())
        result = handler._combined_method_selection_and_extraction("query", [], {})
        assert result[0] == ""
        assert result[2] == 0.0

    def test_successful_selection_parses(self):
        service = AnsweringService(
            text=(
                '{"selected_method": "run", "method_confidence": 0.9,'
                ' "method_reasoning": "fits", "extracted_parameters": {"x": 1},'
                ' "parameter_confidence": 0.8, "parameter_reasoning": "clear"}'
            )
        )
        handler = self.make_handler(service)
        methods = [{"name": "run", "description": "", "parameters": {}}]
        result = handler._combined_method_selection_and_extraction(
            "run with x=1", methods, {}
        )
        assert result[0] == "run"
        assert result[1] == {"x": 1}


class TestLLMAnalyzer:
    def test_fallback_on_llm_error(self):
        analyzer = LLMAnalyzer(RaisingService())
        analysis = analyzer.analyze(["processing data..."])
        assert isinstance(analysis, LogAnalysis)
        assert analysis.status == "working"  # pattern-matching fallback

    def test_structured_analysis(self):
        analyzer = LLMAnalyzer(
            AnsweringService(
                structured={
                    "summary": "I'm indexing files",
                    "progress": 40,
                    "status": "working",
                    "errors": [],
                    "suggestions": [],
                }
            )
        )
        analysis = analyzer.analyze(["indexing"])
        assert analysis.summary == "I'm indexing files"
        assert analysis.progress == 40

    def test_terminal_display_consumes_analyzer_fields(self):
        from agenthub.monitoring.terminal_display import TerminalDisplay

        display = TerminalDisplay()
        analysis = LogAnalysis(
            summary="done",
            progress=100,
            status="complete",
            errors=["e1"],
            suggestions=["s1"],
        )
        # Must not raise: previously accessed fields from a different
        # LogAnalysis dataclass that this object never carried.
        display.show_final_summary(
            analysis, total_logs=3, execution_time=1.0, return_code=0
        )
