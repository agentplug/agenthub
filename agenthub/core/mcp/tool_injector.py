"""Tool Injector - Injects tool metadata into agent context.

This module handles injecting tool information into agent contexts so agents
know what tools are available and how to use them.
"""

from typing import Any

from agenthub.core.mcp.agent_tool_manager import get_tool_manager
from agenthub.core.tools import get_tool_registry


class ToolInjector:
    """Injects tool metadata into agent contexts."""

    def __init__(self) -> None:
        """Initialize the tool injector."""
        self.tool_manager = get_tool_manager()
        self.tool_registry = get_tool_registry()

    def inject_tools_into_agent_context(
        self, agent_id: str, tool_names: list[str]
    ) -> dict[str, Any]:
        """Inject tool metadata into agent context.

        Args:
            agent_id: Unique identifier for the agent
            tool_names: List of tool names to inject

        Returns:
            Dictionary containing tool metadata for the agent
        """
        # First assign tools to the agent
        assigned_tools = self.tool_manager.assign_tools_to_agent(agent_id, tool_names)

        # Get metadata for assigned tools
        tool_descriptions = {}
        tool_parameters = {}
        tool_examples = {}

        for tool_name in assigned_tools:
            metadata = self.tool_registry.get_tool_metadata(tool_name)
            if metadata:
                tool_descriptions[tool_name] = metadata.description
                tool_parameters[tool_name] = metadata.parameters

                # Create example usage
                if metadata.parameters:
                    example_args: dict[str, Any] = {}
                    for param_name, param_type in metadata.parameters.items():
                        if param_type is str:
                            example_args[param_name] = f"example_{param_name}"
                        elif param_type is int:
                            example_args[param_name] = 42
                        elif param_type is float:
                            example_args[param_name] = 3.14
                        elif param_type is bool:
                            example_args[param_name] = True
                        else:
                            example_args[param_name] = f"example_{param_name}"

                    args_str = ", ".join(
                        f"{k}={repr(v)}" for k, v in example_args.items()
                    )
                    function_call = f"{tool_name}({args_str})"
                    tool_examples[tool_name] = {
                        "function_call": function_call,
                        "arguments": example_args,
                    }

        # Create system prompt with tool information
        # Filter out None values from tool_parameters
        filtered_tool_parameters = {
            k: v for k, v in tool_parameters.items() if v is not None
        }
        system_prompt = self._create_tool_system_prompt(
            assigned_tools, tool_descriptions, filtered_tool_parameters, tool_examples
        )

        return {
            "agent_id": agent_id,
            "available_tools": assigned_tools,
            "tool_descriptions": tool_descriptions,
            "tool_parameters": tool_parameters,
            "tool_examples": tool_examples,
            "system_prompt": system_prompt,
            "tool_count": len(assigned_tools),
        }

    def _create_tool_system_prompt(
        self,
        tool_names: list[str],
        descriptions: dict[str, str],
        parameters: dict[str, dict],
        examples: dict[str, dict],
    ) -> str:
        """Create a system prompt that includes tool information.

        Args:
            tool_names: List of available tool names
            descriptions: Tool descriptions
            parameters: Tool parameter information
            examples: Tool usage examples

        Returns:
            Formatted system prompt string
        """
        if not tool_names:
            return "No tools are available for this agent."

        prompt_parts = ["You have access to the following tools:", ""]

        for tool_name in tool_names:
            prompt_parts.append(f"## {tool_name}")
            description = descriptions.get(tool_name, "No description available")
            prompt_parts.append(f"Description: {description}")

            if tool_name in parameters:
                param_info = []
                for param_name, param_type in parameters[tool_name].items():
                    type_name = (
                        param_type.__name__
                        if hasattr(param_type, "__name__")
                        else str(param_type)
                    )
                    param_info.append(f"  - {param_name}: {type_name}")

                if param_info:
                    prompt_parts.append("Parameters:")
                    prompt_parts.extend(param_info)

            if tool_name in examples:
                example = examples[tool_name]
                prompt_parts.append(f"Example: {example['function_call']}")

            prompt_parts.append("")

        prompt_parts.extend(
            [
                "When you need to use a tool, you can call it through the MCP system.",
                "The tool will be executed automatically and the result "
                "will be returned to you.",
                "Make sure to use the correct parameter names and types "
                "as shown above.",
                "",
            ]
        )

        return "\n".join(prompt_parts)

    def get_agent_tool_summary(self, agent_id: str) -> dict[str, Any]:
        """Get a summary of tools assigned to an agent.

        Args:
            agent_id: Unique identifier for the agent

        Returns:
            Dictionary containing tool summary information
        """
        agent_tools = self.tool_manager.get_agent_tools(agent_id)

        if not agent_tools:
            return {
                "agent_id": agent_id,
                "tool_count": 0,
                "tools": [],
                "message": "No tools assigned to this agent",
            }

        tool_summaries = []
        for tool_name in agent_tools:
            metadata = self.tool_registry.get_tool_metadata(tool_name)
            tool_summaries.append(
                {
                    "name": tool_name,
                    "description": (
                        metadata.description if metadata else "No description"
                    ),
                    "parameter_count": (
                        len(metadata.parameters)
                        if metadata and metadata.parameters
                        else 0
                    ),
                }
            )

        return {
            "agent_id": agent_id,
            "tool_count": len(agent_tools),
            "tools": tool_summaries,
        }


# Global instance
_tool_injector: ToolInjector | None = None


def get_tool_injector() -> ToolInjector:
    """Get the global tool injector instance."""
    global _tool_injector
    if _tool_injector is None:
        _tool_injector = ToolInjector()
    return _tool_injector
