# Built-in Tools Architecture

## System Overview

The built-in tools system extends the existing AgentManager tool infrastructure without breaking changes, providing a rich library of pre-built tools organized by category. The system follows a hybrid loading approach where critical tools are auto-loaded while heavy tools are loaded on-demand.

## Core Architecture Components

### 1. Tool Registry Integration

The built-in tools system integrates seamlessly with the existing `ToolRegistry`:

```python
# Existing ToolRegistry (unchanged)
class ToolRegistry:
    def __init__(self):
        self.mcp_server = FastMCP("AgentHub Tools")
        self.registered_tools: Dict[str, Callable] = {}      # Custom tools
        self.tool_metadata: Dict[str, ToolMetadata] = {}     # All tool metadata
        self.agent_tool_access: Dict[str, List[str]] = {}    # Agent access control
```

**Integration Points:**
- Built-in tools register with existing `ToolRegistry`
- Same namespace system (`custom`, `mcp`, `builtin`)
- Same tool discovery mechanism via `get_available_tools()`
- Same agent access control system

**Context:** This ensures that built-in tools are treated as first-class citizens alongside custom and MCP tools, maintaining the existing system's simplicity while adding new functionality.

### 2. Directory Structure

```
agentmanager/
├── builtin/                           # NEW: Top-level builtin module
│   ├── __init__.py                    # Package initialization
│   ├── tools/                         # Built-in tools package
│   │   ├── __init__.py               # Tool package initialization
│   │   ├── base.py                   # Base classes and interfaces
│   │   ├── loader.py                 # Auto-loading mechanism
│   │   ├── registry.py               # Built-in tool registry
│   │   └── categories/               # Tool categories
│   │       ├── __init__.py
│   │       ├── math.py              # Math operations (auto-loaded)
│   │       ├── text.py              # Text processing (auto-loaded)
│   │       ├── web.py               # Web tools (auto-loaded)
│   │       ├── data.py              # Data manipulation (lazy-loaded)
│   │       └── system.py            # System utilities (lazy-loaded)
│   └── config.py                     # Built-in tools configuration
├── core/tools/                        # Existing (unchanged)
└── examples/tools/                    # Existing (unchanged)
```

**Context:** This structure separates built-in tools from core infrastructure while maintaining clear organization and avoiding conflicts with existing code.

## Tool Loading Strategy

### Hybrid Loading Implementation

The system implements a hybrid loading strategy that balances performance with functionality:

```python
# Auto-loaded categories (loaded on package import)
auto_load_categories = ['math', 'text', 'web']

# Lazy-loaded categories (loaded when needed)
lazy_load_categories = ['data', 'system']
```

**Context:** This approach ensures that critical tools like web search are always available while keeping the system performant by not loading heavy tools until needed.

### Tool Resolution Flow

When a user calls `load_agent()` with tools, the system follows this resolution hierarchy:

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

**Context:** This ensures that existing tools take precedence while providing seamless access to built-in tools when needed.

## Tool Categories Architecture

### 1. Math Tools (Auto-loaded)

**Purpose:** Basic mathematical operations and calculations
**Dependencies:** None (pure Python)
**Auto-load:** Yes (critical for agent functionality)

```python
# agentmanager/builtin/tools/categories/math.py
from ...core.tools import tool

@tool(name="add", description="Add two numbers", namespace="builtin")
def add(a: int, b: int) -> int:
    return a + b

@tool(name="multiply", description="Multiply two numbers", namespace="builtin")
def multiply(a: int, b: int) -> int:
    return a * b
```

**Context:** These tools are moved from the examples and provide essential mathematical capabilities that agents commonly need.

### 2. Text Tools (Auto-loaded)

**Purpose:** Text processing and manipulation
**Dependencies:** None (pure Python)
**Auto-load:** Yes (commonly used)

