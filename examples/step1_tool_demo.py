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

def main():
    """Demonstrate Step 1 capabilities."""
    print("🚀 Step 1 Demo: Core Tools Foundation")
    print("=" * 50)
    
    # Show available tools
    print(f"Available tools: {get_available_tools()}")
    
    # Show MCP server info
    mcp_server = get_mcp_server()
    print(f"MCP server: {mcp_server.name}")
    print(f"Tools in MCP server: {len(mcp_server._tool_manager._tools)}")
    
    # Test custom tools
    print("\n📝 Testing Custom Tools:")
    
    # Test greeting tool
    greeting_result = greeting_tool("Alice", "es")
    print(f"Greeting: {greeting_result}")
    
    # Test calculator tool
    calc_result = calculator("multiply", 5, 3)
    print(f"Calculator: {calc_result}")
    
    print("\n✅ Step 1 Demo Complete!")
    print("Tools are registered and ready for agent integration.")

if __name__ == "__main__":
    main()
