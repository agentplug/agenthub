"""Enhanced CLI commands for Step 6: Environment Management Integration."""

import os
import shutil
import time
from pathlib import Path
from typing import Dict, List, Optional

import click
from rich import print as rprint
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table

from agentmanager.github.auto_installer import AutoInstaller
from agentmanager.github.repository_cloner import RepositoryCloner
from agentmanager.environment.environment_setup import EnvironmentSetup
from agentmanager.environment.environment_manager import AdvancedEnvironmentManager

console = Console()


@click.group()
def agent():
    """Agent management commands."""
    pass


@agent.command("install")
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
def install_agent(agent_name: str, setup_environment: bool, base_path: Optional[str], force: bool):
    """Install an agent from GitHub."""
    try:
        # Validate agent name format
        if "/" not in agent_name:
            rprint("❌ [red]Agent name must be in format 'developer/agent-name'[/red]")
            return

        # Check if already installed
        cloner = RepositoryCloner(base_storage_path=Path(base_path) if base_path else None)
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


@agent.command("list")
@click.option(
    "--detailed", "-d", is_flag=True, help="Show detailed information about each agent"
)
@click.option(
    "--base-path",
    type=click.Path(),
    help="Custom base storage path for agents",
)
def list_agents(detailed: bool, base_path: Optional[str]):
    """List all installed agents."""
    try:
        cloner = RepositoryCloner(base_storage_path=Path(base_path) if base_path else None)
        agents = cloner.list_cloned_agents()

        if not agents:
            rprint("📦 [yellow]No agents installed[/yellow]")
            return

        if detailed:
            _display_detailed_agent_list(agents, cloner)
        else:
            _display_simple_agent_list(agents)

    except Exception as e:
        rprint(f"❌ [red]Error listing agents: {e}[/red]")


def _display_simple_agent_list(agents: Dict[str, str]):
    """Display simple agent list."""
    table = Table(title=f"📦 Installed Agents ({len(agents)})")
    table.add_column("Agent", style="cyan")
    table.add_column("Path", style="green")

    for agent_name, path in agents.items():
        table.add_row(agent_name, path)

    console.print(table)


def _display_detailed_agent_list(agents: Dict[str, str], cloner: RepositoryCloner):
    """Display detailed agent information."""
    from agentmanager.github.repository_validator import RepositoryValidator

    table = Table(title=f"📦 Detailed Agent Information ({len(agents)})")
    table.add_column("Agent", style="cyan")
    table.add_column("Path", style="green")
    table.add_column("Status", style="magenta")
    table.add_column("Files", style="yellow")
    table.add_column("Python Files", style="blue")

    validator = RepositoryValidator()

    for agent_name, path in agents.items():
        try:
            validation_result = validator.validate_repository(path)
            
            status = "✅ Valid" if validation_result.is_valid else "❌ Invalid"
            total_files = validation_result.repository_info.get("total_files", "N/A")
            python_files = validation_result.repository_info.get("python_files", "N/A")
            
            table.add_row(
                agent_name,
                path,
                status,
                str(total_files),
                str(python_files),
            )
        except Exception as e:
            table.add_row(agent_name, path, f"❌ Error", str(e), "N/A")

    console.print(table)


@agent.command("remove")
@click.argument("agent_name")
@click.option(
    "--base-path",
    type=click.Path(),
    help="Custom base storage path for agents",
)
@click.option("--force", is_flag=True, help="Skip confirmation prompt")
def remove_agent(agent_name: str, base_path: Optional[str], force: bool):
    """Remove an installed agent."""
    try:
        cloner = RepositoryCloner(base_storage_path=Path(base_path) if base_path else None)

        if not cloner.is_agent_cloned(agent_name):
            rprint(f"❌ [red]Agent '{agent_name}' not found[/red]")
            return

        agent_path = cloner.get_agent_path(agent_name)
        
        if not force:
            if not Confirm.ask(
                f"Remove agent '{agent_name}' from {agent_path}?"
            ):
                return

        if cloner.remove_agent(agent_name):
            rprint(f"✅ [green]Agent '{agent_name}' removed successfully[/green]")
            rprint(f"📁 Removed: {agent_path}")
        else:
            rprint(f"❌ [red]Failed to remove agent '{agent_name}'[/red]")

    except Exception as e:
        rprint(f"❌ [red]Error removing agent: {e}[/red]")


