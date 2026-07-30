"""Characterization tests: pin FrameworkSolveHandler's current observable contract.

These tests document behavior as it exists *today* (error-dict returns,
silent first-method fallback on LLM outage) so that the typed-error
migration can proceed without silently changing caller-visible results.
When the handler switches to raising typed errors, these tests are updated
to the new contract — they are the seam, not a endorsement of the status quo.
"""

from unittest.mock import Mock

from agenthub.core.agents.solve.framework_handler import FrameworkSolveHandler
from agenthub.core.llm.errors import LLMError


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


class TestErrorDictContract:
    def test_no_methods_returns_error_dict(self):
        handler = make_handler(make_wrapper(methods=[]))
        result = handler.solve("do something")
        assert result["error"] == "No methods available for this agent"
        assert isinstance(result["execution_time"], float)

    def test_unparseable_llm_response_returns_no_selection_dict(self):
        handler = make_handler(
            make_wrapper(methods=["summarize"]), llm_response="not json at all"
        )
        result = handler.solve("summarize this")
        assert result["error"] == "Could not select appropriate method"
        assert isinstance(result["execution_time"], float)

    def test_unexpected_exception_returns_error_dict(self):
        wrapper = make_wrapper(methods=["summarize"])
        wrapper.get_all_available_tools.side_effect = RuntimeError("ctx boom")
        handler = make_handler(wrapper)
        result = handler.solve("q")
        assert result == {
            "error": "ctx boom",
            "execution_time": result["execution_time"],
        }
        assert isinstance(result["execution_time"], float)


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
