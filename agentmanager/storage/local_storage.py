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
