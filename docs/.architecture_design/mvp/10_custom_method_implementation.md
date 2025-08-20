# Custom Method Injection Implementation Plan

**Document Type**: Implementation Design  
**Author**: William  
**Date Created**: 2025-06-28  
**Last Updated**: 2025-06-28  
**Status**: Draft  
**Level**: L4 - Implementation Level  
**Audience**: Development Team, Implementation Engineers

## 🎯 **Overview**

This document outlines the **code implementation plan** for extending Agent Hub to support custom method injection, allowing users to pass in method implementations in any language for agents to invoke.

## 🏗️ **Architecture Changes**

### **1. Enhanced Process Manager**

```python
# agentmanager/runtime/process_manager.py
class ProcessManager:
    def __init__(self, timeout: int = 300):
        self.timeout = timeout
        self.environment_manager = EnvironmentManager()
        self.custom_method_manager = CustomMethodManager()  # NEW

    def execute_agent(self, agent_path: str, method: str, parameters: dict, custom_methods: dict = None) -> dict:
        """Execute agent method with custom method support."""
        if not agent_path or not method:
            raise ValueError("agent_path and method are required")

        # NEW: Inject custom methods if provided
        if custom_methods:
            self.custom_method_manager.inject_methods(agent_path, custom_methods)

        # Rest of existing implementation...
        agent_dir = Path(agent_path)
        if not agent_dir.exists():
            raise ValueError(f"Agent directory does not exist: {agent_path}")

        agent_script = agent_dir / "agent.py"
        if not agent_script.exists():
            raise ValueError(f"Agent script not found: {agent_script}")

        # Prepare execution data with custom method context
        execution_data = {
            "method": method, 
            "parameters": parameters,
            "custom_methods": self.custom_method_manager.get_method_context(agent_path)  # NEW
        }

        try:
            # Get Python executable for this agent's virtual environment
            python_executable = self.environment_manager.get_python_executable(agent_path)

            # Execute agent in subprocess with custom method support
            start_time = time.time()
            result = subprocess.run(
                [python_executable, str(agent_script), json.dumps(execution_data)],
                cwd=str(agent_dir),
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env=self._prepare_environment_with_custom_methods(agent_path, custom_methods)  # NEW
            )
            execution_time = time.time() - start_time

            # Parse the result
            if result.returncode == 0:
                try:
                    parsed_result = json.loads(result.stdout)
                    parsed_result["execution_time"] = execution_time
                    return parsed_result
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse agent output: {result.stdout}")
                    return {
                        "error": f"Invalid JSON response from agent: {e}",
                        "raw_output": result.stdout,
                        "execution_time": execution_time,
                    }
            else:
                error_msg = result.stderr or result.stdout or "Unknown error"
                return {
                    "error": f"Agent execution failed: {error_msg}",
                    "return_code": result.returncode,
                    "execution_time": execution_time,
                }

        except subprocess.TimeoutExpired:
            return {
                "error": f"Agent execution timed out after {self.timeout} seconds",
                "timeout": self.timeout,
            }
        except FileNotFoundError as e:
            raise RuntimeError(f"Failed to execute agent: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error executing agent: {e}")
            return {"error": f"Unexpected execution error: {e}"}

    def _prepare_environment_with_custom_methods(self, agent_path: str, custom_methods: dict) -> dict:
        """Prepare environment variables for custom method execution."""
        env = os.environ.copy()
        
        if custom_methods:
            # Set custom method context
            env["AGENT_CUSTOM_METHODS"] = json.dumps(custom_methods)
            env["AGENT_CUSTOM_METHODS_PATH"] = str(self.custom_method_manager.get_methods_path(agent_path))
        
        return env
```

### **2. Custom Method Manager (NEW)**

