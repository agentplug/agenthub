"""Core CLI commands coordinator for AgentHub."""

import click

from .exec import core_exec
from .info import core_info
from .list import core_list
from .remove import core_remove
from .validate import core_validate


@click.group()
def core() -> None:
    """Core AgentHub commands."""
    pass


# Add individual commands directly
core.add_command(core_list.commands["list"])
core.add_command(core_info.commands["info"])
core.add_command(core_exec.commands["exec"])
core.add_command(core_validate.commands["validate"])
core.add_command(core_remove.commands["remove"])
