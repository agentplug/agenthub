"""Characterization tests: pin FrameworkSolveHandler's observable contract.

Originally written against the legacy error-dict contract; updated when the
handler migrated to typed errors (Phase 1 of the hardening program). The
legacy dict shape survives at the AgentWrapper shim and is pinned in
tests/core/agents/test_solve_errors.py — this file pins the typed contract
and the unchanged success/fallback paths.
"""

import json
from unittest.mock import Mock

import pytest

from agenthub.core.agents.solve.framework_handler import FrameworkSolveHandler
from agenthub.core.llm.errors import LLMError
from agenthub.core.tools.exceptions import AgentSolveError


def make_wrapper(methods=None):
    wrapper = Mock()
    wrapper.get_all_available_tools.return_value = []
    wrapper.get_tool_context_json.return_value = "{}"
    wrapper.is_knowledge_available.return_value = False
    wrapper.agent_info.name = "bot"
    wrapper.agent_info.namespace = "acme"
    wrapper.agent_info.methods = methods or []
    wrapper.agent_info.get_method_info.side_effect = lambda m: {
        "description": f"Execute {m}",
        "parameters": {},
    }
    return wrapper


def make_handler(wrapper, llm_response=None, llm_error=None):
    llm = Mock()
    if llm_error is not None:
        llm.generate.side_effect = llm_error
    else:
        llm.generate.return_value = llm_response
    return FrameworkSolveHandler(wrapper, llm)


class TestTypedErrorContract:
    def test_no_methods_raises_with_suggestions_and_timing(self):
        handler = make_handler(make_wrapper(methods=[]))
        with pytest.raises(AgentSolveError) as exc_info:
            handler.solve("do something")
        error = exc_info.value
        assert error.args[0] == "No methods available for this agent"
        assert error.suggestions  # actionable guidance for typed-path users
        assert isinstance(error.context["execution_time"], float)

    def test_unparseable_llm_response_raises_with_raw_response(self):
        handler = make_handler(
            make_wrapper(methods=["summarize"]), llm_response="not json at all"
        )
        with pytest.raises(AgentSolveError) as exc_info:
            handler.solve("summarize this")
        error = exc_info.value
        assert error.args[0] == "Could not select appropriate method"
        assert isinstance(error.__cause__, json.JSONDecodeError)
        assert error.context["raw_response"] == "not json at all"
        assert isinstance(error.context["execution_time"], float)

    def test_unexpected_exception_raises_chained_with_plain_message(self):
        """The blanket wrap keeps args[0] identical to the legacy dict's
        error string so the wrapper shim reproduces it byte-for-byte."""
        wrapper = make_wrapper(methods=["summarize"])
        wrapper.get_all_available_tools.side_effect = RuntimeError("ctx boom")
        handler = make_handler(wrapper)
        with pytest.raises(AgentSolveError) as exc_info:
            handler.solve("q")
        assert exc_info.value.args[0] == "ctx boom"
        assert isinstance(exc_info.value.__cause__, RuntimeError)
        assert isinstance(exc_info.value.context["execution_time"], float)

    def test_execution_failure_wrapped_with_legacy_message(self):
        """An AgentExecutionError from the method call surfaces as
        AgentSolveError whose plain message matches the legacy dict."""
        from agenthub.core.tools.exceptions import AgentExecutionError

        wrapper = make_wrapper(methods=["summarize"])
        wrapper.execute.side_effect = AgentExecutionError(
            "Failed to execute method 'summarize': boom"
        )
        handler = make_handler(
            wrapper,
            llm_response=(
                '{"selected_method": "summarize", "extracted_parameters": {}, '
                '"method_reasoning": "r", "method_confidence": 0.9, '
                '"parameter_reasoning": "r", "parameter_confidence": 0.9}'
            ),
        )
        with pytest.raises(AgentSolveError) as exc_info:
            handler.solve("q")
        assert exc_info.value.args[0] == "Failed to execute method 'summarize': boom"


class TestLLMOutageFallback:
    def test_falls_back_to_first_method_with_empty_params(self):
        wrapper = make_wrapper(methods=["summarize", "translate"])
        wrapper.execute.return_value = {"summary": "..."}
        handler = make_handler(wrapper, llm_error=LLMError("no provider"))

        result = handler.solve("summarize this")

        wrapper.execute.assert_called_once_with("summarize", {})
        assert result == {"summary": "..."}


class TestSuccessPath:
    def test_valid_selection_executes_and_returns_result_as_is(self):
        wrapper = make_wrapper(methods=["summarize"])
        execute_result = {"summary": "short"}
        wrapper.execute.return_value = execute_result
        handler = make_handler(
            wrapper,
            llm_response=(
                '{"selected_method": "summarize", "method_reasoning": "fits", '
                '"method_confidence": 0.9, '
                '"extracted_parameters": {"text": "hello"}, '
                '"parameter_reasoning": "found", "parameter_confidence": 0.8}'
            ),
        )

        result = handler.solve("summarize hello")

        wrapper.execute.assert_called_once_with("summarize", {"text": "hello"})
        assert result is execute_result

    def test_prose_wrapped_json_parses_via_structured_extractor(self):
        """Robustness gain from core.llm.structured: responses that bury the
        JSON object in prose or code fences now parse instead of failing."""
        wrapper = make_wrapper(methods=["summarize"])
        wrapper.execute.return_value = {"summary": "short"}
        handler = make_handler(
            wrapper,
            llm_response=(
                'Sure! Here is the selection:\n```json\n{"selected_method": '
                '"summarize", "extracted_parameters": {"text": "hi"}, '
                '"method_reasoning": "r", "method_confidence": 0.9, '
                '"parameter_reasoning": "r", "parameter_confidence": 0.8}\n```'
            ),
        )

        result = handler.solve("summarize hi")

        wrapper.execute.assert_called_once_with("summarize", {"text": "hi"})
        assert result == {"summary": "short"}
