#!/usr/bin/env python3
"""Step 1 Demo: Core Tools Foundation

This demo shows the basic tool registration and MCP integration capabilities.
"""

import agentmanager as amg
from agentmanager.core.tools import tool, get_available_tools, get_mcp_server

# Define custom tools
@tool(name="greeting_tool", description="Generate personalized greetings")
def greeting_tool(name: str, language: str = "en") -> dict:
    """Generate a greeting in different languages."""
    greetings = {
        "en": f"Hello, {name}!",
        "es": f"¡Hola, {name}!",
        "fr": f"Bonjour, {name}!",
        "de": f"Hallo, {name}!"
    }
    return {
        "greeting": greetings.get(language, greetings["en"]),
        "language": language,
        "name": name
    }

@tool(name="calculator", description="Basic arithmetic operations")
def calculator(operation: str, a: float, b: float) -> dict:
    """Perform basic arithmetic operations."""
    operations = {
        "add": a + b,
        "subtract": a - b,
        "multiply": a * b,
        "divide": a / b if b != 0 else "Error: Division by zero"
    }
    
    if operation not in operations:
        return {"error": f"Unknown operation: {operation}"}
    
    return {
        "operation": operation,
        "a": a,
        "b": b,
        "result": operations[operation]
    }

async def main():
    """Demonstrate Step 1 capabilities."""
    print("🚀 Step 1 Demo: Core Tools Foundation")
    print("=" * 50)
    
    # Show available tools
    print(f"Available tools: {get_available_tools()}")
    
    # Show MCP server info
    mcp_server = get_mcp_server()
    print(f"MCP server: {mcp_server.name}")
    print(f"Tools in MCP server: {len(mcp_server._tool_manager._tools)}")
    
    # Test custom tools through MCP server
    print("\n📝 Testing Custom Tools via MCP:")
    
    # Test greeting tool through MCP
    greeting_result = await mcp_server.call_tool("greeting_tool", {"name": "Alice", "language": "es"})
    print(f"Greeting via MCP: {greeting_result[0].text}")
    
    # Test calculator tool through MCP
    calc_result = await mcp_server.call_tool("calculator", {"operation": "multiply", "a": 5, "b": 3})
    print(f"Calculator via MCP: {calc_result[0].text}")
    
    # Show that direct function calls still work (for comparison)
    print("\n📝 Direct Function Calls (for comparison):")
    direct_greeting = greeting_tool("Bob", "fr")
    direct_calc = calculator("add", 10, 5)
    print(f"Direct greeting: {direct_greeting}")
    print(f"Direct calculator: {direct_calc}")
    
    print("\n✅ Step 1 Demo Complete!")
    print("Tools are registered and ready for agent integration.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
