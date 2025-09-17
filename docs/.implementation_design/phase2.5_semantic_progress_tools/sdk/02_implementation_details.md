# SDK Implementation Details - Phase 2.5

**Document Type**: Implementation Details
**Module**: sdk
**Phase**: 2.5
**Status**: Draft

## 🎯 **Purpose**

Detailed implementation of enhanced `load_agent()` with tool assignment, tool integration, and user-friendly API.

## 🏗️ **Architecture Overview**

```
Enhanced load_agent()
├── Tool Validation
├── Base Agent Loading
├── Tool Assignment
├── Tool Injection
└── Enhanced Agent Creation

EnhancedAgent
├── Tool Capabilities
├── Tool Discovery
├── Tool Execution
└── Tool Metadata Access

SDK Integration
├── Backward Compatibility
├── Error Handling
├── User Experience
└── Performance Optimization
```

## 🔧 **Core Implementation**

### **1. Enhanced load_agent() Function**

```python
# agenthub/sdk/load_agent.py
from agenthub.runtime import get_tool_injector, get_context_manager
from agenthub.core.tools import get_available_tools
from typing import List, Optional, Dict, Any, Union
import asyncio
from dataclasses import dataclass

@dataclass
class AgentConfig:
    base_agent: str
    tools: Optional[List[str]] = None
    agent_id: Optional[str] = None
    config: Optional[Dict[str, Any]] = None

class EnhancedAgent:
    def __init__(self, base_agent, tool_metadata=None, agent_id=None):
        self.base_agent = base_agent
        self.tool_metadata = tool_metadata
        self.agent_id = agent_id or f"agent_{id(self)}"
        self._tool_injector = None
        self._context_manager = None
        self._client_manager = None

    def has_tool(self, tool_name: str) -> bool:
        """Check if agent has access to specific tool"""
        if not self.tool_metadata:
            return False
        return tool_name in self.tool_metadata.get("available_tools", [])

    def get_available_tools(self) -> List[str]:
        """Get list of available tools for agent"""
        if not self.tool_metadata:
            return []
        return self.tool_metadata.get("available_tools", [])

    def get_tool_metadata(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get metadata for specific tool"""
        if not self.tool_metadata:
            return None

        tools = self.tool_metadata.get("tools", {})
        if tool_name not in tools.get("available_tools", []):
            return None

        return {
            "name": tool_name,
            "description": tools.get("tool_descriptions", {}).get(tool_name, ""),
            "parameters": tools.get("tool_parameters", {}).get(tool_name, {}),
            "examples": tools.get("tool_usage_examples", {}).get(tool_name, [])
        }

    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Execute tool for agent"""
        if not self.has_tool(tool_name):
            raise ToolAccessDeniedError(f"Agent does not have access to tool {tool_name}")

        # Execute tool via MCP
        from agenthub.runtime import execute_tool_for_agent
        return await execute_tool_for_agent(self, tool_name, arguments)

def load_agent(base_agent: str, tools: Optional[List[str]] = None, **kwargs) -> EnhancedAgent:
    """Load an agent with optional tool assignment"""

    # Validate base agent
    if not base_agent:
        raise AgentLoadingError("Base agent is required")

    # Create agent configuration
    config = AgentConfig(
        base_agent=base_agent,
        tools=tools,
        agent_id=kwargs.get("agent_id"),
        config=kwargs
    )

    # Load base agent (existing functionality)
    base_agent_instance = _load_base_agent(base_agent, **kwargs)

    # Create enhanced agent
    enhanced_agent = EnhancedAgent(
        base_agent=base_agent_instance,
        agent_id=config.agent_id
    )

    # If tools are specified, inject them
    if tools:
        try:
            # Validate tool assignment
            valid_tools = _validate_tool_assignment(tools)

            # Inject tools into agent context
            tool_injector = get_tool_injector()
            tool_metadata = tool_injector.inject_tools_into_agent(
                enhanced_agent.agent_id,
                valid_tools
            )

            # Create agent context with tools
            context_manager = get_context_manager()
            agent_context = context_manager.create_agent_context(
                agent_id=enhanced_agent.agent_id,
                base_context={"name": f"Agent {enhanced_agent.agent_id}"},
                tool_metadata=tool_metadata
            )

            # Add tool metadata to agent
            enhanced_agent.tool_metadata = tool_metadata
            enhanced_agent._tool_injector = tool_injector
            enhanced_agent._context_manager = context_manager

        except Exception as e:
            # If tool injection fails, return agent without tools
            print(f"Warning: Tool injection failed: {e}")
            print("Agent loaded without tools")

    return enhanced_agent

def _load_base_agent(base_agent: str, **kwargs):
    """Load the base agent (existing implementation)"""
    # This would use existing agent loading logic
    # For now, return a mock agent
    class MockBaseAgent:
        def __init__(self, name):
            self.name = name

        def __getattr__(self, name):
            # Delegate to base agent functionality
            return getattr(self, name)

    return MockBaseAgent(base_agent)

def _validate_tool_assignment(tool_names: List[str]) -> List[str]:
    """Validate tool assignment and return valid tools"""
    available_tools = get_available_tools()
    valid_tools = [name for name in tool_names if name in available_tools]

    if not valid_tools:
        raise ToolAssignmentError("No valid tools found for assignment")

    return valid_tools
```

