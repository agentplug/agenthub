"""Core communication module for real-time agent interaction.

This module provides WebSocket-based real-time communication infrastructure
for user-agent and agent-agent interactions.

Components:
- CommunicationServer: Single shared WebSocket server
- MessageRouter: Routes messages between users, agents, and services
- SessionManager: Manages active agent execution sessions
- A2AMessageAdapter: A2A-compatible message format adapter

Usage:
    from agenthub.core.communication import get_communication_server

    # Get singleton server instance
    server = get_communication_server()

    # Start server (auto-starts on first use)
    success = await server.start()
"""

from .protocol import (
    A2AAgentCard,
    A2AMessageAdapter,
    A2AMessageType,
    A2AResultMessage,
    A2AStatusMessage,
    A2ATaskMessage,
    A2ATaskStatus,
)
from .router import MessageRouter, MessageType
from .server import CommunicationServer, get_communication_server
from .session import SessionManager

__all__ = [
    # Server
    "CommunicationServer",
    "get_communication_server",
    # Router
    "MessageRouter",
    "MessageType",
    # Session
    "SessionManager",
    # Protocol
    "A2AMessageAdapter",
    "A2AAgentCard",
    "A2ATaskMessage",
    "A2AStatusMessage",
    "A2AResultMessage",
    "A2AMessageType",
    "A2ATaskStatus",
]
