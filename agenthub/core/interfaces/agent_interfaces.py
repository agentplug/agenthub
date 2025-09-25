"""Agent-related interfaces to break circular dependencies."""

from typing import Any, Protocol

from typing_extensions import runtime_checkable


@runtime_checkable
class AgentInfoProtocol(Protocol):
    """Protocol for agent information."""

    agent_id: str
    name: str
    namespace: str
    agent_name: str
    path: str
    version: str
    description: str
    methods: list[str]
    dependencies: list[str]
    manifest: dict[str, Any]
    interface: dict[str, Any]

    def has_method(self, method_name: str) -> bool:
        """Check if agent has method."""
        ...

    def get_method_info(self, method_name: str) -> dict[str, Any]:
        """Get method information."""
        ...


@runtime_checkable
class MethodExecutorProtocol(Protocol):
    """Protocol for method execution."""

    def execute(self, method: str, parameters: dict[str, Any]) -> Any:
        """Execute agent method."""
        ...


@runtime_checkable
class SolveEngineProtocol(Protocol):
    """Protocol for solve engine."""

    def solve(
        self, query: str, context: dict[str, Any] | None = None, **kwargs: Any
    ) -> Any:
        """Solve query using agent capabilities."""
        ...


@runtime_checkable
class AgentWrapperProtocol(Protocol):
    """Protocol for agent wrapper."""

    agent_info: AgentInfoProtocol
    method_executor: MethodExecutorProtocol
    solve_engine: SolveEngineProtocol
    runtime: Any

    def solve(
        self, query: str, context: dict[str, Any] | None = None, **kwargs: Any
    ) -> Any:
        """Solve query."""
        ...

    def execute(self, method: str, parameters: dict[str, Any] | None = None) -> Any:
        """Execute method."""
        ...

    def has_method(self, method_name: str) -> bool:
        """Check if agent has method."""
        ...

    def get_method_info(self, method_name: str) -> dict[str, Any]:
        """Get method information."""
        ...

    def get_all_available_tools(self) -> list[str]:
        """Get all available tools."""
        ...

    def get_tool_context_json(self) -> str:
        """Get tool context as JSON."""
        ...

    def is_knowledge_available(self) -> bool:
        """Check if knowledge is available."""
        ...

    def get_knowledge(self) -> str:
        """Get injected knowledge."""
        ...
