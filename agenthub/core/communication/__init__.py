"""Core communication module for real-time user-agent interaction.

This module provides WebSocket-based real-time infrastructure for
monitoring and user interaction: streaming agent logs/progress to
clients and routing user-input requests to connected users.

Agent-to-agent messaging (the phase-3.4 A2A protocol) was removed:
AgentHub's composition story is MCP tools. See
docs/adr/0002-communication-transport.md.

Components:
- CommunicationServer: Single shared WebSocket server
- MessageRouter: Routes session/user-input/status messages
- SessionManager: Manages active agent execution sessions

Usage:
    from agenthub.core.communication import get_communication_server

    # Get singleton server instance
    server = get_communication_server()

    # Start server (auto-starts on first use)
    success = await server.start()
"""

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
]
