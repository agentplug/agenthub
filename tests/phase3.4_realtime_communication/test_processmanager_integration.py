"""Tests for ProcessManager integration with real-time communication."""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from agenthub.runtime.process_manager import ProcessManager


class TestProcessManagerIntegration:
    """Test ProcessManager integration with communication server."""

    def test_init_with_realtime_communication_enabled(self):
        """Test ProcessManager initialization with real-time communication enabled."""
        with patch(
            "agenthub.core.communication.get_communication_server"
        ) as mock_get_server:
            mock_server = Mock()
            mock_server.is_running = False
            mock_get_server.return_value = mock_server

            manager = ProcessManager(realtime_communication=True)

            assert manager.realtime_communication is True
            assert manager.communication_server is not None
            assert manager._server_started is False

    def test_init_with_realtime_communication_disabled(self):
        """Test ProcessManager initialization with real-time communication disabled."""
        manager = ProcessManager(realtime_communication=False)

        assert manager.realtime_communication is False
        assert manager.communication_server is None
        assert manager._server_started is False

    def test_init_with_websockets_unavailable(self):
        """Test ProcessManager initialization when websockets library is unavailable."""
        # Mock the import to raise ImportError
        original_import = __builtins__["__import__"]

        def mock_import(name, *args, **kwargs):
            if name == "websockets":
                raise ImportError("No module named 'websockets'")
            return original_import(name, *args, **kwargs)

        __builtins__["__import__"] = mock_import
        try:
            manager = ProcessManager(realtime_communication=True)

            assert manager.realtime_communication is False
            assert manager.communication_server is None
        finally:
            __builtins__["__import__"] = original_import

    def test_set_realtime_communication_enable(self):
        """Test enabling real-time communication dynamically."""
        manager = ProcessManager(realtime_communication=False)

        with patch(
            "agenthub.core.communication.get_communication_server"
        ) as mock_get_server:
            mock_server = Mock()
            mock_get_server.return_value = mock_server

            manager.set_realtime_communication(True)

            assert manager.realtime_communication is True
            assert manager.communication_server is not None

    def test_set_realtime_communication_disable(self):
        """Test disabling real-time communication dynamically."""
        with patch(
            "agenthub.core.communication.get_communication_server"
        ) as mock_get_server:
            mock_server = Mock()
            mock_server.is_running = True
            mock_get_server.return_value = mock_server

            manager = ProcessManager(realtime_communication=True)

            manager.set_realtime_communication(False)

            assert manager.realtime_communication is False
            assert manager.communication_server is None
            assert manager.communication_manager.enabled is False
            # The server was not started by this manager (no owned loop),
            # so disable must not attempt to stop it.
            mock_server.stop.assert_not_called()

    def test_get_communication_status_disabled(self):
        """Test getting communication status when disabled."""
        manager = ProcessManager(realtime_communication=False)

        status = manager.get_communication_status()

        assert status["enabled"] is False
        assert status["reason"] == "disabled"

    def test_get_communication_status_not_initialized(self):
        """Test getting communication status when not initialized."""
        manager = ProcessManager(realtime_communication=True)
        manager.communication_server = None

        status = manager.get_communication_status()

        assert status["enabled"] is False
        assert status["reason"] == "not_initialized"

    def test_get_communication_status_enabled(self):
        """Test getting communication status when enabled."""
        with patch(
            "agenthub.core.communication.get_communication_server"
        ) as mock_get_server:
            mock_server = Mock()
            mock_server.is_running = True
            mock_server.port = 38765
            mock_server.host = "localhost"
            mock_server.agent_sessions = {"agent1": {}, "agent2": {}}
            mock_get_server.return_value = mock_server

            manager = ProcessManager(realtime_communication=True)

            status = manager.get_communication_status()

            assert status["enabled"] is True
            assert status["server_running"] is True
            assert status["port"] == 38765
            assert status["host"] == "localhost"
            assert status["active_sessions"] == 2

    @pytest.mark.asyncio
    async def test_ensure_communication_server_success(self):
        """Test ensuring communication server is running successfully."""
        with patch(
            "agenthub.core.communication.get_communication_server"
        ) as mock_get_server:
            mock_server = Mock()
            mock_server.is_running = False
            mock_server.start = AsyncMock(return_value=True)
            mock_get_server.return_value = mock_server

            manager = ProcessManager(realtime_communication=True)

            result = await manager._ensure_communication_server()

            assert result is True
            mock_server.start.assert_called_once()

    @pytest.mark.asyncio
    async def test_ensure_communication_server_failure(self):
        """Test ensuring communication server fails to start."""
        with patch(
            "agenthub.core.communication.get_communication_server"
        ) as mock_get_server:
            mock_server = Mock()
            mock_server.is_running = False
            mock_server.start = AsyncMock(return_value=False)
            mock_get_server.return_value = mock_server

            manager = ProcessManager(realtime_communication=True)

            result = await manager._ensure_communication_server()

            assert result is False

    def test_execute_agent_with_communication_session(self):
        """Test agent execution with communication session management."""
        # Create a temporary agent directory
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_path = temp_dir
            agent_dir = Path(agent_path)

            # Create agent.yaml
            agent_yaml = agent_dir / "agent.yaml"
            agent_yaml.write_text("name: test-agent\nversion: 1.0.0")

            # Create agent.py
            agent_py = agent_dir / "agent.py"
            agent_py.write_text(
                """
import json
import sys

class Agent:
    def test_method(self, param1):
        return {"result": f"Hello {param1}", "status": "success"}

if __name__ == "__main__":
    data = json.loads(sys.argv[1])
    method = data["method"]
    parameters = data["parameters"]

    agent = Agent()
    if hasattr(agent, method):
        result = getattr(agent, method)(**parameters)
        print(json.dumps(result))
    else:
        print(json.dumps({"error": f"Unknown method: {method}"}))
"""
            )

            with patch(
                "agenthub.core.communication.get_communication_server"
            ) as mock_get_server:
                mock_server = Mock()
                mock_server.is_running = True
                mock_server.register_agent_session = Mock()
                mock_server.unregister_agent_session = Mock()
                mock_get_server.return_value = mock_server

                manager = ProcessManager(realtime_communication=True)

                # Mock environment manager to avoid venv requirements
                with patch.object(
                    manager.environment_manager,
                    "get_python_executable",
                    return_value="python",
                ):
                    result = manager.execute_agent(
                        agent_path=agent_path,
                        method="test_method",
                        parameters={"param1": "World"},
                    )

                # Verify session management
                mock_server.register_agent_session.assert_called_once()
                mock_server.unregister_agent_session.assert_called_once()

                # Verify result
                assert "result" in result
                assert result["result"]["result"] == "Hello World"

    def test_execute_agent_without_communication(self):
        """Test agent execution without communication server."""
        # Create a temporary agent directory
        with tempfile.TemporaryDirectory() as temp_dir:
            agent_path = temp_dir
            agent_dir = Path(agent_path)

            # Create agent.yaml
            agent_yaml = agent_dir / "agent.yaml"
            agent_yaml.write_text("name: test-agent\nversion: 1.0.0")

            # Create agent.py
            agent_py = agent_dir / "agent.py"
            agent_py.write_text(
                """
import json
import sys

class Agent:
    def test_method(self, param1):
        return {"result": f"Hello {param1}", "status": "success"}

if __name__ == "__main__":
    data = json.loads(sys.argv[1])
    method = data["method"]
    parameters = data["parameters"]

    agent = Agent()
    if hasattr(agent, method):
        result = getattr(agent, method)(**parameters)
        print(json.dumps(result))
    else:
        print(json.dumps({"error": f"Unknown method: {method}"}))
"""
            )

            manager = ProcessManager(realtime_communication=False)

            # Mock environment manager to avoid venv requirements
            with patch.object(
                manager.environment_manager,
                "get_python_executable",
                return_value="python",
            ):
                result = manager.execute_agent(
                    agent_path=agent_path,
                    method="test_method",
                    parameters={"param1": "World"},
                )

            # Verify result
            assert "result" in result
            assert result["result"]["result"] == "Hello World"

    def test_execute_agent_error_handling(self):
        """Test agent execution error handling with communication."""
        with patch(
            "agenthub.core.communication.get_communication_server"
        ) as mock_get_server:
            mock_server = Mock()
            mock_server.is_running = True
            mock_server.register_agent_session = Mock()
            mock_server.unregister_agent_session = Mock()
            mock_get_server.return_value = mock_server

            manager = ProcessManager(realtime_communication=True)

            # Test with invalid agent path
            with pytest.raises(ValueError, match="Agent directory does not exist"):
                manager.execute_agent(
                    agent_path="/nonexistent/path", method="test_method", parameters={}
                )

            # Verify session cleanup on error
            # Note: Session is not registered if agent path validation fails
            mock_server.register_agent_session.assert_not_called()
            mock_server.unregister_agent_session.assert_not_called()
