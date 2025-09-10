# AgentHub Examples

This directory contains comprehensive examples demonstrating AgentHub's capabilities, organized by complexity and use case.

## 📁 Directory Structure

### 🚀 Getting Started (`getting_started/`)
Essential examples for new users to understand basic AgentHub functionality.

- **`quick_start.py`** - Complete quick start guide with all core features
- **`agent_declaration.py`** - How to declare and configure agents
- **`online_agent.py`** - Working with online/remote agents
- **`offline_agents.py`** - Working with local/offline agents

### 🔧 Tools (`tools/`)
Examples focused on tool integration and MCP (Model Context Protocol).

- **`agent_loading_with_tools.py`** - Load agents with tool assignments
- **`mcp_tool_server.py`** - MCP tool server implementation
- **`mcp_tool_client.py`** - MCP client usage examples

### 🧪 Testing (`testing/`)
Examples for testing, debugging, and validation.

- **`debug_tool_execution.py`** - Debug tool execution with detailed logging
- **`error_handling_demo.py`** - Error handling and recovery patterns
- **`agent_discovery_and_validation.py`** - Agent discovery and validation
- **`tool_access_control_demo.py`** - Tool access control and permissions
- **`tool_discovery_service.py`** - Tool discovery and metadata

### 🚀 Advanced (`advanced/`)
Complex examples showcasing advanced AgentHub features.

- **`business_automation_showcase.py`** - Business process automation
- **`dynamic_agent_orchestration.py`** - Dynamic agent orchestration
- **`code_generation_workflow.py`** - Code generation workflows
- **`content_analysis_suite.py`** - Content analysis and processing

### 📦 Deprecated (`deprecated/`)
Legacy examples that are no longer recommended but kept for reference.

- **`auto_installation_demo.py`** - Legacy auto-installation (use quick_start.py)
- **`clone_agent.py`** - Legacy agent cloning (use agent_declaration.py)
- **`core_unified_interface.py`** - Legacy interface (use modern examples)

## 🎯 Quick Start

1. **Start with**: `getting_started/quick_start.py`
2. **Learn tools**: `tools/agent_loading_with_tools.py`
3. **Test features**: `testing/debug_tool_execution.py`
4. **Advanced usage**: `advanced/business_automation_showcase.py`

## 📋 Prerequisites

- Python 3.8+
- AgentHub installed (`pip install -e .`)
- MCP tool server running (for tool examples)

## 🔧 Running Examples

```bash
# Basic example
python examples/getting_started/quick_start.py

# With tools (requires MCP server)
python examples/tools/mcp_tool_server.py &
python examples/tools/agent_loading_with_tools.py

# Testing and debugging
python examples/testing/debug_tool_execution.py
```

## 📚 Documentation

- [User Guide](../docs/USER_GUIDE.md)
- [API Reference](../docs/API_REFERENCE.md)
- [Tool Development Guide](../docs/TOOL_DEVELOPMENT.md)
