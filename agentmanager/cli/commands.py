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