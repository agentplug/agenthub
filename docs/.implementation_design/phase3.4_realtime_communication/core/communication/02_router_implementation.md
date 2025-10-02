# Message Router Implementation Details - Phase 3.4

**Document Type**: Implementation Details
**Component**: MessageRouter
**Module**: core/communication
**Phase**: 3.4
**Status**: Design Phase

## 🎯 **Purpose**

Detailed implementation of the MessageRouter that handles routing of messages between users, agents, and other services, with support for A2A-compatible message passing.

## 🏗️ **Architecture Overview**

```
MessageRouter
├── User Input Handling
│   ├── Request user input from agent
│   ├── Forward user response to agent
│   └── Timeout handling
├── Agent-to-Agent Routing
│   ├── A2A message format
│   ├── Agent discovery
│   └── Message delivery
├── System Messages
│   ├── Status updates
│   ├── Progress notifications
│   └── Error notifications
└── Message Queue
    ├── Pending requests
    ├── Response tracking
    └── Cleanup on timeout
```

## 🔧 **Core Implementation**

### **1. MessageRouter Class**

```python
# agenthub/core/communication/router.py
"""Message routing for real-time agent communication."""

import asyncio
import logging
import time
import uuid
from typing import Dict, Any, Optional, Set, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Message types for routing."""
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
    future: asyncio.Future


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

    def __init__(self, server=None):
        """
        Initialize message router.

        Args:
            server: CommunicationServer instance
        """
        self.server = server

        # Pending user input requests
        self.pending_requests: Dict[str, PendingRequest] = {}

        # Agent registry for agent-to-agent communication
        self.agent_registry: Dict[str, Dict[str, Any]] = {}

        # Message handlers
        self.message_handlers: Dict[MessageType, Callable] = {
            MessageType.USER_INPUT_REQUEST: self._handle_user_input_request,
            MessageType.USER_INPUT_RESPONSE: self._handle_user_input_response,
            MessageType.AGENT_MESSAGE: self._handle_agent_message,
            MessageType.AGENT_REQUEST: self._handle_agent_request,
            MessageType.AGENT_RESPONSE: self._handle_agent_response,
            MessageType.SYSTEM_STATUS: self._handle_system_status,
            MessageType.ERROR: self._handle_error,
        }

        # Cleanup task
        self.cleanup_task: Optional[asyncio.Task] = None

        logger.info("MessageRouter initialized")

    def start(self):
        """Start background tasks."""
        if self.cleanup_task is None:
            self.cleanup_task = asyncio.create_task(self._cleanup_expired_requests())
            logger.info("MessageRouter started")

    async def stop(self):
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

    async def route_message(self, websocket, message: Dict[str, Any]):
        """
        Route message to appropriate handler.

        Args:
            websocket: Client WebSocket connection
            message: Message data
        """
        try:
            # Extract message type
            msg_type_str = message.get('type')

            # Convert to enum
            try:
                msg_type = MessageType(msg_type_str)
            except ValueError:
                logger.warning(f"Unknown message type: {msg_type_str}")
                await self._send_error(websocket, f"Unknown message type: {msg_type_str}")
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

    async def request_user_input(
        self,
        agent_id: str,
        prompt: str,
        timeout: float = 300.0
    ) -> Optional[str]:
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
        future = asyncio.Future()

        # Track pending request
        request = PendingRequest(
            request_id=request_id,
            agent_id=agent_id,
            prompt=prompt,
            timestamp=time.time(),
            timeout=timeout,
            future=future
        )
        self.pending_requests[request_id] = request

        # Send request to user
        message = {
            'type': MessageType.USER_INPUT_REQUEST.value,
            'data': {
                'request_id': request_id,
                'agent_id': agent_id,
                'prompt': prompt,
                'timestamp': request.timestamp
            }
        }

        await self.server.broadcast(message)
        logger.info(f"Requested user input for agent {agent_id}: {prompt}")

        try:
            # Wait for response with timeout
            response = await asyncio.wait_for(future, timeout=timeout)
            return response

        except asyncio.TimeoutError:
            logger.warning(f"User input request timed out: {request_id}")
            return None

        except Exception as e:
            logger.error(f"Error waiting for user input: {e}")
            return None

        finally:
            # Cleanup request
            self.pending_requests.pop(request_id, None)

    async def _handle_user_input_request(self, websocket, message: Dict):
        """Handle user input request from agent."""
        data = message.get('data', {})
        agent_id = data.get('agent_id')
        prompt = data.get('prompt')

        if not agent_id or not prompt:
            await self._send_error(websocket, "Missing agent_id or prompt")
            return

        # This is typically called from ProcessManager, not from WebSocket clients
        logger.debug(f"User input request: {agent_id} - {prompt}")

    async def _handle_user_input_response(self, websocket, message: Dict):
        """Handle user input response."""
        data = message.get('data', {})
        request_id = data.get('request_id')
        user_input = data.get('input')

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

    async def _handle_agent_message(self, websocket, message: Dict):
        """Handle agent-to-agent message."""
        data = message.get('data', {})
        from_agent = data.get('from_agent')
        to_agent = data.get('to_agent')
        content = data.get('content')

        if not all([from_agent, to_agent, content]):
            await self._send_error(websocket, "Missing required fields for agent message")
            return

        # Route to target agent
        success = await self.server.send_to_agent(to_agent, {
            'type': MessageType.AGENT_MESSAGE.value,
            'data': {
                'from_agent': from_agent,
                'content': content,
                'timestamp': time.time()
            }
        })

        if not success:
            logger.warning(f"Failed to deliver message to agent: {to_agent}")
            await self._send_error(websocket, f"Agent not found: {to_agent}")

    async def _handle_agent_request(self, websocket, message: Dict):
        """Handle agent-to-agent request (A2A style)."""
        data = message.get('data', {})
        from_agent = data.get('from_agent')
        to_agent = data.get('to_agent')
        task_type = data.get('task_type')
        parameters = data.get('parameters', {})
        request_id = data.get('request_id', str(uuid.uuid4()))

        if not all([from_agent, to_agent, task_type]):
            await self._send_error(websocket, "Missing required fields for agent request")
            return

        # Create A2A-compatible task message
        task_message = {
            'type': MessageType.AGENT_REQUEST.value,
            'data': {
                'request_id': request_id,
                'from_agent': from_agent,
                'task_type': task_type,
                'parameters': parameters,
                'timestamp': time.time()
            }
        }

        # Route to target agent
        success = await self.server.send_to_agent(to_agent, task_message)

        if not success:
            logger.warning(f"Failed to send request to agent: {to_agent}")
            await self._send_error(websocket, f"Agent not found: {to_agent}")
        else:
            logger.info(f"Agent request sent: {from_agent} -> {to_agent} ({task_type})")

    async def _handle_agent_response(self, websocket, message: Dict):
        """Handle response from agent (A2A style)."""
        data = message.get('data', {})
        request_id = data.get('request_id')
        result = data.get('result')
        error = data.get('error')

        if not request_id:
            await self._send_error(websocket, "Missing request_id")
            return

        # Find original requester and forward response
        # This would integrate with agent-to-agent request tracking
        logger.info(f"Agent response received for request: {request_id}")

    async def _handle_system_status(self, websocket, message: Dict):
        """Handle system status message."""
        data = message.get('data', {})
        agent_id = data.get('agent_id')
        status = data.get('status')

        logger.info(f"System status from {agent_id}: {status}")

        # Broadcast status to all clients
        await self.server.broadcast(message)

    async def _handle_error(self, websocket, message: Dict):
        """Handle error message."""
        data = message.get('data', {})
        error = data.get('error')
        agent_id = data.get('agent_id')

        logger.error(f"Error from {agent_id}: {error}")

    async def _send_error(self, websocket, error: str):
        """Send error message to client."""
        try:
            import json
            error_msg = json.dumps({
                'type': MessageType.ERROR.value,
                'data': {'error': error}
            })
            await websocket.send(error_msg)
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")

    async def _cleanup_expired_requests(self):
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
                            TimeoutError(f"User input request timed out: {request.prompt}")
                        )
                        logger.warning(f"Cleaned up expired request: {request_id}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")

    def register_agent(self, agent_id: str, metadata: Dict[str, Any]):
        """
        Register agent for agent-to-agent discovery.

        Args:
            agent_id: Agent identifier
            metadata: Agent metadata (capabilities, methods, etc.)
        """
        self.agent_registry[agent_id] = metadata
        logger.info(f"Registered agent: {agent_id}")

    def unregister_agent(self, agent_id: str):
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
            agent for agent in self.agent_registry.values()
            if capability in agent.get('capabilities', [])
        ]

    def get_stats(self) -> Dict[str, Any]:
        """Get router statistics."""
        return {
            'pending_requests': len(self.pending_requests),
            'registered_agents': len(self.agent_registry),
            'active_handlers': len(self.message_handlers)
        }
```

