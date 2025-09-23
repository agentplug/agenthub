"""Custom log formatters for AgentHub."""

import json
import logging
from datetime import datetime


class ColorfulFormatter(logging.Formatter):
    """Colorful formatter for agent logs with enhanced styling."""

    # ANSI color codes
    COLORS = {
        "RESET": "\033[0m",
        "BOLD": "\033[1m",
        "DIM": "\033[2m",
        "BLACK": "\033[30m",
        "RED": "\033[31m",
        "GREEN": "\033[32m",
        "YELLOW": "\033[33m",
        "BLUE": "\033[34m",
        "MAGENTA": "\033[35m",
        "CYAN": "\033[36m",
        "WHITE": "\033[37m",
    }

    LEVEL_COLORS = {
        "DEBUG": COLORS["DIM"],
        "INFO": COLORS["GREEN"],
        "WARNING": COLORS["YELLOW"],
        "ERROR": COLORS["RED"],
        "CRITICAL": COLORS["RED"] + COLORS["BOLD"],
    }

    def __init__(self, fmt: str | None = None, enable_colors: bool = True):
        """Initialize colorful formatter.

        Args:
            fmt: Log format string
            enable_colors: Whether to enable colors
        """
        super().__init__(fmt)
        self.enable_colors = enable_colors

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        # Get the original message
        message = super().format(record)

        if not self.enable_colors:
            return message

        # Add colors to specific log messages
        if hasattr(record, "msg") and record.msg:
            msg = str(record.msg)

            # Agent loading success
            if "Successfully loaded agent" in msg:
                if "with" in msg and "tools" in msg:
                    # Extract tool count
                    try:
                        tool_part = msg.split("with")[1].split("tools")[0].strip()
                        tool_count = int(tool_part)
                        if tool_count > 0:
                            message = message.replace(
                                "Successfully loaded agent",
                                f"{self.COLORS['GREEN']}✅ Successfully loaded agent"
                                f"{self.COLORS['RESET']}",
                            )
                            message = message.replace(
                                f"with {tool_count} tools",
                                f"{self.COLORS['CYAN']}with {tool_count} tools"
                                f"{self.COLORS['RESET']}",
                            )
                    except (ValueError, IndexError):
                        message = message.replace(
                            "Successfully loaded agent",
                            f"{self.COLORS['GREEN']}✅ Successfully loaded agent"
                            f"{self.COLORS['RESET']}",
                        )
                else:
                    message = message.replace(
                        "Successfully loaded agent",
                        f"{self.COLORS['GREEN']}✅ Successfully loaded agent"
                        f"{self.COLORS['RESET']}",
                    )

            # Tool execution
            elif "[TOOL]" in msg:
                message = message.replace(
                    "[TOOL]", f"{self.COLORS['BLUE']}🔧 [TOOL]{self.COLORS['RESET']}"
                )

            # Error messages
            elif "error" in msg.lower() or "failed" in msg.lower():
                message = message.replace(
                    "error", f"{self.COLORS['RED']}error{self.COLORS['RESET']}"
                )
                message = message.replace(
                    "failed", f"{self.COLORS['RED']}failed{self.COLORS['RESET']}"
                )

            # Success messages
            elif "success" in msg.lower() or "completed" in msg.lower():
                message = message.replace(
                    "success", f"{self.COLORS['GREEN']}success{self.COLORS['RESET']}"
                )
                message = message.replace(
                    "completed",
                    f"{self.COLORS['GREEN']}completed{self.COLORS['RESET']}",
                )

        # Add level colors
        level_color = self.LEVEL_COLORS.get(record.levelname, "")
        if level_color:
            message = message.replace(
                record.levelname,
                f"{level_color}{record.levelname}{self.COLORS['RESET']}",
            )

        return message


class StructuredFormatter(logging.Formatter):
    """Structured formatter for JSON logging."""

    def __init__(self, enable_colors: bool = False):
        """Initialize structured formatter.

        Args:
            enable_colors: Whether to enable colors (ignored for JSON)
        """
        super().__init__()
        self.enable_colors = enable_colors

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as structured JSON."""
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add extra fields if present
        if hasattr(record, "agent_id"):
            log_entry["agent_id"] = record.agent_id
        if hasattr(record, "tool_name"):
            log_entry["tool_name"] = record.tool_name
        if hasattr(record, "execution_time"):
            log_entry["execution_time"] = record.execution_time
        if hasattr(record, "session_id"):
            log_entry["session_id"] = record.session_id

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, default=str)


class AgentFormatter(logging.Formatter):
    """Specialized formatter for agent-related logs."""

    def __init__(self, enable_colors: bool = True):
        """Initialize agent formatter.

        Args:
            enable_colors: Whether to enable colors
        """
        super().__init__()
        self.enable_colors = enable_colors
        self.colors = ColorfulFormatter.COLORS if enable_colors else {}

    def format(self, record: logging.LogRecord) -> str:
        """Format agent log record with special handling."""
        # Extract agent context
        agent_id = getattr(record, "agent_id", "unknown")
        tool_name = getattr(record, "tool_name", None)
        execution_time = getattr(record, "execution_time", None)

        # Build context string
        context_parts = [f"agent={agent_id}"]
        if tool_name:
            context_parts.append(f"tool={tool_name}")
        if execution_time is not None:
            context_parts.append(f"time={execution_time:.3f}s")

        context = f"[{' '.join(context_parts)}]"

        # Format message
        if self.enable_colors:
            context = f"{self.colors['CYAN']}{context}{self.colors['RESET']}"

        return f"{record.levelname:8} {context} {record.getMessage()}"
