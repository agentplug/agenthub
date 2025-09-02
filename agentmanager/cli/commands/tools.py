"""CLI commands for tool management in AgentHub.

This module provides CLI commands for managing the tool registry service,
including start, stop, status, list, unregister, and restart operations.
"""

import json
import os
import signal
import sys
import time
from pathlib import Path
from typing import Optional

import click
import requests
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from agentmanager.core.tools import (
    ToolServiceHost, ServiceConfiguration, get_global_service_host,
    is_service_running, get_global_registry, get_global_registration_manager
)

console = Console()


def _get_service_url(host: str = "127.0.0.1", port: int = 8000) -> str:
    """Get the service URL."""
    return f"http://{host}:{port}"


def _check_service_health(host: str = "127.0.0.1", port: int = 8000) -> bool:
    """Check if the tool service is healthy."""
    try:
        response = requests.get(f"{_get_service_url(host, port)}/health", timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False


def _get_service_info(host: str = "127.0.0.1", port: int = 8000) -> Optional[dict]:
    """Get service information."""
    try:
        response = requests.get(f"{_get_service_url(host, port)}/tools/", timeout=2)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.RequestException:
        return None


@click.group()
def tools():
    """Tool management commands for AgentHub."""
    pass


@tools.command("start")
@click.option(
    "--host", 
    default="127.0.0.1", 
    help="Host to bind the service to"
)
@click.option(
    "--port", 
    type=int, 
    default=8000, 
    help="Port to bind the service to"
)
@click.option(
    "--background", 
    is_flag=True, 
    default=True,
    help="Start service in background (default: True)"
)
@click.option(
    "--log-level", 
    type=click.Choice(["debug", "info", "warning", "error"]),
    default="info",
    help="Log level for the service"
)
def start_tools(host: str, port: int, background: bool, log_level: str):
    """Start the tool registry service."""
    try:
        # Check if service is already running
        if _check_service_health(host, port):
            rprint(f"✅ [green]Tool service is already running on {host}:{port}[/green]")
            return

        # Check if port is available
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.bind((host, port))
            sock.close()
        except OSError:
            rprint(f"❌ [red]Port {port} is already in use[/red]")
            rprint(f"💡 [yellow]Try a different port: agenthub tools start --port {port + 1}[/yellow]")
            sys.exit(1)

        rprint(f"🚀 [cyan]Starting tool service on {host}:{port}...[/cyan]")

        # Create service configuration
        config = ServiceConfiguration(
            host=host,
            port=port,
            log_level=log_level
        )

        # Start the service
        service_host = ToolServiceHost(config)
        
        if background:
            service_host.start(background=True)
            
            # Wait for service to be ready
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task("Starting service...", total=None)
                
                max_wait = 10
                wait_time = 0
                while wait_time < max_wait:
                    if _check_service_health(host, port):
                        progress.update(task, description="✅ Service started successfully!")
                        break
                    time.sleep(0.5)
                    wait_time += 0.5
                else:
                    progress.update(task, description="❌ Service failed to start")
                    rprint("❌ [red]Service failed to start within timeout[/red]")
                    sys.exit(1)

            rprint(f"✅ [green]Tool service started successfully![/green]")
            rprint(f"🌐 [dim]Service URL: {_get_service_url(host, port)}[/dim]")
            rprint(f"📋 [dim]Use 'agenthub tools status' to check service health[/dim]")
            rprint(f"🛑 [dim]Use 'agenthub tools stop' to stop the service[/dim]")
        else:
            rprint("🔄 [yellow]Starting service in foreground mode...[/yellow]")
            rprint("💡 [dim]Press Ctrl+C to stop the service[/dim]")
            service_host.start(background=False)

    except KeyboardInterrupt:
        rprint("\n🛑 [yellow]Service startup interrupted[/yellow]")
        sys.exit(0)
    except Exception as e:
        rprint(f"❌ [red]Failed to start tool service: {e}[/red]")
        sys.exit(1)


@tools.command("stop")
@click.option(
    "--host", 
    default="127.0.0.1", 
    help="Host where the service is running"
)
@click.option(
    "--port", 
    type=int, 
    default=8000, 
    help="Port where the service is running"
)
def stop_tools(host: str, port: int):
    """Stop the tool registry service."""
    try:
        # Check if service is running
        if not _check_service_health(host, port):
            rprint(f"⚠️  [yellow]Tool service is not running on {host}:{port}[/yellow]")
            return

        rprint(f"🛑 [cyan]Stopping tool service on {host}:{port}...[/cyan]")

        # Get the global service host and stop it
        service_host = get_global_service_host()
        if service_host and service_host.is_running():
            service_host.stop()
            rprint("✅ [green]Tool service stopped successfully![/green]")
        else:
            # Try to stop via HTTP if we can't access the global instance
            try:
                # This is a fallback - in a real implementation, you might want to
                # implement a proper shutdown endpoint
                rprint("⚠️  [yellow]Service instance not accessible, but service appears to be running[/yellow]")
                rprint("💡 [dim]You may need to stop the service manually or restart your terminal[/dim]")
            except Exception:
                rprint("❌ [red]Could not stop service - it may need to be stopped manually[/red]")

    except Exception as e:
        rprint(f"❌ [red]Failed to stop tool service: {e}[/red]")
        sys.exit(1)


@tools.command("status")
@click.option(
    "--host", 
    default="127.0.0.1", 
    help="Host where the service is running"
)
@click.option(
    "--port", 
    type=int, 
    default=8000, 
    help="Port where the service is running"
)
@click.option(
    "--json", 
    "output_json", 
    is_flag=True, 
    help="Output status in JSON format"
)
def status_tools(host: str, port: int, output_json: bool):
    """Check the status of the tool registry service."""
    try:
        service_url = _get_service_url(host, port)
        is_healthy = _check_service_health(host, port)
        service_info = _get_service_info(host, port) if is_healthy else None

        if output_json:
            status_data = {
                "service_url": service_url,
                "is_running": is_healthy,
                "tool_count": service_info.get("count", 0) if service_info else 0,
                "tools": service_info.get("tools", []) if service_info else []
            }
            print(json.dumps(status_data, indent=2))
            return

        # Rich output
        if is_healthy:
            rprint(f"✅ [green]Tool service is running on {service_url}[/green]")
            
            if service_info:
                tool_count = service_info.get("count", 0)
                tools = service_info.get("tools", [])
                
                rprint(f"📊 [cyan]Registered tools: {tool_count}[/cyan]")
                
                if tools:
                    table = Table(title="Registered Tools")
                    table.add_column("Tool Name", style="cyan", no_wrap=True)
                    
                    for tool_name in tools:
                        table.add_row(tool_name)
                    
                    console.print(table)
                else:
                    rprint("📝 [dim]No tools registered yet[/dim]")
                    rprint("💡 [dim]Use @tool decorator or register tools to see them here[/dim]")
            else:
                rprint("⚠️  [yellow]Service is running but tool information unavailable[/yellow]")
        else:
            rprint(f"❌ [red]Tool service is not running on {service_url}[/red]")
            rprint("💡 [dim]Use 'agenthub tools start' to start the service[/dim]")

    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, indent=2))
        else:
            rprint(f"❌ [red]Failed to check service status: {e}[/red]")
        sys.exit(1)


