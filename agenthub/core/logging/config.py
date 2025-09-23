"""Centralized logging configuration for AgentHub."""

import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path

from ...config import get_config
from .filters import AgentLogFilter, HTTPLogFilter
from .formatters import ColorfulFormatter, StructuredFormatter
from .http_suppressor import suppress_mcp_http_logs


@dataclass
class LoggingSettings:
    """Logging configuration settings."""

    level: str = "INFO"
    format: str = "structured"  # "simple", "detailed", "structured"
    enable_file_logging: bool = False
    log_file: str | None = None
    quiet_mode: bool = False
    suppress_http: bool = True
    suppress_urllib3: bool = True
    enable_colors: bool = True
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5


class LoggingManager:
    """Centralized logging manager for AgentHub."""

    def __init__(self, settings: LoggingSettings | None = None):
        """Initialize logging manager.

        Args:
            settings: Logging settings, uses config if None
        """
        self.settings = settings or self._get_settings_from_config()
        self._setup_done = False

    def _get_settings_from_config(self) -> LoggingSettings:
        """Get logging settings from global config."""
        try:
            config = get_config()
            # Use existing config structure
            return LoggingSettings(
                level=getattr(config, "log_level", "INFO"),
                format="structured",
                enable_file_logging=os.getenv(
                    "AGENTHUB_ENABLE_FILE_LOGGING", "false"
                ).lower()
                == "true",
                log_file=os.getenv("AGENTHUB_LOG_FILE"),
                quiet_mode=getattr(config, "quiet_mode", False),
                suppress_http=getattr(config, "suppress_http_logs", True),
                suppress_urllib3=os.getenv("AGENTHUB_SUPPRESS_URLLIB3", "true").lower()
                == "true",
                enable_colors=os.getenv("AGENTHUB_ENABLE_COLORS", "true").lower()
                == "true",
            )
        except Exception:
            # Fallback to environment variables
            return LoggingSettings(
                level=os.getenv("AGENTHUB_LOG_LEVEL", "INFO"),
                format="structured",
                enable_file_logging=os.getenv(
                    "AGENTHUB_ENABLE_FILE_LOGGING", "false"
                ).lower()
                == "true",
                log_file=os.getenv("AGENTHUB_LOG_FILE"),
                quiet_mode=os.getenv("AGENTHUB_QUIET", "false").lower() == "true",
                suppress_http=os.getenv("AGENTHUB_SUPPRESS_HTTP", "true").lower()
                == "true",
                suppress_urllib3=os.getenv("AGENTHUB_SUPPRESS_URLLIB3", "true").lower()
                == "true",
                enable_colors=os.getenv("AGENTHUB_ENABLE_COLORS", "true").lower()
                == "true",
            )

    def setup_logging(self) -> None:
        """Set up logging configuration."""
        if self._setup_done:
            return

        # Convert string level to logging constant
        log_level = getattr(logging, self.settings.level.upper(), logging.INFO)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        # Clear existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Setup console handler
        self._setup_console_handler(log_level)

        # Setup file handler if enabled
        if self.settings.enable_file_logging and self.settings.log_file:
            self._setup_file_handler(log_level)

        # Configure specific loggers
        self._configure_library_loggers()

        # Suppress MCP HTTP logs if in quiet mode
        if self.settings.quiet_mode:
            suppress_mcp_http_logs()

        self._setup_done = True

    def _setup_console_handler(self, log_level: int) -> None:
        """Setup console handler with appropriate formatter."""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)

        # Choose formatter based on settings
        if self.settings.format == "structured":
            formatter: logging.Formatter = StructuredFormatter()
        elif self.settings.format == "detailed":
            formatter = ColorfulFormatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                enable_colors=self.settings.enable_colors,
            )
        else:  # simple
            formatter = ColorfulFormatter(
                (
                    "%(message)s"
                    if self.settings.quiet_mode
                    else "%(asctime)s - %(levelname)s - %(message)s"
                ),
                enable_colors=self.settings.enable_colors,
            )

        console_handler.setFormatter(formatter)

        # Add filters
        if self.settings.suppress_http:
            console_handler.addFilter(HTTPLogFilter())

        if self.settings.quiet_mode:
            console_handler.addFilter(AgentLogFilter())

        # Add to root logger
        logging.getLogger().addHandler(console_handler)

    def _setup_file_handler(self, log_level: int) -> None:
        """Setup file handler for logging."""
        from logging.handlers import RotatingFileHandler

        log_file = Path(self.settings.log_file or "agenthub.log")
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=self.settings.max_file_size,
            backupCount=self.settings.backup_count,
        )
        file_handler.setLevel(log_level)

        # Use structured formatter for file logging
        formatter = StructuredFormatter(enable_colors=False)
        file_handler.setFormatter(formatter)

        logging.getLogger().addHandler(file_handler)

    def _configure_library_loggers(self) -> None:
        """Configure logging levels for third-party libraries."""
        if self.settings.quiet_mode:
            # Suppress verbose logs but keep important agent logs
            logging.getLogger("agenthub").setLevel(logging.INFO)
            logging.getLogger("urllib3").setLevel(logging.ERROR)
            logging.getLogger("httpx").setLevel(logging.ERROR)
            logging.getLogger("httpcore").setLevel(logging.ERROR)
            logging.getLogger("requests").setLevel(logging.ERROR)
            logging.getLogger("mcp").setLevel(logging.ERROR)
            # Suppress MCP client HTTP logs
            logging.getLogger("mcp.client").setLevel(logging.ERROR)
            logging.getLogger("mcp.client.session").setLevel(logging.ERROR)
            logging.getLogger("mcp.client.stdio").setLevel(logging.ERROR)
            # Suppress specific MCP client loggers that generate HTTP logs
            logging.getLogger("mcp.client.session.client").setLevel(logging.ERROR)
            logging.getLogger("mcp.client.stdio.stdio_client").setLevel(logging.ERROR)
            # Suppress any logger that might generate HTTP request logs
            for logger_name in [
                "mcp",
                "mcp.client",
                "mcp.client.session",
                "mcp.client.stdio",
            ]:
                logger = logging.getLogger(logger_name)
                logger.setLevel(logging.ERROR)
                # Add a filter to suppress HTTP request logs
                logger.addFilter(HTTPLogFilter())
        else:
            # Set appropriate levels for common libraries
            logging.getLogger("urllib3").setLevel(logging.WARNING)
            logging.getLogger("httpx").setLevel(logging.WARNING)
            logging.getLogger("httpcore").setLevel(logging.WARNING)
            logging.getLogger("requests").setLevel(logging.WARNING)
            logging.getLogger("mcp").setLevel(logging.WARNING)
            # Reduce MCP client verbosity
            logging.getLogger("mcp.client").setLevel(logging.WARNING)
            logging.getLogger("mcp.client.session").setLevel(logging.WARNING)
            logging.getLogger("mcp.client.stdio").setLevel(logging.WARNING)

    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger instance with AgentHub configuration.

        Args:
            name: Logger name (will be prefixed with 'agenthub.')

        Returns:
            Configured logger instance
        """
        if not self._setup_done:
            self.setup_logging()

        return logging.getLogger(f"agenthub.{name}")

    def set_level(self, level: str) -> None:
        """Change logging level at runtime.

        Args:
            level: New logging level
        """
        log_level = getattr(logging, level.upper(), logging.INFO)
        logging.getLogger().setLevel(log_level)

        # Update all handlers
        for handler in logging.getLogger().handlers:
            handler.setLevel(log_level)

    def enable_quiet_mode(self, enabled: bool = True) -> None:
        """Enable or disable quiet mode.

        Args:
            enabled: Whether to enable quiet mode
        """
        self.settings.quiet_mode = enabled
        if self._setup_done:
            # Re-setup to apply changes
            self._setup_done = False
            self.setup_logging()


# Global logging manager instance
_logging_manager: LoggingManager | None = None


def get_logging_manager() -> LoggingManager:
    """Get the global logging manager instance."""
    global _logging_manager
    if _logging_manager is None:
        _logging_manager = LoggingManager()
    return _logging_manager


def setup_logging(settings: LoggingSettings | None = None) -> None:
    """Set up logging configuration.

    Args:
        settings: Optional logging settings
    """
    if settings:
        global _logging_manager
        _logging_manager = LoggingManager(settings)

    get_logging_manager().setup_logging()


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with AgentHub configuration.

    Args:
        name: Logger name

    Returns:
        Configured logger instance
    """
    return get_logging_manager().get_logger(name)


def set_quiet_mode(enabled: bool = True) -> None:
    """Enable or disable quiet mode for logging.

    Args:
        enabled: Whether to enable quiet mode
    """
    get_logging_manager().enable_quiet_mode(enabled)
