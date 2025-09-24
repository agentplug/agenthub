"""
Parameter Processing Utilities for AgentHub

General-purpose utilities for parameter validation, conversion, and formatting
that can be reused across different components.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class ParameterProcessor:
    """General parameter processing utilities."""

    @staticmethod
    def validate_parameters(
        params: dict[str, Any], schema: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Validate and clean parameters according to schema.

        Args:
            params: Extracted parameters
            schema: Parameter schema with type and requirement info

        Returns:
            Validated and cleaned parameters
        """
        validated = {}

        for param_name, param_details in schema.items():
            if param_name in params:
                value = params[param_name]
                # Basic type validation and conversion
                validated[param_name] = ParameterProcessor.convert_parameter_value(
                    value, param_details.get("type", "string")
                )
            elif not param_details.get("optional", False):
                # Required parameter not provided
                logger.warning(f"Required parameter '{param_name}' not provided")
                validated[param_name] = None
            else:
                # Optional parameter with default
                validated[param_name] = param_details.get("default")

        return validated

    @staticmethod
    def convert_parameter_value(value: Any, param_type: str) -> Any:
        """
        Convert parameter value to appropriate type.

        Args:
            value: The value to convert
            param_type: Target type (string, int, float, bool, list)

        Returns:
            Converted value
        """
        if value is None:
            return None

        try:
            if param_type == "string" or param_type == "str":
                return str(value)
            elif param_type == "integer" or param_type == "int":
                return int(value)
            elif param_type == "float":
                return float(value)
            elif param_type == "boolean" or param_type == "bool":
                if isinstance(value, bool):
                    return value
                return str(value).lower() in ("true", "yes", "1", "on", "enable")
            elif param_type == "list":
                if isinstance(value, list):
                    return value
                elif isinstance(value, str):
                    return [item.strip() for item in value.split(",")]
                else:
                    return [value]
            else:
                return value
        except (ValueError, TypeError) as e:
            logger.warning(
                f"Failed to convert parameter value {value} to {param_type}: {e}"
            )
            return value

    @staticmethod
    def format_parameter_info(parameters: dict[str, Any]) -> str:
        """
        Format parameter information for LLM consumption.

        Args:
            parameters: Parameter definitions

        Returns:
            Formatted parameter information string
        """
        param_info = []

        for param_name, param_details in parameters.items():
            param_type = param_details.get("type", "unknown")
            param_desc = param_details.get("description", "No description")
            required = not param_details.get("optional", False)
            required_str = "required" if required else "optional"
            param_info.append(
                f"  - {param_name} ({param_type}, {required_str}): {param_desc}"
            )

        return "\n".join(param_info) if param_info else "  - No parameters"

    @staticmethod
    def format_options_for_llm(options: list[dict[str, Any]]) -> str:
        """
        Format options information for LLM consumption.

        Args:
            options: List of options with metadata

        Returns:
            Formatted options information string
        """
        option_descriptions = []

        for option in options:
            name = option.get("name", "unknown")
            description = option.get("description", "No description available")
            metadata = option.get("metadata", {})

            # Format metadata information
            metadata_info = []
            for key, value in metadata.items():
                metadata_info.append(f"  - {key}: {value}")

            metadata_str = (
                "\n".join(metadata_info) if metadata_info else "  - No metadata"
            )

            option_descriptions.append(
                f"Option: {name}\n"
                f"Description: {description}\n"
                f"Metadata:\n{metadata_str}"
            )

        return "\n\n".join(option_descriptions)

    @staticmethod
    def extract_parameter_schema(method_parameters: dict[str, Any]) -> dict[str, str]:
        """
        Extract simplified parameter schema for validation.

        Args:
            method_parameters: Full parameter definitions

        Returns:
            Simplified schema mapping parameter names to types
        """
        schema = {}
        for param_name, param_details in method_parameters.items():
            schema[param_name] = param_details.get("type", "string")
        return schema
