# 🤖 AgentHub

<div align="center">

**The "App Store for AI Agents"** - Discover, compose, and use AI agents with one-line simplicity

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Beta-green.svg)]()
[![PyPI version](https://badge.fury.io/py/agenthub-sdk.svg)](https://badge.fury.io/py/agenthub-sdk)
[![PyPI downloads](https://pepy.tech/badge/agenthub-sdk)](https://pepy.tech/project/agenthub-sdk)

[📖 Documentation](https://docs.agenthub.dev) • [🚀 Quick Start](#-quick-start) • [🤝 Contributing](#-contributing) • [📧 Contact](#-contact)

</div>

## 🚀 What is AgentHub?

Transform weeks of AI agent integration into **one line of code**. AgentHub makes powerful AI agents as easy to use as installing a Python package.

### 🎯 **Core Abilities**

AgentHub revolutionizes how you work with AI agents:

- **🧩 Compose Multi-Agent Systems**: Build a `Team()` by plugging together pre-built or custom agents
- **🧠 Universal Intelligence**: `agent.solve()` and `Team().solve()` for high-level, goal-driven execution
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

## 🧩 Build Multi-Agent Teams (High-Level Flow)

Create complex systems by composing pre-built agents (research, analysis, data access, planning, quality control, ...) and your custom agents into a `Team()`.

```python
import agenthub as ah

# 1) Load pre-built agents from the marketplace (customize via load params)
research = ah.load_agent(
    "agentplug/research-agent",
    external_tools=["web_search"],            # attach your tools
    knowledge=["knowledge/base/"]             # attach your knowledge sources
)

analysis = ah.load_agent(
    "agentplug/analysis-agent",
    knowledge=["knowledge/base/"]
)

planner  = ah.load_agent("agentplug/planning-agent")
qc       = ah.load_agent("agentplug/quality-control-agent")

# 3) Compose into a Team
#    Team API preview — designed for simple, high-level orchestration
from agenthub import Team  # Coming soon

team = Team(name="ResearchPipeline", agents=[planner, research, analysis, qc])

# 4) High-level goal, single entry point
result = team.solve("Analyze the latest LLM papers and produce actionable insights")
print(result["result"])  # Unified output
```

Flow to build:

- **Pick agents**: research, analysis, data access, planning, quality control, ...
- **Customize**: pass `external_tools=[...]` and `knowledge=[...]` to `ah.load_agent(...)`
- **Compose**: add agents into a `Team()`
- **Solve**: call `Team().solve(goal)` to run the entire multi-agent pipeline

## ✨ Key Features

- **🧩 Team Composition (High-Level Logic)**: Create a `Team()` and plug agents together to build complex systems
- **🧠 Universal Solve Method**: `agent.solve()` and `Team().solve()` - describe goals, not steps
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

The `agent.solve()` and upcoming `Team().solve()` are AgentHub's breakthrough capabilities — describe a goal in natural language and let the system choose the best approach:

```python
import agenthub as ah

# Load any agent
coding_agent = ah.load_agent("agentplug/coding-agent")
analysis_agent = ah.load_agent("agentplug/analysis-agent")

# 🧠 AI automatically selects the best method for each query
code = coding_agent.solve("Create a neural network class")  # → generate_code()
review = coding_agent.solve("Review this code: def hello(): print('world')")  # → review_code()
explanation = coding_agent.solve("Explain what this function does")  # → explain_code()

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
# List all agents
agenthub list

# Get agent information
agenthub info agentplug/scientific-paper-analyzer

# Install new agent
agenthub agent install agentplug/scientific-paper-analyzer

# Execute agent method (multiple ways)
agenthub exec agentplug/scientific-paper-analyzer analyze_paper "research.pdf"
agenthub exec agentplug/scientific-paper-analyzer analyze_paper '{"file": "research.pdf"}'
agenthub exec agentplug/scientific-paper-analyzer analyze_paper --interactive

# Agent management commands
agenthub agent list                                    # List installed agents
agenthub agent status agentplug/scientific-paper-analyzer  # Check agent status
agenthub agent remove agentplug/scientific-paper-analyzer  # Remove an agent
agenthub agent backup agentplug/scientific-paper-analyzer  # Create backup
agenthub agent restore agentplug/scientific-paper-analyzer # Restore from backup
agenthub agent repair agentplug/scientific-paper-analyzer  # Repair broken agent
agenthub agent migrate agentplug/scientific-paper-analyzer # Migrate Python version
agenthub agent optimize agentplug/scientific-paper-analyzer # Optimize environment
agenthub agent analyze-deps agentplug/scientific-paper-analyzer # Analyze dependencies

# System validation
agenthub validate
```

## 🛠️ Creating Your Own Agent

### 1. Create Agent Files

```bash
mkdir my-coding-agent
cd my-coding-agent/
```

Create `agent.py`:

```python
class CodingAgent:
    def __init__(self):
        self.name = "Coding Agent"

    def generate_code(self, description: str) -> str:
        """Generate code based on description."""
        return f"# Generated code for: {description}\nprint('Hello, World!')"

    def review_code(self, code: str) -> str:
        """Review and improve code."""
        return f"Code review: {code} looks good!"
```

Create `agent.yaml`:

```yaml
name: coding-agent
version: 1.0.0
description: AI agent for code generation and review
author: your-username
entry_point: agent.py:CodingAgent
```

### 2. Test Locally

```bash
agenthub exec ./my-coding-agent generate_code "hello world"
```

### 3. Publish to GitHub

```bash
git init
git add .
git commit -m "Initial agent release"
git remote add origin https://github.com/your-username/my-coding-agent.git
git push -u origin main
```

### 4. Share with the World

```python
# Anyone can now use your agent:
import agenthub as ah
agent = ah.load_agent("your-username/my-coding-agent")
code = agent.generate_code("React component")
```

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

review = coding_agent.solve("Review this code: def hello(): print('world')")
print(review["result"])

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

review = coding_agent.review_code("def hello(): print('world')")
print(review["result"])
```

### 🧠 Universal Solve Method Benefits

- **🎯 No Method Learning**: Just describe what you want
- **🤖 AI Method Selection**: Automatically chooses the best approach
- **📝 Natural Language**: Use plain English queries
- **🔄 Consistent Interface**: Same pattern across all agents

## 🤝 Contributing

We welcome contributions! You can:

- Build and contribute new tools (via `@tool` and `run_resources()`)
- Create new pre-built agents (publishable GitHub repos with `agent.yaml`)
- Enhance existing agents (add methods, improve prompts, optimize flows)
- Improve documentation and examples

Here's how to get started:

### 🚀 Development Setup

```bash
# 1. Fork and clone
git clone https://github.com/YOUR_USERNAME/agenthub.git
cd agenthub

# 2. Setup environment
python3.12 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e ".[dev]"

# 3. Run tests
pytest tests/ -v

# 4. Make changes
git checkout -b feature/your-feature
```

### 🎯 Ways to Contribute

- **🧰 Tools**: Add new tools or improve existing ones
- **🤖 Pre-built Agents**: Create and share agents for common tasks
- **🚀 Enhancements**: Optimize agent methods, prompts, and pipelines
- **🐛 Bug Reports**: [Open an Issue](https://github.com/agentplug/agenthub/issues)
- **📖 Documentation**: Improve guides and examples
- **🔧 Code**: Fix bugs, add features
- **🎨 Design**: UI/UX improvements
- **📊 Testing**: Help improve test coverage

## 📞 Support & Community

### 💬 Get Help

| Platform | Purpose | Link |
|:---------|:--------|:-----|
| **💬 Discord** | Live chat and support | [Join Server](https://discord.gg/agenthub) |
| **🐦 Twitter** | Updates and announcements | [@AgentHub](https://twitter.com/agenthub) |
| **📧 Email** | Business inquiries | [agenthub@agentplug.net](mailto:agenthub@agentplug.net) |

### 🐛 Report Issues

- **Bug Reports**: [GitHub Issues](https://github.com/agentplug/agenthub/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/agentplug/agenthub/discussions)
- **Security Issues**: [agenthub@agentplug.net](mailto:agenthub@agentplug.net)

## 📄 License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

# 🚀 **AgentHub** - Making AI agents as easy as `pip install`

**One line. Infinite possibilities.**

</div>
