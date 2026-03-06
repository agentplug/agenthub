"""Agent loader for discovering and loading agents with tool capabilities."""

import logging
from pathlib import Path
from typing import Any

from .manifest import ManifestParser
from .validator import InterfaceValidator

logger = logging.getLogger(__name__)


class AgentLoadError(Exception):
    """Raised when agent loading fails."""

    pass


class AgentLoader:
    """Load and validate agents from storage with tool capabilities."""

    def __init__(self, storage: Any = None, tool_registry: Any = None) -> None:
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
            # Parse manifest (check for both agent.yaml and agent.yml)
            manifest_file = agent_dir / "agent.yaml"
            if not manifest_file.exists():
                manifest_file = agent_dir / "agent.yml"

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
        Supports both Python and Dana agents based on configuration.

        Args:
            agent_path: Path to the agent directory
            require_venv: Whether to require virtual environment (default: False)

        Returns:
            True if agent structure is valid
        """
        agent_dir = Path(agent_path)

        # Check agent configuration to determine required files
        agent_config = self._get_agent_config(agent_path)

        # Always require agent.yaml or agent.yml
        agent_yaml_exists = (agent_dir / "agent.yaml").exists()
        agent_yml_exists = (agent_dir / "agent.yml").exists()

        if not agent_yaml_exists and not agent_yml_exists:
            logger.debug("Missing required file: agent.yaml (or agent.yml)")
            return False

        # Check for agent script file (either agent.py or agent.na)
        agent_py_exists = (agent_dir / "agent.py").exists()
        agent_na_exists = (agent_dir / "agent.na").exists()

        if agent_config and "dana_version" in agent_config:
            # For Dana agents, require agent.na
            if not agent_na_exists:
                logger.debug("Missing required file: agent.na (Dana agent)")
                return False
        else:
            # For Python agents or default, require agent.py
            if not agent_py_exists:
                logger.debug("Missing required file: agent.py (Python agent)")
                return False

        # Ensure only one agent script file exists
        if agent_py_exists and agent_na_exists:
            logger.debug("Both agent.py and agent.na found - only one should exist")
            return False

        # Check virtual environment only if required
        if require_venv:
            venv_path = agent_dir / ".venv"
            if not venv_path.exists():
                logger.debug(f"Missing virtual environment: {venv_path}")
                return False

            # Check if executable exists in venv (Python or Dana)
            import sys

            if agent_config and "dana_version" in agent_config:
                # Check for Dana executable
                if sys.platform == "win32":
                    executable = venv_path / "Scripts" / "dana.exe"
                else:
                    executable = venv_path / "bin" / "dana"
            else:
                # Check for Python executable
                if sys.platform == "win32":
                    executable = venv_path / "Scripts" / "python.exe"
                else:
                    executable = venv_path / "bin" / "python"

            if not executable.exists():
                logger.debug(f"Executable not found: {executable}")
                return False

        return True

    def _get_agent_config(self, agent_path: str) -> dict[str, Any] | None:
        """
        Get agent configuration from agent.yaml or agent.yml file.

        Args:
            agent_path: Path to the agent directory

        Returns:
            Agent configuration dictionary or None if not found
        """
        agent_yaml_path = Path(agent_path) / "agent.yaml"
        agent_yml_path = Path(agent_path) / "agent.yml"

        config_path = None
        if agent_yaml_path.exists():
            config_path = agent_yaml_path
        elif agent_yml_path.exists():
            config_path = agent_yml_path

        if not config_path:
            return None

        try:
            import yaml

            with open(config_path) as f:
                return yaml.safe_load(f)  # type: ignore[no-any-return]
        except Exception as e:
            logger.warning(f"Failed to parse agent config: {e}")
            return None

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

        agents = self.storage.discover_agents()
        return agents if isinstance(agents, list) else []

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
            # Just parse manifest without full validation (check for both yaml and yml)
            manifest_file = Path(agent_path) / "agent.yaml"
            if not manifest_file.exists():
                manifest_file = Path(agent_path) / "agent.yml"
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
