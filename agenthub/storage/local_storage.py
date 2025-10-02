"""Local storage manager for agent files and metadata."""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class LocalStorage:
    """Main interface for local storage operations."""

    def __init__(self, base_dir: Path | None = None):
        """
        Initialize local storage manager.

        Args:
            base_dir: Base directory for agent storage. If None, uses ~/.agenthub
        """
        self._base_dir = base_dir or Path.home() / ".agenthub"
        self._agents_dir = self._base_dir / "agents"
        self._cache_dir = self._base_dir / "cache"
        self._config_dir = self._base_dir / "config"
        self._logs_dir = self._base_dir / "logs"

    def get_agenthub_dir(self) -> Path:
        """
        Get the Agent Hub directory for the current platform.

        Returns:
            Path to the Agent Hub directory
        """
        return self._base_dir

    def get_agents_dir(self) -> Path:
        """
        Get the agents directory for the current platform.

        Returns:
            Path to the agents directory
        """
        return self._agents_dir

    def initialize_storage(self) -> None:
        """
        Initialize the storage directory structure.
        Creates all necessary directories if they don't exist.

        Raises:
            PermissionError: If unable to create directories due to permissions
            OSError: If unable to create directories due to system error
        """
        directories = [
            self._base_dir,
            self._agents_dir,
            self._cache_dir,
            self._config_dir,
            self._logs_dir,
        ]

        for directory in directories:
            try:
                directory.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Created directory: {directory}")
            except PermissionError as e:
                logger.error(f"Permission denied creating directory {directory}: {e}")
                raise
            except OSError as e:
                logger.error(f"OS error creating directory {directory}: {e}")
                raise

    def discover_agents(self) -> list[dict[str, str]]:
        """
        Discover all installed agents in the agents directory.

        Returns:
            List of agent information dictionaries with keys:
            - name: Agent name
            - namespace: Developer namespace
            - path: Full path to agent directory
            - version: Agent version (if available)

        Raises:
            OSError: If unable to read agents directory
        """
        agents: list[dict[str, str]] = []

        if not self._agents_dir.exists():
            logger.debug(f"Agents directory does not exist: {self._agents_dir}")
            return agents

        try:
            # Iterate through namespace directories (e.g., agentplug/)
            for namespace_dir in self._agents_dir.iterdir():
                if not namespace_dir.is_dir():
                    continue

                namespace = namespace_dir.name
                if namespace.startswith("."):
                    continue  # Skip hidden directories

                # Iterate through agent directories
                for agent_dir in namespace_dir.iterdir():
                    if not agent_dir.is_dir():
                        continue

                    agent_name = agent_dir.name
                    if agent_name.startswith("."):
                        continue  # Skip hidden directories

                    # Check if this is a valid agent directory
                    if self._is_valid_agent_directory(agent_dir):
                        agent_info = {
                            "name": agent_name,
                            "namespace": namespace,
                            "path": str(agent_dir),
                        }

                        # Try to get version from manifest
                        version = self._get_agent_version(agent_dir)
                        if version:
                            agent_info["version"] = version

                        agents.append(agent_info)

        except OSError as e:
            logger.error(f"Error discovering agents: {e}")
            raise

        return agents

    def _is_valid_agent_directory(self, agent_path: Path) -> bool:
        """
        Check if a directory contains a valid agent.
        Supports both Python and Dana agents based on configuration.

        Args:
            agent_path: Path to the agent directory

        Returns:
            True if the directory contains required agent files
        """
        # Check for agent config file (agent.yaml or agent.yml)
        agent_yaml_exists = (agent_path / "agent.yaml").exists()
        agent_yml_exists = (agent_path / "agent.yml").exists()

        if not agent_yaml_exists and not agent_yml_exists:
            logger.debug(f"Missing required config file in {agent_path}")
            return False

        # Determine config file path
        config_path = (
            agent_path / "agent.yaml" if agent_yaml_exists else agent_path / "agent.yml"
        )

        # Check agent configuration to determine script file requirement
        try:
            import yaml

            with open(config_path) as f:
                agent_config = yaml.safe_load(f)

            if agent_config and "dana_version" in agent_config:
                # For Dana agents, require agent.na
                if not (agent_path / "agent.na").exists():
                    logger.debug(
                        f"Missing required file agent.na (Dana agent) in {agent_path}"
                    )
                    return False
            else:
                # For Python agents or default, require agent.py
                if not (agent_path / "agent.py").exists():
                    logger.debug(
                        f"Missing required file agent.py (Python agent) in {agent_path}"
                    )
                    return False
        except Exception as e:
            logger.debug(f"Error reading agent config from {config_path}: {e}")
            # Default to requiring agent.py if config can't be read
            if not (agent_path / "agent.py").exists():
                logger.debug(
                    f"Missing required file agent.py (fallback) in {agent_path}"
                )
                return False

        return True

    def _get_agent_version(self, agent_path: Path) -> str | None:
        """
        Get agent version from manifest file.

        Args:
            agent_path: Path to the agent directory

        Returns:
            Agent version string if available, None otherwise
        """
        # Check for both agent.yaml and agent.yml
        manifest_path = agent_path / "agent.yaml"
        if not manifest_path.exists():
            manifest_path = agent_path / "agent.yml"

        if not manifest_path.exists():
            return None

        try:
            import yaml

            with open(manifest_path) as f:
                manifest = yaml.safe_load(f)
                version = manifest.get("version")
                return str(version) if version is not None else None
        except Exception as e:
            logger.debug(f"Error reading version from {manifest_path}: {e}")
            return None

    def get_agent_path(self, namespace: str, agent_name: str) -> Path:
        """
        Get the path to a specific agent.

        Args:
            namespace: The agent namespace (e.g., 'agentplug')
            agent_name: The agent name (e.g., 'coding-agent')

        Returns:
            Path to the agent directory
        """
        return self._agents_dir / namespace / agent_name

    def agent_exists(self, namespace: str, agent_name: str) -> bool:
        """
        Check if an agent exists in storage.

        Args:
            namespace: The agent namespace (e.g., 'agentplug')
            agent_name: The agent name (e.g., 'coding-agent')

        Returns:
            True if the agent exists and is valid
        """
        agent_path = self.get_agent_path(namespace, agent_name)
        return agent_path.exists() and self._is_valid_agent_directory(agent_path)
