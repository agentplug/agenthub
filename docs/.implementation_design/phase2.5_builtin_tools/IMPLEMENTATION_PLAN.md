# Built-in Tools Implementation Plan

## Overview

This document provides a detailed, step-by-step implementation plan for Phase 2.5 built-in tools, following the hybrid loading approach with web search as a critical always-loaded tool.

## Phase 1: Foundation Setup (Week 1)

### 1.1 Directory Structure Creation

**Objective:** Create the complete directory structure for built-in tools

**Files to Create:**
```bash
# Create main directories
mkdir -p agentmanager/builtin/tools/categories
mkdir -p agentmanager/builtin/tools/tests

# Create base files
touch agentmanager/builtin/__init__.py
touch agentmanager/builtin/tools/__init__.py
touch agentmanager/builtin/tools/base.py
touch agentmanager/builtin/tools/loader.py
touch agentmanager/builtin/tools/registry.py
touch agentmanager/builtin/config.py
touch agentmanager/builtin/tools/categories/__init__.py
```

**Context:** This creates the foundation structure that separates built-in tools from the core tool infrastructure while maintaining clear organization.

### 1.2 Base Classes Implementation

**File:** `agentmanager/builtin/tools/base.py`

```python
"""Base classes for built-in tools."""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Callable

class BuiltinTool(ABC):
    """Abstract base class for built-in tool categories."""
    
    @abstractmethod
    def get_tools(self) -> List[Dict[str, Any]]:
        """Return list of tools in this category.
        
        Returns:
            List of dictionaries containing tool information:
            - name: Tool name
            - func: Tool function
            - description: Tool description
        """
        pass

class ToolCategory:
    """Container for a tool category."""
    
    def __init__(self, name: str, tools: List[Dict[str, Any]]):
        self.name = name
        self.tools = tools
    
    def get_tool_names(self) -> List[str]:
        """Get list of tool names in this category."""
        return [tool['name'] for tool in self.tools]
```

**Context:** These base classes provide the foundation for organizing tools by category and ensure consistent tool registration across all categories.

### 1.3 Configuration System

**File:** `agentmanager/builtin/config.py`

```python
"""Configuration for built-in tools."""

from typing import List, Dict
from dataclasses import dataclass

@dataclass
class BuiltinToolsConfig:
    """Configuration for built-in tools."""
    
    # Auto-loading settings
    auto_load_enabled: bool = True
    auto_load_categories: List[str] = ['math', 'text', 'web']
    
    # Lazy-loading settings
    lazy_load_categories: List[str] = ['data', 'system']
    
    # Tool-specific settings
    web_search_max_results: int = 5
    web_search_timeout: int = 10
    
    # Optional dependencies
    optional_dependencies: Dict[str, List[str]] = {
        'data': ['pandas', 'numpy'],
        'system': ['psutil']
    }
    
    # Tool categories configuration
    categories: Dict[str, Dict[str, Any]] = {
        'math': {
            'enabled': True,
            'tools': ['add', 'subtract', 'multiply', 'divide', 'compare_numbers']
        },
        'text': {
            'enabled': True,
            'tools': ['process_text', 'greet', 'text_length']
        },
        'web': {
            'enabled': True,
            'tools': ['web_search', 'fetch_url', 'validate_url']
        }
    }
```

**Context:** This configuration system allows fine-tuning of which tools are loaded and how they behave, with web search marked as critical for auto-loading.

## Phase 2: Core Categories Implementation (Week 2)

### 2.1 Math Tools Category

**File:** `agentmanager/builtin/tools/categories/math.py`

