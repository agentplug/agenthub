# Tools Examples

Examples focused on tool integration, MCP (Model Context Protocol), and tool management.

## 🔧 Examples Overview

### `agent_loading_with_tools.py`
- **Purpose**: Load agents with tool assignments
- **Features**: Tool discovery, assignment, execution
- **Duration**: ~3 minutes
- **Prerequisites**: MCP tool server running

### `mcp_tool_server.py`
- **Purpose**: MCP tool server implementation
- **Features**: Tool registration, HTTP server, MCP protocol
- **Duration**: Continuous (background service)
- **Prerequisites**: FastMCP, uvicorn

### `mcp_tool_client.py`
- **Purpose**: MCP client usage examples
- **Features**: Client connection, tool discovery, execution
- **Duration**: ~2 minutes
- **Prerequisites**: MCP tool server running

## 🚀 Quick Start

1. **Start the MCP server**:
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

## 📋 Tool Development

To add new tools:
1. Edit `mcp_tool_server.py`
2. Add your tool function with `@tool` decorator
3. Restart the MCP server
4. Test with `agent_loading_with_tools.py`

## 🐛 Troubleshooting

- **Connection refused**: Make sure MCP server is running
- **Tool not found**: Check tool registration in server
- **Import errors**: Install required dependencies
