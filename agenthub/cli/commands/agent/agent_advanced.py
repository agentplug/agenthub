"""CLI commands for advanced agent operations.

Includes migrate, clone, optimize, analyze-deps, python-versions.
"""

from pathlib import Path

import click
from rich import print as rprint
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from agenthub.environment.environment_manager import AdvancedEnvironmentManager

console = Console()


@click.group()
def agent_advanced() -> None:
    """Advanced agent operations commands."""
    pass


@agent_advanced.command("migrate")
@click.argument("agent_name")
@click.argument("python_version")
@click.option(
    "--backup/--no-backup",
    default=True,
    help="Create backup before migration",
)
@click.option(
    "--force",
    is_flag=True,
    help="Force migration even if already on target version",
)
@click.option(
    "--base-path",
    type=click.Path(),
    help="Custom base storage path for agents",
)
def migrate_agent(
    agent_name: str,
    python_version: str,
    backup: bool,
    force: bool,
    base_path: str | None,
) -> None:
    """Migrate agent environment to a different Python version."""
    try:
        # Validate agent name format
        if "/" not in agent_name:
            rprint("❌ [red]Agent name must be in format 'developer/agent-name'[/red]")
            return

        # Initialize manager
        manager = AdvancedEnvironmentManager(
            base_storage_path=Path(base_path) if base_path else None
        )

        # Validate agent exists
        if not manager._get_agent_path(agent_name).exists():
            rprint(f"❌ [red]Agent '{agent_name}' not found[/red]")
            return

        rprint(f"🚀 [cyan]Migrating {agent_name} to Python {python_version}[/cyan]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Migrating...", total=None)

            # Perform migration
            result = manager.migrate_python_version(
                agent_name=agent_name,
                target_python_version=python_version,
                create_backup=backup,
                force=force,
            )

            progress.update(task, completed=True)

        # Display results
        if result.success:
            rprint("✅ [green]Migration successful![/green]")
            rprint(f"📊 From: Python {result.source_python}")
            rprint(f"📊 To: Python {result.target_python}")
            rprint(f"⏱️  Time: {result.migration_time:.2f}s")

            if result.backup_path:
                rprint(f"💾 Backup: {result.backup_path}")

            if result.next_steps:
                rprint("\n📋 [bold]Next steps:[/bold]")
                for step in result.next_steps:
                    rprint(f"  • {step}")
        else:
            rprint("❌ [red]Migration failed![/red]")
            rprint(f"Error: {result.error_message}")

            if result.next_steps:
                rprint("\n🔧 [bold]Troubleshooting:[/bold]")
                for step in result.next_steps:
                    rprint(f"  • {step}")

    except Exception as e:
        rprint(f"❌ [red]Migration error: {e}[/red]")


@agent_advanced.command("clone")
@click.argument("source_agent")
@click.argument("target_agent")
@click.option(
    "--include-env/--no-include-env",
    default=True,
    help="Include virtual environment in clone",
)
@click.option(
    "--base-path",
    type=click.Path(),
    help="Custom base storage path for agents",
)
def clone_agent(
    source_agent: str, target_agent: str, include_env: bool, base_path: str | None
) -> None:
    """Clone an existing agent to a new agent."""
    try:
        # Validate agent name formats
        if "/" not in source_agent or "/" not in target_agent:
            rprint("❌ [red]Agent names must be in format 'developer/agent-name'[/red]")
            return

        # Initialize manager
        manager = AdvancedEnvironmentManager(
            base_storage_path=Path(base_path) if base_path else None
        )

        rprint(f"🔄 [cyan]Cloning {source_agent} to {target_agent}[/cyan]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Cloning...", total=None)

            # Perform cloning
            result = manager.clone_environment(
                source_agent=source_agent,
                target_agent=target_agent,
                include_env=include_env,
            )

            progress.update(task, completed=True)

        # Display results
        if result.success:
            rprint("✅ [green]Clone successful![/green]")
            rprint(f"📁 Source: {result.source_path}")
            rprint(f"📁 Target: {result.target_path}")
            rprint(f"⏱️  Time: {result.clone_time:.2f}s")

            if result.warnings:
                rprint("\n⚠️  [yellow]Warnings:[/yellow]")
                for warning in result.warnings:
                    rprint(f"  • {warning}")
        else:
            rprint("❌ [red]Clone failed![/red]")
            rprint(f"Error: {result.error_message}")

    except Exception as e:
        rprint(f"❌ [red]Clone error: {e}[/red]")