```python
"""Math tools category - basic mathematical operations."""

from ...core.tools import tool
from ..base import BuiltinTool

class MathTools(BuiltinTool):
    """Math tools category."""
    
    def get_tools(self):
        return [
            {'name': 'add', 'func': add, 'description': 'Add two numbers'},
            {'name': 'subtract', 'func': subtract, 'description': 'Subtract two numbers'},
            {'name': 'multiply', 'func': multiply, 'description': 'Multiply two numbers'},
            {'name': 'divide', 'func': divide, 'description': 'Divide two numbers'},
            {'name': 'compare_numbers', 'func': compare_numbers, 'description': 'Compare two numbers'},
        ]

# Tool implementations moved from examples/tools/mcp_tool_server.py
@tool(name="add", description="Add two numbers", namespace="builtin")
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    print(f"[TOOL] Adding {a} + {b}")
    return a + b

@tool(name="subtract", description="Subtract two numbers", namespace="builtin")
def subtract(a: int, b: int) -> int:
    """Subtract the second number from the first."""
    print(f"[TOOL] Subtracting {a} - {b}")
    return a - b

@tool(name="multiply", description="Multiply two numbers", namespace="builtin")
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    print(f"[TOOL] Multiplying {a} * {b}")
    return a * b

@tool(name="divide", description="Divide two numbers", namespace="builtin")
def divide(a: float, b: float) -> float:
    """Divide the first number by the second."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    print(f"[TOOL] Dividing {a} / {b}")
    return a / b

@tool(name="compare_numbers", description="Compare two numbers", namespace="builtin")
def compare_numbers(a: float, b: float) -> str:
    """Compare two numbers and return the larger one."""
    print(f"[TOOL] Comparing {a} and {b}")
    if type(a) != float:
        a = float(a)
    if type(b) != float:
        b = float(b)
    return f"The larger number is {float(max(a, b))}"
```

**Context:** This moves the existing math tools from the examples to the built-in system, maintaining the same functionality while adding proper namespace separation.

### 2.2 Text Tools Category

**File:** `agentmanager/builtin/tools/categories/text.py`

```python
"""Text tools category - text processing and manipulation."""

from ...core.tools import tool
from ..base import BuiltinTool
import re

class TextTools(BuiltinTool):
    """Text tools category."""
    
    def get_tools(self):
        return [
            {'name': 'process_text', 'func': process_text, 'description': 'Process text with operations'},
            {'name': 'greet', 'func': greet, 'description': 'Generate personalized greeting'},
            {'name': 'text_length', 'func': text_length, 'description': 'Get character count of text'},
            {'name': 'extract_numbers', 'func': extract_numbers, 'description': 'Extract numbers from text'},
        ]

@tool(name="process_text", description="Process text with operations", namespace="builtin")
def process_text(text: str, operation: str = "uppercase") -> str:
    """Process text with various operations."""
    print(f"[TOOL] Processing text with operation: {operation}")
    
    operations = {
        "uppercase": text.upper(),
        "lowercase": text.lower(),
        "titlecase": text.title(),
        "reverse": text[::-1],
        "wordcount": str(len(text.split())),
        "charcount": str(len(text))
    }
    
    if operation not in operations:
        raise ValueError(f"Unknown operation: {operation}. Available: {list(operations.keys())}")
    
    return operations[operation]

@tool(name="greet", description="Generate personalized greeting", namespace="builtin")
def greet(name: str, greeting: str = "Hello") -> str:
    """Generate a personalized greeting."""
    print(f"[TOOL] Greeting {name} with '{greeting}'")
    return f"{greeting}, {name}!"

@tool(name="text_length", description="Get character count of text", namespace="builtin")
def text_length(text: str) -> int:
    """Get character count of text."""
    return len(text)

@tool(name="extract_numbers", description="Extract numbers from text", namespace="builtin")
def extract_numbers(text: str) -> list:
    """Extract all numbers from text."""
    numbers = re.findall(r'-?\d+\.?\d*', text)
    return [float(num) if '.' in num else int(num) for num in numbers]
```

**Context:** This provides essential text processing capabilities that agents commonly need, with proper error handling and clear operation definitions.

### 2.3 Web Tools Category

**File:** `agentmanager/builtin/tools/categories/web.py`

