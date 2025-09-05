# Agent-Tools Tracker Module Design

**Document Type**: Module Organization
**Phase**: 2.5 - Native MCP Tool Integration
**Author**: William
**Date Created**: 2025-06-28
**Last Updated**: 2025-06-28
**Status**: Active
**Purpose**: Define module structure and placement for agent-tools tracker

## 🏗️ **Module Placement Decision**

The **Agent-Tools Tracker** is implemented as a **new module within the existing `tools` package**.

### **Decision Rationale**

1. **✅ Logical Grouping**: Agent-tools tracker is fundamentally about tool management
2. **✅ Cohesion**: Works closely with `registry.py` and `discovery.py`
3. **✅ Separation of Concerns**: Different from core tool functionality but related
4. **✅ Extensibility**: Can grow with additional tracking features
5. **✅ Maintainability**: Keeps related functionality together

## 📁 **Updated Module Structure**

```
agentmanager/
├── core/
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── decorators.py          # @tool decorator
│   │   ├── discovery.py           # Tool discovery system
│   │   ├── registry.py            # Global tool registry
│   │   ├── agent_tools_tracker.py # NEW: Agent-tools assignment tracking
│   │   ├── execution/
│   │   │   └── __init__.py
│   │   ├── security.py
│   │   └── validation.py
│   ├── agents/
│   │   ├── loader.py              # Agent loading
│   │   └── wrapper.py             # Agent wrapper (integrates with tracker)
│   ├── mcp/
│   │   ├── client.py              # MCP client
│   │   └── server.py              # MCP server
│   └── runtime/
│       └── process_manager.py     # Process manager (integrates with tracker)
├── cli/
│   └── commands/
│       └── tools/
│           └── main.py            # CLI commands (integrates with tracker)
└── ...
```

## 🔗 **Module Dependencies**

### **Agent-Tools Tracker Dependencies**
```python
# agentmanager/core/tools/agent_tools_tracker.py
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

# Internal dependencies
from .registry import get_global_registry  # For tool validation
```

### **Modules That Depend on Agent-Tools Tracker**
```python
# agentmanager/core/agents/wrapper.py
from agentmanager.core.tools.agent_tools_tracker import get_agent_tools_tracker

# agentmanager/runtime/process_manager.py
from agentmanager.core.tools.agent_tools_tracker import get_agent_tools_tracker

# agentmanager/cli/commands/tools/main.py
from agentmanager.core.tools.agent_tools_tracker import get_agent_tools_tracker
```

## 📦 **Package Exports**

### **Updated `agentmanager/core/tools/__init__.py`**
```python
"""Tool system for AgentHub with @tool decorator and MCP integration."""

from .decorators import (
    tool, register_tool, ToolMetadata, get_tool_metadata, is_tool
)
from .registry import ToolRegistry, get_global_registry
from .discovery import ToolDiscovery
from .agent_tools_tracker import (  # NEW EXPORTS
    AgentToolsTracker, 
    AgentToolAssignment,
    get_agent_tools_tracker
)

__all__ = [
    "tool",
    "register_tool", 
    "ToolMetadata",
    "ToolRegistry",
    "ToolDiscovery",
    "AgentToolsTracker",      # NEW
    "AgentToolAssignment",    # NEW
    "get_agent_tools_tracker", # NEW
    "get_global_registry",
    "get_tool_metadata",
    "is_tool",
]
```

## 🎯 **Integration Points**

### **1. Tool Registry Integration**
- Agent-tools tracker validates tools against global registry
- Ensures only registered tools can be assigned to agents

### **2. Agent Wrapper Integration**
- Agent wrapper registers tool assignments when agent is loaded
- Provides tool context to agents during execution

### **3. Process Manager Integration**
- Process manager queries tracker for agent's assigned tools
- Injects tool context via environment variables

### **4. CLI Integration**
- CLI commands provide management interface for tool assignments
- Commands for viewing, assigning, and managing tool assignments

## 🚀 **Implementation Steps**

### **Step 1: Create Module Structure**
```bash
# Create the new module file
touch agentmanager/core/tools/agent_tools_tracker.py
```

### **Step 2: Implement Core Classes**
```python
# agentmanager/core/tools/agent_tools_tracker.py
@dataclass
class AgentToolAssignment:
    # Implementation

class AgentToolsTracker:
    # Implementation

def get_agent_tools_tracker() -> AgentToolsTracker:
    # Implementation
```

### **Step 3: Update Package Exports**
```python
# Update agentmanager/core/tools/__init__.py
# Add new exports for agent-tools tracker
```

### **Step 4: Integrate with Existing Modules**
- Update `agentmanager/core/agents/wrapper.py`
- Update `agentmanager/runtime/process_manager.py`
- Update `agentmanager/cli/commands/tools/main.py`

### **Step 5: Add Tests**
```python
# tests/phase2_5_semantic_tools/step2_tool_decorator/unit/test_agent_tools_tracker.py
# Comprehensive tests for agent-tools tracker
```

## ✅ **Benefits of This Module Structure**

1. **✅ Logical Organization**: Related functionality grouped together
2. **✅ Clear Dependencies**: Obvious import paths and relationships
3. **✅ Maintainability**: Easy to find and modify tool-related code
4. **✅ Extensibility**: Can add more tracking features to the same module
5. **✅ Testing**: Easy to test in isolation and integration
6. **✅ Documentation**: Clear module boundaries and responsibilities

## 🎯 **Success Criteria**

- [ ] Module created at `agentmanager/core/tools/agent_tools_tracker.py`
- [ ] Package exports updated in `__init__.py`
- [ ] All dependent modules updated with correct imports
- [ ] Integration points working correctly
- [ ] Tests passing for all functionality
- [ ] Documentation updated with module structure

