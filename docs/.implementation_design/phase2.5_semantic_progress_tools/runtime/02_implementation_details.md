# Runtime Implementation Details - Phase 2.5

**Document Type**: Implementation Details
**Module**: runtime
**Phase**: 2.5
**Status**: Draft

## 🎯 **Purpose**

Detailed implementation of tool injection into agent context, MCP client integration, and agent tool access.

## 🏗️ **Architecture Overview**

```
ToolInjector
├── Tool Metadata Injection
├── Tool Discovery
├── Tool Access Control
└── Agent Context Enhancement

AgentContextManager
├── Context Creation
├── Context Updates
├── Context Persistence
└── Context Cleanup

MCPClientManager
├── Client Connection Management
├── Tool Execution
├── Connection Pooling
└── Error Handling
```

## 🔧 **Core Implementation**

### **1. ToolInjector Class**

```python
# agenthub/runtime/tool_injector.py
from agenthub.core.tools import get_tool_metadata, get_available_tools
from agenthub.core.mcp import get_tool_manager
from typing import Dict, List, Any, Optional
import asyncio
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ToolMetadata:
    available_tools: List[str]
    tool_descriptions: Dict[str, str]
    tool_usage_examples: Dict[str, str]
    tool_parameters: Dict[str, Dict[str, Any]]
    tool_return_types: Dict[str, str]
    tool_namespaces: Dict[str, str]

class ToolInjector:
    def __init__(self):
        self.tool_manager = get_tool_manager()
        self._injected_agents: Dict[str, ToolMetadata] = {}

    def inject_tools_into_agent(self, agent_id: str, tool_names: List[str]) -> Dict[str, Any]:
        """Inject tool metadata into agent context"""
        # Validate tool names
        available_tools = get_available_tools()
        valid_tools = [name for name in tool_names if name in available_tools]

        if not valid_tools:
            raise ToolInjectionError(f"No valid tools found for agent {agent_id}")

        # Assign tools to agent
        assigned_tools = self.tool_manager.assign_tools_to_agent(agent_id, valid_tools)

        # Create tool metadata
        tool_metadata = self._create_tool_metadata(assigned_tools)

        # Store injected tools for agent
        self._injected_agents[agent_id] = tool_metadata

        return {
            "available_tools": tool_metadata.available_tools,
            "tool_descriptions": tool_metadata.tool_descriptions,
            "tool_usage_examples": tool_metadata.tool_usage_examples,
            "tool_parameters": tool_metadata.tool_parameters,
            "tool_return_types": tool_metadata.tool_return_types,
            "tool_namespaces": tool_metadata.tool_namespaces
        }

    def _create_tool_metadata(self, tool_names: List[str]) -> ToolMetadata:
        """Create tool metadata for assigned tools"""
        tool_descriptions = {}
        tool_usage_examples = {}
        tool_parameters = {}
        tool_return_types = {}
        tool_namespaces = {}

        for tool_name in tool_names:
            # Get tool metadata from registry
            metadata = get_tool_metadata(tool_name)
            if not metadata:
                continue

            # Extract tool information
            tool_descriptions[tool_name] = metadata.description
            tool_usage_examples[tool_name] = self._generate_usage_examples(tool_name, metadata)
            tool_parameters[tool_name] = metadata.parameters
            tool_return_types[tool_name] = str(metadata.return_type)
            tool_namespaces[tool_name] = metadata.namespace

        return ToolMetadata(
            available_tools=tool_names,
            tool_descriptions=tool_descriptions,
            tool_usage_examples=tool_usage_examples,
            tool_parameters=tool_parameters,
            tool_return_types=tool_return_types,
            tool_namespaces=tool_namespaces
        )

    def _generate_usage_examples(self, tool_name: str, metadata) -> List[str]:
        """Generate usage examples for tool"""
        examples = []

        # Generate basic example
        if metadata.parameters:
            param_examples = []
            for param_name, param_info in metadata.parameters.items():
                if param_info.get("type") == str:
                    param_examples.append(f'"{param_name}_value"')
                elif param_info.get("type") == int:
                    param_examples.append("123")
                elif param_info.get("type") == float:
                    param_examples.append("123.45")
                elif param_info.get("type") == bool:
                    param_examples.append("True")
                else:
                    param_examples.append(f'"{param_name}_value"')

            example = f"{tool_name}({', '.join(param_examples)})"
            examples.append(example)

        return examples

    def get_tool_descriptions(self, tool_names: List[str]) -> Dict[str, str]:
        """Get tool descriptions for specific tools"""
        descriptions = {}
        for tool_name in tool_names:
            metadata = get_tool_metadata(tool_name)
            if metadata:
                descriptions[tool_name] = metadata.description
        return descriptions

    def get_tool_examples(self, tool_names: List[str]) -> Dict[str, List[str]]:
        """Get tool usage examples for specific tools"""
        examples = {}
        for tool_name in tool_names:
            metadata = get_tool_metadata(tool_name)
            if metadata:
                examples[tool_name] = self._generate_usage_examples(tool_name, metadata)
        return examples

    def get_injected_tools(self, agent_id: str) -> Optional[ToolMetadata]:
        """Get injected tools for agent"""
        return self._injected_agents.get(agent_id)
```

