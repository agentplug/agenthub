"""Command execution engine for installation commands."""

import logging
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class CommandResult:
    """Result of command execution."""

    success: bool
    command: str
    stdout: str = ""
    stderr: str = ""
    error: str = ""
    execution_time: float = 0.0
    exit_code: int = 0


class CommandExecutor:
    """Executes installation commands from agent.yaml."""

    def __init__(self, agent_path: str, venv_path: str):
        """Initialize command executor."""
        self.agent_path = Path(agent_path)
        self.venv_path = Path(venv_path)
        self.environment = self._setup_environment()
        self.timeout = 300  # 5 minutes default timeout

    def execute_installation_command(self, command: str) -> CommandResult:
        """Execute a single installation command."""
        start_time = time.time()

        try:
            logger.info(f"Executing installation command: {command}")

            # Parse command
            command_parts = self._parse_command(command)

            # Execute command
            result = subprocess.run(
                command_parts,
                cwd=self.agent_path,
                env=self.environment,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )

            execution_time = time.time() - start_time

            success = result.returncode == 0

            if success:
                logger.info(f"Command succeeded in {execution_time:.2f}s: {command}")
            else:
                logger.warning(
                    f"Command failed with exit code {result.returncode}: {command}"
                )

            return CommandResult(
                success=success,
                command=command,
                stdout=result.stdout,
                stderr=result.stderr,
                execution_time=execution_time,
                exit_code=result.returncode,
            )

        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            logger.error(f"Command timed out after {execution_time:.2f}s: {command}")
            return CommandResult(
                success=False,
                command=command,
                error=f"Command timed out after {self.timeout}s",
                execution_time=execution_time,
                exit_code=-1,
            )
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Command execution failed: {command} - {e}")
            return CommandResult(
                success=False,
                command=command,
                error=str(e),
                execution_time=execution_time,
                exit_code=-1,
            )

    def execute_validation_command(self, command: str) -> CommandResult:
        """Execute a validation command."""
        logger.info(f"Executing validation command: {command}")
        return self.execute_installation_command(command)

    def _parse_command(self, command: str) -> list[str]:
        """Parse command string into list of arguments."""
        # Simple command parsing - can be enhanced for complex commands
        import shlex

        try:
            return shlex.split(command)
        except ValueError:
            # Fallback to simple split if shlex fails
            return command.split()

    def _setup_environment(self) -> dict[str, str]:
        """Setup environment variables for command execution."""
        env = os.environ.copy()

        # Set virtual environment variables
        env["VIRTUAL_ENV"] = str(self.venv_path)
        env["PATH"] = f"{self.venv_path}/bin:{env.get('PATH', '')}"

        # Set Python path
        python_path = self.venv_path / "bin" / "python"
        if python_path.exists():
            env["PYTHON"] = str(python_path)

        # Set working directory
        env["PWD"] = str(self.agent_path)

        # Preserve important environment variables
        important_vars = [
            "HOME",
            "USER",
            "SHELL",
            "TERM",
            "LANG",
            "LC_ALL",
            "PYTHONPATH",
            "LD_LIBRARY_PATH",
            "DYLD_LIBRARY_PATH",
        ]

        for var in important_vars:
            if var in os.environ:
                env[var] = os.environ[var]

        return env

    def set_timeout(self, timeout: int) -> None:
        """Set command execution timeout."""
        self.timeout = timeout
        logger.debug(f"Set command timeout to {timeout}s")

    def get_environment_info(self) -> dict[str, Any]:
        """Get information about the execution environment."""
        return {
            "agent_path": str(self.agent_path),
            "venv_path": str(self.venv_path),
            "timeout": self.timeout,
            "python_executable": str(self.venv_path / "bin" / "python"),
            "environment_vars": {
                "VIRTUAL_ENV": self.environment.get("VIRTUAL_ENV"),
                "PATH": self.environment.get("PATH", "").split(":")[
                    :3
                ],  # First 3 PATH entries
                "PYTHON": self.environment.get("PYTHON"),
            },
        }
