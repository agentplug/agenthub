# Tool Development Guide

## Overview

This guide explains how to create, test, and contribute new tools to AgentHub. Tools are the building blocks that enable agents to interact with external systems, manipulate data, and perform various operations.

## Tool Architecture

### Core Components

1. **Tool Decorator** (`@tool`) - Registers functions as tools
2. **Tool Registry** - Manages all registered tools
3. **Tool Metadata** - Stores tool information and parameters
4. **MCP Integration** - Enables tools to work with Model Context Protocol

### Tool Structure

```python
from agenthub.core.tools import tool

@tool(
    name="my_tool",
    description="Description of what the tool does",
    version="1.0.0"  # Optional, defaults to "1.0.0"
)
def my_tool(param1: str, param2: int = 10) -> dict:
    """
    Detailed tool documentation.
    
    Args:
        param1 (str): Description of parameter 1
        param2 (int): Description of parameter 2 (default: 10)
    
    Returns:
        dict: Description of return value
    """
    # Tool implementation
    return {"result": "success"}
```

## Creating New Tools

### Step 1: Choose Tool Category

Decide which category your tool belongs to:

- **Web Tools** (`agenthub/core/tools/builtin/web/`) - HTTP requests, web scraping, APIs
- **Data Tools** (`agenthub/core/tools/builtin/data/`) - File operations, data processing
- **AI Tools** (`agenthub/core/tools/builtin/ai/`) - RAG, vector search, text analysis
- **System Tools** (`agenthub/core/tools/builtin/system/`) - Shell commands, system info

### Step 2: Implement Tool Function

Create a new Python file in the appropriate category directory:

```python
# agenthub/core/tools/builtin/web/http.py
from typing import Dict, Any
from ...decorator import tool

@tool(
    name="http_request",
    description="Make HTTP requests to external APIs",
    version="1.0.0"
)
def http_request(
    method: str,
    url: str,
    headers: Dict[str, str] = None,
    data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Make HTTP requests to external APIs and web services.
    
    Args:
        method (str): HTTP method (GET, POST, PUT, DELETE)
        url (str): Target URL
        headers (dict, optional): Request headers
        data (dict, optional): Request body data
    
    Returns:
        dict: Response data with status, headers, and body
    """
    import requests
    
    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers or {},
            json=data
        )
        
        return {
            "success": True,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
```

### Step 3: Register Tool

Add your tool to the loader:

```python
# agenthub/core/tools/builtin/loader.py
def load_all_builtin_tools(registry: "ToolRegistry") -> None:
    # ... existing tools ...
    
    # Add your new tool
    from .web.http import http_request
    registry.register_tool(http_request)
```

### Step 4: Update Category Init

Update the category's `__init__.py` file:

```python
# agenthub/core/tools/builtin/web/__init__.py
from .search import web_search
from .http import http_request  # Add your new tool

__all__ = ["web_search", "http_request"]
```

## Tool Best Practices

### 1. Error Handling

Always handle errors gracefully:

```python
@tool(name="my_tool")
def my_tool(param: str) -> dict:
    try:
        # Tool logic
        result = perform_operation(param)
        return {"success": True, "result": result}
    except Exception as e:
        return {
            "success": False,
            "error": f"Operation failed: {str(e)}"
        }
```

### 2. Input Validation

Validate inputs before processing:

```python
@tool(name="my_tool")
def my_tool(url: str, timeout: int = 30) -> dict:
    if not url or not isinstance(url, str):
        return {"success": False, "error": "URL must be a non-empty string"}
    
    if timeout <= 0:
        return {"success": False, "error": "Timeout must be positive"}
    
    # Continue with tool logic
```

### 3. Security Considerations

- **Sanitize inputs** to prevent injection attacks
- **Validate file paths** to prevent directory traversal
- **Limit resource usage** with timeouts and size limits
- **Check permissions** before file operations

### 4. Performance Optimization

- **Use async operations** for I/O-bound tasks
- **Implement caching** for expensive operations
- **Add rate limiting** for API calls
- **Optimize memory usage** for large data processing

### 5. Documentation

Provide comprehensive documentation:

