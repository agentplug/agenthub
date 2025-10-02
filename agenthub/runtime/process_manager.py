"""Process manager for executing agents in isolated subprocesses with monitoring."""

import json
import logging
import subprocess
import time
from pathlib import Path
from typing import Any

from agenthub.core.agents.dynamic_executor import DynamicAgentExecutor
from agenthub.runtime.environment_manager import EnvironmentManager

logger = logging.getLogger(__name__)


class ProcessManager:
    """Manages agent subprocess execution with isolation and real-time monitoring."""

    def __init__(
        self,
        timeout: int = 300,
        use_dynamic_execution: bool = True,
        monitoring: bool = False,
    ) -> None:
        """
        Initialize the process manager.

        Args:
            timeout: Maximum execution time in seconds
            use_dynamic_execution: Whether to use dynamic execution (default: True)
            monitoring: Whether to enable real-time monitoring (default: False)
        """
        self.timeout = timeout
        self.environment_manager = EnvironmentManager()
        self.use_dynamic_execution = use_dynamic_execution
        self.dynamic_executor = (
            DynamicAgentExecutor() if use_dynamic_execution else None
        )
        self.monitoring = monitoring
        # Initialize monitoring components as None initially
        self.core_llm: Any = None
        self.llm_analyzer: Any = None
        self.log_streamer: Any = None
        self.terminal_display: Any = None

        # Initialize monitoring components if enabled
        if self.monitoring:
            try:
                from agenthub.core.llm.llm_service import get_shared_llm_service
                from agenthub.monitoring.llm_analyzer import LLMAnalyzer
                from agenthub.monitoring.log_streamer import LogStreamer
                from agenthub.monitoring.terminal_display import TerminalDisplay

                self.core_llm = get_shared_llm_service()
                self.llm_analyzer = LLMAnalyzer(self.core_llm)
                self.log_streamer = LogStreamer()
                self.terminal_display = TerminalDisplay()
                logger.info("Real-time monitoring components initialized")
            except ImportError as e:
                logger.warning(f"Monitoring components not available: {e}")
                self.monitoring = False
        # Monitoring components are already initialized as None above

    def set_monitoring(self, enabled: bool) -> None:
        """Enable or disable monitoring dynamically."""
        if enabled and not self.monitoring:
            try:
                from agenthub.core.llm.llm_service import get_shared_llm_service
                from agenthub.monitoring.llm_analyzer import LLMAnalyzer
                from agenthub.monitoring.log_streamer import LogStreamer
                from agenthub.monitoring.terminal_display import TerminalDisplay

                self.core_llm = get_shared_llm_service()
                self.llm_analyzer = LLMAnalyzer(self.core_llm)
                self.log_streamer = LogStreamer()
                self.terminal_display = TerminalDisplay()
                self.monitoring = True
                logger.info("Real-time monitoring enabled")
            except ImportError as e:
                logger.warning(f"Monitoring components not available: {e}")
                self.monitoring = False
        elif not enabled and self.monitoring:
            self.monitoring = False
            # Reset monitoring components to None
            self.core_llm = None
            self.llm_analyzer = None
            self.log_streamer = None
            self.terminal_display = None
            logger.info("Real-time monitoring disabled")

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

        Returns:
            dict: Execution result with 'result' or 'error' key

        Raises:
            ValueError: If agent_path or method is invalid
            RuntimeError: If subprocess creation fails
        """
        if not agent_path or not method:
            raise ValueError("agent_path and method are required")

        agent_dir = Path(agent_path)
        if not agent_dir.exists():
            raise ValueError(f"Agent directory does not exist: {agent_path}")

        # Determine agent script based on configuration
        agent_script = self._get_agent_script(agent_path)
        if not agent_script.exists():
            raise ValueError(f"Agent script not found: {agent_script}")

        # Try dynamic execution first if enabled
        if self.use_dynamic_execution and self.dynamic_executor:
            try:
                start_time = time.time()
                result = self.dynamic_executor.execute_agent_method(
                    agent_path, method, parameters, manifest
                )
                execution_time = time.time() - start_time
                result["execution_time"] = execution_time
                return result
            except Exception as e:
                logger.warning(
                    f"Dynamic execution failed, falling back to subprocess: {e}"
                )

        # Choose execution method based on monitoring setting
        if self.monitoring:
            return self._execute_with_monitoring(
                agent_path, method, parameters, tool_context, agent_script, agent_dir
            )
        else:
            return self._execute_without_monitoring(
                agent_path, method, parameters, tool_context, agent_script, agent_dir
            )

    def _execute_without_monitoring(
        self,
        agent_path: str,
        method: str,
        parameters: dict[str, Any],
        tool_context: dict[str, Any] | None,
        agent_script: Path,
        agent_dir: Path,
    ) -> dict[str, Any]:
        """Execute agent without monitoring (original subprocess execution)."""
        # Prepare execution data with tool context if available
        execution_data = {"method": method, "parameters": parameters}
        if tool_context:
            execution_data["tool_context"] = tool_context

        try:
            # Get Python executable for this agent's virtual environment
            python_executable = self.environment_manager.get_python_executable(
                agent_path
            )

            # Check if this is a Dana script being executed with Python
            if agent_script.suffix == ".na" and "python" in python_executable.lower():
                return {
                    "error": "Dana agent execution not supported",
                    "message": (
                        "Dana script cannot be executed with Python. "
                        "Dana runtime is required but not available in venv."
                    ),
                    "suggestion": (
                        "Install Dana runtime or use a Python-based agent instead."
                    ),
                }

            # Execute agent in subprocess
            start_time = time.time()
            logger.info(
                f"Executing agent in subprocess: {python_executable} "
                f"{str(agent_script)} '{json.dumps(execution_data)}'"
            )
            result = subprocess.run(
                [python_executable, str(agent_script), json.dumps(execution_data)],
                cwd=str(agent_dir),
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            execution_time = time.time() - start_time

            # Parse the result
            if result.returncode == 0:
                try:
                    parsed_result = json.loads(result.stdout)
                    if isinstance(parsed_result, dict):
                        parsed_result["execution_time"] = execution_time
                        return parsed_result
                    else:
                        return {
                            "error": "Agent returned non-dictionary result",
                            "raw_output": result.stdout,
                            "execution_time": execution_time,
                        }
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse agent output: {result.stdout}")
                    return {
                        "error": f"Invalid JSON response from agent: {e}",
                        "raw_output": result.stdout,
                        "execution_time": execution_time,
                    }
            else:
                # Agent execution failed
                error_msg = result.stderr or result.stdout or "Unknown error"
                return {
                    "error": f"Agent execution failed: {error_msg}",
                    "return_code": result.returncode,
                    "execution_time": execution_time,
                }

        except subprocess.TimeoutExpired:
            return {
                "error": f"Agent execution timed out after {self.timeout} seconds",
                "timeout": self.timeout,
            }
        except FileNotFoundError as e:
            raise RuntimeError(f"Failed to execute agent: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error executing agent: {e}")
            return {"error": f"Unexpected execution error: {e}"}

    def _execute_with_monitoring(
        self,
        agent_path: str,
        method: str,
        parameters: dict[str, Any],
        tool_context: dict[str, Any] | None,
        agent_script: Path,
        agent_dir: Path,
    ) -> dict[str, Any]:
        """Execute agent with real-time monitoring."""
        execution_data = self._prepare_execution_data(method, parameters, tool_context)

        try:
            command = self._prepare_monitoring_command(
                agent_path, agent_script, execution_data
            )
            start_time = self._start_monitoring_session(command, agent_dir)
            return_code, execution_time = self._monitor_execution(start_time)
            final_logs, final_analysis = self._finalize_monitoring(
                execution_time, return_code
            )

            return self._parse_monitoring_result(
                return_code, execution_time, final_logs, final_analysis
            )

        except Exception as e:
            logger.error(f"Unexpected error in monitored execution: {e}")
            return self._create_error_result(f"Unexpected execution error: {e}")

    def _prepare_execution_data(
        self,
        method: str,
        parameters: dict[str, Any],
        tool_context: dict[str, Any] | None,
    ) -> dict[str, Any]:
        """Prepare execution data with tool context."""
        execution_data = {"method": method, "parameters": parameters}
        if tool_context:
            execution_data["tool_context"] = tool_context
        return execution_data

    def _prepare_monitoring_command(
        self, agent_path: str, agent_script: Path, execution_data: dict[str, Any]
    ) -> list[str]:
        """Prepare command for monitored execution."""
        try:
            python_executable = self.environment_manager.get_python_executable(
                agent_path
            )
        except Exception:
            # Fallback to system Python if no virtual environment
            import sys

            python_executable = sys.executable

        command = [python_executable, str(agent_script), json.dumps(execution_data)]
        logger.info(f"Starting monitored execution: {' '.join(command)}")
        return command

    def _start_monitoring_session(self, command: list[str], agent_dir: Path) -> float:
        """Start the monitoring session with log streaming and terminal display."""
        # Clear logs from previous executions to prevent accumulation
        self.log_streamer.clear_logs()
        self.log_streamer.start_streaming(command, cwd=str(agent_dir))
        self.terminal_display.start_display()
        return time.time()

    def _monitor_execution(self, start_time: float) -> tuple[int, float]:
        """Monitor the execution with periodic log analysis."""
        last_analysis_time = 0.0
        analysis_interval = 2.0  # Analyze logs every 2 seconds

        while not self.log_streamer.is_complete():
            current_time = time.time()
            new_logs = self.log_streamer.get_new_logs(0)

            # Analyze logs periodically
            if current_time - last_analysis_time >= analysis_interval and new_logs:
                try:
                    analysis = self.llm_analyzer.analyze(new_logs)
                    self.terminal_display.update_analysis(
                        analysis, len(self.log_streamer.get_logs())
                    )
                    last_analysis_time = current_time
                except Exception as e:
                    logger.warning(f"Log analysis failed: {e}")

            time.sleep(0.1)  # Small delay to prevent excessive CPU usage

        # Wait for process completion
        return_code = self.log_streamer.wait_for_completion(timeout=self.timeout)
        execution_time = time.time() - start_time
        return return_code, execution_time

    def _finalize_monitoring(
        self, execution_time: float, return_code: int
    ) -> tuple[list[str], Any]:
        """Finalize monitoring session and get final analysis."""
        final_logs = self.log_streamer.get_logs()
        final_analysis = self.llm_analyzer.analyze(final_logs)

        # Stop monitoring components
        self.terminal_display.stop_display()
        self.log_streamer.stop_streaming()

        # Show final summary
        self.terminal_display.show_final_summary(
            final_analysis, len(final_logs), execution_time, return_code
        )

        return final_logs, final_analysis

    def _parse_monitoring_result(
        self,
        return_code: int,
        execution_time: float,
        final_logs: list[str],
        final_analysis: Any,
    ) -> dict[str, Any]:
        """Parse the monitoring result and return appropriate response."""
        if return_code == 0:
            return self._parse_successful_result(final_logs, execution_time)
        else:
            return self._parse_failed_result(final_analysis, execution_time)

    def _parse_successful_result(
        self, final_logs: list[str], execution_time: float
    ) -> dict[str, Any]:
        """Parse result from successful execution."""
        try:
            stdout_lines = [line for line in final_logs if "[STDOUT]" in line]
            if stdout_lines:
                result_text = self._extract_result_text(stdout_lines)
                parsed_result = json.loads(result_text)
                logger.debug("Successfully parsed JSON result")

                # The agent already returns the correct structure, add execution_time
                # to match non-monitoring format
                if isinstance(parsed_result, dict):
                    parsed_result["execution_time"] = execution_time
                    return parsed_result
                else:
                    return self._create_parse_error_result(
                        ValueError("Agent returned non-dictionary result"),
                        execution_time,
                    )
            else:
                return self._create_success_result(execution_time)

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse agent output: {e}")
            return self._create_parse_error_result(e, execution_time)

    def _extract_result_text(self, stdout_lines: list[str]) -> str:
        """Extract and combine result text from stdout lines."""
        result_text = ""
        for line in stdout_lines:
            if "[STDOUT]" in line:
                result_text += line.split("[STDOUT]")[-1].strip()
            else:
                result_text += line.strip()

        logger.debug(f"Attempting to parse JSON: {result_text[:200]}...")
        return result_text

    def _parse_failed_result(
        self, final_analysis: Any, execution_time: float
    ) -> dict[str, Any]:
        """Parse result from failed execution."""
        error_msg = "Agent execution failed"
        if final_analysis.errors:
            error_msg += f": {', '.join(final_analysis.errors)}"

        return {
            "status": "error",
            "summary": error_msg,
            "tools_used": [],
            "execution_time": execution_time,
        }

    def _create_success_result(self, execution_time: float) -> dict[str, Any]:
        """Create a simple success result structure."""
        return {
            "status": "completed",
            "summary": "Execution completed successfully",
            "tools_used": [],
            "execution_time": execution_time,
        }

    def _create_parse_error_result(
        self, error: Exception, execution_time: float
    ) -> dict[str, Any]:
        """Create an error result for JSON parsing failures."""
        return {
            "status": "error",
            "summary": f"Invalid JSON response from agent: {error}",
            "tools_used": [],
            "execution_time": execution_time,
        }

    def _create_error_result(self, error_msg: str) -> dict[str, Any]:
        """Create a generic error result."""
        return {
            "status": "error",
            "summary": error_msg,
            "tools_used": [],
            "execution_time": 0,
        }

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

        # Check agent configuration to determine required files
        agent_config = self.environment_manager._get_agent_config(agent_path)

        # Always require agent.yaml or agent.yml
        agent_yaml_exists = (agent_dir / "agent.yaml").exists()
        agent_yml_exists = (agent_dir / "agent.yml").exists()

        if not agent_yaml_exists and not agent_yml_exists:
            logger.debug("Missing required file: agent.yaml (or agent.yml)")
            return False

        # Check for agent script file (either agent.py or agent.na)
        agent_py_exists = (agent_dir / "agent.py").exists()
        agent_na_exists = (agent_dir / "agent.na").exists()

        if agent_config and "dana_version" in agent_config:
            # For Dana agents, require agent.na
            if not agent_na_exists:
                logger.debug("Missing required file: agent.na (Dana agent)")
                return False
        else:
            # For Python agents or default, require agent.py
            if not agent_py_exists:
                logger.debug("Missing required file: agent.py (Python agent)")
                return False

        # Ensure only one agent script file exists
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

        # Check agent configuration to determine script type
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
