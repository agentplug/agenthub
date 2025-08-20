"""
Enhanced Security Framework for Tool Validation and Execution.

This module provides comprehensive security measures for tool integration,
including sandboxing, validation, and threat detection.
"""

import ast
import inspect
import os
import resource
import signal
import sys
import threading
import time
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import subprocess
import tempfile
import logging

logger = logging.getLogger(__name__)


class SecurityLevel(Enum):
    """Security classification levels for tools."""
    SAFE = "safe"           # Pure computation, no I/O
    LIMITED = "limited"     # Restricted file/network access
    RESTRICTED = "restricted"  # Full access with monitoring
    UNSAFE = "unsafe"       # Not allowed


@dataclass
class SecurityResult:
    """Result of security analysis."""
    level: SecurityLevel
    approved: bool
    risks: List[str]
    recommendations: List[str]


@dataclass
class ToolExecutionContext:
    """Context for secure tool execution."""
    tool_name: str
    parameters: Dict[str, Any]
    timeout: int = 30
    memory_limit: int = 100 * 1024 * 1024  # 100MB
    cpu_limit: int = 10  # 10 seconds
    network_access: bool = False
    file_access: bool = False
    allowed_paths: List[str] = None


class ToolSecurityValidator:
    """Comprehensive security validator for tools."""
    
    def __init__(self):
        self.banned_imports = {
            'os', 'subprocess', 'sys', 'socket', 'urllib', 'requests',
            'ftplib', 'smtplib', 'telnetlib', 'paramiko', 'cryptography'
        }
        self.builtins_blacklist = {
            'eval', 'exec', 'compile', '__import__', 'open', 'file',
            'input', 'raw_input', 'reload'
        }
        self.dangerous_attributes = {
            '__subclasses__', '__bases__', '__globals__', '__code__',
            '__func__', '__closure__', '__defaults__'
        }
    
    def validate_tool_source(self, source_code: str) -> SecurityResult:
        """Validate tool source code for security risks."""
        try:
            tree = ast.parse(source_code)
            visitor = SecurityAstVisitor()
            visitor.visit(tree)
            
            risks = []
            recommendations = []
            
            if visitor.has_imports:
                risks.append("Tool uses imports - requires sandboxing")
                recommendations.append("Run in restricted environment")
            
            if visitor.has_file_operations:
                risks.append("File system access detected")
                recommendations.append("Limit to specific directories")
            
            if visitor.has_network_operations:
                risks.append("Network operations detected")
                recommendations.append("Block network access")
            
            if visitor.has_eval_operations:
                risks.append("Dynamic code execution detected")
                recommendations.append("Reject tool - security risk")
                return SecurityResult(SecurityLevel.UNSAFE, False, risks, recommendations)
            
            if not risks:
                return SecurityResult(SecurityLevel.SAFE, True, [], ["No security concerns"])
            elif len(risks) <= 2:
                return SecurityResult(SecurityLevel.LIMITED, True, risks, recommendations)
            else:
                return SecurityResult(SecurityLevel.RESTRICTED, True, risks, recommendations)
                
        except SyntaxError as e:
            return SecurityResult(
                SecurityLevel.UNSAFE, 
                False, 
                [f"Syntax error: {e}"],
                ["Fix syntax errors before validation"]
            )
    
    def validate_tool_function(self, func: callable) -> SecurityResult:
        """Validate a tool function by analyzing its source."""
        try:
            source = inspect.getsource(func)
            return self.validate_tool_source(source)
        except (OSError, TypeError):
            # Handle built-in functions or compiled code
            return SecurityResult(
                SecurityLevel.LIMITED, 
                True, 
                ["Cannot analyze source code"],
                ["Run with restricted permissions"]
            )


class SecurityAstVisitor(ast.NodeVisitor):
    """AST visitor for security analysis."""
    
    def __init__(self):
        self.has_imports = False
        self.has_file_operations = False
        self.has_network_operations = False
        self.has_eval_operations = False
    
    def visit_Import(self, node):
        self.has_imports = True
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        self.has_imports = True
        self.generic_visit(node)
    
    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in ['open', 'file', 'exec', 'eval']:
                if node.func.id in ['open', 'file']:
                    self.has_file_operations = True
                elif node.func.id in ['exec', 'eval']:
                    self.has_eval_operations = True
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in ['read', 'write', 'open', 'connect', 'request']:
                if any(network in str(node) for network in ['http', 'ftp', 'socket']):
                    self.has_network_operations = True
        self.generic_visit(node)


class SecureToolExecutor:
    """Secure executor for tool functions with sandboxing."""
    
    def __init__(self):
        self.validator = ToolSecurityValidator()
    
    def execute_secure(self, tool_func: callable, context: ToolExecutionContext) -> Any:
        """Execute tool in secure sandbox environment."""
        try:
            # Validate tool security
            security_result = self.validator.validate_tool_function(tool_func)
            if not security_result.approved:
                raise SecurityError(f"Tool rejected: {security_result.risks}")
            
            # Set up resource limits
            self._setup_resource_limits(context)
            
            # Execute with monitoring
            return self._execute_with_monitoring(tool_func, context)
            
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            raise
    
    def _setup_resource_limits(self, context: ToolExecutionContext):
        """Set up resource limits for tool execution."""
        try:
            # Memory limit
            resource.setrlimit(resource.RLIMIT_AS, (context.memory_limit, context.memory_limit))
            
            # CPU time limit
            resource.setrlimit(resource.RLIMIT_CPU, (context.cpu_limit, context.cpu_limit))
            
            # File descriptor limit
            resource.setrlimit(resource.RLIMIT_NOFILE, (50, 50))
            
        except (resource.error, ValueError) as e:
            logger.warning(f"Could not set resource limits: {e}")
    
    def _execute_with_monitoring(self, tool_func: callable, context: ToolExecutionContext) -> Any:
        """Execute tool with runtime monitoring."""
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Tool execution timed out after {context.timeout}s")
        
        # Set timeout
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(context.timeout)
        
        try:
            result = tool_func(**context.parameters)
            return result
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)


class ToolSandbox:
    """Lightweight sandbox for tool execution."""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp(prefix="agent_tool_sandbox_")
        self.original_dir = os.getcwd()
    
    def __enter__(self):
        os.chdir(self.temp_dir)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.original_dir)
        # Clean up temporary directory
        try:
            import shutil
            shutil.rmtree(self.temp_dir)
        except (OSError, IOError):
            pass


class SecurityError(Exception):
    """Raised when a security violation is detected."""
    pass


class ToolExecutionMonitor:
    """Monitor tool execution for anomalies and performance."""
    
    def __init__(self):
        self.execution_log = []
        self.performance_metrics = {}
    
    def log_execution(self, tool_name: str, duration: float, memory_peak: int, 
                     success: bool, error: Optional[str] = None):
        """Log tool execution metrics."""
        self.execution_log.append({
            'tool_name': tool_name,
            'timestamp': time.time(),
            'duration': duration,
            'memory_peak': memory_peak,
            'success': success,
            'error': error
        })
    
    def get_security_report(self) -> Dict[str, Any]:
        """Generate security report for monitoring."""
        total_executions = len(self.execution_log)
        successful_executions = sum(1 for log in self.execution_log if log['success'])
        failed_executions = total_executions - successful_executions
        
        return {
            'total_executions': total_executions,
            'success_rate': successful_executions / max(total_executions, 1),
            'failed_executions': failed_executions,
            'average_duration': sum(log['duration'] for log in self.execution_log) / max(total_executions, 1),
            'recent_errors': [log for log in self.execution_log[-10:] if not log['success']]
        }