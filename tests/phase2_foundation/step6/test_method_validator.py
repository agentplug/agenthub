"""
Simplified tests for Method Validator.
"""

import pytest

from agentmanager.validation.method_validator import MethodValidator, ValidationResult


class TestValidationResult:
    """Test cases for ValidationResult."""
    
    def test_init_default_values(self):
        """Test initialization with default values."""
        result = ValidationResult()
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []
        assert result.security_score == 100
    
    def test_add_error(self):
        """Test adding validation errors."""
        result = ValidationResult()
        result.add_error("Test error")
        
        assert not result.is_valid
        assert len(result.errors) == 1
        assert "Test error" in result.errors
        assert result.security_score == 80
    
    def test_add_warning(self):
        """Test adding validation warnings."""
        result = ValidationResult()
        result.add_warning("Test warning")
        
        assert result.is_valid is True
        assert len(result.warnings) == 1
        assert "Test warning" in result.warnings
        assert result.security_score == 95
    
    def test_merge_results(self):
        """Test merging validation results."""
        result1 = ValidationResult()
        result1.add_error("Error 1")
        result1.add_warning("Warning 1")
        
        result2 = ValidationResult()
        result2.add_error("Error 2")
        result2.add_warning("Warning 2")
        
        result1.merge(result2)
        
        assert not result1.is_valid
        assert len(result1.errors) == 2
        assert len(result1.warnings) == 2
        # Security score should be reduced for errors and warnings
        assert result1.security_score < 80
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = ValidationResult()
        result.add_error("Error 1")
        result.add_warning("Warning 1")
        
        data = result.to_dict()
        
        assert data["is_valid"] is False
        assert data["errors"] == ["Error 1"]
        assert data["warnings"] == ["Warning 1"]
        assert data["security_score"] == 75
        assert data["total_issues"] == 2

    def test_total_issues_property(self):
        """Test total_issues property."""
        result = ValidationResult()
        assert result.total_issues == 0
        
        result.add_error("Error")
        assert result.total_issues == 1
        
        result.add_warning("Warning")
        assert result.total_issues == 2


