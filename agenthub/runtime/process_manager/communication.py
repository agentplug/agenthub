"""
Communication management module for WebSocket server lifecycle.

This module manages the WebSocket communication server used for real-time
agent-to-client communication.
"""

import asyncio
import logging
import threading
from typing import Any

logger = logging.getLogger(__name__)


class CommunicationManager:
    """
    Manages WebSocket server lifecycle and agent sessions.

    Handles initialization, session registration, and graceful fallback
    to stdin/stdout when WebSocket is unavailable.
    """

    def __init__(self, enabled: bool = True):
        """
        Initialize communication manager.

        Args:
            enabled: Whether to enable WebSocket communication (default: True)
        """
        self.enabled = enabled
        self.server: Any = None
        self._initialized = False
        # Set when this manager starts the server on its own background
        # thread; needed to stop that loop and join the thread on shutdown.
        self._server_thread: threading.Thread | None = None
        self._server_loop: asyncio.AbstractEventLoop | None = None
        self._start_task: Any = None

        if self.enabled:
            self._try_initialize_server()
        else:
            logger.info("📝 Real-time communication disabled - using stdin/stdout")

    def _try_initialize_server(self) -> None:
        """Try to initialize communication server with graceful fallback."""
        try:
            # Check if WebSocket dependencies are available
            import websockets  # noqa: F401

            logger.debug("✅ WebSocket library available")

            # Import communication server
            from agenthub.core.communication import get_communication_server

            # Create server instance
            self.server = get_communication_server()
            self._initialized = True

            logger.info("✅ Communication server initialized (lazy start)")
            logger.info(f"   📡 WebSocket port: {self.server.port}")

        except ImportError as e:
            logger.warning(f"❌ WebSocket library not available: {e}")
            logger.info("📝 Falling back to stdin/stdout communication")
            self.enabled = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize communication server: {e}")
            logger.info("📝 Falling back to stdin/stdout communication")
            self.enabled = False

    async def ensure_server_running(self) -> bool:
        """
        Ensure communication server is running.

        Returns:
            bool: True if server available, False if fallback needed
        """
        if not self.enabled or not self.server:
            logger.debug("📝 Communication server not available - using fallback")
            return False

        # Check if server is already running
        if self.server.is_running:
            logger.debug(
                f"✅ WebSocket server already running on port {self.server.port}"
            )
            return True

        # Try to start server
        logger.info("🚀 Starting WebSocket communication server...")
        success = await self.server.start()
        if not success:
            logger.warning("❌ Communication server failed to start - using fallback")
            return False

        logger.info(f"✅ WebSocket server started on port {self.server.port}")
        return True

    def start_server_if_needed(self) -> bool:
        """
        Start server in background thread if not running.

        Returns:
            bool: True if server is running or started successfully
        """
        if not self.enabled or not self.server:
            return False

        if self.server.is_running:
            return True

        # Check if there's an event loop running
        try:
            try:
                caller_loop = asyncio.get_running_loop()
                # If we get here, there's a running loop
                logger.debug("📡 Event loop is running, scheduling server start")
                # Keep references: the task must not be garbage-collected,
                # and shutdown() needs to know which loop runs the server.
                self._start_task = caller_loop.create_task(self.ensure_server_running())
                self._server_loop = caller_loop
                return True
            except RuntimeError:
                # No running loop, start server in background thread
                logger.debug(
                    "📡 No running event loop, starting server in background thread"
                )
                return self._start_server_thread()
        except Exception as e:
            logger.warning(f"Failed to start communication server: {e}")
            return False

    def _start_server_thread(self) -> bool:
        """Start the server on a dedicated background thread and wait for it.

        Returns:
            bool: True if the server reported a successful start.
        """
        started = threading.Event()
        start_ok = False

        def run_server_in_thread() -> None:
            """Run WebSocket server in dedicated thread."""
            nonlocal start_ok
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            self._server_loop = loop
            try:
                start_ok = loop.run_until_complete(self.ensure_server_running())
            except Exception as e:
                logger.warning(f"Communication server failed to start: {e}")
            finally:
                # Signal only after start finished, so the caller never
                # observes a half-started server.
                started.set()
            if start_ok:
                # Serve until shutdown() stops the loop.
                loop.run_forever()
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()

        self._server_thread = threading.Thread(
            target=run_server_in_thread,
            name="agenthub-communication-server",
            daemon=True,
        )
        self._server_thread.start()
        if not started.wait(timeout=10):
            logger.warning("Communication server start timed out")
            return False
        return start_ok

    def shutdown(self, timeout: float = 5.0) -> None:
        """Stop the WebSocket server and the background thread running it.

        Safe to call multiple times and from any thread. If the server was
        started on a caller-owned event loop, stopping is scheduled there
        instead of blocking.
        """
        server = self.server
        loop = self._server_loop

        if server is None or loop is None:
            return

        try:
            current_loop = asyncio.get_running_loop()
        except RuntimeError:
            current_loop = None

        if not loop.is_closed() and server.is_running:
            try:
                if current_loop is loop:
                    # Called from the loop the server runs on: cannot block
                    # on it, schedule the stop instead.
                    self._start_task = loop.create_task(server.stop())
                else:
                    future = asyncio.run_coroutine_threadsafe(server.stop(), loop)
                    future.result(timeout=timeout)
            except Exception as e:
                logger.warning(f"Error stopping communication server: {e}")

        if self._server_thread is not None:
            if not loop.is_closed():
                loop.call_soon_threadsafe(loop.stop)
            self._server_thread.join(timeout=timeout)
            if self._server_thread.is_alive():
                logger.warning("Communication server thread did not stop in time")
            self._server_thread = None

        self._server_loop = None

    def register_session(self, agent_id: str, session_data: dict[str, Any]) -> bool:
        """
        Register agent session for communication.

        Args:
            agent_id: Agent identifier
            session_data: Session metadata

        Returns:
            bool: True if session registered successfully
        """
        # Validate agent_id early to avoid confusing empty IDs downstream
        if not agent_id or not str(agent_id).strip():
            logger.warning(
                "📝 Cannot register WebSocket session with empty agent_id; ignoring"
            )
            return False

        if not self.is_available():
            logger.debug(
                f"📝 Cannot register session {agent_id} - server not available"
            )
            return False

        try:
            logger.info(f"📡 Registering WebSocket session: {agent_id}")
            self.server.register_agent_session(agent_id, session_data)
            return True
        except Exception as e:
            logger.warning(f"Failed to register session {agent_id}: {e}")
            return False

    def unregister_session(self, agent_id: str) -> bool:
        """
        Clean up agent session.

        Args:
            agent_id: Agent identifier

        Returns:
            bool: True if session unregistered successfully
        """
        if not agent_id or not str(agent_id).strip():
            logger.warning(
                "📝 Cannot unregister WebSocket session with empty agent_id; ignoring"
            )
            return False

        if not self.is_available():
            return False

        try:
            logger.info(f"✅ Agent completed - unregistering session: {agent_id}")
            self.server.unregister_agent_session(agent_id)
            return True
        except Exception as e:
            logger.warning(f"Failed to unregister session {agent_id}: {e}")
            return False

    def send_message(self, agent_id: str, message: dict[str, Any]) -> bool:
        """
        Send message to specific agent session.

        Args:
            agent_id: Agent identifier
            message: Message to send

        Returns:
            bool: True if message sent successfully
        """
        if not self.is_available():
            return False

        try:
            if hasattr(self.server, "send_to_agent_sync"):
                return bool(self.server.send_to_agent_sync(agent_id, message))
            return False
        except Exception as e:
            logger.warning(f"Failed to send message to {agent_id}: {e}")
            return False

    def is_available(self) -> bool:
        """
        Check if WebSocket communication is available.

        Returns:
            bool: True if server is available and running
        """
        return self.enabled and self.server is not None and self.server.is_running

    def get_status(self) -> dict[str, Any]:
        """
        Get communication server status.

        Returns:
            dict: Status information
        """
        if not self.enabled:
            return {"enabled": False, "reason": "disabled"}

        if not self.server:
            return {"enabled": False, "reason": "not_initialized"}

        try:
            return {
                "enabled": True,
                "server_running": self.server.is_running,
                "port": self.server.port,
                "host": self.server.host,
                "active_sessions": len(self.server.agent_sessions),
            }
        except Exception as e:
            return {"enabled": False, "reason": f"error: {e}"}

    def log_status(self) -> None:
        """Log the current communication status for debugging."""
        status = self.get_status()

        if status["enabled"]:
            logger.info("📡 COMMUNICATION STATUS: WebSocket Real-time Communication")
            logger.info(f"   ✅ Server running: {status['server_running']}")
            logger.info(f"   🌐 Host: {status['host']}")
            logger.info(f"   🔌 Port: {status['port']}")
            logger.info(f"   👥 Active sessions: {status['active_sessions']}")
        else:
            logger.info("📝 COMMUNICATION STATUS: stdin/stdout Fallback")
            logger.info(f"   ❌ Reason: {status['reason']}")

    def enable(self) -> bool:
        """
        Enable real-time communication.

        Returns:
            bool: True if enabled successfully
        """
        if self.enabled:
            logger.info("✅ Real-time communication already enabled")
            return True

        logger.info("🔄 Enabling real-time communication...")
        self._try_initialize_server()

        if self.server is not None:
            self.enabled = True
            logger.info("✅ Real-time communication enabled")
            return True
        else:
            logger.warning("❌ Failed to enable real-time communication")
            return False

    def disable(self) -> None:
        """Disable real-time communication."""
        if not self.enabled:
            logger.info("📝 Real-time communication already disabled")
            return

        logger.info("🔄 Disabling real-time communication...")
        self.enabled = False

        # Stop server if this manager started it
        self.shutdown()

        logger.info("📝 Real-time communication disabled - using stdin/stdout fallback")
