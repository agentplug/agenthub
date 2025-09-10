"""Core CLI commands coordinator for AgentHub."""

import click

from .list import core_list
from .info import core_info
from .exec import core_exec
from .validate import core_validate
from .remove import core_remove


@click.group()
def core():
    """Core AgentHub commands."""
    pass


# Add individual commands directly
core.add_command(core_list.commands["list"])
core.add_command(core_info.commands["info"])
core.add_command(core_exec.commands["exec"])
core.add_command(core_validate.commands["validate"])
core.add_command(core_remove.commands["remove"])
