# Core/Tools Module - Phase 2.5

**Purpose**: Tool registry, decorator, metadata management, and validation with FastMCP integration

## 🎯 **Module Overview**

The tools module provides a clean, simple interface for users to define custom tools that can be injected into agents. It wraps FastMCP to provide automatic tool registration and management.

## 🔧 **Key Features**

- **`@tool` Decorator**: Simple decorator for tool definition
- **Automatic Registration**: Tools are automatically registered with FastMCP
- **Global Registry**: Centralized tool registry with per-agent access control
- **Tool Validation**: Tool signature validation at registration time
- **Metadata Management**: Tool metadata for agent context injection

## 📋 **User Experience**

```python
from agenthub.core.tools import tool

@tool(name="data_analyzer", description="Analyze data")
def my_data_analyzer(data: str) -> dict:
    return {"insights": f"analyzed: {data}"}

@tool(name="sentiment_analysis", description="Analyze sentiment")
def my_sentiment_analyzer(data: str) -> dict:
    return {"insights": f"analyzed: {data}"}
```

## 🔄 **Implementation Flow**

1. **Tool Definition**: User defines tool with `@tool` decorator
2. **Automatic Registration**: Tool is automatically registered with FastMCP
3. **Global Registry**: Tool is added to global registry
4. **Validation**: Tool signature is validated
5. **Metadata Creation**: Tool metadata is created for agent context

## 📁 **Documentation Files**

- `01_interface_design.md` - `@tool` decorator, tool registry API, FastMCP integration
- `02_implementation_details.md` - Tool registry with FastMCP, validation, metadata
- `03_testing_strategy.md` - Unit tests for tool registration, validation, metadata
- `04_success_criteria.md` - Tool registration works, validation works, metadata complete
