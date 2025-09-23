"""Shared utilities for CLI agent management commands."""

from pathlib import Path

from rich import print as rprint
from rich.console import Console
from rich.table import Table

from agenthub.github.repository_cloner import RepositoryCloner
from agenthub.github.repository_validator import RepositoryValidator

console = Console()


def display_simple_agent_list(agents: dict[str, str]) -> None:
    """Display simple agent list with descriptions."""
    from agenthub.core.agents.loader import AgentLoader
    from agenthub.storage.local_storage import LocalStorage

    table = Table(title=f"📦 Installed Agents ({len(agents)})")
    table.add_column("Agent", style="cyan", no_wrap=True)
    table.add_column("Version", style="magenta")
    table.add_column("Description", style="green")

    # Initialize loader to get agent descriptions
    storage = LocalStorage()
    loader = AgentLoader(storage=storage)

    for agent_name, _path in agents.items():
        try:
            # Parse agent name
            if "/" in agent_name:
                namespace, name = agent_name.split("/", 1)

                # Try to load agent info for description
                try:
                    agent_info = loader.load_agent(namespace, name)
                    version = agent_info.get("version", "unknown")
                    description = agent_info.get(
                        "description", "No description available"
                    )

                    # Truncate long descriptions
                    if len(description) > 50:
                        description = description[:47] + "..."

                except Exception:
                    # Fallback if agent info can't be loaded
                    version = "unknown"
                    description = "Error loading description"
            else:
                version = "unknown"
                description = "Invalid agent name format"

        except Exception:
            version = "unknown"
            description = "Error loading agent info"

        table.add_row(agent_name, version, description)

    console.print(table)


def display_detailed_agent_list(
    agents: dict[str, str], cloner: RepositoryCloner
) -> None:
    """Display detailed agent information."""
    validator = RepositoryValidator()

    table = Table(title=f"📦 Detailed Agent Information ({len(agents)})")
    table.add_column("Agent", style="cyan")
    table.add_column("Path", style="green")
    table.add_column("Status", style="magenta")
    table.add_column("Files", style="yellow")
    table.add_column("Python Files", style="blue")

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
            table.add_row(agent_name, path, "❌ Error", str(e), "N/A")

    console.print(table)


def show_agent_status(agent_name: str, agent_path: str) -> None:
    """Show detailed status for a single agent."""
    from agenthub.environment.environment_setup import EnvironmentSetup

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

            status = "Active" if env_info.get("venv_exists") else "Broken"
            rprint(f"🌍 Environment: {status}")
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
