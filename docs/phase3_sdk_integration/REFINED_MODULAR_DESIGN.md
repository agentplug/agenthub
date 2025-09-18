# Phase 3: Refined Modular Design for Clean and Scalable Architecture

**Document Type**: Refined Architecture Design
**Author**: AgentHub Team
**Date Created**: 2025-01-27
**Last Updated**: 2025-01-27
**Status**: Ready for Implementation
**Purpose**: Clean, scalable, and maintainable modular architecture for Phase 3 SDK integration

## 🎯 **Design Principles**

### **1. Clean Architecture Principles**

- **Separation of Concerns**: Each module has a single, well-defined responsibility
- **Dependency Inversion**: High-level modules don't depend on low-level modules
- **Interface Segregation**: Small, focused interfaces rather than large, monolithic ones
- **Single Responsibility**: Each class/module has one reason to change

### **2. Scalability Principles**

- **Modular Design**: Easy to add new features without breaking existing functionality
- **Plugin Architecture**: Extensible system for new tool types and installation methods
- **Configuration-Driven**: Behavior controlled by configuration rather than code changes
- **Performance-First**: Optimized for common use cases while supporting complex scenarios

### **3. User Experience Principles**

- **Progressive Disclosure**: Simple API for common use cases, advanced features available when needed
- **Fail-Fast**: Clear error messages with actionable suggestions
- **Backward Compatibility**: Existing code continues to work with deprecation warnings
- **Intuitive Naming**: Self-documenting API with clear parameter names

## 🏗️ **Refined Module Architecture**

### **Core Module Structure**

```
agenthub/
├── sdk/                          # User-facing SDK (Simple API)
│   ├── __init__.py              # Clean public API
│   ├── load_agent.py            # Main load_agent function
│   ├── exceptions.py            # User-friendly exceptions
│   └── utils.py                 # SDK utilities
├── core/                        # Core business logic
│   ├── agents/                  # Agent management
│   │   ├── loader.py           # Agent loading and validation
│   │   ├── wrapper.py          # Agent wrapper with enhanced features
│   │   ├── manifest.py         # YAML parsing and validation
│   │   ├── validator.py        # Agent validation logic
│   │   └── tool_manager.py     # Built-in tool management
│   ├── tools/                   # Tool management system
│   │   ├── registry.py         # Tool registry (existing)
│   │   ├── builtin_manager.py  # Built-in tool management
│   │   ├── external_manager.py # External tool management
│   │   ├── conflict_resolver.py # Tool conflict resolution
│   │   └── validator.py        # Tool parameter validation
│   ├── knowledge/               # Knowledge management
│   │   ├── manager.py          # Knowledge injection and retrieval
│   │   ├── storage.py          # Knowledge persistence
│   │   └── validator.py        # Knowledge validation
│   └── installation/            # Installation system
│       ├── command_executor.py  # Command execution engine
│       ├── validator.py        # Installation validation
│       ├── plugins/            # Installation method plugins
│       │   ├── uv_plugin.py    # UV installation plugin
│       │   ├── pip_plugin.py   # Pip installation plugin
│       │   ├── make_plugin.py  # Make installation plugin
│       │   └── npm_plugin.py   # NPM installation plugin
│       └── result.py           # Installation results
├── runtime/                     # Runtime execution
│   ├── agent_runtime.py        # Agent execution runtime
│   ├── process_manager.py      # Process management
│   └── communication.py        # Framework-agent communication
└── config/                      # Configuration management
    ├── agent_config.py         # Agent configuration parsing
    ├── sdk_config.py           # SDK configuration
    └── validation.py           # Configuration validation
```

## 🔧 **Enhanced Module Design**

### **1. SDK Module (User-Facing)**

#### **`agenthub/sdk/__init__.py`**

