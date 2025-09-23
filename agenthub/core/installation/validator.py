"""Installation validation for agents."""

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of installation validation."""

    is_valid: bool
    errors: list[str]
    warnings: list[str]


class InstallationValidator:
    """Validates installation commands and configuration."""

    def __init__(self) -> None:
        """Initialize installation validator."""
        self.supported_commands = [
            "uv",
            "pip",
            "python",
            "make",
            "npm",
            "yarn",
            "cargo",
            "go",
            "docker",
        ]
        self.dangerous_commands = [
            "rm",
            "del",
            "format",
            "fdisk",
            "mkfs",
            "dd",
            "shutdown",
            "reboot",
        ]

    def validate_installation_commands(self, commands: list[str]) -> ValidationResult:
        """Validate installation commands."""
        errors: list[str] = []
        warnings: list[str] = []

        if not commands:
            errors.append("At least one installation command is required")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        for i, command in enumerate(commands):
            command_errors, command_warnings = self._validate_single_command(command, i)
            errors.extend(command_errors)
            warnings.extend(command_warnings)

        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)

    def validate_validation_commands(self, commands: list[str]) -> ValidationResult:
        """Validate validation commands."""
        errors: list[str] = []
        warnings: list[str] = []

        for i, command in enumerate(commands):
            command_errors, command_warnings = self._validate_single_command(command, i)
            errors.extend(command_errors)
            warnings.extend(command_warnings)

        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)

    def _validate_single_command(
        self, command: str, index: int
    ) -> tuple[list[str], list[str]]:
        """Validate a single command."""
        errors: list[str] = []
        warnings: list[str] = []

        if not command.strip():
            errors.append(f"Command {index + 1} is empty")
            return errors, warnings

        # Check for dangerous commands
        command_lower = command.lower()
        for dangerous in self.dangerous_commands:
            if command_lower.startswith(dangerous):
                errors.append(
                    f"Command {index + 1} contains dangerous command "
                    f"'{dangerous}': {command}"
                )

        # Check for supported commands
        command_parts = command.split()
        if command_parts:
            first_command = command_parts[0]
            if first_command not in self.supported_commands:
                warnings.append(
                    f"Command {index + 1} uses unsupported command "
                    f"'{first_command}': {command}"
                )

        # Check for common issues
        if "sudo" in command_lower:
            warnings.append(
                f"Command {index + 1} uses 'sudo' which may require "
                f"user interaction: {command}"
            )

        if "&&" in command or "||" in command or ";" in command:
            warnings.append(
                f"Command {index + 1} contains shell operators which may "
                f"not work as expected: {command}"
            )

        # Check for proper virtual environment usage
        if (
            "pip install" in command_lower
            and "venv" not in command_lower
            and "virtual" not in command_lower
        ):
            warnings.append(
                f"Command {index + 1} uses pip without virtual environment: {command}"
            )

        return errors, warnings

    def validate_agent_config(self, config: dict[str, Any]) -> ValidationResult:
        """Validate agent configuration for installation."""
        errors: list[str] = []
        warnings: list[str] = []

        # Check for installation section
        if "installation" not in config:
            errors.append("Agent configuration must include 'installation' section")
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        installation = config["installation"]

        # Check for commands
        if "commands" not in installation:
            errors.append("Installation section must include 'commands'")
        else:
            commands = installation["commands"]
            if not isinstance(commands, list):
                errors.append("Installation commands must be a list")
            elif not commands:
                errors.append("At least one installation command is required")
            else:
                command_validation = self.validate_installation_commands(commands)
                errors.extend(command_validation.errors)
                warnings.extend(command_validation.warnings)

        # Check for validation commands
        if "validation" in installation:
            validation_commands = installation["validation"]
            if not isinstance(validation_commands, list):
                errors.append("Installation validation commands must be a list")
            else:
                validation_validation = self.validate_validation_commands(
                    validation_commands
                )
                errors.extend(validation_validation.errors)
                warnings.extend(validation_validation.warnings)

        # Check for backward compatibility
        if "dependencies" in config:
            warnings.append(
                "Agent uses deprecated 'dependencies' field. Consider migrating "
                "to 'installation.commands'"
            )

        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)
