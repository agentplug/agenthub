# Agent Hub MVP Technology Stack

**Document Type**: MVP Technology Stack
**Author**: William
**Date Created**: 2025-06-28
**Last Updated**: 2025-06-28
**Status**: Final
**Level**: L1 - MVP Technology Level
**Audience**: Technical Architects, Developers, DevOps Team

## 🎯 **MVP Technology Overview**

Agent Hub MVP uses a **mature, proven technology stack** optimized for rapid development, reliability, and developer experience. The stack prioritizes **simplicity over complexity** and **stability over cutting-edge features** to ensure MVP success.

### **MVP Technology Principles**
1. **Proven Technologies**: Use battle-tested tools with strong community support
2. **Minimal Dependencies**: Reduce complexity and potential failure points
3. **Developer Experience**: Optimize for fast iteration and debugging
4. **Cross-Platform**: Support Windows, macOS, and Linux from day one
5. **Performance**: Meet MVP performance requirements without over-engineering

## 🐍 **Core Language & Runtime**

### **Python 3.12+**
- **Version**: Python 3.12 or higher
- **Rationale**: Latest stable Python with performance improvements and modern features
- **Benefits**:
  - Excellent subprocess and virtual environment support
  - Rich ecosystem for CLI and package management
  - Cross-platform compatibility
  - Strong typing support for better code quality

### **Python Features Used**
```python
# Key Python features for MVP
import subprocess          # Agent execution
import venv               # Virtual environment management
import pathlib            # Cross-platform path handling
import asyncio            # Async operations (future enhancement)
import typing             # Type hints for better code quality
import dataclasses        # Clean data structures
```

## 🖥️ **CLI Framework**

### **Click 8.x**
- **Version**: Click 8.0 or higher
- **Rationale**: Mature, feature-rich CLI framework with excellent Python integration
- **Benefits**:
  - Declarative command definition
  - Built-in help generation
  - Type conversion and validation
  - Rich plugin ecosystem
  - Excellent documentation

### **CLI Structure Example**
```python
# agenthub/cli/main.py
import click

@click.group()
@click.version_option(version="1.0.0")
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
def cli(verbose):
    """Agent Hub - One-line AI agent integration."""
    pass

@cli.command()
@click.argument('agent_path')
@click.option('--version', help='Specific agent version')
def install(agent_path, version):
    """Install an agent from the registry."""
    # Implementation
    pass

@cli.command()
@click.option('--installed', is_flag=True, help='Show only installed agents')
def list(installed):
    """List available or installed agents."""
    # Implementation
    pass
```

## 📦 **Package Management**

### **UV Package Manager**
- **Version**: Latest stable release
- **Rationale**: 10x faster than pip, unified tool for Python development
- **Benefits**:
  - Extremely fast dependency resolution
  - Built-in virtual environment management
  - Lock file support for reproducible builds
  - Compatible with existing Python ecosystem
  - Single binary installation

### **UV Integration with Fallback**
```python
# agenthub/runtime/environment_manager.py
import subprocess
import shutil
```

## 🛠️ **Tool Management Dependencies**

### **Core Tool Support**
- **inspect**: Function signature and metadata extraction
- **pickle**: Tool serialization and persistence
- **typing**: Type hints for tool validation

### **Tool Infrastructure Dependencies**
- **inspect**: Function signature and metadata extraction
- **pickle**: Tool serialization and persistence
- **typing**: Type hints for tool validation
- **pathlib**: Safe file operations for tool discovery

