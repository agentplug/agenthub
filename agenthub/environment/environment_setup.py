"""
Environment setup and management for Agent Hub.

This module provides functionality for creating and managing virtual environments
and dependency installation for auto-installed agents.
"""

import logging
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Check if environment module is available
ENVIRONMENT_AVAILABLE = True  # This module is self-contained


@dataclass
class EnvironmentSetupResult:
    """Result of environment setup operation."""

    success: bool
    agent_path: str
    venv_path: str
    setup_time_seconds: float
    error_message: str | None = None
    warnings: list[str] | None = None
    next_steps: list[str] | None = None
    environment_info: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Initialize lists if they are None."""
        if self.warnings is None:
            self.warnings = []
        if self.next_steps is None:
            self.next_steps = []
        if self.environment_info is None:
            self.environment_info = {}


@dataclass
class DependencyInstallResult:
    """Result of dependency installation operation."""

    success: bool
    agent_path: str
    venv_path: str
    install_time_seconds: float
    installed_packages: list[str]
    error_message: str | None = None
    warnings: list[str] | None = None
    next_steps: list[str] | None = None

    def __post_init__(self) -> None:
        """Initialize lists if they are None."""
        if self.warnings is None:
            self.warnings = []
        if self.next_steps is None:
            self.next_steps = []


class EnvironmentSetupError(Exception):
    """Base exception for environment setup errors."""

    pass


class UVNotAvailableError(EnvironmentSetupError):
    """Raised when UV is not available on the system."""

    pass


class EnvironmentSetup:
    """Manages UV virtual environment creation and dependency installation."""

    def __init__(self) -> None:
        """Initialize the environment setup."""
        self.logger = logger
        if not self._check_uv_available():
            raise UVNotAvailableError(
                "UV is not available on the system. Please install UV first."
            )

    def _check_uv_available(self) -> bool:
        """Check if UV is available on the system."""
        try:
            result = subprocess.run(
                ["uv", "--version"], capture_output=True, text=True, timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def setup_environment(self, agent_path: str) -> EnvironmentSetupResult:
        """Set up a virtual environment for the agent."""
        start_time = time.time()

        # Ensure the path is properly expanded (handle ~ characters)
        if isinstance(agent_path, str) and "~" in agent_path:
            agent_path = str(Path(agent_path).expanduser())

        agent_path_obj = Path(agent_path)

        if not agent_path_obj.exists():
            return EnvironmentSetupResult(
                success=False,
                agent_path=agent_path,
                venv_path="",
                setup_time_seconds=time.time() - start_time,
                error_message=f"Agent path does not exist: {agent_path}",
                next_steps=["Verify the agent path is correct"],
            )

        try:
            # Check if we have any installation method available
            pyproject_path = agent_path_obj / "pyproject.toml"
            requirements_path = agent_path_obj / "requirements.txt"
            agent_yaml_path = agent_path_obj / "agent.yaml"

            has_installation_method = False

            # Check for installation commands in agent.yaml
            if agent_yaml_path.exists():
                try:
                    import yaml

                    with open(agent_yaml_path, encoding="utf-8") as f:
                        agent_config = yaml.safe_load(f)
                    if (
                        "installation" in agent_config
                        and "commands" in agent_config["installation"]
                    ):
                        has_installation_method = True
                except Exception:
                    pass

            # Check for other installation methods
            if pyproject_path.exists() or requirements_path.exists():
                has_installation_method = True

            if not has_installation_method:
                return EnvironmentSetupResult(
                    success=False,
                    agent_path=agent_path,
                    venv_path="",
                    setup_time_seconds=time.time() - start_time,
                    error_message="No installation method found",
                    next_steps=[
                        "Add installation.commands to agent.yaml",
                        "Or provide a pyproject.toml file",
                        "Or provide a requirements.txt file",
                    ],
                )

            # Create virtual environment using UV
            venv_path = agent_path_obj / ".venv"
            self.logger.info(f"Creating virtual environment at {venv_path}")

            # Step 1: Create the virtual environment first
            create_result = subprocess.run(
                ["uv", "venv", ".venv"],
                cwd=agent_path,
                capture_output=True,
                text=True,
                timeout=60,
            )

            if create_result.returncode != 0:
                return EnvironmentSetupResult(
                    success=False,
                    agent_path=agent_path,
                    venv_path=str(venv_path),
                    setup_time_seconds=time.time() - start_time,
                    error_message=f"UV venv creation failed: {create_result.stderr}",
                    next_steps=[
                        "Check if UV is properly installed",
                        "Verify system permissions",
                        "Ensure sufficient disk space",
                    ],
                )

            # Step 2: Install dependencies using installation commands or dependencies
            # from agent.yaml or requirements.txt
            # First try to read installation commands and dependencies from agent.yaml
            agent_yaml_path = agent_path_obj / "agent.yaml"
            dependencies = []
            installation_commands = []

            if agent_yaml_path.exists():
                try:
                    import yaml

                    with open(agent_yaml_path) as f:
                        agent_config = yaml.safe_load(f)

                    # Check for installation commands first (preferred method)
                    if (
                        "installation" in agent_config
                        and "commands" in agent_config["installation"]
                    ):
                        installation_commands = agent_config["installation"]["commands"]
                        self.logger.info(
                            f"Found {len(installation_commands)} installation commands "
                            f"in agent.yaml"
                        )
                    elif "dependencies" in agent_config:
                        dependencies = agent_config["dependencies"]
                        self.logger.info(
                            f"Found {len(dependencies)} dependencies in agent.yaml"
                        )
                    else:
                        self.logger.info(
                            "No installation commands or dependencies section in "
                            "agent.yaml, falling back to requirements.txt"
                        )
                except Exception as e:
                    self.logger.warning(
                        f"Failed to parse agent.yaml: {e}, "
                        f"falling back to requirements.txt"
                    )

            # If no installation commands or dependencies from agent.yaml,
            # try requirements.txt
            if not installation_commands and not dependencies:
                requirements_path = agent_path_obj / "requirements.txt"
                if requirements_path.exists():
                    with open(requirements_path) as f:
                        dependencies = [
                            line.strip()
                            for line in f
                            if line.strip() and not line.startswith("#")
                        ]
                    self.logger.info(
                        f"Found {len(dependencies)} dependencies in requirements.txt"
                    )
                else:
                    return EnvironmentSetupResult(
                        success=False,
                        agent_path=agent_path,
                        venv_path=str(venv_path),
                        setup_time_seconds=time.time() - start_time,
                        error_message=(
                            "No installation commands, dependencies found in "
                            "agent.yaml or requirements.txt"
                        ),
                        next_steps=[
                            "Ensure agent.yaml has an installation.commands section",
                            "Or ensure agent.yaml has a dependencies section",
                            "Or provide a requirements.txt file",
                        ],
                    )

            # Get Python executable path for environment
            venv_python = venv_path / "bin" / "python"
            if not venv_python.exists():
                # Fallback for Windows
                venv_python = venv_path / "Scripts" / "python.exe"

            # Set environment variables for installation commands
            install_env = dict(os.environ)
            install_env["VIRTUAL_ENV"] = str(venv_path)
            install_env["PATH"] = f"{venv_path / 'bin'}:{install_env.get('PATH', '')}"

            result = None

            if installation_commands:
                # Execute installation commands in sequence
                self.logger.info(
                    f"Executing {len(installation_commands)} installation commands"
                )
                for i, command in enumerate(installation_commands):
                    self.logger.info(
                        f"Running command {i+1}/{len(installation_commands)}: {command}"
                    )

                    # Parse command string into list for subprocess
                    import shlex

                    cmd_parts = shlex.split(command)

                    result = subprocess.run(
                        cmd_parts,
                        cwd=agent_path,
                        capture_output=True,
                        text=True,
                        timeout=300,  # 5 minutes per command
                        env=install_env,
                    )

                    if result.returncode != 0:
                        self.logger.error(f"Installation command failed: {command}")
                        break
                    else:
                        self.logger.info(f"Command completed successfully: {command}")

            elif dependencies:
                # Use dependencies with UV pip install
                self.logger.info(
                    f"Installing {len(dependencies)} dependencies: {dependencies}"
                )
                result = subprocess.run(
                    ["uv", "pip", "install", "--python", str(venv_python)]
                    + dependencies,
                    cwd=agent_path,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minutes for dependency installation
                    env=install_env,
                )
            else:
                # Fallback to requirements.txt if no dependencies found
                result = subprocess.run(
                    [
                        "uv",
                        "pip",
                        "install",
                        "--python",
                        str(venv_python),
                        "-r",
                        "requirements.txt",
                    ],
                    cwd=agent_path,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minutes for dependency installation
                    env=install_env,
                )

            if result and result.returncode != 0:
                return EnvironmentSetupResult(
                    success=False,
                    agent_path=agent_path,
                    venv_path=str(venv_path),
                    setup_time_seconds=time.time() - start_time,
                    error_message=f"UV sync failed: {result.stderr}",
                    next_steps=[
                        "Check if requirements.txt is valid",
                        "Verify Python version compatibility",
                    ],
                )

            # Verify environment was created
            if not venv_path.exists():
                return EnvironmentSetupResult(
                    success=False,
                    agent_path=agent_path,
                    venv_path=str(venv_path),
                    setup_time_seconds=time.time() - start_time,
                    error_message=(
                        "Virtual environment was not created despite successful UV sync"
                    ),
                    next_steps=["Check UV installation and permissions"],
                )

            setup_time = time.time() - start_time
            self.logger.info(
                f"Virtual environment created successfully in {setup_time:.2f}s"
            )

            # Collect environment information
            environment_info = self._collect_environment_info(agent_path_obj, venv_path)

            return EnvironmentSetupResult(
                success=True,
                agent_path=agent_path,
                venv_path=str(venv_path),
                setup_time_seconds=setup_time,
                environment_info=environment_info,
                next_steps=[
                    "Virtual environment is ready",
                    "Install dependencies with install_dependencies()",
                ],
            )

        except subprocess.TimeoutExpired:
            return EnvironmentSetupResult(
                success=False,
                agent_path=agent_path,
                venv_path="",
                setup_time_seconds=time.time() - start_time,
                error_message="UV sync timed out",
                next_steps=["Check system resources and try again"],
            )
        except Exception as e:
            return EnvironmentSetupResult(
                success=False,
                agent_path=agent_path,
                venv_path="",
                setup_time_seconds=time.time() - start_time,
                error_message=f"Unexpected error during environment setup: {e}",
                next_steps=["Check system logs for more details"],
            )

    def install_dependencies(
        self, agent_path: str, venv_path: str
    ) -> DependencyInstallResult:
        """Install dependencies in the virtual environment."""
        start_time = time.time()

        # Ensure the paths are properly expanded (handle ~ characters)
        if isinstance(agent_path, str) and "~" in agent_path:
            agent_path = str(Path(agent_path).expanduser())
        if isinstance(venv_path, str) and "~" in venv_path:
            venv_path = str(Path(venv_path).expanduser())

        agent_path_obj = Path(agent_path)
        venv_path_obj = Path(venv_path)

        if not venv_path_obj.exists():
            return DependencyInstallResult(
                success=False,
                agent_path=agent_path,
                venv_path=venv_path,
                install_time_seconds=time.time() - start_time,
                installed_packages=[],
                error_message="Virtual environment does not exist",
                warnings=["Environment must be created before installing dependencies"],
            )

        # Check for requirements.txt
        requirements_path = agent_path_obj / "requirements.txt"
        if not requirements_path.exists():
            return DependencyInstallResult(
                success=False,
                agent_path=agent_path,
                venv_path=venv_path,
                install_time_seconds=time.time() - start_time,
                installed_packages=[],
                error_message="No requirements.txt found",
                warnings=["Dependencies cannot be installed without requirements.txt"],
            )

        try:
            self.logger.info(f"Installing dependencies from {requirements_path}")

            # Install dependencies using UV pip
            result = subprocess.run(
                ["uv", "pip", "install", "-r", "requirements.txt"],
                cwd=agent_path,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes for dependency installation
            )

            if result.returncode != 0:
                return DependencyInstallResult(
                    success=False,
                    agent_path=agent_path,
                    venv_path=venv_path,
                    install_time_seconds=time.time() - start_time,
                    installed_packages=[],
                    error_message=f"Dependency installation failed: {result.stderr}",
                    warnings=["Check requirements.txt format and package availability"],
                )

            install_time = time.time() - start_time
            self.logger.info(
                f"Dependencies installed successfully in {install_time:.2f}s"
            )

            # Get list of installed packages
            installed_packages = self._get_installed_packages(venv_path)

            return DependencyInstallResult(
                success=True,
                agent_path=agent_path,
                venv_path=venv_path,
                install_time_seconds=install_time,
                installed_packages=installed_packages,
                next_steps=[
                    "Dependencies are ready",
                    "Agent can now be imported and used",
                ],
            )

        except subprocess.TimeoutExpired:
            return DependencyInstallResult(
                success=False,
                agent_path=agent_path,
                venv_path=venv_path,
                install_time_seconds=time.time() - start_time,
                installed_packages=[],
                error_message="Dependency installation timed out",
                warnings=["Large dependency trees may take longer to install"],
            )
        except Exception as e:
            return DependencyInstallResult(
                success=False,
                agent_path=agent_path,
                venv_path=venv_path,
                install_time_seconds=time.time() - start_time,
                installed_packages=[],
                error_message=f"Unexpected error during dependency installation: {e}",
                warnings=["Check system logs for more details"],
            )

    def _collect_environment_info(
        self, agent_path: Path, venv_path: Path
    ) -> dict[str, Any]:
        """Collect information about the created environment."""
        info = {
            "venv_path": str(venv_path),
            "python_executable": str(venv_path / "bin" / "python"),
            "uv_version": self._get_uv_version(),
            "project_files": self._get_project_files(agent_path),
        }
        return info

    def _get_uv_version(self) -> str:
        """Get UV version."""
        try:
            result = subprocess.run(
                ["uv", "--version"], capture_output=True, text=True, timeout=10
            )
            return result.stdout.strip() if result.returncode == 0 else "Unknown"
        except Exception:
            return "Unknown"

    def _get_project_files(self, agent_path: Path) -> list[str]:
        """Get list of project files."""
        try:
            return [f.name for f in agent_path.iterdir() if f.is_file()]
        except Exception:
            return []

    def _get_installed_packages(self, venv_path: str) -> list[str]:
        """Get list of installed packages in the virtual environment."""
        try:
            result = subprocess.run(
                ["uv", "pip", "list"],
                cwd=venv_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                # Parse the output to extract package names
                lines = result.stdout.strip().split("\n")[2:]  # Skip header lines
                packages = []
                for line in lines:
                    if line.strip():
                        package_name = line.split()[0]
                        packages.append(package_name)
                return packages
            return []
        except Exception:
            return []

    def activate_environment(self, venv_path: str) -> str:
        """Get the command to activate the virtual environment."""
        return f"source {venv_path}/bin/activate"
