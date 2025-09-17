"""CLI commands for agent installation and removal."""

from pathlib import Path

import click
from rich import print as rprint
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from agenthub.github.auto_installer import AutoInstaller
from agenthub.github.repository_cloner import RepositoryCloner

console = Console()


@click.group()
def agent_install():
    """Agent installation and removal commands."""
    pass


@agent_install.command("install")
@click.argument("agent_name")
@click.option(
    "--setup-environment/--no-setup-environment",
    default=True,
    help="Set up UV virtual environment and install dependencies",
)
@click.option(
    "--base-path",
    type=click.Path(),
    help="Custom base storage path for agents",
)
@click.option(
    "--force",
    is_flag=True,
    help="Force reinstallation if agent already exists",
)
def install_agent(
    agent_name: str, setup_environment: bool, base_path: str | None, force: bool
):
    """Install an agent from GitHub."""
    try:
        # Validate agent name format
        if "/" not in agent_name:
            rprint("❌ [red]Agent name must be in format 'developer/agent-name'[/red]")
            return

        # Check if already installed
        cloner = RepositoryCloner(
            base_storage_path=Path(base_path) if base_path else None
        )
        if cloner.is_agent_cloned(agent_name) and not force:
            if not Confirm.ask(
                f"Agent '{agent_name}' is already installed. Reinstall?"
            ):
                return

        # Initialize installer
        installer = AutoInstaller(
            base_storage_path=Path(base_path) if base_path else None,
            setup_environment=setup_environment,
        )

        rprint(f"🚀 [cyan]Installing agent: {agent_name}[/cyan]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Installing...", total=None)

            # Install agent
            result = installer.install_agent(agent_name)

            progress.update(task, completed=True)

        # Display results
        if result.success:
            rprint("\n✅ [green]Installation successful![/green]")
            rprint(f"📁 Location: {result.local_path}")
            rprint(f"⏱️  Time: {result.installation_time_seconds:.2f}s")

            if result.environment_result and result.environment_result.success:
                rprint(f"🌍 Environment: {result.environment_result.venv_path}")

            if result.dependency_result and result.dependency_result.success:
                package_count = len(result.dependency_result.installed_packages)
                rprint(f"📦 Dependencies: {package_count} packages installed")

            # Show next steps
            if result.next_steps:
                rprint("\n📋 [bold]Next steps:[/bold]")
                for step in result.next_steps:
                    rprint(f"  • {step}")
        else:
            rprint("❌ [red]Installation failed![/red]")
            rprint(f"Error: {result.error_message}")

            if result.next_steps:
                rprint("\n🔧 [bold]Troubleshooting:[/bold]")
                for step in result.next_steps:
                    rprint(f"  • {step}")

    except Exception as e:
        rprint(f"❌ [red]Installation error: {e}[/red]")


@agent_install.command("remove")
@click.argument("agent_name")
@click.option(
    "--base-path",
    type=click.Path(),
    help="Custom base storage path for agents",
)
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
def remove_agent(agent_name: str, base_path: str | None, force: bool):
    """Remove an installed agent."""
    try:
        cloner = RepositoryCloner(
            base_storage_path=Path(base_path) if base_path else None
        )

        if not cloner.is_agent_cloned(agent_name):
            rprint(f"❌ [red]Agent '{agent_name}' not found[/red]")
            return

        agent_path = cloner.get_agent_path(agent_name)

        if not force:
            if not Confirm.ask(f"Remove agent '{agent_name}' from {agent_path}?"):
                return

        if cloner.remove_agent(agent_name):
            rprint(f"✅ [green]Agent '{agent_name}' removed successfully[/green]")
            rprint(f"📁 Removed: {agent_path}")
        else:
            rprint(f"❌ [red]Failed to remove agent '{agent_name}'[/red]")

    except Exception as e:
        rprint(f"❌ [red]Error removing agent: {e}[/red]")
