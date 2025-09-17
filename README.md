# 🤖 AgentHub

<div align="center">

**The "App Store for AI Agents"** - Discover, install, and use AI agents with one-line simplicity

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Beta-green.svg)]()
[![PyPI version](https://badge.fury.io/py/agentplug.svg)](https://badge.fury.io/py/agentplug)
[![PyPI downloads](https://pepy.tech/badge/agentplug)](https://pepy.tech/project/agentplug)

[📖 Documentation](https://docs.agenthub.dev) • [🚀 Quick Start](#-quick-start) • [🤝 Contributing](#-contributing) • [📧 Contact](#-contact)

</div>

## 🚀 What is AgentHub?

Transform weeks of AI agent integration into **one line of code**. AgentHub makes powerful AI agents as easy to use as installing a Python package.

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
import agentplug as ah
coding_agent = ah.load_agent("agentplug/coding-agent")
code = coding_agent.generate_code("neural network class")
```

## ✨ Key Features

- **🏪 Agent Marketplace**: Discover and install agents from GitHub
- **🔌 One-Line Integration**: `ah.load_agent("user/agent")`
- **🛠️ Custom Tools**: Create and inject tools with `@tool` decorator
- **🔒 Isolated Environments**: No dependency conflicts
- **⚡ Auto-Installation**: Agents install automatically when needed
- **🎯 CLI Interface**: Full command-line management

## 🚀 Quick Start

### ⚡ Install AgentHub

```bash
# Install AgentHub
pip install agentplug

# Verify installation
agentplug --version
```

### 🎯 Your First Agent (30 seconds)

```python
import agentplug as ah

# 🪄 One line to load any agent
paper_analyzer = ah.load_agent("agentplug/scientific-paper-analyzer")

# 📄 Use the agent immediately
result = paper_analyzer.analyze_paper("research_paper.pdf")
print(f"📊 Summary: {result['summary'][:200]}...")

# ✅ Magic happens automatically:
# • GitHub repository cloned
# • Virtual environment created
# • Dependencies installed
# • Agent validated and ready
```

### 🛠️ Using Custom Tools

Create powerful agents with your own tools:

```python
from agentplug.core.tools import tool, run_resources

@tool(name="web_search", description="Search the web for information")
def web_search(query: str, max_results: int = 10) -> list:
    """Search the web and return results."""
    # Your search implementation here
    return [f"Result {i+1} for '{query}'" for i in range(min(max_results, 3))]

@tool(name="data_analyzer", description="Analyze data patterns")
def data_analyzer(data: list, analysis_type: str = "basic") -> dict:
    """Analyze data and return insights."""
    return {
        "type": analysis_type,
        "count": len(data),
        "insights": f"Analyzed {len(data)} items"
    }

# 🚀 Start the tool server
if __name__ == "__main__":
    print("🔧 Starting tool server...")
    run_resources()  # Starts MCP server for tool execution
```

```python
# 🤖 Use tools with agents (run in separate process/terminal)
import agentplug as ah

# Load agent with custom tools
agent = ah.load_agent("agentplug/analysis-agent", tools=["web_search", "data_analyzer"])

# Agent's AI decides when and how to use tools
result = agent.analyze("What are the latest AI trends?")
# Agent automatically uses web_search and data_analyzer as needed!
```

### 💻 CLI Commands

```bash
# List all agents
agentplug list

# Get agent information
agentplug info agentplug/scientific-paper-analyzer

# Install new agent
agentplug agent install agentplug/scientific-paper-analyzer

# Execute agent method
agentplug exec agentplug/scientific-paper-analyzer analyze_paper "research.pdf"

# Check agent status
agentplug agent status agentplug/scientific-paper-analyzer

# Remove an agent
agentplug agent remove agentplug/scientific-paper-analyzer
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
agentplug exec ./my-coding-agent generate_code "hello world"
```

### 3. Publish to GitHub

```bash
git init
git add .
git commit -m "Initial agent release"
git remote add origin https://github.com/your-username/my-coding-agent.git
git push -u origin main
```

### 4. Share with the World!

```python
# Anyone can now use your agent:
import agentplug as ah
agent = ah.load_agent("your-username/my-coding-agent")
code = agent.generate_code("React component")
```

## 📚 Examples

### Code Generation Agent
```python
import agentplug as ah

# Load coding agent
coding_agent = ah.load_agent("agentplug/coding-agent")

# Generate code
code = coding_agent.generate_code("React component for data table")
print(code)

# Review existing code
review = coding_agent.review_code("def hello(): print('world')")
print(review)
```

### Data Analysis Agent
```python
import agentplug as ah

# Load analysis agent with tools
data_agent = ah.load_agent("agentplug/analysis-agent", tools=["data_analyzer", "web_search"])

# Analyze data
insights = data_agent.analyze("sales_data.csv")
print(insights)
```

### Scientific Paper Analyzer
```python
import agentplug as ah

# Load paper analyzer
paper_agent = ah.load_agent("agentplug/scientific-paper-analyzer")

# Analyze research paper
result = paper_agent.analyze_paper("research.pdf")
print(f"Summary: {result['summary']}")
print(f"Key findings: {result['key_findings']}")
```

## 🎯 Available Agents

| Agent | Description | Usage |
|-------|-------------|-------|
| `agentplug/coding-agent` | Generate and review code | `ah.load_agent("agentplug/coding-agent")` |
| `agentplug/analysis-agent` | Data analysis and insights | `ah.load_agent("agentplug/analysis-agent")` |
| `agentplug/scientific-paper-analyzer` | Analyze research papers | `ah.load_agent("agentplug/scientific-paper-analyzer")` |

## 🤝 Contributing

We welcome contributions! Here's how to get started:

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

- **🐛 Bug Reports**: [Open an Issue](https://github.com/agentplug/agenthub/issues)
- **📖 Documentation**: Improve guides and examples
- **🔧 Code**: Fix bugs, add features
- **🎨 Design**: UI/UX improvements
- **📊 Testing**: Help improve test coverage

## 📊 Roadmap

### ✅ Phase 1: Foundation (Live!)
- ✅ Core SDK with one-line agent loading
- ✅ GitHub integration and auto-installation
- ✅ Environment isolation with UV
- ✅ CLI tools and validation engine

### ✅ Phase 2.5: Tool Injection (Live!)
- ✅ Tool registry with FastMCP integration
- ✅ `@tool` decorator for custom tools
- ✅ Agent tool assignment functionality
- ✅ Comprehensive testing suite

### 🚧 Phase 2: Developer Experience (In Progress)
- 🚧 Agent Studio visual development environment
- 🚧 Testing framework and validation suite
- 🚧 Marketplace UI for agent discovery
- 🚧 Analytics dashboard

### 📋 Phase 3: Ecosystem Growth (Planning)
- 📋 Multi-agent workflows
- 📋 AI-powered agent recommendations
- 📋 Mobile app for agent management
- 📋 Revenue sharing platform

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
