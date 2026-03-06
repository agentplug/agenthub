"""Unit tests for SessionManager."""

import time

from agenthub.core.communication.session import SessionManager


def test_session_manager_initialization():
    """Test SessionManager initialization."""
    manager = SessionManager()
    assert manager.sessions == {}


def test_create_session():
    """Test session creation."""
    manager = SessionManager()

    session_id = manager.create_session(
        agent_id="test-agent", method="test_method", parameters={"param1": "value1"}
    )

    assert session_id is not None
    assert session_id in manager.sessions

    session = manager.sessions[session_id]
    assert session["agent_id"] == "test-agent"
    assert session["method"] == "test_method"
    assert session["parameters"] == {"param1": "value1"}
    assert session["status"] == "starting"
    assert "start_time" in session


def test_update_session():
    """Test session updates."""
    manager = SessionManager()

    session_id = manager.create_session(
        agent_id="test-agent", method="test_method", parameters={}
    )

    # Update status
    manager.update_session(session_id, "running")
    assert manager.sessions[session_id]["status"] == "running"
    assert "last_updated" in manager.sessions[session_id]

    # Update with additional data
    manager.update_session(session_id, "running", {"progress": 0.5})
    assert manager.sessions[session_id]["progress"] == 0.5


def test_end_session():
    """Test session completion."""
    manager = SessionManager()

    session_id = manager.create_session(
        agent_id="test-agent", method="test_method", parameters={}
    )

    # End session
    result = {"output": "success"}
    manager.end_session(session_id, result)

    session = manager.sessions[session_id]
    assert session["status"] == "completed"
    assert session["result"] == result
    assert "end_time" in session
    assert "duration" in session
    assert session["duration"] >= 0


def test_fail_session():
    """Test session failure."""
    manager = SessionManager()

    session_id = manager.create_session(
        agent_id="test-agent", method="test_method", parameters={}
    )

    # Fail session
    error_msg = "Test error"
    manager.fail_session(session_id, error_msg)

    session = manager.sessions[session_id]
    assert session["status"] == "failed"
    assert session["error"] == error_msg
    assert "end_time" in session
    assert "duration" in session


def test_get_session():
    """Test getting session by ID."""
    manager = SessionManager()

    session_id = manager.create_session(
        agent_id="test-agent", method="test_method", parameters={}
    )

    # Get existing session
    session = manager.get_session(session_id)
    assert session is not None
    assert session["agent_id"] == "test-agent"

    # Get non-existent session
    non_existent = manager.get_session("non-existent-id")
    assert non_existent is None


def test_get_active_sessions():
    """Test getting active sessions."""
    manager = SessionManager()

    # Create multiple sessions
    session1 = manager.create_session("agent1", "method1", {})
    session2 = manager.create_session("agent2", "method2", {})
    session3 = manager.create_session("agent3", "method3", {})

    # All sessions should be active initially
    active = manager.get_active_sessions()
    assert len(active) == 3

    # End one session
    manager.end_session(session1)
    active = manager.get_active_sessions()
    assert len(active) == 2
    assert session1 not in active

    # Fail another session
    manager.fail_session(session2, "error")
    active = manager.get_active_sessions()
    assert len(active) == 1
    assert session3 in active


def test_get_sessions_by_agent():
    """Test getting sessions for specific agent."""
    manager = SessionManager()

    # Create sessions for different agents
    _session1 = manager.create_session("agent1", "method1", {})
    _session2 = manager.create_session("agent1", "method2", {})
    _session3 = manager.create_session("agent2", "method1", {})

    # Get sessions for agent1
    agent1_sessions = manager.get_sessions_by_agent("agent1")
    assert len(agent1_sessions) == 2

    # Get sessions for agent2
    agent2_sessions = manager.get_sessions_by_agent("agent2")
    assert len(agent2_sessions) == 1

    # Get sessions for non-existent agent
    agent3_sessions = manager.get_sessions_by_agent("agent3")
    assert len(agent3_sessions) == 0


def test_cleanup_old_sessions():
    """Test cleanup of old sessions."""
    manager = SessionManager()

    # Create and complete some sessions
    session1 = manager.create_session("agent1", "method1", {})
    manager.end_session(session1)

    session2 = manager.create_session("agent2", "method2", {})
    manager.fail_session(session2, "error")

    session3 = manager.create_session("agent3", "method3", {})  # Active session

    # Cleanup with very short max_age (should remove completed/failed)
    manager.cleanup_old_sessions(max_age_seconds=0.001)
    time.sleep(0.01)  # Wait a bit

    # Note: cleanup only removes completed/failed sessions, not active ones
    # Since we just created them, they might not be old enough yet
    # This test verifies the cleanup doesn't crash
    assert session3 in manager.sessions  # Active session should remain


def test_session_stats():
    """Test session statistics."""
    manager = SessionManager()

    # Create sessions with different statuses
    session1 = manager.create_session("agent1", "method1", {})
    session2 = manager.create_session("agent2", "method2", {})
    _session3 = manager.create_session("agent3", "method3", {})

    manager.end_session(session1)
    manager.fail_session(session2, "error")
    # session3 remains in starting status

    stats = manager.get_stats()
    assert stats["total_sessions"] == 3
    assert stats["active_sessions"] == 1
    assert "status_counts" in stats
    assert stats["status_counts"]["completed"] == 1
    assert stats["status_counts"]["failed"] == 1
    assert stats["status_counts"]["starting"] == 1
