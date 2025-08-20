"""
Method Validator for Agent Hub

Simplified security validation for custom method implementations.
"""

import ast
import re
import logging
from typing import Dict, List, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of method validation."""
    is_valid: bool = True
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    security_score: int = 100  # 0-100, higher is safer
    
    @property
    def total_issues(self) -> int:
        """Total number of errors and warnings."""
        return len(self.errors) + len(self.warnings)
    
    def add_error(self, message: str) -> None:
        """Add a validation error."""
        self.errors.append(message)
        self.is_valid = False
        self.security_score = max(0, self.security_score - 20)
    
    def add_warning(self, message: str) -> None:
        """Add a validation warning."""
        self.warnings.append(message)
        self.security_score = max(0, self.security_score - 5)
    
    def merge(self, other: 'ValidationResult') -> None:
        """Merge another validation result."""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        if not other.is_valid:
            self.is_valid = False
        # Calculate average security score, but weight it towards the lower score
        self.security_score = min(self.security_score, other.security_score) - len(other.errors) * 10 - len(other.warnings) * 2
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "security_score": self.security_score,
            "total_issues": self.total_issues
        }


class MethodValidator:
    """Validates custom method implementations for security and compatibility."""
    
    def __init__(self, security_level: str = "medium"):
        """Initialize the validator."""
        self.security_level = security_level
        self.dangerous_patterns = self._load_dangerous_patterns()
        
    def validate_method(self, implementation: Any, language: str) -> ValidationResult:
        """
        Validate a method implementation.
        
        Args:
            implementation: Method implementation (string or callable)
            language: Programming language
            
        Returns:
            ValidationResult with validation status and details
        """
        result = ValidationResult()
        
        if implementation is None:
            result.add_error("Implementation cannot be None")
            return result
        
        # Convert to string if needed
        code = str(implementation)
        
        # Basic checks
        if len(code.strip()) == 0:
            result.add_warning("Empty implementation")
            return result
        
        if len(code) > 50000:  # 50KB limit
            result.add_warning("Implementation is very large")
        
        # Language-specific validation
        if language == "python":
            self._validate_python(code, result)
        elif language in ["javascript", "js"]:
            self._validate_javascript(code, result)
        elif language in ["shell", "bash"]:
            self._validate_shell(code, result)
        else:
            result.add_warning(f"Generic validation for unknown language: {language}")
        
        # Security pattern checks
        self._check_security_patterns(code, language, result)
        
        return result
    
    def _validate_python(self, code: str, result: ValidationResult) -> None:
        """Validate Python code."""
        try:
            # Parse AST to check syntax
            tree = ast.parse(code)
            
            # Check for dangerous constructs
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        func_name = node.func.id
                        if func_name in ["eval", "exec", "compile"]:
                            result.add_error(f"Dangerous function call: {func_name}")
                        elif func_name in ["open", "__import__"]:
                            result.add_warning(f"Potentially unsafe function: {func_name}")
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in ["os", "sys", "subprocess"]:
                            result.add_warning(f"System module import: {alias.name}")
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module in ["os", "sys", "subprocess"]:
                        result.add_warning(f"System module import: {node.module}")
        
        except SyntaxError as e:
            result.add_error(f"Python syntax error: {e}")
        except Exception as e:
            result.add_warning(f"Could not parse Python code: {e}")
    
    def _validate_javascript(self, code: str, result: ValidationResult) -> None:
        """Validate JavaScript code."""
        # Basic JavaScript validation
        dangerous_js = ["eval(", "setTimeout(", "setInterval(", "Function(", "document.write"]
        
        for pattern in dangerous_js:
            if pattern in code:
                result.add_error(f"Dangerous JavaScript pattern: {pattern}")
        
        # Check for common issues
        if "try" not in code and "catch" not in code:
            result.add_warning("No error handling detected")
    
    def _validate_shell(self, code: str, result: ValidationResult) -> None:
        """Validate shell script code."""
        dangerous_shell = ["rm -rf", "dd if=", ":(){ :|:& };:", "mkfs", "format"]
        
        for pattern in dangerous_shell:
            if pattern in code:
                result.add_error(f"Dangerous shell command: {pattern}")
        
        # Check for basic safety practices
        if "set -e" not in code:
            result.add_warning("No error handling (set -e) detected")
        
        if not code.strip().startswith("#!"):
            result.add_warning("No shebang detected")
    
    def _check_security_patterns(self, code: str, language: str, result: ValidationResult) -> None:
        """Check for security patterns based on language."""
        patterns = self.dangerous_patterns.get(language, {})
        
        # Check dangerous patterns
        for pattern in patterns.get("dangerous", []):
            if re.search(pattern, code, re.IGNORECASE):
                if self.security_level == "high":
                    result.add_error(f"Forbidden pattern detected: {pattern}")
                else:
                    result.add_warning(f"Potentially dangerous pattern: {pattern}")
        
        # Check suspicious patterns
        for pattern in patterns.get("suspicious", []):
            if re.search(pattern, code, re.IGNORECASE):
                result.add_warning(f"Suspicious pattern detected: {pattern}")
    
    def _load_dangerous_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Load dangerous patterns for different languages."""
        return {
            "python": {
                "dangerous": [
                    r"exec\s*\(",
                    r"eval\s*\(",
                    r"__import__\s*\(",
                    r"compile\s*\(",
                    r"globals\s*\(",
                    r"locals\s*\(",
                ],
                "suspicious": [
                    r"import\s+os",
                    r"import\s+sys",
                    r"import\s+subprocess",
                    r"open\s*\(",
                    r"file\s*\(",
                ]
            },
            "javascript": {
                "dangerous": [
                    r"eval\s*\(",
                    r"Function\s*\(",
                    r"setTimeout\s*\(",
                    r"setInterval\s*\(",
                    r"document\.write",
                ],
                "suspicious": [
                    r"innerHTML",
                    r"outerHTML",
                    r"location\.",
                    r"window\.",
                ]
            },
            "shell": {
                "dangerous": [
                    r"rm\s+-rf",
                    r"dd\s+if=",
                    r"mkfs",
                    r"format",
                    r">\s*/dev/",
                ],
                "suspicious": [
                    r"\$\(.*\)",
                    r"`.*`",
                    r"wget\s+",
                    r"curl\s+",
                ]
            }
        }
    
    def suggest_improvements(self, result: ValidationResult) -> List[str]:
        """Suggest improvements based on validation results."""
        suggestions = []
        
        if result.security_score < 50:
            suggestions.append("Security score is very low - review for dangerous patterns")
        
        if result.errors:
            suggestions.append("Fix all errors before using this method")
        
        if result.warnings:
            suggestions.append("Consider addressing warnings to improve security")
        
        if result.security_score < 80:
            suggestions.append("Add input validation and error handling")
            suggestions.append("Avoid system-level operations")
        
        return suggestions
    
    def get_validation_summary(self, result: ValidationResult) -> str:
        """Get a human-readable validation summary."""
        if result.is_valid:
            if result.warnings:
                return f"✅ Validation passed with {len(result.warnings)} warnings. Security: {result.security_score}/100"
            else:
                return f"✅ Validation passed successfully. Security: {result.security_score}/100"
        else:
            return f"❌ Validation failed with {len(result.errors)} errors. Security: {result.security_score}/100"