"""
Process execution module for agent subprocess management.

This module handles the core execution logic for running agents in isolated
subprocesses or via dynamic in-process execution.
"""

import json
import logging
import os
import signal
import subprocess
import time
from pathlib import Path
from typing import Any

from agenthub.core.agents.dynamic_executor import DynamicAgentExecutor
from agenthub.runtime.environment_manager import EnvironmentManager

logger = logging.getLogger(__name__)


class ExecutionResult:
    """Result from agent execution."""

    def __init__(
        self,
        success: bool,
        data: dict[str, Any] | None = None,
        error: str | None = None,
        execution_time: float = 0.0,
        return_code: int = 0,
    ):
        """
        Initialize execution result.

        Args:
            success: Whether execution was successful
            data: Result data (if successful)
            error: Error message (if failed)
            execution_time: Execution duration in seconds
            return_code: Process return code
        """
        self.success = success
        self.data = data or {}
        self.error = error
        self.execution_time = execution_time
        self.return_code = return_code

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        if self.success:
            result = self.data.copy()
            result["execution_time"] = self.execution_time
            return result
        else:
            return {
                "error": self.error,
                "execution_time": self.execution_time,
                "return_code": self.return_code,
            }


class Executor:
    """
    Process executor for running agents in subprocesses.

    Handles both subprocess execution and dynamic in-process execution,
    with support for result parsing, timeout handling, and error management.
    """

    def __init__(
        self,
        timeout: int = 300,
        use_dynamic_execution: bool = True,
        environment_manager: EnvironmentManager | None = None,
    ):
        """
        Initialize executor.

        Args:
            timeout: Maximum execution time in seconds
            use_dynamic_execution: Whether to use dynamic execution (default: True)
            environment_manager: Environment manager for venv handling
        """
        self.timeout = timeout
        self.use_dynamic_execution = use_dynamic_execution
        self.environment_manager = environment_manager or EnvironmentManager()
        self.dynamic_executor = (
            DynamicAgentExecutor() if use_dynamic_execution else None
        )

    def execute(
        self,
        agent_path: str,
        method: str,
        parameters: dict[str, Any],
        manifest: dict[str, Any] | None = None,
        tool_context: dict[str, Any] | None = None,
        log_streamer: Any = None,
    ) -> ExecutionResult:
        """
        Execute agent method.

        Args:
            agent_path: Path to the agent directory
            method: Name of the method to execute
            parameters: Dictionary of method parameters
            manifest: Optional manifest data for dynamic execution
            tool_context: Optional tool context
            log_streamer: Optional log streamer for real-time output

        Returns:
            ExecutionResult: Execution result
        """
        # Try dynamic execution first if enabled
        if self.use_dynamic_execution and self.dynamic_executor:
            try:
                result = self._execute_dynamic(agent_path, method, parameters, manifest)
                if result.success:
                    return result
                else:
                    logger.warning(
                        f"Dynamic execution failed: {result.error}, "
                        f"falling back to subprocess"
                    )
            except Exception as e:
                logger.warning(
                    f"Dynamic execution error: {e}, falling back to subprocess"
                )

        # Fall back to subprocess execution
        return self._execute_subprocess(
            agent_path, method, parameters, tool_context, log_streamer
        )

    def _execute_dynamic(
        self,
        agent_path: str,
        method: str,
        parameters: dict[str, Any],
        manifest: dict[str, Any] | None,
    ) -> ExecutionResult:
        """
        Execute agent using dynamic in-process execution.

        Args:
            agent_path: Path to the agent directory
            method: Method name to execute
            parameters: Method parameters
            manifest: Optional manifest data

        Returns:
            ExecutionResult: Execution result
        """
        start_time = time.time()
        if self.dynamic_executor is None:
            return ExecutionResult(success=False, error="Dynamic execution is disabled")
        try:
            result = self.dynamic_executor.execute_agent_method(
                agent_path, method, parameters, manifest
            )
            execution_time = time.time() - start_time

            # execute_agent_method always returns a dict with either a
            # payload or an "error" key
            if "error" in result:
                return ExecutionResult(
                    success=False,
                    error=result["error"],
                    execution_time=execution_time,
                )
            return ExecutionResult(
                success=True, data=result, execution_time=execution_time
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                error=f"Dynamic execution failed: {e}",
                execution_time=execution_time,
            )

    def _execute_subprocess(
        self,
        agent_path: str,
        method: str,
        parameters: dict[str, Any],
        tool_context: dict[str, Any] | None,
        log_streamer: Any = None,
    ) -> ExecutionResult:
        """
        Execute agent in subprocess.

        Args:
            agent_path: Path to the agent directory
            method: Method name to execute
            parameters: Method parameters
            tool_context: Optional tool context
            log_streamer: Optional log streamer

        Returns:
            ExecutionResult: Execution result
        """
        agent_dir = Path(agent_path)
        agent_script = self._get_agent_script(agent_path)

        # Prepare execution data
        execution_data = {"method": method, "parameters": parameters}
        if tool_context:
            execution_data["tool_context"] = tool_context

        try:
            # Get Python executable
            python_executable = self.environment_manager.get_python_executable(
                agent_path
            )

            # Check for Dana script with Python (not supported)
            if agent_script.suffix == ".na" and "python" in python_executable.lower():
                return ExecutionResult(
                    success=False,
                    error="Dana agent execution not supported",
                )

            start_time = time.time()

            # Execute with or without log streaming
            if log_streamer:
                result = self._execute_with_streaming(
                    python_executable,
                    agent_script,
                    execution_data,
                    agent_dir,
                    log_streamer,
                )
            else:
                result = self._execute_simple(
                    python_executable, agent_script, execution_data, agent_dir
                )

            execution_time = time.time() - start_time

            # Parse result
            return self._parse_result(result, execution_time)

        except subprocess.TimeoutExpired:
            return ExecutionResult(
                success=False,
                error=f"Agent execution timed out after {self.timeout} seconds",
            )
        except FileNotFoundError as e:
            return ExecutionResult(success=False, error=f"Failed to execute agent: {e}")
        except Exception as e:
            logger.error(f"Unexpected error executing agent: {e}")
            return ExecutionResult(
                success=False, error=f"Unexpected execution error: {e}"
            )

    def _execute_simple(
        self,
        python_executable: str,
        agent_script: Path,
        execution_data: dict[str, Any],
        agent_dir: Path,
    ) -> subprocess.CompletedProcess:
        """Execute subprocess without log streaming."""
        logger.info(f"Executing agent without log streaming: {agent_script.name}")

        process = subprocess.Popen(
            [python_executable, str(agent_script), json.dumps(execution_data)],
            cwd=str(agent_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        try:
            stdout, stderr = process.communicate(timeout=self.timeout)
        except subprocess.TimeoutExpired:
            self._kill_process_tree(process)
            raise
        return subprocess.CompletedProcess(
            process.args, process.returncode, stdout, stderr
        )

    def _execute_with_streaming(
        self,
        python_executable: str,
        agent_script: Path,
        execution_data: dict[str, Any],
        agent_dir: Path,
        log_streamer: Any,
    ) -> subprocess.CompletedProcess:
        """Execute subprocess with real-time log streaming."""
        logger.info(f"Executing agent with log streaming: {agent_script.name}")

        logger.debug(
            "Agent command: %s %s %s",
            python_executable,
            agent_script,
            json.dumps(execution_data),
        )
        process = subprocess.Popen(
            [python_executable, str(agent_script), json.dumps(execution_data)],
            cwd=str(agent_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,  # Line buffered
            start_new_session=True,
        )

        # One deadline covers both streaming and process exit: streaming ends
        # at pipe EOF, which normally coincides with the process exiting.
        deadline = time.monotonic() + self.timeout
        try:
            stdout_lines, stderr_lines = log_streamer.stream_logs(
                process, timeout=self.timeout
            )
            process.wait(timeout=max(deadline - time.monotonic(), 1.0))
            stdout = "".join(stdout_lines)
            stderr = "".join(stderr_lines)
            return subprocess.CompletedProcess(
                process.args, process.returncode, stdout, stderr
            )
        except subprocess.TimeoutExpired:
            self._kill_process_tree(process)
            return subprocess.CompletedProcess(
                process.args,
                -1,
                "",
                f"Process timed out after {self.timeout} seconds",
            )

    def _kill_process_tree(self, process: subprocess.Popen) -> None:
        """Kill the agent's process group and release its pipes.

        Agents may spawn their own children; killing only the direct child
        would leak them and let them hold the output pipes open. The process
        was started with ``start_new_session=True``, so its pid is also its
        process group id.
        """
        if os.name == "posix":
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
        try:
            process.kill()
        except ProcessLookupError:
            pass
        # Reap the child and drain/close pipes so no reader stays blocked.
        try:
            process.communicate(timeout=5)
        except (subprocess.TimeoutExpired, ValueError):
            for stream in (process.stdout, process.stderr):
                if stream is not None:
                    stream.close()

    def _parse_result(
        self, result: subprocess.CompletedProcess, execution_time: float
    ) -> ExecutionResult:
        """
        Parse subprocess result.

        Args:
            result: Subprocess completed process
            execution_time: Execution duration

        Returns:
            ExecutionResult: Parsed result
        """
        if result.returncode == 0:
            try:
                parsed_result = json.loads(result.stdout)
                if isinstance(parsed_result, dict):
                    return ExecutionResult(
                        success=True,
                        data=parsed_result,
                        execution_time=execution_time,
                        return_code=0,
                    )
                else:
                    return ExecutionResult(
                        success=False,
                        error="Agent returned non-dictionary result",
                        execution_time=execution_time,
                        return_code=0,
                    )
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse agent output: {result.stdout}")
                return ExecutionResult(
                    success=False,
                    error=f"Invalid JSON response from agent: {e}",
                    execution_time=execution_time,
                    return_code=0,
                )
        else:
            # Agent execution failed
            error_msg = result.stderr or result.stdout or "Unknown error"
            return ExecutionResult(
                success=False,
                error=f"Agent execution failed: {error_msg}",
                execution_time=execution_time,
                return_code=result.returncode,
            )

    def _get_agent_script(self, agent_path: str) -> Path:
        """
        Get the agent script path based on agent configuration.

        Supports both agent.py (Python) and agent.na (Dana).

        Args:
            agent_path: Path to the agent directory

        Returns:
            Path to the agent script file
        """
        agent_dir = Path(agent_path)

        # Check agent configuration
        agent_config = self.environment_manager._get_agent_config(agent_path)

        if agent_config and "dana_version" in agent_config:
            # Use Dana script
            agent_script = agent_dir / "agent.na"
            logger.info(f"Using Dana script for agent: {agent_path}")
        else:
            # Default to Python script
            agent_script = agent_dir / "agent.py"
            logger.info(f"Using Python script for agent: {agent_path}")

        return agent_script

    def validate_agent_structure(
        self, agent_path: str, require_venv: bool = True
    ) -> bool:
        """
        Validate that an agent has the required structure.

        Args:
            agent_path: Path to the agent directory
            require_venv: Whether to require virtual environment (default: True)

        Returns:
            True if agent structure is valid
        """
        agent_dir = Path(agent_path)

        # Check agent configuration
        agent_config = self.environment_manager._get_agent_config(agent_path)

        # Always require agent.yaml or agent.yml
        agent_yaml_exists = (agent_dir / "agent.yaml").exists()
        agent_yml_exists = (agent_dir / "agent.yml").exists()

        if not agent_yaml_exists and not agent_yml_exists:
            logger.debug("Missing required file: agent.yaml (or agent.yml)")
            return False

        # Check for agent script file
        agent_py_exists = (agent_dir / "agent.py").exists()
        agent_na_exists = (agent_dir / "agent.na").exists()

        if agent_config and "dana_version" in agent_config:
            # For Dana agents, require agent.na
            if not agent_na_exists:
                logger.debug("Missing required file: agent.na (Dana agent)")
                return False
        else:
            # For Python agents, require agent.py
            if not agent_py_exists:
                logger.debug("Missing required file: agent.py (Python agent)")
                return False

        # Ensure only one agent script exists
        if agent_py_exists and agent_na_exists:
            logger.debug("Both agent.py and agent.na found - only one should exist")
            return False

        # Check virtual environment only if required
        if require_venv:
            venv_path = self.environment_manager.get_agent_venv_path(agent_path)
            if not venv_path.exists():
                logger.debug(f"Missing virtual environment: {venv_path}")
                return False

            try:
                self.environment_manager.get_python_executable(agent_path)
                return True
            except RuntimeError:
                logger.debug("Python executable not found in virtual environment")
                return False

        return True