### **2. AgentContextManager Class**

```python
# agenthub/runtime/context_manager.py
from typing import Dict, List, Any, Optional
import threading
from dataclasses import dataclass
from datetime import datetime
import uuid

@dataclass
class AgentContext:
    agent_id: str
    base_context: Dict[str, Any]
    tools: Dict[str, Any]
    tool_access: Dict[str, bool]
    created_at: datetime
    updated_at: datetime
    context_id: str

class AgentContextManager:
    def __init__(self):
        self._contexts: Dict[str, AgentContext] = {}
        self._lock = threading.Lock()

    def create_agent_context(self, agent_id: str, base_context: Dict[str, Any],
                           tool_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Create agent context with tools"""
        with self._lock:
            # Check if context already exists
            if agent_id in self._contexts:
                raise AgentContextError(f"Context already exists for agent {agent_id}")

            # Create tool access mapping
            tool_access = {}
            available_tools = tool_metadata.get("available_tools", [])
            for tool_name in available_tools:
                tool_access[tool_name] = True

            # Create agent context
            context = AgentContext(
                agent_id=agent_id,
                base_context=base_context,
                tools=tool_metadata,
                tool_access=tool_access,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                context_id=str(uuid.uuid4())
            )

            self._contexts[agent_id] = context

            return self._serialize_context(context)

    def update_agent_context(self, agent_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update agent context"""
        with self._lock:
            if agent_id not in self._contexts:
                raise AgentContextError(f"Context not found for agent {agent_id}")

            context = self._contexts[agent_id]

            # Update context fields
            for key, value in updates.items():
                if key == "base_context":
                    context.base_context.update(value)
                elif key == "tools":
                    context.tools.update(value)
                elif key == "tool_access":
                    context.tool_access.update(value)
                else:
                    setattr(context, key, value)

            context.updated_at = datetime.now()

            return self._serialize_context(context)

    def get_agent_context(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent context"""
        with self._lock:
            if agent_id not in self._contexts:
                return None

            return self._serialize_context(self._contexts[agent_id])

    def cleanup_agent_context(self, agent_id: str) -> bool:
        """Clean up agent context"""
        with self._lock:
            if agent_id in self._contexts:
                del self._contexts[agent_id]
                return True
            return False

    def _serialize_context(self, context: AgentContext) -> Dict[str, Any]:
        """Serialize agent context for return"""
        return {
            "agent_id": context.agent_id,
            "base_context": context.base_context,
            "tools": context.tools,
            "tool_access": context.tool_access,
            "created_at": context.created_at.isoformat(),
            "updated_at": context.updated_at.isoformat(),
            "context_id": context.context_id
        }

    def list_agent_contexts(self) -> List[str]:
        """List all agent context IDs"""
        with self._lock:
            return list(self._contexts.keys())

    def cleanup_expired_contexts(self, max_age: int = 3600) -> int:
        """Clean up expired agent contexts"""
        current_time = datetime.now()
        expired_agents = []

        with self._lock:
            for agent_id, context in self._contexts.items():
                age_seconds = (current_time - context.created_at).total_seconds()
                if age_seconds > max_age:
                    expired_agents.append(agent_id)

            for agent_id in expired_agents:
                del self._contexts[agent_id]

        return len(expired_agents)
```