```python
"""Web tools category - web-related operations and data fetching."""

from ...core.tools import tool
from ..base import BuiltinTool

class WebTools(BuiltinTool):
    """Web tools category - web-related operations and data fetching."""
    
    def get_tools(self):
        return [
            {'name': 'web_search', 'func': web_search, 'description': 'Search the web'},
            {'name': 'fetch_url', 'func': fetch_url, 'description': 'Fetch content from URL'},
            {'name': 'validate_url', 'func': validate_url, 'description': 'Validate URL format'},
        ]

@tool(name="web_search", description="Search the web", namespace="builtin")
def web_search(query: str) -> dict:
    """Search the web for a query using DuckDuckGo and return summarized results.
    
    Args:
        query (str): The search query.
    
    Returns:
        dict: A dictionary with 'results' containing search results.
    """
    print(f"[TOOL] Performing web search for: '{query}' (max_results=5)")
    
    try:
        from ddgs import DDGS
        import requests
        from bs4 import BeautifulSoup
        import asyncio
        import aiohttp
        from concurrent.futures import ThreadPoolExecutor
    except ImportError:
        raise ImportError("Required packages 'ddgs', 'requests', 'beautifulsoup4', and 'aiohttp' are not installed.")

    # Move implementation from examples/tools/mcp_tool_server.py
    # ... existing web search implementation ...
    
    return {"results": results}

@tool(name="fetch_url", description="Fetch content from URL", namespace="builtin")
def fetch_url(url: str) -> str:
    """Fetch content from a URL."""
    try:
        import requests
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text
    except ImportError:
        raise ImportError("Required package 'requests' not installed")
    except Exception as e:
        raise ValueError(f"Failed to fetch URL: {e}")

@tool(name="validate_url", description="Validate URL format", namespace="builtin")
def validate_url(url: str) -> bool:
    """Validate if URL is properly formatted."""
    import re
    pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return pattern.match(url) is not None
```

**Context:** This is the most critical category as web search is essential for agent functionality. The implementation is moved from examples and enhanced with proper error handling.

## Phase 3: Tool Loader and Registry (Week 3)

### 3.1 Built-in Tool Loader

**File:** `agentmanager/builtin/tools/loader.py`

```python
"""Built-in tool loader with hybrid loading strategy."""

import importlib
import logging
from typing import List, Dict, Any
from .base import BuiltinTool
from ...core.tools import get_tool_registry

logger = logging.getLogger(__name__)

class BuiltinToolLoader:
    """Loader for built-in tools with hybrid loading strategy."""
    
    def __init__(self):
        self.loaded_categories = set()
        self.tool_registry = get_tool_registry()
        self.category_modules = {}
    
    def load_category(self, category: str) -> bool:
        """Load all tools from a specific category.
        
        Args:
            category: Category name to load
            
        Returns:
            bool: True if category loaded successfully
        """
        if category in self.loaded_categories:
            return True
        
        try:
            # Import category module
            module_name = f'.categories.{category}'
            category_module = importlib.import_module(module_name, __package__)
            self.category_modules[category] = category_module
            
            # Get tools from category
            if hasattr(category_module, 'get_tools'):
                tools = category_module.get_tools()
            else:
                # Fallback: look for tool functions directly
                tools = self._extract_tools_from_module(category_module)
            
            # Register each tool
            for tool_info in tools:
                self.tool_registry.register_tool(
                    name=tool_info['name'],
                    func=tool_info['func'],
                    description=tool_info['description'],
                    namespace='builtin'
                )
            
            self.loaded_categories.add(category)
            logger.info(f"Loaded built-in tools category: {category}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load category '{category}': {e}")
            return False
    
    def load_tool(self, tool_name: str) -> bool:
        """Load a specific tool if it's a built-in tool.
        
        Args:
            tool_name: Name of tool to load
            
        Returns:
            bool: True if tool was loaded
        """
        # Check which category contains this tool
        for category in ['math', 'text', 'web', 'data', 'system']:
            if self._tool_exists_in_category(tool_name, category):
                return self.load_category(category)
        return False
    
    def load_all(self) -> None:
        """Load all auto-load categories."""
        from ..config import BuiltinToolsConfig
        config = BuiltinToolsConfig()
        
        for category in config.auto_load_categories:
            self.load_category(category)
    
    def _tool_exists_in_category(self, tool_name: str, category: str) -> bool:
        """Check if a tool exists in a specific category."""
        try:
            if category not in self.category_modules:
                module_name = f'.categories.{category}'
                module = importlib.import_module(module_name, __package__)
                self.category_modules[category] = module
            
            if hasattr(self.category_modules[category], 'get_tools'):
                tools = self.category_modules[category].get_tools()
                return any(tool['name'] == tool_name for tool in tools)
            
            return False
        except Exception:
            return False
    
    def _extract_tools_from_module(self, module) -> List[Dict[str, Any]]:
        """Extract tools from module by looking for @tool decorated functions."""
        tools = []
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if callable(attr) and hasattr(attr, '__wrapped__'):
                # This is a @tool decorated function
                tools.append({
                    'name': getattr(attr, '_tool_name', attr_name),
                    'func': attr,
                    'description': getattr(attr, '_tool_description', '')
                })
        return tools
```

