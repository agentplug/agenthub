"""
Agent Method Selector for Solve Functionality

Solve-specific component that uses the generalized LLM decision maker
to select the best agent method for a given query.
"""

import logging
from typing import Any

from ...llm.llm_decision_maker import LLMDecisionMaker

logger = logging.getLogger(__name__)


class AgentMethodSelector:
    """Solve-specific agent method selection using generalized LLM decision maker."""

    def __init__(self, llm_decision_maker: LLMDecisionMaker | None = None):
        """
        Initialize the agent method selector.

        Args:
            llm_decision_maker: Optional LLM decision maker instance
        """
        self.decision_maker = llm_decision_maker or LLMDecisionMaker()

    def select_method(
        self,
        query: str,
        agent_methods: list[dict[str, Any]],
        context: dict[str, Any] | None = None,
    ) -> tuple[str, float, str]:
        """
        Select the most appropriate agent method based on user query.

        Args:
            query: User's natural language query
            agent_methods: List of available agent methods with metadata
            context: Optional context information

        Returns:
            Tuple of (selected_method_name, confidence_score, reasoning)
        """
        if not agent_methods:
            return "", 0.0, "No methods available"

        # Prepare methods for decision making
        method_options = self._prepare_method_options(agent_methods)

        # Use generalized decision maker
        selection_criteria = (
            "agent method selection based on user intent and capabilities"
        )
        result = self.decision_maker.make_decision(
            query=query,
            options=method_options,
            selection_criteria=selection_criteria,
            context=context,
            custom_prompt=self._create_method_selection_prompt(),
        )

        # Validate method exists
        if result.selected_option not in [m["name"] for m in agent_methods]:
            logger.warning(f"LLM selected invalid method: {result.selected_option}")
            return "", 0.0, f"Invalid method selected: {result.selected_option}"

        return result.selected_option, result.confidence, result.reasoning

    def _prepare_method_options(
        self, agent_methods: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Prepare agent methods as options for decision making."""
        method_options = []

        for method in agent_methods:
            name = method.get("name", "unknown")
            description = method.get("description", "No description available")
            parameters = method.get("parameters", {})

            # Create metadata for decision making
            metadata = {
                "parameter_count": len(parameters),
                "has_required_params": any(
                    not param.get("optional", False) for param in parameters.values()
                ),
                "parameter_types": [
                    param.get("type", "string") for param in parameters.values()
                ],
            }

            method_options.append(
                {"name": name, "description": description, "metadata": metadata}
            )

        return method_options

    def _create_method_selection_prompt(self) -> str:
        """Create solve-specific method selection prompt."""
        return (
            "You are an intelligent agent method selection assistant. Your task is to "
            "analyze a user query and select the most appropriate method from a "
            "list of available agent methods.\n\n"
            "You must respond with a JSON object containing:\n"
            '- "reasoning": A brief explanation of why this method was selected\n'
            '- "selected_option": The name of the most appropriate method\n'
            '- "confidence": A confidence score between 0.0 and 1.0\n\n'
            "Consider the following factors when selecting a method:\n"
            "1. Semantic similarity between the query and method description\n"
            "2. Parameter compatibility (can the required parameters be extracted "
            "from the query?)\n"
            "3. Method purpose alignment with user intent\n"
            "4. Confidence level based on clarity of the match\n\n"
            "If no method is clearly appropriate, select the most general method "
            "and provide a low confidence score.\n\n"
            "CORRECT Output format (use this exact format):\n"
            """{
            "reasoning": "explanation of method selection",
            "selected_option": "method_name",
            "confidence": 0.95
            }\n\n"""
            "INCORRECT Output format (DO NOT use):\n"
            "```json\n{...}\n```\n"
            "```\n{...}\n```\n"
            "Just the reasoning without JSON structure\n"
            "Missing required fields (reasoning, selected_option, confidence)\n"
            "Invalid method name (not from available methods)"
        )
