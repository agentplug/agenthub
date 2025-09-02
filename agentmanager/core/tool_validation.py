"""Tool validation system for AgentHub.

This module integrates tool metadata, registration, and security components
to provide unified validation and secure execution for tools.
"""

import inspect
import logging
import time
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field

from .tool_decorators import ToolMetadata, get_tool_metadata
from .tool_security import (
    SecurityLevel, SecurityResult, ToolExecutionContext, 
    ToolSecurityValidator, SecureToolExecutor, ToolExecutionMonitor, 
    SecurityError
)

logger = logging.getLogger(__name__)


@dataclass
class ToolValidationConfig:
    """Configuration for tool validation behavior."""
    enable_signature_validation: bool = True
    enable_security_validation: bool = True
    enable_sandboxing: bool = True
    enable_execution_monitoring: bool = True
    allowed_security_levels: List[SecurityLevel] = field(
        default_factory=lambda: [SecurityLevel.SAFE, SecurityLevel.LIMITED]
    )
    default_timeout: int = 30
    default_memory_limit: int = 100 * 1024 * 1024  # 100MB
    default_cpu_limit: int = 10  # 10 seconds


@dataclass
class SignatureValidationResult:
    """Result of function signature validation."""
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass 
class ToolValidationResult:
    """Result of comprehensive tool validation."""
    tool_name: str
    is_valid: bool
    security_result: Optional[SecurityResult] = None
    signature_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    execution_context: Optional[ToolExecutionContext] = None


