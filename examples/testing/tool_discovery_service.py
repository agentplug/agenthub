#!/usr/bin/env python3
"""
Tool Discovery Service - Explores available tools from MCP server

This service connects to the MCP server and discovers all available tools,
providing detailed information about each tool for the framework to use.
"""

import asyncio
import json

from mcp import ClientSession
from mcp.client.sse import sse_client


class ToolDiscoveryService:
    """Service for discovering and exploring available tools."""

    def __init__(self, server_url: str = "http://localhost:8000/sse"):
        self.server_url = server_url
        self.discovered_tools = {}

    async def discover_tools(self) -> dict:
        """
        Discover all available tools from the MCP server.

        Returns:
            Dictionary with tool information
        """
        try:
            async with sse_client(self.server_url) as (read, write):
                async with ClientSession(read, write) as session:
                    # List all available tools
                    tools = await session.list_tools()

                    if hasattr(tools, "tools"):
                        for tool in tools.tools:
                            tool_info = {
                                "name": tool.name,
                                "description": tool.description,
                                "input_schema": getattr(tool, "inputSchema", {}),
                                "output_schema": getattr(tool, "outputSchema", {}),
                                "available": True,
                            }
                            self.discovered_tools[tool.name] = tool_info

                    print(
                        f"🔍 Discovered {len(self.discovered_tools)} tools "
                        f"from MCP server"
                    )
                    return self.discovered_tools

        except Exception as e:
            print(f"❌ Error discovering tools: {e}")
            return {}

    def get_tool_info(self, tool_name: str) -> dict:
        """
        Get information about a specific tool.

        Args:
            tool_name: Name of the tool

        Returns:
            Dictionary with tool information
        """
        return self.discovered_tools.get(tool_name, {})

    def get_available_tools(self) -> list:
        """Get list of available tool names."""
        return list(self.discovered_tools.keys())

    def generate_tool_usage_examples(self, tool_name: str) -> list:
        """
        Generate usage examples for a tool based on its schema.

        Args:
            tool_name: Name of the tool

        Returns:
            List of usage examples
        """
        tool_info = self.get_tool_info(tool_name)
        if not tool_info:
            return []

        input_schema = tool_info.get("input_schema", {})
        properties = input_schema.get("properties", {})

        # Generate example based on tool type and properties
        if tool_name in ["add", "subtract", "multiply", "divide"]:
            return [f'{tool_name}({{"a": "number1", "b": "number2"}})']
        elif tool_name == "greet":
            return [f'{tool_name}({{"name": "string"}})']
        elif tool_name == "get_weather":
            return [f'{tool_name}({{"location": "string"}})']
        elif tool_name == "process_text":
            return [f'{tool_name}({{"text": "string", "operation": "string"}})']
        else:
            # Generic example based on properties
            example_params = {}
            for prop_name, prop_info in properties.items():
                prop_type = prop_info.get("type", "string")
                if prop_type == "number":
                    example_params[prop_name] = "number"
                elif prop_type == "integer":
                    example_params[prop_name] = "integer"
                else:
                    example_params[prop_name] = "string"

            return [f"{tool_name}({json.dumps(example_params)})"]

    def generate_tool_context_for_agent(self, assigned_tools: list) -> dict:
        """
        Generate tool context for an agent based on assigned tools.

        Args:
            assigned_tools: List of tool names assigned to the agent

        Returns:
            Dictionary with tool context
        """
        tool_descriptions = {}
        tool_usage_examples = {}

        for tool_name in assigned_tools:
            tool_info = self.get_tool_info(tool_name)
            if tool_info:
                tool_descriptions[tool_name] = tool_info["description"]
                tool_usage_examples[tool_name] = self.generate_tool_usage_examples(
                    tool_name
                )

        return {
            "available_tools": assigned_tools,
            "tool_descriptions": tool_descriptions,
            "tool_usage_examples": tool_usage_examples,
        }


async def main():
    """Main function to demonstrate tool discovery."""
    print("🔍 Tool Discovery Service - Exploring Available Tools")
    print("=" * 60)

    # Create discovery service
    discovery = ToolDiscoveryService()

    # Discover tools
    print("\n📋 Discovering Tools from MCP Server...")
    tools = await discovery.discover_tools()

    if tools:
        print(f"\n✅ Discovered {len(tools)} tools:")
        for tool_name, tool_info in tools.items():
            print(f"  • {tool_name}: {tool_info['description']}")

        # Show tool information for specific tools
        print("\n🔍 Detailed Tool Information:")
        for tool_name in ["add", "multiply", "greet", "process_text"]:
            if tool_name in tools:
                tool_info = discovery.get_tool_info(tool_name)
                examples = discovery.generate_tool_usage_examples(tool_name)
                print(f"\n  {tool_name}:")
                print(f"    Description: {tool_info['description']}")
                print(f"    Usage examples: {examples}")

        # Generate tool context for an agent
        print("\n🤖 Generating Tool Context for Agent:")
        assigned_tools = ["add", "multiply", "process_text"]
        context = discovery.generate_tool_context_for_agent(assigned_tools)
        print(f"  Assigned tools: {context['available_tools']}")
        print(f"  Descriptions: {context['tool_descriptions']}")
        print(f"  Usage examples: {context['tool_usage_examples']}")

    else:
        print("❌ No tools discovered. Make sure the MCP server is running.")


if __name__ == "__main__":
    asyncio.run(main())
