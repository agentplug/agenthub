"""Environment manager for isolated virtual environments."""

import logging
import sys
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


class EnvironmentManager:
    """Manages isolated virtual environments for agents."""

    def __init__(self) -> None:
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

    def _get_agent_config(self, agent_path: str) -> dict | None:
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
            with open(config_path) as f:
                return yaml.safe_load(f)  # type: ignore[no-any-return]
        except Exception as e:
            logger.warning(f"Failed to parse agent config: {e}")
            return None

    def get_executable(self, agent_path: str) -> str:
        """
        Get the executable path for an agent's virtual environment.
        Supports both Python and Dana based on agent.yaml configuration.

        Args:
            agent_path: Path to the agent directory

        Returns:
            Path to the executable in the agent's virtual environment

        Raises:
            RuntimeError: If virtual environment doesn't exist
        """
        venv_path = self.get_agent_venv_path(agent_path)

        if not venv_path.exists():
            raise RuntimeError(f"Virtual environment not found: {venv_path}")

        # Check agent configuration to determine executable type
        agent_config = self._get_agent_config(agent_path)
        executable_name = "python"  # Default to Python

        if agent_config:
            if "dana_version" in agent_config:
                executable_name = "dana"
                logger.info(f"Using Dana executable for agent: {agent_path}")
            elif "python_version" in agent_config:
                executable_name = "python"
                logger.info(f"Using Python executable for agent: {agent_path}")

        # Determine executable path based on platform
        if sys.platform == "win32":
            executable_path = venv_path / "Scripts" / f"{executable_name}.exe"
        else:
            executable_path = venv_path / "bin" / executable_name

        if not executable_path.exists():
            if executable_name == "dana":
                # For Dana agents, fall back to Python if Dana is not available
                logger.warning(f"Dana executable not found: {executable_path}")
                logger.info("Falling back to Python executable for Dana agent")
                if sys.platform == "win32":
                    executable_path = venv_path / "Scripts" / "python.exe"
                else:
                    executable_path = venv_path / "bin" / "python"

                if not executable_path.exists():
                    raise RuntimeError(
                        f"Python executable not found: {executable_path}"
                    )
            else:
                raise RuntimeError(
                    f"{executable_name.title()} executable not found: {executable_path}"
                )

        return str(executable_path)

    def get_python_executable(self, agent_path: str) -> str:
        """
        Get the Python executable path for an agent's virtual environment.
        This method is kept for backward compatibility.

        Args:
            agent_path: Path to the agent directory

        Returns:
            Path to the Python executable in the agent's virtual environment

        Raises:
            RuntimeError: If virtual environment doesn't exist
        """
        return self.get_executable(agent_path)
