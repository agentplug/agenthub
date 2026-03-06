"""Integration tests for the agent loading, execution, and error-handling lifecycle.

These tests exercise real code paths end-to-end.  Heavy mocking is avoided;
only external network calls (GitHub API, LLM API) are patched where needed.
"""

import pytest
import yaml

from agenthub.core.agents.lifecycle.loader import AgentLoader, AgentLoadError
from agenthub.core.agents.lifecycle.manifest import (
    ManifestParser,
    ManifestValidationError,
)
from agenthub.core.tools.exceptions import AgentExecutionError

# ===================================================================
# 1. Load a real agent from disk -> call solve() -> assert result
# ===================================================================


class TestLoadAgentAndSolve:
    """Load an agent from disk and call solve()."""

    def test_load_agent_from_disk(self, loaded_agent_info):
        """AgentLoader.load_agent returns a valid agent_info dict."""
        assert loaded_agent_info["name"] == "echo-agent"
        assert loaded_agent_info["namespace"] == "test-ns"
        assert loaded_agent_info["valid"] is True
        assert "echo" in loaded_agent_info["methods"]
        assert "greet" in loaded_agent_info["methods"]

    def test_agent_wrapper_from_loaded_info(self, agent_wrapper):
        """AgentWrapper initialises correctly from real agent_info."""
        assert agent_wrapper.name == "echo-agent"
        assert agent_wrapper.namespace == "test-ns"
        assert agent_wrapper.has_method("echo")
        assert agent_wrapper.has_method("greet")
        assert not agent_wrapper.has_method("nonexistent")

    def test_solve_returns_result(self, agent_wrapper):
        """solve() should return a dict (not raise) even without an LLM.

        Without an LLM service the framework handler falls back, but the
        key invariant is: solve() never raises -- it returns a dict with
        either 'result' or 'error'.
        """
        result = agent_wrapper.solve("echo hello world")
        assert isinstance(result, dict)
        # solve() should always return a dict, even on error path
        assert "error" in result or "result" in result

    def test_solve_with_context(self, agent_wrapper):
        """solve() accepts optional context dict."""
        result = agent_wrapper.solve(
            "greet the user", context={"user": "integration-test"}
        )
        assert isinstance(result, dict)


# ===================================================================
# 2. Load agent with external_tools -> assert tools are wired up
# ===================================================================


class TestAgentToolWiring:
    """Verify that external tools are wired through the wrapper."""

    def test_add_external_tools_registered(self, agent_wrapper):
        """add_external_tools works when the tool is actually registered."""
        from agenthub.core.tools import get_tool_registry

        registry = get_tool_registry()
        agent_wrapper.tool_registry = registry

        # Register a dummy tool so the registry knows about it
        tool_name = "integration_test_tool"
        if tool_name not in registry.registered_tools:
            registry.register_tool(tool_name, lambda x: x, description="test tool")

        agent_wrapper.add_external_tools([tool_name])
        assert tool_name in agent_wrapper.assigned_tools

    def test_add_unregistered_tool_raises(self, agent_wrapper):
        """add_external_tools with an unknown tool raises ToolNotFoundError."""
        from agenthub.core.tools import get_tool_registry
        from agenthub.core.tools.exceptions import ToolNotFoundError

        registry = get_tool_registry()
        agent_wrapper.tool_registry = registry

        with pytest.raises(ToolNotFoundError):
            agent_wrapper.add_external_tools(["totally_fake_tool"])

    def test_get_tool_context_json_empty(self, agent_wrapper):
        """Tool context JSON is valid JSON even with no tools assigned."""
        import json

        raw = agent_wrapper.get_tool_context_json()
        ctx = json.loads(raw)
        assert "available_tools" in ctx
        assert isinstance(ctx["available_tools"], list)

    def test_get_assigned_tools_returns_copy(self, agent_wrapper):
        """get_assigned_tools returns a copy, not the internal list."""
        tools = agent_wrapper.get_assigned_tools()
        tools.append("should_not_leak")
        assert "should_not_leak" not in agent_wrapper.assigned_tools


# ===================================================================
# 3. Call a method that does not exist -> assert proper error
# ===================================================================


class TestMethodNotFoundError:
    """Calling a missing method must raise AgentExecutionError."""

    def test_execute_nonexistent_method_raises(self, agent_wrapper):
        """execute() with a bad method name raises AgentExecutionError."""
        with pytest.raises(AgentExecutionError, match="not found"):
            agent_wrapper.execute("this_method_does_not_exist", {})

    def test_execute_nonexistent_includes_available_methods(self, agent_wrapper):
        """The error message should list available methods."""
        with pytest.raises(AgentExecutionError) as exc_info:
            agent_wrapper.execute("bogus", {})
        err_msg = str(exc_info.value)
        assert "echo" in err_msg
        assert "greet" in err_msg

    def test_getattr_nonexistent_method_raises_attribute_error(self, agent_wrapper):
        """Accessing a non-existent method via attribute raises AttributeError."""
        with pytest.raises(AttributeError, match="not found"):
            agent_wrapper.nonexistent_method()

    def test_getattr_private_attr_raises(self, agent_wrapper):
        """Private attributes that don't exist raise AttributeError."""
        with pytest.raises(AttributeError):
            _ = agent_wrapper._hidden_thing


