# Core/MCP Interface Design - Phase 2.5

**Document Type**: Interface Design
**Module**: core/mcp
**Phase**: 2.5
**Status**: Draft

## 🎯 **Purpose**

Define the public interfaces for MCP server management, tool routing, context tracking, and FastMCP integration.

## 🔧 **Core Interfaces**

### **1. AgentToolManager Interface**

```python
from agenthub.core.mcp import AgentToolManager
from typing import Dict, List, Any, Optional

# Create tool manager
tool_manager = AgentToolManager()

# Assign tools to agent
assigned_tools = tool_manager.assign_tools_to_agent(
    agent_id: str,
    tool_names: List[str]
) -> List[str]

# Get tools for agent
agent_tools = tool_manager.get_agent_tools(agent_id: str) -> List[str]

# Execute tool
result = await tool_manager.execute_tool(
    tool_name: str,
    arguments: Dict[str, Any]
) -> Any

# Close connections
await tool_manager.close()
```

### **2. MCP Server Interface**

```python
from agenthub.core.mcp import get_mcp_server, get_available_tools

# Get MCP server instance
mcp_server = get_mcp_server()

# Get available tools
available_tools = get_available_tools() -> List[str]

# Get tool metadata
tool_metadata = get_tool_metadata(tool_name: str) -> Optional[Dict[str, Any]]
```

### **3. Tool Execution Interface**

```python
from agenthub.core.mcp import ToolExecutor
from typing import Dict, Any, Optional

# Create tool executor
executor = ToolExecutor()

# Execute tool with context
result = await executor.execute_tool(
    tool_name: str,
    arguments: Dict[str, Any],
    agent_id: str,
    context: Optional[Dict[str, Any]] = None
) -> Any

# Execute tool with retry
result = await executor.execute_tool_with_retry(
    tool_name: str,
    arguments: Dict[str, Any],
    agent_id: str,
    max_retries: int = 3
) -> Any
```

## 🔄 **Tool Assignment Flow**

### **1. Agent Tool Assignment**
```python
# Assign specific tools to agent
assigned_tools = tool_manager.assign_tools_to_agent(
    agent_id="agent_1",
    tool_names=["data_analyzer", "file_processor"]
)

# Verify assignment
agent_tools = tool_manager.get_agent_tools("agent_1")
# Returns: ["data_analyzer", "file_processor"]
```

### **2. Tool Execution Request**
```python
# Agent requests tool execution
result = await tool_manager.execute_tool(
    tool_name="data_analyzer",
    arguments={"data": "sample_data"}
)
```

### **3. Context Tracking**
```python
# System tracks agent context
execution_context = {
    "agent_id": "agent_1",
    "tool_name": "data_analyzer",
    "timestamp": "2025-06-28T10:00:00Z",
    "arguments": {"data": "sample_data"}
}
```

## 🛠️ **FastMCP Integration**

### **1. MCP Server Management**
```python
from fastmcp import FastMCP, Client

# Global MCP server instance
mcp_server = FastMCP("AgentHub Tools")

# Tool registration with FastMCP
@mcp_server.tool()
def tool_wrapper(**kwargs):
    return original_function(**kwargs)

# MCP client for tool execution
client = Client(mcp_server)
```

### **2. Tool Execution via MCP**
```python
# Execute tool through MCP client
async with client:
    result = await client.call_tool("data_analyzer", {"data": "sample"})
    return result.content[0].text
```

### **3. Tool Discovery via MCP**
```python
# List available tools
async with client:
    tools = await client.list_tools()
    tool_names = [tool.name for tool in tools.tools]
    return tool_names
```

## 🔒 **Tool Access Control**

### **1. Per-Agent Tool Assignment**
```python
# Tool assignments per agent
agent_tool_assignments = {
    "agent_1": ["data_analyzer", "file_processor"],
    "agent_2": ["sentiment_analysis", "text_processor"],
    "agent_3": ["data_analyzer", "sentiment_analysis"]
}
```

