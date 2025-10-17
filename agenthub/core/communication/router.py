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
    AGENT_MESSAGE = "agent_message"
    AGENT_REQUEST = "agent_request"
    AGENT_RESPONSE = "agent_response"
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

    Design Principles:
    - Message type based routing
    - Request/response tracking
    - Timeout handling
    - A2A-compatible message format

    Integration Points:
    - CommunicationServer: Uses this router for message handling
    - ProcessManager: Sends/receives messages through this router
    - A2AMessageAdapter: Converts messages to A2A format
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

        # Agent registry for agent-to-agent communication
        self.agent_registry: dict[str, dict[str, Any]] = {}

        # Message handlers
        self.message_handlers: dict[MessageType, Callable] = {
            MessageType.REGISTER_SESSION: self._handle_register_session,
            MessageType.USER_INPUT_REQUEST: self._handle_user_input_request,
            MessageType.USER_INPUT_RESPONSE: self._handle_user_input_response,
            MessageType.AGENT_MESSAGE: self._handle_agent_message,
            MessageType.AGENT_REQUEST: self._handle_agent_request,
            MessageType.AGENT_RESPONSE: self._handle_agent_response,
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
            except asyncio.CancelledError:
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

        # Send request to user
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
        logger.info(f"Requested user input for agent {agent_id}: {prompt}")

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
            self.pending_requests.pop(request_id, None)

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
            logger.info(f"User input received for request {request_id}")
        else:
            logger.warning(f"Request already completed: {request_id}")

    async def _handle_agent_message(
        self, websocket: Any, message: dict[str, Any]
    ) -> None:
        """Handle agent-to-agent message."""
        data = message.get("data", {})
        from_agent = data.get("from_agent")
        to_agent = data.get("to_agent")
        content = data.get("content")

        if not all([from_agent, to_agent, content]):
            await self._send_error(
                websocket, "Missing required fields for agent message"
            )
            return

        # Route to target agent
        success = await self.server.send_to_agent(
            to_agent,
            {
                "type": MessageType.AGENT_MESSAGE.value,
                "data": {
                    "from_agent": from_agent,
                    "content": content,
                    "timestamp": time.time(),
                },
            },
        )

        if not success:
            logger.warning(f"Failed to deliver message to agent: {to_agent}")
            await self._send_error(websocket, f"Agent not found: {to_agent}")

    async def _handle_agent_request(
        self, websocket: Any, message: dict[str, Any]
    ) -> None:
        """Handle agent-to-agent request (A2A style)."""
        data = message.get("data", {})
        from_agent = data.get("from_agent")
        to_agent = data.get("to_agent")
        task_type = data.get("task_type")
        parameters = data.get("parameters", {})
        request_id = data.get("request_id", str(uuid.uuid4()))

        if not all([from_agent, to_agent, task_type]):
            await self._send_error(
                websocket, "Missing required fields for agent request"
            )
            return

        # Create A2A-compatible task message
        task_message = {
            "type": MessageType.AGENT_REQUEST.value,
            "data": {
                "request_id": request_id,
                "from_agent": from_agent,
                "task_type": task_type,
                "parameters": parameters,
                "timestamp": time.time(),
            },
        }

        # Route to target agent
        success = await self.server.send_to_agent(to_agent, task_message)

        if not success:
            logger.warning(f"Failed to send request to agent: {to_agent}")
            await self._send_error(websocket, f"Agent not found: {to_agent}")
        else:
            logger.info(f"Agent request sent: {from_agent} -> {to_agent} ({task_type})")

    async def _handle_agent_response(
        self, websocket: Any, message: dict[str, Any]
    ) -> None:
        """Handle response from agent (A2A style)."""
        data = message.get("data", {})
        request_id = data.get("request_id")
        # result = data.get("result")  # Placeholder for future implementation
        # error = data.get("error")  # Placeholder for future implementation

        if not request_id:
            await self._send_error(websocket, "Missing request_id")
            return

        # Find original requester and forward response
        # This would integrate with agent-to-agent request tracking
        logger.info(f"Agent response received for request: {request_id}")

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
                    request = self.pending_requests.pop(request_id, None)
                    if request and not request.future.done():
                        request.future.set_exception(
                            TimeoutError(
                                f"User input request timed out: {request.prompt}"
                            )
                        )
                        logger.warning(f"Cleaned up expired request: {request_id}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")

    def register_agent(self, agent_id: str, metadata: dict[str, Any]) -> None:
        """
        Register agent for agent-to-agent discovery.

        Args:
            agent_id: Agent identifier
            metadata: Agent metadata (capabilities, methods, etc.)
        """
        self.agent_registry[agent_id] = metadata
        logger.info(f"Registered agent: {agent_id}")

    def unregister_agent(self, agent_id: str) -> None:
        """Unregister agent."""
        if agent_id in self.agent_registry:
            del self.agent_registry[agent_id]
            logger.info(f"Unregistered agent: {agent_id}")

    def discover_agents(self, capability: str = None) -> list:
        """
        Discover available agents.

        Args:
            capability: Optional capability filter

        Returns:
            List of agent metadata dicts
        """
        if capability is None:
            return list(self.agent_registry.values())

        # Filter by capability
        return [
            agent
            for agent in self.agent_registry.values()
            if capability in agent.get("capabilities", [])
        ]

    def get_stats(self) -> dict[str, Any]:
        """Get router statistics."""
        return {
            "pending_requests": len(self.pending_requests),
            "registered_agents": len(self.agent_registry),
            "active_handlers": len(self.message_handlers),
        }
