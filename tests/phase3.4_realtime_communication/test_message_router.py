"""Unit tests for MessageRouter."""

import asyncio

import pytest

from agenthub.core.communication.router import (
    MessageRouter,
    MessageType,
    PendingRequest,
)


@pytest.mark.asyncio
async def test_router_initialization():
    """Test MessageRouter initialization."""
    router = MessageRouter()

    assert router.pending_requests == {}
    assert router.agent_registry == {}
    assert len(router.message_handlers) > 0


@pytest.mark.asyncio
async def test_router_start_stop():
    """Test router start and stop."""
    router = MessageRouter()

    # Start router
    router.start()
    assert router.cleanup_task is not None

    # Stop router
    await router.stop()
    assert router.cleanup_task is None
    assert len(router.pending_requests) == 0


@pytest.mark.asyncio
async def test_router_agent_registry():
    """Test agent registration and discovery."""
    router = MessageRouter()

    # Register agent
    agent_metadata = {
        "agent_id": "test-agent",
        "name": "Test Agent",
        "capabilities": ["search", "analyze"],
    }
    router.register_agent("test-agent", agent_metadata)

    # Verify registration
    assert "test-agent" in router.agent_registry
    assert router.agent_registry["test-agent"]["name"] == "Test Agent"

    # Discover all agents
    agents = router.discover_agents()
    assert len(agents) == 1
    assert agents[0]["agent_id"] == "test-agent"

    # Discover by capability
    search_agents = router.discover_agents(capability="search")
    assert len(search_agents) == 1

    analyze_agents = router.discover_agents(capability="analyze")
    assert len(analyze_agents) == 1

    other_agents = router.discover_agents(capability="other")
    assert len(other_agents) == 0

    # Unregister agent
    router.unregister_agent("test-agent")
    assert "test-agent" not in router.agent_registry


@pytest.mark.asyncio
async def test_router_stats():
    """Test router statistics."""
    router = MessageRouter()

    stats = router.get_stats()
    assert "pending_requests" in stats
    assert "registered_agents" in stats
    assert "active_handlers" in stats
    assert stats["pending_requests"] == 0
    assert stats["registered_agents"] == 0


@pytest.mark.asyncio
async def test_message_type_enum():
    """Test MessageType enum values."""
    assert MessageType.USER_INPUT_REQUEST.value == "user_input_request"
    assert MessageType.USER_INPUT_RESPONSE.value == "user_input_response"
    assert MessageType.AGENT_MESSAGE.value == "agent_message"
    assert MessageType.AGENT_REQUEST.value == "agent_request"
    assert MessageType.AGENT_RESPONSE.value == "agent_response"
    assert MessageType.SYSTEM_STATUS.value == "system_status"
    assert MessageType.ERROR.value == "error"


@pytest.mark.asyncio
async def test_pending_request_dataclass():
    """Test PendingRequest dataclass."""
    import time

    future = asyncio.Future()
    request = PendingRequest(
        request_id="test-123",
        agent_id="test-agent",
        prompt="Test prompt",
        timestamp=time.time(),
        timeout=300.0,
        future=future,
    )

    assert request.request_id == "test-123"
    assert request.agent_id == "test-agent"
    assert request.prompt == "Test prompt"
    assert request.timeout == 300.0
    assert request.future is future
