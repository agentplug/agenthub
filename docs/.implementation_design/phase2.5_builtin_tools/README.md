# Phase 2.5: Built-in Tools Implementation

## Overview

This phase implements a comprehensive built-in tools system for AgentManager, providing users with a rich library of pre-built, ready-to-use tools while maintaining 100% backward compatibility with existing custom and MCP tools.

## Design Philosophy

- **Single Interface**: All tools use the same `amg.load_agent(agent, tools=[...])` interface
- **Auto-Loading**: Critical tools load automatically, no manual setup required
- **Clear Organization**: Tools organized by category for easy discovery
- **Minimal API**: Only essential functions exposed to users
- **Incremental Development**: Start with basic categories, add more as needed
- **Simple Configuration**: Basic config options only, avoid complex settings
- **Focus on Core Use Cases**: Math, text, and web tools are the priority

## High-Level Architecture

### Directory Structure
```
agentmanager/
├── builtin/                           # NEW: Top-level builtin module
│   ├── __init__.py
│   ├── tools/                         # Built-in tools package
│   │   ├── __init__.py
│   │   ├── base.py                    # Base classes and interfaces
│   │   ├── loader.py                  # Auto-loading mechanism
│   │   ├── registry.py                # Built-in tool registry
│   │   └── categories/                # Tool categories
│   │       ├── __init__.py
│   │       ├── math.py               # Math operations
│   │       ├── text.py               # Text processing tools
│   │       ├── web.py                # Web tools (CRITICAL - always loaded)
│   │       ├── data.py               # Data manipulation (lazy-loaded)
│   │       └── system.py             # System utilities (lazy-loaded)
│   └── config.py                      # Configuration
├── core/tools/                        # Existing (unchanged)
└── examples/tools/                    # Existing (unchanged)
```

### Tool Integration with Existing System

The built-in tools system integrates seamlessly with the existing AgentManager tool infrastructure:

```python
# Current ToolRegistry (unchanged)
class ToolRegistry:
    def __init__(self):
        self.mcp_server = FastMCP("AgentHub Tools")
        self.registered_tools: Dict[str, Callable] = {}      # Custom tools
        self.tool_metadata: Dict[str, ToolMetadata] = {}     # All tool metadata
        self.agent_tool_access: Dict[str, List[str]] = {}    # Agent access control
```

**Integration Points:**

#### 1. Registry Integration
- Built-in tools register with the existing `ToolRegistry` using the same `register_tool()` method
- All tools (custom, MCP, built-in) are stored in the same `registered_tools` dictionary
- Tool metadata is managed through the same `tool_metadata` system
- No changes required to the core registry implementation

#### 2. Namespace System
- Built-in tools use `namespace="builtin"` to distinguish from other tool types
- Existing namespaces (`custom`, `mcp`) remain unchanged
- Tool discovery and filtering can be done by namespace if needed
- Maintains clear separation between tool sources

#### 3. Tool Discovery
- Built-in tools are included in `get_available_tools()` alongside custom and MCP tools
- The discovery mechanism is extended to check built-in tool categories
- Users see all available tools through the same interface
- No changes required to existing discovery code

#### 4. Agent Access Control
- Built-in tools use the same agent access control system as existing tools
- Tools are assigned to agents using `assign_tools_to_agent()`
- Access checking works identically for all tool types
- No changes required to the access control implementation

#### 5. Tool Execution
- Built-in tools execute through the same `execute_tool()` path as custom tools
- Once registered, all tools are treated identically by the execution system
- No changes required to the tool execution infrastructure
- Maintains consistent behavior across all tool types

#### 6. MCP Server Integration
- Built-in tools are registered with the FastMCP server just like custom tools
- The MCP server treats all registered tools identically
- No changes required to the MCP server implementation
- Maintains compatibility with existing MCP clients

## Hybrid Loading Strategy

### Auto-loaded Categories (Critical Tools)
```python
# These are loaded automatically when agentmanager is imported
auto_load_categories = ['math', 'text', 'web']  # web is CRITICAL
```

**Rationale:**
- **Math & Text**: Lightweight, commonly used, no external dependencies
- **Web**: **CRITICAL** - web search is essential for agent functionality and should always be available

### Lazy-loaded Categories (Heavy Tools)
```python
# These are loaded only when explicitly requested
lazy_load_categories = ['data', 'system']
```

**Rationale:**
- **Data**: May have heavy dependencies (pandas, numpy)
- **System**: Platform-specific, not always needed