### **3. MCPClientManager Class**

```python
# agenthub/runtime/mcp_client_manager.py
from fastmcp import Client
from agenthub.core.tools import get_mcp_server
from agenthub.core.mcp import get_tool_manager
from typing import Dict, Any, Optional
import asyncio
import threading
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MCPClientInfo:
    client: Client
    agent_id: str
    created_at: datetime
    last_used: datetime
    is_connected: bool

class MCPClientManager:
    def __init__(self, max_clients: int = 10):
        self.mcp_server = get_mcp_server()
        self.tool_manager = get_tool_manager()
        self._clients: Dict[str, MCPClientInfo] = {}
        self._lock = threading.Lock()
        self._client_lock = asyncio.Lock()
        self.max_clients = max_clients

    async def get_client_for_agent(self, agent_id: str) -> Optional[Client]:
        """Get MCP client for agent"""
        async with self._client_lock:
            # Check if client already exists
            if agent_id in self._clients:
                client_info = self._clients[agent_id]
                if client_info.is_connected:
                    client_info.last_used = datetime.now()
                    return client_info.client

            # Create new client if under limit
            if len(self._clients) < self.max_clients:
                return await self._create_client_for_agent(agent_id)

            # Reuse least recently used client
            return await self._reuse_client_for_agent(agent_id)

    async def _create_client_for_agent(self, agent_id: str) -> Client:
        """Create new MCP client for agent"""
        client = Client(self.mcp_server)
        await client.__aenter__()

        client_info = MCPClientInfo(
            client=client,
            agent_id=agent_id,
            created_at=datetime.now(),
            last_used=datetime.now(),
            is_connected=True
        )

        with self._lock:
            self._clients[agent_id] = client_info

        return client

    async def _reuse_client_for_agent(self, agent_id: str) -> Client:
        """Reuse least recently used client for agent"""
        with self._lock:
            # Find least recently used client
            lru_agent_id = min(
                self._clients.keys(),
                key=lambda aid: self._clients[aid].last_used
            )

            # Close old client
            old_client_info = self._clients[lru_agent_id]
            await old_client_info.client.__aexit__(None, None, None)
            del self._clients[lru_agent_id]

        # Create new client
        return await self._create_client_for_agent(agent_id)

    async def execute_tool(self, agent_id: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute tool via MCP client"""
        # Get client for agent
        client = await self.get_client_for_agent(agent_id)
        if not client:
            raise MCPClientError(f"Failed to get MCP client for agent {agent_id}")

        try:
            # Execute tool via MCP
            result = await client.call_tool(tool_name, arguments)
            return result.content[0].text
        except Exception as e:
            raise MCPClientError(f"Tool execution failed: {str(e)}")

    async def close_client_for_agent(self, agent_id: str) -> bool:
        """Close MCP client for agent"""
        async with self._client_lock:
            if agent_id in self._clients:
                client_info = self._clients[agent_id]
                await client_info.client.__aexit__(None, None, None)
                del self._clients[agent_id]
                return True
            return False

    async def close_all_clients(self) -> bool:
        """Close all MCP clients"""
        async with self._client_lock:
            for agent_id, client_info in self._clients.items():
                await client_info.client.__aexit__(None, None, None)

            self._clients.clear()
            return True

    def get_client_status(self) -> Dict[str, Any]:
        """Get MCP client status"""
        with self._lock:
            return {
                "total_clients": len(self._clients),
                "max_clients": self.max_clients,
                "agents": list(self._clients.keys()),
                "client_info": {
                    agent_id: {
                        "created_at": info.created_at.isoformat(),
                        "last_used": info.last_used.isoformat(),
                        "is_connected": info.is_connected
                    }
                    for agent_id, info in self._clients.items()
                }
            }
```

### **4. Runtime Module Integration**

