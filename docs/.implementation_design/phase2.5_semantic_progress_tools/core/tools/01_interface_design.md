# Core/Tools Interface Design - Phase 2.5

**Document Type**: Interface Design
**Module**: core/tools
**Phase**: 2.5
**Status**: Draft

## 🎯 **Purpose**

Define the public interfaces for tool registration, management, and FastMCP integration.

## 🔧 **Core Interfaces**

### **1. Tool Decorator Interface**

```python
from agenthub.core.tools import tool

@tool(name: str, description: str = "")
def tool_function(*args, **kwargs) -> Any:
    """Tool function implementation"""
    pass
```

**Parameters**:
- `name`: Unique tool name for registration
- `description`: Tool description for agent context

**Returns**: Decorated function (same function, registered automatically)

### **2. Tool Registry Interface**

```python
from agenthub.core.tools import get_available_tools, get_mcp_server

# Get list of available tools
tools: List[str] = get_available_tools()

# Get MCP server instance
mcp_server = get_mcp_server()
```

### **3. Tool Metadata Interface**

```python
from typing import Dict, Any

ToolMetadata = {
    "name": str,
    "description": str,
    "function": Callable,
    "parameters": Dict[str, Any],
    "return_type": type,
    "namespace": str  # "custom" or "builtin"
}
```

## 🔄 **Tool Registration Flow**

### **1. User Defines Tool**
```python
@tool(name="data_analyzer", description="Analyze data")
def my_data_analyzer(data: str) -> dict:
    return {"insights": f"analyzed: {data}"}
```

### **2. Automatic Registration**
- Tool is automatically registered with FastMCP
- Tool is added to global registry
- Tool metadata is created
- Tool validation is performed

### **3. Tool Discovery**
```python
# Get available tools
available_tools = get_available_tools()
# Returns: ["data_analyzer", "sentiment_analysis", ...]
```

## 🛠️ **FastMCP Integration**

### **Internal FastMCP Usage**
```python
from fastmcp import FastMCP

# Global MCP server instance
mcp_server = FastMCP("AgentHub Tools")

# Tool registration with FastMCP
@mcp_server.tool()
def tool_wrapper(**kwargs):
    return original_function(**kwargs)
```

### **Tool Execution via MCP**
```python
from fastmcp import Client

# Create MCP client
client = Client(mcp_server)

# Execute tool
result = await client.call_tool("data_analyzer", {"data": "sample"})
```

## 🔒 **Tool Access Control**

### **Per-Agent Tool Assignment**
```python
# Tools are assigned to agents, not globally accessible
agent_tools = {
    "agent_1": ["data_analyzer", "file_processor"],
    "agent_2": ["sentiment_analysis", "text_processor"]
}
```

### **Tool Namespace Support**
```python
# Built-in tools
builtin_tools = ["file_reader", "data_processor"]

# Custom tools
custom_tools = ["data_analyzer", "sentiment_analysis"]

# Future: Explicit namespacing
# tools = ["builtin.file_reader", "custom.data_analyzer"]
```

## ⚡ **Tool Validation**

### **Signature Validation**
```python
def validate_tool_signature(func: Callable) -> bool:
    """Validate tool function signature"""
    # Check parameter types
    # Check return type
    # Check function name
    pass
```

### **Tool Name Validation**
```python
def validate_tool_name(name: str) -> bool:
    """Validate tool name uniqueness"""
    # Check name format
    # Check uniqueness
    # Check reserved names
    pass
```

## 🔄 **Error Handling**

### **Tool Registration Errors**
```python
class ToolRegistrationError(Exception):
    """Tool registration failed"""
    pass

class ToolNameConflictError(Exception):
    """Tool name already exists"""
    pass

class ToolValidationError(Exception):
    """Tool validation failed"""
    pass
```

### **Tool Execution Errors**
```python
class ToolExecutionError(Exception):
    """Tool execution failed"""
    pass

class ToolNotFoundError(Exception):
    """Tool not found"""
    pass
```

## 📊 **Tool Metadata Structure**

```python
{
    "name": "data_analyzer",
    "description": "Analyze data",
    "function": <function my_data_analyzer>,
    "parameters": {
        "data": {"type": "str", "required": True}
    },
    "return_type": "dict",
    "namespace": "custom",
    "examples": [
        "data_analyzer('sales_data.csv')"
    ]
}
```

## 🎯 **Success Criteria**

- ✅ `@tool` decorator works for tool definition
- ✅ Tools are automatically registered with FastMCP
- ✅ Global tool registry maintains tool list
- ✅ Tool validation works at registration time
- ✅ Tool metadata is created and accessible
- ✅ Tool access control works per-agent
- ✅ Error handling works for all failure cases
