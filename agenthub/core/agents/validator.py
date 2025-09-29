"""Interface validator for agent interfaces."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class InterfaceValidationError(Exception):
    """Raised when agent interface validation fails."""

    pass


class InterfaceValidator:
    """Validate agent interfaces and methods."""

    def __init__(self) -> None:
        """Initialize the interface validator."""
        pass

    def validate_interface(self, interface: dict) -> bool:
        """
        Validate an agent interface structure.

        Args:
            interface: Interface section from agent manifest

        Returns:
            True if interface is valid

        Raises:
            InterfaceValidationError: If interface is invalid
        """
        if not isinstance(interface, dict):
            raise InterfaceValidationError("Interface must be a dictionary")

        # Check if methods section exists
        if "methods" not in interface:
            raise InterfaceValidationError("Interface must contain 'methods' section")

        methods = interface["methods"]
        if not isinstance(methods, dict):
            raise InterfaceValidationError("Methods must be a dictionary")

        if not methods:
            raise InterfaceValidationError("No methods defined in interface")

        # Validate each method
        for method_name, method_def in methods.items():
            self._validate_method_definition(method_name, method_def)

        return True

    def _validate_method_definition(self, method_name: str, method_def: dict) -> None:
        """
        Validate a single method definition.

        Args:
            method_name: Name of the method
            method_def: Method definition

        Raises:
            InterfaceValidationError: If method definition is invalid
        """
        if not isinstance(method_def, dict):
            raise InterfaceValidationError(
                f"Method '{method_name}' definition must be a dictionary"
            )

        # Check required description field
        if "description" not in method_def:
            raise InterfaceValidationError(
                f"Method '{method_name}' missing required 'description' field"
            )

        # Validate optional parameters section
        if "parameters" in method_def:
            parameters = method_def["parameters"]
            if parameters is not None and not isinstance(parameters, dict):
                raise InterfaceValidationError(
                    f"Method '{method_name}' parameters must be a dictionary or null"
                )

        # Validate optional returns section
        if "returns" in method_def:
            returns = method_def["returns"]
            if not isinstance(returns, dict):
                raise InterfaceValidationError(
                    f"Method '{method_name}' returns must be a dictionary"
                )

    def validate_method_exists(self, interface: dict, method_name: str) -> bool:
        """
        Check if a method exists in the interface.

        Args:
            interface: Interface section from agent manifest
            method_name: Name of the method to check

        Returns:
            True if method exists, False otherwise
        """
        if "methods" not in interface:
            return False

        methods = interface["methods"]
        if not isinstance(methods, dict):
            return False

        return method_name in methods

    def get_method_info(self, interface: dict, method_name: str) -> dict[str, Any]:
        """
        Get information about a specific method.

        Args:
            interface: Interface section from agent manifest
            method_name: Name of the method

        Returns:
            Method definition dictionary

        Raises:
            InterfaceValidationError: If method doesn't exist
        """
        if not self.validate_method_exists(interface, method_name):
            raise InterfaceValidationError(
                f"Method '{method_name}' not found in interface"
            )

        method_info = interface["methods"][method_name]
        return method_info if isinstance(method_info, dict) else {}

    def get_available_methods(self, interface: dict) -> list[str]:
        """
        Get list of available method names.

        Args:
            interface: Interface section from agent manifest

        Returns:
            List of method names
        """
        if "methods" not in interface:
            return []

        methods = interface["methods"]
        if not isinstance(methods, dict):
            return []

        return list(methods.keys())