```python
# agentmanager/core/custom_method_manager.py
import os
import json
import time
import inspect
from pathlib import Path
from typing import Dict, Any, Callable, Optional
from .method_validator import MethodValidator
from .exceptions import MethodValidationError, MethodNotFoundError

class CustomMethodManager:
    """Manages custom method injection and execution."""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path.home() / ".agenthub" / "custom_methods"
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.method_validator = MethodValidator()
        self.active_methods: Dict[str, Dict[str, Any]] = {}

    def inject_method(self, agent_path: str, method_name: str, implementation: Any, language: str = "python") -> None:
        """Inject a custom method for an agent."""
        # Validate method implementation
        validation_result = self.method_validator.validate_method(implementation, language)
        if not validation_result.is_valid:
            raise MethodValidationError(f"Method validation failed: {validation_result.errors}")

        # Create method directory
        method_dir = self.base_path / agent_path.replace("/", "_") / method_name
        method_dir.mkdir(parents=True, exist_ok=True)

        # Store method implementation
        method_info = {
            "name": method_name,
            "language": language,
            "implementation": self._serialize_implementation(implementation, language),
            "injected_at": time.time(),
            "metadata": self._extract_metadata(implementation, language)
        }

        # Save to disk
        method_file = method_dir / f"{method_name}.json"
        with open(method_file, 'w') as f:
            json.dump(method_info, f, indent=2)

        # Store in memory
        self.active_methods[f"{agent_path}:{method_name}"] = method_info

        logger.info(f"Injected custom method '{method_name}' for agent '{agent_path}'")

    def get_method(self, agent_path: str, method_name: str) -> Any:
        """Get a custom method implementation."""
        key = f"{agent_path}:{method_name}"
        if key not in self.active_methods:
            raise MethodNotFoundError(f"Custom method '{method_name}' not found for agent '{agent_path}'")
        
        method_info = self.active_methods[key]
        return self._deserialize_implementation(method_info["implementation"], method_info["language"])

    def list_methods(self, agent_path: str) -> Dict[str, Any]:
        """List all custom methods for an agent."""
        methods = {}
        agent_methods_dir = self.base_path / agent_path.replace("/", "_")
        
        if agent_methods_dir.exists():
            for method_dir in agent_methods_dir.iterdir():
                if method_dir.is_dir():
                    method_file = method_dir / f"{method_dir.name}.json"
                    if method_file.exists():
                        with open(method_file) as f:
                            methods[method_dir.name] = json.load(f)
        
        return methods

    def remove_method(self, agent_path: str, method_name: str) -> None:
        """Remove a custom method."""
        key = f"{agent_path}:{method_name}"
        if key in self.active_methods:
            del self.active_methods[key]

        # Remove from disk
        method_dir = self.base_path / agent_path.replace("/", "_") / method_name
        if method_dir.exists():
            import shutil
            shutil.rmtree(method_dir)

        logger.info(f"Removed custom method '{method_name}' for agent '{agent_path}'")

    def get_method_context(self, agent_path: str) -> dict:
        """Get execution context for custom methods."""
        methods = self.list_methods(agent_path)
        return {
            "methods": list(methods.keys()),
            "methods_path": str(self.base_path / agent_path.replace("/", "_")),
            "available_languages": list(set(m["language"] for m in methods.values()))
        }

    def _serialize_implementation(self, implementation: Any, language: str) -> str:
        """Serialize method implementation for storage."""
        if language == "python":
            if callable(implementation):
                return inspect.getsource(implementation)
            else:
                return str(implementation)
        elif language == "javascript":
            return str(implementation)
        elif language == "shell":
            return str(implementation)
        else:
            return str(implementation)

    def _deserialize_implementation(self, serialized: str, language: str) -> Any:
        """Deserialize method implementation from storage."""
        if language == "python":
            # Create a temporary module and execute the code
            import types
            module = types.ModuleType("custom_method")
            exec(serialized, module.__dict__)
            
            # Find the function (assuming it's the first function defined)
            for name, obj in module.__dict__.items():
                if callable(obj) and not name.startswith('_'):
                    return obj
            return None
        else:
            return serialized

    def _extract_metadata(self, implementation: Any, language: str) -> dict:
        """Extract metadata from method implementation."""
        metadata = {"language": language}
        
        if language == "python" and callable(implementation):
            sig = inspect.signature(implementation)
            metadata["parameters"] = list(sig.parameters.keys())
            metadata["docstring"] = implementation.__doc__ or ""
        
        return metadata
```

