"""
LLM Decision Engine for Phase 3.2 Intelligent Solve Method

Handles intelligent method selection and parameter extraction using LLM.
"""

import json
import logging
from typing import Any

from .llm_service import CoreLLMService, get_shared_llm_service

logger = logging.getLogger(__name__)


class LLMDecisionEngine:
    """
    LLM-powered decision engine for intelligent method selection and parameter
    extraction.

    Uses the existing CoreLLMService to analyze user queries and select the most
    appropriate agent method, then extract parameters from natural language.
    """

    def __init__(self, llm_service: CoreLLMService | None = None):
        """
        Initialize the LLM Decision Engine.

        Args:
            llm_service: Optional LLM service instance. If None, uses the shared
                        instance to avoid duplicate model detection logs.
        """
        self.llm_service = llm_service or get_shared_llm_service()

    def get_current_model(self) -> str:
        """
        Get the currently configured model name.

        Returns:
            str: Current model identifier in aisuite format
        """
        return self.llm_service.get_current_model()

    def select_method(
        self,
        query: str,
        agent_methods: list[dict[str, Any]],
        context: dict[str, Any] | None = None,
    ) -> tuple[str, float, str]:
        """
        Select the most appropriate method based on user query.

        Args:
            query: User's natural language query
            agent_methods: List of available methods with metadata
            context: Optional context information

        Returns:
            Tuple of (selected_method_name, confidence_score, reasoning)
        """
        if not agent_methods:
            return "", 0.0, "No methods available"

        # Prepare method information for LLM
        method_info = self._prepare_method_info(agent_methods)

        # Create system prompt for method selection
        system_prompt = self._create_method_selection_prompt()

        # Create user prompt with query and method information
        user_prompt = self._create_method_selection_user_prompt(
            query, method_info, context
        )

        try:
            # Get LLM response
            response = self.llm_service.generate(
                user_prompt, system_prompt=system_prompt, return_json=True
            )

            # Parse response
            result = json.loads(response)

            method_name = result.get("selected_method", "")
            confidence = result.get("confidence", 0.0)
            reasoning = result.get("reasoning", "No reasoning provided")

            # Validate method exists
            if method_name not in [m["name"] for m in agent_methods]:
                logger.warning(f"LLM selected invalid method: {method_name}")
                return "", 0.0, f"Invalid method selected: {method_name}"

            return method_name, confidence, reasoning

        except Exception as e:
            logger.error(f"Error in method selection: {e}")
            # Fallback to first method
            return agent_methods[0]["name"], 0.0, f"Fallback due to error: {e}"

    def extract_parameters(
        self,
        query: str,
        method_name: str,
        method_parameters: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], float, str]:
        """
        Extract parameters from natural language query for a specific method.

        Args:
            query: User's natural language query
            method_name: Name of the selected method
            method_parameters: Parameter definitions for the method
            context: Optional context information

        Returns:
            Tuple of (extracted_parameters, confidence_score, reasoning)
        """
        if not method_parameters:
            return {}, 1.0, "No parameters required"

        # Create system prompt for parameter extraction
        system_prompt = self._create_parameter_extraction_prompt()

        # Create user prompt with query and parameter information
        user_prompt = self._create_parameter_extraction_user_prompt(
            query, method_name, method_parameters, context
        )

        try:
            # Get LLM response
            response = self.llm_service.generate(
                user_prompt, system_prompt=system_prompt, return_json=True
            )
            print(response)

            # Parse response
            result = json.loads(response)

            parameters = result.get("parameters", {})
            confidence = result.get("confidence", 0.0)
            reasoning = result.get("reasoning", "No reasoning provided")

            # Validate extracted parameters
            validated_params = self._validate_extracted_parameters(
                parameters, method_parameters
            )

            return validated_params, confidence, reasoning

        except Exception as e:
            logger.error(f"Error in parameter extraction: {e}")
            # Fallback to empty parameters
            return {}, 0.0, f"Fallback due to error: {e}"

    def _prepare_method_info(self, methods: list[dict[str, Any]]) -> str:
        """Prepare method information for LLM consumption."""
        method_descriptions = []

        for method in methods:
            name = method.get("name", "unknown")
            description = method.get("description", "No description available")
            parameters = method.get("parameters", {})

            # Format parameter information
            param_info = []
            for param_name, param_details in parameters.items():
                param_type = param_details.get("type", "unknown")
                param_desc = param_details.get("description", "No description")
                required = not param_details.get("optional", False)
                required_str = "required" if required else "optional"
                param_info.append(
                    f"  - {param_name} ({param_type}, {required_str}): {param_desc}"
                )

            param_str = "\n".join(param_info) if param_info else "  - No parameters"

            method_descriptions.append(
                f"Method: {name}\n"
                f"Description: {description}\n"
                f"Parameters:\n{param_str}"
            )

        return "\n\n".join(method_descriptions)

    def _create_method_selection_prompt(self) -> str:
        """Create system prompt for method selection."""
        return (
            "You are an intelligent method selection assistant. Your task is to "
            "analyze a user query and select the most appropriate method from a "
            "list of available agent methods.\n\n"
            "You must respond with a JSON object containing:\n"
            '- "selected_method": The name of the most appropriate method\n'
            '- "confidence": A confidence score between 0.0 and 1.0\n'
            '- "reasoning": A brief explanation of why this method was selected\n\n'
            "Consider the following factors when selecting a method:\n"
            "1. Semantic similarity between the query and method description\n"
            "2. Parameter compatibility (can the required parameters be extracted "
            "from the query?)\n"
            "3. Method purpose alignment with user intent\n"
            "4. Confidence level based on clarity of the match\n\n"
            "If no method is clearly appropriate, select the most general method "
            "and provide a low confidence score."
        )

    def _create_method_selection_user_prompt(
        self, query: str, method_info: str, context: dict[str, Any] | None = None
    ) -> str:
        """Create user prompt for method selection."""
        prompt = f"""User Query: "{query}"

Available Methods:
{method_info}"""

        if context:
            prompt += f"\n\nContext: {json.dumps(context, indent=2)}"

        return prompt

    def _create_parameter_extraction_prompt(self) -> str:
        """Create system prompt for parameter extraction."""
        return (
            "You are an intelligent parameter extraction assistant. Your task is to "
            "analyze a user query and extract the appropriate parameters for a "
            "specific agent method.\n\n"
            "You must respond with a JSON object containing:\n"
            '- "parameters": A dictionary of parameter names and their extracted '
            "values\n"
            '- "confidence": A confidence score between 0.0 and 1.0 for the '
            "extraction\n"
            '- "reasoning": A brief explanation of how parameters were extracted\n\n'
            "Guidelines for parameter extraction:\n"
            "1. Extract only parameters that are defined in the method signature\n"
            "2. Use reasonable defaults for optional parameters when not specified\n"
            "3. Convert natural language values to appropriate types when possible\n"
            "4. If a required parameter cannot be extracted, set it to null and "
            "explain in reasoning\n"
            "5. Be conservative - only extract parameters you're confident about\n\n"
            "Parameter types to consider:\n"
            "- String: Extract text values as-is\n"
            "- Integer: Convert numeric values to integers\n"
            "- Boolean: Convert yes/no, true/false, enable/disable to boolean\n"
            "- List: Extract comma-separated or list-like values\n"
            "- File paths: Extract file references and paths"
        )

    def _create_parameter_extraction_user_prompt(
        self,
        query: str,
        method_name: str,
        method_parameters: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> str:
        """Create user prompt for parameter extraction."""
        # Format parameter information
        param_info = []
        for param_name, param_details in method_parameters.items():
            param_type = param_details.get("type", "unknown")
            param_desc = param_details.get("description", "No description")
            required = not param_details.get("optional", False)
            required_str = "required" if required else "optional"
            default = param_details.get("default", "No default")
            param_info.append(
                f"  - {param_name} ({param_type}, {required_str}): {param_desc} "
                f"(default: {default})"
            )

        param_str = "\n".join(param_info) if param_info else "  - No parameters"

        prompt = f"""User Query: "{query}"

Target Method: {method_name}

Method Parameters:
{param_str}"""

        if context:
            prompt += f"\n\nContext: {json.dumps(context, indent=2)}"

        return prompt

    def _validate_extracted_parameters(
        self, extracted_params: dict[str, Any], method_parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Validate and clean extracted parameters."""
        validated = {}

        for param_name, param_details in method_parameters.items():
            if param_name in extracted_params:
                value = extracted_params[param_name]
                # Basic type validation and conversion
                validated[param_name] = self._convert_parameter_value(
                    value, param_details.get("type", "string")
                )
            elif not param_details.get("optional", False):
                # Required parameter not provided
                logger.warning(f"Required parameter '{param_name}' not extracted")
                validated[param_name] = None
            else:
                # Optional parameter with default
                validated[param_name] = param_details.get("default")

        return validated

    def _convert_parameter_value(self, value: Any, param_type: str) -> Any:
        """Convert parameter value to appropriate type."""
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