```python
"""AgentHub SDK - Clean, user-friendly API for Phase 3.

This module provides a simple, intuitive interface for loading and configuring agents.
Users never need to understand the internal complexity - just use the simple API.
"""

from .load_agent import load_agent
from .exceptions import (
    AgentLoadError,
    AgentExecutionError,
    ValidationError,
    ToolConflictError,
    InstallationError
)

# Clean, simple API - no complex classes, just functions
__all__ = [
    "load_agent",           # Main function: load_agent(agent, external_tools=[...])
    "AgentLoadError",       # User-friendly exceptions
    "AgentExecutionError",
    "ValidationError",
    "ToolConflictError",
    "InstallationError"
]
```

#### **`agenthub/sdk/load_agent.py`**

```python
"""Enhanced load_agent function with Phase 3 features."""

import warnings
from typing import List, Optional, Dict, Any
from ..core.agents import AgentLoader, AgentWrapper
from ..core.tools import get_tool_registry
from ..core.knowledge import KnowledgeManager
from ..core.installation import InstallationManager
from .exceptions import AgentLoadError, ValidationError


def load_agent(
    agent_name: str,
    tools: Optional[List[str]] = None,  # DEPRECATED: use external_tools instead
    external_tools: Optional[List[str]] = None,  # New: external tools
    disabled_builtin_tools: Optional[List[str]] = None,  # New: disable built-in tools
    knowledge: Optional[str] = None,  # New: inject knowledge
    **kwargs
) -> AgentWrapper:
    """
    Load agent with user-friendly configuration.

    Args:
        agent_name: Agent name in format "namespace/agent"
        tools: DEPRECATED - use external_tools instead (for backward compatibility)
        external_tools: List of external tool names to add
        disabled_builtin_tools: List of built-in tools to disable (all enabled by default)
        knowledge: Text knowledge to inject into agent context

    Returns:
        AgentWrapper instance with configured tools and knowledge

    Raises:
        AgentLoadError: If agent cannot be loaded
        ValidationError: If configuration is invalid
    """
    # Handle backward compatibility
    if tools is not None:
        if external_tools is not None:
            raise ValidationError("Cannot specify both 'tools' and 'external_tools'. Use 'external_tools' instead.")
        external_tools = tools
        warnings.warn("'tools' parameter is deprecated. Use 'external_tools' instead.", DeprecationWarning)

    try:
        # Load agent definition from YAML (developer created)
        agent_info = _load_agent_from_yaml(agent_name)

        # Create agent instance
        agent = _create_agent_instance(agent_info)

        # Apply user configuration
        if external_tools:
            agent.add_external_tools(external_tools)

        if disabled_builtin_tools:
            agent.disable_builtin_tools(disabled_builtin_tools)

        if knowledge:
            agent.inject_knowledge(knowledge)

        return agent

    except Exception as e:
        raise AgentLoadError(f"Failed to load agent '{agent_name}': {e}") from e


def _load_agent_from_yaml(agent_name: str) -> Dict[str, Any]:
    """Load agent definition from YAML with enhanced schema support."""
    from ..core.agents import AgentLoader
    from ..storage.local_storage import LocalStorage

    storage = LocalStorage()
    loader = AgentLoader(storage=storage)

    # Parse namespace/agent format
    if "/" in agent_name:
        namespace, name = agent_name.split("/", 1)
    else:
        namespace, name = "default", agent_name

    return loader.load_agent(namespace, name)


def _create_agent_instance(agent_info: Dict[str, Any]) -> AgentWrapper:
    """Create agent instance with enhanced capabilities."""
    from ..core.agents import AgentWrapper
    from ..runtime.agent_runtime import AgentRuntime
    from ..storage.local_storage import LocalStorage

    storage = LocalStorage()
    runtime = AgentRuntime(storage=storage)

    return AgentWrapper(
        agent_info=agent_info,
        runtime=runtime,
        tool_registry=get_tool_registry()
    )
```

### **2. Core Agents Module (Enhanced)**

#### **`agenthub/core/agents/tool_manager.py`**