@agent.command("repair")
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
def repair_agent(agent_name: str, base_path: Optional[str], force_reinstall_deps: bool):
    """Repair a broken agent environment."""
    try:
        cloner = RepositoryCloner(base_storage_path=Path(base_path) if base_path else None)
        
        if not cloner.is_agent_cloned(agent_name):
            rprint(f"❌ [red]Agent '{agent_name}' not found[/red]")
            return

        agent_path = cloner.get_agent_path(agent_name)
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
                    rprint(f"✅ [green]Dependencies installed: {package_count} packages[/green]")
                else:
                    rprint(f"⚠️ [yellow]Dependency installation failed: {dep_result.error_message}[/yellow]")
            
            rprint("\n🚀 [green]Agent repair completed successfully![/green]")
        else:
            rprint(f"❌ [red]Environment creation failed: {env_result.error_message}[/red]")

    except Exception as e:
        rprint(f"❌ [red]Repair error: {e}[/red]")


@agent.command("backup")
@click.argument("agent_name")
@click.option("--backup-path", type=click.Path(), help="Custom backup directory")
@click.option(
    "--include-env", is_flag=True, help="Include virtual environment in backup"
)
def backup_agent(agent_name: str, backup_path: Optional[str], include_env: bool):
    """Create a backup of an installed agent."""
    try:
        cloner = RepositoryCloner()
        
        if not cloner.is_agent_cloned(agent_name):
            rprint(f"❌ [red]Agent '{agent_name}' not found[/red]")
            return

        agent_path = Path(cloner.get_agent_path(agent_name))
        
        # Create backup directory
        backup_dir = Path(backup_path) if backup_path else Path.home() / ".agenthub/backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_name = f"{agent_name.replace('/', '_')}_{timestamp}"
        backup_path = backup_dir / backup_name
        
        rprint(f"💾 [cyan]Creating backup: {backup_name}[/cyan]")
        
        # Copy agent directory
        shutil.copytree(agent_path, backup_path, 
                       ignore=shutil.ignore_patterns('.venv') if not include_env else None)
        
        rprint(f"✅ [green]Backup created: {backup_path}[/green]")
        
    except Exception as e:
        rprint(f"❌ [red]Backup error: {e}[/red]")


@agent.command("restore")
@click.argument("backup_path", type=click.Path(exists=True))
@click.option("--agent-name", help="Override agent name for restore")
def restore_agent(backup_path: str, agent_name: Optional[str]):
    """Restore an agent from backup."""
    try:
        backup_path = Path(backup_path)
        
        if not backup_path.exists():
            rprint(f"❌ [red]Backup not found: {backup_path}[/red]")
            return

        # Determine agent name
        if agent_name:
            target_name = agent_name
        else:
            # Extract from backup directory name
            backup_name = backup_path.name
            if '_' in backup_name and backup_name.count('_') >= 1:
                target_name = backup_name.rsplit('_', 1)[0].replace('_', '/')
            else:
                target_name = backup_name

        cloner = RepositoryCloner()
        
        if cloner.is_agent_cloned(target_name):
            if not Confirm.ask(f"Agent '{target_name}' exists. Overwrite?"):
                return

        target_path = cloner._get_agent_storage_path(target_name)
        
        rprint(f"🔄 [cyan]Restoring agent: {target_name}[/cyan]")
        
        # Remove existing if present
        if target_path.exists():
            shutil.rmtree(target_path)
        
        # Restore from backup
        shutil.copytree(backup_path, target_path)
        
        rprint(f"✅ [green]Agent restored: {target_name}[/green]")
        rprint(f"📁 Location: {target_path}")
        
    except Exception as e:
        rprint(f"❌ [red]Restore error: {e}[/red]")


