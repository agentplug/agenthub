"""MCP Connection Manager - Centralized connection management with pooling."""

import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

logger = logging.getLogger(__name__)


class MCPConnectionPool:
    """Connection pool for MCP clients to reduce connection overhead."""

    def __init__(self, max_connections: int = 5, max_idle_time: int = 300) -> None:
        """Initialize connection pool.

        Args:
            max_connections: Maximum number of concurrent connections
            max_idle_time: Maximum idle time before closing connection (seconds)
        """
        self.max_connections = max_connections
        self.max_idle_time = max_idle_time
        self._connections: list[ClientSession] = []
        self._available_connections: asyncio.Queue = asyncio.Queue()
        self._connection_times: dict[ClientSession, float] = {}
        self._lock = asyncio.Lock()
        self._cleanup_task: asyncio.Task | None = None

    async def _create_connection(self) -> ClientSession:
        """Create a new MCP connection."""
        server_params = StdioServerParameters(
            command="python",
            args=[
                "-c",
                "from agenthub.core.tools import get_mcp_server; "
                "import asyncio; asyncio.run(get_mcp_server().run_stdio())",
            ],
        )

        stdio_transport = stdio_client(server_params)
        client = await stdio_transport.__aenter__()
        logger.debug("Created new MCP connection")
        return client  # type: ignore

    async def _cleanup_idle_connections(self) -> None:
        """Clean up idle connections."""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                current_time = asyncio.get_event_loop().time()

                async with self._lock:
                    connections_to_close = []
                    for conn, created_time in self._connection_times.items():
                        if current_time - created_time > self.max_idle_time:
                            connections_to_close.append(conn)

                    for conn in connections_to_close:
                        await self._close_connection(conn)

            except Exception as e:
                logger.error(f"Error in connection cleanup: {e}")

    async def _close_connection(self, connection: ClientSession) -> None:
        """Close a specific connection."""
        try:
            if hasattr(connection, "close"):
                await connection.close()
            elif hasattr(connection, "aclose"):
                await connection.aclose()
            if connection in self._connections:
                self._connections.remove(connection)
            if connection in self._connection_times:
                del self._connection_times[connection]
            logger.debug("Closed MCP connection")
        except Exception as e:
            logger.error(f"Error closing connection: {e}")

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[ClientSession, None]:
        """Get a connection from the pool (context manager)."""
        connection = None
        try:
            # Try to get existing connection
            try:
                connection = self._available_connections.get_nowait()
            except asyncio.QueueEmpty:
                # Create new connection if under limit
                async with self._lock:
                    if len(self._connections) < self.max_connections:
                        connection = await self._create_connection()
                        self._connections.append(connection)
                        self._connection_times[connection] = (
                            asyncio.get_event_loop().time()
                        )
                    else:
                        # Wait for available connection
                        connection = await self._available_connections.get()

            yield connection

        finally:
            # Return connection to pool
            if connection:
                try:
                    self._available_connections.put_nowait(connection)
                except asyncio.QueueFull:
                    # Pool is full, close the connection
                    await self._close_connection(connection)

    async def close_all(self) -> None:
        """Close all connections in the pool."""
        async with self._lock:
            for connection in self._connections.copy():
                await self._close_connection(connection)
            self._connections.clear()
            self._connection_times.clear()

        # Cancel cleanup task
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()

    def start_cleanup_task(self) -> None:
        """Start the cleanup task."""
        if not self._cleanup_task or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_idle_connections())


# Global connection pool
_connection_pool: MCPConnectionPool | None = None


def get_connection_pool() -> MCPConnectionPool:
    """Get the global connection pool."""
    global _connection_pool
    if _connection_pool is None:
        _connection_pool = MCPConnectionPool()
        _connection_pool.start_cleanup_task()
    return _connection_pool


async def cleanup_connection_pool() -> None:
    """Cleanup the global connection pool."""
    global _connection_pool
    if _connection_pool:
        await _connection_pool.close_all()
        _connection_pool = None