```python
"""Built-in tool management for agents."""

from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass
from ..tools import ToolRegistry


@dataclass
class BuiltinToolInfo:
    """Information about a built-in tool."""
    name: str
    description: str
    required: bool  # True = cannot be disabled, False = can be disabled
    parameters: Dict[str, Any]
    enabled: bool = True


class AgentToolManager:
    """Manages built-in tools for an agent."""

    def __init__(self, agent_manifest: Dict[str, Any]):
        """Initialize tool manager from agent manifest."""
        self.builtin_tools: Dict[str, BuiltinToolInfo] = {}
        self.disabled_tools: Set[str] = set()
        self._load_builtin_tools_from_manifest(agent_manifest)

    def _load_builtin_tools_from_manifest(self, manifest: Dict[str, Any]) -> None:
        """Load built-in tools from agent.yaml builtin_tools section."""
        builtin_tools_config = manifest.get('builtin_tools', {})

        for tool_name, tool_config in builtin_tools_config.items():
            self.builtin_tools[tool_name] = BuiltinToolInfo(
                name=tool_name,
                description=tool_config.get('description', ''),
                required=tool_config.get('required', False),
                parameters=tool_config.get('parameters', {})
            )

    def disable_builtin_tools(self, tool_names: List[str]) -> None:
        """Disable specified built-in tools."""
        for tool_name in tool_names:
            if tool_name in self.builtin_tools:
                tool_info = self.builtin_tools[tool_name]
                if tool_info.required:
                    raise ValueError(f"Built-in tool '{tool_name}' cannot be disabled (required core functionality)")
                self.disabled_tools.add(tool_name)
                tool_info.enabled = False

    def get_available_tools(self) -> List[str]:
        """Get list of available (enabled) built-in tools."""
        return [name for name, tool in self.builtin_tools.items() if tool.enabled]

    def get_tool_info(self, tool_name: str) -> Optional[BuiltinToolInfo]:
        """Get information about a specific built-in tool."""
        return self.builtin_tools.get(tool_name)

    def validate_tool_parameters(self, tool_name: str, parameters: Dict[str, Any]) -> List[str]:
        """Validate parameters for a built-in tool."""
        tool_info = self.get_tool_info(tool_name)
        if not tool_info:
            return [f"Tool '{tool_name}' not found"]

        errors = []
        tool_params = tool_info.parameters

        for param_name, param_config in tool_params.items():
            if param_config.get('required', False) and param_name not in parameters:
                errors.append(f"Required parameter '{param_name}' is missing")

            if param_name in parameters:
                param_value = parameters[param_name]
                expected_type = param_config.get('type', 'string')

                if not self._validate_parameter_type(param_value, expected_type):
                    errors.append(f"Parameter '{param_name}' should be {expected_type}, got {type(param_value).__name__}")

        return errors

    def _validate_parameter_type(self, value: Any, expected_type: str) -> bool:
        """Validate parameter type."""
        type_mapping = {
            'string': str,
            'integer': int,
            'number': (int, float),
            'boolean': bool,
            'object': dict,
            'array': list
        }

        expected_python_type = type_mapping.get(expected_type, str)
        return isinstance(value, expected_python_type)
```

#### **`agenthub/core/agents/wrapper.py` (Enhanced)**

