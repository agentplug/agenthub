# Migration Guide: Examples to Built-in Tools

## Overview

This guide helps migrate from the current examples-based tool system to the new built-in tools system while maintaining 100% backward compatibility. The migration is designed to be seamless with zero breaking changes.

## Current State vs New State

### Current (Examples-based)
```python
# examples/tools/mcp_tool_server.py
@tool(name="add", description="Add two numbers together")
def add(a: int, b: int) -> int:
    return a + b

# Usage requires manual tool definition
from agentmanager.core.tools import tool, run_resources

@tool(name="my_tool", description="My custom tool")
def my_tool():
    return "custom"

run_resources()  # Start MCP server
```

### New (Built-in Tools)
```python
# agentmanager/builtin/tools/categories/math.py
@tool(name="add", description="Add two numbers", namespace="builtin")
def add(a: int, b: int) -> int:
    return a + b

# Usage (same interface!)
import agentmanager as amg
agent = amg.load_agent('agentplug/analysis-agent', tools=['add'])
```

**Context:** The built-in tools system provides the same tools that were previously in examples, but they're now automatically available without manual definition.

## Migration Steps

### Step 1: No Changes Required for Users

**Existing code continues to work unchanged:**

```python
# This still works exactly the same
import agentmanager as amg

agent = amg.load_agent('agentplug/analysis-agent', tools=['add', 'multiply'])
result = agent.execute_tool('add', 5, 3)  # Still returns 8
```

**Context:** The migration is designed to be completely transparent to users. All existing code continues to work without any modifications.

### Step 2: Tool Discovery

**Before (Manual):**
```python
# Had to manually define tools in each script
@tool(name="add", description="Add two numbers")
def add(a: int, b: int) -> int:
    return a + b

# Had to start MCP server manually
run_resources()
```

**After (Automatic):**
```python
# Tools are automatically available
import agentmanager as amg

# Built-in tools are already loaded
tools = amg.get_available_tools()
print(tools)  # ['add', 'subtract', 'multiply', 'divide', 'web_search', ...]
```

**Context:** Built-in tools are automatically loaded when the package is imported, eliminating the need for manual tool definition and MCP server startup.

### Step 3: Tool Categories

**Before (All in one file):**
```python
# examples/tools/mcp_tool_server.py - all tools mixed together
@tool(name="add", description="Add two numbers")
def add(a: int, b: int) -> int:
    return a + b

@tool(name="web_search", description="Search the web")
def web_search(query: str) -> dict:
    # ... implementation
```

**After (Organized by category):**
```python
# agentmanager/builtin/tools/categories/math.py
@tool(name="add", description="Add two numbers", namespace="builtin")
def add(a: int, b: int) -> int:
    return a + b

# agentmanager/builtin/tools/categories/web.py
@tool(name="web_search", description="Search the web", namespace="builtin")
def web_search(query: str) -> dict:
    # ... implementation
```

**Context:** Tools are now organized by category for better maintainability and discoverability, while maintaining the same functionality.

## Tool Mapping

### Math Tools (from examples)
| Example Tool | Built-in Tool | Status | Context |
|-------------|---------------|---------|---------|
| `add` | `add` | ✅ Moved | Same functionality, moved to math category |
| `subtract` | `subtract` | ✅ Moved | Same functionality, moved to math category |
| `multiply` | `multiply` | ✅ Moved | Same functionality, moved to math category |
| `divide` | `divide` | ✅ Moved | Same functionality, moved to math category |
| `compare_numbers` | `compare_numbers` | ✅ Moved | Same functionality, moved to math category |

### Text Tools (from examples)
| Example Tool | Built-in Tool | Status | Context |
|-------------|---------------|---------|---------|
| `process_text` | `process_text` | ✅ Moved | Same functionality, moved to text category |
| `greet` | `greet` | ✅ Moved | Same functionality, moved to text category |

