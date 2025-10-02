# Phase 3.4: Real-time Communication Architecture Design

## 1. System Overview

The real-time communication system provides WebSocket-based bidirectional communication between users and agents, and enables A2A-compatible message passing between agents.

## 2. Architecture Components

### 2.1 Core Communication Module

```python
# agenthub/core/communication/__init__.py
"""Core communication module for real-time agent interaction."""

from .server import CommunicationServer
from .router import MessageRouter
from .session import SessionManager
from .protocol import A2AMessageAdapter

__all__ = [
    "CommunicationServer",
    "MessageRouter",
    "SessionManager",
    "A2AMessageAdapter",
]
```

### 2.2 Communication Server

```python
# agenthub/core/communication/server.py
"""WebSocket server for real-time communication."""

import asyncio
import json
import logging
import websockets
from typing import Set, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class CommunicationServer:
    """
    Single shared WebSocket server for all agents.

    Integrates with existing AgentHub patterns:
    - Auto-starts when first agent needs communication
    - Gracefully handles startup failures
    - Routes messages between users and agents
    - A2A-compatible message structure
    """

    def __init__(self, port: int = 38765):
        """
        Initialize communication server.

        Args:
            port: WebSocket server port (default: 38765)
                  Port 38765 is in the IANA unassigned range (38866-39680)
                  to avoid conflicts with common services
        """
        self.port = port
        self.clients: Set[websockets.WebSocketServerProtocol] = set()
        self.agent_sessions: Dict[str, Dict[str, Any]] = {}
        self.is_running = False
        self.server_task: asyncio.Task | None = None
        self.message_router = None
        self.session_manager = None

    async def start(self) -> bool:
        """
        Start WebSocket server with graceful error handling.

        Returns:
            True if server started successfully, False otherwise
        """
        if self.is_running:
            logger.info("Communication server already running")
            return True

        try:
            # Initialize components
            from .router import MessageRouter
            from .session import SessionManager

            self.message_router = MessageRouter(self)
            self.session_manager = SessionManager(self)

            # Start WebSocket server
            self.server_task = asyncio.create_task(self._run_server())

            # Wait briefly to ensure server is ready
            await asyncio.sleep(0.1)

            self.is_running = True
            logger.info(f"Communication server started on port {self.port}")
            return True

        except Exception as e:
            logger.warning(f"Failed to start communication server: {e}")
            self.is_running = False
            return False

    async def stop(self):
        """Stop WebSocket server gracefully."""
        if not self.is_running:
            return

        self.is_running = False

        # Close all client connections
        if self.clients:
            await asyncio.gather(
                *[client.close() for client in self.clients],
                return_exceptions=True
            )

        # Cancel server task
        if self.server_task:
            self.server_task.cancel()
            try:
                await self.server_task
            except asyncio.CancelledError:
                pass

        logger.info("Communication server stopped")

    async def _run_server(self):
        """Run WebSocket server loop."""
        try:
            async with websockets.serve(
                self._handle_client,
                "localhost",
                self.port
            ):
                await asyncio.Future()  # Run forever
        except Exception as e:
            logger.error(f"WebSocket server error: {e}")
            self.is_running = False

    async def _handle_client(self, websocket, path):
        """Handle client connections."""
        self.clients.add(websocket)
        logger.debug(f"Client connected. Total clients: {len(self.clients)}")

        try:
            async for message in websocket:
                await self._handle_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            logger.debug("Client connection closed")
        finally:
            self.clients.discard(websocket)
            logger.debug(f"Client disconnected. Total clients: {len(self.clients)}")

    async def _handle_message(self, websocket, message: str):
        """Handle incoming messages."""
        try:
            data = json.loads(message)

            # Route message through message router
            if self.message_router:
                await self.message_router.route_message(websocket, data)
            else:
                logger.warning("Message router not initialized")

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message: {message}")
            await self._send_error(websocket, "Invalid JSON message")
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self._send_error(websocket, str(e))

    async def broadcast_event(self, event: Dict[str, Any]):
        """
        Broadcast event to all connected clients.

        Args:
            event: Event data to broadcast
        """
        if not self.clients:
            return

        message = json.dumps({
            "type": "event",
            "data": event
        })

        # Send to all connected clients
        disconnected = set()
        for client in self.clients:
            try:
                await client.send(message)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)

        # Clean up disconnected clients
        self.clients -= disconnected

    async def _send_error(self, websocket, error: str):
        """Send error message to client."""
        try:
            await websocket.send(json.dumps({
                "type": "error",
                "error": error
            }))
        except Exception:
            pass
```

### 2.3 Message Router

