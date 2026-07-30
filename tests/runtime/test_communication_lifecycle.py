"""Lifecycle tests for CommunicationManager and ProcessManager.

Covers the startup race (server slower than the old fixed 0.5s sleep),
clean shutdown of the background server thread, idempotency, and the
ProcessManager context-manager form.
"""

import asyncio
import threading

from agenthub.runtime.process_manager.communication import CommunicationManager
from agenthub.runtime.process_manager.manager import ProcessManager

SERVER_THREAD_NAME = "agenthub-communication-server"


class FakeServer:
    """Minimal stand-in for CommunicationServer."""

    def __init__(self, start_delay: float = 0.0, start_ok: bool = True):
        self.is_running = False
        self.port = 8765
        self.host = "localhost"
        self.agent_sessions: dict = {}
        self._start_delay = start_delay
        self._start_ok = start_ok
        self.stop_calls = 0

    async def start(self) -> bool:
        await asyncio.sleep(self._start_delay)
        if self._start_ok:
            self.is_running = True
        return self._start_ok

    async def stop(self) -> None:
        self.stop_calls += 1
        self.is_running = False


def make_manager(server: FakeServer) -> CommunicationManager:
    manager = CommunicationManager(enabled=False)
    manager.server = server
    manager.enabled = True
    manager._initialized = True
    return manager


def server_threads() -> set[threading.Thread]:
    """Live server threads. Other suites may leak the singleton server's
    thread (they never call close()), so tests must assert relative to a
    baseline captured before they start their own server — never on the
    global set being empty."""
    return {t for t in threading.enumerate() if t.name == SERVER_THREAD_NAME}


class TestStartServer:
    def test_start_waits_for_slow_server(self):
        """Regression: a server slower than the old 0.5s sleep must still
        be reported as started (the old code returned False here)."""
        server = FakeServer(start_delay=1.0)
        manager = make_manager(server)
        try:
            assert manager.start_server_if_needed() is True
            assert server.is_running
        finally:
            manager.shutdown()

    def test_start_failure_reported(self):
        server = FakeServer(start_ok=False)
        manager = make_manager(server)
        try:
            assert manager.start_server_if_needed() is False
            assert not server.is_running
        finally:
            manager.shutdown()

    def test_start_is_noop_when_already_running(self):
        server = FakeServer()
        server.is_running = True
        manager = make_manager(server)
        assert manager.start_server_if_needed() is True
        # No thread was started for an already-running server.
        assert manager._server_thread is None


class TestShutdown:
    def test_shutdown_stops_server_and_joins_thread(self):
        server = FakeServer()
        manager = make_manager(server)
        baseline = server_threads()
        assert manager.start_server_if_needed() is True
        started = server_threads() - baseline
        assert len(started) == 1

        manager.shutdown()

        assert server.stop_calls == 1
        assert not server.is_running
        assert not any(thread.is_alive() for thread in started)
        assert manager._server_thread is None
        assert manager._server_loop is None

    def test_shutdown_is_idempotent(self):
        server = FakeServer()
        manager = make_manager(server)
        manager.start_server_if_needed()

        manager.shutdown()
        manager.shutdown()  # second call must be a safe no-op

        assert server.stop_calls == 1

    def test_shutdown_without_start_is_noop(self):
        manager = make_manager(FakeServer())
        manager.shutdown()  # nothing started; must not raise

    def test_disable_stops_running_server(self):
        server = FakeServer()
        manager = make_manager(server)
        baseline = server_threads()
        manager.start_server_if_needed()
        started = server_threads() - baseline

        manager.disable()

        assert not manager.enabled
        assert server.stop_calls == 1
        assert not any(thread.is_alive() for thread in started)

    def test_no_thread_leak_across_cycles(self):
        baseline = threading.active_count()
        for _ in range(10):
            server = FakeServer()
            manager = make_manager(server)
            manager.start_server_if_needed()
            manager.shutdown()
        assert threading.active_count() <= baseline + 1


class TestProcessManagerLifecycle:
    def test_context_manager_closes_communication(self):
        with ProcessManager(realtime_communication=False) as manager:
            assert manager is not None
        # No server started; exit must simply not raise.

    def test_close_shuts_down_started_server(self):
        manager = ProcessManager(realtime_communication=False)
        server = FakeServer()
        manager.communication_manager = make_manager(server)
        baseline = server_threads()
        manager.communication_manager.start_server_if_needed()
        started = server_threads() - baseline
        assert len(started) == 1

        manager.close()

        assert server.stop_calls == 1
        assert not any(thread.is_alive() for thread in started)

    def test_close_is_idempotent(self):
        manager = ProcessManager(realtime_communication=False)
        manager.close()
        manager.close()
