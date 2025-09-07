#!/usr/bin/env python3
"""
Simple MCP Client for Tool Discovery
"""

import asyncio
import json
from mcp.client.sse import sse_client
from mcp import ClientSession

async def discover_tools_from_server():
    """Discover tools from the MCP server."""
    try:
        async with sse_client("http://localhost:8000/sse") as (read, write):
            async with ClientSession(read, write) as session:
                tools = await session.list_tools()
                return [tool.name for tool in tools.tools]
    except Exception as e:
        print(f"Error discovering tools: {e}")
        return []

def get_available_tools():
    """Synchronous wrapper for tool discovery."""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(discover_tools_from_server())
        finally:
            loop.close()
    except Exception as e:
        print(f"Error in sync wrapper: {e}")
        return []

if __name__ == "__main__":
    tools = get_available_tools()
    print(f"Discovered tools: {tools}")