@agent_advanced.command("optimize")
@click.argument("agent_name")
@click.option(
    "--base-path",
    type=click.Path(),
    help="Custom base storage path for agents",
)
def optimize_agent(agent_name: str, base_path: str | None) -> None:
    """Optimize agent environment for size and performance."""
    try:
        # Validate agent name format
        if "/" not in agent_name:
            rprint("❌ [red]Agent name must be in format 'developer/agent-name'[/red]")
            return

        # Initialize manager
        manager = AdvancedEnvironmentManager(
            base_storage_path=Path(base_path) if base_path else None
        )

        # Validate agent exists
        if not manager._get_agent_path(agent_name).exists():
            rprint(f"❌ [red]Agent '{agent_name}' not found[/red]")
            return

        rprint(f"🧹 [cyan]Optimizing {agent_name}[/cyan]")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Optimizing...", total=None)

            # Perform optimization
            result = manager.optimize_environment(agent_name)

            progress.update(task, completed=True)

        # Display results
        if result.success:
            rprint("✅ [green]Optimization successful![/green]")
            rprint(f"📊 Original size: {result.original_size_mb:.2f} MB")
            rprint(f"📊 Optimized size: {result.optimized_size_mb:.2f} MB")
            rprint(f"📊 Space saved: {result.space_saved_mb:.2f} MB")
            rprint(f"⏱️  Time: {result.optimization_time:.2f}s")

            if result.actions_taken:
                rprint("\n🎯 [bold]Actions taken:[/bold]")
                for action in result.actions_taken:
                    rprint(f"  • {action}")
        else:
            rprint("❌ [red]Optimization failed![/red]")
            rprint(f"Error: {result.error_message}")

    except Exception as e:
        rprint(f"❌ [red]Optimization error: {e}[/red]")


@agent_advanced.command("python-versions")
def list_python_versions() -> None:
    """List available Python versions for migration."""
    try:
        manager = AdvancedEnvironmentManager()
        versions = manager.list_python_versions()

        if not versions:
            rprint("📦 [yellow]No Python versions found[/yellow]")
            return

        table = Table(title="🐍 Available Python Versions")
        table.add_column("Version", style="cyan")
        table.add_column("Status", style="green")

        for version in versions:
            table.add_row(version, "Available")

        console.print(table)

    except Exception as e:
        rprint(f"❌ [red]Error listing Python versions: {e}[/red]")


@agent_advanced.command("analyze-deps")
@click.argument("agent_name")
@click.option(
    "--base-path",
    type=click.Path(),
    help="Custom base storage path for agents",
)
def analyze_dependencies(agent_name: str, base_path: str | None) -> None:
    """Analyze agent dependencies for conflicts and issues."""
    try:
        # Validate agent name format
        if "/" not in agent_name:
            rprint("❌ [red]Agent name must be in format 'developer/agent-name'[/red]")
            return

        # Initialize manager
        manager = AdvancedEnvironmentManager(
            base_storage_path=Path(base_path) if base_path else None
        )

        # Validate agent exists
        if not manager._get_agent_path(agent_name).exists():
            rprint(f"❌ [red]Agent '{agent_name}' not found[/red]")
            return

        rprint(f"🔍 [cyan]Analyzing dependencies for {agent_name}[/cyan]")

        # Perform analysis
        result = manager.analyze_dependencies(agent_name)

        if result["success"]:
            rprint("✅ [green]Dependency analysis complete[/green]")
            rprint(f"📦 Total packages: {result['total_packages']}")

            if result["packages"]:
                table = Table(title="📦 Installed Packages")
                table.add_column("Package", style="cyan")

                for package in result["packages"][:20]:  # Show first 20
                    table.add_row(package)

                if len(result["packages"]) > 20:
                    table.add_row(f"... and {len(result['packages']) - 20} more")

                console.print(table)

            if result["conflicts"]:
                rprint("\n⚠️  [yellow]Conflicts found:[/yellow]")
                for conflict in result["conflicts"]:
                    rprint(f"  • {conflict}")

            if result["recommendations"]:
                rprint("\n💡 [bold]Recommendations:[/bold]")
                for rec in result["recommendations"]:
                    rprint(f"  • {rec}")

        else:
            rprint("❌ [red]Analysis failed![/red]")
            rprint(f"Error: {result['error']}")

    except Exception as e:
        rprint(f"❌ [red]Analysis error: {e}[/red]")
