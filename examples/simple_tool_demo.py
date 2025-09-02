#!/usr/bin/env python3
"""
Minimal demo of AgentHub tool registration - Step 1 features
"""

from agentmanager.core.tool_decorators import tool, get_global_registry


# Create a simple tool
@tool(name="greeter", description="Simple greeting tool")
def say_hello(name: str, style: str = "friendly") -> str:
    """Generate a greeting message."""
    if style == "friendly":
        return f"Hello there, {name}! How are you doing?"
    elif style == "formal":
        return f"Good day, {name}."
    else:
        return f"Hi {name}!"


def main():
    print("🔧 Simple Tool Demo")
    print("-" * 30)
    
    # Show registered tools
    registry = get_global_registry()
    tools = registry.get_all_metadata()
    print(f"📋 Registered tools: {list(tools.keys())}")
    
    # Get tool function
    greeter_func = registry.get_function("greeter")
    
    # Test the tool
    result1 = greeter_func("Alice")
    result2 = greeter_func("Bob", "formal")
    
    print(f"🗣️  Result 1: {result1}")
    print(f"🗣️  Result 2: {result2}")
    
    # Show tool metadata
    metadata = tools["greeter"]
    print(f"📝 Tool description: {metadata.description}")
    print(f"⚙️  Parameters: {list(metadata.parameters.keys())}")
    
    print("✅ Tool registration working!")


if __name__ == "__main__":
    main()
