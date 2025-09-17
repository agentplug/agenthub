"""Process manager for executing agents in isolated subprocesses."""

import json
import logging
import subprocess
import time
from pathlib import Path

from agenthub.core.agents.dynamic_executor import DynamicAgentExecutor
from agenthub.runtime.environment_manager import EnvironmentManager

logger = logging.getLogger(__name__)


class ProcessManager:
    """Manages agent subprocess execution with isolation."""

    def __init__(self, timeout: int = 300, use_dynamic_execution: bool = True):
        """
        Initialize the process manager.

        Args:
            timeout: Maximum execution time in seconds
            use_dynamic_execution: Whether to use dynamic execution (default: True)
        """
        self.timeout = timeout
        self.environment_manager = EnvironmentManager()
        self.use_dynamic_execution = use_dynamic_execution
        self.dynamic_executor = (
            DynamicAgentExecutor() if use_dynamic_execution else None
        )

    def execute_agent(
        self,
        agent_path: str,
        method: str,
        parameters: dict,
        manifest: dict = None,
        tool_context: dict = None,
    ) -> dict:
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

        agent_script = agent_dir / "agent.py"
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

        # Fallback to subprocess execution
        # Prepare execution data with tool context if available
        execution_data = {"method": method, "parameters": parameters}
        if tool_context:
            execution_data["tool_context"] = tool_context

        try:
            # Get Python executable for this agent's virtual environment
            python_executable = self.environment_manager.get_python_executable(
                agent_path
            )

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
                    parsed_result["execution_time"] = execution_time
                    return parsed_result
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

        required_files = ["agent.py", "agent.yaml"]
        for file_name in required_files:
            if not (agent_dir / file_name).exists():
                logger.debug(f"Missing required file: {file_name}")
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
