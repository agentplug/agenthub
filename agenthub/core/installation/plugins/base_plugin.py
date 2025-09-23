"""Base plugin for installation methods."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from ..command_executor import CommandResult


class BaseInstallationPlugin(ABC):
    """Base class for installation method plugins."""

    def __init__(self, name: str, description: str = ""):
        """Initialize plugin."""
        self.name = name
        self.description = description

    @abstractmethod
    def can_handle(self, command: str) -> bool:
        """Check if this plugin can handle the given command."""
        pass

    @abstractmethod
    def execute(
        self,
        command: str,
        agent_path: Path,
        venv_path: Path,
        environment: dict[str, str],
    ) -> CommandResult:
        """Execute the command."""
        pass

    def get_supported_commands(self) -> list[str]:
        """Get list of supported command patterns."""
        return []

    def validate_command(self, command: str) -> list[str]:  # noqa: ARG002
        """Validate command before execution."""
        return []

    def get_plugin_info(self) -> dict[str, Any]:
        """Get plugin information."""
        return {
            "name": self.name,
            "description": self.description,
            "supported_commands": self.get_supported_commands(),
        }