### Web Tools (from examples)
| Example Tool | Built-in Tool | Status | Context |
|-------------|---------------|---------|---------|
| `web_search` | `web_search` | ✅ Moved | Same functionality, moved to web category |
| `get_weather` | `get_weather` | ✅ Moved | Same functionality, moved to web category |

**Context:** All existing tools from examples are moved to appropriate built-in categories, maintaining the same functionality while improving organization.

## Code Changes Required

### For End Users: NONE
```python
# This code works exactly the same before and after migration
import agentmanager as amg

agent = amg.load_agent('agentplug/analysis-agent', tools=['add', 'web_search'])
result = agent.analyze_text("Calculate 5 + 3 and search for weather")
```

**Context:** The migration is designed to be completely transparent to end users. No code changes are required.

### For Developers: Minimal

**Before:**
```python
# Had to import and define tools manually
from agentmanager.core.tools import tool, run_resources

@tool(name="my_tool", description="My custom tool")
def my_tool():
    pass

run_resources()
```

**After:**
```python
# Built-in tools are automatically available
import agentmanager as amg

# Custom tools still work the same way
from agentmanager.core.tools import tool

@tool(name="my_tool", description="My custom tool")
def my_tool():
    pass

# Built-in tools are already loaded
agent = amg.load_agent('agentplug/analysis-agent', tools=['add', 'my_tool'])
```

**Context:** Developers can continue to create custom tools exactly as before, while built-in tools are automatically available.

## Benefits After Migration

### 1. Simplified Development
```python
# Before: Had to copy tool definitions
from examples.tools.mcp_tool_server import add, multiply

# After: Tools are automatically available
import agentmanager as amg
# No imports needed for built-in tools
```

**Context:** Built-in tools eliminate the need to copy tool definitions from examples, simplifying development.

### 2. Better Organization
```python
# Before: All tools in one file
# examples/tools/mcp_tool_server.py (200+ lines)

# After: Organized by category
# agentmanager/builtin/tools/categories/math.py (50 lines)
# agentmanager/builtin/tools/categories/text.py (30 lines)  
# agentmanager/builtin/tools/categories/web.py (80 lines)
```

**Context:** Tools are now organized by category, making them easier to find, maintain, and extend.

### 3. Improved Performance
```python
# Before: Had to start MCP server for every script
run_resources()  # Starts server

# After: Tools loaded once on package import
import agentmanager as amg  # Tools already loaded
```

**Context:** Built-in tools are loaded once when the package is imported, eliminating the need to start MCP servers for each script.

### 4. Enhanced Discovery
```python
# Before: Had to know tool names
tools = ['add', 'multiply', 'web_search']

# After: Can discover available tools
available_tools = amg.get_available_tools()
print(available_tools)  # Shows all available tools
```

**Context:** Built-in tools can be discovered programmatically, making it easier to find and use available tools.

## Backward Compatibility

### 1. Existing Examples Still Work
```python
# examples/tools/agent_loading_with_tools.py
# This file continues to work unchanged
agent = amg.load_agent('agentplug/analysis-agent', tools=['multiply'])
```

**Context:** All existing examples continue to work without any modifications, ensuring complete backward compatibility.

### 2. Custom Tools Still Work
```python
# Custom tools continue to work exactly the same
@tool(name="my_custom_tool", description="My custom tool")
def my_custom_tool():
    pass

agent = amg.load_agent('agentplug/analysis-agent', tools=['my_custom_tool'])
```

**Context:** Custom tools continue to work exactly as before, maintaining the existing development workflow.

### 3. MCP Tools Still Work
```python
# MCP tools continue to work exactly the same
agent = amg.load_agent('agentplug/analysis-agent', tools=['mcp_tool'])
```

**Context:** MCP tools continue to work exactly as before, maintaining compatibility with existing MCP integrations.

## Testing Migration

### 1. Verify Existing Code Works
```python
# Run existing examples
python examples/tools/agent_loading_with_tools.py
# Should work exactly the same
```

**Context:** This test ensures that all existing functionality continues to work after the migration.