### **Tool Infrastructure Example**
```python
# agenthub/core/tool_infrastructure.py
import inspect
import pickle
from typing import Dict, Any, Callable
from pathlib import Path

class ToolInfrastructure:
    def __init__(self, agent_dir: Path):
        self.agent_dir = agent_dir
        self.agent_tools = {}
        self.custom_tools = {}
        self.tools_metadata = {}

        # Discover agent's built-in tools
        self._discover_agent_tools()

    def discover_agent_tools(self) -> Dict[str, Callable]:
        """Discover tools that the agent has implemented."""
        # Read agent's manifest.json and find tool implementations
        pass

    def register_custom_tool(self, tool_name: str, tool_function: Callable):
        """Register a custom user tool (can override agent's built-in tools)."""
        self._register_tool(tool_name, tool_function, is_custom=True)

    def get_tool(self, tool_name: str) -> Callable:
        """Get tool with priority: custom tools > agent's built-in tools."""
        if tool_name in self.custom_tools:
            return self.custom_tools[tool_name]
        elif tool_name in self.agent_tools:
            return self.agent_tools[tool_name]
        else:
            raise ToolNotFoundError(f"Tool '{tool_name}' not found")

    def list_available_tools(self) -> Dict[str, List[str]]:
        """List tools by category: agent's built-in, custom, all."""
        return {
            "agent_builtin": list(self.agent_tools.keys()),
            "custom": list(self.custom_tools.keys()),
            "all": list(set(self.agent_tools.keys()) | set(self.custom_tools.keys()))
        }

    def _register_tool(self, tool_name: str, tool_function: Callable, is_custom: bool = False):
        """Internal tool registration with priority handling."""
        if tool_name in self.agent_tools and is_custom:
            # User tool overrides agent's built-in tool
            logging.info(f"Custom tool '{tool_name}' overrides agent's built-in tool")

        if is_custom:
            self.custom_tools[tool_name] = tool_function
        else:
            self.agent_tools[tool_name] = tool_function

        self._update_tool_metadata(tool_name, tool_function, is_custom)
```
from pathlib import Path
import logging

class EnvironmentManager:
    def __init__(self):
        self.uv_path = self._find_uv()
        self.fallback_to_pip = self.uv_path is None
        if self.fallback_to_pip:
            logging.warning("UV not found, falling back to pip")

    def _find_uv(self) -> Path:
        """Find UV package manager with fallback to pip."""
        # Try to find UV in PATH
        uv_path = shutil.which("uv")
        if uv_path:
            return Path(uv_path)

        # Try common installation paths
        common_paths = [
            Path.home() / ".cargo" / "bin" / "uv",
            Path.home() / ".local" / "bin" / "uv",
            Path("/usr/local/bin/uv"),
            Path("/opt/homebrew/bin/uv")  # macOS Homebrew
        ]

        for path in common_paths:
            if path.exists() and path.is_file():
                return path

        return None

    def create_environment(self, agent_path: Path) -> Path:
        """Create virtual environment using UV or fallback to pip."""
        venv_path = agent_path / "venv"

        if self.fallback_to_pip:
            return self._create_venv_with_pip(venv_path)
        else:
            return self._create_venv_with_uv(venv_path)

    def _create_venv_with_uv(self, venv_path: Path) -> Path:
        """Create virtual environment using UV."""
        try:
            subprocess.run([
                str(self.uv_path), "venv", str(venv_path)
            ], check=True, capture_output=True, text=True)
            return venv_path
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logging.warning(f"UV venv creation failed: {e}, falling back to pip")
            self.fallback_to_pip = True
            return self._create_venv_with_pip(venv_path)

    def _create_venv_with_pip(self, venv_path: Path) -> Path:
        """Create virtual environment using standard venv module."""
        import venv
        venv.create(venv_path, with_pip=True)
        return venv_path

    def install_dependencies(self, venv_path: Path, requirements: list):
        """Install dependencies using UV or fallback to pip."""
        if self.fallback_to_pip:
            self._install_dependencies_with_pip(venv_path, requirements)
        else:
            self._install_dependencies_with_uv(venv_path, requirements)

    def _install_dependencies_with_uv(self, venv_path: Path, requirements: list):
        """Install dependencies using UV."""
        python_path = venv_path / "bin" / "python"
        if not python_path.exists():
            python_path = venv_path / "Scripts" / "python.exe"  # Windows

        for requirement in requirements:
            try:
                subprocess.run([
                    str(self.uv_path), "pip", "install", requirement,
                    "--python", str(python_path)
                ], check=True, capture_output=True, text=True)
            except subprocess.CalledProcessError as e:
                logging.warning(f"UV dependency installation failed: {e}, falling back to pip")
                self.fallback_to_pip = True
                self._install_dependencies_with_pip(venv_path, requirements)
                break

    def _install_dependencies_with_pip(self, venv_path: Path, requirements: list):
        """Install dependencies using pip."""
        python_path = venv_path / "bin" / "python"
        if not python_path.exists():
            python_path = venv_path / "Scripts" / "python.exe"  # Windows

        for requirement in requirements:
            subprocess.run([
                str(python_path), "-m", "pip", "install", requirement
            ], check=True, capture_output=True, text=True)
