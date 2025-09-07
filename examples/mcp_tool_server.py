#!/usr/bin/env python3
"""
AgentManager Tool Server - Framework-level Background Execution Example

This example demonstrates how to use the framework-level run_resources() method
for clean background server execution.
"""

from agentmanager.core.tools import tool, run_resources, get_available_tools

#### Tool Registration using agentmanager.core.tools ####

@tool(name="add", description="Add two numbers together")
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    print(f"[TOOL] Adding {a} + {b}")
    return a + b

@tool(name="subtract", description="Subtract the second number from the first")
def subtract(a: int, b: int) -> int:
    """Subtract the second number from the first."""
    print(f"[TOOL] Subtracting {a} - {b}")
    return a - b

@tool(name="multiply", description="Multiply two numbers")
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    print(f"[TOOL] Multiplying {a} * {b}")
    return a * b

@tool(name="divide", description="Divide the first number by the second")
def divide(a: float, b: float) -> float:
    """Divide the first number by the second."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    print(f"[TOOL] Dividing {a} / {b}")
    return a / b

@tool(name="greet", description="Generate a personalized greeting")
def greet(name: str, greeting: str = "Hello") -> str:
    """Generate a personalized greeting."""
    print(f"[TOOL] Greeting {name} with '{greeting}'")
    return f"{greeting}, {name}!"

@tool(name="get_weather", description="Get weather information for a location (simulated)")
def get_weather(location: str, unit: str = "celsius") -> dict:
    """Get weather information for a location (simulated)."""
    print(f"[TOOL] Getting weather for {location} in {unit}")
    
    # Simulate weather data
    import random
    temp = random.randint(-10, 35) if unit == "celsius" else random.randint(14, 95)
    conditions = ["sunny", "cloudy", "rainy", "snowy", "windy"]
    condition = random.choice(conditions)
    
    return {
        "location": location,
        "temperature": temp,
        "unit": unit,
        "condition": condition,
        "humidity": random.randint(30, 90)
    }

@tool(name="process_text", description="Process text with various operations")
def process_text(text: str, operation: str = "uppercase") -> str:
    """Process text with various operations."""
    print(f"[TOOL] Processing text with operation: {operation}")
    
    operations = {
        "uppercase": text.upper(),
        "lowercase": text.lower(),
        "titlecase": text.title(),
        "reverse": text[::-1],
        "wordcount": str(len(text.split())),
        "charcount": str(len(text))
    }
    
    if operation not in operations:
        raise ValueError(f"Unknown operation: {operation}. Available: {list(operations.keys())}")
    
    return operations[operation]


if __name__ == "__main__":
    print("🚀 AgentManager Tool Server - Framework Background Execution")
    print("=" * 60)
    
    # Show available tools
    tools = get_available_tools()
    print("📋 Available tools:")
    for tool_name in tools:
        print(f"  - {tool_name}")
    
    print("\n✨ Starting server with framework run_resources() method...")
    
    # Use the clean framework-level run_resources() function
    
    run_resources()
