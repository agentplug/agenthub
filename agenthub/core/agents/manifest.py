"""Manifest parser for agent.yaml files."""

import logging
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)


class ManifestValidationError(Exception):
    """Raised when agent manifest validation fails."""

    pass


class ManifestParser:
    """Parse and validate agent manifest files."""

    def __init__(self) -> None:
        """Initialize the manifest parser."""
        pass

    def parse_manifest(self, manifest_path: str) -> dict[str, Any]:
        """
        Parse and validate an agent manifest file.

        Args:
            manifest_path: Path to the agent.yaml file

        Returns:
            dict: Parsed and validated manifest data

        Raises:
            ManifestValidationError: If manifest is invalid or missing
        """
        manifest_file = Path(manifest_path)

        # Check if file exists
        if not manifest_file.exists():
            raise ManifestValidationError(f"Manifest file not found: {manifest_path}")

        try:
            # Parse YAML
            with open(manifest_file) as f:
                manifest_data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ManifestValidationError(f"Invalid YAML syntax: {e}") from e
        except Exception as e:
            raise ManifestValidationError(f"Error reading manifest: {e}") from e

        # Validate the parsed data
        if isinstance(manifest_data, dict):
            self._validate_manifest(manifest_data)
            return manifest_data
        else:
            raise ManifestValidationError("Manifest must be a valid JSON object")

    def _validate_manifest(self, manifest: dict) -> None:
        """
        Validate manifest structure and required fields.

        Args:
            manifest: Parsed manifest data

        Raises:
            ManifestValidationError: If validation fails
        """
        # Check required fields
        required_fields = ["name", "version", "description", "author", "interface"]
        for field in required_fields:
            if field not in manifest:
                raise ManifestValidationError(f"Missing required field: {field}")

        # Validate interface structure
        self._validate_interface(manifest["interface"])

    def _validate_interface(self, interface: dict) -> None:
        """
        Validate agent interface structure.

        Args:
            interface: Interface section from manifest

        Raises:
            ManifestValidationError: If interface is invalid
        """
        if not isinstance(interface, dict):
            raise ManifestValidationError(
                "Invalid interface structure: must be a dictionary"
            )

        if "methods" not in interface:
            raise ManifestValidationError("Interface must contain 'methods' section")

        methods = interface["methods"]
        if not isinstance(methods, dict):
            raise ManifestValidationError(
                "Invalid interface structure: methods must be a dictionary"
            )

        if not methods:
            raise ManifestValidationError("No methods defined in interface")

        # Validate each method
        for method_name, method_def in methods.items():
            self._validate_method(method_name, method_def)

    def _validate_method(self, method_name: str, method_def: dict) -> None:
        """
        Validate a single method definition.

        Args:
            method_name: Name of the method
            method_def: Method definition from manifest

        Raises:
            ManifestValidationError: If method definition is invalid
        """
        if not isinstance(method_def, dict):
            raise ManifestValidationError(
                f"Invalid method definition for '{method_name}': must be a dictionary"
            )

        # Check required fields for method
        if "description" not in method_def:
            raise ManifestValidationError(
                f"Method '{method_name}' missing required 'description' field"
            )

        # Validate optional parameters section
        if "parameters" in method_def:
            parameters = method_def["parameters"]
            if parameters is not None and not isinstance(parameters, dict):
                raise ManifestValidationError(
                    f"Method '{method_name}' parameters must be a dictionary or null"
                )

        # Validate optional returns section
        if "returns" in method_def:
            returns = method_def["returns"]
            if not isinstance(returns, dict):
                raise ManifestValidationError(
                    f"Method '{method_name}' returns must be a dictionary"
                )

    def get_methods(self, manifest: dict) -> list[str]:
        """
        Get list of method names from manifest.

        Args:
            manifest: Parsed manifest data

        Returns:
            List of method names
        """
        if "interface" not in manifest or "methods" not in manifest["interface"]:
            return []

        return list(manifest["interface"]["methods"].keys())

    def get_dependencies(self, manifest: dict) -> list[str]:
        """
        Get list of dependencies from manifest.

        Args:
            manifest: Parsed manifest data

        Returns:
            List of dependency specifications
        """
        dependencies = manifest.get("dependencies", [])
        if dependencies is None:
            return []

        return dependencies if isinstance(dependencies, list) else []