```

## 🌐 **HTTP Client & API**

### **Requests 2.31+**
- **Version**: Requests 2.31.0 or higher
- **Rationale**: Battle-tested HTTP library with excellent Python integration
- **Benefits**:
  - Simple, intuitive API
  - Excellent error handling
  - Session management for performance
  - Built-in JSON support
  - Comprehensive documentation

### **GitHub API Integration**
```python
# agenthub/registry/github_client.py
import requests
import json
import base64

class GitHubRegistryClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Agent-Hub/1.0.0',
            'Accept': 'application/vnd.github.v3+json'
        })

    def get_registry(self) -> dict:
        """Fetch registry.json from GitHub."""
        url = "https://api.github.com/repos/agentplug/agent-registry/contents/registry.json"

        response = self.session.get(url)
        response.raise_for_status()

        # Decode GitHub API response
        content_data = response.json()
        content = base64.b64decode(content_data["content"]).decode('utf-8')

        return json.loads(content)
```

## 📊 **Data Formats**

### **YAML Configuration**
- **Library**: PyYAML 6.0+
- **Rationale**: Human-readable configuration format with rich data types
- **Usage**: Agent manifests, configuration files, user preferences

### **JSON Data Exchange**
- **Library**: Built-in json module
- **Rationale**: Standard format for API communication and data storage
- **Usage**: Registry data, agent metadata, configuration

### **Data Format Examples**
```yaml
# agent.yaml - Agent manifest
name: "coding-agent"
version: "1.0.0"
description: "AI coding assistant for Python development"
author: "meta"
license: "MIT"

interface:
  methods:
    generate_code:
      description: "Generate Python code from description"
      parameters:
        prompt: {type: "string", required: true}
        style: {type: "string", required: false, default: "clean"}
      returns: {type: "string", description: "Generated Python code"}

dependencies:
  python: ">=3.12"
  runtime: ["openai>=1.0.0", "tiktoken>=0.5.0"]
```

```json
// registry.json - Agent registry
{
  "version": "1.0.0",
  "updated_at": "2025-06-28T10:00:00Z",
  "agents": {
    "meta/coding-agent": {
      "name": "coding-agent",
      "version": "1.0.0",
      "author": "meta",
      "description": "AI coding assistant for Python development",
      "download_url": "https://github.com/meta/coding-agent/archive/v1.0.0.tar.gz"
    }
  }
}
```

## 🔧 **Development Tools**

### **Testing Framework**
- **Framework**: pytest 7.0+
- **Rationale**: Modern, feature-rich testing framework with excellent Python integration
- **Benefits**:
  - Simple test writing and execution
  - Rich fixture system
  - Excellent plugin ecosystem
  - Built-in coverage reporting

### **Code Quality**
- **Formatter**: black 23.0+
- **Linter**: flake8 6.0+
- **Type Checker**: mypy 1.0+
- **Rationale**: Automated code quality tools for consistent codebase

### **Development Setup**
```bash
# Development environment setup
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black .

# Lint code
flake8

# Type check
mypy .
```

## 🗄️ **Data Storage**

### **File-Based Storage**
- **Approach**: Local file system with structured directories
- **Rationale**: Simple, reliable, no external dependencies
- **Benefits**:
  - Zero maintenance overhead
  - Easy backup and restore
  - Simple debugging
  - Cross-platform compatibility

### **Storage Structure**
```
~/.agenthub/
├── agents/                          # Installed agents
│   ├── meta/
│   │   └── coding-agent/
│   │       ├── agent.yaml           # Agent manifest
│   │       ├── agent.py             # Main agent script
│   │       ├── venv/                # Virtual environment
│   │       └── .metadata.json       # Installation metadata
├── cache/                           # Registry cache
│   └── registry.json               # Cached registry data
├── config/                          # Configuration
│   └── settings.yaml               # User settings
└── logs/                            # Execution logs
    ├── install.log
    └── execution.log
