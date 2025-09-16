# Core/Tools Implementation Details - Phase 2.5

**Document Type**: Implementation Details
**Module**: core/tools
**Phase**: 2.5
**Status**: Draft

## 🎯 **Purpose**

Detailed implementation of tool registry, decorator, metadata management, and FastMCP integration.

## 🏗️ **Architecture Overview**

```
User Code
├── @tool decorator
├── Tool function definition
└── Tool usage

Core/Tools Module
├── ToolRegistry (Singleton)
├── @tool decorator
├── FastMCP integration
└── Tool metadata management

FastMCP
├── MCP server instance
├── Tool registration
└── Tool execution
```

## 🔧 **Core Implementation**

### **1. ToolRegistry Class**

```python
# agenthub/core/tools/registry.py
from fastmcp import FastMCP
from typing import Dict, List, Callable, Any, Optional
import threading
import inspect
from dataclasses import dataclass

@dataclass
class ToolMetadata:
    name: str
    description: str
    function: Callable
    parameters: Dict[str, Any]
    return_type: type
    namespace: str = "custom"

class ToolRegistry:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.mcp_server = FastMCP("AgentHub Tools")
            self.registered_tools: Dict[str, ToolMetadata] = {}
            self._initialized = True

    def register_tool(self, name: str, func: Callable, description: str = "") -> Callable:
        """Register a tool with FastMCP automatically"""
        # Validate tool
        self._validate_tool(name, func)

        # Create tool metadata
        metadata = self._create_tool_metadata(name, func, description)

        # Register with FastMCP
        self._register_with_fastmcp(name, func, description)

        # Store in registry
        self.registered_tools[name] = metadata

        return func

    def _validate_tool(self, name: str, func: Callable):
        """Validate tool before registration"""
        # Check name uniqueness
        if name in self.registered_tools:
            raise ToolNameConflictError(f"Tool '{name}' already exists")

        # Check function signature
        if not callable(func):
            raise ToolValidationError(f"Tool '{name}' is not callable")

        # Check parameter types (basic validation)
        sig = inspect.signature(func)
        for param_name, param in sig.parameters.items():
            if param.annotation == inspect.Parameter.empty:
                # Warn about missing type hints
                pass

    def _create_tool_metadata(self, name: str, func: Callable, description: str) -> ToolMetadata:
        """Create tool metadata"""
        sig = inspect.signature(func)
        parameters = {}

        for param_name, param in sig.parameters.items():
            parameters[param_name] = {
                "type": param.annotation if param.annotation != inspect.Parameter.empty else Any,
                "required": param.default == inspect.Parameter.empty
            }

        return ToolMetadata(
            name=name,
            description=description,
            function=func,
            parameters=parameters,
            return_type=sig.return_annotation if sig.return_annotation != inspect.Parameter.empty else Any,
            namespace="custom"
        )

    def _register_with_fastmcp(self, name: str, func: Callable, description: str):
        """Register tool with FastMCP"""
        @self.mcp_server.tool()
        def tool_wrapper(**kwargs):
            return func(**kwargs)

        # Set tool metadata
        tool_wrapper.__name__ = name
        tool_wrapper.__doc__ = description

        return tool_wrapper

    def get_available_tools(self) -> List[str]:
        """Get list of available tool names"""
        return list(self.registered_tools.keys())

    def get_tool_metadata(self, name: str) -> Optional[ToolMetadata]:
        """Get tool metadata by name"""
        return self.registered_tools.get(name)

    def get_mcp_server(self) -> FastMCP:
        """Get the FastMCP server instance"""
        return self.mcp_server
```

### **2. Tool Decorator**

```python
# agenthub/core/tools/__init__.py
from .registry import ToolRegistry, ToolMetadata
from typing import List, Optional

# Global registry instance
_registry = ToolRegistry()

def tool(name: str, description: str = ""):
    """Decorator for registering tools automatically"""
    def decorator(func):
        return _registry.register_tool(name, func, description)
    return decorator

def get_available_tools() -> List[str]:
    """Get list of available tools"""
    return _registry.get_available_tools()

def get_tool_metadata(name: str) -> Optional[ToolMetadata]:
    """Get tool metadata by name"""
    return _registry.get_tool_metadata(name)

def get_mcp_server():
    """Get the MCP server instance"""
    return _registry.get_mcp_server()
```

### **3. Tool Validation**

