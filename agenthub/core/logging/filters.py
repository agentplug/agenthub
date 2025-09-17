"""Custom log filters for AgentHub."""

import logging
import re


class HTTPLogFilter(logging.Filter):
    """Filter to suppress verbose HTTP logs while keeping important ones."""

    def __init__(self, name: str = ""):
        """Initialize HTTP log filter.

        Args:
            name: Filter name
        """
        super().__init__(name)
        # Patterns for logs to keep (important agent-related logs)
        self.keep_patterns = [
            r"Successfully loaded agent",
            r"Assigned tools to agent",
            r"Tool execution",
            r"Agent execution",
            r"Processing request of type",
            r"\[TOOL\]",
            r"Agent.*error",
            r"Tool.*error",
        ]

        # Patterns for logs to suppress (verbose HTTP logs)
        self.suppress_patterns = [
            r"HTTP Request:",
            r"INFO:.*127\.0\.0\.1.*HTTP/1\.1",
            r"GET /sse HTTP/1\.1.*200 OK",
            r"POST /messages/.*HTTP/1\.1.*202 Accepted",
            r"INFO:.*HTTP Request:",
            r"INFO:.*GET http://localhost:8000/sse",
            r"INFO:.*POST http://localhost:8000/messages/",
        ]

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log record.

        Args:
            record: Log record to filter

        Returns:
            True if record should be kept, False if suppressed
        """
        message = record.getMessage()

        # Always keep important agent logs
        for pattern in self.keep_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return True

        # Suppress verbose HTTP logs
        for pattern in self.suppress_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                return False

        # Keep everything else
        return True


class AgentLogFilter(logging.Filter):
    """Filter to show only agent-related logs in quiet mode."""

    def __init__(self, name: str = ""):
        """Initialize agent log filter.

        Args:
            name: Filter name
        """
        super().__init__(name)
        # Patterns for agent-related logs to keep
        self.agent_patterns = [
            r"agenthub\.",
            r"Successfully loaded agent",
            r"Assigned tools to agent",
            r"Tool execution",
            r"Agent execution",
            r"\[TOOL\]",
            r"Agent.*error",
            r"Tool.*error",
            r"ERROR",
            r"CRITICAL",
        ]

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log record to show only agent-related logs.

        Args:
            record: Log record to filter

        Returns:
            True if record should be kept, False if suppressed
        """
        message = record.getMessage()
        logger_name = record.name

        # Always keep errors and critical messages
        if record.levelno >= logging.ERROR:
            return True

        # Keep agent-related logs
        for pattern in self.agent_patterns:
            if re.search(pattern, message, re.IGNORECASE) or re.search(
                pattern, logger_name, re.IGNORECASE
            ):
                return True

        # Suppress everything else in quiet mode
        return False


class ToolExecutionFilter(logging.Filter):
    """Filter to enhance tool execution logs with context."""

    def __init__(self, name: str = ""):
        """Initialize tool execution filter.

        Args:
            name: Filter name
        """
        super().__init__(name)

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter and enhance tool execution logs.

        Args:
            record: Log record to filter

        Returns:
            True if record should be kept
        """
        # Add tool execution context if not present
        if hasattr(record, "msg") and "[TOOL]" in str(record.msg):
            if not hasattr(record, "tool_name"):
                # Try to extract tool name from message
                msg = str(record.msg)
                if "Multiplying" in msg:
                    record.tool_name = "multiply"
                elif "Adding" in msg:
                    record.tool_name = "add"
                elif "Subtracting" in msg:
                    record.tool_name = "subtract"
                elif "Dividing" in msg:
                    record.tool_name = "divide"
                elif "Searching" in msg:
                    record.tool_name = "web_search"

        return True


class PerformanceFilter(logging.Filter):
    """Filter to track performance-related logs."""

    def __init__(self, name: str = ""):
        """Initialize performance filter.

        Args:
            name: Filter name
        """
        super().__init__(name)
        self.performance_keywords = [
            "execution_time",
            "duration",
            "timeout",
            "performance",
            "slow",
            "fast",
            "latency",
        ]

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter performance-related logs.

        Args:
            record: Log record to filter

        Returns:
            True if record should be kept
        """
        message = record.getMessage().lower()

        # Keep performance-related logs
        for keyword in self.performance_keywords:
            if keyword in message:
                return True

        return True
