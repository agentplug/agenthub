"""CLI command for listing available agents."""

import sys

import click
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from agenthub.core.agents.loader import AgentLoader
from agenthub.storage.local_storage import LocalStorage

from ...utils.display_helpers import truncate_text

console = Console()


@click.group()
def core_list() -> None:
    """Core list command group."""
    pass


@core_list.command("list")
def list_agents() -> None:
    """List all available agents."""
    try:
        # Initialize system
        storage = LocalStorage()
        loader = AgentLoader(storage=storage)

        # Discover agents
        agents = loader.discover_agents()

        if not agents:
            rprint("📦 [yellow]No agents found![/yellow]")
            rprint("💡 Install agents first using the setup instructions.")
            return

        # Create a beautiful table
        table = Table(title=f"📦 Available Agents ({len(agents)} found)")
        table.add_column("Agent", style="cyan", no_wrap=True)
        table.add_column("Version", style="magenta")
        table.add_column("Description", style="green")

        for agent in agents:
            namespace = agent.get("namespace", "unknown")
            name = agent.get("name", "unknown")
            version = agent.get("version", "unknown")

            # Get description from loader
            try:
                info = loader.get_agent_info(namespace, name)
                description = info.get("description", "No description available")
                description = truncate_text(description, 50)
            except Exception:
                description = "Error loading description"

            table.add_row(f"{namespace}/{name}", version, description)

        console.print(table)

        rprint("\n💡 [dim]Use 'agenthub info <agent>' for details[/dim]")
        rprint("🚀 [dim]Use 'agenthub exec <agent> <method> <params>' to run[/dim]")
        rprint(
            "📦 [dim]Use 'agenthub agent install <agent>' to install new agents[/dim]"
        )

    except Exception as e:
        rprint(f"❌ [red]Error listing agents: {e}[/red]")
        sys.exit(1)