## Tool Categories

### 1. Math Tools (Auto-loaded)
**Purpose:** Basic mathematical operations and calculations
**Dependencies:** None (pure Python)
**Tools:** `add`, `subtract`, `multiply`, `divide`, `compare_numbers`, `power`, `sqrt`

### 2. Text Tools (Auto-loaded)
**Purpose:** Text processing and manipulation
**Dependencies:** None (pure Python)
**Tools:** `process_text`, `greet`, `text_length`, `extract_numbers`, `extract_emails`

### 3. Web Tools (Auto-loaded)
**Purpose:** Web-related operations and data fetching
**Dependencies:** `ddgs`, `requests`, `beautifulsoup4`, `aiohttp`
**Tools:** `web_search`, `fetch_url`, `validate_url`

### 4. Data Tools (Lazy-loaded)
**Purpose:** Data manipulation and format conversion
**Dependencies:** `pandas`, `numpy` (optional)
**Tools:** `json_parse`, `json_stringify`, `csv_to_json`, `data_validate`

### 5. System Tools (Lazy-loaded)
**Purpose:** System information and utilities
**Dependencies:** `psutil` (optional)
**Tools:** `get_timestamp`, `get_system_info`, `file_exists`, `directory_list`

## Tool Resolution

### Tool Discovery Hierarchy
When `load_agent()` is called with tools, the system follows this resolution order:

```python
def load_agent(agent, tools):
    for tool_name in tools:
        if not tool_registry.is_tool_registered(tool_name):
            # Try to load as built-in tool
            if load_builtin_tool(tool_name):
                continue
            else:
                raise ValueError(f"Tool '{tool_name}' not found")
```

**Resolution Hierarchy:**
1. **Custom tools** (via `@tool` decorator) - checked first
2. **MCP tools** (from MCP server) - checked second
3. **Built-in tools** (auto-loaded or lazy-loaded) - checked last

### Tool Registration Flow
```
User Code → @tool decorator → ToolRegistry → FastMCP Server
                ↓
        Built-in Tools → BuiltinToolLoader → ToolRegistry → FastMCP Server
```

**All tools end up in the same registry with different namespaces:**
- `custom` - User-defined tools via `@tool` decorator
- `mcp` - Tools from MCP server
- `builtin` - Pre-built tools from agentmanager

## User Experience

### Zero Learning Curve
```python
# Same interface as before - no changes required
import agentmanager as amg

# Built-in tools work seamlessly
agent = amg.load_agent('agentplug/analysis-agent', tools=[
    'add',           # Math tool (auto-loaded)
    'web_search',    # Web tool (auto-loaded - CRITICAL)
    'process_text'   # Text tool (auto-loaded)
])

# Execute tools the same way
result = agent.execute_tool('add', 5, 3)  # Returns 8
```

### Tool Discovery
```python
# Built-in tools are automatically available
tools = amg.get_available_tools()
print(tools)  # ['add', 'subtract', 'multiply', 'web_search', ...]

# Or discover by category (optional advanced usage)
from agentmanager.builtin.tools import list_builtin_tools
categories = list_builtin_tools()
print(categories['web'])  # ['web_search', 'fetch_url', 'validate_url']
```

### Mixed Tool Usage
```python
# Mix custom, MCP, and built-in tools seamlessly
@tool(name="my_custom_tool", description="My custom tool")
def my_custom_tool():
    return "custom"

agent = amg.load_agent('agentplug/analysis-agent', tools=[
    'add',              # Built-in tool
    'my_custom_tool',   # Custom tool
    'mcp_tool'          # MCP tool
])
```

## Configuration

### Built-in Tools Configuration
```python
@dataclass
class BuiltinToolsConfig:
    # Auto-loading settings
    auto_load_enabled: bool = True
    auto_load_categories: List[str] = ['math', 'text', 'web']
    
    # Tool-specific settings
    web_search_max_results: int = 5
    web_search_timeout: int = 10
    
    # Optional dependencies
    optional_dependencies: Dict[str, List[str]] = {
        'data': ['pandas', 'numpy'],
        'system': ['psutil']
    }
```

### Integration with Main Config
```python
# agentmanager/config.py
class AgentHubConfig:
    # ... existing config ...
    
    # Built-in tools config
    builtin_tools: BuiltinToolsConfig = BuiltinToolsConfig()
```

