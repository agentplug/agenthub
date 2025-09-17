# Tools Examples

Examples focused on tool integration, MCP (Model Context Protocol), and tool management using the `run_resources()` method.

## 🔧 Examples Overview

### `agent_loading_with_tools.py`
- **Purpose**: Load agents with tool assignments
- **Features**: Tool discovery, assignment, execution
- **Duration**: ~3 minutes
- **Prerequisites**: MCP tool server running

### `mcp_tool_server.py`
- **Purpose**: MCP tool server implementation using `run_resources()`
- **Features**: Tool registration, HTTP server, MCP protocol
- **Duration**: Continuous (background service)
- **Prerequisites**: FastMCP, uvicorn

### `mcp_tool_client.py`
- **Purpose**: MCP client usage examples
- **Features**: Client connection, tool discovery, execution
- **Duration**: ~2 minutes
- **Prerequisites**: MCP tool server running

## 🚀 Quick Start

### Method 1: Using run_resources() (Recommended)

1. **Start the MCP server with run_resources()**:
   ```python
   from agenthub.core.tools import run_resources

   # This starts the MCP server in the background
   run_resources()
   ```

2. **Run agent examples**:
   ```bash
   python examples/tools/agent_loading_with_tools.py
   ```

### Method 2: Direct Server Execution

1. **Start the MCP server directly**:
   ```bash
   python examples/tools/mcp_tool_server.py
   ```

2. **Run agent examples**:
   ```bash
   python examples/tools/agent_loading_with_tools.py
   ```

3. **Test MCP client**:
   ```bash
   python examples/tools/mcp_tool_client.py
   ```

## 🔧 Available Tools

The MCP server provides these tools:
- `multiply` - Mathematical multiplication
- `add` - Mathematical addition
- `subtract` - Mathematical subtraction
- `divide` - Mathematical division
- `web_search` - Web search functionality
- `compare_numbers` - Number comparison

## 💡 Usage Examples

### Basic Tool Server with run_resources()

```python
#!/usr/bin/env python3
"""
Basic example of starting a tool server using run_resources()
"""
from agenthub.core.tools import tool, run_resources

@tool(name="hello", description="Say hello to someone")
def hello(name: str) -> str:
    return f"Hello, {name}!"

@tool(name="add", description="Add two numbers")
def add(a: int, b: int) -> int:
    return a + b

if __name__ == "__main__":
    print("🚀 Starting tool server with run_resources()...")
    run_resources()  # This starts the MCP server
```

### Using Tools with Agents

```python
#!/usr/bin/env python3
"""
Example of using tools with agents after starting run_resources()
"""
import agenthub as ah

# Start the tool server (run this in a separate terminal or process)
# from agenthub.core.tools import run_resources
# run_resources()

# Load agent with tools
agent = ah.load_agent('agentplug/analysis-agent', tools=['add', 'multiply'])

# Use the agent
result = agent.analyze_text("Calculate 5 + 3 and then multiply by 2")
print(result)
```

### Custom Tool Development

```python
#!/usr/bin/env python3
"""
Example of creating custom tools and using run_resources()
"""
from agenthub.core.tools import tool, run_resources

@tool(name="weather", description="Get weather for a location")
def get_weather(location: str) -> dict:
    # Simulate weather data
    return {
        "location": location,
        "temperature": 22,
        "condition": "sunny"
    }

@tool(name="file_info", description="Get information about a file")
def file_info(filepath: str) -> dict:
    import os
    if os.path.exists(filepath):
        stat = os.stat(filepath)
        return {
            "path": filepath,
            "size": stat.st_size,
            "modified": stat.st_mtime
        }
    return {"error": "File not found"}

if __name__ == "__main__":
    print("🔧 Starting custom tool server...")
    run_resources()
```

## 📋 Tool Development

To add new tools:
1. Edit `mcp_tool_server.py` or create your own server file
2. Add your tool function with `@tool` decorator
3. Use `run_resources()` to start the server
4. Test with `agent_loading_with_tools.py`

## 🐛 Troubleshooting

- **Connection refused**: Make sure MCP server is running with `run_resources()`
- **Tool not found**: Check tool registration in server
- **Import errors**: Install required dependencies
- **Server not starting**: Ensure `run_resources()` is called in the main block