```python
# agentmanager/builtin/tools/categories/text.py
from ...core.tools import tool

@tool(name="process_text", description="Process text with operations", namespace="builtin")
def process_text(text: str, operation: str = "uppercase") -> str:
    operations = {
        "uppercase": text.upper(),
        "lowercase": text.lower(),
        "titlecase": text.title(),
        "reverse": text[::-1],
        "wordcount": str(len(text.split())),
        "charcount": str(len(text))
    }
    return operations.get(operation, text)
```

**Context:** These tools provide essential text processing capabilities with clear operation definitions and proper error handling.

### 3. Web Tools (Auto-loaded)

**Purpose:** Web-related operations and data fetching
**Dependencies:** `ddgs`, `requests`, `beautifulsoup4`, `aiohttp`
**Auto-load:** Yes (critical for agent functionality)

```python
# agentmanager/builtin/tools/categories/web.py
from ...core.tools import tool

@tool(name="web_search", description="Search the web", namespace="builtin")
def web_search(query: str) -> dict:
    """Search the web for a query using DuckDuckGo and return summarized results.
    """
    try:
        from ddgs import DDGS
        # ... implementation moved from examples
    except ImportError:
        raise ImportError("Required packages not installed")
    
    return {"results": results}
```

**Context:** This is the most critical category as web search is essential for agent functionality. The implementation is moved from examples and enhanced with proper error handling.

### 4. Data Tools (Lazy-loaded)

**Purpose:** Data manipulation and format conversion
**Dependencies:** `pandas`, `numpy` (optional)
**Auto-load:** No (heavy dependencies)

```python
# agentmanager/builtin/tools/categories/data.py
from ...core.tools import tool

@tool(name="json_parse", description="Parse JSON string", namespace="builtin")
def json_parse(json_string: str) -> dict:
    try:
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
```

**Context:** These tools are loaded only when needed to avoid the overhead of heavy dependencies like pandas and numpy.

### 5. System Tools (Lazy-loaded)

**Purpose:** System information and utilities
**Dependencies:** `psutil` (optional)
**Auto-load:** No (platform-specific)

```python
# agentmanager/builtin/tools/categories/system.py
from ...core.tools import tool

@tool(name="get_timestamp", description="Get current timestamp", namespace="builtin")
def get_timestamp() -> str:
    return datetime.now().isoformat() + "Z"
```

**Context:** These tools provide system-level functionality that may not be needed in all use cases.

## Tool Registration Flow

### Registration Process

```
User Code → @tool decorator → ToolRegistry → FastMCP Server
                ↓
        Built-in Tools → BuiltinToolLoader → ToolRegistry → FastMCP Server
```

**Context:** All tools, regardless of type, end up in the same registry with different namespaces, ensuring consistent behavior and access control.

### Namespace Management

```python
namespaces = {
    'custom': 'User-defined tools via @tool decorator',
    'mcp': 'Tools from MCP server',
    'builtin': 'Pre-built tools from agentmanager'
}
```

**Context:** This namespace system allows the registry to distinguish between different tool sources while maintaining a unified interface.

## Data Flow Architecture

### Tool Discovery Flow

```python
def get_available_tools() -> List[str]:
    # 1. Get custom tools (existing)
    custom_tools = list(registered_tools.keys())
    
    # 2. Get MCP tools (existing)
    mcp_tools = discover_mcp_tools()
    
    # 3. Get built-in tools (NEW)
    builtin_tools = discover_builtin_tools()
    
    # 4. Combine all sources
    return list(set(custom_tools + mcp_tools + builtin_tools))
```

**Context:** This ensures that all tool types are discoverable through the same interface, maintaining consistency for users.

### Tool Execution Flow

```python
def execute_tool(tool_name, *args, **kwargs):
    # Same execution path for all tool types
    tool_func = get_tool_function(tool_name)
    return tool_func(*args, **kwargs)
```

**Context:** Once registered, all tools execute through the same path, ensuring consistent behavior regardless of tool source.

## Configuration Management

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

**Context:** This configuration system allows fine-tuning of tool loading behavior and tool-specific settings while maintaining sensible defaults.

### Integration with Main Config

