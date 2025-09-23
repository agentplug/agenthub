"""
Real-time log streaming for agent execution monitoring

Captures and buffers agent execution logs in real-time using subprocess.Popen
for non-blocking execution and immediate log availability.
"""

import subprocess
import threading
import time
from typing import Any


class LogStreamer:
    """
    Real-time log streaming from subprocess execution

    Captures stdout and stderr from agent subprocess execution in real-time,
    providing buffered access to logs for analysis and display.
    """

    def __init__(self, buffer_size: int = 1000) -> None:
        """
        Initialize Log Streamer

        Args:
            buffer_size: Maximum number of log lines to keep in buffer
        """
        self.buffer_size = buffer_size
        self.logs: list[str] = []
        self.process: subprocess.Popen[str] | None = None
        self.stdout_thread: threading.Thread | None = None
        self.stderr_thread: threading.Thread | None = None
        self.is_running = False
        self._lock = threading.Lock()

    def start_streaming(
        self, command: list[str], cwd: str | None = None
    ) -> subprocess.Popen[str]:
        """
        Start streaming logs from subprocess execution

        Args:
            command: Command to execute as list of strings
            cwd: Working directory for subprocess

        Returns:
            Subprocess Popen object for process management
        """
        if self.is_running:
            raise RuntimeError("LogStreamer is already running")

        # Start subprocess with real-time output capture
        self.process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
            cwd=cwd,
        )

        self.is_running = True

        # Start threads for real-time log capture
        self.stdout_thread = threading.Thread(
            target=self._stream_output,
            args=(self.process.stdout, "stdout"),
            daemon=True,
        )
        self.stderr_thread = threading.Thread(
            target=self._stream_output,
            args=(self.process.stderr, "stderr"),
            daemon=True,
        )

        self.stdout_thread.start()
        self.stderr_thread.start()

        return self.process

    def _stream_output(self, pipe: Any, stream_type: str) -> None:
        """
        Stream output from subprocess pipe in real-time

        Args:
            pipe: Subprocess stdout or stderr pipe
            stream_type: Type of stream ("stdout" or "stderr")
        """
        try:
            for line in iter(pipe.readline, ""):
                if line:
                    # Add timestamp and stream type to log line
                    timestamp = time.strftime("%H:%M:%S")
                    formatted_line = (
                        f"[{timestamp}] [{stream_type.upper()}] {line.rstrip()}"
                    )

                    with self._lock:
                        self.logs.append(formatted_line)
                        # Keep buffer size manageable
                        if len(self.logs) > self.buffer_size:
                            self.logs = self.logs[-self.buffer_size :]
        except Exception as e:
            print(f"Error streaming {stream_type}: {e}")
        finally:
            pipe.close()

    def get_logs(self, last_n: int | None = None) -> list[str]:
        """
        Get captured logs

        Args:
            last_n: Number of recent log lines to return (None for all)

        Returns:
            List of log lines
        """
        with self._lock:
            if last_n is None:
                return self.logs.copy()
            else:
                return self.logs[-last_n:] if self.logs else []

    def get_new_logs(self, since_index: int) -> list[str]:
        """
        Get new logs since a specific index

        Args:
            since_index: Index to get logs after

        Returns:
            List of new log lines
        """
        with self._lock:
            if since_index >= len(self.logs):
                return []
            return self.logs[since_index:]

    def wait_for_completion(self, timeout: int | None = None) -> int:
        """
        Wait for subprocess to complete

        Args:
            timeout: Optional timeout in seconds

        Returns:
            Process return code
        """
        if not self.process:
            raise RuntimeError("No process is running")

        try:
            return self.process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            self.process.kill()
            return -1
        finally:
            self.is_running = False

    def stop_streaming(self) -> None:
        """Stop log streaming and cleanup resources"""
        if self.process and self.is_running:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()

        self.is_running = False

        # Wait for threads to finish
        if self.stdout_thread and self.stdout_thread.is_alive():
            self.stdout_thread.join(timeout=1)
        if self.stderr_thread and self.stderr_thread.is_alive():
            self.stderr_thread.join(timeout=1)

    def clear_logs(self) -> None:
        """Clear all captured logs to prevent accumulation between calls"""
        with self._lock:
            self.logs.clear()

    def is_complete(self) -> bool:
        """
        Check if subprocess has completed

        Returns:
            True if process has finished, False otherwise
        """
        if not self.process:
            return True

        return self.process.poll() is not None

    def get_return_code(self) -> int | None:
        """
        Get subprocess return code

        Returns:
            Return code if process has finished, None otherwise
        """
        if not self.process:
            return None

        return self.process.poll()
