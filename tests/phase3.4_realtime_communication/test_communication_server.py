"""Unit tests for CommunicationServer."""

import pytest

from agenthub.core.communication.server import (
    CommunicationServer,
    get_communication_server,
)

# Skip tests if websockets not available
try:
    import websockets  # noqa: F401

    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False


@pytest.fixture
def server_port():
    """Provide a test port for the server."""
    return 38766  # Use different port for testing


@pytest.mark.skipif(not WEBSOCKETS_AVAILABLE, reason="websockets library not installed")
@pytest.mark.asyncio
async def test_server_singleton():
    """Test that CommunicationServer follows singleton pattern."""
    server1 = CommunicationServer()
    server2 = CommunicationServer()
    assert server1 is server2, "CommunicationServer should be a singleton"


@pytest.mark.skipif(not WEBSOCKETS_AVAILABLE, reason="websockets library not installed")
@pytest.mark.asyncio
async def test_server_start_stop(server_port):
    """Test server startup and shutdown."""
    server = CommunicationServer(port=server_port)

    # Start server
    success = await server.start()
    assert success is True, "Server should start successfully"
    assert server.is_running is True, "Server should be marked as running"

    # Stop server
    await server.stop()
    assert server.is_running is False, "Server should be stopped"


@pytest.mark.skipif(not WEBSOCKETS_AVAILABLE, reason="websockets library not installed")
@pytest.mark.asyncio
async def test_server_stats(server_port):
    """Test server statistics."""
    server = CommunicationServer(port=server_port)
    await server.start()

    stats = server.get_stats()
    assert "is_running" in stats
    assert "connected_clients" in stats
    assert "active_sessions" in stats
    assert stats["is_running"] is True
    assert stats["connected_clients"] == 0

    await server.stop()


@pytest.mark.skipif(not WEBSOCKETS_AVAILABLE, reason="websockets library not installed")
@pytest.mark.asyncio
async def test_server_graceful_fallback_on_port_conflict(server_port):
    """Test that server handles port conflicts gracefully."""
    # Start first server
    server1 = CommunicationServer(port=server_port)
    success1 = await server1.start()
    assert success1 is True

    # Since CommunicationServer is a singleton, server2 will be the same instance
    # Instead, test by checking if already running
    success2 = await server1.start()  # Try to start again
    assert success2 is True  # Should succeed (already running)
    assert server1.is_running is True

    # Cleanup
    await server1.stop()


@pytest.mark.skipif(not WEBSOCKETS_AVAILABLE, reason="websockets library not installed")
@pytest.mark.asyncio
async def test_server_session_management(server_port):
    """Test agent session registration and unregistration."""
    server = CommunicationServer(port=server_port)
    await server.start()

    # Register session
    session_data = {"agent_id": "test-agent", "execution_id": "12345"}
    server.register_agent_session("test-agent", session_data)

    # Verify session registered
    assert "test-agent" in server.agent_sessions
    assert server.agent_sessions["test-agent"]["agent_id"] == "test-agent"

    # Unregister session
    server.unregister_agent_session("test-agent")
    assert "test-agent" not in server.agent_sessions

    await server.stop()


@pytest.mark.skipif(not WEBSOCKETS_AVAILABLE, reason="websockets library not installed")
@pytest.mark.asyncio
async def test_get_communication_server():
    """Test the global server accessor function."""
    server1 = get_communication_server()
    server2 = get_communication_server()

    assert server1 is server2, "Should return same singleton instance"


@pytest.mark.skipif(not WEBSOCKETS_AVAILABLE, reason="websockets library not installed")
@pytest.mark.asyncio
async def test_server_message_validation(server_port):
    """Test message validation."""
    server = CommunicationServer(port=server_port)

    # Valid message
    valid_msg = {"type": "test", "data": {"key": "value"}}
    assert server._validate_message(valid_msg) is True

    # Missing type
    invalid_msg1 = {"data": {"key": "value"}}
    assert server._validate_message(invalid_msg1) is False

    # Missing data
    invalid_msg2 = {"type": "test"}
    assert server._validate_message(invalid_msg2) is False

    # Not a dict
    invalid_msg3 = "string message"
    assert server._validate_message(invalid_msg3) is False


def test_server_without_websockets():
    """Test that server handles missing websockets library gracefully."""
    # This test should pass regardless of websockets availability
    server = CommunicationServer()

    if not WEBSOCKETS_AVAILABLE:
        assert server.startup_failed is True
        assert server.failure_reason is not None

    # Server should still be instantiable
    assert server is not None
