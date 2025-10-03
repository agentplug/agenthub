"""Agent runner that allows agents to use return statements instead of print."""

import json
from typing import Any


def run_agent(agent_class: type, execution_data: dict[str, Any]) -> None:
    """
    Run agent method and automatically handle return values.

    Agents can now use clean return statements:
        def my_method(self, param):
            return {"result": "success", "data": [...]}

    Instead of:
        def my_method(self, param):
            result = {"result": "success", "data": [...]}
            print(json.dumps(result))

    Args:
        agent_class: The agent class to instantiate
        execution_data: Dict with 'method' and 'parameters' keys
    """
    try:
        method_name = execution_data.get("method")
        parameters = execution_data.get("parameters", {})

        if not method_name:
            print(json.dumps({"error": "No method specified"}))
            return

        # Instantiate agent
        agent = agent_class()

        # Get method
        if not hasattr(agent, method_name):
            print(json.dumps({"error": f"Method '{method_name}' not found"}))
            return

        method = getattr(agent, method_name)

        # Execute method
        result = method(**parameters)

        # Handle return value
        if result is None:
            # Method returned nothing, assume success
            output = {"result": "success", "status": "completed"}
        elif isinstance(result, dict):
            # Already a dict, use as-is
            output = result
        else:
            # Wrap non-dict results
            output = {"result": result}

        # Print JSON result for subprocess to capture
        print(json.dumps(output))

    except Exception as e:
        # Handle errors gracefully
        print(json.dumps({"error": str(e), "type": type(e).__name__}))


if __name__ == "__main__":
    # This module is meant to be imported, not run directly
    print(
        json.dumps(
            {
                "error": "agent_runner.py should be imported, not run directly",
                "usage": "from agenthub.core.agents.agent_runner import run_agent",
            }
        )
    )