```

## 🔒 **Security & Validation**

### **Input Validation**
- **Library**: Pydantic 2.0+
- **Rationale**: Data validation and settings management with excellent type hints
- **Benefits**:
  - Runtime type checking
  - Automatic validation
  - Clear error messages
  - JSON schema generation

### **Security Features**
```python
# agenthub/security/validator.py
from pydantic import BaseModel, Field
from typing import List, Optional

class AgentManifest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    version: str = Field(..., regex=r'^\d+\.\d+\.\d+$')
    description: str = Field(..., min_length=10, max_length=1000)
    author: str = Field(..., min_length=1, max_length=100)
    license: str = Field(..., min_length=1, max_length=50)

    interface: dict = Field(..., description="Agent interface definition")
    dependencies: Optional[dict] = Field(default=None)
    tags: Optional[List[str]] = Field(default_factory=list)

def validate_manifest(manifest_data: dict) -> AgentManifest:
    """Validate agent manifest data."""
    return AgentManifest(**manifest_data)
```

## 🚀 **Performance & Caching**

### **Local Caching**
- **Approach**: File-based caching with TTL
- **Rationale**: Simple, reliable caching without external dependencies
- **Benefits**:
  - Offline operation capability
  - Fast access to cached data
  - Simple cache invalidation
  - No external service dependencies

### **Caching Implementation**
```python
# agenthub/cache/cache_manager.py
import json
import time
from pathlib import Path
from typing import Optional, Any

class CacheManager:
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def get(self, key: str, ttl: int = 3600) -> Optional[Any]:
        """Get cached value if not expired."""
        cache_file = self.cache_dir / f"{key}.json"

        if not cache_file.exists():
            return None

        try:
            # Simple TTL check using file modification time
            if time.time() - cache_file.stat().st_mtime > ttl:
                return None

            with open(cache_file, 'r') as f:
                return json.load(f)

        except (json.JSONDecodeError, IOError):
            return None

    def set(self, key: str, value: Any):
        """Cache a value."""
        cache_file = self.cache_dir / f"{key}.json"

        try:
            with open(cache_file, 'w') as f:
                json.dump(value, f)
        except IOError as e:
            logging.error(f"Failed to cache {key}: {e}")
```

## 📱 **Cross-Platform Support**

### **Platform Compatibility**
- **Windows**: Windows 10+ (64-bit)
- **macOS**: macOS 10.15+ (Catalina)
- **Linux**: Ubuntu 18.04+, CentOS 7+, RHEL 7+

### **Platform-Specific Handling**
```python
# agenthub/utils/platform.py
import platform
import os
from pathlib import Path

def get_platform_info():
    """Get platform-specific information."""
    system = platform.system().lower()

    if system == "windows":
        return {
            'venv_python': 'Scripts\\python.exe',
            'venv_activate': 'Scripts\\activate.bat',
            'path_separator': ';'
        }
    elif system == "darwin":  # macOS
        return {
            'venv_python': 'bin/python',
            'venv_activate': 'bin/activate',
            'path_separator': ':'
        }
    else:  # Linux and others
        return {
            'venv_python': 'bin/python',
            'venv_activate': 'bin/activate',
            'path_separator': ':'
        }

def get_python_executable(venv_path: Path) -> Path:
    """Get Python executable path for virtual environment."""
    system = platform.system().lower()
    if system == "windows":
        return venv_path / "Scripts\\python.exe"
    else:
        return venv_path / "bin/python"

def get_activate_script(venv_path: Path) -> Path:
    """Get virtual environment activation script."""
    system = platform.system().lower()
    if system == "windows":
        return venv_path / "Scripts\\activate.bat"
    else:
        return venv_path / "bin/activate"
```

def get_home_dir() -> Path:
    """Get user home directory."""
    return Path.home()

def get_agenthub_dir() -> Path:
    """Get Agent Hub configuration directory."""
    return get_home_dir() / '.agenthub'
```

## 📊 **Technology Evaluation Matrix**