**Context:** This loader implements the hybrid loading strategy, automatically loading critical tools while providing lazy loading for heavy tools. It integrates with the existing tool registry system.

### 3.2 Built-in Tool Registry

**File:** `agentmanager/builtin/tools/registry.py`

```python
"""Built-in tool registry and discovery."""

from typing import List, Dict, Any
from .loader import BuiltinToolLoader

class BuiltinToolRegistry:
    """Registry for built-in tools."""
    
    def __init__(self):
        self.loader = BuiltinToolLoader()
        self._available_tools_cache = None
    
    def list_builtin_tools(self) -> Dict[str, List[str]]:
        """List all available built-in tools by category.
        
        Returns:
            Dictionary mapping category names to lists of tool names
        """
        categories = {}
        
        for category in ['math', 'text', 'web', 'data', 'system']:
            try:
                if category in self.loader.loaded_categories:
                    # Category already loaded
                    module = self.loader.category_modules[category]
                    if hasattr(module, 'get_tools'):
                        tools = module.get_tools()
                        categories[category] = [tool['name'] for tool in tools]
                else:
                    # Check if category can be loaded
                    if self.loader._tool_exists_in_category('dummy', category):
                        # Load category to get tool list
                        if self.loader.load_category(category):
                            module = self.loader.category_modules[category]
                            if hasattr(module, 'get_tools'):
                                tools = module.get_tools()
                                categories[category] = [tool['name'] for tool in tools]
            except Exception:
                categories[category] = []
        
        return categories
    
    def get_builtin_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Get information about a specific built-in tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Dictionary with tool information
        """
        for category in ['math', 'text', 'web', 'data', 'system']:
            if self.loader._tool_exists_in_category(tool_name, category):
                # Load category if not already loaded
                if category not in self.loader.loaded_categories:
                    self.loader.load_category(category)
                
                # Get tool info
                module = self.loader.category_modules[category]
                if hasattr(module, 'get_tools'):
                    tools = module.get_tools()
                    for tool in tools:
                        if tool['name'] == tool_name:
                            return {
                                'name': tool['name'],
                                'description': tool['description'],
                                'category': category,
                                'namespace': 'builtin'
                            }
        
        return None
    
    def load_tool_if_builtin(self, tool_name: str) -> bool:
        """Load a tool if it's a built-in tool.
        
        Args:
            tool_name: Name of tool to load
            
        Returns:
            bool: True if tool was loaded
        """
        return self.loader.load_tool(tool_name)
```

**Context:** This registry provides discovery and management capabilities for built-in tools, working alongside the existing tool registry system.

## Phase 4: Integration with Existing System (Week 4)

### 4.1 Update Main Package

**File:** `agentmanager/__init__.py`

```python
# Add built-in tools integration
from .builtin.tools import load_all_builtin_tools

# Auto-load critical tools (math, text, web)
load_all_builtin_tools()

__all__ = [
    # ... existing exports ...
    "load_all_builtin_tools",
]
```

**Context:** This ensures built-in tools are automatically loaded when the package is imported, making them immediately available to users.

### 4.2 Update load_agent Function

**File:** `agentmanager/sdk/load_agent.py`

```python
def load_agent(
    base_agent: str,
    tools: Optional[List[str]] = None,
    **kwargs
):
    """Enhanced load_agent with smart built-in tool loading."""
    if tools is None:
        tools = []
    
    # Get tool registry
    tool_registry = get_tool_registry()
    
    # Smart tool resolution
    resolved_tools = []
    for tool_name in tools:
        if tool_registry.is_tool_registered(tool_name):
            # Tool already registered (custom or MCP)
            resolved_tools.append(tool_name)
        else:
            # Try to load as built-in tool
            from ..builtin.tools import load_tool_if_builtin
            if load_tool_if_builtin(tool_name):
                resolved_tools.append(tool_name)
            else:
                # Tool not found anywhere
                raise ValueError(f"Tool '{tool_name}' not found in custom, MCP, or built-in tools")
    
    # Rest of the function remains the same...
    # ... existing code ...
```

**Context:** This implements the smart tool resolution that automatically loads built-in tools when needed, maintaining the same interface while adding new functionality.

### 4.3 Update Tool Registry Discovery

