# Communication Server Implementation Details - Phase 3.4

**Document Type**: Implementation Details
**Component**: CommunicationServer
**Module**: core/communication
**Phase**: 3.4
**Status**: Design Phase

## 🎯 **Purpose**

Detailed implementation of the WebSocket-based CommunicationServer that enables real-time bidirectional communication between users and agents, with support for A2A-compatible agent-to-agent messaging.

## 🏗️ **Architecture Overview**

```
CommunicationServer (Singleton)
├── WebSocket Server (asyncio-based)
│   ├── Connection Manager
│   ├── Message Handler
│   └── Broadcast System
├── Message Router
│   ├── User → Agent routing
│   ├── Agent → Agent routing
│   └── Agent → User routing
├── Session Manager
│   ├── Active sessions tracking
│   ├── Session lifecycle management
│   └── Session cleanup
└── Error Handler
    ├── Connection errors
    ├── Message routing errors
    └── Graceful degradation
```

## 🔧 **Core Implementation**

### **1. CommunicationServer Class**

```python
# agenthub/core/communication/server.py
"""WebSocket server for real-time agent communication."""

import asyncio
import websockets
import json
import logging
import os
from typing import Set, Dict, Any, Optional, Callable
from pathlib import Path
from websockets.server import WebSocketServerProtocol

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

    _instance: Optional['CommunicationServer'] = None
    _lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
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

        # Server configuration
        self.port = port or int(os.getenv('AGENTHUB_WEBSOCKET_PORT', '38765'))
        self.host = host

        # Connection tracking
        self.clients: Set[WebSocketServerProtocol] = set()
        self.agent_sessions: Dict[str, Dict[str, Any]] = {}

        # Server state
        self.is_running = False
        self.server = None
        self.server_task: Optional[asyncio.Task] = None

        # Message handlers
        self.message_handlers: Dict[str, Callable] = {}

        # Error tracking
        self.startup_failed = False
        self.failure_reason = None

        self._initialized = True

        logger.info(f"CommunicationServer initialized on {self.host}:{self.port}")

    async def start(self) -> bool:
        """
        Start WebSocket server with graceful fallback.

        Returns:
            bool: True if server started successfully, False if fallback needed
        """
        async with self._lock:
            # Check if already running
            if self.is_running:
                logger.info("CommunicationServer already running")
                return True

            # Check if startup already failed
            if self.startup_failed:
                logger.warning(f"CommunicationServer startup failed previously: {self.failure_reason}")
                return False

            try:
                # Start WebSocket server
                self.server = await websockets.serve(
                    self._handle_client,
                    self.host,
                    self.port,
                    ping_interval=20,  # Keep connections alive
                    ping_timeout=10,   # Detect dead connections
                )

                self.is_running = True
                self.startup_failed = False

                logger.info(f"✅ CommunicationServer started on ws://{self.host}:{self.port}")
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

    async def stop(self):
        """Stop WebSocket server gracefully."""
        async with self._lock:
            if not self.is_running:
                logger.info("CommunicationServer not running")
                return

            try:
                # Close all client connections
                if self.clients:
                    await asyncio.gather(
                        *[client.close() for client in self.clients],
                        return_exceptions=True
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

    async def _handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """
        Handle individual client connection.

        Args:
            websocket: WebSocket client connection
            path: Connection path (unused in Phase 3.4)
        """
        # Register client
        self.clients.add(websocket)
        client_id = id(websocket)
        logger.info(f"Client connected: {client_id} (total clients: {len(self.clients)})")

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

    async def _handle_message(self, websocket: WebSocketServerProtocol, message: str):
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

            # Extract message type
            msg_type = data.get('type')

            # Route message to appropriate handler
            handler = self.message_handlers.get(msg_type, self._handle_unknown_message)
            await handler(websocket, data)

        except json.JSONDecodeError:
            logger.error(f"Invalid JSON message: {message}")
            await self._send_error(websocket, "Invalid JSON")

        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self._send_error(websocket, f"Message handling error: {str(e)}")

    def _validate_message(self, data: Dict[str, Any]) -> bool:
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

        if 'type' not in data:
            logger.warning("Message missing 'type' field")
            return False

        if 'data' not in data:
            logger.warning("Message missing 'data' field")
            return False

        return True

    async def _handle_unknown_message(self, websocket: WebSocketServerProtocol, data: Dict):
        """Handle unknown message type."""
        msg_type = data.get('type', 'unknown')
        logger.warning(f"Unknown message type: {msg_type}")
        await self._send_error(websocket, f"Unknown message type: {msg_type}")

    async def _send_error(self, websocket: WebSocketServerProtocol, error: str):
        """Send error message to client."""
        try:
            error_msg = json.dumps({
                'type': 'error',
                'data': {'error': error}
            })
            await websocket.send(error_msg)
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")

    async def broadcast(self, message: Dict[str, Any], exclude: Set[WebSocketServerProtocol] = None):
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
            return_exceptions=True
        )

    async def send_to_agent(self, agent_id: str, message: Dict[str, Any]) -> bool:
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
        client = session.get('client')
        if not client or client not in self.clients:
            logger.warning(f"Agent client not connected: {agent_id}")
            return False

        # Send message
        message_str = json.dumps(message)
        return await self._send_safe(client, message_str)

    async def _send_safe(self, websocket: WebSocketServerProtocol, message: str) -> bool:
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

    def register_agent_session(self, agent_id: str, session_data: Dict[str, Any]):
        """
        Register agent execution session.

        Args:
            agent_id: Agent identifier
            session_data: Session metadata (client, execution_id, etc.)
        """
        self.agent_sessions[agent_id] = session_data
        logger.info(f"Registered agent session: {agent_id}")

    def unregister_agent_session(self, agent_id: str):
        """Unregister agent session."""
        if agent_id in self.agent_sessions:
            del self.agent_sessions[agent_id]
            logger.info(f"Unregistered agent session: {agent_id}")

    async def _cleanup_client_sessions(self, client_id: int):
        """Cleanup sessions associated with disconnected client."""
        # Find sessions associated with this client
        sessions_to_remove = []
        for agent_id, session in self.agent_sessions.items():
            if id(session.get('client')) == client_id:
                sessions_to_remove.append(agent_id)

        # Remove sessions
        for agent_id in sessions_to_remove:
            self.unregister_agent_session(agent_id)

    def register_message_handler(self, msg_type: str, handler: Callable):
        """
        Register custom message handler.

        Args:
            msg_type: Message type to handle
            handler: Async function (websocket, data) -> None
        """
        self.message_handlers[msg_type] = handler
        logger.info(f"Registered message handler: {msg_type}")

    def get_stats(self) -> Dict[str, Any]:
        """Get server statistics."""
        return {
            'is_running': self.is_running,
            'connected_clients': len(self.clients),
            'active_sessions': len(self.agent_sessions),
            'port': self.port,
            'host': self.host,
            'startup_failed': self.startup_failed,
            'failure_reason': self.failure_reason
        }


# Global server instance accessor
_server_instance: Optional[CommunicationServer] = None

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
```

