# AgentHub Tools

## Overview

AgentHub provides a comprehensive tools system that enables agents to interact with external services, manipulate data, and perform various operations. The tools system is built on a robust registry architecture with support for both built-in and custom tools.

## Tool Categories

### Built-in Tools
- **[Web Tools](BUILT_IN_TOOLS.md#web-tools)** - Web search, HTTP requests, API calls
- **[Data Tools](BUILT_IN_TOOLS.md#data-tools)** - File operations, data processing, parsing
- **[AI Tools](BUILT_IN_TOOLS.md#ai-tools)** - RAG queries, vector search, text analysis
- **[System Tools](BUILT_IN_TOOLS.md#system-tools)** - Shell commands, system monitoring, logs

### Custom Tools
- **[Tool Development Guide](TOOL_DEVELOPMENT_GUIDE.md)** - How to create custom tools
- **[Tool Integration](TOOL_DEVELOPMENT_GUIDE.md#integration)** - Integrating tools with agents
- **[Tool Examples](examples/)** - Example implementations

## Quick Start

### Using Built-in Tools
```python
from agenthub import load_agent

# Load agent with built-in tools
agent = load_agent("coding-agent")
result = agent.web_search("Python best practices")
```

### Creating Custom Tools
```python
from agenthub.core.tools import tool

@tool(name="my_custom_tool", version="1.0.0")
def my_custom_tool(input_text: str) -> str:
    """Process input text and return result."""
    return f"Processed: {input_text}"

# Tool is automatically registered and available to agents
```

## Architecture

### Tool Registry
- **Single Registry**: All tools (built-in and custom) in one registry
- **Version Management**: Semantic versioning with compatibility tracking
- **Metadata**: Rich tool metadata including parameters, examples, and descriptions
- **Access Control**: Tool-level permissions and security controls

### Tool Execution
- **MCP Integration**: Tools work seamlessly with Model Context Protocol
- **Async Support**: Non-blocking tool execution
- **Error Handling**: Comprehensive error handling and recovery
- **Monitoring**: Built-in performance monitoring and logging

## Documentation

- **[Built-in Tools Catalog](BUILT_IN_TOOLS.md)** - Complete list of available built-in tools
- **[Tool Development Guide](TOOL_DEVELOPMENT_GUIDE.md)** - Creating and contributing tools
- **[Tool Benchmarking](TOOL_BENCHMARKING.md)** - Testing and performance optimization
- **[Examples](examples/)** - Code examples and tutorials

## Contributing

We welcome contributions to the AgentHub tools system! See our [Tool Development Guide](TOOL_DEVELOPMENT_GUIDE.md) for details on how to contribute new tools or improve existing ones.
