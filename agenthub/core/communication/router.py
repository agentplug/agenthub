"""Message routing for real-time agent communication."""

import asyncio
import logging
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Message types for routing."""

    REGISTER_SESSION = "register_session"
    USER_INPUT_REQUEST = "user_input_request"
    USER_INPUT_RESPONSE = "user_input_response"
    SYSTEM_STATUS = "system_status"
    ERROR = "error"


@dataclass
class PendingRequest:
    """Tracks pending input requests."""

    request_id: str
    agent_id: str
    prompt: str
    timestamp: float
    timeout: float
    future: asyncio.Future[str]


class MessageRouter:
    """
    Routes messages between users, agents, and services.

    Scope: user-facing real-time interaction (session registration, user
    input requests, status broadcast). The agent-to-agent message types
    and the capability registry were removed — AgentHub's composition
    story is MCP tools, not agent-to-agent messaging
    (docs/adr/0002-communication-transport.md).

    Design Principles:
    - Message type based routing
    - Request/response tracking
    - Timeout handling

    Integration Points:
    - CommunicationServer: Uses this router for message handling
    - ProcessManager: Sends/receives messages through this router
    """

    def __init__(self, server: Any = None) -> None:
        """
        Initialize message router.

        Args:
            server: CommunicationServer instance
        """
        self.server = server

        # Pending user input requests
        self.pending_requests: dict[str, PendingRequest] = {}

        # Message handlers
        self.message_handlers: dict[MessageType, Callable] = {
            MessageType.REGISTER_SESSION: self._handle_register_session,
            MessageType.USER_INPUT_REQUEST: self._handle_user_input_request,
            MessageType.USER_INPUT_RESPONSE: self._handle_user_input_response,
            MessageType.SYSTEM_STATUS: self._handle_system_status,
            MessageType.ERROR: self._handle_error,
        }

        # Cleanup task
        self.cleanup_task: asyncio.Task | None = None

        logger.info("MessageRouter initialized")

    def start(self) -> None:
        """Start background tasks."""
        if self.cleanup_task is None:
            self.cleanup_task = asyncio.create_task(self._cleanup_expired_requests())
            logger.info("MessageRouter started")

    async def stop(self) -> None:
        """Stop background tasks."""
        if self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except (asyncio.CancelledError, RuntimeError):
                # RuntimeError: Task was created in different event loop
                # CancelledError: Expected during task cancellation
                pass
            self.cleanup_task = None

        # Cancel all pending requests
        for request in self.pending_requests.values():
            if not request.future.done():
                request.future.set_exception(RuntimeError("Router stopped"))

        self.pending_requests.clear()
        logger.info("MessageRouter stopped")

    async def route_message(self, websocket: Any, message: dict[str, Any]) -> None:
        """
        Route message to appropriate handler.

        Args:
            websocket: Client WebSocket connection
            message: Message data
        """
        try:
            # Extract message type
            msg_type_str = message.get("type")

            # Convert to enum
            try:
                msg_type = MessageType(msg_type_str)
            except ValueError:
                logger.warning(f"Unknown message type: {msg_type_str}")
                await self._send_error(
                    websocket, f"Unknown message type: {msg_type_str}"
                )
                return

            # Get handler
            handler = self.message_handlers.get(msg_type)
            if not handler:
                logger.error(f"No handler for message type: {msg_type}")
                await self._send_error(websocket, f"No handler for {msg_type}")
                return

            # Execute handler
            await handler(websocket, message)

        except Exception as e:
            logger.error(f"Error routing message: {e}")
            await self._send_error(websocket, f"Routing error: {str(e)}")

    async def _handle_register_session(
        self, websocket: Any, message: dict[str, Any]
    ) -> None:
        """Handle session registration from client."""
        data = message.get("data", {})
        agent_id = data.get("agent_id")
        session_metadata = data.get("metadata", {})

        if not agent_id:
            await self._send_error(
                websocket, "Missing agent_id for session registration"
            )
            return

        # Check if this is a reconnection
        is_reconnection = self.server.reconnect_session(agent_id, websocket)

        if not is_reconnection:
            # Register new session with WebSocket client reference
            session_data = {
                "client": websocket,
                "state": "connected",
                "metadata": session_metadata,
                "registered_at": time.time(),
            }
            self.server.register_agent_session(agent_id, session_data)
            logger.info(f"Registered new WebSocket session for agent: {agent_id}")
        else:
            logger.info(f"Reconnected WebSocket session for agent: {agent_id}")

        # Send confirmation back to client
        import json

        confirmation = json.dumps(
            {
                "type": "session_registered",
                "data": {
                    "agent_id": agent_id,
                    "status": "success",
                    "reconnected": is_reconnection,
                },
            }
        )
        await websocket.send(confirmation)

    async def request_user_input(
        self, agent_id: str, prompt: str, timeout: float = 300.0
    ) -> str | None:
        """
        Request input from user with timeout.

        Args:
            agent_id: Agent requesting input
            prompt: Prompt to display to user
            timeout: Timeout in seconds (default: 5 minutes)

        Returns:
            User input string, or None if timeout/error
        """
        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Create future for response
        future: asyncio.Future[str] = asyncio.Future()

        # Track pending request
        request = PendingRequest(
            request_id=request_id,
            agent_id=agent_id,
            prompt=prompt,
            timestamp=time.time(),
            timeout=timeout,
            future=future,
        )
        self.pending_requests[request_id] = request

        # If no WebSocket clients are connected, fall back to console prompt
        try:
            has_clients = bool(getattr(self.server, "clients", None))
        except Exception:
            has_clients = False

        if not has_clients:
            # Console fallback: prompt user directly in the terminal without WebSocket

            logger.info(
                "No WebSocket clients connected; falling back to console prompt."
            )
            print("\n[INPUT REQUIRED]", prompt)
            try:
                # Avoid blocking the event loop by reading input in a thread
                user_input = await asyncio.to_thread(
                    lambda: input("Enter your answer: ").strip()
                )
            except EOFError:
                user_input = ""

            # Complete the future immediately with console input
            request.future.set_result(user_input)
            logger.info(
                f"Console input received for agent {agent_id}; delivering to caller."
            )
        else:
            # Send request to user via WebSocket broadcast
            message = {
                "type": MessageType.USER_INPUT_REQUEST.value,
                "data": {
                    "request_id": request_id,
                    "agent_id": agent_id,
                    "prompt": prompt,
                    "timestamp": request.timestamp,
                },
            }

            await self.server.broadcast(message)
            logger.info(
                f"Requested user input for agent {agent_id} via WebSocket broadcast"
            )

        try:
            # Wait for response with timeout
            response = await asyncio.wait_for(future, timeout=timeout)
            return response

        except TimeoutError:
            logger.warning(f"User input request timed out: {request_id}")
            return None

        except Exception as e:
            logger.error(f"Error waiting for user input: {e}")
            return None

        finally:
            # Cleanup request
            if request_id in self.pending_requests:
                del self.pending_requests[request_id]

    async def _handle_user_input_request(
        self, websocket: Any, message: dict[str, Any]
    ) -> None:
        """Handle user input request from agent."""
        data = message.get("data", {})
        agent_id = data.get("agent_id")
        prompt = data.get("prompt")

        if not agent_id or not prompt:
            await self._send_error(websocket, "Missing agent_id or prompt")
            return

        # This is typically called from ProcessManager, not from WebSocket clients
        logger.debug(f"User input request: {agent_id} - {prompt}")

    async def _handle_user_input_response(
        self, websocket: Any, message: dict[str, Any]
    ) -> None:
        """Handle user input response."""
        data = message.get("data", {})
        request_id = data.get("request_id")
        user_input = data.get("input")

        if not request_id:
            await self._send_error(websocket, "Missing request_id")
            return

        # Find pending request
        request = self.pending_requests.get(request_id)
        if not request:
            logger.warning(f"No pending request found: {request_id}")
            await self._send_error(websocket, f"Request not found: {request_id}")
            return

        # Complete the future
        if not request.future.done():
            request.future.set_result(user_input)
            logger.info(
                f"User input received: req={request_id}, agent={request.agent_id}"
            )
        else:
            logger.warning(f"Request already completed: {request_id}")

    async def _handle_system_status(
        self, websocket: Any, message: dict[str, Any]
    ) -> None:
        """Handle system status message."""
        data = message.get("data", {})
        agent_id = data.get("agent_id")
        status = data.get("status")

        logger.info(f"System status from {agent_id}: {status}")

        # Broadcast status to all clients
        await self.server.broadcast(message)

    async def _handle_error(self, websocket: Any, message: dict[str, Any]) -> None:
        """Handle error message."""
        data = message.get("data", {})
        error = data.get("error")
        agent_id = data.get("agent_id")

        logger.error(f"Error from {agent_id}: {error}")

    async def _send_error(self, websocket: Any, error: str) -> None:
        """Send error message to client."""
        try:
            import json

            error_msg = json.dumps(
                {"type": MessageType.ERROR.value, "data": {"error": error}}
            )
            await websocket.send(error_msg)
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")

    async def _cleanup_expired_requests(self) -> None:
        """Background task to cleanup expired requests."""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds

                current_time = time.time()
                expired_requests = []

                # Find expired requests
                for request_id, request in self.pending_requests.items():
                    age = current_time - request.timestamp
                    if age > request.timeout:
                        expired_requests.append(request_id)

                # Cleanup expired requests
                for request_id in expired_requests:
                    expired = self.pending_requests.get(request_id)
                    if expired is not None:
                        del self.pending_requests[request_id]
                        if not expired.future.done():
                            expired.future.set_exception(
                                TimeoutError(
                                    f"User input request timed out: {expired.prompt}"
                                )
                            )
                        logger.warning(f"Cleaned up expired request: {request_id}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")

    def get_stats(self) -> dict[str, Any]:
        """Get router statistics."""
        return {
            "pending_requests": len(self.pending_requests),
            "active_handlers": len(self.message_handlers),
        }