### **2. Tool Assignment Functions**

```python
# agenthub/sdk/tool_assignment.py
from agenthub.runtime import get_tool_injector, get_context_manager
from agenthub.core.tools import get_available_tools
from typing import List, Dict, Any, Optional
from .exceptions import ToolAssignmentError, ToolAccessDeniedError

def assign_tools_to_agent(agent: EnhancedAgent, tool_names: List[str]) -> List[str]:
    """Assign tools to existing agent"""
    if not agent.tool_metadata:
        # Create initial tool metadata
        agent.tool_metadata = {
            "available_tools": [],
            "tool_descriptions": {},
            "tool_usage_examples": {},
            "tool_parameters": {},
            "tool_return_types": {},
            "tool_namespaces": {}
        }

    # Validate tool assignment
    valid_tools = _validate_tool_assignment(tool_names)

    # Get existing tools
    existing_tools = agent.tool_metadata.get("available_tools", [])

    # Add new tools
    new_tools = [name for name in valid_tools if name not in existing_tools]

    if new_tools:
        # Inject new tools
        tool_injector = get_tool_injector()
        tool_metadata = tool_injector.inject_tools_into_agent(
            agent.agent_id,
            new_tools
        )

        # Update agent tool metadata
        agent.tool_metadata["available_tools"].extend(new_tools)
        agent.tool_metadata["tool_descriptions"].update(tool_metadata.get("tool_descriptions", {}))
        agent.tool_metadata["tool_usage_examples"].update(tool_metadata.get("tool_usage_examples", {}))
        agent.tool_metadata["tool_parameters"].update(tool_metadata.get("tool_parameters", {}))
        agent.tool_metadata["tool_return_types"].update(tool_metadata.get("tool_return_types", {}))
        agent.tool_metadata["tool_namespaces"].update(tool_metadata.get("tool_namespaces", {}))

        # Update agent context
        if agent._context_manager:
            agent._context_manager.update_agent_context(
                agent.agent_id,
                {"tools": agent.tool_metadata}
            )

    return valid_tools

def get_agent_tools(agent: EnhancedAgent) -> List[str]:
    """Get tools assigned to agent"""
    return agent.get_available_tools()

def remove_tools_from_agent(agent: EnhancedAgent, tool_names: List[str]) -> List[str]:
    """Remove tools from agent"""
    if not agent.tool_metadata:
        return []

    available_tools = agent.tool_metadata.get("available_tools", [])
    removed_tools = [name for name in tool_names if name in available_tools]

    if removed_tools:
        # Remove tools from metadata
        for tool_name in removed_tools:
            agent.tool_metadata["available_tools"].remove(tool_name)
            agent.tool_metadata["tool_descriptions"].pop(tool_name, None)
            agent.tool_metadata["tool_usage_examples"].pop(tool_name, None)
            agent.tool_metadata["tool_parameters"].pop(tool_name, None)
            agent.tool_metadata["tool_return_types"].pop(tool_name, None)
            agent.tool_metadata["tool_namespaces"].pop(tool_name, None)

        # Update agent context
        if agent._context_manager:
            agent._context_manager.update_agent_context(
                agent.agent_id,
                {"tools": agent.tool_metadata}
            )

    return removed_tools
```

### **3. Tool Execution Functions**

