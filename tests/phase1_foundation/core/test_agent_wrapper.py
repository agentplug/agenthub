"""Tests for AgentWrapper class."""

import pytest

from agenthub.core.agents.wrapper import AgentExecutionError, AgentWrapper


class TestAgentWrapper:
    """Test cases for AgentWrapper class."""

    def test_init(self):
        """Test AgentWrapper initialization."""
        agent_info = {
            "name": "test-agent",
            "namespace": "test",
            "agent_name": "test-agent",
            "path": "/path/to/agent",
            "methods": ["test_method"],
            "manifest": {
                "interface": {"methods": {"test_method": {"description": "Test"}}}
            },
        }

        wrapper = AgentWrapper(agent_info)

        assert wrapper.name == "test-agent"
        assert wrapper.namespace == "test"
        assert wrapper.agent_name == "test-agent"
        assert wrapper.path == "/path/to/agent"
        assert wrapper.methods == ["test_method"]

    def test_init_with_runtime(self):
        """Test AgentWrapper initialization with runtime."""
        agent_info = {
            "name": "test-agent",
            "namespace": "test",
            "agent_name": "test-agent",
            "path": "/path/to/agent",
            "methods": ["test_method"],
            "manifest": {
                "interface": {"methods": {"test_method": {"description": "Test"}}}
            },
        }

        mock_runtime = object()
        wrapper = AgentWrapper(agent_info, runtime=mock_runtime)

        assert wrapper.runtime is mock_runtime

    def test_has_method_true(self):
        """Test checking for existing method."""
        agent_info = {
            "name": "test-agent",
            "namespace": "test",
            "agent_name": "test-agent",
            "path": "/path/to/agent",
            "methods": ["test_method", "another_method"],
            "manifest": {
                "interface": {"methods": {"test_method": {"description": "Test"}}}
            },
        }

        wrapper = AgentWrapper(agent_info)

        assert wrapper.has_method("test_method") is True
        assert wrapper.has_method("another_method") is True

    def test_has_method_false(self):
        """Test checking for nonexistent method."""
        agent_info = {
            "name": "test-agent",
            "namespace": "test",
            "agent_name": "test-agent",
            "path": "/path/to/agent",
            "methods": ["test_method"],
            "manifest": {
                "interface": {"methods": {"test_method": {"description": "Test"}}}
            },
        }

        wrapper = AgentWrapper(agent_info)

        assert wrapper.has_method("nonexistent_method") is False

    def test_get_method_info(self):
        """Test getting method information."""
        agent_info = {
            "name": "test-agent",
            "namespace": "test",
            "agent_name": "test-agent",
            "path": "/path/to/agent",
            "methods": ["test_method"],
            "manifest": {
                "interface": {
                    "methods": {
                        "test_method": {
                            "description": "Test method description",
                            "parameters": {"input": {"type": "string"}},
                            "returns": {"type": "string"},
                        }
                    }
                }
            },
        }

        wrapper = AgentWrapper(agent_info)

        method_info = wrapper.get_method_info("test_method")

        assert method_info["description"] == "Test method description"
        assert "parameters" in method_info
        assert "returns" in method_info

    def test_get_method_info_nonexistent(self):
        """Test getting method info for nonexistent method."""
        agent_info = {
            "name": "test-agent",
            "namespace": "test",
            "agent_name": "test-agent",
            "path": "/path/to/agent",
            "methods": ["test_method"],
            "manifest": {
                "interface": {"methods": {"test_method": {"description": "Test"}}}
            },
        }

        wrapper = AgentWrapper(agent_info)

        with pytest.raises(
            AgentExecutionError, match="Method 'nonexistent' not available"
        ):
            wrapper.get_method_info("nonexistent")

    def test_execute_method_without_runtime(self):
        """Test executing method without runtime should raise error."""
        agent_info = {
            "name": "test-agent",
            "namespace": "test",
            "agent_name": "test-agent",
            "path": "/path/to/agent",
            "methods": ["test_method"],
            "manifest": {
                "interface": {"methods": {"test_method": {"description": "Test"}}}
            },
        }

        wrapper = AgentWrapper(agent_info)

        with pytest.raises(AgentExecutionError, match="No runtime provided"):
            wrapper.execute("test_method", {})

    def test_execute_method_nonexistent(self):
        """Test executing nonexistent method."""
        agent_info = {
            "name": "test-agent",
            "namespace": "test",
            "agent_name": "test-agent",
            "path": "/path/to/agent",
            "methods": ["test_method"],
            "manifest": {
                "interface": {"methods": {"test_method": {"description": "Test"}}}
            },
        }

        mock_runtime = object()
        wrapper = AgentWrapper(agent_info, runtime=mock_runtime)

        with pytest.raises(
            AgentExecutionError, match="Method 'nonexistent' not available"
        ):
            wrapper.execute("nonexistent", {})

    def test_execute_method_success(self):
        """Test successful method execution."""
        agent_info = {
            "name": "test-agent",
            "namespace": "test",
            "agent_name": "test-agent",
            "path": "/path/to/agent",
            "methods": ["test_method"],
            "manifest": {
                "interface": {"methods": {"test_method": {"description": "Test"}}}
            },
        }

        # Mock runtime that returns success
        class MockRuntime:
            def execute_agent(
                self, namespace, agent_name, method, parameters, tool_context=None
            ):
                return {"result": "test_output", "execution_time": 1.0}

        wrapper = AgentWrapper(agent_info, runtime=MockRuntime())

        result = wrapper.execute("test_method", {"input": "test"})

        assert result["result"] == "test_output"
        assert result["execution_time"] == 1.0

    def test_getattr_method_call(self):
        """Test calling method via __getattr__ magic method."""
        agent_info = {
            "name": "test-agent",
            "namespace": "test",
            "agent_name": "test-agent",
            "path": "/path/to/agent",
            "methods": ["test_method"],
            "manifest": {
                "interface": {"methods": {"test_method": {"description": "Test"}}}
            },
        }

        # Mock runtime that returns success
        class MockRuntime:
            def execute_agent(
                self, namespace, agent_name, method, parameters, tool_context=None
            ):
                return {"result": f"Called {method} with {parameters}"}

        wrapper = AgentWrapper(agent_info, runtime=MockRuntime())

        # Call method directly as if it were an attribute
        result = wrapper.test_method(input="test_value")

        assert "Called test_method" in result["result"]
        assert "test_value" in result["result"]

    def test_getattr_nonexistent_method(self):
        """Test calling nonexistent method via __getattr__."""
        agent_info = {
            "name": "test-agent",
            "namespace": "test",
            "agent_name": "test-agent",
            "path": "/path/to/agent",
            "methods": ["test_method"],
            "manifest": {
                "interface": {"methods": {"test_method": {"description": "Test"}}}
            },
        }

        wrapper = AgentWrapper(agent_info)

        with pytest.raises(
            AttributeError,
            match="Method 'nonexistent' not found in agent 'test-agent'!",
        ):
            wrapper.nonexistent()

    def test_repr(self):
        """Test string representation of AgentWrapper."""
        agent_info = {
            "name": "test-agent",
            "namespace": "test",
            "agent_name": "test-agent",
            "path": "/path/to/agent",
            "methods": ["test_method"],
            "manifest": {
                "interface": {"methods": {"test_method": {"description": "Test"}}}
            },
        }

        wrapper = AgentWrapper(agent_info)

        repr_str = repr(wrapper)
        assert "test/test-agent" in repr_str
        assert "test_method" in repr_str

    def test_to_dict(self):
        """Test converting AgentWrapper to dictionary."""
        agent_info = {
            "name": "test-agent",
            "namespace": "test",
            "agent_name": "test-agent",
            "path": "/path/to/agent",
            "version": "1.0.0",
            "description": "Test agent",
            "methods": ["test_method"],
            "manifest": {
                "interface": {"methods": {"test_method": {"description": "Test"}}}
            },
        }

        wrapper = AgentWrapper(agent_info)

        result = wrapper.to_dict()

        assert result["name"] == "test-agent"
        assert result["namespace"] == "test"
        assert result["version"] == "1.0.0"
        assert result["methods"] == ["test_method"]
