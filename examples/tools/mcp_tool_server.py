#!/usr/bin/env python3
"""
AgentManager Tool Server - Framework-level Background Execution Example

This example demonstrates how to use the framework-level run_resources() method
for clean background server execution.
"""

from agentmanager.core.tools import tool, run_resources, get_available_tools

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


@tool(name="web_search", description="Search the web for a query and return summarized results")
def web_search(query: str) -> list:
    """
    Search the web for a query using DuckDuckGo and return summarized results.

    Args:
        query (str): The search query.

    Returns:
        list: A list of dictionaries with 'title', 'url', and 'snippet' for each result.
    """
    print(f"[TOOL] Performing web search for: '{query}' (max_results={10})")
    try:
        from ddgs import DDGS
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        raise ImportError("Required packages 'ddgs', 'requests', and 'beautifulsoup4' are not installed.")

    ddg = DDGS()
    results = []
    for r in ddg.text(query, max_results=5):
        url = r.get("href")
        title = r.get("title", "")
        snippet = ""
        if url:
            try:
                html = requests.get(url, timeout=10).text
                soup = BeautifulSoup(html, "html.parser")
                # crude text extraction: first 2 paragraphs
                paragraphs = [p.get_text() for p in soup.find_all("p")]
                snippet = " ".join(paragraphs)
            except Exception as e:
                snippet = f"Error fetching page: {e}"
        results.append({
            "title": title,
            "url": url,
            "snippet": snippet
        })
    return {"results": results}

@tool(name="compare_numbers", description="Compare two numbers and answer which one is larger")
def compare_numbers(a: float, b: float) -> str:
    """Compare two numbers and return the larger one."""
    print(f"[TOOL] Comparing {a} and {b}")
    if type(a) != float:
        a = float(a)
    if type(b) != float:
        b = float(b)

    return f"The larger number is {float(max(a, b))}"


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
