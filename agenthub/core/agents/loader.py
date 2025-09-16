"""Agent loader for discovering and loading agents with tool capabilities."""

import logging
from pathlib import Path

from .manifest import ManifestParser
from .validator import InterfaceValidator
from .wrapper import AgentWrapper

logger = logging.getLogger(__name__)


class AgentLoadError(Exception):
    """Raised when agent loading fails."""

    pass


class AgentLoader:
    """Load and validate agents from storage with tool capabilities."""

    def __init__(self, storage=None, tool_registry=None):
        """
        Initialize the agent loader.

        Args:
            storage: Optional storage instance for agent discovery
            tool_registry: Optional tool registry for tool capabilities
        """
        self.storage = storage
        self.manifest_parser = ManifestParser()
        self.interface_validator = InterfaceValidator()
        self.tool_registry = tool_registry
        self.assigned_tools = {}  # agent_id -> list of tool names

    def load_agent_by_path(self, agent_path: str) -> dict:
        """
        Load an agent from a specific path.

        Args:
            agent_path: Path to the agent directory

        Returns:
            dict: Agent information including manifest and metadata

        Raises:
            AgentLoadError: If agent cannot be loaded
        """
        agent_dir = Path(agent_path)

        # Check if agent directory exists
        if not agent_dir.exists():
            raise AgentLoadError(f"Agent directory does not exist: {agent_path}")

        # Validate agent structure (without requiring virtual environment)
        if not self.validate_agent_structure(agent_path, require_venv=False):
            raise AgentLoadError(f"Invalid agent structure: {agent_path}")

        try:
            # Parse manifest
            manifest_file = agent_dir / "agent.yaml"
            manifest = self.manifest_parser.parse_manifest(str(manifest_file))

            # Validate interface
            self.interface_validator.validate_interface(manifest["interface"])

            # Get methods and dependencies
            methods = self.manifest_parser.get_methods(manifest)
            dependencies = self.manifest_parser.get_dependencies(manifest)

            # Build agent info
            agent_info = {
                "name": manifest["name"],
                "version": manifest.get("version", "unknown"),
                "description": manifest.get("description", ""),
                "author": manifest.get("author", ""),
                "path": agent_path,
                "manifest": manifest,
                "methods": methods,
                "dependencies": dependencies,
                "valid": True,
            }

            return agent_info

        except Exception as e:
            raise AgentLoadError(f"Failed to load agent from {agent_path}: {e}") from e

    def load_agent(self, namespace: str, agent_name: str) -> dict:
        """
        Load an agent using namespace and name.

        Args:
            namespace: Agent namespace (e.g., 'agentplug')
            agent_name: Agent name (e.g., 'coding-agent')

        Returns:
            dict: Agent information

        Raises:
            AgentLoadError: If agent cannot be loaded
        """
        if not self.storage:
            raise AgentLoadError("No storage provided for agent loading")

        # Check if agent exists
        if not self.storage.agent_exists(namespace, agent_name):
            raise AgentLoadError(f"Agent not found: {namespace}/{agent_name}")

        # Get agent path
        agent_path = str(self.storage.get_agent_path(namespace, agent_name))

        # Load agent by path
        agent_info = self.load_agent_by_path(agent_path)

        # Add namespace information
        agent_info["namespace"] = namespace
        agent_info["agent_name"] = agent_name

        return agent_info

    def validate_agent_structure(
        self, agent_path: str, require_venv: bool = False
    ) -> bool:
        """
        Validate that an agent has the required structure.

        Args:
            agent_path: Path to the agent directory
            require_venv: Whether to require virtual environment (default: False)

        Returns:
            True if agent structure is valid
        """
        agent_dir = Path(agent_path)

        # Check required files
        required_files = ["agent.py", "agent.yaml"]
        for file_name in required_files:
            if not (agent_dir / file_name).exists():
                logger.debug(f"Missing required file: {file_name}")
                return False

        # Check virtual environment only if required
        if require_venv:
            venv_path = agent_dir / ".venv"
            if not venv_path.exists():
                logger.debug(f"Missing virtual environment: {venv_path}")
                return False

            # Check if Python executable exists in venv
            import sys

            if sys.platform == "win32":
                python_executable = venv_path / "Scripts" / "python.exe"
            else:
                python_executable = venv_path / "bin" / "python"

            if not python_executable.exists():
                logger.debug(f"Python executable not found: {python_executable}")
                return False

        return True

    def discover_agents(self) -> list[dict]:
        """
        Discover all available agents.

        Returns:
            List of agent information dictionaries

        Raises:
            AgentLoadError: If no storage is provided
        """
        if not self.storage:
            raise AgentLoadError("No storage provided for agent discovery")

        return self.storage.discover_agents()

    def get_agent_info(self, namespace: str, agent_name: str) -> dict:
        """
        Get basic information about an agent without fully loading it.

        Args:
            namespace: Agent namespace
            agent_name: Agent name

        Returns:
            dict: Basic agent information

        Raises:
            AgentLoadError: If agent cannot be found
        """
        if not self.storage:
            raise AgentLoadError("No storage provided")

        if not self.storage.agent_exists(namespace, agent_name):
            raise AgentLoadError(f"Agent not found: {namespace}/{agent_name}")

        agent_path = str(self.storage.get_agent_path(namespace, agent_name))

        try:
            # Just parse manifest without full validation
            manifest_file = Path(agent_path) / "agent.yaml"
            manifest = self.manifest_parser.parse_manifest(str(manifest_file))

            return {
                "name": manifest["name"],
                "version": manifest.get("version", "unknown"),
                "description": manifest.get("description", ""),
                "author": manifest.get("author", ""),
                "namespace": namespace,
                "agent_name": agent_name,
                "path": agent_path,
                "methods": self.manifest_parser.get_methods(manifest),
                "dependencies": self.manifest_parser.get_dependencies(manifest),
                "valid_structure": self.validate_agent_structure(agent_path),
            }

        except Exception as e:
            return {
                "name": agent_name,
                "namespace": namespace,
                "agent_name": agent_name,
                "path": agent_path,
                "error": str(e),
                "valid_structure": False,
            }

    def load_agent_with_tools(
        self, agent_path: str, tools: list[str] | None = None
    ) -> "AgentWrapper":
        """
        Load an agent with tool capabilities.

        Args:
            agent_path: Path to the agent directory
            tools: List of tool names to assign to the agent

        Returns:
            AgentWrapper instance with tool capabilities
        """
        if tools is None:
            tools = []

        # Load agent info
        agent_info = self.load_agent_by_path(agent_path)
        if not agent_info.get("valid", False):
            raise AgentLoadError(f"Invalid agent: {agent_path}")

        # Assign tools if tool registry is available
        namespace = agent_info.get("namespace", "unknown")
        name = agent_info.get("name", "unknown")
        agent_id = f"{namespace}/{name}"
        if self.tool_registry and tools:
            from ..tools import assign_tools_to_agent

            assign_tools_to_agent(agent_id, tools)
            self.assigned_tools[agent_id] = tools

        # Create agent wrapper with tool capabilities
        return AgentWrapper(agent_info, self.tool_registry, agent_id, tools)

    def assign_tools_to_agent(self, agent_id: str, tools: list[str]) -> None:
        """Assign tools to an agent."""
        if self.tool_registry:
            from ..tools import assign_tools_to_agent

            assign_tools_to_agent(agent_id, tools)
            self.assigned_tools[agent_id] = tools

    def get_agent_tools(self, agent_id: str) -> list[str]:
        """Get tools assigned to an agent."""
        return self.assigned_tools.get(agent_id, [])
