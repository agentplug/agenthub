"""Session management for agent execution."""

import logging
import time
import uuid

# For type hints only
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages active agent execution sessions.

    Design Principles:
    - Track active execution sessions
    - Manage session lifecycle
    - Provide session queries
    - Automatic cleanup of completed sessions

    Integration Points:
    - CommunicationServer: Uses this for session tracking
    - ProcessManager: Creates sessions for agent execution
    """

    def __init__(self, server: Any = None) -> None:
        """
        Initialize session manager.

        Args:
            server: CommunicationServer instance
        """
        self.server = server
        self.sessions: dict[str, dict[str, Any]] = {}
        logger.info("SessionManager initialized")

    def create_session(
        self, agent_id: str, method: str, parameters: dict[str, Any]
    ) -> str:
        """
        Create new execution session.

        Args:
            agent_id: Agent identifier
            method: Method being executed
            parameters: Method parameters

        Returns:
            Session ID
        """
        session_id = str(uuid.uuid4())

        self.sessions[session_id] = {
            "session_id": session_id,
            "agent_id": agent_id,
            "method": method,
            "parameters": parameters,
            "start_time": time.time(),
            "status": "starting",
            "metadata": {},
        }

        logger.info(f"Created session {session_id} for agent {agent_id}.{method}")
        return session_id

    def update_session(
        self, session_id: str, status: str, data: dict[str, Any] | None = None
    ) -> None:
        """
        Update session status and data.

        Args:
            session_id: Session identifier
            status: New status (starting, running, completed, failed)
            data: Additional data to update
        """
        if session_id in self.sessions:
            self.sessions[session_id]["status"] = status
            self.sessions[session_id]["last_updated"] = time.time()

            if data:
                self.sessions[session_id].update(data)

            logger.debug(f"Updated session {session_id}: status={status}")
        else:
            logger.warning(f"Attempted to update non-existent session: {session_id}")

    def end_session(self, session_id: str, result: Any | None = None) -> None:
        """
        End session and mark as completed.

        Args:
            session_id: Session identifier
            result: Optional execution result
        """
        if session_id in self.sessions:
            self.sessions[session_id]["end_time"] = time.time()
            self.sessions[session_id]["status"] = "completed"

            if result is not None:
                self.sessions[session_id]["result"] = result

            # Calculate duration
            start_time = self.sessions[session_id].get("start_time")
            end_time = self.sessions[session_id]["end_time"]
            self.sessions[session_id]["duration"] = end_time - start_time

            logger.info(f"Ended session {session_id}")
        else:
            logger.warning(f"Attempted to end non-existent session: {session_id}")

    def fail_session(self, session_id: str, error: str) -> None:
        """
        Mark session as failed.

        Args:
            session_id: Session identifier
            error: Error message
        """
        if session_id in self.sessions:
            self.sessions[session_id]["end_time"] = time.time()
            self.sessions[session_id]["status"] = "failed"
            self.sessions[session_id]["error"] = error

            # Calculate duration
            start_time = self.sessions[session_id].get("start_time")
            end_time = self.sessions[session_id]["end_time"]
            self.sessions[session_id]["duration"] = end_time - start_time

            logger.error(f"Session {session_id} failed: {error}")
        else:
            logger.warning(f"Attempted to fail non-existent session: {session_id}")

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        """
        Get session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session data or None if not found
        """
        return self.sessions.get(session_id)

    def get_active_sessions(self) -> dict[str, dict[str, Any]]:
        """
        Get all active sessions.

        Returns:
            Dictionary of active sessions (not completed/failed)
        """
        return {
            sid: session
            for sid, session in self.sessions.items()
            if session.get("status") not in ["completed", "failed"]
        }

    def get_sessions_by_agent(self, agent_id: str) -> list[dict[str, Any]]:
        """
        Get all sessions for a specific agent.

        Args:
            agent_id: Agent identifier

        Returns:
            List of session data
        """
        return [
            session
            for session in self.sessions.values()
            if session.get("agent_id") == agent_id
        ]

    def cleanup_old_sessions(self, max_age_seconds: float = 3600) -> None:
        """
        Cleanup old completed/failed sessions.

        Args:
            max_age_seconds: Maximum age for keeping sessions (default: 1 hour)
        """
        current_time = time.time()
        sessions_to_remove = []

        for session_id, session in self.sessions.items():
            # Only cleanup completed/failed sessions
            if session.get("status") in ["completed", "failed"]:
                end_time = session.get("end_time", session.get("start_time"))
                age = current_time - end_time

                if age > max_age_seconds:
                    sessions_to_remove.append(session_id)

        # Remove old sessions
        for session_id in sessions_to_remove:
            del self.sessions[session_id]
            logger.debug(f"Cleaned up old session: {session_id}")

        if sessions_to_remove:
            logger.info(f"Cleaned up {len(sessions_to_remove)} old sessions")

    def get_stats(self) -> dict[str, Any]:
        """
        Get session statistics.

        Returns:
            Statistics dictionary
        """
        total_sessions = len(self.sessions)
        active_sessions = len(self.get_active_sessions())

        status_counts: dict[str, int] = {}
        for session in self.sessions.values():
            status = session.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "total_sessions": total_sessions,
            "active_sessions": active_sessions,
            "status_counts": status_counts,
        }