```python
"""Enhanced agent wrapper with Phase 3 features."""

from typing import Dict, List, Any, Optional, Set
from .tool_manager import AgentToolManager
from ..knowledge import KnowledgeManager
from ..tools import ToolRegistry


class AgentWrapper:
    """Enhanced wrapper for agent operations with Phase 3 features."""

    def __init__(
        self,
        agent_info: Dict[str, Any],
        runtime=None,
        tool_registry: Optional[ToolRegistry] = None
    ):
        """Initialize the enhanced agent wrapper."""
        self.agent_info = agent_info
        self.runtime = runtime
        self.tool_registry = tool_registry

        # Extract key information
        self.name = agent_info.get("name", "unknown")
        self.namespace = agent_info.get("namespace", "unknown")
        self.version = agent_info.get("version", "unknown")
        self.description = agent_info.get("description", "")
        self.path = agent_info.get("path", "")
        self.methods = agent_info.get("methods", [])

        # Initialize managers
        self.tool_manager = AgentToolManager(agent_info.get("manifest", {}))
        self.knowledge_manager = KnowledgeManager()
        self.external_tools: List[str] = []

    def add_external_tools(self, tool_names: List[str]) -> None:
        """Add external tools from user."""
        if self.tool_registry is None:
            raise ValueError("Tool registry not available")

        available_tools = self.tool_registry.get_available_tools()
        invalid_tools = [tool for tool in tool_names if tool not in available_tools]

        if invalid_tools:
            raise ValueError(f"External tools not found: {invalid_tools}. Available: {available_tools}")

        self.external_tools.extend(tool_names)

    def disable_builtin_tools(self, tool_names: List[str]) -> None:
        """Disable specified built-in tools."""
        self.tool_manager.disable_builtin_tools(tool_names)

    def inject_knowledge(self, knowledge_text: str) -> None:
        """Inject knowledge into agent context."""
        self.knowledge_manager.inject_knowledge(knowledge_text)

    def get_available_tools(self) -> List[str]:
        """Get all available tools (enabled built-in + external)."""
        available = self.tool_manager.get_available_tools()
        available.extend(self.external_tools)
        return available

    def get_builtin_tools(self) -> Dict[str, Any]:
        """Get built-in tools information."""
        return {
            name: {
                "description": tool.description,
                "required": tool.required,
                "enabled": tool.enabled,
                "parameters": tool.parameters
            }
            for name, tool in self.tool_manager.builtin_tools.items()
        }

    def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute tool with proper validation and routing."""
        # Check if it's a built-in tool
        if tool_name in self.tool_manager.builtin_tools:
            if not self.tool_manager.builtin_tools[tool_name].enabled:
                raise ValueError(f"Built-in tool '{tool_name}' is disabled")

            # Validate parameters
            errors = self.tool_manager.validate_tool_parameters(tool_name, parameters)
            if errors:
                raise ValueError(f"Tool parameter validation failed: {'; '.join(errors)}")

            # Execute via runtime
            return self.runtime.execute_tool(tool_name, parameters)

        # Check if it's an external tool
        elif tool_name in self.external_tools:
            if self.tool_registry is None:
                raise ValueError("Tool registry not available for external tools")
            return self.tool_registry.execute_tool(tool_name, parameters)

        else:
            raise ValueError(f"Tool '{tool_name}' not found")

    def has_method(self, method_name: str) -> bool:
        """Check if agent has a specific method."""
        return method_name in self.methods

    def get_method_info(self, method_name: str) -> Dict[str, Any]:
        """Get detailed information about a method."""
        manifest = self.agent_info.get("manifest", {})
        interface = manifest.get("interface", {})
        methods = interface.get("methods", {})

        return methods.get(method_name, {})

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation."""
        return {
            "name": self.name,
            "namespace": self.namespace,
            "version": self.version,
            "description": self.description,
            "path": self.path,
            "methods": self.methods,
            "builtin_tools": self.get_builtin_tools(),
            "external_tools": self.external_tools,
            "available_tools": self.get_available_tools(),
            "has_runtime": self.runtime is not None,
            "has_knowledge": self.knowledge_manager.is_knowledge_available()
        }
```

### **3. Knowledge Management Module**

#### **`agenthub/core/knowledge/__init__.py`**

```python
"""Knowledge management system for Phase 3."""

from .manager import KnowledgeManager
from .storage import KnowledgeStorage
from .validator import KnowledgeValidator

__all__ = [
    "KnowledgeManager",
    "KnowledgeStorage",
    "KnowledgeValidator"
]
```

#### **`agenthub/core/knowledge/manager.py`**

