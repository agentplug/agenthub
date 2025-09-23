"""Agent runtime for coordinating agent execution."""

import logging
from pathlib import Path
from typing import Any

import yaml

from agenthub.environment.environment_setup import EnvironmentSetup
from agenthub.runtime.environment_manager import EnvironmentManager
from agenthub.runtime.process_manager import ProcessManager

logger = logging.getLogger(__name__)


class AgentRuntime:
    """Coordinates agent execution and provides unified interface."""

    def __init__(self, storage: Any = None) -> None:
        """
        Initialize the agent runtime.

        Args:
            storage: Optional storage instance for agent discovery
        """
        self.process_manager = ProcessManager()
        self.environment_manager = EnvironmentManager()
        self.storage = storage

        # Initialize environment setup for automatic environment creation
        try:
            self.environment_setup = EnvironmentSetup()
        except Exception as e:
            logger.warning(f"Environment setup not available: {e}")
            self.environment_setup = None  # type: ignore

    def execute_agent(
        self,
        namespace: str,
        agent_name: str,
        method: str,
        parameters: dict,
        tool_context: dict | None = None,
    ) -> dict:
        """
        Execute an agent method with full runtime coordination.

        Args:
            namespace: Agent namespace (e.g., 'agentplug')
            agent_name: Agent name (e.g., 'coding-agent')
            method: Name of the method to execute
            parameters: Dictionary of method parameters

        Returns:
            dict: Execution result with 'result' or 'error' key
        """
        if self.storage:
            # Use storage to get agent path and validate existence
            if not self.storage.agent_exists(namespace, agent_name):
                return {
                    "error": f"Agent not found: {namespace}/{agent_name}",
                    "namespace": namespace,
                    "agent_name": agent_name,
                }
            agent_path = str(self.storage.get_agent_path(namespace, agent_name))
        else:
            # Fallback to direct path construction
            agent_path = f"~/.agenthub/agents/{namespace}/{agent_name}"
            agent_path = str(Path(agent_path).expanduser())

        # Validate agent structure (without requiring virtual environment initially)
        if not self.process_manager.validate_agent_structure(
            agent_path, require_venv=False
        ):
            return {
                "error": f"Invalid agent structure: {namespace}/{agent_name}",
                "agent_path": agent_path,
            }

        # Ensure virtual environment exists before execution
        venv_path = self.environment_manager.get_agent_venv_path(agent_path)
        if not venv_path.exists() and self.environment_setup:
            logger.info(
                f"Virtual environment not found for {namespace}/{agent_name}, "
                f"setting up..."
            )
            setup_result = self.environment_setup.setup_environment(agent_path)
            if not setup_result.success:
                return {
                    "error": (
                        f"Failed to set up environment for {namespace}/{agent_name}: "
                        f"{setup_result.error_message}"
                    ),
                    "agent_path": agent_path,
                }
            logger.info(f"Environment setup completed for {namespace}/{agent_name}")

        # Validate method exists in agent interface
        if not self.validate_method(agent_path, method):
            available_methods = self.get_available_methods(agent_path)
            return {
                "error": f"Method '{method}' not found in agent interface",
                "available_methods": available_methods,
                "suggestion": (
                    f"Available methods: {', '.join(available_methods)}"
                    if available_methods
                    else "No methods available"
                ),
            }

        # Load manifest for dynamic execution
        manifest = None
        try:
            manifest = self.load_agent_manifest(agent_path)
        except Exception as e:
            logger.debug(f"Could not load manifest for dynamic execution: {e}")

        # Execute the agent
        return self.process_manager.execute_agent(
            agent_path, method, parameters, manifest, tool_context
        )

    def validate_method(self, agent_path: str, method: str) -> bool:
        """
        Validate that a method exists in an agent's interface.

        Args:
            agent_path: Path to the agent directory
            method: Name of the method to validate

        Returns:
            bool: True if method exists and is valid
        """
        try:
            manifest = self.load_agent_manifest(agent_path)
            interface = manifest.get("interface", {})
            methods = interface.get("methods", {})
            return method in methods
        except Exception as e:
            logger.debug(
                f"Error validating method {method} for agent {agent_path}: {e}"
            )
            return False

    def get_available_methods(self, agent_path: str) -> list[str]:
        """
        Get list of available methods for an agent.

        Args:
            agent_path: Path to the agent directory

        Returns:
            List of available method names
        """
        try:
            manifest = self.load_agent_manifest(agent_path)
            interface = manifest.get("interface", {})
            methods = interface.get("methods", {})
            return list(methods.keys())
        except Exception as e:
            logger.debug(f"Error getting available methods for agent {agent_path}: {e}")
            return []

    def load_agent_manifest(self, agent_path: str) -> dict:
        """
        Load and parse an agent manifest.

        Args:
            agent_path: Path to the agent directory

        Returns:
            dict: Parsed agent manifest

        Raises:
            ValueError: If manifest is invalid or missing
            FileNotFoundError: If agent directory doesn't exist
        """
        agent_dir = Path(agent_path)
        if not agent_dir.exists():
            raise FileNotFoundError(f"Agent directory does not exist: {agent_path}")

        manifest_path = agent_dir / "agent.yaml"
        if not manifest_path.exists():
            raise ValueError(f"Agent manifest not found: {manifest_path}")

        try:
            with open(manifest_path) as f:
                manifest = yaml.safe_load(f)

            if not isinstance(manifest, dict):
                raise ValueError("Manifest must be a valid YAML dictionary")

            # Validate required fields
            required_fields = ["name", "interface"]
            for field in required_fields:
                if field not in manifest:
                    raise ValueError(f"Missing required field in manifest: {field}")

            return manifest

        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in manifest: {e}") from e
        except Exception as e:
            raise ValueError(f"Error reading manifest: {e}") from e

    def get_agent_info(self, agent_path: str) -> dict:
        """
        Get information about an agent.

        Args:
            agent_path: Path to the agent directory

        Returns:
            dict: Agent information including interface and metadata
        """
        try:
            manifest = self.load_agent_manifest(agent_path)

            info = {
                "name": manifest.get("name"),
                "version": manifest.get("version"),
                "description": manifest.get("description"),
                "author": manifest.get("author"),
                "path": agent_path,
                "methods": list(
                    manifest.get("interface", {}).get("methods", {}).keys()
                ),
                "valid_structure": self.process_manager.validate_agent_structure(
                    agent_path
                ),
            }

            return info

        except Exception as e:
            return {
                "error": f"Failed to get agent info: {e}",
                "path": agent_path,
                "valid_structure": False,
            }
