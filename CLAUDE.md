# AgentHub - Claude Code Assistant Guide

This file provides context and guidance for Claude Code when working with the AgentHub codebase.

## 🎯 Quick Context

**AgentHub** is an "App Store for AI Agents" - a Python framework that enables developers to discover, install, and use AI agents with one line of code. Think `npm install` but for AI agents.

**Current Status**: Production-ready. Core features complete through Phase 3.4 (Real-time Communication).

## 🚀 Development Workflow

### Before You Start
1. **Understand the task** - Read requirements carefully
2. **Explore first** - Use `codebase_search` and `grep` to understand existing patterns
3. **Plan complex tasks** - Use `todo_write` for multi-step work (3+ steps)
4. **Follow existing patterns** - Don't reinvent; reuse what's working

### Core Principles
- **KISS**: Keep it simple. Avoid over-engineering
- **YAGNI**: Build only what's needed now, not for hypothetical futures
- **Incremental validation**: Write → Test → Fix → Continue (don't write everything then test)
- **Prefer existing files**: Modify over create. Delete temporary experiments immediately

## 📁 Project Structure

```
agenthub/
├── core/              # Core agent system
│   ├── agents/        # Agent loading, execution, lifecycle
│   ├── tools/         # Tool registry, MCP integration
│   ├── communication/ # WebSocket, inter-agent messaging
│   ├── llm/          # LLM service abstraction
│   └── knowledge/     # RAG and knowledge base
├── runtime/           # Process management, isolated execution
├── sdk/              # Public API (load_agent, solve)
├── github/           # GitHub-based agent registry
├── builtin/tools/    # Built-in tools (RAG, web_search)
├── cli/              # Command-line interface
└── storage/          # Local caching and persistence

examples/             # Usage examples and demos
tests/               # Comprehensive test suites
```

## 🔑 Key Architecture Patterns

### 1. Agent Loading & Execution
```python
import agenthub as ah

# Load from GitHub
agent = ah.load_agent("namespace/agent-name")

# Universal solve method
result = agent.solve("Natural language goal")
```

**Key Files**:
- `agenthub/sdk/load_agent.py` - Main entry point
- `agenthub/core/agents/base.py` - Base agent interface
- `agenthub/runtime/agent_runtime.py` - Isolated execution

### 2. MCP Tool Integration
Tools use the Model Context Protocol (MCP) for standardized execution.

**Key Files**:
- `agenthub/core/tools/registry.py` - Tool registration
- `agenthub/core/tools/base.py` - Tool base classes
- `agenthub/core/mcp/` - MCP server implementation

**Pattern**: Create tools with `@tool` decorator, run with `run_resources()`
```python
from agenthub.core.tools import tool, run_resources

@tool(name="my_tool", description="...")
def my_tool(param: str) -> dict:
    return {"result": param}

run_resources()  # Starts MCP server
```

### 3. Process Isolation with UV
Each agent runs in an isolated subprocess using UV (10x faster than pip).

**Key Files**:
- `agenthub/runtime/environment_manager.py`
- `agenthub/runtime/process_manager/`

### 4. Real-time Communication
WebSocket-based inter-agent communication and real-time updates.

**Key Files**:
- `agenthub/core/communication/server.py`
- `agenthub/core/communication/router.py`

## 🛠 Common Development Tasks

### Adding New Built-in Tools
1. Create tool in `agenthub/builtin/tools/<tool_name>/`
2. Use `@tool` decorator for functions
3. Add to `__init__.py` exports
4. Create example in `examples/builtin_tools/`
5. Write tests in `tests/phase2.5_tool_injection/`

### Creating Examples
- **Simple examples**: In `examples/getting_started/`
- **Tool examples**: In `examples/builtin_tools/`
- **Client examples**: In `examples/clients/`
- Keep examples minimal, focused on one concept
- Include clear comments and docstrings

### Writing Tests
- Follow phase-based organization: `tests/phase{X}_*/`
- Use pytest fixtures from `conftest.py`
- Test both success and error cases
- Run with: `pytest tests/phase2.5_tool_injection/ -v`

## ⚙️ Technical Details

### Dependencies
- **UV**: Fast package manager (core requirement)
- **Click**: CLI framework
- **Rich**: Terminal UI
- **Pydantic**: Data validation
- **MCP**: Model Context Protocol
- **FastAPI**: For MCP servers
- **WebSockets**: Real-time communication

### Environment Variables
```bash
AGENTHUB_DIR=/custom/path              # Installation directory
AGENTHUB_MCP_HOST=localhost           # MCP server host
AGENTHUB_MCP_PORT=8000               # MCP server port
AGENTHUB_LOG_LEVEL=DEBUG             # Logging level
AGENTHUB_SUPPRESS_HTTP=true          # Suppress HTTP logs
```

### Code Style
- **Formatter**: Black (line length: 88)
- **Linter**: Ruff
- **Type checking**: MyPy (strict)
- **Imports**: Organized with isort

### CLI Commands
```bash
# Agent management
agenthub agent install agentplug/agent-name
agenthub agent list
agenthub agent info agentplug/agent-name
agenthub agent remove agentplug/agent-name

# Execution
agenthub agent exec agentplug/agent-name method_name "parameters"
```

## 🔧 File Editing Best Practices

### General Guidelines
- **Read before edit**: Always read files to understand structure
- **Exact matches**: Ensure old_string matches exactly (whitespace, quotes, etc.)
- **Small edits**: Break large changes into smaller, targeted edits
- **Verify changes**: Check the result after each edit
- **Preserve formatting**: Keep indentation and line breaks consistent

### Common Pitfalls
❌ **String mismatch**: Off by one space or quote character
✅ **Solution**: Read the file section first, copy exact text

❌ **Large multi-line edit fails**: Too much context, inexact match
✅ **Solution**: Break into smaller, focused edits

❌ **File doesn't exist**: Trying to edit non-existent file
✅ **Solution**: Check with `glob_file_search` or `list_dir` first

❌ **Creating backup files**: `old_implementation_backup.py`
✅ **Solution**: Use git, not manual backups

### Experiment Workflow
1. Create temporary file for validation (e.g., `temp_test.py`)
2. Test and validate approach
3. If successful, integrate into existing files
4. **Delete temporary file immediately**
5. Verify integration works

## 🎨 Built-in Tools Development

### RAG Tool
**Location**: `agenthub/builtin/tools/rag/`

**Key Files**:
- `rag_tool.py` - Main RAG implementation
- `document_store.py` - Document indexing and retrieval
- `config.py` - RAG configuration

**Usage Pattern**:
```python
from agenthub.builtin.tools.rag import create_rag_tool, RAGConfig

config = RAGConfig(source_directory="./docs")
rag = create_rag_tool(config=config)
results = rag.search_documents(query_text="query", max_results=5)
```

### Web Search Tool
**Location**: `agenthub/builtin/tools/web_search/`

**Simple MCP Server Pattern**:
```python
from agenthub.core.tools import tool, run_resources

@tool(name="tool_name", description="...")
def tool_function(param: str) -> dict:
    # Implementation
    return {"result": param}

run_resources()  # Start MCP server
```


## 📝 Documentation Guidelines

### Code Documentation
- Add docstrings to all public functions/classes
- Include type hints for all parameters and returns
- Explain **why**, not just **what**
- Document exceptions and edge cases

### Examples
- Keep examples minimal and focused
- One concept per example file
- Include comments for key steps
- Show both basic and advanced usage
- Add error handling examples

### Comments
- Explain non-obvious decisions
- Link to relevant issues/PRs when applicable
- Mark TODOs with context: `# TODO(username): description`

## ⚠️ Known Issues & Workarounds

### MCP Connection Testing
**Issue**: Connection test may fail with TaskGroup errors, but tool calls still work.
**Workaround**: Return success=True from connection tests, allow tool calls to proceed.

**Example**: See `examples/clients/rag_client.py` for handling pattern.

### UV Environment Isolation
**Issue**: Some packages don't install cleanly in UV environments.
**Workaround**: Add explicit dependencies to agent.yaml, use standard PyPI packages.

### WebSocket Connections
**Issue**: WebSocket sessions need proper cleanup.
**Workaround**: Use context managers, explicit close() calls in teardown.

## 🎯 Current Focus Areas

### Priorities
1. **Tool ecosystem expansion** - More built-in tools
2. **Agent examples** - Showcase real-world use cases
3. **Documentation** - User guides, API docs
4. **Performance** - Optimize agent loading and execution

### What Works Well
✅ Agent loading and execution
✅ MCP tool integration
✅ Process isolation with UV
✅ WebSocket communication
✅ GitHub-based registry
✅ RAG and web search tools

### What Needs Care
⚠️ Complex multi-agent orchestration (new territory)
⚠️ Large-scale tool injection (test thoroughly)
⚠️ Cross-platform compatibility (focus on Unix first)

## 🔍 Debugging Tips

### Enable Debug Logging
```bash
export AGENTHUB_LOG_LEVEL=DEBUG
export AGENTHUB_SUPPRESS_HTTP=false
```

### Common Issues
**Agent not found**: Check GitHub URL, verify agent.yaml exists
**Tool not registered**: Verify `@tool` decorator, check MCP server is running
**Import errors**: Check UV environment, verify dependencies in agent.yaml
**WebSocket errors**: Check port availability, verify server is running

### Useful Debug Commands
```python
# Check agent installation
ah.list_installed_agents()

# Verify tool registration
from agenthub.core.tools.registry import get_tool_registry
registry = get_tool_registry()
print(registry.list_tools())

# Test MCP connection
# See examples/clients/ for client patterns
```

## 📚 Additional Resources

- **Main README**: `/Users/nguyennm/Project/agenthub/README.md`
- **Examples**: `/Users/nguyennm/Project/agenthub/examples/`
- **Tests**: `/Users/nguyennm/Project/agenthub/tests/`

## 🤝 Contributing Guidelines

When implementing features:
1. Follow existing patterns in the codebase
2. Write tests alongside code (test-first when possible)
3. Keep changes focused and atomic
4. Update examples if adding new functionality
5. Run linters and type checking before completion
6. Clean up any temporary files or experiments

Remember: **Simple, working code is better than complex, perfect code.**
