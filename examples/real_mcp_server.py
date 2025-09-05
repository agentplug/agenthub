#!/usr/bin/env python3
"""
Real MCP Server - Following Official MCP SDK Patterns

This is a proper MCP server that implements the MCP protocol correctly.
"""

import asyncio
import sys
from mcp.server.fastmcp import FastMCP
from mcp.server.stdio import stdio_server

# Create FastMCP server instance
app = FastMCP("AgentHub Real MCP Server", "1.0.0")

# Register tools using FastMCP decorators
@app.tool(name="calculator", description="Simple calculator for basic math operations")
def calculator(a: int, b: int, operation: str = "add") -> str:
    """Calculate two numbers with specified operation."""
    if operation == "add":
        return f"{a} + {b} = {a + b}"
    elif operation == "multiply":
        return f"{a} × {b} = {a * b}"
    elif operation == "subtract":
        return f"{a} - {b} = {a - b}"
    elif operation == "divide":
        if b == 0:
            return "Error: Division by zero"
        return f"{a} ÷ {b} = {a / b}"
    else:
        return f"Unknown operation: {operation}"

@app.tool(name="greeter", description="Greet someone")
def greeter(person: str = "World") -> str:
    """Say hello to someone."""
    return f"Hello, {person}!"

@app.tool(name="file_info", description="Get information about a file")
def file_info(file_path: str) -> str:
    """Get basic information about a file."""
    import os
    try:
        if not os.path.exists(file_path):
            return f"❌ File {file_path} does not exist"
        
        stat = os.stat(file_path)
        return f"📄 File: {file_path}\n   Size: {stat.st_size:,} bytes\n   Exists: Yes"
    except Exception as e:
        return f"❌ Error: {e}"

# Register resources using FastMCP
@app.resource("file://readme", name="README", description="Project README content")
def readme_resource() -> str:
    """Get README content."""
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error reading README: {e}"

# Register prompts using FastMCP
@app.prompt(name="code_review", description="Review code for best practices")
def code_review_prompt(code: str) -> str:
    """Generate a code review prompt."""
    return f"""Please review the following code for best practices, potential issues, and improvements:

```python
{code}
```

Focus on:
1. Code quality and readability
2. Performance considerations
3. Security issues
4. Best practices adherence
5. Potential bugs or edge cases
"""

def main():
    """Run the MCP server."""
    app.run(transport="stdio")

if __name__ == "__main__":
    main()
