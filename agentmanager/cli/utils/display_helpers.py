"""Display formatting utilities for CLI commands."""

from typing import Any

from rich import print as rprint


def format_agent_result(agent_result: Any) -> None:
    """Format and display agent execution result."""
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


def truncate_long_text(text: str, max_length: int = 200) -> str:
    """Truncate long text with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
