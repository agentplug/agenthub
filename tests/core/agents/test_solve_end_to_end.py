"""End-to-end pins for the invocation contract: a real AgentWrapper,
SolveEngine, and FrameworkSolveHandler with a stubbed LLM and a capturing
runtime — the full load → select → execute path, no mocks between the
components under test.
"""

from unittest.mock import Mock

import pytest

from agenthub.core.agents.wrapper import AgentWrapper
from agenthub.core.tools.exceptions import AgentSolveError

AGENT_INFO = {
    "name": "bot",
    "namespace": "acme",
    "agent_name": "bot",
    "path": "",
    "version": "1.0.0",
    "description": "test agent",
    "methods": ["summarize"],
    "dependencies": [],
    "manifest": {
        "interface": {
            "methods": {
                "summarize": {
                    "description": "Summarize text",
                    "parameters": {"text": {"type": "string", "required": True}},
                }
            }
        }
    },
}

SELECTION = (
    '{"selected_method": "summarize", "method_reasoning": "fits", '
    '"method_confidence": 0.9, "extracted_parameters": {"text": "hello"}, '
    '"parameter_reasoning": "found", "parameter_confidence": 0.8}'
)


def make_wrapper(llm_response):
    runtime = Mock()
    runtime.execute_agent.return_value = {"result": "summary!"}
    llm = Mock()
    llm.generate.return_value = llm_response

    wrapper = AgentWrapper(
        AGENT_INFO,
        runtime=runtime,
        knowledge_manager=Mock(),
        tool_manager=Mock(),
    )
    # Swap the real (unconfigured) LLM service for the stub
    wrapper.solve_engine.framework_handler.llm_service = llm
    return wrapper, runtime


class TestSolveSuccessPath:
    def test_full_chain_selects_and_executes(self, recwarn):
        wrapper, runtime = make_wrapper(SELECTION)

        result = wrapper.solve("summarize hello for me")

        assert result == {"result": "summary!"}
        call = runtime.execute_agent.call_args.kwargs
        assert call["namespace"] == "acme"
        assert call["agent_name"] == "bot"
        assert call["method"] == "summarize"
        assert call["parameters"] == {"text": "hello"}
        assert isinstance(call["tool_context"], dict)
        assert not [
            w for w in recwarn.list if issubclass(w.category, DeprecationWarning)
        ]


class TestSolveFailurePaths:
    def test_unparseable_llm_response_default_returns_legacy_dict(self):
        wrapper, _ = make_wrapper("definitely not json")
        with pytest.warns(DeprecationWarning, match="raise_errors=True"):
            result = wrapper.solve("summarize this")
        assert result["error"] == "Could not select appropriate method"
        assert isinstance(result["execution_time"], float)
        assert set(result) == {"error", "execution_time"}

    def test_unparseable_llm_response_opt_in_raises_typed(self):
        wrapper, _ = make_wrapper("definitely not json")
        with pytest.raises(AgentSolveError) as exc_info:
            wrapper.solve("summarize this", raise_errors=True)
        error = exc_info.value
        assert error.args[0] == "Could not select appropriate method"
        assert error.context["raw_response"] == "definitely not json"
        assert error.suggestions