## 🔄 **Integration with ProcessManager**

```python
# agenthub/runtime/process_manager.py
# Add to ProcessManager class

class ProcessManager:
    async def _request_user_input_with_timeout(
        self,
        agent_id: str,
        prompt: str,
        timeout: float = 300.0
    ) -> Optional[str]:
        """
        Request user input during agent execution.

        This method integrates with the MessageRouter to request
        input from users in real-time during agent execution.
        """
        if not self.communication_server or not self.communication_server.is_running:
            # Fallback to stdin/stdout
            return self._request_user_input_fallback(prompt)

        # Get message router
        router = self.communication_server.message_router
        if not router:
            return self._request_user_input_fallback(prompt)

        # Request input through router
        user_input = await router.request_user_input(agent_id, prompt, timeout)

        if user_input is None:
            # Timeout or error - try fallback
            return self._request_user_input_fallback(prompt)

        return user_input

    def _request_user_input_fallback(self, prompt: str) -> str:
        """Fallback to stdin/stdout for user input."""
        print(f"\n{prompt}")
        return input("> ")
```

## 📊 **Performance Characteristics**

```python
# Expected performance metrics
- Message routing latency: 0.5-1ms
- Request/response round-trip: 2-5ms (depending on user response time)
- Pending request lookup: O(1)
- Agent discovery: O(n) where n = number of agents
- Cleanup cycle: Every 30 seconds, O(n) where n = pending requests
```

