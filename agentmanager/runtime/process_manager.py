"""Process manager for executing agents in isolated subprocesses."""

import json
import logging
import subprocess
import time
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, Optional

from agentmanager.runtime.environment_manager import EnvironmentManager
from agentmanager.core.custom_method_manager import CustomMethodManager
from agentmanager.core.exceptions import MethodNotFoundError, MethodExecutionError

logger = logging.getLogger(__name__)


class ProcessManager:
    """Manages agent subprocess execution with isolation."""

    def __init__(self, timeout: int = 300, custom_method_manager: CustomMethodManager = None):
        """
        Initialize the process manager.

        Args:
            timeout: Maximum execution time in seconds
            custom_method_manager: Optional custom method manager for method injection
        """
        self.timeout = timeout
        self.environment_manager = EnvironmentManager()
        self.custom_method_manager = custom_method_manager or CustomMethodManager()

    def execute_agent(self, agent_path: str, method: str, parameters: dict) -> dict:
        """
        Execute an agent method in an isolated subprocess.

        Args:
            agent_path: Path to the agent directory
            method: Name of the method to execute
            parameters: Dictionary of method parameters

        Returns:
            dict: Execution result with 'result' or 'error' key

        Raises:
            ValueError: If agent_path or method is invalid
            RuntimeError: If subprocess creation fails
        """
        if not agent_path or not method:
            raise ValueError("agent_path and method are required")

        # Check if this is a custom method
        if self.custom_method_manager.validate_method_exists(agent_path, method):
            return self._execute_custom_method(agent_path, method, parameters)

        # Execute built-in agent method
        return self._execute_builtin_method(agent_path, method, parameters)

    def _execute_custom_method(self, agent_path: str, method: str, parameters: dict) -> dict:
        """
        Execute a custom injected method.
        
        Args:
            agent_path: Path to the agent directory
            method: Name of the custom method
            parameters: Dictionary of method parameters
            
        Returns:
            dict: Execution result
        """
        try:
            # Get the custom method implementation
            method_impl = self.custom_method_manager.get_method(agent_path, method)
            method_info = self.custom_method_manager.get_method_info(agent_path, method)
            
            if not method_impl:
                raise MethodExecutionError(f"Could not load custom method implementation: {method}")
            
            # Execute based on language
            if method_info.language == "python":
                return self._execute_python_custom_method(method_impl, parameters, method_info)
            elif method_info.language in ["shell", "bash"]:
                return self._execute_shell_custom_method(method_impl, parameters, method_info)
            elif method_info.language == "javascript":
                return self._execute_javascript_custom_method(method_impl, parameters, method_info)
            else:
                raise MethodExecutionError(f"Unsupported language for custom method: {method_info.language}")
                
        except Exception as e:
            logger.error(f"Failed to execute custom method '{method}': {e}")
            return {
                "error": f"Custom method execution failed: {str(e)}",
                "method_name": method,
                "agent_path": agent_path,
                "execution_time": 0
            }

    def _execute_python_custom_method(self, method_impl: Any, parameters: dict, method_info: Any) -> dict:
        """Execute a Python custom method."""
        start_time = time.time()
        
        try:
            # Execute the method with parameters
            if callable(method_impl):
                result = method_impl(**parameters)
            else:
                # If it's a string, execute it in a restricted environment
                result = self._execute_python_string(method_impl, parameters)
            
            execution_time = time.time() - start_time
            
            return {
                "result": result,
                "method_type": "custom_python",
                "execution_time": execution_time,
                "language": method_info.language,
                "security_score": getattr(method_info, 'security_score', 'unknown')
            }
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Python custom method execution failed: {e}")
            return {
                "error": f"Python custom method execution failed: {str(e)}",
                "method_type": "custom_python",
                "execution_time": execution_time,
                "language": method_info.language
            }

    def _execute_shell_custom_method(self, method_impl: str, parameters: dict, method_info: Any) -> dict:
        """Execute a shell script custom method."""
        start_time = time.time()
        
        try:
            # Create temporary script file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as temp_file:
                # Write the script content
                temp_file.write(method_impl)
                temp_file.flush()
                temp_file_path = temp_file.name
            
            try:
                # Make script executable
                os.chmod(temp_file_path, 0o755)
                
                # Prepare environment variables from parameters
                env = os.environ.copy()
                for key, value in parameters.items():
                    env[f"AGENT_PARAM_{key.upper()}"] = str(value)
                
                # Execute the script
                result = subprocess.run(
                    [temp_file_path],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    env=env,
                    cwd=tempfile.gettempdir()
                )
                
                execution_time = time.time() - start_time
                
                if result.returncode == 0:
                    return {
                        "result": result.stdout.strip(),
                        "method_type": "custom_shell",
                        "execution_time": execution_time,
                        "language": method_info.language,
                        "return_code": result.returncode
                    }
                else:
                    return {
                        "error": f"Shell script execution failed: {result.stderr}",
                        "method_type": "custom_shell",
                        "execution_time": execution_time,
                        "language": method_info.language,
                        "return_code": result.returncode,
                        "stderr": result.stderr
                    }
                    
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary file {temp_file_path}: {e}")
                    
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Shell custom method execution failed: {e}")
            return {
                "error": f"Shell custom method execution failed: {str(e)}",
                "method_type": "custom_shell",
                "execution_time": execution_time,
                "language": method_info.language
            }

    def _execute_javascript_custom_method(self, method_impl: str, parameters: dict, method_info: Any) -> dict:
        """Execute a JavaScript custom method."""
        start_time = time.time()
        
        try:
            # Create temporary JavaScript file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as temp_file:
                # Wrap the method in a Node.js executable format
                wrapped_code = f"""
const methodImpl = {json.dumps(method_impl)};

// Execute with parameters
try {{
    const result = methodImpl({json.dumps(parameters)});
    console.log(JSON.stringify({{"result": result}}));
}} catch (error) {{
    console.error(JSON.stringify({{"error": error.message}}));
    process.exit(1);
}}
"""
                temp_file.write(wrapped_code)
                temp_file.flush()
                temp_file_path = temp_file.name
            
            try:
                # Execute with Node.js
                result = subprocess.run(
                    ["node", temp_file_path],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=tempfile.gettempdir()
                )
                
                execution_time = time.time() - start_time
                
                if result.returncode == 0:
                    try:
                        output = json.loads(result.stdout)
                        return {
                            "result": output.get("result"),
                            "method_type": "custom_javascript",
                            "execution_time": execution_time,
                            "language": method_info.language
                        }
                    except json.JSONDecodeError:
                        return {
                            "result": result.stdout.strip(),
                            "method_type": "custom_javascript",
                            "execution_time": execution_time,
                            "language": method_info.language
                        }
                else:
                    return {
                        "error": f"JavaScript execution failed: {result.stderr}",
                        "method_type": "custom_javascript",
                        "execution_time": execution_time,
                        "language": method_info.language,
                        "return_code": result.returncode,
                        "stderr": result.stderr
                    }
                    
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.warning(f"Failed to clean up temporary file {temp_file_path}: {e}")
                    
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"JavaScript custom method execution failed: {e}")
            return {
                "error": f"JavaScript custom method execution failed: {str(e)}",
                "method_type": "custom_javascript",
                "execution_time": execution_time,
                "language": method_info.language
            }

    def _execute_python_string(self, code: str, parameters: dict) -> Any:
        """Execute Python code string in a restricted environment."""
        # Create a restricted globals dictionary
        restricted_globals = {
            '__builtins__': {
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict,
                'set': set,
                'tuple': tuple,
                'bool': bool,
                'type': type,
                'isinstance': isinstance,
                'print': print,
                'range': range,
                'enumerate': enumerate,
                'zip': zip,
                'map': map,
                'filter': filter,
                'sum': sum,
                'min': min,
                'max': max,
                'abs': abs,
                'round': round,
                'sorted': sorted,
                'reversed': reversed,
                'any': any,
                'all': all,
                'chr': chr,
                'ord': ord,
                'hex': hex,
                'bin': bin,
                'oct': oct,
                'divmod': divmod,
                'pow': pow,
                'hash': hash,
                'id': id,
                'callable': callable,
                'getattr': getattr,
                'hasattr': hasattr,
                'setattr': setattr,
                'delattr': delattr,
                'property': property,
                'super': super,
                'object': object,
                'Exception': Exception,
                'ValueError': ValueError,
                'TypeError': TypeError,
                'AttributeError': AttributeError,
                'KeyError': KeyError,
                'IndexError': IndexError,
                'RuntimeError': RuntimeError,
                'OSError': OSError,
                'FileNotFoundError': FileNotFoundError,
                'PermissionError': PermissionError,
                'TimeoutError': TimeoutError,
                'MemoryError': MemoryError,
                'RecursionError': RecursionError,
                'ZeroDivisionError': ZeroDivisionError,
                'OverflowError': OverflowError,
                'ArithmeticError': ArithmeticError,
                'AssertionError': AssertionError,
                'ImportError': ImportError,
                'ModuleNotFoundError': ModuleNotFoundError,
                'SyntaxError': SyntaxError,
                'IndentationError': IndentationError,
                'TabError': TabError,
                'UnicodeError': UnicodeError,
                'UnicodeDecodeError': UnicodeDecodeError,
                'UnicodeEncodeError': UnicodeEncodeError,
                'UnicodeTranslateError': UnicodeTranslateError,
                'BlockingIOError': BlockingIOError,
                'ChildProcessError': ChildProcessError,
                'ConnectionError': ConnectionError,
                'BrokenPipeError': BrokenPipeError,
                'ConnectionAbortedError': ConnectionAbortedError,
                'ConnectionRefusedError': ConnectionRefusedError,
                'ConnectionResetError': ConnectionResetError,
                'FileExistsError': FileExistsError,
                'FileNotFoundError': FileNotFoundError,
                'IsADirectoryError': IsADirectoryError,
                'NotADirectoryError': NotADirectoryError,
                'PermissionError': PermissionError,
                'ProcessLookupError': ProcessLookupError,
                'TimeoutError': TimeoutError,
                'InterruptedError': InterruptedError,
                'NotImplementedError': NotImplementedError,
                'StopIteration': StopIteration,
                'GeneratorExit': GeneratorExit,
                'SystemExit': SystemExit,
                'KeyboardInterrupt': KeyboardInterrupt,
                'BufferError': BufferError,
                'LookupError': LookupError,
                'ReferenceError': ReferenceError,
                'SystemError': SystemError,
                'UnboundLocalError': UnboundLocalError,
                'NameError': NameError,
                'NameError': NameError,
                'UnboundLocalError': UnboundLocalError,
                'SystemError': SystemError,
                'ReferenceError': ReferenceError,
                'LookupError': LookupError,
                'BufferError': BufferError,
                'KeyboardInterrupt': KeyboardInterrupt,
                'SystemExit': SystemExit,
                'GeneratorExit': GeneratorExit,
                'StopIteration': StopIteration,
                'NotImplementedError': NotImplementedError,
                'InterruptedError': InterruptedError,
                'TimeoutError': TimeoutError,
                'ProcessLookupError': ProcessLookupError,
                'PermissionError': PermissionError,
                'NotADirectoryError': NotADirectoryError,
                'IsADirectoryError': IsADirectoryError,
                'FileNotFoundError': FileNotFoundError,
                'FileExistsError': FileExistsError,
                'ConnectionResetError': ConnectionResetError,
                'ConnectionRefusedError': ConnectionRefusedError,
                'ConnectionAbortedError': ConnectionAbortedError,
                'BrokenPipeError': BrokenPipeError,
                'ConnectionError': ConnectionError,
                'ChildProcessError': ChildProcessError,
                'BlockingIOError': BlockingIOError,
                'UnicodeTranslateError': UnicodeTranslateError,
                'UnicodeEncodeError': UnicodeEncodeError,
                'UnicodeDecodeError': UnicodeDecodeError,
                'UnicodeError': UnicodeError,
                'TabError': TabError,
                'IndentationError': IndentationError,
                'SyntaxError': SyntaxError,
                'ModuleNotFoundError': ModuleNotFoundError,
                'ImportError': ImportError,
                'AssertionError': AssertionError,
                'ArithmeticError': ArithmeticError,
                'OverflowError': OverflowError,
                'ZeroDivisionError': ZeroDivisionError,
                'RecursionError': RecursionError,
                'MemoryError': MemoryError,
                'TimeoutError': TimeoutError,
                'PermissionError': PermissionError,
                'FileNotFoundError': FileNotFoundError,
                'OSError': OSError,
                'RuntimeError': RuntimeError,
                'IndexError': IndexError,
                'KeyError': KeyError,
                'AttributeError': AttributeError,
                'TypeError': TypeError,
                'ValueError': ValueError,
                'object': object,
                'super': super,
                'property': property,
                'delattr': delattr,
                'hasattr': hasattr,
                'getattr': getattr,
                'callable': callable,
                'id': id,
                'hash': hash,
                'pow': pow,
                'divmod': divmod,
                'oct': oct,
                'bin': bin,
                'hex': hex,
                'ord': ord,
                'chr': chr,
                'all': all,
                'any': any,
                'reversed': reversed,
                'sorted': sorted,
                'round': round,
                'abs': abs,
                'max': max,
                'min': min,
                'sum': sum,
                'filter': filter,
                'map': map,
                'zip': zip,
                'enumerate': enumerate,
                'range': range,
                'print': print,
                'isinstance': isinstance,
                'type': type,
                'bool': bool,
                'tuple': tuple,
                'set': set,
                'dict': dict,
                'list': list,
                'float': float,
                'int': int,
                'str': str,
                'len': len,
            }
        }
        
        # Add parameters to globals
        restricted_globals.update(parameters)
        
        # Execute the code
        exec(code, restricted_globals)
        
        # Look for a result variable or return the last expression
        if 'result' in restricted_globals:
            return restricted_globals['result']
        elif 'return_value' in restricted_globals:
            return restricted_globals['return_value']
        else:
            # Try to find the last defined function or variable
            for key in reversed(list(restricted_globals.keys())):
                if not key.startswith('__') and callable(restricted_globals[key]):
                    return restricted_globals[key]
            return None

    def _execute_builtin_method(self, agent_path: str, method: str, parameters: dict) -> dict:
        """Execute a built-in agent method."""
        agent_dir = Path(agent_path)
        if not agent_dir.exists():
            raise ValueError(f"Agent directory does not exist: {agent_path}")

        agent_script = agent_dir / "agent.py"
        if not agent_script.exists():
            raise ValueError(f"Agent script not found: {agent_script}")

        # Prepare execution data
        execution_data = {"method": method, "parameters": parameters}

        try:
            # Get Python executable for this agent's virtual environment
            python_executable = self.environment_manager.get_python_executable(
                agent_path
            )

            # Execute agent in subprocess
            start_time = time.time()
            result = subprocess.run(
                [python_executable, str(agent_script), json.dumps(execution_data)],
                cwd=str(agent_dir),
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            execution_time = time.time() - start_time

            # Parse the result
            if result.returncode == 0:
                try:
                    parsed_result = json.loads(result.stdout)
                    parsed_result["execution_time"] = execution_time
                    parsed_result["method_type"] = "builtin"
                    return parsed_result
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse agent output: {result.stdout}")
                    return {
                        "error": f"Invalid JSON response from agent: {e}",
                        "raw_output": result.stdout,
                        "execution_time": execution_time,
                        "method_type": "builtin"
                    }
            else:
                # Agent execution failed
                error_msg = result.stderr or result.stdout or "Unknown error"
                return {
                    "error": f"Agent execution failed: {error_msg}",
                    "return_code": result.returncode,
                    "execution_time": execution_time,
                    "method_type": "builtin"
                }

        except subprocess.TimeoutExpired:
            return {
                "error": f"Agent execution timed out after {self.timeout} seconds",
                "timeout": self.timeout,
                "method_type": "builtin"
            }
        except FileNotFoundError as e:
            raise RuntimeError(f"Failed to execute agent: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error executing agent: {e}")
            return {"error": f"Unexpected execution error: {e}", "method_type": "builtin"}

    def validate_agent_structure(self, agent_path: str) -> bool:
        """
        Validate that an agent has the required structure.

        Args:
            agent_path: Path to the agent directory

        Returns:
            True if agent structure is valid
        """
        agent_dir = Path(agent_path)

        required_files = ["agent.py", "agent.yaml"]
        for file_name in required_files:
            if not (agent_dir / file_name).exists():
                logger.debug(f"Missing required file: {file_name}")
                return False

        # Check if virtual environment exists
        venv_path = self.environment_manager.get_agent_venv_path(agent_path)
        if not venv_path.exists():
            logger.debug(f"Missing virtual environment: {venv_path}")
            return False

        try:
            self.environment_manager.get_python_executable(agent_path)
            return True
        except RuntimeError:
            logger.debug("Python executable not found in virtual environment")
            return False

    def get_custom_methods(self, agent_path: str) -> dict:
        """
        Get information about custom methods available for an agent.
        
        Args:
            agent_path: Path to the agent directory
            
        Returns:
            Dictionary with custom method information
        """
        if not self.custom_method_manager:
            return {}
        
        try:
            return self.custom_method_manager.get_method_context(agent_path)
        except Exception as e:
            logger.warning(f"Failed to get custom methods for {agent_path}: {e}")
            return {}

    def inject_custom_method(self, agent_path: str, method_name: str, implementation: Any, language: str = "python") -> dict:
        """
        Inject a custom method for an agent.
        
        Args:
            agent_path: Path to the agent directory
            method_name: Name of the method to inject
            implementation: Method implementation
            language: Programming language of the implementation
            
        Returns:
            Dictionary with injection result
        """
        if not self.custom_method_manager:
            return {"error": "Custom method manager not available"}
        
        try:
            self.custom_method_manager.inject_method(agent_path, method_name, implementation, language)
            return {
                "success": True,
                "message": f"Successfully injected custom method '{method_name}' for agent '{agent_path}'",
                "method_name": method_name,
                "agent_path": agent_path,
                "language": language
            }
        except Exception as e:
            logger.error(f"Failed to inject custom method: {e}")
            return {
                "error": f"Failed to inject custom method: {str(e)}",
                "method_name": method_name,
                "agent_path": agent_path,
                "language": language
            }