### **3. Method Validator (NEW)**

```python
# agentmanager/validation/method_validator.py
import inspect
import re
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class ValidationResult:
    is_valid: bool = True
    errors: List[str] = None
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []
    
    def add_error(self, error: str):
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str):
        self.warnings.append(warning)
    
    def merge(self, other: 'ValidationResult'):
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        if not other.is_valid:
            self.is_valid = False

class MethodValidator:
    """Validates custom method implementations for safety and compatibility."""
    
    def __init__(self, security_level: str = "medium"):
        self.security_level = security_level
        self.security_patterns = self._load_security_patterns()
    
    def validate_method(self, implementation: Any, language: str) -> ValidationResult:
        """Validate custom method implementation."""
        result = ValidationResult()
        
        # Language-specific validation
        if language == "python":
            result.merge(self._validate_python_method(implementation))
        elif language == "javascript":
            result.merge(self._validate_javascript_method(implementation))
        elif language == "shell":
            result.merge(self._validate_shell_method(implementation))
        else:
            result.merge(self._validate_generic_method(implementation, language))
        
        # Security validation
        result.merge(self._validate_security(implementation, language))
        
        # Resource validation
        result.merge(self._validate_resources(implementation, language))
        
        return result
    
    def _validate_python_method(self, implementation: Any) -> ValidationResult:
        """Validate Python method implementation."""
        result = ValidationResult()
        
        # Check if it's callable
        if not callable(implementation):
            result.add_error("Python method must be callable")
            return result
        
        # Check for dangerous patterns
        try:
            source_code = inspect.getsource(implementation)
            for pattern in self.security_patterns["python"]["dangerous"]:
                if pattern in source_code:
                    result.add_warning(f"Potentially dangerous pattern detected: {pattern}")
        except Exception:
            result.add_warning("Could not inspect source code for validation")
        
        # Check function signature
        try:
            sig = inspect.signature(implementation)
            if len(sig.parameters) > 10:
                result.add_warning("Method has many parameters, consider simplifying")
        except Exception:
            result.add_warning("Could not inspect function signature")
        
        return result
    
    def _validate_javascript_method(self, implementation: str) -> ValidationResult:
        """Validate JavaScript method implementation."""
        result = ValidationResult()
        
        if not isinstance(implementation, str):
            result.add_error("JavaScript method must be a string")
            return result
        
        # Check for dangerous patterns
        for pattern in self.security_patterns["javascript"]["dangerous"]:
            if pattern in implementation:
                result.add_warning(f"Potentially dangerous pattern detected: {pattern}")
        
        # Check for dangerous functions
        dangerous_functions = ["eval", "Function", "setTimeout", "setInterval"]
        for func in dangerous_functions:
            if func in implementation:
                result.add_error(f"Dangerous JavaScript function detected: {func}")
        
        return result
    
    def _validate_shell_method(self, implementation: str) -> ValidationResult:
        """Validate shell script method implementation."""
        result = ValidationResult()
        
        if not isinstance(implementation, str):
            result.add_error("Shell method must be a string")
            return result
        
        # Check for dangerous commands
        dangerous_commands = ["rm -rf", "dd", "format", "fdisk"]
        for cmd in dangerous_commands:
            if cmd in implementation:
                result.add_error(f"Dangerous shell command detected: {cmd}")
        
        # Check for proper quoting
        if "'" in implementation and '"' in implementation:
            result.add_warning("Mixed quotes detected, ensure proper escaping")
        
        return result
    
    def _validate_generic_method(self, implementation: Any, language: str) -> ValidationResult:
        """Validate generic method implementation."""
        result = ValidationResult()
        result.add_warning(f"Generic validation for language: {language}")
        return result
    
    def _validate_security(self, implementation: Any, language: str) -> ValidationResult:
        """Validate security aspects of method implementation."""
        result = ValidationResult()
        
        # Check for file system access
        if isinstance(implementation, str):
            if "file://" in implementation or "file:///" in implementation:
                result.add_warning("File system access detected")
        
        # Check for network access
        if isinstance(implementation, str):
            if "http://" in implementation or "https://" in implementation:
                result.add_warning("Network access detected")
        
        return result
    
    def _validate_resources(self, implementation: Any, language: str) -> ValidationResult:
        """Validate resource usage of method implementation."""
        result = ValidationResult()
        
        # Check for potential infinite loops
        if isinstance(implementation, str):
            if "while True" in implementation or "for i in range(1000000)" in implementation:
                result.add_warning("Potential resource-intensive operation detected")
        
        return result
    
    def _load_security_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Load security patterns for different languages."""
        return {
            "python": {
                "dangerous": [
                    "exec(", "eval(", "os.system(", "subprocess.call(",
                    "__import__(", "globals()", "locals()"
                ]
            },
            "javascript": {
                "dangerous": [
                    "eval(", "Function(", "setTimeout(", "setInterval(",
                    "document.write(", "innerHTML"
                ]
            },
            "shell": {
                "dangerous": [
                    "rm -rf", "dd", "format", "fdisk", "mkfs",
                    "chmod 777", "chown root"
                ]
            }
        }
```

