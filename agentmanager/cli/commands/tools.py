"""CLI commands for tool management in AgentHub.

This module provides CLI commands for managing the tool registry service,
including start, stop, status, list, unregister, and restart operations.
"""

import click

from .tools_service import tools_service
from .tools_info import tools_info
from .tools_manage import tools_manage


@click.group()
def tools():
    """Tool management commands for AgentHub."""
    pass


# Add individual commands directly
tools.add_command(tools_service.commands["start"])
tools.add_command(tools_service.commands["stop"])
tools.add_command(tools_service.commands["restart"])
tools.add_command(tools_info.commands["status"])
tools.add_command(tools_info.commands["list"])
tools.add_command(tools_info.commands["info"])
tools.add_command(tools_manage.commands["unregister"])