### **Selection Criteria**
| Criterion | Weight | Description |
|-----------|--------|-------------|
| **Maturity** | 30% | Proven in production environments |
| **Simplicity** | 25% | Easy to understand and maintain |
| **Performance** | 20% | Meets MVP performance requirements |
| **Community** | 15% | Active development and support |
| **Integration** | 10% | Good integration with other tools |

### **Technology Evaluation**

#### **CLI Framework**
| Tool | Maturity | Simplicity | Performance | Community | Integration | Score |
|------|----------|------------|-------------|-----------|-------------|-------|
| **Click** ✅ | 9/10 | 8/10 | 9/10 | 9/10 | 9/10 | **8.8/10** |
| argparse | 10/10 | 6/10 | 10/10 | 8/10 | 7/10 | 8.2/10 |
| typer | 7/10 | 8/10 | 8/10 | 7/10 | 8/10 | 7.6/10 |

#### **Package Manager**
| Tool | Maturity | Simplicity | Performance | Community | Integration | Score |
|------|----------|------------|-------------|-----------|-------------|-------|
| **UV** ✅ | 7/10 | 8/10 | 10/10 | 7/10 | 8/10 | **8.0/10** |
| pip | 10/10 | 7/10 | 4/10 | 10/10 | 9/10 | 8.0/10 |
| conda | 9/10 | 5/10 | 6/10 | 8/10 | 7/10 | 7.0/10 |

#### **HTTP Client**
| Tool | Maturity | Simplicity | Performance | Community | Integration | Score |
|------|----------|------------|-------------|-----------|-------------|-------|
| **requests** ✅ | 10/10 | 9/10 | 8/10 | 10/10 | 9/10 | **9.2/10** |
| httpx | 8/10 | 8/10 | 8/10 | 7/10 | 8/10 | 7.8/10 |
| aiohttp | 8/10 | 6/10 | 9/10 | 8/10 | 7/10 | 7.6/10 |

## 🔮 **Post-MVP Technology Considerations**

### **Future Enhancements**
- **Async Support**: asyncio for concurrent operations
- **Database**: SQLite or PostgreSQL for complex data
- **Search Engine**: Elasticsearch for agent discovery
- **Containerization**: Docker for enhanced security
- **Cloud Integration**: AWS/GCP for scaling

### **Technology Migration Path**
```python
# Current MVP approach
import subprocess
import venv

# Future enhancement approach
import asyncio
import docker
import elasticsearch

# Migration strategy: Gradual enhancement without breaking changes
class AgentRuntime:
    def __init__(self, use_containers: bool = False):
        self.use_containers = use_containers
        self.executor = DockerExecutor() if use_containers else SubprocessExecutor()

    async def execute_agent(self, agent_path: str, method: str, params: dict):
        """Execute agent with current or future technology."""
        if self.use_containers:
            return await self.executor.execute_container(agent_path, method, params)
        else:
            return await self.executor.execute_subprocess(agent_path, method, params)
```

## 🎯 **MVP Technology Summary**

### **Selected Technologies**
- **Core Language**: Python 3.12+
- **CLI Framework**: Click 8.x
- **Package Manager**: UV (latest)
- **HTTP Client**: Requests 2.31+
- **Data Formats**: YAML (PyYAML), JSON
- **Testing**: pytest 7.0+
- **Code Quality**: black, flake8, mypy
- **Validation**: Pydantic 2.0+

### **Technology Benefits**
- ✅ **Proven Reliability**: Battle-tested tools with strong community support
- ✅ **Fast Development**: Excellent developer experience and tooling
- ✅ **Cross-Platform**: Native support for Windows, macOS, and Linux
- ✅ **Performance**: Meets MVP performance requirements
- ✅ **Maintainability**: Simple, well-documented technologies

### **Implementation Timeline**
- **Week 1**: Core Python setup and UV integration
- **Week 2**: Click CLI framework and basic commands
- **Week 3**: Requests integration and GitHub API
- **Week 4**: Testing framework and code quality tools
- **Week 5**: Validation and error handling
- **Week 6**: Documentation and final polish

This technology stack provides a **solid, performant, and maintainable foundation** for the Agent Hub MVP while optimizing for rapid development and minimal operational overhead.