### **4. Enhanced Agent Wrapper**

```python
# agentmanager/core/agent_wrapper.py
class AgentWrapper:
    def __init__(self, agent_info: dict, runtime=None, custom_methods: dict = None):
        """Initialize agent wrapper with custom method support."""
        self.agent_info = agent_info
        self.runtime = runtime
        self.interface_validator = InterfaceValidator()
        self.custom_methods = custom_methods or {}  # NEW

        # Extract key information for easy access
        self.name = agent_info.get("name", "unknown")
        self.namespace = agent_info.get("namespace", "unknown")
        self.agent_name = agent_info.get("agent_name", "unknown")
        self.path = agent_info.get("path", "")
        self.version = agent_info.get("version", "unknown")
        self.description = agent_info.get("description", "")
        self.methods = agent_info.get("methods", [])
        self.dependencies = agent_info.get("dependencies", [])

        # Extract interface for method operations
        self.manifest = agent_info.get("manifest", {})
        self.interface = self.manifest.get("interface", {})

        # NEW: Add custom methods to available methods
        if self.custom_methods:
            self.methods.extend(list(self.custom_methods.keys()))

    def execute(self, method_name: str, parameters: dict) -> dict:
        """Execute an agent method with custom method support."""
        if not self.runtime:
            raise AgentExecutionError("No runtime provided for agent execution")

        if not self.has_method(method_name):
            available = ", ".join(self.methods) if self.methods else "none"
            raise AgentExecutionError(
                f"Method '{method_name}' not available in agent '{self.name}'. "
                f"Available methods: {available}"
            )

        try:
            # NEW: Pass custom methods to runtime
            result = self.runtime.execute_agent(
                self.namespace, 
                self.agent_name, 
                method_name, 
                parameters,
                custom_methods=self.custom_methods  # NEW
            )
            return result
        except Exception as e:
            raise AgentExecutionError(f"Failed to execute {method_name}: {e}") from e

    def inject_custom_method(self, method_name: str, implementation: Any, language: str = "python") -> None:
        """Inject a custom method for the agent to use."""
        if not self.runtime:
            raise AgentExecutionError("No runtime provided for custom method injection")
        
        # Use runtime's custom method manager
        if hasattr(self.runtime, 'custom_method_manager'):
            self.runtime.custom_method_manager.inject_method(
                f"{self.namespace}/{self.agent_name}",
                method_name,
                implementation,
                language
            )
            # Update local methods list
            if method_name not in self.methods:
                self.methods.append(method_name)
            # Update custom methods dict
            self.custom_methods[method_name] = {
                "implementation": implementation,
                "language": language
            }
        else:
            raise AgentExecutionError("Runtime does not support custom method injection")

    def list_methods(self) -> dict:
        """List all available methods (built-in + custom)."""
        return {
            "builtin": [m for m in self.methods if m not in self.custom_methods],
            "custom": self.custom_methods,
            "all": self.methods
        }
```