## 🔄 **Integration with ProcessManager**

### **1. Auto-Start on Agent Execution**

```python
# agenthub/runtime/process_manager.py
# Add to existing ProcessManager class

class ProcessManager:
    def __init__(self):
        # ... existing initialization ...
        self.communication_server = None
        self.communication_enabled = True  # Auto-enable by default

    async def _ensure_communication_server(self) -> bool:
        """
        Ensure communication server is running.

        Returns:
            bool: True if server available, False if fallback needed
        """
        if not self.communication_enabled:
            return False

        if self.communication_server is None:
            from agenthub.core.communication import get_communication_server
            self.communication_server = get_communication_server()

        # Try to start server if not running
        if not self.communication_server.is_running:
            success = await self.communication_server.start()
            if not success:
                logger.warning("Communication server unavailable, using fallback")
                return False

        return True

    async def execute_with_communication(self, agent_id: str, method: str, parameters: dict):
        """Execute agent with real-time communication."""
        # Ensure server is running
        server_available = await self._ensure_communication_server()

        if server_available:
            # Register agent session
            self.communication_server.register_agent_session(agent_id, {
                'execution_id': self._generate_execution_id(),
                'method': method,
                'parameters': parameters,
                'start_time': time.time()
            })

        try:
            # Execute agent
            result = await self._execute_agent(agent_id, method, parameters, server_available)
            return result
        finally:
            # Cleanup session
            if server_available:
                self.communication_server.unregister_agent_session(agent_id)
```

## 📊 **Performance Characteristics**

### **1. Startup Performance**

```python
# Benchmark results (expected)
- Server initialization: 2-3ms
- First connection: 5-10ms
- WebSocket handshake: 1-2ms
- Total startup overhead: 8-15ms (one-time)
```

### **2. Message Throughput**

```python
# Expected performance
- Messages/second: 1,000-5,000
- Per-message latency: 0.5-1.5ms
- Broadcast to 10 clients: 2-5ms
- Max concurrent clients: 100+
```

### **3. Memory Usage**

```python
# Expected memory footprint
- Base server: 2-3MB
- Per client: 20-50KB
- Per session: 10-20KB
- Total for 10 agents: 3-5MB
```

## 🧪 **Testing Requirements**

### **1. Unit Tests**

```python
# tests/phase3.4/test_communication_server.py

import pytest
import asyncio
from agenthub.core.communication.server import CommunicationServer

@pytest.mark.asyncio
async def test_server_start_stop():
    """Test server startup and shutdown."""
    server = CommunicationServer(port=38766)  # Use different port for testing

    # Start server
    success = await server.start()
    assert success is True
    assert server.is_running is True

    # Stop server
    await server.stop()
    assert server.is_running is False

@pytest.mark.asyncio
async def test_server_singleton():
    """Test singleton pattern."""
    server1 = CommunicationServer()
    server2 = CommunicationServer()
    assert server1 is server2

@pytest.mark.asyncio
async def test_graceful_fallback():
    """Test graceful fallback when port is unavailable."""
    # Start server on port
    server1 = CommunicationServer(port=38767)
    await server1.start()

    # Try to start another server on same port (should fail gracefully)
    server2 = CommunicationServer(port=38767)
    success = await server2.start()
    assert success is False
    assert server2.startup_failed is True

    # Cleanup
    await server1.stop()
```

### **2. Integration Tests**

```python
# Test WebSocket communication
@pytest.mark.asyncio
async def test_client_connection():
    """Test client connection and disconnection."""
    server = CommunicationServer(port=38768)
    await server.start()

    # Connect client
    import websockets
    async with websockets.connect(f"ws://localhost:{server.port}") as ws:
        assert len(server.clients) == 1

    # Client should be removed after disconnect
    await asyncio.sleep(0.1)
    assert len(server.clients) == 0

    await server.stop()
```

## 🚀 **Future Enhancements**

Phase 3.4 provides foundation for:
- **Phase 4.x**: SSL/TLS support for remote connections
- **Phase 4.x**: Authentication and authorization
- **Phase 4.x**: Cross-machine agent communication
- **Phase 4.x**: Message persistence and replay
- **Phase 4.x**: Advanced monitoring and metrics
