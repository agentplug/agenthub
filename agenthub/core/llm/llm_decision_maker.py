"""
Generalized LLM Decision Maker for AgentHub

A reusable LLM-powered decision making component that can be used for any
choice scenario, not just agent method selection.
"""

import json
import logging
from dataclasses import dataclass
from typing import Any

from .llm_service import CoreLLMService, get_shared_llm_service

logger = logging.getLogger(__name__)


@dataclass
class DecisionResult:
    """Result of a decision making process."""

    selected_option: str
    confidence: float
    reasoning: str
    all_options_considered: list[dict[str, Any]]


@dataclass
class StructuredDataResult:
    """Result of structured data extraction."""

    extracted_data: dict[str, Any]
    confidence: float
    reasoning: str
    validation_errors: list[str]


class LLMDecisionMaker:
    """
    General-purpose LLM-powered decision making component.

    This component can be reused for any decision scenario:
    - Agent method selection
    - Tool selection
    - Strategy selection
    - Any other choice-based scenarios
    """

    def __init__(self, llm_service: CoreLLMService | None = None):
        """
        Initialize the LLM Decision Maker.

        Args:
            llm_service: Optional LLM service instance. If None, uses shared instance.
        """
        self.llm_service = llm_service or get_shared_llm_service()

    def make_decision(
        self,
        query: str,
        options: list[dict[str, Any]],
        selection_criteria: str,
        context: dict[str, Any] | None = None,
        custom_prompt: str | None = None,
    ) -> DecisionResult:
        """
        Make a decision by selecting the best option from a list.

        Args:
            query: The user's query or request
            options: List of available options with metadata
            selection_criteria: Description of what makes a good selection
            context: Optional context information
            custom_prompt: Optional custom prompt template

        Returns:
            DecisionResult with selected option, confidence, and reasoning
        """
        if not options:
            return DecisionResult("", 0.0, "No options available", [])

        # Prepare options information for LLM
        options_info = self._prepare_options_info(options)

        # Create system prompt
        system_prompt = custom_prompt or self._create_generic_selection_prompt(
            selection_criteria
        )

        # Create user prompt
        user_prompt = self._create_decision_user_prompt(query, options_info, context)

        try:
            # Get LLM response
            response = self.llm_service.generate(
                user_prompt, system_prompt=system_prompt, return_json=True
            )

            # Debug: Log the raw response
            logger.debug(f"LLM Decision Response: {repr(response)}")

            # Check if response is empty or None
            if not response or response.strip() == "":
                logger.warning("LLM returned empty response")
                return DecisionResult(
                    options[0].get("name", ""), 0.0, "Empty response from LLM", options
                )

            # Parse response - try direct parsing first, then extract JSON if needed
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                # Try to extract JSON from response that might have extra text
                result = self._extract_json_from_response(response)

            selected_option = result.get("selected_option", "")
            confidence = result.get("confidence", 0.0)
            reasoning = result.get("reasoning", "No reasoning provided")

            # Validate selected option exists
            if selected_option not in [opt.get("name", "") for opt in options]:
                logger.warning(f"LLM selected invalid option: {selected_option}")
                return DecisionResult(
                    "", 0.0, f"Invalid option selected: {selected_option}", options
                )

            return DecisionResult(selected_option, confidence, reasoning, options)

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in decision making: {e}")
            logger.error(f"Raw response: {repr(response)}")
            # Fallback to first option
            return DecisionResult(
                options[0].get("name", ""), 0.0, f"JSON parsing failed: {e}", options
            )
        except Exception as e:
            logger.error(f"Error in decision making: {e}")
            response_info = repr(response) if "response" in locals() else "No response"
            logger.error(f"Raw response: {response_info}")
            # Fallback to first option
            return DecisionResult(
                options[0].get("name", ""), 0.0, f"Fallback due to error: {e}", options
            )

    def extract_structured_data(
        self,
        query: str,
        schema: dict[str, Any],
        extraction_instructions: str,
        context: dict[str, Any] | None = None,
        custom_prompt: str | None = None,
    ) -> StructuredDataResult:
        """
        Extract structured data from natural language query.

        Args:
            query: The user's natural language query
            schema: Schema defining the expected data structure
            extraction_instructions: Instructions for extraction
            context: Optional context information
            custom_prompt: Optional custom prompt template

        Returns:
            StructuredDataResult with extracted data and validation info
        """
        # Create system prompt
        system_prompt = custom_prompt or self._create_generic_extraction_prompt(
            extraction_instructions
        )

        # Create user prompt
        user_prompt = self._create_extraction_user_prompt(query, schema, context)

        try:
            # Get LLM response
            response = self.llm_service.generate(
                user_prompt, system_prompt=system_prompt, return_json=True
            )

            # Debug: Log the raw response
            logger.debug(f"LLM Extraction Response: {repr(response)}")

            # Check if response is empty or None
            if not response or response.strip() == "":
                logger.warning("LLM returned empty response for data extraction")
                return StructuredDataResult(
                    {}, 0.0, "Empty response from LLM", ["Empty response from LLM"]
                )

            # Parse response - try direct parsing first, then extract JSON if needed
            try:
                result = json.loads(response)
            except json.JSONDecodeError:
                # Try to extract JSON from response that might have extra text
                result = self._extract_json_from_response(response)

            extracted_data = result.get("extracted_data", {})
            confidence = result.get("confidence", 0.0)
            reasoning = result.get("reasoning", "No reasoning provided")

            # Validate extracted data
            validation_errors = self._validate_extracted_data(extracted_data, schema)

            return StructuredDataResult(
                extracted_data, confidence, reasoning, validation_errors
            )

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error in data extraction: {e}")
            logger.error(f"Raw response: {repr(response)}")
            return StructuredDataResult(
                {}, 0.0, f"JSON parsing failed: {e}", [f"JSON parsing failed: {e}"]
            )
        except Exception as e:
            logger.error(f"Error in data extraction: {e}")
            response_info = repr(response) if "response" in locals() else "No response"
            logger.error(f"Raw response: {response_info}")
            return StructuredDataResult(
                {}, 0.0, f"Fallback due to error: {e}", [f"Extraction failed: {e}"]
            )

    def _prepare_options_info(self, options: list[dict[str, Any]]) -> str:
        """Prepare options information for LLM consumption."""
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

    def _create_generic_selection_prompt(self, selection_criteria: str) -> str:
        """Create generic selection prompt template."""
        return (
            "You are an intelligent selection assistant. Your task is to "
            "analyze a user query and select the most appropriate option from a "
            "list of available options.\n\n"
            "You must respond with a JSON object containing:\n"
            '- "reasoning": A brief explanation of why this option was selected\n'
            '- "selected_option": The name of the most appropriate option\n'
            '- "confidence": A confidence score between 0.0 and 1.0\n\n'
            f"Selection criteria: {selection_criteria}\n\n"
            "Consider the following factors when selecting an option:\n"
            "1. Semantic similarity between the query and option description\n"
            "2. Compatibility with user intent\n"
            "3. Option purpose alignment with user needs\n"
            "4. Confidence level based on clarity of the match\n\n"
            "If no option is clearly appropriate, select the most general option "
            "and provide a low confidence score.\n\n"
            "CORRECT Output format (use this exact format):\n"
            """{
            "reasoning": "explanation of selection",
            "selected_option": "option_name",
            "confidence": 0.95
            }\n\n"""
            "INCORRECT Output format (DO NOT use):\n"
            "```json\n{...}\n```\n"
            "```\n{...}\n```\n"
            "Just the reasoning without JSON structure\n"
            "Missing required fields (reasoning, selected_option, confidence)"
        )

    def _create_generic_extraction_prompt(self, extraction_instructions: str) -> str:
        """Create generic extraction prompt template."""
        return (
            "You are an intelligent data extraction assistant. Your task is to "
            "analyze a user query and extract structured data according to the "
            "provided schema.\n\n"
            "You must respond with a JSON object containing:\n"
            '- "reasoning": A brief explanation of how data was extracted\n'
            '- "extracted_data": A dictionary of extracted data\n'
            '- "confidence": A confidence score between 0.0 and 1.0\n\n'
            f"Extraction instructions: {extraction_instructions}\n\n"
            "Guidelines for data extraction:\n"
            "1. Extract only the data that is clearly present in the query\n"
            "2. Use appropriate data types (string, number, boolean, list)\n"
            "3. Provide reasonable defaults for missing optional data\n"
            "4. Be conservative with confidence scores\n\n"
            "CORRECT Output format (use this exact format):\n"
            """{
            "reasoning": "explanation of extraction",
            "extracted_data": {"key": "value"},
            "confidence": 0.95
            }\n\n"""
            "INCORRECT Output format (DO NOT use):\n"
            "```json\n{...}\n```\n"
            "```\n{...}\n```\n"
            "Just the extracted data without JSON structure\n"
            "Missing required fields (reasoning, extracted_data, confidence)\n"
            "Invalid JSON syntax"
        )

    def _create_decision_user_prompt(
        self, query: str, options_info: str, context: dict[str, Any] | None = None
    ) -> str:
        """Create user prompt for decision making."""
        prompt = f"""User Query: "{query}"

Available Options:
{options_info}"""

        if context:
            prompt += f"\n\nContext: {json.dumps(context, indent=2)}"

        return prompt

    def _create_extraction_user_prompt(
        self, query: str, schema: dict[str, Any], context: dict[str, Any] | None = None
    ) -> str:
        """Create user prompt for data extraction."""
        prompt = f"""User Query: "{query}"

Expected Schema:
{json.dumps(schema, indent=2)}"""

        if context:
            prompt += f"\n\nContext: {json.dumps(context, indent=2)}"

        return prompt

    def _validate_extracted_data(
        self, extracted_data: dict[str, Any], schema: dict[str, Any]
    ) -> list[str]:
        """Validate extracted data against schema."""
        errors = []

        for key, expected_type in schema.items():
            if key not in extracted_data:
                errors.append(f"Missing required field: {key}")
            else:
                # Basic type validation
                value = extracted_data[key]
                if expected_type == "string" and not isinstance(value, str):
                    errors.append(f"Field '{key}' should be string, got {type(value)}")
                elif expected_type == "number" and not isinstance(value, int | float):
                    errors.append(f"Field '{key}' should be number, got {type(value)}")
                elif expected_type == "boolean" and not isinstance(value, bool):
                    errors.append(f"Field '{key}' should be boolean, got {type(value)}")

        return errors

    def _extract_json_from_response(self, response: str) -> dict[str, Any]:
        """
        Try to extract JSON from response that might contain extra text.

        Args:
            response: Raw LLM response

        Returns:
            Parsed JSON dictionary

        Raises:
            json.JSONDecodeError: If no valid JSON can be extracted
        """
        import re

        # Try to find JSON object in the response
        json_pattern = r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}"
        matches = re.findall(json_pattern, response, re.DOTALL)

        for match in matches:
            try:
                result = json.loads(match)
                if isinstance(result, dict):
                    return result
            except json.JSONDecodeError:
                continue

        # If no JSON object found, try to find JSON array
        json_array_pattern = r"\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]"
        array_matches = re.findall(json_array_pattern, response, re.DOTALL)

        for match in array_matches:
            try:
                result = json.loads(match)
                if isinstance(result, dict):
                    return result
            except json.JSONDecodeError:
                continue

        # If still no valid JSON, raise error
        raise json.JSONDecodeError("No valid JSON found in response", response, 0)
