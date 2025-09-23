"""CLI commands for agent listing, information, and status."""

from pathlib import Path

import click
from rich import print as rprint

from agenthub.github.repository_cloner import RepositoryCloner

from .agent_utils import (
    display_detailed_agent_list,
    display_simple_agent_list,
    show_agent_status,
)


@click.group()
def agent_list() -> None:
    """Agent listing, information, and status commands."""
    pass


@agent_list.command("list")
@click.option(
    "--detailed", "-d", is_flag=True, help="Show detailed information about each agent"
)
@click.option(
    "--base-path",
    type=click.Path(),
    help="Custom base storage path for agents",
)
def list_agents(detailed: bool, base_path: str | None) -> None:
    """List all installed agents."""
    try:
        cloner = RepositoryCloner(base_storage_path=base_path)
        agents = cloner.list_cloned_agents()

        if not agents:
            rprint("📦 [yellow]No agents installed[/yellow]")
            return

        if detailed:
            display_detailed_agent_list(agents, cloner)
        else:
            display_simple_agent_list(agents)

    except Exception as e:
        rprint(f"❌ [red]Error listing agents: {e}[/red]")


@agent_list.command("status")
@click.argument("agent_name", required=False)
def status(agent_name: str | None) -> None:
    """Show detailed status of agents or a specific agent."""
    try:
        cloner = RepositoryCloner()

        if agent_name:
            # Single agent status
            if not cloner.is_agent_cloned(agent_name):
                rprint(f"❌ [red]Agent '{agent_name}' not found[/red]")
                return

            agent_path = cloner.get_agent_path(agent_name)
            if agent_path:
                show_agent_status(agent_name, agent_path)
            else:
                rprint(f"❌ [red]Could not get path for agent '{agent_name}'[/red]")
        else:
            # All agents status
            agents = cloner.list_cloned_agents()
            if not agents:
                rprint("📦 [yellow]No agents installed[/yellow]")
                return

            rprint(f"📊 [bold]Agent Status Report ({len(agents)} agents)[/bold]")

            for agent_name, path in agents.items():
                rprint(f"\n{'='*50}")
                show_agent_status(agent_name, path)

    except Exception as e:
        rprint(f"❌ [red]Status error: {e}[/red]")


@agent_list.command("info")
@click.argument("agent_name")
@click.option(
    "--base-path",
    type=click.Path(),
    help="Custom base storage path for agents",
)
def info_agent(agent_name: str, base_path: str | None) -> None:
    """Show detailed information about an installed agent."""
    try:
        from agenthub.core.agents.loader import AgentLoader
        from agenthub.storage.local_storage import LocalStorage

        # Parse agent name
        if "/" not in agent_name:
            rprint("❌ [red]Agent name must be in format 'namespace/name'[/red]")
            rprint("💡 [dim]Example: agentplug/coding-agent[/dim]")
            return

        namespace, name = agent_name.split("/", 1)

        # Initialize system
        storage = LocalStorage(base_dir=Path(base_path) if base_path else None)
        loader = AgentLoader(storage=storage)

        # Load agent info
        try:
            agent_info = loader.load_agent(namespace, name)
        except Exception as e:
            rprint(f"❌ [red]Agent not found: {agent_name}[/red]")
            rprint(f"Error: {e}")
            return

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

            from rich.table import Table

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

            from rich.console import Console

            console = Console()
            console.print(method_table)

        # Show dependencies
        dependencies = agent_info.get("dependencies", [])
        if dependencies:
            rprint(f"\n📦 [bold]Dependencies ({len(dependencies)}):[/bold]")
            for dep in dependencies:
                rprint(f"  • {dep}")

        # Show environment info
        from agenthub.environment.environment_setup import EnvironmentSetup

        agent_path = agent_info.get("path")
        if agent_path:
            venv_path = Path(agent_path) / ".venv"
            if venv_path.exists():
                try:
                    env_setup = EnvironmentSetup()
                    env_info = env_setup._collect_environment_info(
                        agent_path, venv_path
                    )

                    rprint("\n🌍 [bold]Environment:[/bold]")
                    status = "Active" if env_info.get("venv_exists") else "Broken"
                    rprint(f"   Status: {status}")
                    rprint(f"   Python: {env_info.get('python_executable', 'Unknown')}")
                    rprint(f"   UV Version: {env_info.get('uv_version', 'Unknown')}")

                    # Check installed packages
                    packages = env_setup._get_installed_packages(str(venv_path))
                    rprint(f"   Packages: {len(packages)} installed")

                except Exception as e:
                    rprint(f"❌ Environment info: {e}")
            else:
                rprint("\n🌍 [bold]Environment:[/bold] Not created")

    except Exception as e:
        rprint(f"❌ [red]Error getting agent info: {e}[/red]")
