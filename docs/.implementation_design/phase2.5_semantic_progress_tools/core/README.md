# Core Module - Phase 2.5

**Purpose**: Core functionality for tool injection and MCP integration

## 📁 **Submodules**

### **tools/**
- Tool registry, decorator, metadata management, validation
- Automatic FastMCP integration
- Global tool registration with per-agent access control

### **mcp/**
- MCP server, tool routing, context tracking
- FastMCP server management
- Tool execution routing and concurrency support

## 🔄 **Module Dependencies**

- **tools** → **mcp** (tools must be registered before MCP can route them)
- **mcp** → **runtime** (MCP server must be running before tool injection)
- **runtime** → **sdk** (tool injection must work before SDK can use it)

## 🎯 **Key Features**

- **Tool Registration**: Automatic tool registration with `@tool` decorator
- **MCP Integration**: FastMCP server for tool execution
- **Tool Validation**: Tool signature validation at registration time
- **Metadata Management**: Tool metadata for agent context injection
- **Concurrency Support**: Queue-based approach for tools with side effects
