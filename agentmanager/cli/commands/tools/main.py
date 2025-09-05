"""CLI commands for tool management in AgentHub.

This module provides CLI commands for managing MCP tools.
"""

import click


@click.group()
def tools():
    """Tool management commands for AgentHub."""
    pass


# TODO: Add MCP tool management commands in Phase 2.5
# tools.add_command(mcp_tools_list)
# tools.add_command(mcp_tools_validate)
# tools.add_command(mcp_tools_test)
