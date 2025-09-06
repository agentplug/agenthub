# Core/MCP Module - Phase 2.5

**Purpose**: MCP server, tool routing, context tracking, and FastMCP integration

## 🎯 **Module Overview**

The MCP module provides the core infrastructure for tool execution using the Model Context Protocol (MCP). It manages tool routing, agent context tracking, and integrates with FastMCP for seamless tool execution.

## 🔧 **Key Features**

- **MCP Server Management**: Single FastMCP server instance for all tools
- **Tool Routing**: Route tool execution requests to appropriate tools
- **Agent Context Tracking**: Track which agent is calling which tool
- **Concurrency Support**: Handle concurrent tool execution safely
- **Error Handling**: Robust error handling for tool execution failures

## 📋 **Core Components**

### **AgentToolManager**
- Manages tool assignments per agent
- Handles tool execution routing
- Tracks agent context for tool calls

### **MCP Server Integration**
- Single FastMCP server instance
- Tool registration and execution
- MCP protocol compliance

### **Tool Execution Queue**
- Queue-based execution for tools with side effects
- Concurrent execution support
- Error handling and retry logic

## 🔄 **Implementation Flow**

1. **Tool Registration**: Tools are registered with FastMCP server
2. **Agent Assignment**: Tools are assigned to specific agents
3. **Tool Execution**: Agent requests tool execution via MCP
4. **Context Tracking**: System tracks which agent is calling which tool
5. **Result Return**: Tool results are returned to the requesting agent

## 📁 **Documentation Files**

- `01_interface_design.md` - MCP server API, tool routing interface, context tracking
- `02_implementation_details.md` - FastMCP server, tool execution routing, agent context
- `03_testing_strategy.md` - MCP server tests, tool routing tests, concurrency tests
- `04_success_criteria.md` - MCP server working, tool routing working, concurrency working