```python
# agenthub/runtime/__init__.py
from .tool_injector import ToolInjector
from .context_manager import AgentContextManager
from .mcp_client_manager import MCPClientManager
from typing import Dict, List, Any, Optional

# Global instances
_tool_injector = None
_context_manager = None
_client_manager = None

def get_tool_injector() -> ToolInjector:
    """Get global tool injector instance"""
    global _tool_injector
    if _tool_injector is None:
        _tool_injector = ToolInjector()
    return _tool_injector

def get_context_manager() -> AgentContextManager:
    """Get global context manager instance"""
    global _context_manager
    if _context_manager is None:
        _context_manager = AgentContextManager()
    return _context_manager

def get_client_manager() -> MCPClientManager:
    """Get global client manager instance"""
    global _client_manager
    if _client_manager is None:
        _client_manager = MCPClientManager()
    return _client_manager

# Convenience functions
def inject_tools_into_agent(agent_id: str, tool_names: List[str]) -> Dict[str, Any]:
    """Inject tools into agent context"""
    tool_injector = get_tool_injector()
    return tool_injector.inject_tools_into_agent(agent_id, tool_names)

def create_agent_context(agent_id: str, base_context: Dict[str, Any],
                        tool_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Create agent context with tools"""
    context_manager = get_context_manager()
    return context_manager.create_agent_context(agent_id, base_context, tool_metadata)

async def execute_tool_for_agent(agent_id: str, tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Execute tool for agent"""
    client_manager = get_client_manager()
    return await client_manager.execute_tool(agent_id, tool_name, arguments)
```

## 🔄 **Tool Injection Flow**

### **1. Tool Assignment and Injection**
```python
# Inject tools into agent context
tool_injector = get_tool_injector()
tool_metadata = tool_injector.inject_tools_into_agent(
    agent_id="agent_1",
    tool_names=["data_analyzer", "file_processor"]
)
```

### **2. Agent Context Creation**
```python
# Create agent context with tools
context_manager = get_context_manager()
agent_context = context_manager.create_agent_context(
    agent_id="agent_1",
    base_context={"name": "Data Analysis Agent"},
    tool_metadata=tool_metadata
)
```

### **3. Tool Execution**
```python
# Execute tool for agent
client_manager = get_client_manager()
result = await client_manager.execute_tool(
    agent_id="agent_1",
    tool_name="data_analyzer",
    arguments={"data": "sample_data"}
)
```

## 🚀 **Performance Optimization**

### **1. Client Connection Pooling**
```python
class MCPConnectionPool:
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.connections: List[Client] = []
        self.available_connections: asyncio.Queue = asyncio.Queue()
        self._lock = asyncio.Lock()

    async def get_connection(self) -> Client:
        """Get available MCP connection"""
        try:
            return self.available_connections.get_nowait()
        except asyncio.QueueEmpty:
            if len(self.connections) < self.max_connections:
                client = Client(get_mcp_server())
                await client.__aenter__()
                self.connections.append(client)
                return client
            else:
                return await self.available_connections.get()

    async def return_connection(self, client: Client):
        """Return connection to pool"""
        await self.available_connections.put(client)
```

### **2. Context Caching**
```python
class ContextCache:
    def __init__(self, max_size: int = 1000, ttl: float = 300.0):
        self.cache: Dict[str, AgentContext] = {}
        self.timestamps: Dict[str, datetime] = {}
        self.max_size = max_size
        self.ttl = ttl
        self._lock = asyncio.Lock()

    async def get_context(self, agent_id: str) -> Optional[AgentContext]:
        """Get cached agent context"""
        async with self._lock:
            if agent_id in self.cache:
                timestamp = self.timestamps[agent_id]
                if (datetime.now() - timestamp).total_seconds() < self.ttl:
                    return self.cache[agent_id]
                else:
                    # Remove expired entry
                    del self.cache[agent_id]
                    del self.timestamps[agent_id]
            return None

    async def cache_context(self, agent_id: str, context: AgentContext):
        """Cache agent context"""
        async with self._lock:
            # Remove oldest entries if cache is full
            if len(self.cache) >= self.max_size:
                oldest_agent_id = min(
                    self.timestamps.keys(),
                    key=lambda aid: self.timestamps[aid]
                )
                del self.cache[oldest_agent_id]
                del self.timestamps[oldest_agent_id]

            self.cache[agent_id] = context
            self.timestamps[agent_id] = datetime.now()
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
- ✅ Client connection pooling works
- ✅ Context caching improves performance
