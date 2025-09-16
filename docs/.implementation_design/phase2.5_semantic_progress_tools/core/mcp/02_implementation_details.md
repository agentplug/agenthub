# Core/MCP Implementation Details - Phase 2.5

**Document Type**: Implementation Details
**Module**: core/mcp
**Phase**: 2.5
**Status**: Draft

## 🎯 **Purpose**

Detailed implementation of MCP server management, tool routing, context tracking, and FastMCP integration.

## 🏗️ **Architecture Overview**

```
AgentToolManager
├── Tool Assignment Management
├── Tool Execution Routing
├── Agent Context Tracking
└── FastMCP Integration

FastMCP Server
├── Tool Registration
├── Tool Execution
├── MCP Protocol Compliance
└── Concurrency Support

Tool Execution Queue
├── Side Effect Handling
├── Concurrent Execution
├── Error Handling
└── Retry Logic
```

## 🔧 **Core Implementation**

### **1. AgentToolManager Class**

```python
# agenthub/core/mcp/manager.py
from fastmcp import FastMCP, Client
from agenthub.core.tools import get_mcp_server, get_available_tools
from typing import Dict, List, Any, Optional
import asyncio
import threading
from dataclasses import dataclass
from datetime import datetime
import uuid

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

class AgentToolManager:
    def __init__(self):
        self.mcp_server = get_mcp_server()
        self.agent_tool_assignments: Dict[str, List[str]] = {}
        self.client: Optional[Client] = None
        self.execution_contexts: Dict[str, ToolExecutionContext] = {}
        self._lock = threading.Lock()
        self._client_lock = asyncio.Lock()

    def assign_tools_to_agent(self, agent_id: str, tool_names: List[str]) -> List[str]:
        """Assign specific tools to an agent"""
        available_tools = get_available_tools()
        valid_tools = [name for name in tool_names if name in available_tools]

        with self._lock:
            self.agent_tool_assignments[agent_id] = valid_tools

        return valid_tools

    def get_agent_tools(self, agent_id: str) -> List[str]:
        """Get tools assigned to an agent"""
        with self._lock:
            return self.agent_tool_assignments.get(agent_id, [])

    def validate_tool_access(self, agent_id: str, tool_name: str) -> bool:
        """Validate that agent can access tool"""
        agent_tools = self.get_agent_tools(agent_id)
        return tool_name in agent_tools

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any], agent_id: str = None) -> Any:
        """Execute a tool via MCP"""
        # Validate tool access if agent_id provided
        if agent_id and not self.validate_tool_access(agent_id, tool_name):
            raise ToolAccessDeniedError(f"Agent {agent_id} not authorized to access tool {tool_name}")

        # Create execution context
        execution_id = self._create_execution_context(agent_id, tool_name, arguments)

        try:
            # Ensure client is available
            await self._ensure_client()

            # Execute tool via MCP
            result = await self.client.call_tool(tool_name, arguments)

            # Update context with result
            self._update_execution_context(execution_id, "completed", result.content[0].text)

            return result.content[0].text

        except Exception as e:
            # Update context with error
            self._update_execution_context(execution_id, "failed", error=str(e))
            raise ToolExecutionError(f"Tool execution failed: {str(e)}")

    async def execute_tool_with_retry(self, tool_name: str, arguments: Dict[str, Any],
                                    agent_id: str = None, max_retries: int = 3) -> Any:
        """Execute tool with retry logic"""
        for attempt in range(max_retries):
            try:
                return await self.execute_tool(tool_name, arguments, agent_id)
            except ToolExecutionError as e:
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff

    async def _ensure_client(self):
        """Ensure MCP client is available"""
        async with self._client_lock:
            if self.client is None:
                self.client = Client(self.mcp_server)
                await self.client.__aenter__()

    def _create_execution_context(self, agent_id: str, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Create execution context"""
        execution_id = f"{agent_id}_{tool_name}_{uuid.uuid4().hex[:8]}"
        context = ToolExecutionContext(
            agent_id=agent_id or "unknown",
            tool_name=tool_name,
            arguments=arguments,
            timestamp=datetime.now(),
            execution_id=execution_id,
            status="pending"
        )

        with self._lock:
            self.execution_contexts[execution_id] = context

        return execution_id

    def _update_execution_context(self, execution_id: str, status: str, result: Any = None, error: str = None):
        """Update execution context"""
        with self._lock:
            if execution_id in self.execution_contexts:
                context = self.execution_contexts[execution_id]
                context.status = status
                context.result = result
                context.error = error

    async def close(self):
        """Close MCP client connection"""
        if self.client:
            await self.client.__aexit__(None, None, None)
            self.client = None
```

### **2. Tool Execution Queue**