**File:** `agentmanager/core/tools/registry.py`

```python
def get_available_tools(self) -> List[str]:
    """Get list of available tool names."""
    # First check local registry
    local_tools = list(self.registered_tools.keys())
    
    # Try to discover from MCP server and combine with local tools
    try:
        import asyncio
        from mcp.client.sse import sse_client
        from mcp import ClientSession
        
        async def discover_tools():
            try:
                async with sse_client(url="http://localhost:8000/sse") as streams:
                    async with ClientSession(*streams) as session:
                        await session.initialize()
                        tools = await session.list_tools()
                        return [tool.name for tool in tools.tools]
            except Exception as e:
                print(f"⚠️  MCP discovery failed: {e}")
                return []
        
        # Check if we're already in an event loop
        try:
            loop = asyncio.get_running_loop()
            # We're in an event loop, create a task instead
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, discover_tools())
                mcp_tools = future.result(timeout=5)  # 5 second timeout
        except RuntimeError:
            # No event loop running, safe to use asyncio.run()
            mcp_tools = asyncio.run(discover_tools())
        
        # Add built-in tools discovery
        builtin_tools = self._discover_builtin_tools()
        
        # Combine all sources
        all_tools = list(set(local_tools + mcp_tools + builtin_tools))
        return all_tools
    except Exception as e:
        print(f"⚠️  Could not discover tools from MCP server: {e}")
        # Fallback to local tools + built-in tools
        builtin_tools = self._discover_builtin_tools()
        return list(set(local_tools + builtin_tools))

def _discover_builtin_tools(self) -> List[str]:
    """Discover available built-in tools."""
    try:
        from ..builtin.tools import list_builtin_tools
        categories = list_builtin_tools()
        all_tools = []
        for tool_list in categories.values():
            all_tools.extend(tool_list)
        return all_tools
    except ImportError:
        return []
```

**Context:** This integrates built-in tool discovery with the existing tool discovery system, ensuring all tool types are visible through the same interface.

## Phase 5: Testing and Validation (Week 5)

### 5.1 Unit Tests

**File:** `agentmanager/builtin/tools/tests/test_math_tools.py`

```python
"""Unit tests for math tools."""

import pytest
from ..categories.math import add, subtract, multiply, divide, compare_numbers

def test_add():
    """Test add function."""
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(0, 0) == 0

def test_subtract():
    """Test subtract function."""
    assert subtract(5, 3) == 2
    assert subtract(0, 5) == -5
    assert subtract(10, 10) == 0

def test_multiply():
    """Test multiply function."""
    assert multiply(3, 4) == 12
    assert multiply(0, 5) == 0
    assert multiply(-2, 3) == -6

def test_divide():
    """Test divide function."""
    assert divide(10, 2) == 5.0
    assert divide(15, 3) == 5.0
    assert divide(7, 2) == 3.5
    
    # Test division by zero
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(5, 0)

def test_compare_numbers():
    """Test compare_numbers function."""
    result = compare_numbers(9.8, 9.11)
    assert "9.8" in result
    
    result = compare_numbers(5, 10)
    assert "10" in result
```

**Context:** These tests ensure each tool works correctly and handles edge cases properly, maintaining the same behavior as the original examples.

### 5.2 Integration Tests

**File:** `agentmanager/builtin/tools/tests/test_integration.py`

```python
"""Integration tests for built-in tools."""

import agentmanager as amg

def test_builtin_tools_in_agent():
    """Test that built-in tools work with load_agent."""
    agent = amg.load_agent('agentplug/analysis-agent', tools=['add', 'multiply'])
    
    # Test tool execution
    result = agent.execute_tool('add', 5, 3)
    assert result == 8
    
    result = agent.execute_tool('multiply', 4, 6)
    assert result == 24

def test_web_search_tool():
    """Test web search tool (critical tool)."""
    agent = amg.load_agent('agentplug/analysis-agent', tools=['web_search'])
    
    # Test web search (may require internet connection)
    try:
        result = agent.execute_tool('web_search', 'weather')
        assert isinstance(result, dict)
        assert 'results' in result
    except ImportError:
        # Skip if dependencies not available
        pytest.skip("Web search dependencies not available")

def test_mixed_tool_types():
    """Test mixing custom, MCP, and built-in tools."""
    # Create a custom tool
    from agentmanager.core.tools import tool
    
    @tool(name="custom_test_tool", description="Custom test tool")
    def custom_test_tool():
        return "custom"
    
    # This should work seamlessly
    agent = amg.load_agent('agentplug/analysis-agent', tools=[
        'add',              # Built-in
        'custom_test_tool', # Custom
        # 'mcp_tool'        # MCP (if available)
    ])
    
    # Test built-in tool
    result = agent.execute_tool('add', 2, 3)
    assert result == 5
    
    # Test custom tool
    result = agent.execute_tool('custom_test_tool')
    assert result == "custom"

def test_backward_compatibility():
    """Test that existing code still works."""
    # Test existing examples
    from examples.tools.agent_loading_with_tools import example_1_basic_agent
    result = example_1_basic_agent()
    assert result is not None
```

