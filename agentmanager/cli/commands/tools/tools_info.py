"""CLI commands for tool information and listing (status, list, info)."""

import json
import sys
from typing import Optional

import click
import requests
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from .tools_utils import check_service_health, get_service_url, get_service_info, ensure_service_running

console = Console()


@click.group()
def tools_info():
    """Tool information and listing commands."""
    pass


@tools_info.command("status")
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
        service_url = get_service_url(host, port)
        is_healthy = check_service_health(host, port)
        service_info = get_service_info(host, port) if is_healthy else None

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


@tools_info.command("list")
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
        service_url = get_service_url(host, port)
        ensure_service_running(host, port)

        # Get tools from service
        service_info = get_service_info(host, port)
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


@tools_info.command("info")
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
        service_url = get_service_url(host, port)
        ensure_service_running(host, port)

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