### Configuration Management
- **Centralized Settings**: All built-in tool settings are managed through `BuiltinToolsConfig`
- **Environment Variables**: Configuration can be overridden via environment variables
- **Runtime Configuration**: Settings can be modified at runtime without restart
- **Validation**: Configuration values are validated on startup
- **Defaults**: Sensible defaults ensure the system works out of the box

## Error Handling

### Dependency Management
```python
try:
    import pandas
    # Load data tools
except ImportError:
    logger.warning("Pandas not available, data tools disabled")
    # Skip data tools gracefully
```

**Dependency Handling Strategy:**
- **Optional Dependencies**: Heavy dependencies are marked as optional
- **Graceful Degradation**: Tools with missing dependencies are skipped, not failed
- **Clear Logging**: Users are informed about missing dependencies
- **Installation Hints**: Error messages suggest how to install missing packages
- **Category-level Control**: Entire categories can be disabled if dependencies are missing

### Tool Resolution Errors
```python
# Clear error messages for missing tools
if tool_name not in available_tools:
    raise ValueError(f"Tool '{tool_name}' not found in custom, MCP, or built-in tools")
```

**Error Handling Strategy:**
- **Hierarchical Resolution**: Tools are checked in order (custom → MCP → built-in)
- **Clear Error Messages**: Users get specific information about why a tool wasn't found
- **Suggestions**: Error messages can suggest similar tool names or installation steps
- **Debugging Information**: Detailed error messages help with troubleshooting
- **Graceful Failures**: System continues to work even if some tools are unavailable

### Tool Execution Errors
```python
try:
    result = tool_func(*args, **kwargs)
    return result
except Exception as e:
    logger.error(f"Tool execution failed: {e}")
    raise ToolExecutionError(f"Tool '{tool_name}' failed: {e}")
```

**Execution Error Handling:**
- **Exception Wrapping**: Tool exceptions are wrapped with context information
- **Logging**: All tool execution errors are logged for debugging
- **Error Propagation**: Errors are propagated to the caller with context
- **Timeout Handling**: Long-running tools can be configured with timeouts
- **Retry Logic**: Transient failures can be retried automatically

### Graceful Degradation
- **Tool Availability**: Tools with missing dependencies are skipped, not failed
- **Category Fallback**: If a category can't be loaded, other categories continue to work
- **Partial Loading**: System works with whatever tools are available
- **User Notification**: Users are informed about what tools are available
- **Fallback Behavior**: Alternative tools or behaviors when primary tools fail

## Performance Considerations

### Startup Time
- **Auto-loaded categories**: Loaded on package import (math, text, web)
- **Lazy-loaded categories**: Loaded only when needed (data, system)
- **Tool discovery**: Cached after first discovery

### Memory Usage
- **Tool functions**: Stored in registry (minimal overhead)
- **Tool metadata**: Cached for quick access
- **Dependencies**: Only loaded when tools are used

### Execution Performance
- **Custom tools**: Direct function call (fastest)
- **Built-in tools**: Direct function call (same as custom)
- **MCP tools**: HTTP call (slowest)

## Benefits

### For Users
- ✅ **Zero breaking changes** - existing code works unchanged
- ✅ **Rich tool library** - pre-built tools for common tasks
- ✅ **No setup required** - critical tools work out of the box
- ✅ **Seamless integration** - built-in tools work with existing workflow

### For Developers
- ✅ **Clean architecture** - clear separation of concerns
- ✅ **Easy extension** - simple to add new tool categories
- ✅ **Maintainable** - each category maintained independently
- ✅ **Testable** - tools can be tested in isolation

## Success Metrics

### Functional Requirements
- [ ] 100% backward compatibility with existing code
- [ ] Built-in tools available via `load_agent()`
- [ ] Auto-loading works for critical tools (math, text, web)
- [ ] Lazy loading works for heavy tools (data, system)
- [ ] Tool discovery includes built-in tools

### Performance Requirements
- [ ] Startup time impact < 100ms
- [ ] Tool execution performance same as custom tools
- [ ] Memory usage increase < 10MB

### Quality Requirements
- [ ] 90%+ test coverage
- [ ] All tools have proper error handling
- [ ] Documentation is complete and clear

## Next Steps

1. **Review and approve** this implementation design
2. **Create directory structure** and base files
3. **Implement core categories** (math, text, web)
4. **Update load_agent()** with smart resolution
5. **Test with existing examples** to ensure compatibility
6. **Add documentation** and examples

---

*This implementation provides a solid foundation for future tool development while maintaining simplicity and focusing on essential functionality.*
