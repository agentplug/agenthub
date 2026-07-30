"""Characterization tests: pin AgentWrapper's public surface.

Phase 2 slims this facade (property delegations, tool-context dict instead
of a JSON round-trip, __getattr__ cleanup). These tests keep the observable
contract fixed across that refactor.
"""

import json
from unittest.mock import Mock

import pytest

from agenthub.core.agents.wrapper import AgentWrapper

AGENT_INFO = {
    "name": "bot",
    "namespace": "acme",
    "agent_name": "bot",
    "path": "/agents/acme/bot",
    "version": "1.0.0",
    "description": "test agent",
    "methods": ["summarize"],
    "dependencies": ["requests"],
    "manifest": {
        "interface": {
            "methods": {
                "summarize": {
                    "description": "Summarize text",
                    "parameters": {"text": {"type": "string"}},
                }
            }
        }
    },
}


def make_wrapper(**overrides):
    kwargs = {
        "agent_info": AGENT_INFO,
        "tool_registry": None,
        "knowledge_manager": Mock(),
        "tool_manager": Mock(),
    }
    kwargs.update(overrides)
    return AgentWrapper(**kwargs)


class TestPropertySurface:
    def test_agent_info_fields_mirrored_on_wrapper(self):
        wrapper = make_wrapper()
        assert wrapper.name == "bot"
        assert wrapper.namespace == "acme"
        assert wrapper.agent_name == "bot"
        assert wrapper.path == "/agents/acme/bot"
        assert wrapper.version == "1.0.0"
        assert wrapper.description == "test agent"
        assert wrapper.methods == ["summarize"]
        assert wrapper.dependencies == ["requests"]
        assert wrapper.manifest == AGENT_INFO["manifest"]
        assert wrapper.interface == AGENT_INFO["manifest"]["interface"]["methods"]

    def test_agent_id_defaults_to_namespace_slash_name(self):
        assert make_wrapper().agent_id == "acme/bot"

    def test_agent_id_override_wins(self):
        assert make_wrapper(agent_id="custom-id").agent_id == "custom-id"

    def test_get_assigned_tools_returns_copy(self):
        wrapper = make_wrapper(assigned_tools=["t1"])
        tools = wrapper.get_assigned_tools()
        assert tools == ["t1"]
        assert tools is not wrapper.assigned_tools


class TestDelegation:
    def test_execute_delegates_to_method_executor(self):
        wrapper = make_wrapper()
        result = wrapper.execute("summarize", {"text": "hi"})
        assert result == {
            "result": "Method 'summarize' executed with parameters: {'text': 'hi'}"
        }

    def test_execute_defaults_parameters_to_empty_dict(self):
        wrapper = make_wrapper()
        result = wrapper.execute("summarize")
        assert result == {"result": "Method 'summarize' executed with parameters: {}"}

    def test_has_method_and_get_method_info_delegate(self):
        wrapper = make_wrapper()
        assert wrapper.has_method("summarize") is True
        assert wrapper.has_method("nope") is False
        assert wrapper.get_method_info("summarize")["description"] == "Summarize text"


class TestDynamicDispatch:
    def test_known_method_returns_callable_routing_to_executor(self):
        wrapper = make_wrapper()
        result = wrapper.summarize(text="hi")
        assert result == {
            "result": "Method 'summarize' executed with parameters: {'text': 'hi'}"
        }

    def test_unknown_method_raises_attribute_error_with_available_list(self):
        wrapper = make_wrapper()
        with pytest.raises(AttributeError) as exc_info:
            _ = wrapper.nope
        assert "Method 'nope' not found in agent 'bot'" in str(exc_info.value)
        assert "Available methods: summarize" in str(exc_info.value)

    def test_private_attribute_raises_plain_attribute_error(self):
        wrapper = make_wrapper()
        with pytest.raises(AttributeError):
            _ = wrapper._not_a_real_attr

    def test_positional_args_map_by_declared_order(self):
        """Dynamic positional calls map onto declared interface parameters
        in order (see MethodExecutor pins for the no-schema raw-args quirk)."""
        wrapper = make_wrapper()
        result = wrapper.summarize("hi")
        assert result == {
            "result": "Method 'summarize' executed with parameters: {'text': 'hi'}"
        }


class TestToolContextDocument:
    EMPTY_DOC = {
        "available_tools": [],
        "tool_descriptions": {},
        "tool_usage_examples": {},
        "tool_parameters": {},
        "tool_return_types": {},
        "tool_namespaces": {},
    }

    def test_no_tools_yields_empty_six_key_document(self):
        wrapper = make_wrapper()
        assert json.loads(wrapper.get_tool_context_json()) == self.EMPTY_DOC

    def test_assigned_tools_without_registry_yields_empty_document(self):
        wrapper = make_wrapper(assigned_tools=["t1"])
        assert json.loads(wrapper.get_tool_context_json()) == self.EMPTY_DOC

    def test_metadata_flows_into_document(self):
        registry = Mock()
        metadata = Mock()
        metadata.description = "Searches the web"
        metadata.examples = ["search for cats"]
        metadata.parameters = {"query": str}
        metadata.return_type = str
        metadata.namespace = "web"
        registry.get_tool_metadata.return_value = metadata

        wrapper = make_wrapper(tool_registry=registry, assigned_tools=["search"])
        doc = json.loads(wrapper.get_tool_context_json())

        assert doc["available_tools"] == ["search"]
        assert doc["tool_descriptions"] == {"search": "Searches the web"}
        assert doc["tool_usage_examples"] == {"search": "search for cats"}
        assert doc["tool_parameters"] == {"search": {"query": str(str)}}
        assert doc["tool_return_types"] == {"search": str(str)}
        assert doc["tool_namespaces"] == {"search": "web"}

    def test_missing_metadata_leaves_tool_out_of_detail_maps(self):
        registry = Mock()
        registry.get_tool_metadata.return_value = None
        wrapper = make_wrapper(tool_registry=registry, assigned_tools=["ghost"])
        doc = json.loads(wrapper.get_tool_context_json())
        assert doc["available_tools"] == ["ghost"]
        assert doc["tool_descriptions"] == {}

    def test_metadata_error_falls_back_to_placeholder_description(self):
        registry = Mock()
        registry.get_tool_metadata.side_effect = RuntimeError("registry down")
        wrapper = make_wrapper(tool_registry=registry, assigned_tools=["broken"])
        doc = json.loads(wrapper.get_tool_context_json())
        assert doc["tool_descriptions"] == {"broken": "Tool: broken"}
