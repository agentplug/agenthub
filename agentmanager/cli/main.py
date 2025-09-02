"""Main CLI entry point for AgentHub."""

import click

from .commands.agent import agent
from .commands.tools import tools
from .commands.core import core


@click.group()
@click.version_option()
def cli():
    """AgentHub - AI Agent Management Platform."""
    pass


# Add command groups
cli.add_command(agent)
cli.add_command(tools)
cli.add_command(core)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