```python
"""Knowledge management for agents."""

from typing import Dict, Any, Optional
from .storage import KnowledgeStorage
from .validator import KnowledgeValidator


class KnowledgeManager:
    """Manages knowledge injection and retrieval for agents."""

    def __init__(self):
        """Initialize knowledge manager."""
        self.storage = KnowledgeStorage()
        self.validator = KnowledgeValidator()
        self.knowledge: str = ""
        self.metadata: Dict[str, Any] = {}

    def inject_knowledge(self, knowledge_text: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Inject text-based knowledge into agent context."""
        # Validate knowledge
        validation_result = self.validator.validate_knowledge(knowledge_text)
        if not validation_result.is_valid:
            raise ValueError(f"Knowledge validation failed: {validation_result.errors}")

        self.knowledge = knowledge_text
        self.metadata = metadata or {}

        # Store knowledge
        self.storage.store_knowledge(knowledge_text, self.metadata)

    def get_knowledge(self) -> str:
        """Get injected knowledge."""
        return self.knowledge

    def get_metadata(self) -> Dict[str, Any]:
        """Get knowledge metadata."""
        return self.metadata

    def is_knowledge_available(self) -> bool:
        """Check if knowledge is available."""
        return bool(self.knowledge.strip())

    def clear_knowledge(self) -> None:
        """Clear injected knowledge."""
        self.knowledge = ""
        self.metadata = {}
        self.storage.clear_knowledge()

    def search_knowledge(self, query: str) -> Optional[str]:
        """Search knowledge for relevant information."""
        if not self.is_knowledge_available():
            return None

        # Simple text search - can be enhanced with semantic search
        if query.lower() in self.knowledge.lower():
            return self.knowledge

        return None
```

### **4. Installation Management Module**

#### **`agenthub/core/installation/__init__.py`**

```python
"""Installation management system for Phase 3."""

from .command_executor import CommandExecutor, CommandResult
from .validator import InstallationValidator
from .manager import InstallationManager
from .plugins import PluginManager

__all__ = [
    "CommandExecutor",
    "CommandResult",
    "InstallationValidator",
    "InstallationManager",
    "PluginManager"
]
```

#### **`agenthub/core/installation/command_executor.py`**

```python
"""Command execution engine for installation commands."""

import subprocess
import time
from typing import Dict, Any, List
from dataclasses import dataclass
from .plugins import PluginManager


@dataclass
class CommandResult:
    """Result of command execution."""
    success: bool
    command: str
    stdout: str = ""
    stderr: str = ""
    error: str = ""
    execution_time: float = 0.0


class CommandExecutor:
    """Executes installation commands from agent.yaml."""

    def __init__(self, agent_path: str, venv_path: str):
        """Initialize command executor."""
        self.agent_path = agent_path
        self.venv_path = venv_path
        self.plugin_manager = PluginManager()
        self.environment = self._setup_environment()

    def execute_installation_command(self, command: str) -> CommandResult:
        """Execute a single installation command."""
        start_time = time.time()

        try:
            # Route to appropriate plugin
            plugin = self.plugin_manager.get_plugin_for_command(command)
            if plugin:
                result = plugin.execute(command, self.agent_path, self.venv_path, self.environment)
            else:
                result = self._execute_generic_command(command)

            result.execution_time = time.time() - start_time
            return result

        except Exception as e:
            return CommandResult(
                success=False,
                command=command,
                error=str(e),
                execution_time=time.time() - start_time
            )

    def execute_validation_command(self, command: str) -> CommandResult:
        """Execute a validation command."""
        return self.execute_installation_command(command)

    def _execute_generic_command(self, command: str) -> CommandResult:
        """Execute any generic command."""
        try:
            result = subprocess.run(
                command.split(),
                cwd=self.agent_path,
                env=self.environment,
                capture_output=True,
                text=True,
                timeout=300
            )

            return CommandResult(
                success=result.returncode == 0,
                command=command,
                stdout=result.stdout,
                stderr=result.stderr
            )
        except Exception as e:
            return CommandResult(
                success=False,
                command=command,
                error=str(e)
            )

    def _setup_environment(self) -> Dict[str, str]:
        """Setup environment variables for command execution."""
        import os
        env = os.environ.copy()
        env["VIRTUAL_ENV"] = str(self.venv_path)
        env["PATH"] = f"{self.venv_path}/bin:{env.get('PATH', '')}"
        return env
```

### **5. Enhanced Configuration Module**

#### **`agenthub/config/agent_config.py`**