```python
# agenthub/core/mcp/queue.py
import asyncio
from asyncio import Queue
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import uuid

@dataclass
class QueuedToolExecution:
    execution_id: str
    tool_name: str
    arguments: Dict[str, Any]
    agent_id: str
    priority: int = 0
    created_at: datetime = None
    max_retries: int = 3
    timeout: float = 30.0

class ToolExecutionQueue:
    def __init__(self, max_size: int = 1000):
        self.queue = Queue(maxsize=max_size)
        self.running = False
        self.execution_tasks: Dict[str, asyncio.Task] = {}
        self._lock = asyncio.Lock()

    async def enqueue_tool_execution(self, tool_name: str, arguments: Dict[str, Any],
                                   agent_id: str, priority: int = 0) -> str:
        """Enqueue tool execution"""
        execution_id = f"queue_{uuid.uuid4().hex[:8]}"
        queued_execution = QueuedToolExecution(
            execution_id=execution_id,
            tool_name=tool_name,
            arguments=arguments,
            agent_id=agent_id,
            priority=priority,
            created_at=datetime.now()
        )

        await self.queue.put(queued_execution)

        # Start processing if not running
        if not self.running:
            asyncio.create_task(self._process_queue())

        return execution_id

    async def _process_queue(self):
        """Process tool execution queue"""
        self.running = True

        try:
            while not self.queue.empty():
                queued_execution = await self.queue.get()

                # Create execution task
                task = asyncio.create_task(
                    self._execute_queued_tool(queued_execution)
                )

                async with self._lock:
                    self.execution_tasks[queued_execution.execution_id] = task

                # Wait for task completion
                try:
                    await task
                except Exception as e:
                    # Log error but continue processing
                    print(f"Tool execution failed: {e}")
                finally:
                    async with self._lock:
                        if queued_execution.execution_id in self.execution_tasks:
                            del self.execution_tasks[queued_execution.execution_id]

        finally:
            self.running = False

    async def _execute_queued_tool(self, queued_execution: QueuedToolExecution):
        """Execute queued tool"""
        try:
            # Import here to avoid circular imports
            from agenthub.core.mcp import AgentToolManager

            tool_manager = AgentToolManager()

            # Execute tool with timeout
            result = await asyncio.wait_for(
                tool_manager.execute_tool(
                    queued_execution.tool_name,
                    queued_execution.arguments,
                    queued_execution.agent_id
                ),
                timeout=queued_execution.timeout
            )

            return result

        except asyncio.TimeoutError:
            raise ToolTimeoutError(f"Tool execution timed out: {queued_execution.tool_name}")
        except Exception as e:
            raise ToolExecutionError(f"Tool execution failed: {str(e)}")

    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel queued tool execution"""
        async with self._lock:
            if execution_id in self.execution_tasks:
                task = self.execution_tasks[execution_id]
                task.cancel()
                del self.execution_tasks[execution_id]
                return True
        return False

    def get_queue_status(self) -> Dict[str, Any]:
        """Get queue status"""
        return {
            "queue_size": self.queue.qsize(),
            "running": self.running,
            "active_executions": len(self.execution_tasks)
        }
```

### **3. MCP Server Integration**

```python
# agenthub/core/mcp/__init__.py
from .manager import AgentToolManager, ToolExecutionContext
from .queue import ToolExecutionQueue
from agenthub.core.tools import get_mcp_server, get_available_tools, get_tool_metadata
from typing import List, Optional, Dict, Any

# Global instances
_tool_manager = None
_execution_queue = None

def get_tool_manager() -> AgentToolManager:
    """Get global tool manager instance"""
    global _tool_manager
    if _tool_manager is None:
        _tool_manager = AgentToolManager()
    return _tool_manager

def get_execution_queue() -> ToolExecutionQueue:
    """Get global execution queue instance"""
    global _execution_queue
    if _execution_queue is None:
        _execution_queue = ToolExecutionQueue()
    return _execution_queue

# Convenience functions
async def execute_tool(tool_name: str, arguments: Dict[str, Any], agent_id: str = None) -> Any:
    """Execute tool via MCP"""
    tool_manager = get_tool_manager()
    return await tool_manager.execute_tool(tool_name, arguments, agent_id)

async def execute_tool_with_retry(tool_name: str, arguments: Dict[str, Any],
                                agent_id: str = None, max_retries: int = 3) -> Any:
    """Execute tool with retry logic"""
    tool_manager = get_tool_manager()
    return await tool_manager.execute_tool_with_retry(tool_name, arguments, agent_id, max_retries)

def assign_tools_to_agent(agent_id: str, tool_names: List[str]) -> List[str]:
    """Assign tools to agent"""
    tool_manager = get_tool_manager()
    return tool_manager.assign_tools_to_agent(agent_id, tool_names)

def get_agent_tools(agent_id: str) -> List[str]:
    """Get tools assigned to agent"""
    tool_manager = get_tool_manager()
    return tool_manager.get_agent_tools(agent_id)
```

