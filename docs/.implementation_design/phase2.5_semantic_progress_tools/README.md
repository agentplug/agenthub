# Phase 2.5: Tool Injection Implementation Design

**Document Type**: Phase Implementation Design  
**Author**: William  
**Date Created**: 2025-06-28  
**Last Updated**: 2025-06-28  
**Status**: In Progress  
**Purpose**: Implementation design for tool injection using MCP (Model Context Protocol)

## 🎯 **Phase 2.5 Overview**

Phase 2.5 introduces **tool injection** capabilities that allow users to define custom tools and inject them into agents using the Model Context Protocol (MCP). This phase bridges the gap between basic agent execution and full SDK integration.

### **Key Features**
- **Custom Tool Definition**: Users can define tools with simple `@tool` decorator
- **Automatic Tool Registration**: Tools are automatically registered with FastMCP
- **Agent Tool Assignment**: Tools can be assigned to specific agents via `amg.load_agent(tools=[...])`
- **MCP Integration**: Full MCP protocol support for tool execution
- **Concurrent Tool Access**: Multiple agents can use tools simultaneously
- **Agent-Driven Tool Usage**: Agent's AI automatically decides when and how to use tools in any method

### **User Experience**
```python
from agentmanager.core.tools import tool

# Define custom tools
@tool(name="data_analyzer", description="Analyze data")
def my_data_analyzer(data: str) -> dict:
    return {"insights": f"analyzed: {data}"}

@tool(name="sentiment_analysis", description="Analyze sentiment")
def my_sentiment_analyzer(data: str) -> dict:
    return {"insights": f"analyzed: {data}"}

# Load agent with tools
import agentmanager as amg
agent = amg.load_agent(
    base_agent="agentplug/analyzer",
    tools=["data_analyzer", "sentiment_analysis"]
)

# Agent's AI automatically decides when to use tools in ANY method
response = agent.run("What's the weather?")           # Agent might use web_search
result = agent.analyze("sales_data.csv")              # Agent might use data_analyzer
insights = agent.process("customer_feedback.txt")     # Agent might use sentiment_analysis
```

## 📁 **Module Structure**

### **core/tools/**
- **Purpose**: Tool registry, decorator, metadata management, validation
- **Key Features**: `@tool` decorator, automatic FastMCP registration, tool validation
- **Files**: README.md, 01_interface_design.md, 02_implementation_details.md, 03_testing_strategy.md, 04_success_criteria.md

### **core/mcp/**
- **Purpose**: MCP server, tool routing, context tracking
- **Key Features**: FastMCP server, tool execution routing, agent context management
- **Files**: README.md, 01_interface_design.md, 02_implementation_details.md, 03_testing_strategy.md, 04_success_criteria.md

### **runtime/**
- **Purpose**: Tool injection into agent context
- **Key Features**: Tool metadata injection, agent tool access, MCP client integration
- **Files**: README.md, 01_interface_design.md, 02_implementation_details.md, 03_testing_strategy.md, 04_success_criteria.md

### **sdk/**
- **Purpose**: Enhanced `load_agent()` with tool assignment
- **Key Features**: `amg.load_agent(tools=[...])` API, tool assignment logic
- **Files**: README.md, 01_interface_design.md, 02_implementation_details.md, 03_testing_strategy.md, 04_success_criteria.md

### **testing/**
- **Purpose**: Comprehensive testing for Phase 2.5
- **Key Features**: Unit tests, integration tests, MCP testing
- **Files**: README.md, core_testing.md, runtime_testing.md, sdk_testing.md

## 🔄 **Implementation Flow**

1. **Tool Definition**: User defines tools with `@tool` decorator
2. **Automatic Registration**: Tools are automatically registered with FastMCP
3. **Agent Loading**: User loads agent with `amg.load_agent(tools=[...])`
4. **Tool Assignment**: Framework assigns specific tools to agent
5. **Tool Injection**: Tool metadata is injected into agent's AI context
6. **Agent-Driven Execution**: Agent's AI automatically decides when to use tools in any method
7. **MCP Tool Execution**: When agent needs tools, they are executed via MCP

## 🎯 **Success Criteria**

- ✅ `@tool` decorator works for custom tool registration
- ✅ Global tool registry with per-agent access control works
- ✅ Single MCP server with tool routing works
- ✅ Tool metadata injection into agent's AI context works
- ✅ `amg.load_agent(tools=[...])` functionality works
- ✅ Agent's AI automatically decides when to use tools in any method
- ✅ Tool execution via MCP works seamlessly
- ✅ Concurrency support for tool execution works

## 🏗️ **Architecture Understanding**

### **Tool Usage Pattern**
- **Framework Role**: Provides tool injection and MCP client capabilities
- **Agent Role**: Has its own methods (`run`, `analyze`, `process`, etc.)
- **Agent's AI**: Automatically decides when to use tools in ANY method
- **User Experience**: Just calls `agent.any_method()` and tools work automatically

### **Key Architectural Points**
- **No Manual Tool Calls**: Users never call tools manually
- **Agent-Driven Decisions**: Agent's AI decides when and how to use tools
- **Method Agnostic**: Tools work in any agent method, not just `run()`
- **Seamless Integration**: Tool usage is transparent to the user

## 🔗 **Dependencies**

- **Phase 1**: Foundation (runtime, storage, core, CLI)
- **Phase 2**: Auto-install (registry, cache, installer, storage enhancements)
- **FastMCP**: MCP server framework for tool execution
- **MCP Protocol**: Standardized tool communication

## 📊 **Progress Tracking**

- [ ] core/tools module complete
- [ ] core/mcp module complete
- [ ] runtime module complete
- [ ] sdk module complete
- [ ] testing module complete
- [ ] Phase 2.5 testing complete

This phase enables the foundation for advanced agent capabilities while maintaining a simple, clean user experience.
