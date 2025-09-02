"""CLI commands for tool management (unregister)."""

import sys

import click
from rich import print as rprint

from agentmanager.core.tools import get_global_registry, get_global_registration_manager


@click.group()
def tools_manage():
    """Tool management commands."""
    pass


@tools_manage.command("unregister")
@click.argument("tool_name")
@click.option(
    "--force", 
    is_flag=True, 
    help="Force unregistration without confirmation"
)
def unregister_tool(tool_name: str, force: bool):
    """Unregister a tool from the registry."""
    try:
        # Check if tool exists in global registry
        registry = get_global_registry()
        if not registry.get_tool(tool_name):
            rprint(f"❌ [red]Tool '{tool_name}' is not registered[/red]")
            rprint("💡 [dim]Use 'agenthub tools list' to see available tools[/dim]")
            sys.exit(1)

        # Confirm unregistration
        if not force:
            if not click.confirm(f"Unregister tool '{tool_name}'?"):
                rprint("❌ [yellow]Unregistration cancelled[/yellow]")
                return

        # Unregister the tool
        registration_manager = get_global_registration_manager()
        success = registration_manager.unregister_tool(tool_name)
        
        if success:
            rprint(f"✅ [green]Tool '{tool_name}' unregistered successfully![/green]")
            rprint("💡 [dim]Note: This only affects the current session. Restart the service to persist changes.[/dim]")
        else:
            rprint(f"❌ [red]Failed to unregister tool '{tool_name}'[/red]")

    except Exception as e:
        rprint(f"❌ [red]Failed to unregister tool: {e}[/red]")
        sys.exit(1)