### **5. Enhanced Public API**

```python
# agentmanager/__init__.py
def load_agent(agent_name, setup_environment=True, custom_methods=None):
    """
    Load an agent with optional custom method injection.
    
    Args:
        agent_name (str): Agent name in format "developer/agent"
        setup_environment (bool): Whether to set up virtual environment
        custom_methods (dict): Optional custom methods to inject
        
    Returns:
        AgentWrapper: Wrapped agent ready for method execution
    """
    # Parse agent name
    if "/" not in agent_name:
        raise ValueError(f"Invalid agent name format: {agent_name}. Expected: 'developer/agent'")

    developer, agent = agent_name.split("/", 1)

    # Initialize managers
    storage_manager = LocalStorage()
    runtime_manager = AgentRuntime(storage_manager)
    loader = AgentLoader(storage_manager)

    # Check if agent exists
    if not storage_manager.agent_exists(developer, agent):
        print(f"📥 Agent '{agent_name}' not found. Installing automatically...")
        
        from agentmanager.github.auto_installer import AutoInstaller
        installer = AutoInstaller(setup_environment=setup_environment)
        result = installer.install_agent(agent_name)

        if not result.success:
            raise RuntimeError(f"Failed to install agent '{agent_name}': {result.error_message}")

        print(f"✅ Agent '{agent_name}' installed successfully!")

    # Load the agent
    agent_data = loader.load_agent(developer, agent)
    agent_wrapper = AgentWrapper(agent_data, runtime=runtime_manager, custom_methods=custom_methods)

    return agent_wrapper
```

## 🚀 **Usage Examples**

### **Basic Custom Method Injection**

```python
import agentmanager as amg

# Define custom methods
def custom_code_analyzer(code: str) -> dict:
    """Custom code analysis implementation."""
    return {
        "complexity": len(code.split('\n')),
        "analysis": "Custom analysis result"
    }

def shell_data_processor(input_file: str) -> str:
    """Shell script for data processing."""
    return f"#!/bin/bash\ncat {input_file} | wc -l"

# Load agent with custom methods
agent = amg.load_agent("agentplug/coding-agent",
    custom_methods={
        "custom_analyzer": custom_code_analyzer,
        "data_processor": shell_data_processor
    }
)

# Use custom methods
result = agent.custom_analyzer("def test(): pass")
print(result)  # {'complexity': 1, 'analysis': 'Custom analysis result'}

# Use built-in methods
code = agent.generate_code("Create a neural network class")
```

### **CLI Usage**

```bash
# Inject a custom method
agenthub inject-method agentplug/coding-agent custom_analyzer custom_analyzer.py --language python

# List all methods
agenthub list-methods agentplug/coding-agent

# Remove a custom method
agenthub remove-method agentplug/coding-agent custom_analyzer
```

## 🔒 **Security Considerations**

1. **Method Validation**: All custom methods are validated for dangerous patterns
2. **Process Isolation**: Custom methods run in isolated subprocesses
3. **Resource Limits**: Execution timeouts and memory limits
4. **File System Access**: Restricted access to prevent malicious operations
5. **Network Access**: Controlled network access for security

## 🧪 **Testing Strategy**

1. **Unit Tests**: Test each component in isolation
2. **Integration Tests**: Test method injection and execution flow
3. **Security Tests**: Test validation and security measures
4. **Performance Tests**: Test method execution overhead
5. **Cross-Language Tests**: Test different programming language support

## 📋 **Implementation Checklist**

- [ ] Custom Method Manager implementation
- [ ] Method Validator implementation
- [ ] Enhanced Process Manager
- [ ] Enhanced Agent Wrapper
- [ ] Enhanced Public API
- [ ] CLI commands for method management
- [ ] Unit tests for all components
- [ ] Integration tests
- [ ] Security validation tests
- [ ] Documentation and examples

This implementation plan provides a comprehensive approach to extending Agent Hub with custom method injection capabilities while maintaining security, performance, and usability.