```python
# agenthub/sdk/tool_execution.py
from agenthub.runtime import execute_tool_for_agent
from typing import Dict, Any, Optional
import asyncio
from .exceptions import ToolExecutionError, ToolAccessDeniedError

async def execute_tool_for_agent(agent: EnhancedAgent, tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Execute tool for agent"""
    if not agent.has_tool(tool_name):
        raise ToolAccessDeniedError(f"Agent does not have access to tool {tool_name}")

    try:
        # Execute tool via MCP
        from agenthub.runtime import execute_tool_for_agent as runtime_execute_tool
        return await runtime_execute_tool(agent.agent_id, tool_name, arguments)
    except Exception as e:
        raise ToolExecutionError(f"Tool execution failed: {str(e)}")

async def execute_tool_for_agent_with_retry(
    agent: EnhancedAgent,
    tool_name: str,
    arguments: Dict[str, Any],
    max_retries: int = 3
) -> Any:
    """Execute tool for agent with retry logic"""
    for attempt in range(max_retries):
        try:
            return await execute_tool_for_agent(agent, tool_name, arguments)
        except ToolExecutionError as e:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2 ** attempt)  # Exponential backoff

def execute_tool_sync(agent: EnhancedAgent, tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Execute tool synchronously (for backward compatibility)"""
    return asyncio.run(execute_tool_for_agent(agent, tool_name, arguments))
```

### **4. Tool Discovery Functions**

```python
# agenthub/sdk/tool_discovery.py
from typing import List, Optional, Dict, Any
from .exceptions import ToolNotFoundError

class ToolDiscovery:
    def __init__(self, agent: EnhancedAgent):
        self.agent = agent

    def search_tools(self, query: str) -> List[str]:
        """Search tools available to agent"""
        available_tools = self.agent.get_available_tools()
        if not query:
            return available_tools

        matching_tools = []
        for tool_name in available_tools:
            metadata = self.agent.get_tool_metadata(tool_name)
            if metadata:
                description = metadata.get("description", "")
                if (query.lower() in tool_name.lower() or
                    query.lower() in description.lower()):
                    matching_tools.append(tool_name)

        return matching_tools

    def get_tool_help(self, tool_name: str) -> Optional[str]:
        """Get help information for tool"""
        metadata = self.agent.get_tool_metadata(tool_name)
        if not metadata:
            return None

        help_text = f"Tool: {tool_name}\n"
        help_text += f"Description: {metadata.get('description', 'No description')}\n"

        parameters = metadata.get("parameters", {})
        if parameters:
            help_text += "Parameters:\n"
            for param_name, param_info in parameters.items():
                param_type = param_info.get("type", "unknown")
                required = param_info.get("required", False)
                help_text += f"  {param_name} ({param_type}){'*' if required else ''}\n"

        examples = metadata.get("examples", [])
        if examples:
            help_text += "Examples:\n"
            for example in examples:
                help_text += f"  {example}\n"

        return help_text

    def list_tools(self) -> List[Dict[str, Any]]:
        """List all tools available to agent"""
        available_tools = self.agent.get_available_tools()
        tool_list = []

        for tool_name in available_tools:
            metadata = self.agent.get_tool_metadata(tool_name)
            if metadata:
                tool_list.append({
                    "name": tool_name,
                    "description": metadata.get("description", ""),
                    "parameters": metadata.get("parameters", {}),
                    "examples": metadata.get("examples", [])
                })

        return tool_list
```

### **5. Error Handling**

```python
# agenthub/sdk/exceptions.py
class SDKError(Exception):
    """Base exception for SDK-related errors"""
    pass

class AgentLoadingError(SDKError):
    """Agent loading failed"""
    pass

class ToolAssignmentError(SDKError):
    """Tool assignment failed"""
    pass

class ToolAccessDeniedError(SDKError):
    """Agent not authorized to access tool"""
    pass

class ToolExecutionError(SDKError):
    """Tool execution failed"""
    pass

class ToolNotFoundError(SDKError):
    """Tool not found"""
    pass

class ToolDiscoveryError(SDKError):
    """Tool discovery failed"""
    pass
```

### **6. SDK Module Integration**