@tools.command("list")
@click.option(
    "--host", 
    default="127.0.0.1", 
    help="Host where the service is running"
)
@click.option(
    "--port", 
    type=int, 
    default=8000, 
    help="Port where the service is running"
)
@click.option(
    "--json", 
    "output_json", 
    is_flag=True, 
    help="Output tools in JSON format"
)
def list_tools(host: str, port: int, output_json: bool):
    """List all registered tools."""
    try:
        service_url = _get_service_url(host, port)
        
        if not _check_service_health(host, port):
            rprint(f"❌ [red]Tool service is not running on {service_url}[/red]")
            rprint("💡 [dim]Use 'agenthub tools start' to start the service[/dim]")
            sys.exit(1)

        # Get tools from service
        service_info = _get_service_info(host, port)
        if not service_info:
            rprint("❌ [red]Failed to retrieve tool information[/red]")
            sys.exit(1)

        tools = service_info.get("tools", [])
        tool_count = service_info.get("count", 0)

        if output_json:
            print(json.dumps({
                "service_url": service_url,
                "tool_count": tool_count,
                "tools": tools
            }, indent=2))
            return

        # Rich output
        if tool_count == 0:
            rprint("📝 [yellow]No tools registered[/yellow]")
            rprint("💡 [dim]Use @tool decorator or register tools to see them here[/dim]")
            return

        rprint(f"📋 [cyan]Registered Tools ({tool_count} found)[/cyan]")
        
        table = Table(title=f"Tools on {service_url}")
        table.add_column("Tool Name", style="cyan", no_wrap=True)
        table.add_column("Status", style="green")
        
        for tool_name in tools:
            table.add_row(tool_name, "✅ Available")
        
        console.print(table)
        
        rprint(f"\n💡 [dim]Use 'agenthub tools info <tool_name>' for detailed information[/dim]")

    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, indent=2))
        else:
            rprint(f"❌ [red]Failed to list tools: {e}[/red]")
        sys.exit(1)