### 2. Test New Built-in Tools
```python
# Test built-in tools directly
import agentmanager as amg

# Test math tools
agent = amg.load_agent('agentplug/analysis-agent', tools=['add', 'multiply'])
result = agent.execute_tool('add', 5, 3)
assert result == 8

# Test web tools
agent = amg.load_agent('agentplug/analysis-agent', tools=['web_search'])
result = agent.execute_tool('web_search', 'weather')
assert 'results' in result
```

**Context:** This test verifies that built-in tools work correctly and provide the expected functionality.

### 3. Test Mixed Tool Types
```python
# Test mixing custom, MCP, and built-in tools
@tool(name="custom_tool", description="Custom tool")
def custom_tool():
    return "custom"

agent = amg.load_agent('agentplug/analysis-agent', tools=[
    'add',           # Built-in
    'custom_tool',   # Custom
    'mcp_tool'       # MCP
])
```

**Context:** This test ensures that different tool types can be used together seamlessly.

## Common Issues and Solutions

### Issue 1: Tool Not Found
```python
# Error: Tool 'add' not found
# Solution: Ensure built-in tools are loaded
import agentmanager as amg  # This loads built-in tools
```

**Context:** Built-in tools are loaded automatically when the package is imported, so this error should not occur in normal usage.

### Issue 2: Import Errors
```python
# Error: ImportError: No module named 'ddgs'
# Solution: Install optional dependencies
pip install ddgs requests beautifulsoup4 aiohttp
```

**Context:** Some built-in tools have optional dependencies that need to be installed for full functionality.

### Issue 3: Performance Issues
```python
# Issue: Slow startup
# Solution: Built-in tools are loaded once, not per script
```

**Context:** Built-in tools are loaded once when the package is imported, not every time a script runs.

## Best Practices

### 1. Use Built-in Tools When Available
```python
# Good: Use built-in tools
agent = amg.load_agent('agentplug/analysis-agent', tools=['add', 'web_search'])

# Avoid: Redefining existing tools
@tool(name="add", description="Add numbers")  # Don't redefine built-in tools
def my_add(a, b):
    return a + b
```

**Context:** Built-in tools are designed to be used directly, avoiding the need to redefine existing functionality.

### 2. Create Custom Tools for Specific Needs
```python
# Good: Create custom tools for specific use cases
@tool(name="my_business_logic", description="My specific business logic")
def my_business_logic(data):
    # Custom implementation
    pass
```

**Context:** Custom tools should be created for specific business logic that isn't covered by built-in tools.

### 3. Use Appropriate Categories
```python
# Good: Use tools from appropriate categories
math_tools = ['add', 'multiply', 'divide']
text_tools = ['process_text', 'greet']
web_tools = ['web_search', 'fetch_url']
```

**Context:** Understanding tool categories helps in selecting the right tools for specific tasks.

## Rollback Plan

If issues arise during migration:

### 1. Disable Built-in Tools
```python
# agentmanager/__init__.py
# Comment out built-in tools loading
# load_all_builtin_tools()  # Disabled
```

**Context:** Built-in tools can be disabled by commenting out the auto-loading code.

### 2. Revert to Examples
```python
# Use examples/tools/mcp_tool_server.py
from examples.tools.mcp_tool_server import run_resources
run_resources()
```

**Context:** The original examples-based system remains available as a fallback.

### 3. Gradual Migration
```python
# Migrate one category at a time
# Start with math tools, then text, then web
```

**Context:** Migration can be done gradually, one category at a time, to minimize risk.

## Summary

The migration to built-in tools provides significant benefits with zero breaking changes:

- ✅ **No code changes required** for existing users
- ✅ **Better organization** with tool categories
- ✅ **Improved performance** with auto-loading
- ✅ **Enhanced discoverability** of available tools
- ✅ **Full backward compatibility** with existing code
- ✅ **Easy rollback** if issues arise

The migration is designed to be seamless and risk-free, providing a solid foundation for future tool development.

**Context:** This migration guide ensures that users can benefit from built-in tools without any disruption to their existing workflows, while providing a clear path for future enhancements.
