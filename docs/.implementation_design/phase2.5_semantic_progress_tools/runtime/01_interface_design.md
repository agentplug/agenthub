# Runtime Interface Design - Phase 2.5

**Document Type**: Interface Design
**Module**: runtime
**Phase**: 2.5
**Status**: Draft

## 🎯 **Purpose**

Define the public interfaces for tool injection into agent context, MCP client integration, and agent tool access.

## 🔧 **Core Interfaces**

### **1. ToolInjector Interface**

```python
from agenthub.runtime import ToolInjector
from typing import Dict, List, Any, Optional

# Create tool injector
tool_injector = ToolInjector()

# Inject tools into agent context
tool_metadata = tool_injector.inject_tools_into_agent(
    agent_id: str,
    tool_names: List[str]
) -> Dict[str, Any]

# Get tool descriptions for agent
tool_descriptions = tool_injector.get_tool_descriptions(
    tool_names: List[str]
) -> Dict[str, str]

# Get tool usage examples for agent
tool_examples = tool_injector.get_tool_examples(
    tool_names: List[str]
) -> Dict[str, str]
```

### **2. AgentContextManager Interface**

```python
from agenthub.runtime import AgentContextManager
from typing import Dict, List, Any, Optional

# Create context manager
context_manager = AgentContextManager()

# Create agent context with tools
agent_context = context_manager.create_agent_context(
    agent_id: str,
    base_context: Dict[str, Any],
    tool_metadata: Dict[str, Any]
) -> Dict[str, Any]

# Update agent context
updated_context = context_manager.update_agent_context(
    agent_id: str,
    updates: Dict[str, Any]
) -> Dict[str, Any]

# Get agent context
agent_context = context_manager.get_agent_context(agent_id: str) -> Optional[Dict[str, Any]]

# Clean up agent context
context_manager.cleanup_agent_context(agent_id: str) -> bool
```

### **3. MCPClientManager Interface**

```python
from agenthub.runtime import MCPClientManager
from typing import Dict, Any, Optional

# Create MCP client manager
client_manager = MCPClientManager()

# Get MCP client for agent
mcp_client = client_manager.get_client_for_agent(agent_id: str) -> Optional[Client]

# Execute tool via MCP client
result = await client_manager.execute_tool(
    agent_id: str,
    tool_name: str,
    arguments: Dict[str, Any]
) -> Any

# Close MCP client for agent
client_manager.close_client_for_agent(agent_id: str) -> bool

# Close all MCP clients
client_manager.close_all_clients() -> bool
```

## 🔄 **Tool Injection Flow**

### **1. Tool Assignment and Injection**
```python
# Assign tools to agent
tool_injector = ToolInjector()
tool_metadata = tool_injector.inject_tools_into_agent(
    agent_id="agent_1",
    tool_names=["data_analyzer", "file_processor"]
)

# Tool metadata includes:
# {
#     "available_tools": ["data_analyzer", "file_processor"],
#     "tool_descriptions": {
#         "data_analyzer": "Analyze data",
#         "file_processor": "Process files"
#     },
#     "tool_usage_examples": {
#         "data_analyzer": "data_analyzer('sales_data.csv')",
#         "file_processor": "file_processor('/path/to/file')"
#     }
# }
```

### **2. Agent Context Creation**
```python
# Create agent context with tools
context_manager = AgentContextManager()
agent_context = context_manager.create_agent_context(
    agent_id="agent_1",
    base_context={
        "name": "Data Analysis Agent",
        "capabilities": ["data_processing", "analysis"]
    },
    tool_metadata=tool_metadata
)

# Agent context includes:
# {
#     "name": "Data Analysis Agent",
#     "capabilities": ["data_processing", "analysis"],
#     "tools": {
#         "available_tools": ["data_analyzer", "file_processor"],
#         "tool_descriptions": {...},
#         "tool_usage_examples": {...}
#     }
# }
```

### **3. Tool Execution via MCP**
```python
# Execute tool via MCP client
client_manager = MCPClientManager()
result = await client_manager.execute_tool(
    agent_id="agent_1",
    tool_name="data_analyzer",
    arguments={"data": "sample_data"}
)
```

## 🛠️ **Tool Metadata Structure**

### **1. Tool Metadata Format**
```python
ToolMetadata = {
    "available_tools": List[str],
    "tool_descriptions": Dict[str, str],
    "tool_usage_examples": Dict[str, str],
    "tool_parameters": Dict[str, Dict[str, Any]],
    "tool_return_types": Dict[str, str],
    "tool_namespaces": Dict[str, str]
}
```

### **2. Tool Description Format**
```python
ToolDescription = {
    "name": str,
    "description": str,
    "parameters": Dict[str, Any],
    "return_type": str,
    "namespace": str,
    "examples": List[str]
}
```

### **3. Agent Context Format**
```python
AgentContext = {
    "agent_id": str,
    "base_context": Dict[str, Any],
    "tools": ToolMetadata,
    "tool_access": Dict[str, bool],
    "created_at": datetime,
    "updated_at": datetime
}
```

## 🔒 **Tool Access Control**

### **1. Per-Agent Tool Access**
```python
# Tool access is controlled per agent
tool_access = {
    "agent_1": {
        "data_analyzer": True,
        "file_processor": True,
        "sentiment_analysis": False
    },
    "agent_2": {
        "data_analyzer": False,
        "file_processor": True,
        "sentiment_analysis": True
    }
}
```