```python
# agenthub/core/tools/validator.py
import inspect
from typing import Callable, Any
from .exceptions import ToolValidationError, ToolNameConflictError

class ToolValidator:
    @staticmethod
    def validate_tool_name(name: str, existing_tools: List[str]) -> bool:
        """Validate tool name"""
        if not name or not isinstance(name, str):
            raise ToolValidationError("Tool name must be a non-empty string")

        if name in existing_tools:
            raise ToolNameConflictError(f"Tool '{name}' already exists")

        # Check for reserved names
        reserved_names = ["list_tools", "call_tool", "get_metadata"]
        if name in reserved_names:
            raise ToolValidationError(f"Tool name '{name}' is reserved")

        return True

    @staticmethod
    def validate_tool_function(func: Callable) -> bool:
        """Validate tool function"""
        if not callable(func):
            raise ToolValidationError("Tool must be callable")

        # Check if function has proper signature
        sig = inspect.signature(func)
        if len(sig.parameters) == 0:
            raise ToolValidationError("Tool function must accept at least one parameter")

        return True
```

### **4. Error Handling**

```python
# agenthub/core/tools/exceptions.py
class ToolError(Exception):
    """Base exception for tool-related errors"""
    pass

class ToolRegistrationError(ToolError):
    """Tool registration failed"""
    pass

class ToolNameConflictError(ToolError):
    """Tool name already exists"""
    pass

class ToolValidationError(ToolError):
    """Tool validation failed"""
    pass

class ToolExecutionError(ToolError):
    """Tool execution failed"""
    pass

class ToolNotFoundError(ToolError):
    """Tool not found"""
    pass
```

## 🔄 **Tool Registration Flow**

### **1. User Defines Tool**
```python
@tool(name="data_analyzer", description="Analyze data")
def my_data_analyzer(data: str) -> dict:
    return {"insights": f"analyzed: {data}"}
```

### **2. Decorator Processing**
1. `@tool` decorator is called with name and description
2. Decorator function is created and returned
3. When function is defined, decorator function is called with the actual function

### **3. Tool Registration**
1. `register_tool()` is called with name, function, and description
2. Tool validation is performed
3. Tool metadata is created
4. Tool is registered with FastMCP
5. Tool is stored in global registry

### **4. Tool Discovery**
1. `get_available_tools()` returns list of registered tool names
2. `get_tool_metadata()` returns metadata for specific tool
3. `get_mcp_server()` returns FastMCP server instance

## 🚀 **FastMCP Integration**

### **MCP Server Management**
```python
# Single global MCP server instance
mcp_server = FastMCP("AgentHub Tools")

# Tools are registered as they are defined
@mcp_server.tool()
def tool_wrapper(**kwargs):
    return original_function(**kwargs)
```

### **Tool Execution**
```python
# Tools are executed via MCP client
from fastmcp import Client

client = Client(mcp_server)
result = await client.call_tool("data_analyzer", {"data": "sample"})
```

## 🔒 **Concurrency Support**

### **Thread Safety**
- Singleton pattern with thread-safe initialization
- Thread locks for registry access
- FastMCP handles concurrent tool execution

### **Tool Execution Queue**
```python
# For tools with side effects, use queue-based execution
import asyncio
from asyncio import Queue

class ToolExecutionQueue:
    def __init__(self):
        self.queue = Queue()
        self.running = False

    async def execute_tool(self, tool_name: str, arguments: dict):
        """Execute tool with queuing for side effects"""
        await self.queue.put((tool_name, arguments))
        if not self.running:
            await self._process_queue()

    async def _process_queue(self):
        """Process tool execution queue"""
        self.running = True
        while not self.queue.empty():
            tool_name, arguments = await self.queue.get()
            # Execute tool
            await self._execute_single_tool(tool_name, arguments)
        self.running = False
```

## 📊 **Tool Metadata Management**

### **Metadata Structure**
```python
@dataclass
class ToolMetadata:
    name: str
    description: str
    function: Callable
    parameters: Dict[str, Any]
    return_type: type
    namespace: str = "custom"
    examples: List[str] = None
    version: str = "1.0.0"
    created_at: datetime = None
```

### **Metadata Usage**
- Agent context injection
- Tool discovery and selection
- Tool usage examples
- Tool validation and error handling

## 🎯 **Success Criteria**

- ✅ Tool registry singleton works correctly
- ✅ `@tool` decorator registers tools automatically
- ✅ FastMCP integration works seamlessly
- ✅ Tool validation catches errors at registration time
- ✅ Tool metadata is created and accessible
- ✅ Thread safety is maintained
- ✅ Error handling covers all failure cases
- ✅ Tool discovery works for agent assignment
