# 🤖 AgentHub

<div align="center">

**The "App Store for AI Agents"** - Discover, compose, and use AI agents with one-line simplicity

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Alpha-orange.svg)]()
[![PyPI version](https://badge.fury.io/py/agenthub-sdk.svg)](https://badge.fury.io/py/agenthub-sdk)


[📖 Documentation](https://docs.agenthub.dev) • [🚀 Quick Start](#-quick-start) • [🐛 Report a Bug](#-reporting-bugs) • [🤝 Contributing](#-contributing) • [📧 Contact](#-contact)

</div>

## 🚀 What is AgentHub?

Transform weeks of AI agent integration into **one line of code**. AgentHub makes powerful AI agents as easy to use as installing a Python package.

### 🗺️ At a Glance

- What you do: Install agents, customize with tools/knowledge, and call `agent.solve()`
- What you get: High-level `agent.solve()` API, isolated environments, auto-install, and monitoring
- Who it's for: Developers and builders who want pragmatic, composable AI systems without boilerplate

### 🎯 **Core Abilities**

- **🧠 Universal Solve Method**: `agent.solve()` — describe your goal, AI selects the best method
- **🔧 Customize Agents**: Add custom tools and domain knowledge to any agent
- **🏪 Agent Marketplace**: Discover and install agents from GitHub with one command
- **🔌 One-Line Integration**: `ah.load_agent("user/agent")` - no complex setup required
- **🔒 Isolated Environments**: No dependency conflicts between agents
- **⚡ Auto-Installation**: Agents install automatically when needed
- **🎯 CLI Interface**: Full command-line management and execution
- **📊 Comprehensive Monitoring**: Full visibility into agent execution and performance

### Before AgentHub

```python
# Traditional approach: 2-4 weeks setup
# 1. Find agent on GitHub
# 2. Clone repository
# 3. Read documentation
# 4. Install dependencies (version conflicts!)
# 5. Configure environment
# 6. Debug integration issues
# 7. Write wrapper code
# 8. Test and validate
```

### With AgentHub

```python
# One line, 30 seconds
import agenthub as ah
coding_agent = ah.load_agent("agentplug/coding-agent")
code = coding_agent.generate_code("neural network class")
```

## ✨ Key Features

- **🧠 Universal Solve Method**: `agent.solve()` — describe goals, not steps
- **🏪 Agent Marketplace**: Discover and install agents from GitHub with one command
- **🔌 One-Line Integration**: `ah.load_agent("user/agent")` - no complex setup required
- **🛠️ Custom Tools & Knowledge**: Create tools with `@tool`, connect via `run_resources()`, and attach domain knowledge
- **🔒 Isolated Environments**: No dependency conflicts between agents
- **⚡ Auto-Installation**: Agents install automatically when needed
- **🎯 CLI Interface**: Full command-line management and execution
- **📊 Comprehensive Monitoring**: Full visibility into agent execution and performance

## 🚀 Quick Start

### ⚡ Install AgentHub

```bash
# Install AgentHub
pip install agenthub-sdk

# Verify installation
agenthub --version
```

### 🔑 Set Up Your LLM

Agents need an LLM to run. Choose one:

**Cloud provider** — set the API key for whichever service you use:

```bash
# OpenAI
export OPENAI_API_KEY=sk-...

# Anthropic
export ANTHROPIC_API_KEY=sk-ant-...

# Google Gemini
export GOOGLE_API_KEY=...

# DeepSeek
export DEEPSEEK_API_KEY=...

# Groq
export GROQ_API_KEY=...
```

**Local LLM** — no API key needed. Just start [Ollama](https://ollama.com) or [LM Studio](https://lmstudio.ai) and AgentHub auto-detects it:

```bash
# Ollama (default port 11434)
ollama run llama3.2

# LM Studio (default port 1234) — start the local server from the app
```

AgentHub checks for a running local model first, then falls back to whichever cloud API key is set.

### 🎯 Your First Agent (30 seconds)

```python
import agenthub as ah

# 🪄 One line to load any agent
coding_agent = ah.load_agent("agentplug/coding-agent")

# 🧠 Universal solve method - AI automatically selects the best approach
result = coding_agent.solve("Create a Python function that calculates compound interest")
print(result["result"])

# ✅ Magic happens automatically:
# • GitHub repository cloned
# • Virtual environment created
# • Dependencies installed
# • Agent validated and ready
# • AI selects optimal method for your query
```

### 🧠 Universal Solve Method

Describe your goal in natural language — `agent.solve()` selects the best internal method and executes the steps:

```python
import agenthub as ah

# Load any agent
coding_agent = ah.load_agent("agentplug/coding-agent")
analysis_agent = ah.load_agent("agentplug/analysis-agent")

# 🧠 AI automatically selects the best method for each query
code = coding_agent.solve("Create a neural network class")  # → generate_code()
explanation = coding_agent.solve("Explain what this function does")  # → explain_code()
validation = coding_agent.solve("Validate this code meets PEP8: def hello(): print('world')")  # → validate_code()

# 📊 Analysis agent automatically chooses the right approach
insights = analysis_agent.solve("Analyze this customer feedback: 'Great app!'")  # → analyze_text()
data_analysis = analysis_agent.solve("Process sales_data.csv")  # → analyze_data()

# ✅ No need to know specific method names - just describe what you want!
```

### 🛠️ Custom Tools & Extensions

AgentHub makes it easy to extend agents with custom tools:

```python
from agenthub.core.tools import tool, run_resources

# Create custom tools with @tool decorator
@tool(name="web_search", description="Search the web for information")
def web_search(query: str) -> str:
    """Search the web for information."""
    # Your custom implementation
    return f"Search results for: {query}"

@tool(name="database_query", description="Execute SQL query on database")
def database_query(sql: str) -> dict:
    """Execute SQL query on database."""
    # Your custom implementation
    return {"results": "..."}

# Start the tool server - this makes tools available to agents
if __name__ == "__main__":
    print("🚀 Starting tool server...")
    run_resources()  # This starts the MCP server
```

**Using Tools with Agents:**

```python
import agenthub as ah

# Load agent with external tools (tools are now available after run_resources())
coding_agent = ah.load_agent(
    "agentplug/coding-agent",
    external_tools=["web_search", "database_query"]  # Connect to your custom tools
)
result = coding_agent.solve("Search for React best practices and create a component")
# ✅ Agent can now use your custom web_search tool!
```

### 🔗 Complete Tool Workflow Example

Here's the complete workflow for using custom tools with agents:

```python
# 1. Define and start tools (run this first)
from agenthub.core.tools import tool, run_resources

@tool(name="web_search", description="Search the web for information")
def web_search(query: str) -> str:
    return f"Search results for: {query}"

if __name__ == "__main__":
    run_resources()  # Start MCP server

# 2. Use tools with agents (run this after starting tools)
import agenthub as ah

coding_agent = ah.load_agent(
    "agentplug/coding-agent",
    external_tools=["web_search"]  # Connect to your custom tool
)

result = coding_agent.solve("Search for Python best practices and create a function")
# ✅ Agent can now use your web_search tool!
```

### 🔒 Isolated Environments

Each agent runs in its own isolated environment:

```python
# No dependency conflicts between agents
coding_agent = ah.load_agent("agentplug/coding-agent")      # Uses Python 3.11
data_agent = ah.load_agent("agentplug/data-agent")          # Uses Python 3.12
ml_agent = ah.load_agent("agentplug/ml-agent")             # Uses different packages

# All agents work independently without conflicts
```

### 💻 CLI Commands

```bash
# Get agent information
agenthub info agentplug/scientific-paper-analyzer

# Install new agent
agenthub agent install agentplug/scientific-paper-analyzer

# Execute agent method (multiple ways)
agenthub exec agentplug/scientific-paper-analyzer analyze_paper "research.pdf"
agenthub exec agentplug/scientific-paper-analyzer analyze_paper '{"file": "research.pdf"}'
agenthub exec agentplug/scientific-paper-analyzer analyze_paper --interactive

# Agent management commands
agenthub agent list                                          # List installed agents
agenthub agent info agentplug/scientific-paper-analyzer     # Detailed agent info
agenthub agent status agentplug/scientific-paper-analyzer   # Check agent status
agenthub agent remove agentplug/scientific-paper-analyzer   # Remove an agent
agenthub agent backup agentplug/scientific-paper-analyzer   # Create backup
agenthub agent restore agentplug/scientific-paper-analyzer  # Restore from backup
agenthub agent repair agentplug/scientific-paper-analyzer   # Repair broken agent
agenthub agent migrate agentplug/scientific-paper-analyzer  # Migrate Python version
agenthub agent optimize agentplug/scientific-paper-analyzer # Optimize environment
agenthub agent analyze-deps agentplug/scientific-paper-analyzer # Analyze dependencies
agenthub agent cleanup                                       # Clean up agent storage
agenthub agent clone agentplug/scientific-paper-analyzer    # Clone an agent
agenthub agent python-versions                               # List available Python versions

# System validation
agenthub validate
```

## 🛠️ Creating an AgentHub-Compatible Agent

See **[CREATING_AGENTS.md](CREATING_AGENTS.md)** for the full guide — covering `agent.yaml`, `agent.py`, `pyproject.toml`, and how to publish your agent to GitHub.

Reference implementation: [agentplug/coding-agent](https://github.com/agentplug/coding-agent)

## 📚 Examples

### 🧠 Universal Solve Method (Recommended)

```python
import agenthub as ah

# Load agents
coding_agent = ah.load_agent("agentplug/coding-agent")
analysis_agent = ah.load_agent("agentplug/analysis-agent")

# 🎯 AI automatically selects the best method for each query
code = coding_agent.solve("Create a React component for data table")
print(code["result"])

validation = coding_agent.solve("Validate this code meets PEP8: def hello(): print('world')")
print(validation["result"])

insights = analysis_agent.solve("Analyze this customer feedback: 'Great app!'")
print(insights["result"])
```

### 🛠️ Direct Method Calls

```python
import agenthub as ah

# Load coding agent
coding_agent = ah.load_agent("agentplug/coding-agent")

# Direct method calls (when you know the specific method)
code = coding_agent.generate_code("React component for data table")
print(code["result"])

explanation = coding_agent.explain_code("def hello(): print('world')")
print(explanation["result"])
```

### 🧠 Universal Solve Method Benefits

- **🎯 No Method Learning**: Just describe what you want
- **🤖 AI Method Selection**: Automatically chooses the best approach
- **📝 Natural Language**: Use plain English queries
- **🔄 Consistent Interface**: Same pattern across all agents

## 🐛 Reporting Bugs

Found a bug? [Open an issue](https://github.com/agentplug/agenthub/issues/new) and include:

- A short description of the problem
- Steps to reproduce it
- What you expected vs what happened
- Your Python version and OS (`python --version`, `uname -a`)
- Any relevant error output

## 🤝 Contributing

Contributions are welcome via pull request. Fork the repo, make your changes, and open a PR against `main`.

## 📞 Contact

For questions, bug reports, and feature requests: [nguyennm1024@gmail.com](mailto:nguyennm1024@gmail.com)

## 📄 License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

# 🚀 **AgentHub** - Making AI agents as easy as `pip install`

**One line. Infinite possibilities.**

</div>
