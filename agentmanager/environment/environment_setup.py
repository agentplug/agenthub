"""
Environment setup and management for Agent Hub.

This module provides functionality for creating and managing virtual environments
and dependency installation for auto-installed agents.
"""

import logging
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any

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
    error_message: Optional[str] = None
    warnings: List[str] = None
    next_steps: List[str] = None
    environment_info: Dict[str, Any] = None

    def __post_init__(self):
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
    installed_packages: List[str]
    error_message: Optional[str] = None
    warnings: List[str] = None

    def __post_init__(self):
        """Initialize warnings list if it is None."""
        if self.warnings is None:
            self.warnings = []


class EnvironmentSetupError(Exception):
    """Base exception for environment setup errors."""
    pass


class UVNotAvailableError(EnvironmentSetupError):
    """Raised when UV is not available on the system."""
    pass


class EnvironmentSetup:
    """Manages UV virtual environment creation and dependency installation."""

    def __init__(self):
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
                ["uv", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def setup_environment(self, agent_path: str) -> EnvironmentSetupResult:
        """Set up a virtual environment for the agent."""
        start_time = time.time()
        agent_path_obj = Path(agent_path)

        if not agent_path_obj.exists():
            return EnvironmentSetupResult(
                success=False,
                agent_path=agent_path,
                venv_path="",
                setup_time_seconds=time.time() - start_time,
                error_message=f"Agent path does not exist: {agent_path}",
                next_steps=["Verify the agent path is correct"]
            )

        try:
            # Check if pyproject.toml exists (required for UV)
            pyproject_path = agent_path_obj / "pyproject.toml"
            if not pyproject_path.exists():
                return EnvironmentSetupResult(
                    success=False,
                    agent_path=agent_path,
                    venv_path="",
                    setup_time_seconds=time.time() - start_time,
                    error_message="No pyproject.toml found - required for UV",
                    next_steps=["Ensure the agent has a pyproject.toml file"]
                )

            # Create virtual environment using UV
            venv_path = agent_path_obj / ".venv"
            self.logger.info(f"Creating virtual environment at {venv_path}")

            result = subprocess.run(
                ["uv", "sync"],
                cwd=agent_path,
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                return EnvironmentSetupResult(
                    success=False,
                    agent_path=agent_path,
                    venv_path=str(venv_path),
                    setup_time_seconds=time.time() - start_time,
                    error_message=f"UV sync failed: {result.stderr}",
                    next_steps=[
                        "Check if requirements.txt is valid",
                        "Verify Python version compatibility"
                    ]
                )

            # Verify environment was created
            if not venv_path.exists():
                return EnvironmentSetupResult(
                    success=False,
                    agent_path=agent_path,
                    venv_path=str(venv_path),
                    setup_time_seconds=time.time() - start_time,
                    error_message="Virtual environment was not created despite successful UV sync",
                    next_steps=["Check UV installation and permissions"]
                )

            setup_time = time.time() - start_time
            self.logger.info(f"Virtual environment created successfully in {setup_time:.2f}s")

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
                    "Install dependencies with install_dependencies()"
                ]
            )

        except subprocess.TimeoutExpired:
            return EnvironmentSetupResult(
                success=False,
                agent_path=agent_path,
                venv_path="",
                setup_time_seconds=time.time() - start_time,
                error_message="UV sync timed out",
                next_steps=["Check system resources and try again"]
            )
        except Exception as e:
            return EnvironmentSetupResult(
                success=False,
                agent_path=agent_path,
                venv_path="",
                setup_time_seconds=time.time() - start_time,
                error_message=f"Unexpected error during environment setup: {e}",
                next_steps=["Check system logs for more details"]
            )

    def install_dependencies(self, agent_path: str, venv_path: str) -> DependencyInstallResult:
        """Install dependencies in the virtual environment."""
        start_time = time.time()
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
                warnings=["Environment must be created before installing dependencies"]
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
                warnings=["Dependencies cannot be installed without requirements.txt"]
            )

        try:
            self.logger.info(f"Installing dependencies from {requirements_path}")

            # Install dependencies using UV pip
            result = subprocess.run(
                ["uv", "pip", "install", "-r", "requirements.txt"],
                cwd=agent_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes for dependency installation
            )

            if result.returncode != 0:
                return DependencyInstallResult(
                    success=False,
                    agent_path=agent_path,
                    venv_path=venv_path,
                    install_time_seconds=time.time() - start_time,
                    installed_packages=[],
                    error_message=f"Dependency installation failed: {result.stderr}",
                    warnings=["Check requirements.txt format and package availability"]
                )

            install_time = time.time() - start_time
            self.logger.info(f"Dependencies installed successfully in {install_time:.2f}s")

            # Get list of installed packages
            installed_packages = self._get_installed_packages(venv_path)

            return DependencyInstallResult(
                success=True,
                agent_path=agent_path,
                venv_path=venv_path,
                install_time_seconds=install_time,
                installed_packages=installed_packages,
                next_steps=["Dependencies are ready", "Agent can now be imported and used"]
            )

        except subprocess.TimeoutExpired:
            return DependencyInstallResult(
                success=False,
                agent_path=agent_path,
                venv_path=venv_path,
                install_time_seconds=time.time() - start_time,
                installed_packages=[],
                error_message="Dependency installation timed out",
                warnings=["Large dependency trees may take longer to install"]
            )
        except Exception as e:
            return DependencyInstallResult(
                success=False,
                agent_path=agent_path,
                venv_path=venv_path,
                install_time_seconds=time.time() - start_time,
                installed_packages=[],
                error_message=f"Unexpected error during dependency installation: {e}",
                warnings=["Check system logs for more details"]
            )

    def _collect_environment_info(self, agent_path: Path, venv_path: Path) -> Dict[str, Any]:
        """Collect information about the created environment."""
        info = {
            "venv_path": str(venv_path),
            "python_executable": str(venv_path / "bin" / "python"),
            "uv_version": self._get_uv_version(),
            "project_files": self._get_project_files(agent_path)
        }
        return info

    def _get_uv_version(self) -> str:
        """Get UV version."""
        try:
            result = subprocess.run(
                ["uv", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout.strip() if result.returncode == 0 else "Unknown"
        except Exception:
            return "Unknown"

    def _get_project_files(self, agent_path: Path) -> List[str]:
        """Get list of project files."""
        try:
            return [f.name for f in agent_path.iterdir() if f.is_file()]
        except Exception:
            return []

    def _get_installed_packages(self, venv_path: str) -> List[str]:
        """Get list of installed packages in the virtual environment."""
        try:
            result = subprocess.run(
                ["uv", "pip", "list"],
                cwd=venv_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                # Parse the output to extract package names
                lines = result.stdout.strip().split('\n')[2:]  # Skip header lines
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
