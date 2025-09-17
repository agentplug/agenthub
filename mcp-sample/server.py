from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP()


#### Tools ####
# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    print(f"Adding {a} and {b}")
    return a + b


@mcp.tool()
def subtract(a: int, b: int) -> int:
    """Subtract two numbers"""
    print(f"Subtracting {a} and {b}")
    return a - b


@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    print(f"Multiplying {a} and {b}")
    return a * b


@mcp.tool()
def divide(a: int, b: int) -> float:
    """Divide two numbers"""
    print(f"Dividing {a} and {b}")
    return a / b


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="sse")
