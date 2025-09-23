"""CLI command for validating system health and agent integrity."""

import sys

import click
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from agenthub.core.agents.loader import AgentLoader
from agenthub.storage.local_storage import LocalStorage

console = Console()


@click.group()
def core_validate() -> None:
    """Core validate command group."""
    pass


@core_validate.command("validate")
def validate_system() -> None:
    """Validate system health and agent integrity."""
    try:
        # Initialize system
        storage = LocalStorage()
        loader = AgentLoader(storage=storage)

        rprint("🔍 [cyan]Validating AgentHub System...[/cyan]")
        rprint("════════════════════════════════════════════════════════════════")

        # System validation
        rprint("\n📊 [bold]System Health Check:[/bold]")

        try:
            storage.initialize_storage()
            rprint("  ✅ Storage system: [green]OK[/green]")
        except Exception as e:
            rprint(f"  ❌ Storage system: [red]ERROR - {e}[/red]")
            return

        # Agent validation
        try:
            agents = loader.discover_agents()
            rprint(f"  ✅ Agent discovery: [green]Found {len(agents)} agents[/green]")
        except Exception as e:
            rprint(f"  ❌ Agent discovery: [red]ERROR - {e}[/red]")
            return

        if not agents:
            rprint("\n⚠️  [yellow]No agents found to validate[/yellow]")
            return

        # Validate each agent
        rprint(f"\n🤖 [bold]Agent Validation ({len(agents)} agents):[/bold]")

        validation_table = Table()
        validation_table.add_column("Agent", style="cyan", no_wrap=True)
        validation_table.add_column("Status", style="green")
        validation_table.add_column("Issues", style="yellow")

        valid_count = 0

        for agent in agents:
            namespace = agent.get("namespace", "unknown")
            name = agent.get("name", "unknown")
            agent_name = f"{namespace}/{name}"

            try:
                # Try to load the agent
                agent_info = loader.load_agent(namespace, name)
                if agent_info.get("valid", False):
                    validation_table.add_row(agent_name, "✅ VALID", "None")
                    valid_count += 1
                else:
                    validation_table.add_row(
                        agent_name, "❌ INVALID", "Structure issues"
                    )
            except Exception as e:
                validation_table.add_row(agent_name, "❌ ERROR", str(e)[:50])

        console.print(validation_table)

        # Summary
        rprint("\n🎯 [bold]Validation Summary:[/bold]")
        rprint(f"  • Total agents: {len(agents)}")
        rprint(f"  • Valid agents: {valid_count}")
        rprint(f"  • Invalid agents: {len(agents) - valid_count}")

        if valid_count == len(agents):
            rprint("\n🚀 [green]System ready for production use![/green]")
            rprint("\n📋 [dim]Next steps:[/dim]")
            rprint("  • agenthub agent install <agent> - Install new agents")
            rprint("  • agenthub agent status - Check agent status")
            rprint("  • agenthub agent analyze-deps <agent> - Analyze dependencies")
        else:
            rprint(
                f"\n⚠️  [yellow]{len(agents) - valid_count} agents "
                f"need attention[/yellow]"
            )
            rprint("\n🔧 [dim]Try:[/dim]")
            rprint("  • agenthub agent repair <agent> - Repair broken agents")
            rprint("  • agenthub agent remove <agent> - Remove invalid agents")
            rprint("  • agenthub agent install <agent> - Reinstall agents")

    except Exception as e:
        rprint(f"❌ [red]Validation failed: {e}[/red]")
        sys.exit(1)
