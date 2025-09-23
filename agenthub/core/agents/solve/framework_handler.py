"""Handles framework-level solve using LLM decision engine."""

import logging
import time
from typing import Any

from ...llm.llm_decision_engine import LLMDecisionEngine

logger = logging.getLogger(__name__)


class FrameworkSolveHandler:
    """Handles framework-level solve using LLM method selection."""

    def __init__(self, agent_wrapper: Any) -> None:
        """Initialize framework solve handler."""
        self.agent_wrapper = agent_wrapper
        self.llm_decision_engine = LLMDecisionEngine()

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

            # Use LLM to select method
            method_name, confidence, reasoning = self.llm_decision_engine.select_method(
                query, agent_methods, full_context
            )

            if not method_name:
                return {
                    "error": "Could not select appropriate method",
                    "execution_time": time.time() - start_time,
                }

            # Get method parameters
            method_info = self.agent_wrapper.agent_info.get_method_info(method_name)
            method_parameters = method_info.get("parameters", {})

            # Extract parameters from query
            (
                extracted_params,
                param_confidence,
                param_reasoning,
            ) = self.llm_decision_engine.extract_parameters(
                query, method_name, method_parameters, full_context
            )

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
