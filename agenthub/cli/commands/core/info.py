"""CLI command for showing agent information."""

import sys

import click
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from agenthub.core.agents.loader import AgentLoader
from agenthub.storage.local_storage import LocalStorage

console = Console()


@click.group()
def core_info() -> None:
    """Core info command group."""
    pass


@core_info.command("info")
@click.argument("agent_name")
def info_agent(agent_name: str) -> None:
    """Show detailed information about an agent."""
    try:
        # Parse agent name
        if "/" not in agent_name:
            rprint(
                "❌ [red]Agent name must be in format 'namespace/name' "
                "(e.g., 'agentplug/coding-agent')[/red]"
            )
            sys.exit(1)

        namespace, name = agent_name.split("/", 1)

        # Initialize system
        storage = LocalStorage()
        loader = AgentLoader(storage=storage)

        # Load agent info
        try:
            agent_info = loader.load_agent(namespace, name)
        except Exception as e:
            rprint(f"❌ [red]Agent not found: {agent_name}[/red]")
            rprint(f"Error: {e}")
            sys.exit(1)

        # Display agent information
        rprint(
            f"\n🔧 [bold cyan]Agent: {agent_name} "
            f"v{agent_info.get('version', 'unknown')}[/bold cyan]"
        )
        rprint("═" * 50)

        rprint(
            f"📖 [bold]Description:[/bold] "
            f"{agent_info.get('description', 'No description')}"
        )
        rprint(f"👤 [bold]Author:[/bold] {agent_info.get('author', 'Unknown')}")
        rprint(f"📍 [bold]Location:[/bold] {agent_info.get('path', 'Unknown')}")
        rprint(
            f"✅ [bold]Status:[/bold] "
            f"{'Valid and ready' if agent_info.get('valid', False) else 'Invalid'}"
        )

        # Show methods
        methods = agent_info.get("methods", [])
        if methods:
            rprint(f"\n🎯 [bold]Available Methods ({len(methods)}):[/bold]")

            method_table = Table()
            method_table.add_column("Method", style="cyan", no_wrap=True)
            method_table.add_column("Description", style="green")

            manifest = agent_info.get("manifest", {})
            interface = manifest.get("interface", {})
            method_defs = interface.get("methods", {})

            for method in methods:
                method_def = method_defs.get(method, {})
                description = method_def.get("description", "No description available")
                method_table.add_row(method, description)

            console.print(method_table)

        # Show dependencies
        dependencies = agent_info.get("dependencies", [])
        if dependencies:
            rprint(f"\n📦 [bold]Dependencies ({len(dependencies)}):[/bold]")
            for dep in dependencies:
                rprint(f"  • {dep}")

        # Show usage example
        if methods:
            first_method = methods[0]
            rprint("\n💡 [bold]Example Usage:[/bold]")

            # Get the actual parameter names from the method definition
            method_def = method_defs.get(first_method, {})
            parameters = method_def.get("parameters", {})

            if parameters:
                # Use the first required parameter or first parameter available
                param_name = None
                for param, param_info in parameters.items():
                    if isinstance(param_info, dict) and param_info.get(
                        "required", True
                    ):
                        param_name = param
                        break

                if not param_name and parameters:
                    # Fall back to first parameter if no required ones
                    param_name = list(parameters.keys())[0]

                if param_name:
                    rprint(
                        f"  [dim]agenthub exec {agent_name} {first_method} "
                        f'"{{\\"{param_name}\\": \\"your input\\"}}"[/dim]'
                    )
                else:
                    rprint(
                        f"  [dim]agenthub exec {agent_name} {first_method} "
                        f'"your input"[/dim]'
                    )
            else:
                # No parameters defined, use simple input
                rprint(
                    f"  [dim]agenthub exec {agent_name} {first_method} "
                    f'"your input"[/dim]'
                )

            rprint(f"  [dim]agenthub agent status {agent_name}[/dim]")

    except Exception as e:
        rprint(f"❌ [red]Error getting agent info: {e}[/red]")
        sys.exit(1)
