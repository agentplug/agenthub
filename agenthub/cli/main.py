"""Main CLI entry point for AgentHub."""

import click

from .commands.agent import agent
from .commands.core.exec import core_exec
from .commands.core.info import core_info
from .commands.core.list import core_list
from .commands.core.remove import core_remove
from .commands.core.validate import core_validate


@click.group()
@click.version_option()
def cli() -> None:
    """AgentHub - AI Agent Management Platform."""
    pass


# Add command groups
cli.add_command(agent)

# Add core commands directly (without core prefix for better UX)
cli.add_command(core_list.commands["list"])
cli.add_command(core_info.commands["info"])
cli.add_command(core_exec.commands["exec"])
cli.add_command(core_validate.commands["validate"])
cli.add_command(core_remove.commands["remove"])


def main() -> None:
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
