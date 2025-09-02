"""CLI commands for tool service lifecycle management (start, stop, restart)."""

import sys
import time
from typing import Optional

import click
from rich import print as rprint

from agentmanager.core.tools import ToolServiceHost, ServiceConfiguration, get_global_service_host
from .tools_utils import check_service_health, get_service_url, wait_for_service_ready


@click.group()
def tools_service():
    """Tool service lifecycle management commands."""
    pass


@tools_service.command("start")
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
        if check_service_health(host, port):
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

        # Create and start service
        config = ServiceConfiguration(host=host, port=port, log_level=log_level)
        service_host = ToolServiceHost(config)
        
        if background:
            service_host.start(background=True)
            
            if not wait_for_service_ready(host, port):
                rprint("❌ [red]Service failed to start within timeout[/red]")
                sys.exit(1)

            rprint(f"✅ [green]Tool service started successfully![/green]")
            rprint(f"🌐 [dim]Service URL: {get_service_url(host, port)}[/dim]")
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


@tools_service.command("stop")
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
        if not check_service_health(host, port):
            rprint(f"⚠️  [yellow]Tool service is not running on {host}:{port}[/yellow]")
            return

        rprint(f"🛑 [cyan]Stopping tool service on {host}:{port}...[/cyan]")

        # Get the global service host and stop it
        service_host = get_global_service_host()
        if service_host and service_host.is_running():
            service_host.stop()
            rprint("✅ [green]Tool service stopped successfully![/green]")
        else:
            rprint("⚠️  [yellow]Service instance not accessible, but service appears to be running[/yellow]")
            rprint("💡 [dim]You may need to stop the service manually or restart your terminal[/dim]")

    except Exception as e:
        rprint(f"❌ [red]Failed to stop tool service: {e}[/red]")
        sys.exit(1)


@tools_service.command("restart")
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
        if check_service_health(host, port):
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
        if not wait_for_service_ready(host, port):
            rprint("❌ [red]Service failed to restart within timeout[/red]")
            sys.exit(1)

        rprint(f"✅ [green]Tool service restarted successfully![/green]")
        rprint(f"🌐 [dim]Service URL: {get_service_url(host, port)}[/dim]")
        
        # Show current tool count
        from .tools_utils import get_service_info
        service_info = get_service_info(host, port)
        if service_info:
            tool_count = service_info.get("count", 0)
            rprint(f"📊 [cyan]Registered tools: {tool_count}[/cyan]")

    except Exception as e:
        rprint(f"❌ [red]Failed to restart tool service: {e}[/red]")
        sys.exit(1)