## 🧪 **Testing Requirements**

```python
# tests/phase3.4/test_message_router.py

import pytest
import asyncio
from agenthub.core.communication.router import MessageRouter, MessageType

@pytest.mark.asyncio
async def test_user_input_request_response():
    """Test user input request/response flow."""
    router = MessageRouter()
    router.start()

    # Simulate user input response
    async def provide_input():
        await asyncio.sleep(0.1)
        # Simulate user response
        request_id = list(router.pending_requests.keys())[0]
        await router._handle_user_input_response(None, {
            'type': MessageType.USER_INPUT_RESPONSE.value,
            'data': {
                'request_id': request_id,
                'input': 'test input'
            }
        })

    # Request input
    input_task = asyncio.create_task(
        router.request_user_input('test-agent', 'Enter value:', timeout=5.0)
    )
    response_task = asyncio.create_task(provide_input())

    result = await input_task
    await response_task

    assert result == 'test input'

    await router.stop()

@pytest.mark.asyncio
async def test_user_input_timeout():
    """Test user input request timeout."""
    router = MessageRouter()
    router.start()

    # Request with short timeout
    result = await router.request_user_input('test-agent', 'Enter value:', timeout=0.1)

    assert result is None
    assert len(router.pending_requests) == 0

    await router.stop()
```

## 🚀 **Future Enhancements**

- **Message persistence**: Store messages for replay/history
- **Priority routing**: Priority-based message queue
- **Load balancing**: Distribute agent requests across instances
- **Message encryption**: End-to-end message encryption
- **Rate limiting**: Prevent message flooding