@agent.command("cleanup")
@click.option("--dry-run", is_flag=True, help="Show what would be cleaned without doing it")
@click.option("--remove-invalid", is_flag=True, help="Remove invalid agents")
@click.option("--remove-broken-envs", is_flag=True, help="Remove broken virtual environments")
def cleanup_agents(dry_run: bool, remove_invalid: bool, remove_broken_envs: bool):
    """Clean up and optimize agent storage."""
    try:
        cloner = RepositoryCloner()
        agents = cloner.list_cloned_agents()
        
        if not agents:
            rprint("📦 [yellow]No agents to clean up[/yellow]")
            return

        from agentmanager.github.repository_validator import RepositoryValidator
        from agentmanager.environment.environment_setup import EnvironmentSetup
        
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
                    env_info = env_setup._collect_environment_info(path, venv_path)
                    if not env_info.get("venv_exists", False):
                        issues.append("Broken environment")
                except Exception:
                    issues.append("Environment issues")
            
            if issues:
                cleanup_candidates.append((agent_name, path, issues))
        
        if not cleanup_candidates:
            rprint("✅ [green]All agents are healthy[/green]")
            return
        
        rprint(f"\n🧹 [bold]Found {len(cleanup_candidates)} agents needing cleanup:[/bold]")
        
        for agent_name, path, issues in cleanup_candidates:
            rprint(f"  • [cyan]{agent_name}[/cyan]: {', '.join(issues)}")
        
        if dry_run:
            rprint("\n🔍 [yellow]Dry run - no changes made[/yellow]")
            return
        
        if not (remove_invalid or remove_broken_envs):
            if not Confirm.ask("\nClean up these agents?"):
                return
        
        # Perform cleanup
        cleaned = 0
        for agent_name, path, issues in cleanup_candidates:
            if (remove_invalid and "Invalid structure" in issues) or \
               (remove_broken_envs and "Broken environment" in issues) or \
               (not remove_invalid and not remove_broken_envs):
                
                try:
                    if cloner.remove_agent(agent_name):
                        rprint(f"  ✅ [green]Removed: {agent_name}[/green]")
                        cleaned += 1
                except Exception as e:
                    rprint(f"  ❌ [red]Failed to remove {agent_name}: {e}[/red]")
        
        rprint(f"\n🧹 [green]Cleanup completed: {cleaned} agents removed[/green]")
        
    except Exception as e:
        rprint(f"❌ [red]Cleanup error: {e}[/red]")


@agent.command("status")
@click.argument("agent_name", required=False)
def status(agent_name: Optional[str]):
    """Show detailed status of agents or a specific agent."""
    try:
        cloner = RepositoryCloner()
        
        if agent_name:
            # Single agent status
            if not cloner.is_agent_cloned(agent_name):
                rprint(f"❌ [red]Agent '{agent_name}' not found[/red]")
                return
            
            _show_agent_status(agent_name, cloner.get_agent_path(agent_name))
        else:
            # All agents status
            agents = cloner.list_cloned_agents()
            if not agents:
                rprint("📦 [yellow]No agents installed[/yellow]")
                return
            
            rprint(f"📊 [bold]Agent Status Report ({len(agents)} agents)[/bold]")
            
            for agent_name, path in agents.items():
                rprint(f"\n{'='*50}")
                _show_agent_status(agent_name, path)
                
    except Exception as e:
        rprint(f"❌ [red]Status error: {e}[/red]")


