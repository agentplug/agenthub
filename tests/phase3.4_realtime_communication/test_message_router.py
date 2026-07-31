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
async def test_router_stats():
    """Test router statistics."""
    router = MessageRouter()

    stats = router.get_stats()
    assert "pending_requests" in stats
    assert "active_handlers" in stats
    assert stats["pending_requests"] == 0


@pytest.mark.asyncio
async def test_message_type_enum():
    """Test MessageType enum values."""
    assert MessageType.USER_INPUT_REQUEST.value == "user_input_request"
    assert MessageType.USER_INPUT_RESPONSE.value == "user_input_response"
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
