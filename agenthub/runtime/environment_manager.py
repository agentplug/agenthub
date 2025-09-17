"""Environment manager for isolated virtual environments."""

import logging
import sys
from pathlib import Path

logger = logging.getLogger(__name__)


class EnvironmentManager:
    """Manages isolated virtual environments for agents."""

    def __init__(self):
        """Initialize the environment manager."""
        pass

    def get_agent_venv_path(self, agent_path: str) -> Path:
        """
        Get the virtual environment path for a specific agent.

        Args:
            agent_path: Path to the agent directory

        Returns:
            Path to the virtual environment directory
        """
        return Path(agent_path) / ".venv"

    def get_python_executable(self, agent_path: str) -> str:
        """
        Get the Python executable path for an agent's virtual environment.

        Args:
            agent_path: Path to the agent directory

        Returns:
            Path to the Python executable in the agent's virtual environment

        Raises:
            RuntimeError: If virtual environment doesn't exist
        """
        venv_path = self.get_agent_venv_path(agent_path)

        if not venv_path.exists():
            raise RuntimeError(f"Virtual environment not found: {venv_path}")

        # Determine Python executable path based on platform
        if sys.platform == "win32":
            python_executable = venv_path / "Scripts" / "python.exe"
        else:
            python_executable = venv_path / "bin" / "python"

        if not python_executable.exists():
            raise RuntimeError(f"Python executable not found: {python_executable}")

        return str(python_executable)
