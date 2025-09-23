"""CLI commands for agent management in AgentHub.

This module provides CLI commands for managing agents,
organized into focused submodules for better maintainability.
"""

import click

from .agent_advanced import agent_advanced
from .agent_backup import agent_backup
from .agent_install import agent_install
from .agent_list import agent_list
from .agent_manage import agent_manage


@click.group()
def agent() -> None:
    """Agent management commands."""
    pass


# Add individual commands directly
agent.add_command(agent_install.commands["install"])
agent.add_command(agent_install.commands["remove"])
agent.add_command(agent_list.commands["list"])
agent.add_command(agent_list.commands["status"])
agent.add_command(agent_list.commands["info"])
agent.add_command(agent_manage.commands["repair"])
agent.add_command(agent_manage.commands["cleanup"])
agent.add_command(agent_backup.commands["backup"])
agent.add_command(agent_backup.commands["restore"])
agent.add_command(agent_advanced.commands["migrate"])
agent.add_command(agent_advanced.commands["clone"])
agent.add_command(agent_advanced.commands["optimize"])
agent.add_command(agent_advanced.commands["python-versions"])
agent.add_command(agent_advanced.commands["analyze-deps"])
