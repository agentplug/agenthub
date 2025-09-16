# SDK Interface Design - Phase 2.5

**Document Type**: Interface Design
**Module**: sdk
**Phase**: 2.5
**Status**: Draft

## 🎯 **Purpose**

Define the public interfaces for enhanced `load_agent()` with tool assignment, tool integration, and user-friendly API.

## 🔧 **Core Interfaces**

### **1. Enhanced load_agent() Interface**

```python
import agenthub as amg
from typing import List, Optional, Dict, Any

# Load agent with tools
agent = amg.load_agent(
    base_agent: str,
    tools: Optional[List[str]] = None,
    **kwargs
) -> Agent

# Load agent without tools (backward compatibility)
agent = amg.load_agent(base_agent: str, **kwargs) -> Agent
```

**Parameters**:
- `base_agent`: Base agent identifier (e.g., "agentplug/analyzer")
- `tools`: Optional list of tool names to assign to agent
- `**kwargs`: Additional arguments passed to base agent loading

**Returns**: Enhanced agent instance with tool capabilities

### **2. Tool Assignment Interface**

```python
from agenthub.sdk import assign_tools_to_agent, get_agent_tools

# Assign tools to existing agent
assigned_tools = assign_tools_to_agent(
    agent: Agent,
    tool_names: List[str]
) -> List[str]

# Get tools assigned to agent
agent_tools = get_agent_tools(agent: Agent) -> List[str]

# Check if agent has specific tool
has_tool = agent.has_tool(tool_name: str) -> bool
```

### **3. Tool Execution Interface**

```python
from agenthub.sdk import execute_tool_for_agent

# Execute tool for agent
result = await execute_tool_for_agent(
    agent: Agent,
    tool_name: str,
    arguments: Dict[str, Any]
) -> Any

# Execute tool with error handling
result = await execute_tool_for_agent_with_retry(
    agent: Agent,
    tool_name: str,
    arguments: Dict[str, Any],
    max_retries: int = 3
) -> Any
```

## 🔄 **User Workflow**

### **1. Define Custom Tools**
```python
from agenthub.core.tools import tool

# Define custom tools
@tool(name="data_analyzer", description="Analyze data")
def my_data_analyzer(data: str) -> dict:
    return {"insights": f"analyzed: {data}"}

@tool(name="file_processor", description="Process files")
def my_file_processor(file_path: str) -> dict:
    return {"processed": file_path}
```

### **2. Load Agent with Tools**
```python
import agenthub as amg

# Load agent with tools
agent = amg.load_agent(
    base_agent="agentplug/analyzer",
    tools=["data_analyzer", "file_processor"]
)

# Agent now has access to assigned tools
```

### **3. Use Agent with Tools**
```python
# Agent can use assigned tools
# The agent receives tool metadata and can call tools via MCP
# Tool execution is handled by the framework
```

## 🛠️ **Enhanced Agent Interface**

### **1. Agent with Tool Capabilities**
```python
class EnhancedAgent:
    def __init__(self, base_agent, tool_metadata=None):
        self.base_agent = base_agent
        self.tool_metadata = tool_metadata
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
```

### **2. Tool Discovery Interface**
```python
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
```

## 🔒 **Tool Access Control**

### **1. Per-Agent Tool Access**
```python
def validate_tool_access(agent: EnhancedAgent, tool_name: str) -> bool:
    """Validate that agent can access tool"""
    return agent.has_tool(tool_name)

def execute_tool_with_validation(agent: EnhancedAgent, tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Execute tool with access validation"""
    if not validate_tool_access(agent, tool_name):
        raise ToolAccessDeniedError(f"Agent does not have access to tool {tool_name}")

    return await agent.execute_tool(tool_name, arguments)
```

### **2. Tool Assignment Validation**
```python
def validate_tool_assignment(tool_names: List[str]) -> List[str]:
    """Validate tool assignment and return valid tools"""
    from agenthub.core.tools import get_available_tools

    available_tools = get_available_tools()
    valid_tools = [name for name in tool_names if name in available_tools]

    if not valid_tools:
        raise ToolAssignmentError("No valid tools found for assignment")

    return valid_tools
```

## ⚡ **Error Handling**

### **1. Tool Assignment Errors**
```python
class ToolAssignmentError(Exception):
    """Tool assignment failed"""
    pass

class ToolAccessDeniedError(Exception):
    """Agent not authorized to access tool"""
    pass

class ToolExecutionError(Exception):
    """Tool execution failed"""
    pass

class AgentLoadingError(Exception):
    """Agent loading failed"""
    pass
```

### **2. Error Recovery**
```python
async def load_agent_with_fallback(
    base_agent: str,
    tools: Optional[List[str]] = None,
    fallback_tools: Optional[List[str]] = None
) -> Agent:
    """Load agent with tool fallback"""
    try:
        # Try to load agent with requested tools
        return amg.load_agent(base_agent, tools=tools)
    except ToolAssignmentError:
        if fallback_tools:
            # Try with fallback tools
            return amg.load_agent(base_agent, tools=fallback_tools)
        else:
            # Load without tools
            return amg.load_agent(base_agent)
```

## 📊 **Tool Metadata Structure**

### **1. Agent Tool Metadata**
```python
AgentToolMetadata = {
    "available_tools": List[str],
    "tool_descriptions": Dict[str, str],
    "tool_usage_examples": Dict[str, List[str]],
    "tool_parameters": Dict[str, Dict[str, Any]],
    "tool_return_types": Dict[str, str],
    "tool_namespaces": Dict[str, str]
}
```

### **2. Tool Information**
```python
ToolInfo = {
    "name": str,
    "description": str,
    "parameters": Dict[str, Any],
    "return_type": str,
    "namespace": str,
    "examples": List[str],
    "available": bool
}
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
