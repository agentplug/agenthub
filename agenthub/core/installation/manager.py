"""Installation management for agents."""

import logging
import time
from pathlib import Path
from typing import Any

from .command_executor import CommandExecutor, CommandResult
from .validator import InstallationValidator

logger = logging.getLogger(__name__)


class InstallationManager:
    """Manages installation process for agents."""

    def __init__(self, agent_path: str, venv_path: str):
        """Initialize installation manager."""
        self.agent_path = Path(agent_path)
        self.venv_path = Path(venv_path)
        self.executor = CommandExecutor(agent_path, venv_path)
        self.validator = InstallationValidator()

    def install_agent(self, agent_config: dict[str, Any]) -> dict[str, Any]:
        """Install agent based on configuration."""
        start_time = time.time()

        try:
            # Validate configuration
            validation_result = self.validator.validate_agent_config(agent_config)
            if not validation_result.is_valid:
                return self._create_failure_result(
                    "Configuration validation failed",
                    validation_result.errors,
                    time.time() - start_time,
                )

            # Log warnings
            for warning in validation_result.warnings:
                logger.warning(f"Installation warning: {warning}")

            # Execute installation commands
            installation = agent_config.get("installation", {})
            commands = installation.get("commands", [])

            installation_results = []
            for command in commands:
                result = self.executor.execute_installation_command(command)
                installation_results.append(result)

                if not result.success:
                    return self._create_failure_result(
                        f"Installation command failed: {command}",
                        [result.error or result.stderr],
                        time.time() - start_time,
                        installation_results,
                    )

            # Execute validation commands
            validation_commands = installation.get("validation", [])
            validation_results = []
            for command in validation_commands:
                result = self.executor.execute_validation_command(command)
                validation_results.append(result)

                if not result.success:
                    return self._create_failure_result(
                        f"Validation command failed: {command}",
                        [result.error or result.stderr],
                        time.time() - start_time,
                        installation_results,
                        validation_results,
                    )

            # Success
            return self._create_success_result(
                installation_results, validation_results, time.time() - start_time
            )

        except Exception as e:
            logger.error(f"Installation failed: {e}")
            return self._create_failure_result(
                f"Installation failed: {e}", [str(e)], time.time() - start_time
            )

    def _create_success_result(
        self,
        installation_results: list[CommandResult],
        validation_results: list[CommandResult],
        total_time: float,
    ) -> dict[str, Any]:
        """Create success result."""
        return {
            "success": True,
            "total_time": total_time,
            "installation_commands": len(installation_results),
            "validation_commands": len(validation_results),
            "installation_results": [
                {
                    "command": result.command,
                    "success": result.success,
                    "execution_time": result.execution_time,
                    "exit_code": result.exit_code,
                }
                for result in installation_results
            ],
            "validation_results": [
                {
                    "command": result.command,
                    "success": result.success,
                    "execution_time": result.execution_time,
                    "exit_code": result.exit_code,
                }
                for result in validation_results
            ],
            "environment_info": self.executor.get_environment_info(),
        }

    def _create_failure_result(
        self,
        error_message: str,
        errors: list[str],
        total_time: float,
        installation_results: list[CommandResult] | None = None,
        validation_results: list[CommandResult] | None = None,
    ) -> dict[str, Any]:
        """Create failure result."""
        return {
            "success": False,
            "error_message": error_message,
            "errors": errors,
            "total_time": total_time,
            "installation_commands": (
                len(installation_results) if installation_results else 0
            ),
            "validation_commands": len(validation_results) if validation_results else 0,
            "installation_results": [
                {
                    "command": result.command,
                    "success": result.success,
                    "execution_time": result.execution_time,
                    "exit_code": result.exit_code,
                    "error": result.error or result.stderr,
                }
                for result in (installation_results or [])
            ],
            "validation_results": [
                {
                    "command": result.command,
                    "success": result.success,
                    "execution_time": result.execution_time,
                    "exit_code": result.exit_code,
                    "error": result.error or result.stderr,
                }
                for result in (validation_results or [])
            ],
            "environment_info": self.executor.get_environment_info(),
        }

    def get_installation_summary(self) -> dict[str, Any]:
        """Get installation summary."""
        return {
            "agent_path": str(self.agent_path),
            "venv_path": str(self.venv_path),
            "environment_info": self.executor.get_environment_info(),
        }
