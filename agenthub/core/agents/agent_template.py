#!/usr/bin/env python3
"""
Dynamic Agent Template for AgentHub

This template shows how to create agents that work with the dynamic execution framework.
No hardcoded method routing or parameter extraction is required!
"""

import json
import sys
from typing import Any


class DynamicAgent:
    """
    Base class for dynamic agents.

    Agents should inherit from this class and implement methods
    as defined in their manifest.
    The framework will automatically discover and execute methods using reflection.
    """

    def __init__(self) -> None:
        """Initialize the agent."""
        pass

    def get_agent_info(self) -> dict[str, Any]:
        """
        Get agent information (optional).

        Returns:
            Dictionary with agent metadata
        """
        return {
            "name": self.__class__.__name__,
            "version": "1.0.0",
            "description": "Dynamic agent template",
        }


def main() -> None:
    """
    Main entry point for dynamic agent execution.

    This function is called by the framework and handles dynamic execution.
    No hardcoded method routing is required!
    """
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Invalid arguments"}))
        sys.exit(1)

    try:
        # Parse input from command line
        input_data = json.loads(sys.argv[1])
        method = input_data.get("method")
        parameters = input_data.get("parameters", {})

        # Import the dynamic executor
        from agenthub.core.agents.dynamic_executor import execute_agent_dynamically

        # Get the agent path (current directory)
        agent_path = "."

        # Execute method dynamically
        result = execute_agent_dynamically(agent_path, method, parameters)

        # Return result
        print(json.dumps(result))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
