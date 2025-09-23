"""HTTP log suppressor for MCP client logs."""

import logging
import re


class MCPHTTPLogFilter(logging.Filter):
    """Filter to suppress MCP client HTTP logs."""

    def __init__(self, name: str = ""):
        """Initialize MCP HTTP log filter.

        Args:
            name: Filter name
        """
        super().__init__(name)
        # Patterns for MCP HTTP logs to suppress
        self.suppress_patterns = [
            r"HTTP Request:",
            r"INFO:.*127\.0\.0\.1.*HTTP/1\.1",
            r"GET /sse HTTP/1\.1.*200 OK",
            r"POST /messages/.*HTTP/1\.1.*202 Accepted",
            r"INFO:.*HTTP Request:",
            r"INFO:.*GET http://localhost:8000/sse",
            r"INFO:.*POST http://localhost:8000/messages/",
            r"INFO:.*_client\.py.*HTTP/1\.1",
        ]

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log record.

        Args:
            record: Log record to filter

        Returns:
            True if record should be kept, False if suppressed
        """
        message = record.getMessage()

        # Suppress MCP HTTP logs
        for pattern in self.suppress_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return False

        # Keep everything else
        return True


def suppress_mcp_http_logs() -> None:
    """Suppress MCP client HTTP logs globally."""
    # Aggressively suppress all MCP and HTTP related loggers
    mcp_loggers = [
        "mcp",
        "mcp.client",
        "mcp.client.session",
        "mcp.client.stdio",
        "mcp.client.session.client",
        "mcp.client.stdio.stdio_client",
        "urllib3",
        "httpx",
        "httpcore",
        "requests",
    ]

    for logger_name in mcp_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.CRITICAL)
        logger.disabled = True
