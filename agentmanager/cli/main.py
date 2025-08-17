"""Main CLI entry point for AgentHub."""

import json
import sys
from typing import Any

import click
from rich import print as rprint
from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table

from agentmanager.core.agent_loader import AgentLoader
from agentmanager.runtime.agent_runtime import AgentRuntime
from agentmanager.storage.local_storage import LocalStorage
from agentmanager.cli.commands import agent
from agentmanager.cli.config import CLIConfig

console = Console()


def _interactive_parameter_input(method_name: str) -> dict[str, Any]:
    """Interactive parameter input for user-friendly experience."""
    params = {}

    rprint("📝 [cyan]Let's set up the parameters step by step...[/cyan]")

    if "generate" in method_name.lower() or "code" in method_name.lower():
        prompt = Prompt.ask("What code would you like me to generate?", default="")
        if prompt:
            params["prompt"] = prompt

    elif "analyze" in method_name.lower():
        text = Prompt.ask("What text would you like me to analyze?", default="")
        if text:
            params["text"] = text
            analysis_type = Prompt.ask(
                "What type of analysis?",
                choices=["general", "sentiment", "code_quality", "business"],
                default="general",
            )
            params["analysis_type"] = analysis_type

    elif "summarize" in method_name.lower():
        content = Prompt.ask("What content would you like me to summarize?", default="")
        if content:
            params["content"] = content

    elif "explain" in method_name.lower():
        code = Prompt.ask("What code would you like me to explain?", default="")
        if code:
            params["code"] = code

    else:
        # Generic input
        user_input = Prompt.ask(f"Please provide input for {method_name}", default="")
        if user_input:
            params["input"] = user_input

    return params


def _smart_parameter_mapping(method_name: str, user_input: str) -> dict[str, Any]:
    """Intelligently map simple string input to appropriate parameters."""
    if "generate" in method_name.lower() or "code" in method_name.lower():
        return {"prompt": user_input}
    elif "analyze" in method_name.lower():
        return {"text": user_input, "analysis_type": "general"}
    elif "summarize" in method_name.lower():
        return {"content": user_input}
    elif "explain" in method_name.lower():
        return {"code": user_input}
    else:
        return {"input": user_input}


@click.group()
@click.version_option()
def cli():
    """AgentHub - AI Agent Management Platform."""
    pass


