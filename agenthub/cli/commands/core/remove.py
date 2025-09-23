"""CLI command for removing agents (legacy)."""

import click
from rich import print as rprint

from agenthub.github.repository_cloner import RepositoryCloner


@click.group()
def core_remove() -> None:
    """Core remove command group."""
    pass


@core_remove.command("remove")
@click.argument("agent_name")
@click.option(
    "--base-path",
    type=click.Path(),
    help="Custom base storage path for agents",
)
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
def remove_agent(agent_name: str, base_path: str | None, force: bool) -> None:
    """Remove an installed agent.

    This is a legacy command. Use 'agenthub agent remove <agent>' instead.
    """
    rprint("⚠️  [yellow]This command is deprecated.[/yellow]")
    rprint("💡 [cyan]Use instead: agenthub agent remove <agent>[/cyan]")

    cloner = RepositoryCloner(base_storage_path=base_path)

    if not cloner.is_agent_cloned(agent_name):
        rprint(f"❌ [red]Agent '{agent_name}' not found[/red]")
        return

    agent_path = cloner.get_agent_path(agent_name)

    if not force:
        if not click.confirm(f"Remove agent '{agent_name}' from {agent_path}?"):
            return

    if cloner.remove_agent(agent_name):
        rprint(f"✅ [green]Agent '{agent_name}' removed successfully[/green]")
        rprint(f"📁 Removed: {agent_path}")
    else:
        rprint(f"❌ [red]Failed to remove agent '{agent_name}'[/red]")
