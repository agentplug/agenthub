"""Installation management system for Phase 3."""

from .command_executor import CommandExecutor, CommandResult
from .manager import InstallationManager
from .plugins import PluginManager
from .validator import InstallationValidator

__all__ = [
    "CommandExecutor",
    "CommandResult",
    "InstallationValidator",
    "InstallationManager",
    "PluginManager",
]