### **2. Tool Access Validation**
```python
def validate_tool_access(agent_id: str, tool_name: str) -> bool:
    """Validate that agent can access tool"""
    agent_context = context_manager.get_agent_context(agent_id)
    if not agent_context:
        return False

    tool_access = agent_context.get("tool_access", {})
    return tool_access.get(tool_name, False)
```

### **3. Tool Execution Authorization**
```python
async def execute_tool_with_authorization(
    agent_id: str,
    tool_name: str,
    arguments: Dict[str, Any]
) -> Any:
    """Execute tool with authorization check"""
    if not validate_tool_access(agent_id, tool_name):
        raise ToolAccessDeniedError(f"Agent {agent_id} not authorized to access tool {tool_name}")

    return await client_manager.execute_tool(agent_id, tool_name, arguments)
```

## ⚡ **Tool Discovery**

### **1. Tool Discovery for Agent**
```python
def discover_tools_for_agent(agent_id: str) -> List[str]:
    """Discover tools available to agent"""
    agent_context = context_manager.get_agent_context(agent_id)
    if not agent_context:
        return []

    tools = agent_context.get("tools", {})
    return tools.get("available_tools", [])
```

### **2. Tool Metadata Discovery**
```python
def discover_tool_metadata(agent_id: str, tool_name: str) -> Optional[Dict[str, Any]]:
    """Discover metadata for specific tool"""
    agent_context = context_manager.get_agent_context(agent_id)
    if not agent_context:
        return None

    tools = agent_context.get("tools", {})
    tool_descriptions = tools.get("tool_descriptions", {})
    tool_parameters = tools.get("tool_parameters", {})

    if tool_name not in tool_descriptions:
        return None

    return {
        "name": tool_name,
        "description": tool_descriptions[tool_name],
        "parameters": tool_parameters.get(tool_name, {}),
        "examples": tools.get("tool_usage_examples", {}).get(tool_name, [])
    }
```

### **3. Tool Search and Filtering**
```python
def search_tools_for_agent(agent_id: str, query: str) -> List[str]:
    """Search tools available to agent"""
    available_tools = discover_tools_for_agent(agent_id)
    if not query:
        return available_tools

    # Simple text search in tool names and descriptions
    matching_tools = []
    agent_context = context_manager.get_agent_context(agent_id)
    if agent_context:
        tools = agent_context.get("tools", {})
        tool_descriptions = tools.get("tool_descriptions", {})

        for tool_name in available_tools:
            if (query.lower() in tool_name.lower() or
                query.lower() in tool_descriptions.get(tool_name, "").lower()):
                matching_tools.append(tool_name)

    return matching_tools
```

## 🔄 **Context Management**

### **1. Context Lifecycle**
```python
# Create context
agent_context = context_manager.create_agent_context(agent_id, base_context, tool_metadata)

# Update context
updated_context = context_manager.update_agent_context(agent_id, updates)

# Get context
current_context = context_manager.get_agent_context(agent_id)

# Cleanup context
context_manager.cleanup_agent_context(agent_id)
```

### **2. Context Persistence**
```python
def persist_agent_context(agent_id: str) -> bool:
    """Persist agent context to storage"""
    agent_context = context_manager.get_agent_context(agent_id)
    if not agent_context:
        return False

    # Save to persistent storage
    return storage.save_agent_context(agent_id, agent_context)

def load_agent_context(agent_id: str) -> bool:
    """Load agent context from storage"""
    agent_context = storage.load_agent_context(agent_id)
    if not agent_context:
        return False

    # Restore to context manager
    context_manager._contexts[agent_id] = agent_context
    return True
```

### **3. Context Cleanup**
```python
def cleanup_expired_contexts(max_age: int = 3600) -> int:
    """Cleanup expired agent contexts"""
    current_time = datetime.now()
    expired_agents = []

    for agent_id, context in context_manager._contexts.items():
        created_at = context.get("created_at")
        if created_at and (current_time - created_at).total_seconds() > max_age:
            expired_agents.append(agent_id)

    for agent_id in expired_agents:
        context_manager.cleanup_agent_context(agent_id)

    return len(expired_agents)
```

## 🚨 **Error Handling**

### **1. Tool Injection Errors**
```python
class ToolInjectionError(Exception):
    """Tool injection failed"""
    pass

class ToolMetadataError(Exception):
    """Tool metadata error"""
    pass

class AgentContextError(Exception):
    """Agent context error"""
    pass

class MCPClientError(Exception):
    """MCP client error"""
    pass
```

### **2. Error Recovery**
```python
async def execute_tool_with_recovery(
    agent_id: str,
    tool_name: str,
    arguments: Dict[str, Any],
    max_retries: int = 3
) -> Any:
    """Execute tool with error recovery"""
    for attempt in range(max_retries):
        try:
            return await client_manager.execute_tool(agent_id, tool_name, arguments)
        except MCPClientError as e:
            if attempt == max_retries - 1:
                raise
            # Recreate MCP client
            client_manager.close_client_for_agent(agent_id)
            await asyncio.sleep(2 ** attempt)
```

## 🎯 **Success Criteria**

- ✅ ToolInjector injects tool metadata into agent context
- ✅ AgentContextManager manages agent context with tools
- ✅ MCPClientManager handles MCP client connections
- ✅ Tool discovery works for agents
- ✅ Tool access control works per-agent
- ✅ Context management works properly
- ✅ Error handling covers all failure cases
- ✅ Performance meets requirements
