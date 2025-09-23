"""Plugin manager for installation methods."""

import logging
from pathlib import Path
from typing import Any

from ..command_executor import CommandResult
from .base_plugin import BaseInstallationPlugin

logger = logging.getLogger(__name__)


class PluginManager:
    """Manages installation method plugins."""

    def __init__(self) -> None:
        """Initialize plugin manager."""
        self.plugins: dict[str, BaseInstallationPlugin] = {}
        self._register_default_plugins()

    def register_plugin(self, plugin: BaseInstallationPlugin) -> None:
        """Register a plugin."""
        self.plugins[plugin.name] = plugin
        logger.debug(f"Registered installation plugin: {plugin.name}")

    def get_plugin_for_command(self, command: str) -> BaseInstallationPlugin | None:
        """Get the appropriate plugin for a command."""
        for plugin in self.plugins.values():
            if plugin.can_handle(command):
                return plugin
        return None

    def get_all_plugins(self) -> list[BaseInstallationPlugin]:
        """Get all registered plugins."""
        return list(self.plugins.values())

    def get_plugin(self, name: str) -> BaseInstallationPlugin | None:
        """Get plugin by name."""
        return self.plugins.get(name)

    def list_plugins(self) -> list[dict[str, Any]]:
        """List all plugins with their information."""
        return [plugin.get_plugin_info() for plugin in self.plugins.values()]

    def _register_default_plugins(self) -> None:
        """Register default plugins."""
        # UV plugin
        uv_plugin = UVInstallationPlugin()
        self.register_plugin(uv_plugin)

        # Pip plugin
        pip_plugin = PipInstallationPlugin()
        self.register_plugin(pip_plugin)

        # Make plugin
        make_plugin = MakeInstallationPlugin()
        self.register_plugin(make_plugin)

        # NPM plugin
        npm_plugin = NPMInstallationPlugin()
        self.register_plugin(npm_plugin)

        logger.info(f"Registered {len(self.plugins)} default installation plugins")


# Default plugin implementations
class UVInstallationPlugin(BaseInstallationPlugin):
    """Plugin for UV installation commands."""

    def __init__(self) -> None:
        super().__init__("uv", "UV package manager plugin")

    def can_handle(self, command: str) -> bool:
        """Check if this plugin can handle UV commands."""
        return command.strip().startswith("uv ")

    def execute(
        self,
        command: str,
        agent_path: Path,
        venv_path: Path,
        environment: dict[str, str],
    ) -> CommandResult:
        """Execute UV command."""
        # UV commands are handled by the base command executor
        # This plugin mainly provides validation and specialized handling
        from ..command_executor import CommandExecutor

        executor = CommandExecutor(str(agent_path), str(venv_path))
        return executor.execute_installation_command(command)

    def get_supported_commands(self) -> list[str]:
        """Get supported UV commands."""
        return ["uv venv", "uv pip install", "uv add", "uv remove", "uv sync"]


class PipInstallationPlugin(BaseInstallationPlugin):
    """Plugin for pip installation commands."""

    def __init__(self) -> None:
        super().__init__("pip", "Pip package manager plugin")

    def can_handle(self, command: str) -> bool:
        """Check if this plugin can handle pip commands."""
        return command.strip().startswith("pip ")

    def execute(
        self,
        command: str,
        agent_path: Path,
        venv_path: Path,
        environment: dict[str, str],
    ) -> CommandResult:
        """Execute pip command."""
        from ..command_executor import CommandExecutor

        executor = CommandExecutor(str(agent_path), str(venv_path))
        return executor.execute_installation_command(command)

    def get_supported_commands(self) -> list[str]:
        """Get supported pip commands."""
        return ["pip install", "pip uninstall", "pip freeze", "pip list"]


class MakeInstallationPlugin(BaseInstallationPlugin):
    """Plugin for Make installation commands."""

    def __init__(self) -> None:
        super().__init__("make", "Make build system plugin")

    def can_handle(self, command: str) -> bool:
        """Check if this plugin can handle make commands."""
        return command.strip().startswith("make ")

    def execute(
        self,
        command: str,
        agent_path: Path,
        venv_path: Path,
        environment: dict[str, str],
    ) -> CommandResult:
        """Execute make command."""
        from ..command_executor import CommandExecutor

        executor = CommandExecutor(str(agent_path), str(venv_path))
        return executor.execute_installation_command(command)

    def get_supported_commands(self) -> list[str]:
        """Get supported make commands."""
        return ["make install", "make build", "make test", "make clean"]


class NPMInstallationPlugin(BaseInstallationPlugin):
    """Plugin for NPM installation commands."""

    def __init__(self) -> None:
        super().__init__("npm", "NPM package manager plugin")

    def can_handle(self, command: str) -> bool:
        """Check if this plugin can handle npm commands."""
        return command.strip().startswith("npm ")

    def execute(
        self,
        command: str,
        agent_path: Path,
        venv_path: Path,
        environment: dict[str, str],
    ) -> CommandResult:
        """Execute npm command."""
        from ..command_executor import CommandExecutor

        executor = CommandExecutor(str(agent_path), str(venv_path))
        return executor.execute_installation_command(command)

    def get_supported_commands(self) -> list[str]:
        """Get supported npm commands."""
        return ["npm install", "npm uninstall", "npm run", "npm test"]
