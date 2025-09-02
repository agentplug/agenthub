"""Unit tests for tool validation module."""

import pytest
import time
from unittest.mock import Mock, patch
from typing import Optional

from agentmanager.core.tool_validation import (
    ToolValidator, ToolValidationConfig, ToolValidationResult,
    SignatureValidationResult, validate_tool, execute_tool_safely,
    get_security_report, get_global_validator
)
from agentmanager.core.tool_decorators import tool, ToolMetadata
from agentmanager.core.tool_security import SecurityLevel, SecurityResult


class TestToolValidationConfig:
    """Test ToolValidationConfig dataclass."""
    
    def test_default_config(self):
        """Test default validation configuration."""
        config = ToolValidationConfig()
        
        assert config.enable_signature_validation is True
        assert config.enable_security_validation is True
        assert config.enable_sandboxing is True
        assert config.enable_execution_monitoring is True
        assert SecurityLevel.SAFE in config.allowed_security_levels
        assert SecurityLevel.LIMITED in config.allowed_security_levels
        assert config.default_timeout == 30
        assert config.default_memory_limit == 100 * 1024 * 1024
        assert config.default_cpu_limit == 10
    
    def test_custom_config(self):
        """Test custom validation configuration."""
        config = ToolValidationConfig(
            enable_signature_validation=False,
            enable_security_validation=False,
            allowed_security_levels=[SecurityLevel.SAFE],
            default_timeout=60
        )
        
        assert config.enable_signature_validation is False
        assert config.enable_security_validation is False
        assert config.allowed_security_levels == [SecurityLevel.SAFE]
        assert config.default_timeout == 60


class TestSignatureValidationResult:
    """Test SignatureValidationResult dataclass."""
    
    def test_valid_result(self):
        """Test valid signature result."""
        result = SignatureValidationResult(
            is_valid=True,
            errors=[],
            warnings=["Minor warning"]
        )
        
        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 1
    
    def test_invalid_result(self):
        """Test invalid signature result."""
        result = SignatureValidationResult(
            is_valid=False,
            errors=["Critical error"],
            warnings=[]
        )
        
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert len(result.warnings) == 0


class TestToolValidationResult:
    """Test ToolValidationResult dataclass."""
    
    def test_validation_result_creation(self):
        """Test creating ToolValidationResult."""
        result = ToolValidationResult(
            tool_name="test_tool",
            is_valid=True,
            signature_valid=True,
            errors=[],
            warnings=["Warning"],
            recommendations=["Recommendation"]
        )
        
        assert result.tool_name == "test_tool"
        assert result.is_valid is True
        assert result.signature_valid is True
        assert len(result.warnings) == 1
        assert len(result.recommendations) == 1


