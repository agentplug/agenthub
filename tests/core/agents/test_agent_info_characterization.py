"""Characterization tests: pin AgentInfo's construction-from-dict contract.

Phase 2 replaces the vestigial @dataclass-over-manual-__init__ with a real
dataclass or plain class; these tests keep the observable behavior fixed
across that change.
"""

import pytest

from agenthub.core.agents.agent_info import AgentInfo

FULL_INFO = {
    "name": "bot",
    "namespace": "acme",
    "agent_name": "bot",
    "path": "/agents/acme/bot",
    "version": "1.2.3",
    "description": "does things",
    "methods": ["summarize"],
    "dependencies": ["requests"],
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


class TestConstruction:
    def test_empty_dict_yields_documented_defaults(self):
        info = AgentInfo({})
        assert info.name == "unknown"
        assert info.namespace == "unknown"
        assert info.agent_name == "unknown"
        assert info.path == ""
        assert info.version == "unknown"
        assert info.description == ""
        assert info.methods == []
        assert info.dependencies == []
        assert info.manifest == {}
        assert info.interface == {}

    def test_full_dict_populates_attributes(self):
        info = AgentInfo(FULL_INFO)
        assert info.name == "bot"
        assert info.namespace == "acme"
        assert info.agent_name == "bot"
        assert info.path == "/agents/acme/bot"
        assert info.version == "1.2.3"
        assert info.description == "does things"
        assert info.methods == ["summarize"]
        assert info.dependencies == ["requests"]
        assert info.manifest == FULL_INFO["manifest"]
        assert info.interface == FULL_INFO["manifest"]["interface"]["methods"]

    def test_interface_comes_from_manifest_not_interface_key(self):
        """Quirk: the ``interface`` attribute is built from
        ``manifest.interface.methods``; a top-level ``interface`` key in the
        info dict is ignored."""
        info = AgentInfo({"interface": {"methods": {"x": {}}}})
        assert info.interface == {}


class TestDerivedValues:
    def test_agent_id_is_namespace_slash_name(self):
        assert AgentInfo(FULL_INFO).agent_id == "acme/bot"

    def test_to_dict_shape(self):
        info = AgentInfo(FULL_INFO)
        assert info.to_dict() == {
            "name": "bot",
            "namespace": "acme",
            "agent_name": "bot",
            "path": "/agents/acme/bot",
            "version": "1.2.3",
            "description": "does things",
            "methods": ["summarize"],
            "dependencies": ["requests"],
            "manifest": FULL_INFO["manifest"],
            "interface": FULL_INFO["manifest"]["interface"]["methods"],
        }

    def test_repr(self):
        assert repr(AgentInfo(FULL_INFO)) == (
            "AgentInfo(name='bot', namespace='acme', " "version='1.2.3', methods=1)"
        )

    def test_is_valid(self):
        assert AgentInfo(FULL_INFO).is_valid() is True
        assert AgentInfo({}).is_valid() is False


class TestMethodInfo:
    def test_declared_method_returns_full_shape(self):
        info = AgentInfo(FULL_INFO)
        assert info.get_method_info("summarize") == {
            "description": "Summarize text",
            "parameters": {"text": {"type": "string", "required": True}},
            "required": False,
            "optional": True,
        }

    def test_undeclared_but_listed_method_returns_fallback_shape(self):
        """Quirk: the fallback shape omits the required/optional keys that
        the declared shape includes."""
        info = AgentInfo({"methods": ["ping"]})
        assert info.get_method_info("ping") == {
            "description": "Execute ping",
            "parameters": {},
        }

    def test_unknown_method_raises_value_error(self):
        info = AgentInfo(FULL_INFO)
        with pytest.raises(ValueError, match="Method 'nope' not found"):
            info.get_method_info("nope")

    def test_has_method_and_counts(self):
        info = AgentInfo(FULL_INFO)
        assert info.has_method("summarize") is True
        assert info.has_method("nope") is False
        assert info.get_method_count() == 1
        assert info.get_available_methods() == ["summarize"]
        assert info.get_available_methods() is not info.methods