@cli.command()
def list():
    """List all available agents."""
    try:
        # Initialize system
        storage = LocalStorage()
        loader = AgentLoader(storage=storage)

        # Discover agents
        agents = loader.discover_agents()

        if not agents:
            rprint("📦 [yellow]No agents found![/yellow]")
            rprint("💡 Install agents first using the setup instructions.")
            return

        # Create a beautiful table
        table = Table(title=f"📦 Available Agents ({len(agents)} found)")
        table.add_column("Agent", style="cyan", no_wrap=True)
        table.add_column("Version", style="magenta")
        table.add_column("Description", style="green")

        for agent in agents:
            namespace = agent.get("namespace", "unknown")
            name = agent.get("name", "unknown")
            version = agent.get("version", "unknown")

            # Get description from loader
            try:
                info = loader.get_agent_info(namespace, name)
                description = info.get("description", "No description available")
                # Truncate long descriptions
                if len(description) > 50:
                    description = description[:47] + "..."
            except Exception:
                description = "Error loading description"

            table.add_row(f"{namespace}/{name}", version, description)

        console.print(table)

        rprint("\n💡 [dim]Use 'agenthub info <agent>' for details[/dim]")
        rprint("🚀 [dim]Use 'agenthub exec <agent> <method> <params>' to run[/dim]")

    except Exception as e:
        rprint(f"❌ [red]Error listing agents: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("agent_name")
def info(agent_name: str):
    """Show detailed information about an agent."""
    try:
        # Parse agent name
        if "/" not in agent_name:
            rprint(
                "❌ [red]Agent name must be in format 'namespace/name' "
                "(e.g., 'agentplug/coding-agent')[/red]"
            )
            sys.exit(1)

        namespace, name = agent_name.split("/", 1)

        # Initialize system
        storage = LocalStorage()
        loader = AgentLoader(storage=storage)

        # Load agent info
        try:
            agent_info = loader.load_agent(namespace, name)
        except Exception as e:
            rprint(f"❌ [red]Agent not found: {agent_name}[/red]")
            rprint(f"Error: {e}")
            sys.exit(1)

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

        # Show usage example
        if methods:
            first_method = methods[0]
            rprint("\n💡 [bold]Example Usage:[/bold]")

            # Get the actual parameter names from the method definition
            method_def = method_defs.get(first_method, {})
            parameters = method_def.get("parameters", {})

            if parameters:
                # Use the first required parameter or first parameter available
                param_name = None
                for param, param_info in parameters.items():
                    if isinstance(param_info, dict) and param_info.get(
                        "required", True
                    ):
                        param_name = param
                        break

                if not param_name and parameters:
                    # Fall back to first parameter if no required ones
                    param_name = list(parameters.keys())[0]

                if param_name:
                    rprint(
                        f"  [dim]agenthub exec {agent_name} {first_method} "
                        f'"{{\\"{param_name}\\": \\"your input\\"}}"[/dim]'
                    )
                else:
                    rprint(
                        f"  [dim]agenthub exec {agent_name} {first_method} "
                        f'"your input"[/dim]'
                    )
            else:
                # No parameters defined, use simple input
                rprint(
                    f"  [dim]agenthub exec {agent_name} {first_method} "
                    f'"your input"[/dim]'
                )

    except Exception as e:
        rprint(f"❌ [red]Error getting agent info: {e}[/red]")
        sys.exit(1)


@cli.command()
@click.argument("agent_name")
@click.argument("method_name")
@click.argument("parameters", default="")
@click.option(
    "--interactive", "-i", is_flag=True, help="Interactive mode - no JSON needed!"
)
def exec(
    agent_name: str, method_name: str, parameters: str = "", interactive: bool = False
):
    """Execute any agent method with full flexibility.

    Examples:
      agenthub exec agentplug/coding-agent generate_code
        '{"prompt": "create hello world"}'
      agenthub exec agentplug/analysis-agent analyze_text
        '{"text": "great product"}'
      agenthub exec agentplug/coding-agent generate_code --interactive
      agenthub exec agentplug/coding-agent generate_code "create a calculator"
    """
    try:
        # Parse agent name
        if "/" not in agent_name:
            rprint("❌ [red]Agent name must be in format 'namespace/name'[/red]")
            rprint("💡 [dim]Example: agentplug/coding-agent[/dim]")
            sys.exit(1)

        namespace, name = agent_name.split("/", 1)

        # Handle interactive mode - no JSON complexity!
        if interactive:
            rprint(f"🎯 [cyan]Interactive mode for {agent_name} → {method_name}[/cyan]")
            params = _interactive_parameter_input(method_name)

        # Handle parameters (JSON or simple text)
        elif parameters:
            try:
                # Try JSON first (for power users)
                if parameters.strip().startswith("{") or parameters.strip().startswith(
                    "["
                ):
                    params = json.loads(parameters)
                    rprint("📋 [dim]Using JSON parameters[/dim]")
                else:
                    # Smart mapping for simple text (user-friendly!)
                    params = _smart_parameter_mapping(method_name, parameters)
                    rprint(f'📋 [dim]Auto-mapped: "{parameters}" → {params}[/dim]')
            except json.JSONDecodeError as e:
                rprint(f"❌ [red]JSON parsing failed: {e}[/red]")
                rprint("💡 [yellow]Tip: Use simple text instead of JSON![/yellow]")
                rprint(
                    f"   [cyan]agenthub exec {agent_name} {method_name} "
                    f'"your simple text here"[/cyan]'
                )
                rprint(
                    f"   [cyan]agenthub exec {agent_name} {method_name} "
                    f"--interactive[/cyan]"
                )
                sys.exit(1)

        # No parameters provided
        else:
            rprint("❌ [red]No parameters provided[/red]")
            rprint("💡 [yellow]Choose your preferred style:[/yellow]")
            rprint(
                f"   [cyan]JSON:[/cyan] agenthub exec {agent_name} {method_name} "
                f'\'{{"key": "value"}}\''
            )
            rprint(
                f"   [cyan]Simple:[/cyan] agenthub exec {agent_name} {method_name} "
                f'"your text here"'
            )
            rprint(
                f"   [cyan]Interactive:[/cyan] agenthub exec {agent_name} "
                f"{method_name} --interactive"
            )
            sys.exit(1)

        # Initialize system
        storage = LocalStorage()
        runtime = AgentRuntime(storage=storage)

        rprint(f"🔧 [cyan]Executing: {agent_name} → {method_name}[/cyan]")
        rprint("⏱️  [dim]Processing...[/dim]")

        # Execute agent
        result = runtime.execute_agent(namespace, name, method_name, params)

        if "result" in result:
            execution_time = result.get("execution_time", 0)
            rprint(f"\n✅ [green]Success![/green] [dim]({execution_time:.1f}s)[/dim]")

            # Format and display result
            agent_result = result["result"]

            # Handle different result types
            if isinstance(agent_result, dict):
                rprint("\n📊 [bold]Result:[/bold]")
                for key, value in agent_result.items():
                    if key == "result" and isinstance(value, str) and len(value) > 200:
                        # Truncate long text results
                        rprint(f"  [cyan]{key}:[/cyan] {value[:200]}...")
                        rprint(
                            f"  [dim](truncated, full result has {len(value)} "
                            f"characters)[/dim]"
                        )
                    else:
                        rprint(f"  [cyan]{key}:[/cyan] {value}")
            elif isinstance(agent_result, str):
                if len(agent_result) > 500:
                    rprint("\n📄 [bold]Generated Content:[/bold]")
                    rprint(
                        "════════════════════════════════════════════════════════════════"
                    )
                    rprint(agent_result[:500] + "...")
                    rprint(
                        f"[dim](truncated, full result has {len(agent_result)} "
                        f"characters)[/dim]"
                    )
                else:
                    rprint("\n📄 [bold]Result:[/bold]")
                    rprint(agent_result)
            else:
                rprint(f"\n📋 [bold]Result:[/bold] {agent_result}")

        else:
            # Handle error
            error_msg = result.get("error", "Unknown error")
            rprint(f"\n❌ [red]Error:[/red] {error_msg}")

            # Show suggestions if available
            if "suggestion" in result:
                rprint(f"💡 [yellow]Suggestion:[/yellow] {result['suggestion']}")

            if "available_methods" in result:
                methods = result["available_methods"]
                rprint(f"🎯 [dim]Available methods: {', '.join(methods)}[/dim]")

            sys.exit(1)

    except Exception as e:
        rprint(f"❌ [red]Execution failed: {e}[/red]")
        sys.exit(1)


@cli.command()
def validate():
    """Validate system health and agent integrity."""
    try:
        # Initialize system
        storage = LocalStorage()
        loader = AgentLoader(storage=storage)

        rprint("🔍 [cyan]Validating AgentHub System...[/cyan]")
        rprint("════════════════════════════════════════════════════════════════")

        # System validation
        rprint("\n📊 [bold]System Health Check:[/bold]")

        try:
            storage.initialize_storage()
            rprint("  ✅ Storage system: [green]OK[/green]")
        except Exception as e:
            rprint(f"  ❌ Storage system: [red]ERROR - {e}[/red]")
            return

        # Agent validation
        try:
            agents = loader.discover_agents()
            rprint(f"  ✅ Agent discovery: [green]Found {len(agents)} agents[/green]")
        except Exception as e:
            rprint(f"  ❌ Agent discovery: [red]ERROR - {e}[/red]")
            return

        if not agents:
            rprint("\n⚠️  [yellow]No agents found to validate[/yellow]")
            return

        # Validate each agent
        rprint(f"\n🤖 [bold]Agent Validation ({len(agents)} agents):[/bold]")

        validation_table = Table()
        validation_table.add_column("Agent", style="cyan", no_wrap=True)
        validation_table.add_column("Status", style="green")
        validation_table.add_column("Issues", style="yellow")

        valid_count = 0

        for agent in agents:
            namespace = agent.get("namespace", "unknown")
            name = agent.get("name", "unknown")
            agent_name = f"{namespace}/{name}"

            try:
                # Try to load the agent
                agent_info = loader.load_agent(namespace, name)
                if agent_info.get("valid", False):
                    validation_table.add_row(agent_name, "✅ VALID", "None")
                    valid_count += 1
                else:
                    validation_table.add_row(
                        agent_name, "❌ INVALID", "Structure issues"
                    )
            except Exception as e:
                validation_table.add_row(agent_name, "❌ ERROR", str(e)[:50])

        console.print(validation_table)

        # Summary
        rprint("\n🎯 [bold]Validation Summary:[/bold]")
        rprint(f"  • Total agents: {len(agents)}")
        rprint(f"  • Valid agents: {valid_count}")
        rprint(f"  • Invalid agents: {len(agents) - valid_count}")

        if valid_count == len(agents):
            rprint("\n🚀 [green]System ready for production use![/green]")
        else:
            rprint(
                f"\n⚠️  [yellow]{len(agents) - valid_count} agents "
                f"need attention[/yellow]"
            )

    except Exception as e:
        rprint(f"❌ [red]Validation failed: {e}[/red]")
        sys.exit(1)


# Add agent management commands
cli.add_command(agent)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