def _show_agent_status(agent_name: str, agent_path: str):
    """Show detailed status for a single agent."""
    from agentmanager.github.repository_validator import RepositoryValidator
    from agentmanager.environment.environment_setup import EnvironmentSetup
    
    path = Path(agent_path)
    
    rprint(f"🔧 [bold cyan]Agent: {agent_name}[/bold cyan]")
    rprint(f"📁 Path: {path}")
    
    # Repository validation
    validator = RepositoryValidator()
    try:
        validation_result = validator.validate_repository(str(path))
        rprint(f"✅ Repository: {'Valid' if validation_result.is_valid else 'Invalid'}")
        
        if validation_result.missing_files:
            rprint(f"  ❌ Missing: {', '.join(validation_result.missing_files)}")
        
        if validation_result.validation_errors:
            rprint(f"  ❌ Errors: {', '.join(validation_result.validation_errors)}")
            
    except Exception as e:
        rprint(f"❌ Repository validation: {e}")
    
    # Environment status
    venv_path = path / ".venv"
    if venv_path.exists():
        try:
            env_setup = EnvironmentSetup()
            env_info = env_setup._collect_environment_info(path, venv_path)
            
            rprint(f"🌍 Environment: {'Active' if env_info.get('venv_exists') else 'Broken'}")
            rprint(f"   Python: {env_info.get('python_executable', 'Unknown')}")
            rprint(f"   UV Version: {env_info.get('uv_version', 'Unknown')}")
            
            # Check installed packages
            packages = env_setup._get_installed_packages(str(venv_path))
            rprint(f"   Packages: {len(packages)} installed")
            
        except Exception as e:
            rprint(f"❌ Environment: {e}")
    else:
        rprint("🌍 Environment: Not created")
    
    # File system info
    try:
        total_files = len(list(path.rglob("*")))
        python_files = len(list(path.rglob("*.py")))
        rprint(f"📊 Files: {total_files} total, {python_files} Python")
    except Exception:
        rprint("📊 Files: Unable to count")


@agent.command("migrate")
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
def migrate_agent(agent_name: str, python_version: str, backup: bool, force: bool, base_path: Optional[str]):
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
                force=force
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


@agent.command("clone")
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
def clone_agent(source_agent: str, target_agent: str, include_env: bool, base_path: Optional[str]):
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
                include_env=include_env
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


@agent.command("optimize")
@click.argument("agent_name")
@click.option(
    "--base-path",
    type=click.Path(),
    help="Custom base storage path for agents",
)
def optimize_agent(agent_name: str, base_path: Optional[str]):
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


@agent.command("python-versions")
def list_python_versions():
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


@agent.command("info")
@click.argument("agent_name")
@click.option(
    "--base-path",
    type=click.Path(),
    help="Custom base storage path for agents",
)
def info_agent(agent_name: str, base_path: Optional[str]):
    """Show detailed information about an installed agent."""
    try:
        from agentmanager.core.agents.loader import AgentLoader
        from agentmanager.storage.local_storage import LocalStorage
        
        # Parse agent name
        if "/" not in agent_name:
            rprint("❌ [red]Agent name must be in format 'namespace/name'[/red]")
            rprint("💡 [dim]Example: agentplug/coding-agent[/dim]")
            return

        namespace, name = agent_name.split("/", 1)

        # Initialize system
        storage = LocalStorage()
        if base_path:
            storage.base_storage_path = Path(base_path)
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

        # Show environment info
        from agentmanager.environment.environment_setup import EnvironmentSetup
        agent_path = agent_info.get('path')
        if agent_path:
            venv_path = Path(agent_path) / ".venv"
            if venv_path.exists():
                try:
                    env_setup = EnvironmentSetup()
                    env_info = env_setup._collect_environment_info(agent_path, venv_path)
                    
                    rprint(f"\n🌍 [bold]Environment:[/bold]")
                    rprint(f"   Status: {'Active' if env_info.get('venv_exists') else 'Broken'}")
                    rprint(f"   Python: {env_info.get('python_executable', 'Unknown')}")
                    rprint(f"   UV Version: {env_info.get('uv_version', 'Unknown')}")
                    
                    # Check installed packages
                    packages = env_setup._get_installed_packages(str(venv_path))
                    rprint(f"   Packages: {len(packages)} installed")
                    
                except Exception as e:
                    rprint(f"❌ Environment info: {e}")
            else:
                rprint(f"\n🌍 [bold]Environment:[/bold] Not created")

    except Exception as e:
        rprint(f"❌ [red]Error getting agent info: {e}[/red]")


@agent.command("analyze-deps")
@click.argument("agent_name")
@click.option(
    "--base-path",
    type=click.Path(),
    help="Custom base storage path for agents",
)
def analyze_dependencies(agent_name: str, base_path: Optional[str]):
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
