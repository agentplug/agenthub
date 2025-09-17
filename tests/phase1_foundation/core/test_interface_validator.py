"""Tests for InterfaceValidator class."""

import pytest

from agenthub.core.agents.validator import (
    InterfaceValidationError,
    InterfaceValidator,
)


class TestInterfaceValidator:
    """Test cases for InterfaceValidator class."""

    def test_init(self):
        """Test InterfaceValidator initialization."""
        validator = InterfaceValidator()
        assert validator is not None

    def test_validate_valid_interface(self):
        """Test validation of a valid interface."""
        validator = InterfaceValidator()

        interface = {
            "methods": {
                "test_method": {
                    "description": "Test method",
                    "parameters": {"input": {"type": "string", "required": True}},
                    "returns": {"type": "string"},
                }
            }
        }

        result = validator.validate_interface(interface)
        assert result is True

    def test_validate_missing_methods(self):
        """Test validation when methods section is missing."""
        validator = InterfaceValidator()

        interface = {"description": "No methods"}

        with pytest.raises(
            InterfaceValidationError, match="Interface must contain 'methods' section"
        ):
            validator.validate_interface(interface)

    def test_validate_invalid_methods_type(self):
        """Test validation when methods is not a dictionary."""
        validator = InterfaceValidator()

        interface = {"methods": "not_a_dict"}

        with pytest.raises(
            InterfaceValidationError, match="Methods must be a dictionary"
        ):
            validator.validate_interface(interface)

    def test_validate_empty_methods(self):
        """Test validation when methods dictionary is empty."""
        validator = InterfaceValidator()

        interface = {"methods": {}}

        with pytest.raises(InterfaceValidationError, match="No methods defined"):
            validator.validate_interface(interface)

    def test_validate_invalid_method_definition(self):
        """Test validation of invalid method definition."""
        validator = InterfaceValidator()

        interface = {"methods": {"invalid_method": "not_a_dict"}}

        with pytest.raises(
            InterfaceValidationError, match="definition must be a dictionary"
        ):
            validator.validate_interface(interface)

    def test_validate_method_missing_description(self):
        """Test validation when method is missing description."""
        validator = InterfaceValidator()

        interface = {
            "methods": {"test_method": {"parameters": {"input": {"type": "string"}}}}
        }

        with pytest.raises(
            InterfaceValidationError, match="missing required 'description'"
        ):
            validator.validate_interface(interface)

    def test_validate_invalid_parameters_type(self):
        """Test validation when parameters is not a dictionary."""
        validator = InterfaceValidator()

        interface = {
            "methods": {
                "test_method": {
                    "description": "Test method",
                    "parameters": "not_a_dict",
                }
            }
        }

        with pytest.raises(
            InterfaceValidationError, match="parameters must be a dictionary"
        ):
            validator.validate_interface(interface)

    def test_validate_invalid_returns_type(self):
        """Test validation when returns is not a dictionary."""
        validator = InterfaceValidator()

        interface = {
            "methods": {
                "test_method": {"description": "Test method", "returns": "not_a_dict"}
            }
        }

        with pytest.raises(
            InterfaceValidationError, match="returns must be a dictionary"
        ):
            validator.validate_interface(interface)

    def test_validate_method_exists_valid(self):
        """Test validation that a method exists in interface."""
        validator = InterfaceValidator()

        interface = {
            "methods": {
                "existing_method": {"description": "Exists"},
                "another_method": {"description": "Also exists"},
            }
        }

        result = validator.validate_method_exists(interface, "existing_method")
        assert result is True

    def test_validate_method_exists_invalid(self):
        """Test validation when method doesn't exist in interface."""
        validator = InterfaceValidator()

        interface = {"methods": {"existing_method": {"description": "Exists"}}}

        result = validator.validate_method_exists(interface, "nonexistent_method")
        assert result is False

    def test_get_method_info(self):
        """Test getting method information."""
        validator = InterfaceValidator()

        interface = {
            "methods": {
                "test_method": {
                    "description": "Test method description",
                    "parameters": {"input": {"type": "string", "required": True}},
                    "returns": {"type": "string"},
                }
            }
        }

        method_info = validator.get_method_info(interface, "test_method")

        assert method_info["description"] == "Test method description"
        assert "parameters" in method_info
        assert "returns" in method_info

    def test_get_method_info_nonexistent(self):
        """Test getting method info for nonexistent method."""
        validator = InterfaceValidator()

        interface = {"methods": {"existing": {"description": "Exists"}}}

        with pytest.raises(
            InterfaceValidationError, match="Method 'nonexistent' not found"
        ):
            validator.get_method_info(interface, "nonexistent")

    def test_get_available_methods(self):
        """Test getting list of available methods."""
        validator = InterfaceValidator()

        interface = {
            "methods": {
                "method1": {"description": "First method"},
                "method2": {"description": "Second method"},
                "method3": {"description": "Third method"},
            }
        }

        methods = validator.get_available_methods(interface)

        assert len(methods) == 3
        assert "method1" in methods
        assert "method2" in methods
        assert "method3" in methods