```python
# agenthub/core/communication/router.py
"""Message routing for communication server."""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class MessageRouter:
    """
    Routes messages between users, agents, and services.

    Message Types:
    - user_input: User providing input to agent
    - agent_request: Agent requesting input from user
    - agent_message: Agent-to-agent message (A2A-compatible)
    - system_event: System events and notifications
    """

    def __init__(self, server):
        """Initialize message router."""
        self.server = server
        self.pending_requests: Dict[str, Any] = {}

    async def route_message(self, websocket, message: Dict[str, Any]):
        """Route message to appropriate handler."""
        message_type = message.get("type")

        if message_type == "user_input":
            await self._handle_user_input(message)
        elif message_type == "agent_request":
            await self._handle_agent_request(message)
        elif message_type == "agent_message":
            await self._handle_agent_message(message)
        else:
            logger.warning(f"Unknown message type: {message_type}")

    async def _handle_user_input(self, message: Dict[str, Any]):
        """Handle user input response."""
        request_id = message.get("request_id")
        user_input = message.get("input")

        if request_id in self.pending_requests:
            # Forward input to waiting agent
            agent_session = self.pending_requests[request_id]
            agent_session["user_input"] = user_input
            agent_session["input_received"].set()

            logger.debug(f"User input received for request {request_id}")
        else:
            logger.warning(f"No pending request for ID: {request_id}")

    async def _handle_agent_request(self, message: Dict[str, Any]):
        """Handle agent request for user input."""
        request_id = message.get("request_id")
        prompt = message.get("prompt")
        agent_id = message.get("agent_id")

        # Store pending request
        self.pending_requests[request_id] = {
            "prompt": prompt,
            "agent_id": agent_id,
            "input_received": asyncio.Event()
        }

        # Broadcast request to all clients
        await self.server.broadcast_event({
            "type": "input_request",
            "request_id": request_id,
            "prompt": prompt,
            "agent_id": agent_id
        })

        logger.debug(f"Agent {agent_id} requested user input: {prompt}")

    async def _handle_agent_message(self, message: Dict[str, Any]):
        """Handle agent-to-agent message (A2A-compatible)."""
        from_agent = message.get("from_agent")
        to_agent = message.get("to_agent")
        content = message.get("content")

        # Route message to target agent
        # This will be enhanced in future phases with full A2A protocol
        logger.debug(f"Agent message: {from_agent} -> {to_agent}")

        # For now, broadcast to all clients
        # Future: Route directly to target agent
        await self.server.broadcast_event({
            "type": "agent_message",
            "from_agent": from_agent,
            "to_agent": to_agent,
            "content": content
        })
```

### 2.4 Session Manager

```python
# agenthub/core/communication/session.py
"""Session management for agent execution."""

import uuid
import time
from typing import Dict, Any

class SessionManager:
    """Manages active agent execution sessions."""

    def __init__(self, server):
        """Initialize session manager."""
        self.server = server
        self.sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(self, agent_id: str, method: str, parameters: Dict[str, Any]) -> str:
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
            "agent_id": agent_id,
            "method": method,
            "parameters": parameters,
            "start_time": time.time(),
            "status": "starting"
        }

        return session_id

    def update_session(self, session_id: str, status: str, data: Dict[str, Any] | None = None):
        """Update session status and data."""
        if session_id in self.sessions:
            self.sessions[session_id]["status"] = status
            if data:
                self.sessions[session_id].update(data)

    def end_session(self, session_id: str):
        """End session and cleanup."""
        if session_id in self.sessions:
            self.sessions[session_id]["end_time"] = time.time()
            self.sessions[session_id]["status"] = "completed"
            # Keep for short time for history, then cleanup

    def get_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """Get all active sessions."""
        return {
            sid: session for sid, session in self.sessions.items()
            if session.get("status") not in ["completed", "error"]
        }
```

### 2.5 A2A Message Adapter

