# Runtime Module - Phase 2.5

**Purpose**: Tool injection into agent context, MCP client integration, and agent tool access

## 🎯 **Module Overview**

The runtime module handles the injection of tool metadata and capabilities into agent contexts, enabling agents to discover and use assigned tools. It provides the bridge between the tool registry and agent execution. **The key insight is that agents' AI decides whether and when to use tools in any method - users never call tools manually.**

## 🔧 **Key Features**

- **Tool Metadata Injection**: Inject tool metadata into agent context
- **Agent Tool Access**: Enable agents to discover and use assigned tools
- **MCP Client Integration**: Handle MCP client connections for tool execution
- **Tool Discovery**: Provide tool discovery mechanisms for agents
- **Context Management**: Manage agent context with tool capabilities

## 📋 **Core Components**

### **ToolInjector**
- Injects tool metadata into agent context
- Manages tool discovery for agents
- Handles tool access permissions

### **AgentContextManager**
- Manages agent context with tool capabilities
- Tracks tool usage and performance
- Handles context cleanup

### **MCPClientManager**
- Manages MCP client connections
- Handles tool execution requests
- Provides connection pooling

## 🔄 **Implementation Flow**

1. **Tool Assignment**: Tools are assigned to agents via `amg.load_agent(tools=[...])`
2. **Metadata Injection**: Tool metadata is injected into agent's AI context
3. **Agent Method Call**: User calls any agent method (`run`, `analyze`, `process`, etc.)
4. **AI Decision**: Agent's AI decides whether and when to use tools
5. **Tool Execution**: Agent's AI calls tools via MCP when needed
6. **Result Processing**: Tool results are processed by agent's AI
7. **Response Generation**: Agent returns enhanced response with tool insights

## 📁 **Documentation Files**

- `01_interface_design.md` - Tool injection API, agent context enhancement
- `02_implementation_details.md` - Tool metadata injection, agent tool access
- `03_testing_strategy.md` - Tool injection tests, agent context tests
- `04_success_criteria.md` - Tools injected into agent context, agent can access tools
