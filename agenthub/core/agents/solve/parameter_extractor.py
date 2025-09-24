"""
Agent Parameter Extractor for Solve Functionality

Solve-specific component that uses the generalized LLM decision maker
to extract parameters for agent methods from natural language queries.
"""

import logging
from typing import Any

from ...llm.llm_decision_maker import LLMDecisionMaker
from ...llm.parameter_processor import ParameterProcessor

logger = logging.getLogger(__name__)


class AgentParameterExtractor:
    """
    Solve-specific parameter extraction for agent methods using generalized
    LLM decision maker.
    """

    def __init__(self, llm_decision_maker: LLMDecisionMaker | None = None):
        """
        Initialize the agent parameter extractor.

        Args:
            llm_decision_maker: Optional LLM decision maker instance
        """
        self.decision_maker = llm_decision_maker or LLMDecisionMaker()

    def extract_parameters(
        self,
        query: str,
        method_name: str,
        method_parameters: dict[str, Any],
        context: dict[str, Any] | None = None,
    ) -> tuple[dict[str, Any], float, str]:
        """
        Extract parameters from natural language query for a specific agent method.

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

        # Create parameter schema for extraction
        parameter_schema = self._create_parameter_schema(method_parameters)

        # Use generalized data extraction
        extraction_instructions = f"Extract parameters for agent method '{method_name}'"
        result = self.decision_maker.extract_structured_data(
            query=query,
            schema=parameter_schema,
            extraction_instructions=extraction_instructions,
            context=context,
            custom_prompt=self._create_parameter_extraction_prompt(),
        )

        # Validate and clean extracted parameters
        validated_params = ParameterProcessor.validate_parameters(
            result.extracted_data, method_parameters
        )

        return validated_params, result.confidence, result.reasoning

    def _create_parameter_schema(
        self, method_parameters: dict[str, Any]
    ) -> dict[str, str]:
        """Create simplified parameter schema for extraction."""
        schema = {}
        for param_name, param_details in method_parameters.items():
            schema[param_name] = param_details.get("type", "string")
        return schema

    def _create_parameter_extraction_prompt(self) -> str:
        """Create solve-specific parameter extraction prompt."""
        return (
            "You are an intelligent parameter extraction assistant. Your task is to "
            "analyze a user query and extract the appropriate parameters for a "
            "specific agent method.\n\n"
            "You must respond with a JSON object containing:\n"
            '- "reasoning": A brief explanation of how parameters were extracted\n'
            '- "extracted_data": A dictionary of parameter names and their extracted '
            "values\n"
            '- "confidence": A confidence score between 0.0 and 1.0 for the '
            "extraction\n\n"
            "Guidelines for parameter extraction:\n"
            "1. Extract only the data that is clearly present in the query\n"
            "2. Use appropriate data types (string, number, boolean, list)\n"
            "3. Provide reasonable defaults for missing optional data\n"
            "4. Be conservative with confidence scores\n"
            "5. If a required parameter cannot be extracted, set it to null\n\n"
            "CORRECT Output format (use this exact format):\n"
            """{
            "reasoning": "explanation of parameter extraction",
            "extracted_data": {"param_name": "value"},
            "confidence": 0.95
            }\n\n"""
            "INCORRECT Output format (DO NOT use):\n"
            "```json\n{...}\n```\n"
            "```\n{...}\n```\n"
            "Just the extracted data without JSON structure\n"
            "Missing required fields (reasoning, extracted_data, confidence)\n"
            "Invalid parameter names (not from method schema)\n"
            "Invalid JSON syntax"
        )
