"""
Custom exceptions for Agent Hub custom method injection system.

Provides clear error handling and user feedback for method injection operations.
"""


class MethodValidationError(Exception):
    """Raised when method validation fails."""
    
    def __init__(self, message: str, validation_details: dict = None):
        super().__init__(message)
        self.validation_details = validation_details or {}
    
    def __str__(self):
        if self.validation_details:
            return f"{super().__str__()} - Details: {self.validation_details}"
        return super().__str__()


class MethodNotFoundError(Exception):
    """Raised when a custom method is not found."""
    
    def __init__(self, message: str, agent_path: str = None, method_name: str = None):
        super().__init__(message)
        self.agent_path = agent_path
        self.method_name = method_name
    
    def __str__(self):
        if self.agent_path and self.method_name:
            return f"Custom method '{self.method_name}' not found for agent '{self.agent_path}'"
        return super().__str__()


class MethodSecurityError(Exception):
    """Raised when a method poses security risks."""
    
    def __init__(self, message: str, security_level: str = "medium", detected_patterns: list = None):
        super().__init__(message)
        self.security_level = security_level
        self.detected_patterns = detected_patterns or []
    
    def __str__(self):
        if self.detected_patterns:
            return f"{super().__str__()} - Detected patterns: {', '.join(self.detected_patterns)}"
        return super().__str__()


class MethodExecutionError(Exception):
    """Raised when method execution fails."""
    
    def __init__(self, message: str, method_name: str = None, execution_details: dict = None):
        super().__init__(message)
        self.method_name = method_name
        self.execution_details = execution_details or {}
    
    def __str__(self):
        if self.method_name:
            return f"Execution failed for method '{self.method_name}': {super().__str__()}"
        return super().__str__()


class MethodInjectionError(Exception):
    """Raised when method injection fails."""
    
    def __init__(self, message: str, agent_path: str = None, method_name: str = None, cause: Exception = None):
        super().__init__(message)
        self.agent_path = agent_path
        self.method_name = method_name
        self.cause = cause
    
    def __str__(self):
        base_msg = super().__str__()
        if self.agent_path and self.method_name:
            base_msg = f"Failed to inject method '{self.method_name}' for agent '{self.agent_path}': {base_msg}"
        if self.cause:
            base_msg = f"{base_msg} - Caused by: {self.cause}"
        return base_msg


class MethodLanguageNotSupportedError(Exception):
    """Raised when a programming language is not supported."""
    
    def __init__(self, language: str, supported_languages: list = None):
        message = f"Language '{language}' is not supported"
        if supported_languages:
            message += f". Supported languages: {', '.join(supported_languages)}"
        
        super().__init__(message)
        self.language = language
        self.supported_languages = supported_languages or []


class MethodSizeLimitError(Exception):
    """Raised when method implementation exceeds size limits."""
    
    def __init__(self, actual_size: int, max_size: int, size_unit: str = "bytes"):
        message = f"Method implementation too large: {actual_size} {size_unit}. Maximum allowed: {max_size} {size_unit}"
        super().__init__(message)
        self.actual_size = actual_size
        self.max_size = max_size
        self.size_unit = size_unit


class MethodIntegrityError(Exception):
    """Raised when method integrity check fails."""
    
    def __init__(self, message: str, expected_checksum: str = None, actual_checksum: str = None):
        super().__init__(message)
        self.expected_checksum = expected_checksum
        self.actual_checksum = actual_checksum
    
    def __str__(self):
        base_msg = super().__str__()
        if self.expected_checksum and self.actual_checksum:
            base_msg = f"{base_msg} - Expected: {self.expected_checksum}, Actual: {self.actual_checksum}"
        return base_msg


class MethodPermissionError(Exception):
    """Raised when user lacks permission to perform method operation."""
    
    def __init__(self, message: str, operation: str = None, required_permissions: list = None):
        super().__init__(message)
        self.operation = operation
        self.required_permissions = required_permissions or []
    
    def __str__(self):
        base_msg = super().__str__()
        if self.operation:
            base_msg = f"Permission denied for operation '{self.operation}': {base_msg}"
        if self.required_permissions:
            base_msg = f"{base_msg} - Required permissions: {', '.join(self.required_permissions)}"
        return base_msg


class MethodTimeoutError(Exception):
    """Raised when method execution times out."""
    
    def __init__(self, message: str, timeout_seconds: int = None, method_name: str = None):
        super().__init__(message)
        self.timeout_seconds = timeout_seconds
        self.method_name = method_name
    
    def __str__(self):
        base_msg = super().__init__()
        if self.timeout_seconds and self.method_name:
            base_msg = f"Method '{self.method_name}' timed out after {self.timeout_seconds} seconds"
        elif self.timeout_seconds:
            base_msg = f"Method execution timed out after {self.timeout_seconds} seconds"
        return base_msg


class MethodResourceLimitError(Exception):
    """Raised when method exceeds resource limits."""
    
    def __init__(self, message: str, resource_type: str = None, limit: int = None, actual: int = None):
        super().__init__(message)
        self.resource_type = resource_type
        self.limit = limit
        self.actual = actual
    
    def __str__(self):
        base_msg = super().__str__()
        if self.resource_type and self.limit and self.actual:
            base_msg = f"{self.resource_type} limit exceeded: {self.actual} > {self.limit}"
        return base_msg


class MethodCompatibilityError(Exception):
    """Raised when method is incompatible with agent or environment."""
    
    def __init__(self, message: str, agent_path: str = None, compatibility_issues: list = None):
        super().__init__(message)
        self.agent_path = agent_path
        self.compatibility_issues = compatibility_issues or []
    
    def __str__(self):
        base_msg = super().__str__()
        if self.agent_path:
            base_msg = f"Compatibility error with agent '{self.agent_path}': {base_msg}"
        if self.compatibility_issues:
            base_msg = f"{base_msg} - Issues: {', '.join(self.compatibility_issues)}"
        return base_msg