```python
# agenthub/core/communication/protocol.py
"""A2A-compatible message format adapter."""

from typing import Dict, Any
from datetime import datetime

class A2AMessageAdapter:
    """
    Adapter for A2A-compatible message format.

    Provides lightweight A2A-compatible message structure
    without full protocol implementation. Designed for
    future integration with official A2A SDK.
    """

    @staticmethod
    def create_task_message(
        from_agent: str,
        to_agent: str,
        task_type: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create A2A-compatible task message.

        Args:
            from_agent: Source agent ID
            to_agent: Target agent ID
            task_type: Type of task
            parameters: Task parameters

        Returns:
            A2A-compatible message structure
        """
        return {
            "protocol": "a2a-compatible",
            "version": "0.1.0",
            "message_type": "task",
            "from_agent": from_agent,
            "to_agent": to_agent,
            "task": {
                "type": task_type,
                "parameters": parameters
            },
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "platform": "agenthub",
                "transport": "websocket"
            }
        }

    @staticmethod
    def create_response_message(
        request_message: Dict[str, Any],
        result: Any,
        success: bool = True,
        error: str | None = None
    ) -> Dict[str, Any]:
        """
        Create A2A-compatible response message.

        Args:
            request_message: Original request message
            result: Task result
            success: Whether task succeeded
            error: Error message if failed

        Returns:
            A2A-compatible response message
        """
        return {
            "protocol": "a2a-compatible",
            "version": "0.1.0",
            "message_type": "response",
            "from_agent": request_message.get("to_agent"),
            "to_agent": request_message.get("from_agent"),
            "response": {
                "success": success,
                "result": result,
                "error": error
            },
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "platform": "agenthub",
                "transport": "websocket"
            }
        }

    @staticmethod
    def validate_message(message: Dict[str, Any]) -> bool:
        """
        Validate A2A-compatible message structure.

        Args:
            message: Message to validate

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["protocol", "version", "message_type", "from_agent", "to_agent"]
        return all(field in message for field in required_fields)
```

## 3. ProcessManager Integration

### 3.1 Enhanced ProcessManager

```python
# agenthub/runtime/process_manager.py
"""Process manager with real-time communication support."""

class ProcessManager:
    """Manages agent subprocess execution with real-time communication."""

    def __init__(
        self,
        timeout: int = 300,
        use_dynamic_execution: bool = True,
        monitoring: bool = False,
        realtime_communication: bool = True,  # NEW: Auto-enable by default
    ) -> None:
        """
        Initialize the process manager.

        Args:
            timeout: Maximum execution time in seconds
            use_dynamic_execution: Whether to use dynamic execution
            monitoring: Whether to enable real-time monitoring
            realtime_communication: Whether to enable WebSocket communication
        """
        # Existing initialization...
        self.timeout = timeout
        self.environment_manager = EnvironmentManager()
        self.use_dynamic_execution = use_dynamic_execution
        self.monitoring = monitoring

        # NEW: Real-time communication
        self.realtime_communication = realtime_communication
        self.communication_server = None
        self._server_started = False

        # Try to start communication server if enabled
        if realtime_communication:
            self._try_start_communication_server()

    def _try_start_communication_server(self):
        """Try to start communication server with graceful fallback."""
        try:
            # Check if WebSocket dependencies are available
            import websockets

            # Import communication server
            from agenthub.core.communication import CommunicationServer

            # Create server instance
            self.communication_server = CommunicationServer()

            # Server will be started on first use (lazy initialization)
            logger.info("Communication server initialized (will start on first use)")

        except ImportError as e:
            logger.info(f"WebSocket not available: {e}. Falling back to stdin/stdout")
            self.realtime_communication = False
        except Exception as e:
            logger.warning(f"Failed to initialize communication server: {e}")
            self.realtime_communication = False

    async def _ensure_communication_server(self):
        """Ensure communication server is started."""
        if not self.realtime_communication or self._server_started:
            return

        if self.communication_server:
            success = await self.communication_server.start()
            if success:
                self._server_started = True
            else:
                logger.warning("Failed to start communication server, using fallback")
                self.realtime_communication = False

    def execute_agent(
        self,
        agent_path: str,
        method: str,
        parameters: dict[str, Any],
        manifest: dict[str, Any] | None = None,
        tool_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute agent with real-time communication support."""

        # Ensure communication server is running
        if self.realtime_communication:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            loop.run_until_complete(self._ensure_communication_server())

        # Continue with existing execution logic...
        # (Existing execute_agent code remains unchanged)
```

## 4. Agent Template Enhancement

### 4.1 Enhanced DynamicAgent

