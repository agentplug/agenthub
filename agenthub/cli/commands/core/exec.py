"""CLI command for executing agent methods."""

import json
import sys

import click
from rich import print as rprint
from rich.prompt import Prompt

from agenthub.core.agents.loader import AgentLoader
from agenthub.runtime.agent_runtime import AgentRuntime
from agenthub.storage.local_storage import LocalStorage

from ...utils.display_helpers import format_agent_result
from ...utils.parameter_helpers import (
    interactive_parameter_input,
    smart_parameter_mapping,
)


@click.group()
def core_exec():
    """Core exec command group."""
    pass


@core_exec.command("exec")
@click.argument("agent_name")
@click.argument("method_name")
@click.argument("parameters", default="")
@click.option(
    "--interactive", "-i", is_flag=True, help="Interactive mode - no JSON needed!"
)
def exec_agent(
    agent_name: str, method_name: str, parameters: str = "", interactive: bool = False
):
    """Execute any agent method with full flexibility.

    Examples:
      agenthub exec <namespace>/<agent> <method> '{"param": "value"}'
      agenthub exec <namespace>/<agent> <method> --interactive
      agenthub exec <namespace>/<agent> <method> "simple text input"
    """
    try:
        # Parse agent name
        if "/" not in agent_name:
            rprint("❌ [red]Agent name must be in format 'namespace/name'[/red]")
            rprint("💡 [dim]Example: <namespace>/<agent-name>[/dim]")
            sys.exit(1)

        namespace, name = agent_name.split("/", 1)

        # Handle interactive mode - no JSON complexity!
        if interactive:
            rprint(f"🎯 [cyan]Interactive mode for {agent_name} → {method_name}[/cyan]")

            # Load agent info for dynamic parameter handling
            storage = LocalStorage()
            loader = AgentLoader(storage=storage)
            try:
                agent_info = loader.load_agent(namespace, name)
                params = interactive_parameter_input(agent_info, method_name)
            except Exception as e:
                rprint(f"❌ [red]Failed to load agent info: {e}[/red]")
                rprint("💡 [yellow]Falling back to basic parameter input[/yellow]")
                params = {"data": Prompt.ask("Please provide input", default="")}

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
                    # Load agent info for dynamic parameter mapping
                    storage = LocalStorage()
                    loader = AgentLoader(storage=storage)
                    try:
                        agent_info = loader.load_agent(namespace, name)
                        params = smart_parameter_mapping(
                            agent_info, method_name, parameters
                        )
                        rprint(f'📋 [dim]Auto-mapped: "{parameters}" → {params}[/dim]')
                    except Exception as e:
                        rprint(f"❌ [red]Failed to load agent info: {e}[/red]")
                        rprint(
                            "💡 [yellow]Falling back to basic parameter "
                            "mapping[/yellow]"
                        )
                        params = {"data": parameters}
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
            rprint(
                "\n📦 [dim]Use 'agenthub agent install <agent>' to install "
                "new agents[/dim]"
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
            format_agent_result(result["result"], execution_time)

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
