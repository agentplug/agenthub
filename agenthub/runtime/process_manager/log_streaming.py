"""
Log streaming module for real-time subprocess output capture.

This module handles streaming stdout/stderr from agent subprocesses,
filtering noise, and sending logs via WebSocket communication.
"""

import logging
import subprocess
import threading
import time
from typing import Any

logger = logging.getLogger(__name__)


class LogStreamer:
    """
    Real-time log streaming from subprocess with filtering.

    Captures stdout and stderr from agent subprocess execution,
    filters noise, and optionally sends logs via WebSocket.
    """

    def __init__(
        self,
        agent_path: str,
        method: str,
        communication_manager: Any = None,
    ):
        """
        Initialize log streamer.

        Args:
            agent_path: Path to the agent
            method: Method being executed
            communication_manager: Optional communication manager for WebSocket
        """
        self.agent_path = agent_path
        self.method = method
        self.communication_manager = communication_manager
        self.stdout_lines: list[str] = []
        self.stderr_lines: list[str] = []

    def stream_logs(self, process: subprocess.Popen) -> tuple[list[str], list[str]]:
        """
        Stream logs from subprocess in real-time.

        Args:
            process: The subprocess running the agent

        Returns:
            tuple: (stdout_lines, stderr_lines) collected during streaming
        """
        if (
            not self.communication_manager
            or not self.communication_manager.is_available()
        ):
            # No WebSocket available, just collect output
            return self._collect_output(process)

        # Start log streaming threads
        stdout_thread = threading.Thread(target=self._stream_stdout, args=(process,))
        stderr_thread = threading.Thread(target=self._stream_stderr, args=(process,))

        stdout_thread.start()
        stderr_thread.start()

        logger.info(
            f"📡 Started real-time log streaming for {self.agent_path}.{self.method}"
        )

        # Wait for threads to complete
        stdout_thread.join()
        stderr_thread.join()

        return (self.stdout_lines, self.stderr_lines)

    def _collect_output(self, process: subprocess.Popen) -> tuple[list[str], list[str]]:
        """Collect output without streaming (fallback)."""
        stdout, stderr = process.communicate()
        stdout_lines = stdout.splitlines(keepends=True) if stdout else []
        stderr_lines = stderr.splitlines(keepends=True) if stderr else []
        return (stdout_lines, stderr_lines)

    def _stream_stdout(self, process: subprocess.Popen) -> None:
        """Stream stdout logs in separate thread."""
        try:
            for line in iter(process.stdout.readline, ""):
                if line:
                    # Collect output for final result
                    self.stdout_lines.append(line)

                    # Send log message via WebSocket
                    self._send_log("stdout", line)

                    # Display clean logs
                    self._display_log(line)
        except Exception as e:
            logger.debug(f"Error streaming stdout: {e}")

    def _stream_stderr(self, process: subprocess.Popen) -> None:
        """Stream stderr logs in separate thread."""
        try:
            for line in iter(process.stderr.readline, ""):
                if line:
                    # Collect output for final result
                    self.stderr_lines.append(line)

                    # Send log message via WebSocket
                    self._send_log("stderr", line)

                    # Display clean logs
                    self._display_log(line)
        except Exception as e:
            logger.debug(f"Error streaming stderr: {e}")

    def _send_log(self, stream: str, message: str) -> None:
        """
        Send log message via WebSocket.

        Args:
            stream: Stream name ("stdout" or "stderr")
            message: Log message
        """
        if not self.communication_manager:
            return

        log_message = {
            "type": "agent_log",
            "agent_path": self.agent_path,
            "method": self.method,
            "stream": stream,
            "message": message.strip(),
            "timestamp": time.time(),
        }

        self.communication_manager.send_message(self.agent_path, log_message)

    def _display_log(self, log_line: str) -> None:
        """
        Display log in console (filtered).

        Args:
            log_line: Log line to display
        """
        stripped = log_line.strip()
        if stripped and not self._is_noise_log(stripped):
            # Extract message: "LEVEL:logger:message" -> "message"
            parts = stripped.split(":", 2)
            message = parts[2] if len(parts) > 2 else stripped
            if message:
                agent_name = self.agent_path.split("/")[-1]
                logger.info(f"🤖 {agent_name}: {message}")

    def _is_noise_log(self, log_line: str) -> bool:
        """
        Check if a log line is noise that should be filtered out.

        Args:
            log_line: The log line to check

        Returns:
            bool: True if this is noise, False if it should be displayed
        """
        # Filter by logger name (Python logging format: "LEVEL:logger.name:message")
        if ":" in log_line:
            parts = log_line.split(":", 2)
            if len(parts) >= 2:
                logger_name = parts[1].strip()

                # Filter internal research agent loggers
                internals = [
                    "research_agent.core.research",
                    "research_agent.core.tools.agenthub_mcp_client",
                ]

                for internal in internals:
                    if logger_name.startswith(internal):
                        return True

        # Filter common noise patterns
        noise = [
            'File "/',
            "Traceback",
            "DEBUG:",
            "ERROR:",
            "HTTP Request:",
            "httpx:",
            "pydantic",
        ]

        for pattern in noise:
            if pattern in log_line:
                return True
        return False

    def get_collected_logs(self) -> tuple[list[str], list[str]]:
        """
        Get all collected logs.

        Returns:
            tuple: (stdout_lines, stderr_lines)
        """
        return (self.stdout_lines, self.stderr_lines)
