"""Display formatting utilities for CLI commands."""

from typing import Any

from rich import print as rprint


def format_agent_result(agent_result: Any, execution_time: float = 0) -> None:
    """Format and display agent execution result."""
    if execution_time > 0:
        rprint(f"\n✅ [green]Success![/green] [dim]({execution_time:.1f}s)[/dim]")

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
            rprint("════════════════════════════════════════════════════════════════")
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


def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text to specified length with ellipsis."""
    if len(text) > max_length:
        return text[: max_length - 3] + "..."
    return text