```python
# agenthub/sdk/__init__.py
from .load_agent import load_agent, EnhancedAgent
from .tool_assignment import assign_tools_to_agent, get_agent_tools, remove_tools_from_agent
from .tool_execution import execute_tool_for_agent, execute_tool_for_agent_with_retry, execute_tool_sync
from .tool_discovery import ToolDiscovery
from .exceptions import (
    SDKError,
    AgentLoadingError,
    ToolAssignmentError,
    ToolAccessDeniedError,
    ToolExecutionError,
    ToolNotFoundError,
    ToolDiscoveryError
)

# Convenience functions
def create_agent_with_tools(base_agent: str, tools: List[str], **kwargs) -> EnhancedAgent:
    """Create agent with tools (convenience function)"""
    return load_agent(base_agent, tools=tools, **kwargs)

def get_agent_tool_info(agent: EnhancedAgent, tool_name: str) -> Optional[Dict[str, Any]]:
    """Get tool information for agent"""
    return agent.get_tool_metadata(tool_name)

def search_agent_tools(agent: EnhancedAgent, query: str) -> List[str]:
    """Search tools for agent"""
    discovery = ToolDiscovery(agent)
    return discovery.search_tools(query)

def get_agent_tool_help(agent: EnhancedAgent, tool_name: str) -> Optional[str]:
    """Get tool help for agent"""
    discovery = ToolDiscovery(agent)
    return discovery.get_tool_help(tool_name)
```

## 🔄 **Tool Assignment Flow**

### **1. User Calls load_agent()**
```python
agent = amg.load_agent(
    base_agent="agentplug/analyzer",
    tools=["data_analyzer", "file_processor"]
)
```

### **2. Tool Validation**
```python
# Validate tool assignment
valid_tools = _validate_tool_assignment(tools)
# Returns: ["data_analyzer", "file_processor"]
```

### **3. Base Agent Loading**
```python
# Load base agent
base_agent_instance = _load_base_agent(base_agent, **kwargs)
```

### **4. Tool Injection**
```python
# Inject tools into agent context
tool_injector = get_tool_injector()
tool_metadata = tool_injector.inject_tools_into_agent(
    agent_id,
    valid_tools
)
```

### **5. Enhanced Agent Creation**
```python
# Create enhanced agent with tool capabilities
enhanced_agent = EnhancedAgent(
    base_agent=base_agent_instance,
    tool_metadata=tool_metadata,
    agent_id=agent_id
)
```

## 🚀 **Performance Optimization**

### **1. Lazy Tool Loading**
```python
class LazyToolLoader:
    def __init__(self, agent: EnhancedAgent):
        self.agent = agent
        self._loaded_tools = set()

    async def load_tool_on_demand(self, tool_name: str):
        """Load tool only when needed"""
        if tool_name not in self._loaded_tools:
            # Load tool metadata
            tool_metadata = self.agent.get_tool_metadata(tool_name)
            if tool_metadata:
                self._loaded_tools.add(tool_name)
                return tool_metadata
        return None
```

### **2. Tool Metadata Caching**
```python
class ToolMetadataCache:
    def __init__(self, max_size: int = 1000, ttl: float = 300.0):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.timestamps: Dict[str, datetime] = {}
        self.max_size = max_size
        self.ttl = ttl
        self._lock = asyncio.Lock()

    async def get_tool_metadata(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get cached tool metadata"""
        async with self._lock:
            if tool_name in self.cache:
                timestamp = self.timestamps[tool_name]
                if (datetime.now() - timestamp).total_seconds() < self.ttl:
                    return self.cache[tool_name]
                else:
                    # Remove expired entry
                    del self.cache[tool_name]
                    del self.timestamps[tool_name]
            return None

    async def cache_tool_metadata(self, tool_name: str, metadata: Dict[str, Any]):
        """Cache tool metadata"""
        async with self._lock:
            # Remove oldest entries if cache is full
            if len(self.cache) >= self.max_size:
                oldest_tool = min(
                    self.timestamps.keys(),
                    key=lambda name: self.timestamps[name]
                )
                del self.cache[oldest_tool]
                del self.timestamps[oldest_tool]

            self.cache[tool_name] = metadata
            self.timestamps[tool_name] = datetime.now()
```

## 🎯 **Success Criteria**

- ✅ `amg.load_agent(tools=[...])` works correctly
- ✅ Tool assignment works automatically
- ✅ Tool validation works at assignment time
- ✅ Enhanced agent has tool capabilities
- ✅ Tool discovery works for agents
- ✅ Tool execution works via MCP
- ✅ Error handling covers all failure cases
- ✅ Backward compatibility is maintained
- ✅ User experience is excellent
- ✅ Performance meets requirements
- ✅ Lazy loading improves performance
- ✅ Tool metadata caching works