```python
# agentmanager/config.py
class AgentHubConfig:
    # ... existing config ...
    
    # Built-in tools config
    builtin_tools: BuiltinToolsConfig = BuiltinToolsConfig()
```

**Context:** This integrates built-in tools configuration with the existing configuration system, maintaining consistency.

## Error Handling Architecture

### Dependency Management

```python
try:
    import pandas
    # Load data tools
except ImportError:
    logger.warning("Pandas not available, data tools disabled")
    # Skip data tools gracefully
```

**Context:** This ensures that missing dependencies don't break the system, allowing graceful degradation.

### Tool Resolution Errors

```python
# Clear error messages for missing tools
if tool_name not in available_tools:
    raise ValueError(f"Tool '{tool_name}' not found in custom, MCP, or built-in tools")
```

**Context:** This provides clear feedback to users when tools are not available, helping with debugging.

### Graceful Degradation

- Tools with missing dependencies are skipped
- Clear error messages for missing tools
- Fallback behavior when possible

**Context:** This ensures that the system remains functional even when some tools are not available.

## Performance Architecture

### Startup Time Optimization

```python
# Auto-loaded categories: Loaded on package import
auto_load_categories = ['math', 'text', 'web']

# Lazy-loaded categories: Loaded only when needed
lazy_load_categories = ['data', 'system']
```

**Context:** This balances immediate availability of critical tools with startup performance.

### Memory Usage Optimization

```python
# Tool functions: Stored in registry (minimal overhead)
# Tool metadata: Cached for quick access
# Dependencies: Only loaded when tools are used
```

**Context:** This ensures that the system doesn't consume excessive memory when tools are not being used.

### Execution Performance

```python
# Custom tools: Direct function call (fastest)
# Built-in tools: Direct function call (same as custom)
# MCP tools: HTTP call (slowest)
```

**Context:** This ensures that built-in tools perform as well as custom tools, maintaining system efficiency.

## Security Architecture

### Tool Access Control

```python
# Same access control as existing tools
# Agent-specific tool assignments
# No additional security risks
```

**Context:** This ensures that built-in tools follow the same security model as existing tools.

### Dependency Security

```python
# Optional dependencies handled gracefully
# No automatic package installation
# Clear error messages for missing dependencies
```

**Context:** This ensures that the system doesn't introduce security risks through automatic package installation.

## Testing Architecture

### Unit Testing

```python
# Test each tool category independently
# Test tool loading mechanisms
# Test error handling
```

**Context:** This ensures that each component works correctly in isolation.

### Integration Testing

```python
# Test tool resolution in load_agent()
# Test mixed tool usage (custom + built-in + MCP)
# Test backward compatibility
```

**Context:** This ensures that all components work together correctly and that existing functionality is preserved.

### Performance Testing

```python
# Measure startup time impact
# Measure tool execution performance
# Test memory usage
```

**Context:** This ensures that the system maintains its performance characteristics.

## Future Extensibility

### Adding New Categories

1. Create new category file in `categories/`
2. Add tools with `@tool` decorator
3. Update auto-load configuration if needed
4. Add tests

**Context:** This provides a clear path for extending the system with new tool categories.

### Adding New Tools

1. Add tool function to appropriate category
2. Use `@tool` decorator with `namespace="builtin"`
3. Add tests
4. Update documentation

**Context:** This provides a simple process for adding new tools to existing categories.

### Third-party Integration

- Built-in tools can be extended by third parties
- Plugin architecture for custom categories
- Tool marketplace potential

**Context:** This provides a foundation for future ecosystem development.

## Summary

The built-in tools architecture provides a solid foundation for extending AgentManager with pre-built tools while maintaining the existing system's simplicity, performance, and reliability. The hybrid loading approach ensures that critical tools are always available while keeping the system efficient, and the clear separation of concerns makes the system maintainable and extensible.

The architecture implements only what's needed for Phase 2.5 while providing a clear path for future enhancements. The integration with the existing system is seamless, ensuring that users can benefit from built-in tools without any changes to their existing code.