```python
# agenthub/core/agents/agent_template.py
"""Enhanced agent template with interactive capabilities."""

import os
import json
import sys
from typing import Any

class DynamicAgent:
    """
    Base class for dynamic agents with optional interactive capabilities.

    Backward Compatible:
    - Existing agents work unchanged
    - Interactive methods available but optional
    - Graceful fallback to stdin/stdout if WebSocket unavailable
    """

    def __init__(self) -> None:
        """Initialize the agent."""
        self._websocket_url = os.environ.get('AGENTHUB_WEBSOCKET_URL')
        self._agent_id = os.environ.get('AGENTHUB_AGENT_ID', 'unknown')

    def has_websocket_support(self) -> bool:
        """Check if WebSocket communication is available."""
        return self._websocket_url is not None

    def request_user_input(self, prompt: str, input_type: str = "text") -> str:
        """
        Request input from user with automatic fallback.

        Args:
            prompt: Prompt to show user
            input_type: Type of input (text, confirmation, etc.)

        Returns:
            User input string
        """
        if self.has_websocket_support():
            return self._request_input_via_websocket(prompt, input_type)
        else:
            return self._request_input_via_stdin(prompt, input_type)

    def _request_input_via_websocket(self, prompt: str, input_type: str) -> str:
        """Request input via WebSocket."""
        try:
            # Send request through WebSocket
            # Implementation will use communication server
            request = {
                "type": "agent_request",
                "request_id": str(uuid.uuid4()),
                "prompt": prompt,
                "input_type": input_type,
                "agent_id": self._agent_id
            }

            # This will be handled by the communication infrastructure
            print(json.dumps({"__websocket_request__": request}))
            sys.stdout.flush()

            # Wait for response (handled by runtime)
            response_line = sys.stdin.readline()
            response = json.loads(response_line.strip())
            return response.get("input", "")

        except Exception as e:
            # Fallback to stdin if WebSocket fails
            return self._request_input_via_stdin(prompt, input_type)

    def _request_input_via_stdin(self, prompt: str, input_type: str) -> str:
        """Fallback: Request input via stdin."""
        if input_type == "confirmation":
            response = input(f"{prompt} (y/n): ").lower()
            return "y" if response in ["y", "yes"] else "n"
        else:
            return input(f"{prompt}: ")

    def send_agent_message(self, target_agent: str, message_type: str, content: Any) -> dict:
        """
        Send message to another agent (A2A-compatible).

        Args:
            target_agent: Target agent ID
            message_type: Type of message
            content: Message content

        Returns:
            Response from target agent
        """
        if self.has_websocket_support():
            return self._send_via_websocket(target_agent, message_type, content)
        else:
            # No fallback for agent-to-agent communication
            return {"error": "Agent-to-agent communication not available"}

    def _send_via_websocket(self, target_agent: str, message_type: str, content: Any) -> dict:
        """Send message via WebSocket."""
        from agenthub.core.communication import A2AMessageAdapter

        message = A2AMessageAdapter.create_task_message(
            from_agent=self._agent_id,
            to_agent=target_agent,
            task_type=message_type,
            parameters=content
        )

        # Send through WebSocket
        print(json.dumps({"__websocket_message__": message}))
        sys.stdout.flush()

        # Wait for response
        # Implementation will be handled by runtime
        return {"status": "sent"}
```

## 5. Error Handling and Fallback

### 5.1 Graceful Degradation

```python
def _execute_with_fallback(self, agent_path, method, parameters):
    """Execute with graceful fallback if WebSocket unavailable."""

    # Try WebSocket execution
    if self.realtime_communication and self._server_started:
        try:
            return self._execute_with_websocket(agent_path, method, parameters)
        except Exception as e:
            logger.warning(f"WebSocket execution failed: {e}, using fallback")

    # Fallback to standard execution
    return self._execute_without_websocket(agent_path, method, parameters)
```

## 6. Performance Considerations

### 6.1 Minimal Overhead Design

- **Lazy Server Start**: Server only starts when first agent needs it
- **Connection Pooling**: Reuse connections across agents
- **Async Operations**: Non-blocking message handling
- **Memory Efficient**: Minimal state storage

### 6.2 Overhead Budget

- Startup: 2-5ms (one-time)
- Per-execution: 0.5-1.5ms (with WebSocket)
- Memory: 3-5MB (server + connections)
- CPU: <2% idle, <5% active

## 7. Testing Strategy

### 7.1 Unit Tests

- CommunicationServer startup/shutdown
- Message routing correctness
- Session management
- A2A message format validation
- Fallback mechanisms

### 7.2 Integration Tests

- User-agent interaction flow
- Agent-agent message passing
- WebSocket failure scenarios
- Backward compatibility

## 8. Future Extensibility

### 8.1 Designed for Future Enhancements

- **Cross-machine Communication**: Message format supports remote agents
- **Real-time Chat**: Protocol supports bidirectional streaming
- **Full A2A Protocol**: Compatible with official A2A SDK
- **WebSocket Monitoring**: Foundation for Phase 4.x monitoring system

### 8.2 Migration Path

Phase 3.4 provides the foundation for:
- Phase 4.x: Full A2A protocol implementation
- Phase 4.x: Cross-machine agent communication
- Phase 4.x: WebSocket-based monitoring system
- Phase 4.x: Real-time chat interface

## 9. Success Metrics

- **User-Agent Interaction**: 95%+ success rate
- **Fallback Reliability**: 100% fallback when WebSocket unavailable
- **Performance**: <10% overhead per execution
- **Backward Compatibility**: 100% existing agents work unchanged
- **A2A Compatibility**: Message format compatible with A2A protocol