### **2. Tool Execution Validation**
```python
def validate_tool_access(agent_id: str, tool_name: str) -> bool:
    """Validate that agent can access tool"""
    agent_tools = tool_manager.get_agent_tools(agent_id)
    return tool_name in agent_tools
```

### **3. Tool Namespace Support**
```python
# Built-in tools
builtin_tools = ["file_reader", "data_processor"]

# Custom tools
custom_tools = ["data_analyzer", "sentiment_analysis"]

# Future: Explicit namespacing
# tools = ["builtin.file_reader", "custom.data_analyzer"]
```

## ⚡ **Concurrency Support**

### **1. Concurrent Tool Execution**
```python
import asyncio
from typing import List, Dict, Any

async def execute_tools_concurrently(
    tool_requests: List[Dict[str, Any]]
) -> List[Any]:
    """Execute multiple tools concurrently"""
    tasks = []
    for request in tool_requests:
        task = tool_manager.execute_tool(
            request["tool_name"],
            request["arguments"]
        )
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    return results
```

### **2. Tool Execution Queue**
```python
from asyncio import Queue
from typing import Dict, Any

class ToolExecutionQueue:
    def __init__(self):
        self.queue = Queue()
        self.running = False

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]):
        """Execute tool with queuing for side effects"""
        await self.queue.put((tool_name, arguments))
        if not self.running:
            await self._process_queue()

    async def _process_queue(self):
        """Process tool execution queue"""
        self.running = True
        while not self.queue.empty():
            tool_name, arguments = await self.queue.get()
            await self._execute_single_tool(tool_name, arguments)
        self.running = False
```

## 🔄 **Error Handling**

### **1. Tool Execution Errors**
```python
class ToolExecutionError(Exception):
    """Tool execution failed"""
    pass

class ToolNotFoundError(Exception):
    """Tool not found"""
    pass

class ToolAccessDeniedError(Exception):
    """Agent not authorized to access tool"""
    pass

class ToolTimeoutError(Exception):
    """Tool execution timed out"""
    pass
```

### **2. Error Recovery**
```python
async def execute_tool_with_retry(
    tool_name: str,
    arguments: Dict[str, Any],
    max_retries: int = 3
) -> Any:
    """Execute tool with retry logic"""
    for attempt in range(max_retries):
        try:
            return await tool_manager.execute_tool(tool_name, arguments)
        except ToolExecutionError as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff
```

## 📊 **Context Tracking**

### **1. Execution Context**
```python
@dataclass
class ToolExecutionContext:
    agent_id: str
    tool_name: str
    arguments: Dict[str, Any]
    timestamp: datetime
    execution_id: str
    status: str  # "pending", "running", "completed", "failed"
    result: Optional[Any] = None
    error: Optional[str] = None
```

### **2. Context Management**
```python
class ContextManager:
    def __init__(self):
        self.execution_contexts: Dict[str, ToolExecutionContext] = {}

    def create_context(self, agent_id: str, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Create execution context"""
        execution_id = f"{agent_id}_{tool_name}_{int(time.time())}"
        context = ToolExecutionContext(
            agent_id=agent_id,
            tool_name=tool_name,
            arguments=arguments,
            timestamp=datetime.now(),
            execution_id=execution_id,
            status="pending"
        )
        self.execution_contexts[execution_id] = context
        return execution_id

    def update_context(self, execution_id: str, status: str, result: Any = None, error: str = None):
        """Update execution context"""
        if execution_id in self.execution_contexts:
            context = self.execution_contexts[execution_id]
            context.status = status
            context.result = result
            context.error = error
```

## 🎯 **Success Criteria**

- ✅ AgentToolManager manages tool assignments correctly
- ✅ Tool execution routing works via MCP
- ✅ Agent context tracking works properly
- ✅ Concurrent tool execution is safe
- ✅ Error handling covers all failure cases
- ✅ FastMCP integration is seamless
- ✅ Tool access control works per-agent
- ✅ Performance meets requirements
