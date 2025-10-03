"""Handles framework-level solve using solve-specific components."""

import logging
import time
from typing import Any

from ...interfaces import AgentWrapperProtocol, LLMServiceProtocol

logger = logging.getLogger(__name__)


class FrameworkSolveHandler:
    """Handles framework-level solve using solve-specific components."""

    def __init__(
        self,
        agent_wrapper: AgentWrapperProtocol,
        llm_service: LLMServiceProtocol | None = None,
    ) -> None:
        """Initialize framework solve handler."""
        self.agent_wrapper = agent_wrapper
        self.llm_service = llm_service

    def solve(
        self, query: str, context: dict[str, Any] | None = None, **kwargs: Any
    ) -> Any:
        """Execute framework-level solve using LLM method selection."""
        start_time = time.time()

        try:
            # Prepare context
            full_context = self._prepare_solve_context(context)

            # Get available methods with metadata
            agent_methods = self._get_method_metadata()

            if not agent_methods:
                return {
                    "error": "No methods available for this agent",
                    "execution_time": time.time() - start_time,
                }

            # Combined method selection and parameter extraction in single LLM call
            (
                method_name,
                extracted_params,
                confidence,
                param_confidence,
                reasoning,
                param_reasoning,
            ) = self._combined_method_selection_and_extraction(
                query, agent_methods, full_context
            )

            if not method_name:
                return {
                    "error": "Could not select appropriate method",
                    "execution_time": time.time() - start_time,
                }

            # Execute the selected method
            result = self.agent_wrapper.execute(method_name, extracted_params)

            execution_time = time.time() - start_time

            # Combine reasoning (for future use if needed)
            # combined_reasoning = f"Method selection: {reasoning}. "
            # f"Parameter extraction: {param_reasoning}"
            # combined_confidence = min(confidence, param_confidence)

            # Return the exact same format as direct method calls
            return result

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error in framework solve method: {e}")
            return {"error": str(e), "execution_time": execution_time}

    def _prepare_solve_context(
        self, context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Prepare context for solve operation."""
        full_context = context or {}

        # Add tool context
        full_context["available_tools"] = self.agent_wrapper.get_all_available_tools()
        full_context["tool_descriptions"] = self.agent_wrapper.get_tool_context_json()

        # Add knowledge context
        if self.agent_wrapper.is_knowledge_available():
            full_context["knowledge"] = self.agent_wrapper.get_knowledge()

        # Add agent info
        full_context["agent_info"] = {
            "name": self.agent_wrapper.agent_info.name,
            "namespace": self.agent_wrapper.agent_info.namespace,
            "methods": self.agent_wrapper.agent_info.methods,
        }

        return full_context

    def _get_method_metadata(self) -> list[dict[str, Any]]:
        """Get metadata for all available methods."""
        methods: list[dict[str, Any]] = []

        for method_name in self.agent_wrapper.agent_info.methods:
            try:
                method_info = self.agent_wrapper.agent_info.get_method_info(method_name)
                methods.append(
                    {
                        "name": method_name,
                        "description": method_info.get(
                            "description", f"Execute {method_name}"
                        ),
                        "parameters": method_info.get("parameters", {}),
                    }
                )
            except Exception as e:
                logger.warning(f"Could not get metadata for method {method_name}: {e}")
                methods.append(
                    {
                        "name": method_name,
                        "description": f"Execute {method_name}",
                        "parameters": {},
                    }
                )

        return methods

    def _combined_method_selection_and_extraction(
        self,
        query: str,
        agent_methods: list[dict[str, Any]],
        context: dict[str, Any],
    ) -> tuple[str, dict[str, Any], float, float, str, str]:
        """
        Combined method selection and parameter extraction in a single LLM call.

        Returns:
            Tuple of (method_name, extracted_params, method_confidence,
                     param_confidence, method_reasoning, param_reasoning)
        """
        # Create a combined prompt for both tasks
        combined_prompt = self._create_combined_prompt(query, agent_methods)

        # Use LLM service directly for combined extraction
        if self.llm_service is None:
            from ...llm.llm_service import get_shared_llm_service

            llm_service = get_shared_llm_service()
        else:
            llm_service = self.llm_service  # type: ignore[assignment]

        # Create the full prompt with user query
        full_prompt = f'{combined_prompt}\n\nUser Query: "{query}"'

        # Get LLM response directly
        response = llm_service.generate(full_prompt, return_json=True)

        # Log the combined LLM output
        logger.info("🔍 Combined Method Selection & Parameter Extraction LLM Output:")
        logger.info(f"   Query: {query}")
        logger.info(f"   Available methods: {[m['name'] for m in agent_methods]}")
        logger.info(f"   LLM Response: {response}")

        # Handle fallback response when LLM is unavailable
        if response == "AISuite not available":
            logger.warning("LLM service unavailable, using fallback method selection")
            # Use first available method as fallback
            if agent_methods:
                fallback_method = agent_methods[0]["name"]
                return (
                    fallback_method,
                    {},
                    0.5,  # Low confidence for fallback
                    0.5,
                    "Fallback selection due to LLM unavailability",
                    "No parameters extracted due to LLM unavailability",
                )
            else:
                return "", {}, 0.0, 0.0, "No methods available", "No methods available"

        # Parse the JSON response
        import json

        try:
            extracted_data = json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Raw response: {response}")
            return "", {}, 0.0, 0.0, "JSON parsing failed", "JSON parsing failed"

        # Extract results
        method_name = extracted_data.get("selected_method", "")
        method_reasoning = extracted_data.get(
            "method_reasoning", "No reasoning provided"
        )
        method_confidence = float(extracted_data.get("method_confidence", 0.0))
        extracted_params = extracted_data.get("extracted_parameters", {})
        param_reasoning = extracted_data.get(
            "parameter_reasoning", "No reasoning provided"
        )
        param_confidence = float(extracted_data.get("parameter_confidence", 0.0))

        logger.info(f"   Selected: {method_name} (confidence: {method_confidence})")
        logger.info(
            f"   Extracted: {extracted_params} (confidence: {param_confidence})"
        )

        return (
            method_name,
            extracted_params,
            method_confidence,
            param_confidence,
            method_reasoning,
            param_reasoning,
        )

    def _create_combined_prompt(
        self, query: str, agent_methods: list[dict[str, Any]]
    ) -> str:
        """Create a combined prompt for method selection and parameter extraction."""

        # Format available methods
        methods_text = ""
        for i, method in enumerate(agent_methods, 1):
            methods_text += f"\n{i}. Method: {method['name']}\n"
            methods_text += (
                f"   Description: {method.get('description', 'No description')}\n"
            )
            methods_text += (
                f"   Parameters: {list(method.get('parameters', {}).keys())}\n"
            )

        return f"""You are an intelligent agent method selection
and parameter extraction assistant.
Your task is to analyze a user query and:
1. Select the most appropriate method from the available options
2. Extract the required parameters for that method

Available Methods:{methods_text}

You must respond with a JSON object containing:
- "selected_method": The name of the most appropriate method
- "method_reasoning": Brief explanation of why this method was selected
- "method_confidence": Confidence score between 0.0 and 1.0 for method selection
- "extracted_parameters": Dictionary of parameter names and their extracted values
- "parameter_reasoning": Brief explanation of how parameters were extracted
- "parameter_confidence": Confidence score between 0.0 and 1.0 for parameter extraction

Guidelines:
1. Choose the method that best matches the user's intent
2. Extract only parameters that are clearly present in the query
3. Use appropriate data types (string, number, boolean, list)
4. Provide reasonable defaults for missing optional parameters
5. Be conservative with confidence scores
6. If a required parameter cannot be extracted, set it to null

CORRECT Output format (use this exact format):
{{
    "method_reasoning": "explanation of method selection",
    "selected_method": "method_name",
    "method_confidence": 0.95,
    "parameter_reasoning": "explanation of parameter extraction",
    "extracted_parameters": {{"param_name": "value"}},
    "parameter_confidence": 0.90
}}

INCORRECT Output format (DO NOT use):
```json
{{...}}
```
```{{...}}```
Just the extracted data without JSON structure
Missing required fields
Invalid method name (not from available methods)
Invalid JSON syntax"""