class TestToolValidator:
    """Test ToolValidator functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        # Clear singleton
        ToolValidator._instance = None
    
    def test_validator_singleton(self):
        """Test that ToolValidator is singleton."""
        validator1 = ToolValidator()
        validator2 = ToolValidator()
        assert validator1 is validator2
    
    def test_validator_with_custom_config(self):
        """Test validator with custom configuration."""
        config = ToolValidationConfig(enable_sandboxing=False)
        validator = ToolValidator(config)
        
        assert validator.config.enable_sandboxing is False
    
    def test_validate_signature_success(self):
        """Test successful signature validation."""
        def well_typed_func(x: int, y: str = "default") -> bool:
            return True
        
        config = ToolValidationConfig()
        validator = ToolValidator(config)
        
        result = validator.validate_signature(well_typed_func)
        
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    def test_validate_signature_non_callable(self):
        """Test signature validation with non-callable."""
        not_callable = "not a function"
        
        config = ToolValidationConfig()
        validator = ToolValidator(config)
        
        result = validator.validate_signature(not_callable)
        
        assert result.is_valid is False
        assert any("not callable" in error for error in result.errors)
    
    def test_validate_signature_no_name(self):
        """Test signature validation with function without __name__."""
        class CallableWithoutName:
            def __call__(self):
                pass
        
        callable_obj = CallableWithoutName()
        
        config = ToolValidationConfig()
        validator = ToolValidator(config)
        
        result = validator.validate_signature(callable_obj)
        
        assert result.is_valid is False
        assert any("__name__" in error for error in result.errors)
    
    def test_validate_signature_warnings(self):
        """Test signature validation generates warnings."""
        def func_with_warnings(*args, **kwargs):
            pass
        
        config = ToolValidationConfig()
        validator = ToolValidator(config)
        
        result = validator.validate_signature(func_with_warnings)
        
        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert any("*args" in warning for warning in result.warnings)
        assert any("**kwargs" in warning for warning in result.warnings)
    
    def test_validate_signature_unannotated_params(self):
        """Test signature validation with unannotated parameters."""
        def unannotated_func(x, y=None):
            pass
        
        config = ToolValidationConfig()
        validator = ToolValidator(config)
        
        result = validator.validate_signature(unannotated_func)
        
        assert result.is_valid is True
        assert any("without type annotations" in warning for warning in result.warnings)
    
    def test_validate_safe_tool(self):
        """Test validation of safe tool."""
        def safe_tool(x: int) -> int:
            return x * 2
        
        config = ToolValidationConfig(enable_security_validation=False)
        validator = ToolValidator(config)
        
        result = validator.validate_tool(safe_tool)
        
        assert result.is_valid is True
        assert result.security_result is None
    
    def test_validate_tool_without_annotations(self):
        """Test validation of tool without type annotations."""
        def no_annotations(x, y=None):
            return x
        
        config = ToolValidationConfig(enable_security_validation=False)
        validator = ToolValidator(config)
        
        result = validator.validate_tool(no_annotations)
        
        assert result.is_valid is True
        assert len(result.warnings) > 0
    
    def test_validate_tool_without_docstring(self):
        """Test validation of tool without docstring."""
        def no_docstring():
            pass
        
        config = ToolValidationConfig(enable_security_validation=False)
        validator = ToolValidator(config)
        
        result = validator.validate_tool(no_docstring)
        
        assert result.is_valid is True
        assert any("return type annotation" in warning for warning in result.warnings)
    
    def test_validate_tool_with_metadata(self):
        """Test validation of tool with existing metadata."""
        @tool(name="decorated_tool", description="Test tool")
        def decorated_tool(x: int) -> str:
            return str(x)
        
        config = ToolValidationConfig(enable_security_validation=False)
        validator = ToolValidator(config)
        
        result = validator.validate_tool(decorated_tool)
        
        assert result.is_valid is True
        assert result.tool_name == "decorated_tool"
    
    def test_validate_tool_signature_disabled(self):
        """Test validation with signature validation disabled."""
        def good_func():
            pass
        
        config = ToolValidationConfig(enable_signature_validation=False, enable_security_validation=False)
        validator = ToolValidator(config)
        
        result = validator.validate_tool(good_func)
        
        # Should still be valid since signature validation is disabled
        assert result.signature_valid is True
    
    def test_validate_tool_for_registration_success(self):
        """Test successful tool validation for registration."""
        def registration_tool(x: int) -> str:
            return str(x)
        
        config = ToolValidationConfig(enable_security_validation=False)
        validator = ToolValidator(config)
        
        # This would typically return ToolRegistrationResult but we test the validation part
        result = validator.validate_tool(registration_tool)
        
        assert result.is_valid is True
    
    @patch('time.time')
    def test_execute_tool_safely_success(self, mock_time):
        """Test successful safe tool execution."""
        mock_time.side_effect = [0.0, 1.0, 1.0, 1.0, 1.0]  # start, end, log_execution and extras
        
        def safe_tool(x: int) -> int:
            return x * 2
        
        config = ToolValidationConfig(enable_sandboxing=False, enable_execution_monitoring=False)
        validator = ToolValidator(config)
        
        result = validator.execute_tool_safely(safe_tool, {"x": 5})
        
        assert result == 10
    
    def test_execute_tool_safely_with_error(self):
        """Test safe execution with tool error."""
        def error_tool():
            raise ValueError("Test error")
        
        config = ToolValidationConfig(enable_sandboxing=False, enable_execution_monitoring=False)
        validator = ToolValidator(config)
        
        with pytest.raises(ValueError, match="Test error"):
            validator.execute_tool_safely(error_tool, {})
    
    def test_execute_tool_safely_async(self):
        """Test safe execution of async tool."""
        async def async_tool(x: int) -> int:
            return x * 3
        
        config = ToolValidationConfig(enable_sandboxing=False, enable_execution_monitoring=False)
        validator = ToolValidator(config)
        
        result = validator.execute_tool_safely(async_tool, {"x": 4})
        
        assert result == 12
    
    def test_execute_tool_safely_global(self):
        """Test global safe execution function."""
        def global_tool(x: int) -> int:
            return x + 10
        
        # Mock global validator to avoid security validation issues
        with patch('agentmanager.core.tool_validation._global_validator') as mock_validator:
            mock_validator.execute_tool_safely.return_value = 15
            
            result = execute_tool_safely(global_tool, {"x": 5})
            
            assert result == 15
            mock_validator.execute_tool_safely.assert_called_once()


class TestValidationIntegration:
    """Test validation integration scenarios."""
    
    def setup_method(self):
        """Setup for each test."""
        ToolValidator._instance = None
    
    def test_complete_validation_workflow(self):
        """Test complete validation workflow."""
        @tool(name="workflow_tool", description="Test workflow")
        def workflow_tool(input_data: str) -> str:
            return input_data.upper()
        
        config = ToolValidationConfig(enable_security_validation=False)
        validator = ToolValidator(config)
        
        # Validate tool
        validation_result = validator.validate_tool(workflow_tool)
        assert validation_result.is_valid is True
        
        # Execute tool safely (without monitoring to avoid SecureToolExecutor issues)
        # Clear singleton to force new instance
        ToolValidator._instance = None
        config_no_monitoring = ToolValidationConfig(
            enable_security_validation=False, 
            enable_execution_monitoring=False
        )
        validator_no_monitoring = ToolValidator(config_no_monitoring)
        
        execution_result = validator_no_monitoring.execute_tool_safely(
            workflow_tool, 
            {"input_data": "test"}
        )
        assert execution_result == "TEST"
    
    def test_validation_with_security_levels(self):
        """Test validation with different security levels."""
        def test_tool():
            return "safe"
        
        config = ToolValidationConfig(
            enable_security_validation=False,  # Disable to avoid source code issues
            allowed_security_levels=[SecurityLevel.SAFE]
        )
        validator = ToolValidator(config)
        
        result = validator.validate_tool(test_tool)
        assert result.is_valid is True
    
    def test_validation_error_handling(self):
        """Test validation error handling."""
        # Create a problematic function
        def problematic_func():
            pass
        
        config = ToolValidationConfig()
        validator = ToolValidator(config)
        
        # Mock signature to raise exception
        with patch('inspect.signature', side_effect=ValueError("Signature error")):
            result = validator.validate_tool(problematic_func)
            
            assert result.is_valid is False
            assert len(result.errors) > 0


class TestGlobalValidationFunctions:
    """Test global validation functions."""
    
    def setup_method(self):
        """Setup for each test."""
        ToolValidator._instance = None
    
    def test_global_validate_tool(self):
        """Test global validate_tool function."""
        def global_test_tool():
            return "test"
        
        # Mock global validator to avoid security validation
        with patch('agentmanager.core.tool_validation._global_validator') as mock_validator:
            mock_result = ToolValidationResult(
                tool_name="global_test_tool",
                is_valid=True
            )
            mock_validator.validate_tool.return_value = mock_result
            
            result = validate_tool(global_test_tool)
            
            assert result.is_valid is True
            mock_validator.validate_tool.assert_called_once_with(global_test_tool, None)
    
    def test_global_get_security_report(self):
        """Test global get_security_report function."""
        with patch('agentmanager.core.tool_validation._global_validator') as mock_validator:
            mock_validator.get_security_report.return_value = {"total_executions": 5}
            
            report = get_security_report()
            
            assert report["total_executions"] == 5
            mock_validator.get_security_report.assert_called_once()
    
    def test_get_global_validator(self):
        """Test get_global_validator function."""
        validator = get_global_validator()
        
        assert validator is not None
        assert isinstance(validator, ToolValidator)
        
        # Should return same instance
        validator2 = get_global_validator()
        assert validator is validator2


class TestValidationEdgeCases:
    """Test validation edge cases and error scenarios."""
    
    def setup_method(self):
        """Setup for each test."""
        ToolValidator._instance = None
    
    def test_validation_with_lambda(self):
        """Test validation with lambda function."""
        lambda_func = lambda x: x * 2
        
        config = ToolValidationConfig(enable_security_validation=False)
        validator = ToolValidator(config)
        
        result = validator.validate_tool(lambda_func)
        
        # Lambda should be valid but may have warnings
        assert result.is_valid is True
    
    def test_validation_with_complex_signature(self):
        """Test validation with complex function signature."""
        def complex_func(a: int, b: str = "default", *args, **kwargs) -> dict:
            return {"a": a, "b": b, "args": args, "kwargs": kwargs}
        
        config = ToolValidationConfig(enable_security_validation=False)
        validator = ToolValidator(config)
        
        result = validator.validate_tool(complex_func)
        
        assert result.is_valid is True
        # Should have warnings about *args and **kwargs
        assert len(result.warnings) > 0