```python
@tool(name="my_tool")
def my_tool(param1: str, param2: int = 10) -> dict:
    """
    Brief description of what the tool does.
    
    Longer description explaining the tool's purpose,
    use cases, and any important considerations.
    
    Args:
        param1 (str): Description of parameter 1
        param2 (int): Description of parameter 2 (default: 10)
    
    Returns:
        dict: Description of return value structure
    
    Raises:
        ValueError: When parameter validation fails
    
    Example:
        >>> result = my_tool("example", 20)
        >>> print(result["status"])
        "success"
    """
```

## Testing Tools

### Unit Tests

Create unit tests for your tools:

```python
# tests/test_my_tool.py
import pytest
from agenthub.core.tools.builtin.web.http import http_request

def test_http_request_success():
    result = http_request("GET", "https://httpbin.org/get")
    assert result["success"] is True
    assert result["status_code"] == 200

def test_http_request_invalid_url():
    result = http_request("GET", "invalid-url")
    assert result["success"] is False
    assert "error" in result
```

### Integration Tests

Test tools with the full AgentHub system:

```python
# tests/integration/test_tool_integration.py
def test_tool_with_agent():
    from agenthub import load_agent
    
    agent = load_agent("test-agent")
    result = agent.http_request("GET", "https://httpbin.org/get")
    assert result["success"] is True
```

## Tool Integration

### Using Tools in Agents

Agents can access tools through the registry:

```python
from agenthub import load_agent

# Load agent with built-in tools
agent = load_agent("my-agent")

# Use tools
result = agent.web_search("Python programming")
file_content = agent.file_operations("read", "/path/to/file.txt")
```

### Custom Tool Registration

Register custom tools at runtime:

```python
from agenthub.core.tools import tool, get_tool_registry

@tool(name="custom_tool")
def custom_tool(param: str) -> str:
    return f"Processed: {param}"

# Tool is automatically registered when decorated
```

## Contributing Tools

### Pull Request Process

1. **Fork the repository**
2. **Create a feature branch**
3. **Implement your tool** following best practices
4. **Add comprehensive tests**
5. **Update documentation**
6. **Submit pull request**

### Code Review Checklist

- [ ] Tool follows naming conventions
- [ ] Comprehensive error handling
- [ ] Input validation implemented
- [ ] Security considerations addressed
- [ ] Performance optimized
- [ ] Documentation complete
- [ ] Tests pass
- [ ] No breaking changes

### Tool Requirements

- **Functionality**: Tool must work as documented
- **Reliability**: Handle errors gracefully
- **Security**: Safe for production use
- **Performance**: Efficient resource usage
- **Documentation**: Clear and comprehensive
- **Testing**: Unit and integration tests

## Advanced Topics

### Tool Versioning

Use semantic versioning for tool updates:

```python
@tool(name="my_tool", version="2.0.0")  # Breaking change
def my_tool_v2(new_param: str) -> dict:
    # New implementation
    pass

@tool(name="my_tool", version="1.1.0")  # Backward compatible
def my_tool_v1_1(param: str, optional: str = None) -> dict:
    # Enhanced implementation
    pass
```

### Tool Dependencies

Handle external dependencies gracefully:

```python
@tool(name="my_tool")
def my_tool(param: str) -> dict:
    try:
        import external_library
    except ImportError:
        return {
            "success": False,
            "error": "Required library 'external_library' not installed"
        }
    
    # Use external_library
```

### Tool Configuration

Use environment variables for configuration:

```python
import os

@tool(name="my_tool")
def my_tool(param: str) -> dict:
    api_key = os.getenv("MY_API_KEY")
    if not api_key:
        return {"success": False, "error": "API key not configured"}
    
    # Use api_key
```

## Troubleshooting

### Common Issues

1. **Tool not found**: Ensure tool is registered in loader
2. **Import errors**: Check dependencies are installed
3. **Permission errors**: Verify file system permissions
4. **Timeout errors**: Adjust timeout values
5. **Memory issues**: Optimize data processing

### Debug Tips

- Use logging to trace tool execution
- Test tools in isolation before integration
- Check tool metadata for parameter requirements
- Verify return value format matches documentation

## Resources

- [Built-in Tools Catalog](BUILT_IN_TOOLS.md)
- [Tool Benchmarking Guide](TOOL_BENCHMARKING.md)
- [AgentHub Documentation](../README.md)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