class TestMethodValidator:
    """Test cases for MethodValidator."""
    
    @pytest.fixture
    def validator(self):
        """Create a MethodValidator instance for testing."""
        return MethodValidator(security_level="medium")
    
    @pytest.fixture
    def high_security_validator(self):
        """Create a high security MethodValidator instance."""
        return MethodValidator(security_level="high")
    
    def test_init_default_values(self):
        """Test initialization with default values."""
        validator = MethodValidator()
        assert validator.security_level == "medium"
        assert "python" in validator.dangerous_patterns
    
    def test_init_custom_security_level(self):
        """Test initialization with custom security level."""
        validator = MethodValidator(security_level="high")
        assert validator.security_level == "high"
    
    def test_validate_method_none_implementation(self, validator):
        """Test validation with None implementation."""
        result = validator.validate_method(None, "python")
        
        assert not result.is_valid
        assert len(result.errors) == 1
        assert "cannot be None" in result.errors[0]
    
    def test_validate_method_empty_implementation(self, validator):
        """Test validation with empty implementation."""
        result = validator.validate_method("", "python")
        
        assert result.is_valid is True
        assert len(result.warnings) == 1
        assert "Empty implementation" in result.warnings[0]
    
    def test_validate_method_large_implementation(self, validator):
        """Test validation with very large implementation."""
        large_code = "x" * 60000  # 60KB
        result = validator.validate_method(large_code, "python")
        
        assert result.is_valid is True
        assert len(result.warnings) >= 1
        assert any("very large" in w for w in result.warnings)
    
    def test_validate_python_method_success(self, validator):
        """Test successful validation of Python method."""
        good_code = "def test_function(x):\n    return x * 2"
        result = validator.validate_method(good_code, "python")
        
        assert result.is_valid is True
        assert result.security_score >= 80
    
    def test_validate_python_method_dangerous(self, validator):
        """Test validation of dangerous Python method."""
        dangerous_code = "exec('print(1)')"
        result = validator.validate_method(dangerous_code, "python")
        
        assert not result.is_valid
        assert result.security_score < 80
        assert any("eval" in error or "exec" in error for error in result.errors)
    
    def test_validate_python_syntax_error(self, validator):
        """Test validation with Python syntax error."""
        invalid_code = "def test( x: return x * 2"
        result = validator.validate_method(invalid_code, "python")
        
        assert not result.is_valid
        assert any("syntax error" in error.lower() for error in result.errors)
    
    def test_validate_python_dangerous_imports(self, validator):
        """Test validation with dangerous imports."""
        code_with_imports = "import os\nimport sys\nprint('test')"
        result = validator.validate_method(code_with_imports, "python")
        
        assert result.is_valid is True
        assert len(result.warnings) >= 1
        assert any("system module" in w.lower() for w in result.warnings)
    
    def test_validate_javascript_method_success(self, validator):
        """Test successful validation of JavaScript method."""
        good_js = "function test(x) { return x * 2; }"
        result = validator.validate_method(good_js, "javascript")
        
        assert result.is_valid is True
        assert result.security_score >= 80
    
    def test_validate_javascript_method_dangerous(self, validator):
        """Test validation of dangerous JavaScript method."""
        dangerous_js = "eval('alert(1)')"
        result = validator.validate_method(dangerous_js, "javascript")
        
        assert not result.is_valid
        assert result.security_score < 80
        assert any("eval" in error.lower() for error in result.errors)
    
    def test_validate_javascript_no_error_handling(self, validator):
        """Test JavaScript validation for missing error handling."""
        js_without_handling = "function test() { return 'test'; }"
        result = validator.validate_method(js_without_handling, "javascript")
        
        assert result.is_valid is True
        assert any("error handling" in w.lower() for w in result.warnings)
    
    def test_validate_shell_method_success(self, validator):
        """Test successful validation of shell method."""
        good_shell = "#!/bin/bash\nset -e\necho 'hello'"
        result = validator.validate_method(good_shell, "shell")
        
        assert result.is_valid is True
        assert result.security_score >= 80
    
    def test_validate_shell_method_dangerous(self, validator):
        """Test validation of dangerous shell method."""
        dangerous_shell = "rm -rf /"
        result = validator.validate_method(dangerous_shell, "shell")
        
        assert not result.is_valid
        assert result.security_score < 80
        assert any("dangerous" in error.lower() for error in result.errors)
    
    def test_validate_shell_no_error_handling(self, validator):
        """Test shell validation for missing error handling."""
        shell_without_handling = "echo 'test'"
        result = validator.validate_method(shell_without_handling, "shell")
        
        assert result.is_valid is True
        assert any("error handling" in w.lower() for w in result.warnings)
    
    def test_validate_shell_no_shebang(self, validator):
        """Test shell validation for missing shebang."""
        shell_without_shebang = "echo 'test'"
        result = validator.validate_method(shell_without_shebang, "shell")
        
        assert result.is_valid is True
        assert any("shebang" in w.lower() for w in result.warnings)
    
    def test_validate_unknown_language(self, validator):
        """Test validation of unknown language."""
        content = "Some content"
        result = validator.validate_method(content, "unknown")
        
        assert result.is_valid is True
        assert any("generic validation" in w.lower() for w in result.warnings)
    
    def test_security_level_high_stricter(self, high_security_validator):
        """Test that high security level is stricter."""
        suspicious_code = "import os"
        result = high_security_validator.validate_method(suspicious_code, "python")
        
        # High security should be more strict
        assert result.security_score <= 95  # Should have some penalty
    
    def test_security_patterns_loading(self, validator):
        """Test that security patterns are loaded correctly."""
        patterns = validator.dangerous_patterns
        
        assert "python" in patterns
        assert "javascript" in patterns
        assert "shell" in patterns
        
        assert "dangerous" in patterns["python"]
        assert "suspicious" in patterns["python"]
    
    def test_suggest_improvements_low_security(self, validator):
        """Test improvement suggestions for low security score."""
        result = ValidationResult()
        result.add_error("Test error")
        result.add_warning("Test warning")
        result.security_score = 30
        
        suggestions = validator.suggest_improvements(result)
        
        assert len(suggestions) >= 2
        assert any("very low" in s.lower() for s in suggestions)
        assert any("fix all errors" in s.lower() for s in suggestions)
    
    def test_suggest_improvements_medium_security(self, validator):
        """Test improvement suggestions for medium security score."""
        result = ValidationResult()
        result.add_warning("Test warning")
        result.security_score = 70
        
        suggestions = validator.suggest_improvements(result)
        
        assert len(suggestions) >= 2
        assert any("warnings" in s.lower() for s in suggestions)
    
    def test_suggest_improvements_high_security(self, validator):
        """Test improvement suggestions for high security score."""
        result = ValidationResult()
        result.security_score = 95
        
        suggestions = validator.suggest_improvements(result)
        
        assert len(suggestions) == 0
    
    def test_get_validation_summary_success(self, validator):
        """Test getting validation summary for successful validation."""
        result = ValidationResult()
        summary = validator.get_validation_summary(result)
        
        assert "✅ Validation passed successfully" in summary
        assert "Security: 100/100" in summary
    
    def test_get_validation_summary_with_warnings(self, validator):
        """Test getting validation summary with warnings."""
        result = ValidationResult()
        result.add_warning("Test warning")
        summary = validator.get_validation_summary(result)
        
        assert "✅ Validation passed with 1 warnings" in summary
        assert "Security: 95/100" in summary
    
    def test_get_validation_summary_failed(self, validator):
        """Test getting validation summary for failed validation."""
        result = ValidationResult()
        result.add_error("Test error")
        summary = validator.get_validation_summary(result)
        
        assert "❌ Validation failed with 1 errors" in summary
        assert "Security: 80/100" in summary
    
    def test_python_ast_parsing_comprehensive(self, validator):
        """Test comprehensive Python AST parsing."""
        complex_code = """
import os
import sys

def complex_function(data, config={}):
    result = ""
    for i in range(100):
        result += str(i)
    
    if os.path.exists("test"):
        print("exists")
    
    return result
"""
        
        result = validator.validate_method(complex_code, "python")
        
        # Should have warnings but not necessarily fail
        assert len(result.warnings) > 0
        assert any("system module" in w.lower() for w in result.warnings)
    
    def test_validation_result_immutability(self):
        """Test that ValidationResult operations don't affect other instances."""
        result1 = ValidationResult()
        result2 = ValidationResult()
        
        result1.add_error("Error 1")
        result2.add_warning("Warning 2")
        
        assert len(result1.errors) == 1
        assert len(result1.warnings) == 0
        assert len(result2.errors) == 0
        assert len(result2.warnings) == 1
        
        assert result1.is_valid is False
        assert result2.is_valid is True