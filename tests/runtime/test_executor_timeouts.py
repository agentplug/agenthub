"""Timeout and process-cleanup tests for subprocess agent execution.

Covers the hang paths in Executor and LogStreamer: an agent that never
exits, an agent that spawns children holding the output pipes open, and
the bounded-streaming behavior of LogStreamer.
"""

import contextlib
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

from agenthub.runtime.process_manager.executor import Executor
from agenthub.runtime.process_manager.log_streaming import LogStreamer

# Agent that spawns a child (which would outlive a naive kill), records the
# child's pid, then hangs. cwd is the agent directory, so grandchild.pid
# lands there.
HANGING_AGENT = """\
import subprocess, sys, time

child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
with open("grandchild.pid", "w") as f:
    f.write(str(child.pid))
time.sleep(60)
"""

# Agent that echoes the requested method back as JSON, like agent_runner does.
ECHO_AGENT = """\
import json, sys

data = json.loads(sys.argv[1])
print(json.dumps({"echo": data["method"]}))
"""


class StubEnvironmentManager:
    """Environment manager stub: run agents with the test interpreter."""

    def get_python_executable(self, agent_path: str) -> str:
        return sys.executable

    def _get_agent_config(self, agent_path: str) -> dict:
        return {}


class RecordingCommManager:
    """Communication manager stub that records sent messages."""

    def __init__(self) -> None:
        self.messages: list[tuple[str, dict]] = []

    def is_available(self) -> bool:
        return True

    def send_message(self, agent_path: str, message: dict) -> None:
        self.messages.append((agent_path, message))


@pytest.fixture
def make_agent(tmp_path):
    def _make(script: str) -> str:
        (tmp_path / "agent.py").write_text(script)
        return str(tmp_path)

    return _make


def make_executor(timeout: int = 2) -> Executor:
    return Executor(
        timeout=timeout,
        use_dynamic_execution=False,
        environment_manager=StubEnvironmentManager(),
    )


def assert_process_dies(pid: int, deadline: float = 5.0) -> None:
    end = time.monotonic() + deadline
    while time.monotonic() < end:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return
        time.sleep(0.05)
    pytest.fail(f"process {pid} still alive after kill")


def kill_group(process: subprocess.Popen) -> None:
    if os.name == "posix":
        with contextlib.suppress(ProcessLookupError, PermissionError):
            os.killpg(process.pid, signal.SIGKILL)
    with contextlib.suppress(ProcessLookupError):
        process.kill()
    with contextlib.suppress(Exception):
        process.communicate(timeout=5)


class TestExecutorSubprocess:
    def test_success_result_parsed(self, make_agent):
        executor = make_executor()
        result = executor.execute(make_agent(ECHO_AGENT), "run", {})

        assert result.success
        assert result.data["echo"] == "run"

    def test_timeout_returns_error_promptly(self, make_agent):
        executor = make_executor(timeout=2)
        start = time.monotonic()
        result = executor.execute(make_agent(HANGING_AGENT), "run", {})
        elapsed = time.monotonic() - start

        assert not result.success
        assert "timed out" in str(result.error)
        # Returned near the 2s executor timeout, not the agent's 60s sleep.
        assert elapsed < 30

    @pytest.mark.skipif(os.name != "posix", reason="process groups are POSIX-only")
    def test_timeout_kills_agent_children_too(self, make_agent):
        executor = make_executor(timeout=2)
        agent_dir = make_agent(HANGING_AGENT)

        result = executor.execute(agent_dir, "run", {})

        assert not result.success
        grandchild_pid = int((Path(agent_dir) / "grandchild.pid").read_text())
        assert_process_dies(grandchild_pid)

    def test_streaming_timeout_without_websocket(self, make_agent):
        """Fallback streaming path (no WebSocket) must honor the timeout."""
        executor = make_executor(timeout=2)
        agent_dir = make_agent(HANGING_AGENT)
        streamer = LogStreamer(agent_dir, "run")

        start = time.monotonic()
        result = executor.execute(agent_dir, "run", {}, log_streamer=streamer)
        elapsed = time.monotonic() - start

        assert not result.success
        assert "timed out" in str(result.error).lower()
        assert elapsed < 30

    def test_streaming_timeout_with_websocket(self, make_agent):
        """Threaded streaming path must honor the timeout."""
        executor = make_executor(timeout=2)
        agent_dir = make_agent(HANGING_AGENT)
        streamer = LogStreamer(agent_dir, "run", RecordingCommManager())

        start = time.monotonic()
        result = executor.execute(agent_dir, "run", {}, log_streamer=streamer)
        elapsed = time.monotonic() - start

        assert not result.success
        assert "timed out" in str(result.error).lower()
        assert elapsed < 30


class TestLogStreamer:
    def test_stream_logs_raises_on_hung_process(self):
        process = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(60)"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        streamer = LogStreamer("ns/agent", "run", RecordingCommManager())
        try:
            with pytest.raises(subprocess.TimeoutExpired):
                streamer.stream_logs(process, timeout=1)
        finally:
            kill_group(process)

    def test_stream_logs_collects_and_sends(self):
        process = subprocess.Popen(
            [
                sys.executable,
                "-c",
                "import sys; print('hello'); print('oops', file=sys.stderr)",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        comm = RecordingCommManager()
        streamer = LogStreamer("ns/agent", "run", comm)
        try:
            stdout_lines, stderr_lines = streamer.stream_logs(process, timeout=15)
        finally:
            kill_group(process)

        assert "hello\n" in stdout_lines
        assert any("oops" in line for line in stderr_lines)
        streams = {message["stream"] for _, message in comm.messages}
        assert streams == {"stdout", "stderr"}

    def test_collect_output_timeout_propagates(self):
        process = subprocess.Popen(
            [sys.executable, "-c", "import time; time.sleep(60)"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        # No communication manager: stream_logs falls back to communicate().
        streamer = LogStreamer("ns/agent", "run")
        try:
            with pytest.raises(subprocess.TimeoutExpired):
                streamer.stream_logs(process, timeout=1)
        finally:
            kill_group(process)
