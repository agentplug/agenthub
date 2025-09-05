"""CLI commands for tool management in AgentHub.

This module provides CLI commands for managing MCP tools and agent-tools assignments.
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from typing import List, Optional

from agentmanager.core.tools import get_global_registry, get_agent_tools_tracker
from agentmanager.core.tools.agent_tools_tracker import AgentToolAssignment

console = Console()


@click.group()
def tools():
    """Tool management commands for AgentHub."""
    pass


@tools.command("list")
def tools_list():
    """List all registered tools."""
    registry = get_global_registry()
    tools_data = registry.get_all_metadata()
    
    if not tools_data:
        console.print("[yellow]No tools registered.[/yellow]")
        return
    
    table = Table(title="🔧 Registered Tools")
    table.add_column("Name", style="cyan")
    table.add_column("Description", style="green")
    table.add_column("Parameters", style="magenta")
    table.add_column("Type", style="yellow")
    table.add_column("Tags", style="blue")
    
    for name, metadata in tools_data.items():
        param_count = len(metadata.parameters)
        func_type = "async" if metadata.is_async else "sync"
        tags_str = ", ".join(metadata.tags) if metadata.tags else "None"
        
        table.add_row(
            name,
            metadata.description[:50] + "..." if len(metadata.description) > 50 else metadata.description,
            str(param_count),
            func_type,
            tags_str
        )
    
    console.print(table)


@tools.command("info")
@click.argument("tool_name")
def tools_info(tool_name: str):
    """Show detailed information about a specific tool."""
    registry = get_global_registry()
    metadata = registry.get_tool(tool_name)
    
    if not metadata:
        console.print(f"[red]Tool '{tool_name}' not found.[/red]")
        return
    
    # Create detailed info panel
    info_text = f"""
[bold cyan]Name:[/bold cyan] {metadata.name}
[bold green]Description:[/bold green] {metadata.description}
[bold magenta]Type:[/bold magenta] {'Async' if metadata.is_async else 'Sync'}
[bold yellow]Created:[/bold yellow] {metadata.created_at.strftime('%Y-%m-%d %H:%M:%S')}
[bold blue]Tags:[/bold blue] {', '.join(metadata.tags) if metadata.tags else 'None'}

[bold]Parameters:[/bold]
"""
    
    for param_name, param_info in metadata.parameters.items():
        param_type = param_info.get('annotation', 'Any')
        default = param_info.get('default')
        default_str = f" = {default}" if default is not None else ""
        info_text += f"  • {param_name}: {param_type}{default_str}\n"
    
    if metadata.return_type:
        info_text += f"\n[bold]Return Type:[/bold] {metadata.return_type}"
    
    console.print(Panel(info_text, title=f"Tool: {tool_name}", border_style="cyan"))


@tools.command("test")
@click.argument("tool_name")
@click.option("--params", "-p", help="Parameters as JSON string")
def tools_test(tool_name: str, params: Optional[str]):
    """Test a tool with given parameters."""
    registry = get_global_registry()
    metadata = registry.get_tool(tool_name)
    
    if not metadata:
        console.print(f"[red]Tool '{tool_name}' not found.[/red]")
        return
    
    try:
        # Parse parameters if provided
        import json
        test_params = json.loads(params) if params else {}
        
        console.print(f"[yellow]Testing tool '{tool_name}'...[/yellow]")
        result = registry.execute_tool(tool_name, **test_params)
        
        console.print(f"[green]✓ Tool executed successfully![/green]")
        console.print(f"[bold]Result:[/bold] {result}")
        
    except Exception as e:
        console.print(f"[red]✗ Tool execution failed: {e}[/red]")


@tools.command("tracker")
def tools_tracker():
    """Show agent-tools tracker status."""
    tracker = get_agent_tools_tracker()
    assignments = tracker.get_all_assignments()
    status = tracker.get_tracker_status()
    
    if not assignments:
        console.print("[yellow]No agent-tool assignments found.[/yellow]")
        return
    
    # Create assignments table
    table = Table(title="🔧 Agent-Tools Tracker")
    table.add_column("Agent", style="cyan")
    table.add_column("Tools", style="green")
    table.add_column("Count", style="magenta")
    table.add_column("Usage", style="yellow")
    table.add_column("Status", style="blue")
    
    for agent_name, tool_names in assignments.items():
        assignment = tracker.get_assignment_info(agent_name)
        usage_count = assignment.usage_count if assignment else 0
        status_text = "Active" if assignment and assignment.is_active else "Inactive"
        
        table.add_row(
            agent_name,
            ", ".join(tool_names),
            str(len(tool_names)),
            str(usage_count),
            status_text
        )
    
    console.print(table)
    
    # Show summary stats
    stats_text = f"""
