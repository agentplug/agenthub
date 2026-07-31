"""
Process manager orchestration module.

This module provides the main ProcessManager class that orchestrates
all subprocess execution components with a clean, modular architecture.
"""

import json
import logging
from pathlib import Path
from typing import Any

from agenthub.runtime.environment_manager import EnvironmentManager
from agenthub.runtime.process_manager.communication import CommunicationManager
from agenthub.runtime.process_manager.executor import Executor
from agenthub.runtime.process_manager.log_streaming import LogStreamer
from agenthub.runtime.process_manager.monitoring_adapter import MonitoringAdapter

logger = logging.getLogger(__name__)


class ProcessManager:
    """
    Manages agent subprocess execution with isolation and real-time monitoring.

    Orchestrates execution, communication, log streaming, and optional monitoring
    through a clean modular architecture.
    """

    def __init__(
        self,
        timeout: int = 300,
        use_dynamic_execution: bool = True,
        monitoring: bool = False,
        realtime_communication: bool = True,
    ) -> None:
        """
        Initialize the process manager.

        Args:
            timeout: Maximum execution time in seconds
            use_dynamic_execution: Whether to use dynamic execution (default: True)
            monitoring: Whether to enable real-time monitoring (default: False)
            realtime_communication: Whether to enable WebSocket communication
                (default: True)
        """
        self.timeout = timeout
        self.environment_manager = EnvironmentManager()

        # Initialize core components
        self.executor = Executor(
            timeout=timeout,
            use_dynamic_execution=use_dynamic_execution,
            environment_manager=self.environment_manager,
        )

        self.communication_manager = CommunicationManager(
            enabled=realtime_communication
        )

        self.monitoring_adapter = MonitoringAdapter(enabled=monitoring)

        # Backward compatibility attributes
        self.realtime_communication = self.communication_manager.enabled
        self.communication_server = self.communication_manager.server
        self._server_started = False

        # Note: Server is not started automatically during initialization
        # It will be started when needed (e.g., during agent execution)

        logger.info("✅ ProcessManager initialized with modular architecture")

    @property
    def use_dynamic_execution(self) -> bool:
        """Whether execution attempts dynamic in-process execution first."""
        return self.executor.use_dynamic_execution

    @use_dynamic_execution.setter
    def use_dynamic_execution(self, enabled: bool) -> None:
        # Must reach the executor: a plain attribute here silently diverges
        # from the executor's own flag, and agents then run outside their venv.
        self.executor.use_dynamic_execution = enabled

    def close(self) -> None:
        """Release resources: stop the communication server and its thread.

        Safe to call multiple times. The underlying CommunicationServer also
        registers an atexit hook as a last resort, but callers that create
        many ProcessManagers (or tests) should close explicitly or use the
        context-manager form.
        """
        self.communication_manager.shutdown()

    def __enter__(self) -> "ProcessManager":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def execute_agent(
        self,
        agent_path: str,
        method: str,
        parameters: dict[str, Any],
        manifest: dict[str, Any] | None = None,
        tool_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute an agent method in an isolated subprocess.

        Args:
            agent_path: Path to the agent directory
            method: Name of the method to execute
            parameters: Dictionary of method parameters
            manifest: Optional manifest data for dynamic execution
            tool_context: Optional tool context

        Returns:
            dict: Execution result with 'result' or 'error' key

        Raises:
            ValueError: If agent_path or method is invalid
            RuntimeError: If subprocess creation fails
        """
        # Validate inputs
        if not agent_path or not method:
            raise ValueError("agent_path and method are required")

        agent_dir = Path(agent_path)
        if not agent_dir.exists():
            raise ValueError(f"Agent directory does not exist: {agent_path}")

        # Determine agent script
        agent_script = self.executor._get_agent_script(agent_path)
        if not agent_script.exists():
            raise ValueError(f"Agent script not found: {agent_script}")

        # Register agent session if communication server is available
        session_registered = self._register_session(agent_path, method, parameters)

        try:
            # Create log streamer if communication is available
            log_streamer = None
            if self.communication_manager.is_available():
                log_streamer = LogStreamer(
                    agent_path=agent_path,
                    method=method,
                    communication_manager=self.communication_manager,
                )

            # Execute agent with monitoring if enabled
            if self.monitoring_adapter.is_available():
                result = self._execute_with_monitoring(
                    agent_path,
                    method,
                    parameters,
                    tool_context,
                    agent_script,
                    agent_dir,
                )
            else:
                # Execute agent using executor
                execution_result = self.executor.execute(
                    agent_path=agent_path,
                    method=method,
                    parameters=parameters,
                    manifest=manifest,
                    tool_context=tool_context,
                    log_streamer=log_streamer,
                )

                result = execution_result.to_dict()

            # Unregister session
            if session_registered:
                self.communication_manager.unregister_session(agent_path)

            return result

        except Exception:
            # Unregister session on error
            if session_registered:
                self.communication_manager.unregister_session(agent_path)
            raise

    def _register_session(
        self, agent_path: str, method: str, parameters: dict[str, Any]
    ) -> bool:
        """
        Register agent session with communication server.

        Args:
            agent_path: Path to agent
            method: Method name
            parameters: Method parameters

        Returns:
            bool: True if session registered successfully
        """
        import time

        if not self.communication_manager.is_available():
            # Try to start server if not running
            self.communication_manager.start_server_if_needed()

        if self.communication_manager.is_available():
            session_data = {
                "method": method,
                "parameters": parameters,
                "start_time": time.time(),
            }
            return self.communication_manager.register_session(agent_path, session_data)

        return False

    def _execute_with_monitoring(
        self,
        agent_path: str,
        method: str,
        parameters: dict[str, Any],
        tool_context: dict[str, Any] | None,
        agent_script: Path,
        agent_dir: Path,
    ) -> dict[str, Any]:
        """
        Execute agent with real-time monitoring.

        Args:
            agent_path: Path to agent
            method: Method name
            parameters: Method parameters
            tool_context: Optional tool context
            agent_script: Path to agent script
            agent_dir: Agent directory

        Returns:
            dict: Execution result
        """
        # Prepare execution data
        execution_data = {"method": method, "parameters": parameters}
        if tool_context:
            execution_data["tool_context"] = tool_context

        # Prepare command
        try:
            python_executable = self.environment_manager.get_python_executable(
                agent_path
            )
        except Exception:
            import sys

            python_executable = sys.executable

        command = [python_executable, str(agent_script), json.dumps(execution_data)]

        # Execute with monitoring
        return self.monitoring_adapter.execute_with_monitoring(
            command=command,
            agent_dir=agent_dir,
            timeout=self.timeout,
        )

    def set_monitoring(self, enabled: bool) -> None:
        """
        Enable or disable monitoring dynamically.

        Args:
            enabled: Whether to enable monitoring
        """
        if enabled:
            self.monitoring_adapter.enable()
        else:
            self.monitoring_adapter.disable()

    def set_realtime_communication(self, enabled: bool) -> None:
        """
        Enable or disable real-time communication dynamically.

        Args:
            enabled: Whether to enable real-time communication
        """
        if enabled:
            self.communication_manager.enable()
            self.realtime_communication = True
            self.communication_server = self.communication_manager.server
            # Note: Server is not started automatically, only when needed
        else:
            self.communication_manager.disable()
            self.realtime_communication = False
            self.communication_server = None
            self._server_started = False

    async def _ensure_communication_server(self) -> bool:
        """
        Ensure communication server is running (backward compatibility).

        Returns:
            bool: True if server available, False if fallback needed
        """
        return await self.communication_manager.ensure_server_running()

    def get_communication_status(self) -> dict[str, Any]:
        """
        Get communication server status.

        Returns:
            dict: Status information
        """
        # Handle disabled case first
        if not self.realtime_communication:
            return {"enabled": False, "reason": "disabled"}

        # Handle backward compatibility when server reference was manually cleared
        if self.communication_server is None:
            return {"enabled": False, "reason": "not_initialized"}

        status = self.communication_manager.get_status()

        # Backward compatibility: ensure 'enabled' field exists
        if "enabled" not in status:
            status["enabled"] = (
                self.realtime_communication and self.communication_server is not None
            )

        return status

    def log_communication_status(self) -> None:
        """Log the current communication status for debugging."""
        self.communication_manager.log_status()

    def validate_agent_structure(
        self, agent_path: str, require_venv: bool = True
    ) -> bool:
        """
        Validate that an agent has the required structure.

        Args:
            agent_path: Path to the agent directory
            require_venv: Whether to require virtual environment (default: True)

        Returns:
            bool: True if agent structure is valid
        """
        return self.executor.validate_agent_structure(agent_path, require_venv)
