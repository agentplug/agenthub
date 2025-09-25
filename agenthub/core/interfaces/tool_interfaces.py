"""Tool-related interfaces to break circular dependencies."""

from typing import Any, Protocol

from typing_extensions import runtime_checkable


@runtime_checkable
class ToolRegistryProtocol(Protocol):
    """Protocol for tool registry."""

    def execute_tool(self, name: str, parameters: dict[str, Any]) -> Any:
        """Execute tool with parameters."""
        ...

    def assign_tools_to_agent(self, agent_id: str, tool_names: list[str]) -> None:
        """Assign tools to agent."""
        ...

    def can_agent_access_tool(self, agent_id: str, tool_name: str) -> bool:
        """Check if agent can access tool."""
        ...

    def get_tool_function(self, tool_name: str) -> Any:
        """Get tool function."""
        ...


@runtime_checkable
class ToolManagerProtocol(Protocol):
    """Protocol for tool manager."""

    def assign_tools_to_agent(self, agent_id: str, tool_names: list[str]) -> None:
        """Assign tools to agent."""
        ...

    def get_all_available_tools(self, agent_id: str) -> list[str]:
        """Get all available tools for agent."""
        ...

    def is_builtin_tool_available(self, tool_name: str) -> bool:
        """Check if built-in tool is available."""
        ...

    def validate_builtin_tool_parameters(
        self, tool_name: str, parameters: dict[str, Any]
    ) -> list[str]:
        """Validate built-in tool parameters."""
        ...


@runtime_checkable
class ToolExecutionProtocol(Protocol):
    """Protocol for tool execution."""

    def execute_tool(self, tool_name: str, parameters: dict[str, Any]) -> Any:
        """Execute tool."""
        ...

    def get_tool_context_json(self) -> str:
        """Get tool context as JSON."""
        ...
