#!/usr/bin/env python3
"""
Tool Demo - Register Tools and Use Them

This example shows:
1. Define tools with @tool decorator
2. Register tools with MCP server
3. Use tools through MCP protocol
"""

import asyncio
import sys
import os
import tempfile

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentmanager.core.tools import tool, ToolDiscovery, ToolRegistry, get_global_registry
from agentmanager.core.mcp import MCPServer, MCPClient


# Define tools with @tool decorator
@tool(name="calculator", description="Simple calculator")
def calculator(a: int, b: int, operation: str = "add") -> str:
    """Calculate two numbers."""
    if operation == "add":
        return f"{a} + {b} = {a + b}"
    elif operation == "multiply":
        return f"{a} × {b} = {a * b}"
    else:
        return f"Unknown operation: {operation}"

@tool(name="greeter", description="Greet someone")
def greeter(person: str = "World") -> str:
    """Say hello to someone."""
    return f"Hello, {person}!"


async def main():
    """Main demo function."""
    print("🚀 Tool Demo - Register and Use Tools")
    print("=" * 40)
    
    # Step 1: Show tools defined
    print("📝 Step 1: Tools Defined")
    print("-" * 25)
    tool_functions = [calculator, greeter]
    for func in tool_functions:
        print(f"✅ {func.__name__}: {func.__doc__}")
    
    # Step 2: Discover tools
    print("\n🔍 Step 2: Discover Tools")
    print("-" * 25)
    discovery = ToolDiscovery()
    discovered_tools = discovery.discover_tools(tool_functions)
    print(f"✅ Discovered {len(discovered_tools)} tools")
    
    # Step 3: Register with MCP server
    print("\n🌐 Step 3: Register with MCP Server")
    print("-" * 35)
    mcp_server = MCPServer(name="Demo Server", version="1.0.0")
    
    for tool_metadata in discovered_tools:
        mcp_server.register_tool(
            tool_metadata.name,
            tool_metadata.description,
            tool_metadata.function
        )
    
    print(f"✅ Registered {mcp_server.get_tool_count()} tools")
    print(f"✅ Tools: {list(mcp_server.tools.keys())}")
    
    # Step 4: Create server script
    print("\n📄 Step 4: Create Server Script")
    print("-" * 30)
    
    server_script = '''
import asyncio
import sys
from mcp.server.fastmcp import FastMCP
from mcp.server.stdio import stdio_server

app = FastMCP("Demo Server", "1.0.0")

@app.tool(name="calculator", description="Simple calculator")
def calculator(a: int, b: int, operation: str = "add") -> str:
    if operation == "add":
        return f"{a} + {b} = {a + b}"
    elif operation == "multiply":
        return f"{a} × {b} = {a * b}"
    else:
        return f"Unknown operation: {operation}"

@app.tool(name="greeter", description="Greet someone")
def greeter(person: str = "World") -> str:
    return f"Hello, {person}!"

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream)

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(server_script)
        server_script_path = f.name
    
    print(f"✅ Server script: {server_script_path}")
    
    # Step 5: Test tool registry directly
    print("\n⚡ Step 5: Test Tool Registry")
    print("-" * 30)
    
    registry = get_global_registry()
    
    print("🔧 Testing tools directly...")
    
    # Test calculator
    result = registry.execute_tool("calculator", a=10, b=5, operation="add")
    print(f"✅ Calculator: {result}")
    
    # Test greeter
    result = registry.execute_tool("greeter", person="AgentHub")
    print(f"✅ Greeter: {result}")
    
    print("\n🎉 Tools are working!")
    print(f"📄 Server script ready at: {server_script_path}")
    print("💡 You can run the server script to test MCP connection")


if __name__ == "__main__":
    print("🚀 Starting Tool Demo...")
    print("This shows tool registration and MCP usage!")
    print()
    
    asyncio.run(main())
