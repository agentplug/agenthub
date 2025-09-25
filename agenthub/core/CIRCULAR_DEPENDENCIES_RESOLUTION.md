# Circular Dependencies Resolution

This document explains how circular dependencies have been resolved in the AgentHub codebase.

## 🔄 **Problem Analysis**

### **Identified Circular Dependencies:**

1. **agents ↔ tools**:
   - `agents/wrapper.py` → `tools.exceptions` → `agents/__init__.py` → `tools.exceptions`

2. **agents ↔ mcp**:
   - `agents/wrapper.py` → `mcp/agent_tool_manager.py` → `tools` → `agents`

3. **agents ↔ llm**:
   - `agents/solve/framework_handler.py` → `llm/llm_service.py` → `agents`

4. **mcp ↔ tools**:
   - `mcp/agent_tool_manager.py` → `tools` → `mcp`

## 🛠️ **Solution Architecture**

### **1. Interface-Based Design**

Created protocol interfaces in `core/interfaces/` to define contracts without concrete implementations:

- `AgentInfoProtocol`: Agent information contract
- `AgentWrapperProtocol`: Agent wrapper contract
- `ToolRegistryProtocol`: Tool registry contract
- `ToolManagerProtocol`: Tool manager contract
- `LLMServiceProtocol`: LLM service contract
- `KnowledgeManagerProtocol`: Knowledge manager contract

### **2. Dependency Injection Container**

Implemented a simple DI container in `core/di/`:

- `DIContainer`: Singleton container for service registration
- `providers.py`: Service providers for creating instances
- `setup.py`: Container setup with default services

### **3. Lazy Import Pattern**

Moved imports inside methods/functions to break circular import chains:

```python
# Before (circular import)
from ..tools import get_tool_registry

# After (lazy import)
def some_method(self):
    from ..tools import get_tool_registry
    return get_tool_registry()
```

## 📁 **New File Structure**

```
core/
├── interfaces/
│   ├── __init__.py
│   ├── agent_interfaces.py
│   ├── tool_interfaces.py
│   ├── llm_interfaces.py
│   └── knowledge_interfaces.py
├── di/
│   ├── __init__.py
│   ├── container.py
│   ├── providers.py
│   └── setup.py
└── agents/
    ├── factory.py  # New factory with DI
    ├── wrapper.py  # Updated with interfaces
    └── solve/
        ├── engine.py  # Updated with interfaces
        └── framework_handler.py  # Updated with DI
```

## 🔧 **Implementation Details**

### **Agent Wrapper Refactoring**

```python
class AgentWrapper:
    def __init__(
        self,
        agent_info: dict,
        # ... other params
        knowledge_manager: KnowledgeManagerProtocol | None = None,
        tool_manager: ToolManagerProtocol | None = None,
    ) -> None:
        # Use dependency injection or create defaults
        if knowledge_manager is not None:
            self.knowledge_manager = knowledge_manager
        else:
            # Import here to avoid circular dependency
            from ..knowledge import KnowledgeManager
            self.knowledge_manager = KnowledgeManager()
```

### **Solve Engine Refactoring**

```python
class SolveEngine:
    def __init__(
        self,
        agent_wrapper: AgentWrapperProtocol,
        llm_service: Any = None
    ) -> None:
        # Pass LLM service to framework handler
        self.framework_handler = FrameworkSolveHandler(agent_wrapper, llm_service)
```

### **Framework Handler Refactoring**

```python
class FrameworkSolveHandler:
    def __init__(
        self,
        agent_wrapper: AgentWrapperProtocol,
        llm_service: LLMServiceProtocol | None = None
    ) -> None:
        self.llm_service = llm_service
```

## 🚀 **Usage Examples**

### **Using the Factory**

```python
from agenthub.core.agents.factory import get_agent_wrapper_factory

factory = get_agent_wrapper_factory()
wrapper = factory.create_wrapper(agent_info)
```

### **Manual Dependency Injection**

```python
from agenthub.core.interfaces import KnowledgeManagerProtocol
from agenthub.core.di import get_container

container = get_container()
knowledge_manager = container.get(KnowledgeManagerProtocol)

wrapper = AgentWrapper(
    agent_info=agent_info,
    knowledge_manager=knowledge_manager
)
```

## ✅ **Benefits**

1. **No Circular Imports**: All circular dependencies resolved
2. **Better Testability**: Easy to inject mock dependencies
3. **Type Safety**: Protocol interfaces provide better type hints
4. **Flexibility**: Components can be easily swapped
5. **Maintainability**: Clear separation of concerns

## 🔄 **Migration Guide**

### **For Existing Code:**

1. **Replace direct imports** with interface protocols where possible
2. **Use lazy imports** for remaining dependencies
3. **Consider using the factory** for creating agent wrappers
4. **Update tests** to use dependency injection

### **For New Code:**

1. **Define protocols** for new interfaces
2. **Use dependency injection** in constructors
3. **Register services** in the DI container
4. **Avoid direct imports** between circular modules

## 🧪 **Testing**

The DI container supports easy testing with mock services:

```python
from agenthub.core.di.setup import setup_di_container_for_testing

# Setup mock services for testing
setup_di_container_for_testing()

# Now all components will use mock dependencies
```

## 📝 **Notes**

- Both `wrapper.py` and `wrapper_old.py` are kept as reference
- The new architecture maintains backward compatibility
- All existing functionality is preserved
- The solution is incremental and can be applied gradually
