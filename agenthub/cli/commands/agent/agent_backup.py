"""CLI commands for agent backup and restore."""

import shutil
import time
from pathlib import Path
from typing import Optional

import click
from rich import print as rprint
from rich.prompt import Confirm

from agenthub.github.repository_cloner import RepositoryCloner


@click.group()
def agent_backup():
    """Agent backup and restore commands."""
    pass


@agent_backup.command("backup")
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


@agent_backup.command("restore")
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
