"""WebSocket server for real-time agent communication."""

import asyncio
import atexit
import json
import logging
import os
from collections.abc import Callable
from queue import Queue
from typing import Any, Optional

try:
    import websockets
    from websockets.asyncio.server import ServerConnection as WebSocketServerProtocol

    WEBSOCKETS_AVAILABLE = True
except ImportError:
    try:
        # Fallback for older websockets versions
        from websockets.server import WebSocketServerProtocol

        WEBSOCKETS_AVAILABLE = True
    except ImportError:
        WEBSOCKETS_AVAILABLE = False
        WebSocketServerProtocol = Any

logger = logging.getLogger(__name__)


class CommunicationServer:
    """
    Single shared WebSocket server for all agents.

    Design Principles:
    - Singleton pattern: Only one server instance per process
    - Auto-start: Starts automatically when first agent needs communication
    - Graceful fallback: Falls back to stdin/stdout if server cannot start
    - Minimal overhead: Lightweight implementation with minimal state

    Integration Points:
    - ProcessManager: Uses this server for agent communication
    - AgentRuntime: Manages server lifecycle
    - MessageRouter: Routes messages between clients
    """

    _instance: Optional["CommunicationServer"] = None
    _lock = asyncio.Lock()
    _initialized: bool = False

    def __new__(cls, *args: Any, **kwargs: Any) -> "CommunicationServer":
        """Singleton pattern: Ensure only one server instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, port: int = None, host: str = "localhost"):
        """
        Initialize communication server.

        Args:
            port: WebSocket server port (default: 38765 from env or config)
                  Port 38765 is in IANA unassigned range to avoid conflicts
            host: Server host (default: localhost for security)
        """
        # Prevent re-initialization of singleton
        if self._initialized:
            return

        # Check if websockets is available
        if not WEBSOCKETS_AVAILABLE:
            logger.warning(
                "websockets library not available, communication features disabled"
            )
            self.startup_failed = True
            self.failure_reason = "websockets library not installed"
            self._initialized = True
            return

        # Server configuration
        self.port = port or int(os.getenv("AGENTHUB_WEBSOCKET_PORT", "38765"))
        self.host = host

        # Connection tracking
        self.clients: set[WebSocketServerProtocol] = set()
        self.agent_sessions: dict[str, dict[str, Any]] = {}

        # Server state
        self.is_running = False
        self.server = None
        self.server_task: asyncio.Task | None = None

        # Message handlers
        self.message_handlers: dict[str, Callable] = {}

        # Message router (will be set after initialization)
        from typing import TYPE_CHECKING

        if TYPE_CHECKING:
            from .router import MessageRouter as MR
        self.message_router: MR | None = None  # type: ignore[name-defined]

        # Error tracking
        self.startup_failed = False
        self.failure_reason = None

        # Thread-safe message queue for log streaming from threads
        self.message_queue: Queue = Queue()
        self.queue_processor_task: asyncio.Task | None = None

        self._initialized = True

        # Register cleanup handler for automatic shutdown on process exit
        atexit.register(self._cleanup_on_exit)

        logger.info(f"CommunicationServer initialized on {self.host}:{self.port}")

    def is_port_in_use(self) -> bool:
        """
        Check if the WebSocket port is already in use by another process.

        Returns:
            bool: True if port is in use, False if available
        """
        import socket

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex((self.host, self.port))
                return result == 0
        except Exception:
            return False

    async def start(self) -> bool:
        """
        Start WebSocket server with graceful fallback.

        Returns:
            bool: True if server started successfully, False if fallback needed
        """
        if not WEBSOCKETS_AVAILABLE:
            return False

        async with self._lock:
            # Check if already running
            if self.is_running:
                logger.info("CommunicationServer already running")
                return True

            # Check if port is already in use by another process
            if self.is_port_in_use():
                logger.info(
                    f"Port {self.port} is already in use by another process. "
                    f"Using existing WebSocket server."
                )
                # Mark as running to reuse the existing server
                self.is_running = True
                self.startup_failed = False
                return True

            # Check if startup already failed
            if self.startup_failed:
                # Reset failure state and try again (port might be free now)
                logger.info(
                    "Retrying WebSocket server startup (previous failure: "
                    f"{self.failure_reason})"
                )
                self.startup_failed = False
                self.failure_reason = None

            try:
                # Initialize message router if not already done
                if self.message_router is None:
                    from .router import MessageRouter

                    self.message_router = MessageRouter(self)  # type: ignore[assignment]
                    self.message_router.start()

                # Start WebSocket server
                self.server = await websockets.serve(
                    self._handle_client,
                    self.host,
                    self.port,
                    ping_interval=20,  # Keep connections alive
                    ping_timeout=10,  # Detect dead connections
                )

                self.is_running = True
                self.startup_failed = False

                # Start queue processor for thread-safe message handling
                self.queue_processor_task = asyncio.create_task(
                    self._process_message_queue()
                )

                logger.info(
                    f"✅ CommunicationServer started on ws://{self.host}:{self.port}"
                )
                return True

            except OSError as e:
                # Port already in use or permission denied
                logger.warning(f"Failed to start WebSocket server: {e}")
                self.startup_failed = True
                self.failure_reason = str(e)
                return False

            except Exception as e:
                # Other startup errors
                logger.error(f"Unexpected error starting WebSocket server: {e}")
                self.startup_failed = True
                self.failure_reason = str(e)
                return False

    async def stop(self) -> None:
        """Stop WebSocket server gracefully."""
        if not WEBSOCKETS_AVAILABLE:
            return

        async with self._lock:
            if not self.is_running:
                logger.info("CommunicationServer not running")
                return

            try:
                # Stop message router
                if self.message_router:
                    await self.message_router.stop()

                # Stop queue processor
                if self.queue_processor_task:
                    self.queue_processor_task.cancel()
                    try:
                        await self.queue_processor_task
                    except asyncio.CancelledError:
                        pass
                    self.queue_processor_task = None

                # Close all client connections
                if self.clients:
                    await asyncio.gather(
                        *[client.close() for client in self.clients],
                        return_exceptions=True,
                    )
                    self.clients.clear()

                # Stop server
                if self.server:
                    self.server.close()
                    await self.server.wait_closed()
                    self.server = None

                self.is_running = False
                logger.info("✅ CommunicationServer stopped gracefully")

            except Exception as e:
                logger.error(f"Error stopping CommunicationServer: {e}")

    async def _process_message_queue(self) -> None:
        """Process messages from the thread-safe queue."""
        while self.is_running:
            try:
                # Wait for messages with a timeout to allow checking is_running
                try:
                    message_data = self.message_queue.get(timeout=0.1)
                except Exception:
                    # Timeout - continue loop to check is_running
                    continue

                # Process the message
                message_type = message_data.get("type")
                if message_type == "send_to_agent":
                    agent_id = message_data.get("agent_id")
                    message = message_data.get("message")
                    if agent_id and message:
                        await self.send_to_agent(agent_id, message)
                elif message_type == "broadcast":
                    message = message_data.get("message")
                    if message:
                        await self.broadcast(message)

                # Mark task as done
                self.message_queue.task_done()

            except Exception as e:
                logger.warning(f"Error processing queue message: {e}")

    async def _handle_client(
        self, websocket: WebSocketServerProtocol, path: str
    ) -> None:
        """
        Handle individual client connection.

        Args:
            websocket: WebSocket client connection
            path: Connection path (unused in Phase 3.4)
        """
        # Register client
        self.clients.add(websocket)
        client_id = id(websocket)
        logger.info(
            f"Client connected: {client_id} (total clients: {len(self.clients)})"
        )

        try:
            # Handle messages from this client
            async for message in websocket:
                await self._handle_message(websocket, message)

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Client disconnected: {client_id}")

        except Exception as e:
            logger.error(f"Error handling client {client_id}: {e}")

        finally:
            # Unregister client
            self.clients.discard(websocket)
            await self._cleanup_client_sessions(client_id)

    async def _handle_message(
        self, websocket: WebSocketServerProtocol, message: str
    ) -> None:
        """
        Handle incoming message from client.

        Args:
            websocket: Client connection
            message: Raw message string (expected JSON)
        """
        try:
            # Parse message
            data = json.loads(message)

            # Validate message structure
            if not self._validate_message(data):
                await self._send_error(websocket, "Invalid message format")
                return

            # Route message through message router
            if self.message_router:
                await self.message_router.route_message(websocket, data)
            else:
                logger.warning("Message router not initialized")

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message: {message}")
            await self._send_error(websocket, "Invalid JSON")

        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self._send_error(websocket, f"Message handling error: {str(e)}")

    def _validate_message(self, data: dict[str, Any]) -> bool:
        """
        Validate message structure.

        Required fields:
        - type: Message type (user_input, agent_message, etc.)
        - data: Message payload

        Optional fields:
        - agent_id: Target agent identifier
        - session_id: Session identifier
        - request_id: Request tracking identifier
        """
        if not isinstance(data, dict):
            return False

        if "type" not in data:
            logger.warning("Message missing 'type' field")
            return False

        if "data" not in data:
            logger.warning("Message missing 'data' field")
            return False

        return True

    async def _send_error(self, websocket: WebSocketServerProtocol, error: str) -> None:
        """Send error message to client."""
        try:
            error_msg = json.dumps({"type": "error", "data": {"error": error}})
            await websocket.send(error_msg)
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")

    async def broadcast(
        self,
        message: dict[str, Any],
        exclude: set[WebSocketServerProtocol] | None = None,
    ) -> None:
        """
        Broadcast message to all connected clients.

        Args:
            message: Message to broadcast (will be JSON serialized)
            exclude: Set of clients to exclude from broadcast
        """
        if not self.clients:
            logger.debug("No clients to broadcast to")
            return

        exclude = exclude or set()
        targets = self.clients - exclude

        if not targets:
            return

        # Serialize message once
        message_str = json.dumps(message)

        # Send to all targets
        await asyncio.gather(
            *[self._send_safe(client, message_str) for client in targets],
            return_exceptions=True,
        )

    async def send_to_agent(self, agent_id: str, message: dict[str, Any]) -> bool:
        """
        Send message to specific agent.

        Args:
            agent_id: Target agent identifier
            message: Message to send

        Returns:
            bool: True if message sent successfully
        """
        # Find agent session
        session = self.agent_sessions.get(agent_id)
        if not session:
            logger.warning(f"Agent session not found: {agent_id}")
            return False

        # Get agent's WebSocket connection
        client = session.get("client")
        if not client or client not in self.clients:
            logger.debug(f"Agent client not connected: {agent_id}")
            return False

        # Send message
        message_str = json.dumps(message)
        return await self._send_safe(client, message_str)

    async def _send_safe(
        self, websocket: WebSocketServerProtocol, message: str
    ) -> bool:
        """
        Send message to client with error handling.

        Args:
            websocket: Target client
            message: Message string

        Returns:
            bool: True if sent successfully
        """
        try:
            await websocket.send(message)
            return True
        except websockets.exceptions.ConnectionClosed:
            logger.debug(f"Client connection closed: {id(websocket)}")
            self.clients.discard(websocket)
            return False
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False

    def broadcast_message(self, message: dict[str, Any]) -> None:
        """
        Synchronous wrapper for broadcast method using thread-safe queue.

        Args:
            message: Message to broadcast
        """
        if not self.is_running:
            return

        try:
            # Add message to queue for processing by main event loop
            self.message_queue.put({"type": "broadcast", "message": message})
        except Exception as e:
            logger.warning(f"Failed to queue broadcast message: {e}")

    def send_to_agent_sync(self, agent_id: str, message: dict[str, Any]) -> bool:
        """
        Synchronous wrapper for send_to_agent method using thread-safe queue.

        Args:
            agent_id: Target agent identifier
            message: Message to send

        Returns:
            bool: True if message queued successfully
        """
        if not self.is_running:
            return False

        try:
            # Add message to queue for processing by main event loop
            self.message_queue.put(
                {"type": "send_to_agent", "agent_id": agent_id, "message": message}
            )
            return True
        except Exception as e:
            logger.warning(f"Failed to queue message for agent {agent_id}: {e}")
            return False

    def register_agent_session(
        self, agent_id: str, session_data: dict[str, Any]
    ) -> None:
        """
        Register agent execution session.

        Args:
            agent_id: Agent identifier
            session_data: Session metadata (client, execution_id, etc.)
        """
        self.agent_sessions[agent_id] = session_data
        logger.info(f"Registered agent session: {agent_id}")

    def unregister_agent_session(self, agent_id: str) -> None:
        """Unregister agent session."""
        if agent_id in self.agent_sessions:
            del self.agent_sessions[agent_id]
            logger.info(f"Unregistered agent session: {agent_id}")

    async def _cleanup_client_sessions(self, client_id: int) -> None:
        """Cleanup sessions associated with disconnected client."""
        # Find sessions associated with this client
        sessions_to_remove = []
        for agent_id, session in self.agent_sessions.items():
            if id(session.get("client")) == client_id:
                sessions_to_remove.append(agent_id)

        # Remove sessions
        for agent_id in sessions_to_remove:
            self.unregister_agent_session(agent_id)

    def register_message_handler(
        self, msg_type: str, handler: Callable[..., Any]
    ) -> None:
        """
        Register custom message handler.

        Args:
            msg_type: Message type to handle
            handler: Async function (websocket, data) -> None
        """
        self.message_handlers[msg_type] = handler
        logger.info(f"Registered message handler: {msg_type}")

    def get_stats(self) -> dict[str, Any]:
        """Get server statistics."""
        return {
            "is_running": self.is_running,
            "connected_clients": len(self.clients),
            "active_sessions": len(self.agent_sessions),
            "port": self.port,
            "host": self.host,
            "startup_failed": self.startup_failed,
            "failure_reason": self.failure_reason,
            "websockets_available": WEBSOCKETS_AVAILABLE,
        }

    def _cleanup_on_exit(self) -> None:
        """Cleanup handler called on process exit via atexit."""
        if not self.is_running:
            return

        logger.info("🧹 Auto-cleanup: Shutting down WebSocket server...")
        try:
            # Try to get event loop and stop server
            try:
                loop = asyncio.get_event_loop()
                if not loop.is_closed():
                    loop.run_until_complete(self.stop())
            except RuntimeError:
                # No event loop available, force cleanup
                self.is_running = False
                if self.server:
                    self.server.close()
                logger.info("✅ WebSocket server cleaned up (forced)")
        except Exception as e:
            logger.debug(f"Cleanup error (non-critical): {e}")

    def __del__(self) -> None:
        """Destructor to ensure server cleanup when object is garbage collected."""
        try:
            if hasattr(self, "is_running") and self.is_running:
                logger.debug("🧹 __del__: Cleaning up WebSocket server...")
                if hasattr(self, "server") and self.server:
                    self.server.close()
                self.is_running = False
        except Exception:
            pass  # Silently ignore errors in destructor


# Global server instance accessor
_server_instance: CommunicationServer | None = None


def get_communication_server() -> CommunicationServer:
    """
    Get singleton CommunicationServer instance.

    Returns:
        CommunicationServer: Global server instance
    """
    global _server_instance
    if _server_instance is None:
        _server_instance = CommunicationServer()
    return _server_instance