class ToolValidator:
    """Comprehensive tool validator with security integration."""
    
    _instance: Optional["ToolValidator"] = None
    
    def __new__(cls, config: Optional[ToolValidationConfig] = None) -> "ToolValidator":
        if cls._instance is None:
            cls._instance = super(ToolValidator, cls).__new__(cls)
            cls._instance.config = config if config is not None else ToolValidationConfig()
            cls._instance.security_validator = ToolSecurityValidator()
            cls._instance.secure_executor = SecureToolExecutor()
            cls._instance.execution_monitor = ToolExecutionMonitor()
        return cls._instance
    
    def validate_signature(self, func: Callable[..., Any]) -> SignatureValidationResult:
        """Validate function signature for tool compatibility."""
        errors = []
        warnings = []
        
        try:
            # Check if function is callable
            if not callable(func):
                errors.append("Object is not callable")
                return SignatureValidationResult(False, errors, warnings)
            
            # Check function name
            if not hasattr(func, '__name__'):
                errors.append("Function must have __name__ attribute")
            
            # Analyze signature
            try:
                signature = inspect.signature(func)
                
                # Check for *args, **kwargs patterns
                has_var_positional = False
                has_var_keyword = False
                
                for param in signature.parameters.values():
                    if param.kind == param.VAR_POSITIONAL:
                        has_var_positional = True
                        warnings.append("Function uses *args - may complicate parameter validation")
                    elif param.kind == param.VAR_KEYWORD:
                        has_var_keyword = True
                        warnings.append("Function uses **kwargs - may complicate parameter validation")
                
                # Check parameter annotations
                unannotated_params = []
                for name, param in signature.parameters.items():
                    if param.annotation == param.empty and param.default == param.empty:
                        unannotated_params.append(name)
                
                if unannotated_params:
                    warnings.append(f"Parameters without type annotations: {', '.join(unannotated_params)}")
                
                # Check return annotation
                if signature.return_annotation == signature.empty:
                    warnings.append("Function lacks return type annotation")
                
            except (ValueError, TypeError) as e:
                errors.append(f"Signature analysis failed: {str(e)}")
        
        except Exception as e:
            errors.append(f"Signature validation error: {str(e)}")
        
        return SignatureValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def validate_tool(
        self, 
        func: Callable[..., Any], 
        metadata: Optional[ToolMetadata] = None
    ) -> ToolValidationResult:
        """Perform comprehensive tool validation."""
        tool_name = getattr(func, '__name__', 'unknown')
        errors = []
        warnings = []
        recommendations = []
        security_result = None
        execution_context = None
        
        try:
            # 1. Signature validation
            if self.config.enable_signature_validation:
                sig_result = self.validate_signature(func)
                signature_valid = sig_result.is_valid
                errors.extend(sig_result.errors)
                warnings.extend(sig_result.warnings)
            else:
                signature_valid = True
            
            # 2. Security validation
            if self.config.enable_security_validation:
                try:
                    security_result = self.security_validator.validate_function(func)
                    
                    # Check if security level is allowed
                    if security_result.level not in self.config.allowed_security_levels:
                        errors.append(f"Security level {security_result.level.value} not allowed")
                    
                    # Add security risks as warnings/errors
                    if not security_result.approved:
                        if security_result.level == SecurityLevel.UNSAFE:
                            errors.extend([f"Security risk: {risk}" for risk in security_result.risks])
                        else:
                            warnings.extend([f"Security concern: {risk}" for risk in security_result.risks])
                    
                    # Add recommendations
                    recommendations.extend(security_result.recommendations)
                    
                except SecurityError as e:
                    errors.append(f"Security validation failed: {str(e)}")
                except Exception as e:
                    warnings.append(f"Security validation error: {str(e)}")
            
            # 3. Create execution context if sandboxing enabled
            if self.config.enable_sandboxing:
                execution_context = ToolExecutionContext(
                    tool_name=tool_name,
                    parameters={},
                    timeout=self.config.default_timeout,
                    memory_limit=self.config.default_memory_limit,
                    cpu_limit=self.config.default_cpu_limit,
                    network_access=False,
                    file_access=False,
                    allowed_paths=[]
                )
            
            # 4. Overall validation result
            is_valid = len(errors) == 0 and signature_valid
            
            if is_valid:
                logger.info(f"Tool validation passed for: {tool_name}")
            else:
                logger.warning(f"Tool validation failed for: {tool_name} - {errors}")
            
            return ToolValidationResult(
                tool_name=tool_name,
                is_valid=is_valid,
                security_result=security_result,
                signature_valid=signature_valid,
                errors=errors,
                warnings=warnings,
                recommendations=recommendations,
                execution_context=execution_context
            )
            
        except Exception as e:
            logger.error(f"Tool validation error for {tool_name}: {str(e)}")
            return ToolValidationResult(
                tool_name=tool_name,
                is_valid=False,
                errors=[f"Validation failed: {str(e)}"],
                signature_valid=False
            )
    
    def execute_tool_safely(
        self,
        tool_function: Callable[..., Any],
        parameters: Dict[str, Any],
        execution_context: Optional[ToolExecutionContext] = None
    ) -> Any:
        """Execute a tool function with security monitoring."""
        start_time = time.time()
        
        try:
            # Use provided context or create default
            if execution_context is None:
                execution_context = ToolExecutionContext(
                    tool_name=getattr(tool_function, '__name__', 'unknown'),
                    parameters=parameters,
                    timeout=self.config.default_timeout,
                    memory_limit=self.config.default_memory_limit,
                    cpu_limit=self.config.default_cpu_limit,
                    network_access=False,
                    file_access=False,
                    allowed_paths=[]
                )
            
            # Execute with monitoring if enabled
            if self.config.enable_execution_monitoring:
                result = self.secure_executor.execute_safely(
                    tool_function, parameters, execution_context
                )
                
                # Log execution
                execution_time = time.time() - start_time
                self.execution_monitor.log_execution(
                    getattr(tool_function, '__name__', 'unknown'),
                    execution_time,
                    len(str(parameters)),
                    True
                )
                
                return result
            else:
                # Direct execution without monitoring
                if inspect.iscoroutinefunction(tool_function):
                    import asyncio
                    return asyncio.run(tool_function(**parameters))
                else:
                    return tool_function(**parameters)
                    
        except Exception as e:
            execution_time = time.time() - start_time
            
            if self.config.enable_execution_monitoring:
                self.execution_monitor.log_execution(
                    getattr(tool_function, '__name__', 'unknown'),
                    execution_time,
                    len(str(parameters)),
                    False,
                    str(e)
                )
            
            logger.error(f"Tool execution failed: {str(e)}")
            raise
    
    def get_security_report(self) -> Dict[str, Any]:
        """Get security monitoring report."""
        return self.execution_monitor.get_security_report()


# Global validator instance
_global_validator = ToolValidator()


def validate_tool(
    func: Callable[..., Any], 
    metadata: Optional[ToolMetadata] = None
) -> ToolValidationResult:
    """Validate a tool using the global validator."""
    return _global_validator.validate_tool(func, metadata)


def execute_tool_safely(
    tool_function: Callable[..., Any],
    parameters: Dict[str, Any],
    execution_context: Optional[ToolExecutionContext] = None
) -> Any:
    """Execute a tool safely using the global validator."""
    return _global_validator.execute_tool_safely(tool_function, parameters, execution_context)


def get_security_report() -> Dict[str, Any]:
    """Get security report from global validator."""
    return _global_validator.get_security_report()


def get_global_validator() -> ToolValidator:
    """Get the global validator instance."""
    return _global_validator