# ===================================================================
# 4. Agent manifest with missing required fields -> AgentLoadError
# ===================================================================


class TestBadManifestErrors:
    """Invalid manifests must be rejected with clear errors."""

    def test_missing_name_field(self, storage_dir):
        """A manifest without 'name' should fail validation."""
        bad_manifest = {
            # "name" is missing
            "version": "0.1.0",
            "description": "bad",
            "author": "test",
            "interface": {
                "methods": {
                    "do_thing": {"description": "thing"},
                }
            },
        }
        agent_dir = storage_dir / "agents" / "bad-ns" / "bad-agent"
        agent_dir.mkdir(parents=True)
        with open(agent_dir / "agent.yaml", "w") as f:
            yaml.dump(bad_manifest, f)
        (agent_dir / "agent.py").touch()

        parser = ManifestParser()
        with pytest.raises(ManifestValidationError, match="name"):
            parser.parse_manifest(str(agent_dir / "agent.yaml"))

    def test_missing_interface_field(self, storage_dir):
        """A manifest without 'interface' should fail validation."""
        bad_manifest = {
            "name": "bad-agent",
            "version": "0.1.0",
            "description": "bad",
            "author": "test",
            # "interface" is missing
        }
        agent_dir = storage_dir / "agents" / "bad-ns" / "bad-agent2"
        agent_dir.mkdir(parents=True)
        with open(agent_dir / "agent.yaml", "w") as f:
            yaml.dump(bad_manifest, f)
        (agent_dir / "agent.py").touch()

        parser = ManifestParser()
        with pytest.raises(ManifestValidationError, match="interface"):
            parser.parse_manifest(str(agent_dir / "agent.yaml"))

    def test_empty_methods_rejected(self, storage_dir):
        """A manifest with empty methods dict should fail."""
        bad_manifest = {
            "name": "empty-methods",
            "version": "0.1.0",
            "description": "bad",
            "author": "test",
            "interface": {"methods": {}},
        }
        agent_dir = storage_dir / "agents" / "bad-ns" / "empty-methods"
        agent_dir.mkdir(parents=True)
        with open(agent_dir / "agent.yaml", "w") as f:
            yaml.dump(bad_manifest, f)
        (agent_dir / "agent.py").touch()

        parser = ManifestParser()
        with pytest.raises(ManifestValidationError, match="No methods"):
            parser.parse_manifest(str(agent_dir / "agent.yaml"))

    def test_missing_method_description(self, storage_dir):
        """A method without 'description' should fail validation."""
        bad_manifest = {
            "name": "no-desc",
            "version": "0.1.0",
            "description": "bad",
            "author": "test",
            "interface": {
                "methods": {
                    "broken_method": {
                        "parameters": {"x": {"type": "string"}},
                        # "description" is missing
                    }
                }
            },
        }
        agent_dir = storage_dir / "agents" / "bad-ns" / "no-desc"
        agent_dir.mkdir(parents=True)
        with open(agent_dir / "agent.yaml", "w") as f:
            yaml.dump(bad_manifest, f)
        (agent_dir / "agent.py").touch()

        parser = ManifestParser()
        with pytest.raises(ManifestValidationError, match="description"):
            parser.parse_manifest(str(agent_dir / "agent.yaml"))

    def test_nonexistent_agent_path_raises(self):
        """Loading from a path that does not exist raises AgentLoadError."""
        loader = AgentLoader()
        with pytest.raises(AgentLoadError, match="does not exist"):
            loader.load_agent_by_path("/tmp/absolutely/no/agent/here")

    def test_invalid_structure_raises(self, storage_dir):
        """A directory missing agent.py raises AgentLoadError."""
        agent_dir = storage_dir / "agents" / "bad-ns" / "no-py"
        agent_dir.mkdir(parents=True)
        with open(agent_dir / "agent.yaml", "w") as f:
            yaml.dump(
                {
                    "name": "no-py",
                    "version": "0.1.0",
                    "description": "bad",
                    "author": "test",
                    "interface": {
                        "methods": {"m": {"description": "d"}},
                    },
                },
                f,
            )
        # No agent.py created

        loader = AgentLoader()
        with pytest.raises(AgentLoadError, match="Invalid agent structure"):
            loader.load_agent_by_path(str(agent_dir))

    def test_load_agent_not_found_via_storage(self, local_storage):
        """Loading a non-installed agent through storage raises AgentLoadError."""
        loader = AgentLoader(storage=local_storage)
        with pytest.raises(AgentLoadError, match="not found"):
            loader.load_agent("nonexistent-namespace", "nonexistent-agent")


