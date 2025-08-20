"""
Custom Method Manager for Agent Hub

Simplified, secure method injection system.
"""

import os
import json
import time
import hashlib
import logging
import tempfile
from pathlib import Path
from typing import Dict, Any, Callable, Optional
from dataclasses import dataclass, asdict

from agentmanager.validation.method_validator import MethodValidator, ValidationResult
from .exceptions import MethodValidationError, MethodNotFoundError, MethodSecurityError

logger = logging.getLogger(__name__)


@dataclass
class MethodInfo:
    """Information about a custom method."""
    name: str
    language: str
    implementation: str
    injected_at: float
    checksum: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class CustomMethodManager:
    """Manages injection and execution of custom methods."""
    
    def __init__(self, base_path: Optional[str] = None, security_level: str = "medium"):
        """Initialize the custom method manager."""
        self.base_path = Path(base_path) if base_path else Path.home() / ".agenthub" / "custom_methods"
        self.security_level = security_level
        self.validator = MethodValidator(security_level)
        
        # Supported languages
        self.supported_languages = {"python", "javascript", "shell", "bash"}
        
        # Create base directory
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"CustomMethodManager initialized with base_path: {self.base_path}")

    def inject_method(self, agent_path: str, method_name: str, implementation: Any, language: str = "python") -> None:
        """
        Inject a custom method for an agent.
        
        Args:
            agent_path: Path to the agent (e.g., "agentplug/coding-agent")
            method_name: Name of the method
            implementation: Method implementation (function or string)
            language: Programming language
        """
        # Validate inputs
        if not agent_path or not method_name:
            raise ValueError("agent_path and method_name are required")
        
        if implementation is None:
            raise ValueError("agent_path and method_name are required")
        
        if language not in self.supported_languages:
            raise ValueError(f"Unsupported language: {language}")
        
        if not method_name.isidentifier():
            raise ValueError(f"Invalid method name: {method_name}")
        
        # Convert implementation to string
        if callable(implementation):
            # Store the original function for direct execution
            self._stored_functions = getattr(self, '_stored_functions', {})
            func_key = f"{agent_path}:{method_name}"
            self._stored_functions[func_key] = implementation
            
            # Try to get source, otherwise use placeholder
            try:
                implementation_str = self._get_function_source(implementation)
            except Exception:
                implementation_str = f"# Callable function: {implementation.__name__}"
        else:
            implementation_str = str(implementation)
        
        # Validate implementation
        validation_result = self.validator.validate_method(implementation_str, language)
        if not validation_result.is_valid:
            raise MethodValidationError(f"Method validation failed: {validation_result.errors}")
        
        # Calculate checksum
        checksum = self._calculate_checksum(implementation_str)
        
        # Create method info
        method_info = MethodInfo(
            name=method_name,
            language=language,
            implementation=implementation_str,
            injected_at=time.time(),
            checksum=checksum,
            metadata=self._extract_metadata(implementation, language)
        )
        
        # Save method
        self._save_method(agent_path, method_info)
        
        logger.info(f"Injected method '{method_name}' for agent '{agent_path}'")

    def get_method(self, agent_path: str, method_name: str) -> Callable:
        """Get a custom method for execution."""
        method_info = self.get_method_info(agent_path, method_name)
        if not method_info:
            raise MethodNotFoundError(f"Method '{method_name}' not found for agent '{agent_path}'")
        
        # Check if we have a stored function first (for callable injections)
        func_key = f"{agent_path}:{method_name}"
        stored_functions = getattr(self, '_stored_functions', {})
        if func_key in stored_functions:
            return stored_functions[func_key]
        
        # Verify integrity
        current_checksum = self._calculate_checksum(method_info.implementation)
        if current_checksum != method_info.checksum:
            raise MethodSecurityError("Method integrity check failed")
        
        # Create executable function
        if method_info.language == "python":
            return self._create_python_function(method_info)
        else:
            return self._create_wrapper_function(method_info)

    def get_method_info(self, agent_path: str, method_name: str) -> Optional[MethodInfo]:
        """Get information about a custom method."""
        method_file = self._get_method_file_path(agent_path, method_name)
        if not method_file.exists():
            return None
        
        try:
            with open(method_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return MethodInfo(**data)
        except Exception as e:
            logger.error(f"Failed to load method info: {e}")
            return None

    def list_methods(self, agent_path: str) -> Dict[str, MethodInfo]:
        """List all custom methods for an agent."""
        agent_dir = self.base_path / agent_path.replace("/", os.sep)
        if not agent_dir.exists():
            return {}
        
        methods = {}
        for method_file in agent_dir.glob("*.json"):
            method_name = method_file.stem
            method_info = self.get_method_info(agent_path, method_name)
            if method_info:
                methods[method_name] = method_info
        
        return methods

    def remove_method(self, agent_path: str, method_name: str) -> None:
        """Remove a custom method."""
        method_file = self._get_method_file_path(agent_path, method_name)
        if method_file.exists():
            method_file.unlink()
            
            # Also remove any stored function
            func_key = f"{agent_path}:{method_name}"
            stored_functions = getattr(self, '_stored_functions', {})
            if func_key in stored_functions:
                del stored_functions[func_key]
            
            logger.info(f"Removed method '{method_name}' from agent '{agent_path}'")

    def validate_method_exists(self, agent_path: str, method_name: str) -> bool:
        """Check if a method exists."""
        return self._get_method_file_path(agent_path, method_name).exists()

    def get_method_context(self, agent_path: str) -> Dict[str, Any]:
        """
        Get the execution context for custom methods of an agent.
        This includes a list of available methods and their basic info.
        """
        methods = self.list_methods(agent_path)
        context_methods = {}
        for name, info in methods.items():
            context_methods[name] = {
                "language": info.language,
                "injected_at": info.injected_at,
                "metadata": info.metadata,
                "security_score": info.metadata.get("security_score", "unknown")
            }
        return {
            "methods": context_methods,
            "total_methods": len(methods),
            "base_path": str(self.base_path),
            "agent_path": agent_path
        }

    def cleanup_expired_methods(self, max_age_hours: int = 24) -> int:
        """Clean up expired methods."""
        cutoff_time = time.time() - (max_age_hours * 3600)
        cleaned_count = 0
        
        # Recursively find all JSON files
        for method_file in self.base_path.rglob("*.json"):
            try:
                with open(method_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if data.get('injected_at', 0) < cutoff_time:
                    method_file.unlink()
                    cleaned_count += 1
                    logger.info(f"Cleaned up expired method: {method_file}")
            except Exception as e:
                logger.warning(f"Failed to process {method_file}: {e}")
        
        return cleaned_count

    def _get_method_file_path(self, agent_path: str, method_name: str) -> Path:
        """Get the file path for a method."""
        safe_agent_path = agent_path.replace("/", os.sep)
        agent_dir = self.base_path / safe_agent_path
        return agent_dir / f"{method_name}.json"

    def _save_method(self, agent_path: str, method_info: MethodInfo) -> None:
        """Save method information to file."""
        method_file = self._get_method_file_path(agent_path, method_info.name)
        method_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(method_file, 'w', encoding='utf-8') as f:
            json.dump(method_info.to_dict(), f, indent=2)

    def _calculate_checksum(self, content: str) -> str:
        """Calculate SHA256 checksum of content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def _get_function_source(self, func: Callable) -> str:
        """Get source code of a function."""
        try:
            return inspect.getsource(func)
        except Exception:
            # If we can't get source, try to recreate from signature
            try:
                sig = inspect.signature(func)
                params = []
                for name, param in sig.parameters.items():
                    if param.annotation != param.empty:
                        if param.default != param.empty:
                            params.append(f"{name}: {param.annotation.__name__} = {repr(param.default)}")
                        else:
                            params.append(f"{name}: {param.annotation.__name__}")
                    else:
                        if param.default != param.empty:
                            params.append(f"{name} = {repr(param.default)}")
                        else:
                            params.append(name)
                
                param_str = ", ".join(params)
                return f"def {func.__name__}({param_str}):\n    # Function implementation not available\n    pass"
            except Exception:
                # Last resort
                return f"def {func.__name__}(*args, **kwargs):\n    # Function implementation not available\n    pass"

    def _extract_metadata(self, implementation: Any, language: str) -> Dict[str, Any]:
        """Extract metadata from implementation."""
        metadata = {
            "language": language,
            "size_bytes": len(str(implementation)),
            "extracted_at": time.time()
        }
        
        if callable(implementation):
            try:
                sig = inspect.signature(implementation)
                metadata["parameters"] = list(sig.parameters.keys())
                metadata["docstring"] = implementation.__doc__ or ""
            except Exception as e:
                # If we can't get signature, try to extract from source
                try:
                    source = self._get_function_source(implementation)
                    # Simple extraction of function parameters from source
                    import re
                    match = re.search(r'def\s+\w+\s*\(([^)]*)\)', source)
                    if match:
                        params_str = match.group(1)
                        params = [p.split(':')[0].split('=')[0].strip() for p in params_str.split(',') if p.strip()]
                        metadata["parameters"] = [p for p in params if p and p != 'self']
                except Exception:
                    metadata["parameters"] = []
        
        return metadata

    def _create_python_function(self, method_info: MethodInfo) -> Callable:
        """Create an executable Python function."""
        # Create a safe execution environment
        safe_globals = {
            '__builtins__': {
                'len': len, 'str': str, 'int': int, 'float': float, 'bool': bool,
                'list': list, 'dict': dict, 'tuple': tuple, 'set': set,
                'min': min, 'max': max, 'sum': sum, 'abs': abs,
                'print': print, 'range': range, 'enumerate': enumerate,
                'zip': zip, 'map': map, 'filter': filter,
                'ValueError': ValueError, 'TypeError': TypeError, 'KeyError': KeyError,
                'IndexError': IndexError, 'AttributeError': AttributeError,
                'round': round, 'sorted': sorted, 'reversed': reversed,
                '__import__': __import__, 'isinstance': isinstance, 'hasattr': hasattr,
            }
        }
        
        try:
            # Execute the code
            exec(method_info.implementation, safe_globals)
            
            # Find the function in the executed code
            for name, obj in safe_globals.items():
                if callable(obj) and not name.startswith('_') and name != '__builtins__':
                    return obj
            
            # If no function found, try to find it by method name
            if method_info.name in safe_globals and callable(safe_globals[method_info.name]):
                return safe_globals[method_info.name]
            
            raise ValueError("No callable function found in implementation")
        except Exception as e:
            raise MethodValidationError(f"Failed to create Python function: {e}")

    def _create_wrapper_function(self, method_info: MethodInfo) -> Callable:
        """Create a wrapper function for non-Python implementations."""
        def wrapper(*args, **kwargs):
            if method_info.language in ["javascript", "js"]:
                return self._execute_javascript(method_info.implementation, args, kwargs)
            elif method_info.language in ["shell", "bash"]:
                return self._execute_shell(method_info.implementation, args, kwargs)
            else:
                raise ValueError(f"Unsupported language: {method_info.language}")
        
        return wrapper

    def _execute_javascript(self, implementation: str, args: tuple, kwargs: dict) -> Any:
        """Execute JavaScript implementation."""
        # This is a simplified version - in production, you'd use a proper JS runtime
        raise NotImplementedError("JavaScript execution not implemented in this simplified version")

    def _execute_shell(self, implementation: str, args: tuple, kwargs: dict) -> Any:
        """Execute shell implementation."""
        # This is a simplified version - in production, you'd use proper shell execution
        raise NotImplementedError("Shell execution not implemented in this simplified version")