@tools.command("info")
@click.argument("tool_name")
@click.option(
    "--host", 
    default="127.0.0.1", 
    help="Host where the service is running"
)
@click.option(
    "--port", 
    type=int, 
    default=8000, 
    help="Port where the service is running"
)
@click.option(
    "--json", 
    "output_json", 
    is_flag=True, 
    help="Output tool info in JSON format"
)
def info_tool(tool_name: str, host: str, port: int, output_json: bool):
    """Get detailed information about a specific tool."""
    try:
        service_url = _get_service_url(host, port)
        
        if not _check_service_health(host, port):
            rprint(f"❌ [red]Tool service is not running on {service_url}[/red]")
            rprint("💡 [dim]Use 'agenthub tools start' to start the service[/dim]")
            sys.exit(1)

        # Get tool info from service
        try:
            response = requests.get(f"{service_url}/tools/{tool_name}", timeout=5)
            if response.status_code == 404:
                rprint(f"❌ [red]Tool '{tool_name}' not found[/red]")
                rprint("💡 [dim]Use 'agenthub tools list' to see available tools[/dim]")
                sys.exit(1)
            elif response.status_code != 200:
                rprint(f"❌ [red]Failed to get tool info: HTTP {response.status_code}[/red]")
                sys.exit(1)
            
            tool_info = response.json()
        except requests.RequestException as e:
            rprint(f"❌ [red]Failed to get tool info: {e}[/red]")
            sys.exit(1)

        if output_json:
            print(json.dumps(tool_info, indent=2))
            return

        # Rich output
        rprint(f"🔧 [bold cyan]Tool: {tool_info['name']}[/bold cyan]")
        rprint("═" * 50)
        
        rprint(f"📖 [bold]Description:[/bold] {tool_info['description']}")
        rprint(f"🔄 [bold]Type:[/bold] {'Async' if tool_info['is_async'] else 'Sync'}")
        rprint(f"📤 [bold]Return Type:[/bold] {tool_info['return_type']}")
        rprint(f"📅 [bold]Created:[/bold] {tool_info['created_at']}")
        
        if tool_info.get('tags'):
            rprint(f"🏷️  [bold]Tags:[/bold] {', '.join(tool_info['tags'])}")
        
        # Show parameters
        parameters = tool_info.get('parameters', {})
        if parameters:
            rprint(f"\n📋 [bold]Parameters ({len(parameters)}):[/bold]")
            
            param_table = Table()
            param_table.add_column("Parameter", style="cyan", no_wrap=True)
            param_table.add_column("Type", style="magenta")
            param_table.add_column("Required", style="green")
            
            for param_name, param_info in parameters.items():
                param_type = param_info.get('type', 'Any')
                required = param_info.get('required', False)
                param_table.add_row(
                    param_name, 
                    param_type, 
                    "✅ Yes" if required else "❌ No"
                )
            
            console.print(param_table)
        else:
            rprint("\n📋 [bold]Parameters:[/bold] None")

    except Exception as e:
        if output_json:
            print(json.dumps({"error": str(e)}, indent=2))
        else:
            rprint(f"❌ [red]Failed to get tool info: {e}[/red]")
        sys.exit(1)


@tools.command("unregister")
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


@tools.command("restart")
@click.option(
    "--host", 
    default="127.0.0.1", 
    help="Host to bind the service to"
)
@click.option(
    "--port", 
    type=int, 
    default=8000, 
    help="Port to bind the service to"
)
@click.option(
    "--log-level", 
    type=click.Choice(["debug", "info", "warning", "error"]),
    default="info",
    help="Log level for the service"
)
def restart_tools(host: str, port: int, log_level: str):
    """Restart the tool registry service."""
    try:
        rprint("🔄 [cyan]Restarting tool service...[/cyan]")
        
        # Stop the service if running
        if _check_service_health(host, port):
            rprint("🛑 [yellow]Stopping existing service...[/yellow]")
            service_host = get_global_service_host()
            if service_host and service_host.is_running():
                service_host.stop()
                time.sleep(1)  # Give it time to stop
        
        # Start the service
        rprint("🚀 [cyan]Starting service...[/cyan]")
        
        # Create service configuration
        config = ServiceConfiguration(
            host=host,
            port=port,
            log_level=log_level
        )

        # Start the service
        service_host = ToolServiceHost(config)
        service_host.start(background=True)
        
        # Wait for service to be ready
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Restarting service...", total=None)
            
            max_wait = 10
            wait_time = 0
            while wait_time < max_wait:
                if _check_service_health(host, port):
                    progress.update(task, description="✅ Service restarted successfully!")
                    break
                time.sleep(0.5)
                wait_time += 0.5
            else:
                progress.update(task, description="❌ Service failed to restart")
                rprint("❌ [red]Service failed to restart within timeout[/red]")
                sys.exit(1)

        rprint(f"✅ [green]Tool service restarted successfully![/green]")
        rprint(f"🌐 [dim]Service URL: {_get_service_url(host, port)}[/dim]")
        
        # Show current tool count
        service_info = _get_service_info(host, port)
        if service_info:
            tool_count = service_info.get("count", 0)
            rprint(f"📊 [cyan]Registered tools: {tool_count}[/cyan]")

    except Exception as e:
        rprint(f"❌ [red]Failed to restart tool service: {e}[/red]")
        sys.exit(1)