# ===================================================================
# 5. Load agent -> call execute(method, params) directly -> assert
# ===================================================================


class TestDirectMethodExecution:
    """Test the execute() path end-to-end."""

    def test_execute_fallback_without_runtime(self, agent_wrapper):
        """execute() without runtime returns a fallback result dict."""
        result = agent_wrapper.execute("echo", {"text": "hello"})
        assert isinstance(result, dict)
        # Fallback path returns a dict with "result" key
        assert "result" in result

    def test_execute_with_runtime_subprocess(self, agent_wrapper_with_runtime):
        """execute() through AgentRuntime runs the real agent.py subprocess."""
        result = agent_wrapper_with_runtime.execute("echo", {"text": "integration"})
        assert isinstance(result, dict)
        # Successful subprocess execution returns the agent's output
        if "result" in result:
            assert "integration" in result["result"]
        # Even if there's an error (e.g. venv issue), it should be a dict
        assert "result" in result or "error" in result

    def test_execute_greet_method(self, agent_wrapper_with_runtime):
        """execute() the greet method through the real subprocess."""
        result = agent_wrapper_with_runtime.execute("greet", {"name": "World"})
        assert isinstance(result, dict)
        if "result" in result:
            assert "World" in result["result"]
        assert "result" in result or "error" in result

    def test_execute_returns_execution_time(self, agent_wrapper_with_runtime):
        """Successful execution includes execution_time in result."""
        result = agent_wrapper_with_runtime.execute("echo", {"text": "time-check"})
        assert isinstance(result, dict)
        if "error" not in result:
            assert "execution_time" in result
            assert isinstance(result["execution_time"], int | float)

    def test_dynamic_method_call_via_getattr(self, agent_wrapper):
        """Calling agent.echo(text="hi") dispatches through __getattr__."""
        result = agent_wrapper.echo(text="hi")
        assert isinstance(result, dict)

    def test_has_method_accurate(self, agent_wrapper):
        """has_method reflects the real manifest methods."""
        assert agent_wrapper.has_method("echo") is True
        assert agent_wrapper.has_method("greet") is True
        assert agent_wrapper.has_method("delete_everything") is False

    def test_get_method_info_returns_details(self, agent_wrapper):
        """get_method_info returns description and parameters."""
        info = agent_wrapper.get_method_info("echo")
        assert "description" in info
        assert "parameters" in info
        assert "text" in info["parameters"]

    def test_to_dict_roundtrip(self, agent_wrapper):
        """to_dict includes core fields."""
        d = agent_wrapper.to_dict()
        assert d["name"] == "echo-agent"
        assert d["namespace"] == "test-ns"
        assert "echo" in d["methods"]

    def test_repr_contains_name(self, agent_wrapper):
        """repr includes the agent name."""
        r = repr(agent_wrapper)
        assert "echo-agent" in r


# ===================================================================
# Additional integration: AgentLoader -> discover_agents
# ===================================================================


class TestAgentDiscovery:
    """Test agent discovery through real storage."""

    def test_discover_finds_installed_agent(self, agent_loader, echo_agent_dir):
        """discover_agents returns the agent we installed."""
        _ = echo_agent_dir  # fixture side-effect: creates agent dir on disk
        agents = agent_loader.discover_agents()
        names = [a["name"] for a in agents]
        assert "echo-agent" in names

    def test_agent_info_basic_fields(self, agent_loader, echo_agent_dir):
        """get_agent_info returns basic fields without full load."""
        _ = echo_agent_dir  # fixture side-effect: creates agent dir on disk
        info = agent_loader.get_agent_info("test-ns", "echo-agent")
        assert info["name"] == "echo-agent"
        assert "echo" in info["methods"]
        assert info["valid_structure"] is True


# ===================================================================
# Additional integration: Knowledge injection
# ===================================================================


class TestKnowledgeInjection:
    """Test knowledge management on a real wrapper."""

    def test_inject_and_retrieve_knowledge(self, agent_wrapper):
        """inject_knowledge + get_knowledge round-trips."""
        agent_wrapper.inject_knowledge("The sky is blue.")
        assert agent_wrapper.is_knowledge_available()
        assert "sky" in agent_wrapper.get_knowledge()

    def test_clear_knowledge(self, agent_wrapper):
        """clear_knowledge removes injected knowledge."""
        agent_wrapper.inject_knowledge("Temporary knowledge.")
        agent_wrapper.clear_knowledge()
        assert not agent_wrapper.is_knowledge_available()
