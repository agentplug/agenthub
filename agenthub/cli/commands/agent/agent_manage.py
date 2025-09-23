"""CLI commands for agent management (repair, cleanup)."""

import shutil
from pathlib import Path

import click
from rich import print as rprint
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm

from agenthub.environment.environment_setup import EnvironmentSetup
from agenthub.github.repository_cloner import RepositoryCloner
from agenthub.github.repository_validator import RepositoryValidator

console = Console()


@click.group()
def agent_manage() -> None:
    """Agent management commands."""
    pass


@agent_manage.command("repair")
@click.argument("agent_name")
@click.option(
    "--base-path",
    type=click.Path(),
    help="Custom base storage path for agents",
)
@click.option(
    "--force-reinstall-deps",
    is_flag=True,
    help="Force reinstall all dependencies",
)
def repair_agent(
    agent_name: str, base_path: str | None, force_reinstall_deps: bool
) -> None:
    """Repair a broken agent environment."""
    try:
        cloner = RepositoryCloner(base_storage_path=base_path)

        if not cloner.is_agent_cloned(agent_name):
            rprint(f"❌ [red]Agent '{agent_name}' not found[/red]")
            return

        agent_path = cloner.get_agent_path(agent_name)
        if not agent_path:
            rprint(f"❌ [red]Could not get path for agent '{agent_name}'[/red]")
            return

        rprint(f"🔧 [cyan]Repairing agent: {agent_name}[/cyan]")
        rprint(f"📁 Path: {agent_path}")

        # Check for existing environment
        venv_path = Path(agent_path) / ".venv"
        if venv_path.exists():
            if not Confirm.ask("Virtual environment exists. Recreate?"):
                return

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Removing broken environment...", total=None)
                shutil.rmtree(venv_path)
                progress.update(task, completed=True)

        # Create new environment
        env_setup = EnvironmentSetup()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Creating new environment...", total=None)

            env_result = env_setup.setup_environment(str(agent_path))
            progress.update(task, completed=True)

        if env_result.success:
            rprint("✅ [green]Environment created successfully[/green]")

            # Install dependencies
            requirements_path = Path(agent_path) / "requirements.txt"
            if requirements_path.exists():
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task("Installing dependencies...", total=None)

                    dep_result = env_setup.install_dependencies(
                        str(agent_path), str(venv_path)
                    )
                    progress.update(task, completed=True)

                if dep_result.success:
                    package_count = len(dep_result.installed_packages)
                    message = (
                        f"✅ [green]Dependencies installed: "
                        f"{package_count} packages[/green]"
                    )
                    rprint(message)
                else:
                    message = (
                        f"⚠️ [yellow]Dependency installation failed: "
                        f"{dep_result.error_message}[/yellow]"
                    )
                    rprint(message)

            rprint("\n🚀 [green]Agent repair completed successfully![/green]")
        else:
            rprint(
                f"❌ [red]Environment creation failed: {env_result.error_message}[/red]"
            )

    except Exception as e:
        rprint(f"❌ [red]Repair error: {e}[/red]")


@agent_manage.command("cleanup")
@click.option(
    "--dry-run", is_flag=True, help="Show what would be cleaned without doing it"
)
@click.option("--remove-invalid", is_flag=True, help="Remove invalid agents")
@click.option(
    "--remove-broken-envs", is_flag=True, help="Remove broken virtual environments"
)
def cleanup_agents(
    dry_run: bool, remove_invalid: bool, remove_broken_envs: bool
) -> None:
    """Clean up and optimize agent storage."""
    try:
        cloner = RepositoryCloner()
        agents = cloner.list_cloned_agents()

        if not agents:
            rprint("📦 [yellow]No agents to clean up[/yellow]")
            return

        validator = RepositoryValidator()
        env_setup = EnvironmentSetup()

        cleanup_candidates = []

        rprint("🔍 [cyan]Analyzing agents for cleanup...[/cyan]")

        for agent_name, path in agents.items():
            issues = []

            # Check validation
            try:
                validation_result = validator.validate_repository(path)
                if not validation_result.is_valid:
                    issues.append("Invalid structure")
            except Exception as e:
                issues.append(f"Validation error: {e}")

            # Check environment
            venv_path = Path(path) / ".venv"
            if venv_path.exists():
                try:
                    env_info = env_setup._collect_environment_info(
                        Path(path), venv_path
                    )
                    if not env_info.get("venv_exists", False):
                        issues.append("Broken environment")
                except Exception:
                    issues.append("Environment issues")

            if issues:
                cleanup_candidates.append((agent_name, path, issues))

        if not cleanup_candidates:
            rprint("✅ [green]All agents are healthy[/green]")
            return

        rprint(
            f"\n🧹 [bold]Found {len(cleanup_candidates)} agents needing cleanup:[/bold]"
        )

        for agent_name, _path, issues in cleanup_candidates:
            rprint(f"  • [cyan]{agent_name}[/cyan]: {', '.join(issues)}")

        if dry_run:
            rprint("\n🔍 [yellow]Dry run - no changes made[/yellow]")
            return

        if not (remove_invalid or remove_broken_envs):
            if not Confirm.ask("\nClean up these agents?"):
                return

        # Perform cleanup
        cleaned = 0
        for agent_name, _path, issues in cleanup_candidates:
            if (
                (remove_invalid and "Invalid structure" in issues)
                or (remove_broken_envs and "Broken environment" in issues)
                or (not remove_invalid and not remove_broken_envs)
            ):

                try:
                    if cloner.remove_agent(agent_name):
                        rprint(f"  ✅ [green]Removed: {agent_name}[/green]")
                        cleaned += 1
                except Exception as e:
                    rprint(f"  ❌ [red]Failed to remove {agent_name}: {e}[/red]")

        rprint(f"\n🧹 [green]Cleanup completed: {cleaned} agents removed[/green]")

    except Exception as e:
        rprint(f"❌ [red]Cleanup error: {e}[/red]")