**Context:** These tests verify that built-in tools integrate properly with the existing system and that backward compatibility is maintained.

### 5.3 Performance Tests

**File:** `agentmanager/builtin/tools/tests/test_performance.py`

```python
"""Performance tests for built-in tools."""

import time
import agentmanager as amg

def test_startup_time():
    """Test that built-in tools don't significantly impact startup time."""
    start_time = time.time()
    
    # Import agentmanager (this loads built-in tools)
    import agentmanager as amg
    
    end_time = time.time()
    startup_time = end_time - start_time
    
    # Should be less than 100ms
    assert startup_time < 0.1, f"Startup time too slow: {startup_time:.3f}s"

def test_tool_execution_performance():
    """Test that built-in tools execute quickly."""
    agent = amg.load_agent('agentplug/analysis-agent', tools=['add', 'multiply'])
    
    # Test execution time
    start_time = time.time()
    for _ in range(100):
        agent.execute_tool('add', 1, 2)
    end_time = time.time()
    
    avg_time = (end_time - start_time) / 100
    # Should be very fast (less than 1ms per call)
    assert avg_time < 0.001, f"Tool execution too slow: {avg_time:.6f}s per call"

def test_memory_usage():
    """Test that built-in tools don't use excessive memory."""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    memory_before = process.memory_info().rss
    
    # Load built-in tools
    agent = amg.load_agent('agentplug/analysis-agent', tools=['add', 'web_search'])
    
    memory_after = process.memory_info().rss
    memory_increase = memory_after - memory_before
    
    # Should be less than 10MB
    assert memory_increase < 10 * 1024 * 1024, f"Memory usage too high: {memory_increase / 1024 / 1024:.1f}MB"
```

**Context:** These tests ensure that built-in tools don't negatively impact system performance, maintaining the efficiency of the existing system.

## Success Criteria

### Functional Requirements
- [ ] 100% backward compatibility with existing code
- [ ] Built-in tools available via `load_agent()`
- [ ] Auto-loading works for critical tools (math, text, web)
- [ ] Lazy loading works for heavy tools (data, system)
- [ ] Tool discovery includes built-in tools
- [ ] Web search is always available (critical requirement)

### Performance Requirements
- [ ] Startup time impact < 100ms
- [ ] Tool execution performance same as custom tools
- [ ] Memory usage increase < 10MB

### Quality Requirements
- [ ] 90%+ test coverage
- [ ] All tools have proper error handling
- [ ] Documentation is complete and clear
- [ ] Code follows project style guidelines

## Risk Mitigation

### Technical Risks
- **Breaking Changes**: Extensive backward compatibility testing
- **Performance Impact**: Benchmarking and optimization
- **Dependency Issues**: Graceful handling of missing dependencies

### Project Risks
- **Scope Creep**: Stick to Phase 2.5 requirements only
- **Timeline Delays**: Prioritize core functionality first
- **Quality Issues**: Continuous testing and code review

## Rollback Plan

If issues arise during implementation:

1. **Phase 1-2**: Revert to examples-based tools
2. **Phase 3**: Disable built-in tools, fall back to custom/MCP only
3. **Phase 4-5**: Remove built-in tools from main package

## Future Enhancements (Post-Phase 2.5)

- Additional tool categories (AI, visualization)
- Tool marketplace integration
- Third-party tool plugins
- Advanced tool configuration
- Tool performance monitoring

---

*This implementation plan provides a clear, step-by-step approach to building the built-in tools system while maintaining the existing system's reliability and performance.*