[bold]Summary Statistics:[/bold]
• Total Agents: {status['total_agents']}
• Active Agents: {status['active_agents']}
• Total Tools: {status['total_tools']}
• Total Assignments: {status['total_assignments']}
"""
    console.print(Panel(stats_text, title="Tracker Statistics", border_style="green"))


@tools.command("assign")
@click.argument("agent_name")
@click.argument("tool_names", nargs=-1)
def tools_assign(agent_name: str, tool_names: List[str]):
    """Assign tools to an agent."""
    if not tool_names:
        console.print("[red]Please provide at least one tool name.[/red]")
        return
    
    tracker = get_agent_tools_tracker()
    
    try:
        tracker.assign_tools_to_agent(agent_name, list(tool_names))
        console.print(f"[green]✓ Assigned tools {list(tool_names)} to agent {agent_name}[/green]")
    except ValueError as e:
        console.print(f"[red]✗ Assignment failed: {e}[/red]")


@tools.command("agent")
@click.argument("agent_name")
def tools_agent(agent_name: str):
    """Show tools assigned to a specific agent."""
    tracker = get_agent_tools_tracker()
    tool_names = tracker.get_agent_tools(agent_name)
    assignment = tracker.get_assignment_info(agent_name)
    
    if not tool_names:
        console.print(f"[yellow]Agent '{agent_name}' has no assigned tools.[/yellow]")
        return
    
    # Create agent info panel
    info_text = f"""
[bold cyan]Agent:[/bold cyan] {agent_name}
[bold green]Assigned Tools:[/bold green] {', '.join(tool_names)}
[bold magenta]Tool Count:[/bold magenta] {len(tool_names)}
[bold yellow]Usage Count:[/bold yellow] {assignment.usage_count if assignment else 0}
[bold blue]Last Used:[/bold blue] {assignment.last_used.strftime('%Y-%m-%d %H:%M:%S') if assignment and assignment.last_used else 'Never'}
[bold red]Status:[/bold red] {'Active' if assignment and assignment.is_active else 'Inactive'}
"""
    
    console.print(Panel(info_text, title=f"Agent Tools: {agent_name}", border_style="cyan"))


@tools.command("stats")
def tools_stats():
    """Show tool usage statistics."""
    tracker = get_agent_tools_tracker()
    tool_stats = tracker.get_tool_usage_stats()
    agent_stats = tracker.get_agent_usage_stats()
    
    if not tool_stats:
        console.print("[yellow]No usage statistics available.[/yellow]")
        return
    
    # Tool usage stats
    tool_table = Table(title="📊 Tool Usage Statistics")
    tool_table.add_column("Tool", style="cyan")
    tool_table.add_column("Agent Count", style="green")
    
    for tool_name, count in sorted(tool_stats.items()):
        tool_table.add_row(tool_name, str(count))
    
    console.print(tool_table)
    
    # Agent usage stats
    if agent_stats:
        agent_table = Table(title="📊 Agent Usage Statistics")
        agent_table.add_column("Agent", style="cyan")
        agent_table.add_column("Usage Count", style="green")
        
        for agent_name, count in sorted(agent_stats.items()):
            agent_table.add_row(agent_name, str(count))
        
        console.print(agent_table)


@tools.command("remove")
@click.argument("agent_name")
def tools_remove(agent_name: str):
    """Remove all tools from an agent."""
    tracker = get_agent_tools_tracker()
    
    if agent_name not in tracker._agent_assignments:
        console.print(f"[yellow]Agent '{agent_name}' has no tool assignments.[/yellow]")
        return
    
    tracker.remove_agent_tools(agent_name)
    console.print(f"[green]✓ Removed all tools from agent {agent_name}[/green]")