### **4. Error Handling**

```python
# agenthub/core/mcp/exceptions.py
class MCPError(Exception):
    """Base exception for MCP-related errors"""
    pass

class ToolExecutionError(MCPError):
    """Tool execution failed"""
    pass

class ToolNotFoundError(MCPError):
    """Tool not found"""
    pass

class ToolAccessDeniedError(MCPError):
    """Agent not authorized to access tool"""
    pass

class ToolTimeoutError(MCPError):
    """Tool execution timed out"""
    pass

class MCPConnectionError(MCPError):
    """MCP connection failed"""
    pass

class ToolQueueError(MCPError):
    """Tool execution queue error"""
    pass
```

## 🔄 **Tool Execution Flow**

### **1. Tool Assignment**
```python
# Assign tools to agent
tool_manager = get_tool_manager()
assigned_tools = tool_manager.assign_tools_to_agent(
    agent_id="agent_1",
    tool_names=["data_analyzer", "file_processor"]
)
```

### **2. Tool Execution Request**
```python
# Agent requests tool execution
result = await tool_manager.execute_tool(
    tool_name="data_analyzer",
    arguments={"data": "sample_data"},
    agent_id="agent_1"
)
```

### **3. MCP Client Execution**
```python
# Tool is executed via MCP client
async with mcp_client:
    result = await mcp_client.call_tool("data_analyzer", {"data": "sample_data"})
    return result.content[0].text
```

### **4. Context Tracking**
```python
# Execution context is tracked
context = ToolExecutionContext(
    agent_id="agent_1",
    tool_name="data_analyzer",
    arguments={"data": "sample_data"},
    timestamp=datetime.now(),
    execution_id="exec_123",
    status="completed",
    result="processed_data"
)
```

## 🚀 **Concurrency Support**

### **1. Concurrent Tool Execution**
```python
import asyncio

async def execute_multiple_tools(tool_requests: List[Dict[str, Any]]) -> List[Any]:
    """Execute multiple tools concurrently"""
    tool_manager = get_tool_manager()

    tasks = []
    for request in tool_requests:
        task = tool_manager.execute_tool(
            request["tool_name"],
            request["arguments"],
            request.get("agent_id")
        )
        tasks.append(task)

    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

### **2. Tool Execution Queue**
```python
# For tools with side effects, use queue
execution_queue = get_execution_queue()

# Enqueue tool execution
execution_id = await execution_queue.enqueue_tool_execution(
    tool_name="file_processor",
    arguments={"file_path": "/path/to/file"},
    agent_id="agent_1",
    priority=1
)
```

## 📊 **Performance Optimization**

### **1. Connection Pooling**
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

### **2. Tool Execution Caching**
```python
class ToolExecutionCache:
    def __init__(self, max_size: int = 1000, ttl: float = 300.0):
        self.cache: Dict[str, Any] = {}
        self.timestamps: Dict[str, datetime] = {}
        self.max_size = max_size
        self.ttl = ttl
        self._lock = asyncio.Lock()

    def _generate_cache_key(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Generate cache key for tool execution"""
        import hashlib
        import json

        key_data = {
            "tool_name": tool_name,
            "arguments": sorted(arguments.items())
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

    async def get_cached_result(self, tool_name: str, arguments: Dict[str, Any]) -> Optional[Any]:
        """Get cached tool execution result"""
        cache_key = self._generate_cache_key(tool_name, arguments)

        async with self._lock:
            if cache_key in self.cache:
                timestamp = self.timestamps[cache_key]
                if (datetime.now() - timestamp).total_seconds() < self.ttl:
                    return self.cache[cache_key]
                else:
                    # Remove expired entry
                    del self.cache[cache_key]
                    del self.timestamps[cache_key]

        return None

    async def cache_result(self, tool_name: str, arguments: Dict[str, Any], result: Any):
        """Cache tool execution result"""
        cache_key = self._generate_cache_key(tool_name, arguments)

        async with self._lock:
            # Remove oldest entries if cache is full
            if len(self.cache) >= self.max_size:
                oldest_key = min(self.timestamps.keys(), key=lambda k: self.timestamps[k])
                del self.cache[oldest_key]
                del self.timestamps[oldest_key]

            self.cache[cache_key] = result
            self.timestamps[cache_key] = datetime.now()
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
- ✅ Tool execution queue works for side effects
- ✅ Connection pooling improves performance