```python
"""Enhanced agent configuration parsing for Phase 3."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import yaml
from pathlib import Path


@dataclass
class InstallationConfig:
    """Installation configuration from agent.yaml."""
    commands: List[str]
    validation: List[str]


@dataclass
class AgentConfig:
    """Complete agent configuration from agent.yaml."""
    name: str
    version: str
    description: str
    author: str
    license: str
    python_version: str
    interface: Dict[str, Any]
    installation: InstallationConfig
    builtin_tools: Dict[str, Any]
    dependencies: List[str]  # For backward compatibility


class AgentConfigParser:
    """Parse agent.yaml with Phase 3 schema support."""

    def parse_agent_yaml(self, agent_yaml_path: str) -> AgentConfig:
        """Parse agent.yaml with Phase 3 schema support."""
        with open(agent_yaml_path, 'r') as f:
            agent_config = yaml.safe_load(f)

        # Phase 3: Installation commands
        installation_config = agent_config.get('installation', {})
        commands = installation_config.get('commands', [])
        validation = installation_config.get('validation', [])

        # Phase 3: Built-in tools
        builtin_tools = agent_config.get('builtin_tools', {})

        # Backward compatibility: dependencies
        dependencies = agent_config.get('dependencies', [])

        return AgentConfig(
            name=agent_config.get('name', ''),
            version=agent_config.get('version', ''),
            description=agent_config.get('description', ''),
            author=agent_config.get('author', ''),
            license=agent_config.get('license', ''),
            python_version=agent_config.get('python_version', '3.11+'),
            interface=agent_config.get('interface', {}),
            installation=InstallationConfig(commands=commands, validation=validation),
            builtin_tools=builtin_tools,
            dependencies=dependencies
        )

    def validate_config(self, config: AgentConfig) -> List[str]:
        """Validate agent configuration."""
        errors = []

        # Validate required fields
        if not config.name:
            errors.append("Agent name is required")

        if not config.version:
            errors.append("Agent version is required")

        # Validate installation commands
        if not config.installation.commands:
            errors.append("At least one installation command is required")

        # Validate built-in tools
        for tool_name, tool_config in config.builtin_tools.items():
            if not tool_config.get('description'):
                errors.append(f"Built-in tool '{tool_name}' must have a description")

        return errors
```

## 🚀 **Implementation Benefits**

### **1. Clean Architecture**

- **Single Responsibility**: Each module has one clear purpose
- **Loose Coupling**: Modules interact through well-defined interfaces
- **High Cohesion**: Related functionality is grouped together
- **Easy Testing**: Each module can be tested independently

### **2. Scalability**

- **Plugin Architecture**: Easy to add new installation methods
- **Modular Design**: New features can be added without breaking existing code
- **Configuration-Driven**: Behavior controlled by YAML configuration
- **Performance Optimized**: Efficient for common use cases

### **3. User Experience**

- **Simple API**: Users only need to know `load_agent()` function
- **Progressive Disclosure**: Advanced features available when needed
- **Clear Error Messages**: Helpful suggestions for fixing issues
- **Backward Compatibility**: Existing code continues to work

### **4. Maintainability**

- **Clear Separation**: Business logic separated from infrastructure
- **Consistent Patterns**: Similar patterns used throughout
- **Comprehensive Testing**: Each module thoroughly tested
- **Documentation**: Clear documentation for each component

## 📋 **Migration Strategy**

### **Phase 1: Core Infrastructure (Weeks 1-2)**

1. Create new module structure
2. Implement core classes (AgentConfig, CommandExecutor, etc.)
3. Add comprehensive tests
4. Maintain backward compatibility

### **Phase 2: Enhanced Features (Weeks 3-4)**

1. Implement tool management system
2. Add knowledge management
3. Enhance error handling
4. Update SDK interface

### **Phase 3: Integration & Polish (Weeks 5-6)**

1. Integrate all components
2. Performance optimization
3. Documentation updates
4. Migration examples

## 🎯 **Success Metrics**

- **Code Quality**: 90%+ test coverage, clean architecture principles
- **Performance**: <2s agent loading, <500ms tool execution
- **User Experience**: 90%+ users can configure agents without documentation
- **Maintainability**: New features can be added in <1 day
- **Scalability**: Support for 100+ concurrent agents

---

**This refined modular design provides a clean, scalable, and maintainable architecture that makes AgentHub production-ready while maintaining simplicity for end users.**
