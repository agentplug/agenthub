"""
Auto-installer for Agent Hub Phase 2.

This module provides the main AutoInstaller class that orchestrates the complete
agent installation workflow including cloning, validation, and environment setup.
"""

import logging
import time
from dataclasses import dataclass
from typing import List, Optional

# Check if environment module is available
try:
    from ..environment.environment_setup import EnvironmentSetup
    ENVIRONMENT_AVAILABLE = True
except ImportError:
    ENVIRONMENT_AVAILABLE = False

from .url_parser import URLParser
from .repository_cloner import RepositoryCloner, CloneResult
from .repository_validator import RepositoryValidator, ValidationResult

logger = logging.getLogger(__name__)


@dataclass
class InstallationResult:
    """Result of agent installation operation."""
    success: bool
    agent_name: str
    local_path: str
    github_url: str
    clone_result: Optional[CloneResult] = None
    validation_result: Optional[ValidationResult] = None
    environment_result: Optional[object] = None  # EnvironmentSetupResult
    dependency_result: Optional[object] = None  # DependencyInstallResult
    installation_time_seconds: Optional[float] = None
    error_message: Optional[str] = None
    warnings: List[str] = None
    next_steps: List[str] = None

    def __post_init__(self):
        """Initialize lists if they are None."""
        if self.warnings is None:
            self.warnings = []
        if self.next_steps is None:
            self.next_steps = []


class InstallationError(Exception):
    """Exception raised when agent installation fails."""
    pass


class AutoInstaller:
    """
    Main class for orchestrating agent installation workflow.

    This class coordinates the complete process from agent name to ready-to-use
    agent, including URL parsing, cloning, validation, and environment setup.
    """

    def __init__(self, base_storage_path: Optional[str] = None,
                 setup_environment: bool = True):
        """
        Initialize the AutoInstaller.

        Args:
            base_storage_path: Base path for agent storage
            setup_environment: Whether to set up virtual environments
        """
        self.url_parser = URLParser()
        self.repository_cloner = RepositoryCloner(base_storage_path)
        self.repository_validator = RepositoryValidator()
        self.setup_environment = setup_environment
        self.base_storage_path = self.repository_cloner.base_storage_path

        # Initialize environment setup if available
        if setup_environment and ENVIRONMENT_AVAILABLE:
            try:
                self.environment_setup = EnvironmentSetup()
                logger.debug("Environment setup initialized successfully")
            except Exception as e:
                logger.warning(f"Environment setup not available: {e}")
                self.environment_setup = None
                self.setup_environment = False
        else:
            self.environment_setup = None
            if setup_environment and not ENVIRONMENT_AVAILABLE:
                logger.warning("Environment setup requested but not available")
                self.setup_environment = False

    def install_agent(self, agent_name: str) -> InstallationResult:
        """
        Install an agent using the complete workflow.

        Args:
            agent_name: Agent name in format 'developer/agent-name'

        Returns:
            InstallationResult with complete installation details
        """
        start_time = time.time()
        logger.info(f"Starting installation of agent: {agent_name}")

        try:
            # Step 1: Validate agent name and construct GitHub URL
            logger.debug("Step 1: Validating agent name and constructing GitHub URL")
            github_url = self.url_parser.build_github_url(agent_name)
            if not github_url:
                return self._create_failure_result(
                    agent_name, start_time,
                    f"Invalid agent name format: {agent_name}. "
                    f"Expected: developer/agent-name"
                )

            # Step 2: Clone the repository
            logger.debug("Step 2: Cloning repository")
            clone_result = self.repository_cloner.clone_repository(agent_name)
            if not clone_result.success:
                return self._create_failure_result(
                    agent_name, start_time,
                    f"Repository cloning failed: {clone_result.error_message}",
                    clone_result=clone_result
                )

            # Step 3: Validate the repository
            logger.debug("Step 3: Validating repository")
            validation_result = self.repository_validator.validate_repository(
                clone_result.local_path
            )
            if not validation_result.success:
                return self._create_failure_result(
                    agent_name, start_time,
                    f"Repository validation failed: {validation_result.error_message}",
                    clone_result=clone_result,
                    validation_result=validation_result
                )

            # Step 4: Set up environment (if enabled)
            environment_result = None
            if self.setup_environment and self.environment_setup:
                logger.debug("Step 4: Setting up virtual environment")
                environment_result = self.environment_setup.setup_environment(
                    clone_result.local_path
                )
                if not environment_result.success:
                    logger.warning(
                        f"Environment setup failed: {environment_result.error_message}"
                    )
                    # Continue without environment setup

            # Step 5: Install dependencies (if environment setup succeeded)
            dependency_result = None
            if environment_result and environment_result.success:
                logger.debug("Step 5: Installing dependencies")
                dependency_result = self.environment_setup.install_dependencies(
                    clone_result.local_path,
                    environment_result.venv_path
                )
                if not dependency_result.success:
                    logger.warning(
                        f"Dependency installation failed: "
                        f"{dependency_result.error_message}"
                    )

            # Step 6: Determine success and collect results
            installation_time = time.time() - start_time
            success = (clone_result.success and validation_result.success and
                      (not self.setup_environment or not environment_result or
                       environment_result.success))

            # Step 7: Create result object
            result = InstallationResult(
                success=success,
                agent_name=agent_name,
                local_path=clone_result.local_path,
                github_url=github_url,
                clone_result=clone_result,
                validation_result=validation_result,
                environment_result=environment_result,
                dependency_result=dependency_result,
                installation_time_seconds=installation_time,
                warnings=self._collect_warnings(
                    clone_result, validation_result,
                    environment_result, dependency_result
                ),
                next_steps=self._get_next_steps(
                    success, agent_name, clone_result, validation_result,
                    environment_result, dependency_result
                )
            )

            if success:
                logger.info(
                    f"Agent installation completed successfully in "
                    f"{installation_time:.2f}s"
                )
            else:
                logger.warning(
                    f"Agent installation completed with issues in "
                    f"{installation_time:.2f}s"
                )

            return result

        except Exception as e:
            installation_time = time.time() - start_time
            error_msg = f"Unexpected error during installation: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return self._create_failure_result(agent_name, start_time, error_msg)

    def _create_failure_result(self, agent_name: str, start_time: float,
                              error_message: str,
                              clone_result: Optional[CloneResult] = None,
                              validation_result: Optional[ValidationResult] = None) -> InstallationResult:
        """Create a failure result object."""
        return InstallationResult(
            success=False,
            agent_name=agent_name,
            local_path="",
            github_url="",
            clone_result=clone_result,
            validation_result=validation_result,
            installation_time_seconds=time.time() - start_time,
            error_message=error_message,
            warnings=[],
            next_steps=[
                "Check the error message above",
                "Verify agent name format and availability"
            ]
        )

    def _collect_warnings(self, clone_result: CloneResult,
                         validation_result: ValidationResult,
                         environment_result: Optional[object],
                         dependency_result: Optional[object]) -> List[str]:
        """Collect warnings from all installation steps."""
        warnings = []

        if clone_result.warnings:
            warnings.extend(clone_result.warnings)
        if validation_result.warnings:
            warnings.extend(validation_result.warnings)
        if (environment_result and hasattr(environment_result, 'warnings') and
            environment_result.warnings):
            warnings.extend(environment_result.warnings)
        if (dependency_result and hasattr(dependency_result, 'warnings') and
            dependency_result.warnings):
            warnings.extend(dependency_result.warnings)

        return warnings

    def _get_next_steps(self, success: bool, agent_name: str,
                        clone_result: CloneResult,
                        validation_result: ValidationResult,
                        environment_result: Optional[object],
                        dependency_result: Optional[object]) -> List[str]:
        """Get next steps guidance based on installation results."""
        if success:
            return self._get_next_steps_for_success(
                agent_name, clone_result, validation_result,
                environment_result, dependency_result
            )
        else:
            return self._get_next_steps_for_failure(
                agent_name, clone_result, validation_result, environment_result
            )

    def _get_next_steps_for_success(self, agent_name: str,
                                   clone_result: CloneResult,
                                   validation_result: ValidationResult,
                                   environment_result: Optional[object],
                                   dependency_result: Optional[object]) -> List[str]:
        """Get next steps for successful installation."""
        next_steps = [
            f"✅ Agent '{agent_name}' installed successfully!",
            f"📁 Local path: {clone_result.local_path}",
            f"🔗 GitHub URL: {clone_result.github_url}"
        ]

        if environment_result and environment_result.success:
            next_steps.extend([
                "🌍 Virtual environment created successfully",
                f"📦 Environment path: {environment_result.venv_path}"
            ])

            if dependency_result and dependency_result.success:
                next_steps.extend([
                    "📚 Dependencies installed successfully",
                    f"📦 {len(dependency_result.installed_packages)} packages installed"
                ])
            else:
                next_steps.append("⚠️ Dependencies may need manual installation")

            # Add activation command if environment setup is available
            if self.environment_setup:
                activation_cmd = self.environment_setup.activate_environment(
                    environment_result.venv_path
                )
                next_steps.append(f"💡 Activation command: {activation_cmd}")

        else:
            next_steps.extend([
                "⚠️ Virtual environment not created",
                "🔧 Consider running with setup_environment=True"
            ])

        next_steps.extend([
            "🚀 Next: Activate the environment and test the agent",
            "📖 Check the agent's README.md for usage instructions"
        ])

        return next_steps

    def _get_next_steps_for_failure(self, agent_name: str,
                                   clone_result: CloneResult,
                                   validation_result: ValidationResult,
                                   environment_result: Optional[object]) -> List[str]:
        """Get next steps for failed installation."""
        next_steps = [
            f"❌ Installation of agent '{agent_name}' failed",
            "🔍 Review the error messages above for specific issues"
        ]

        if clone_result and not clone_result.success:
            next_steps.extend([
                "📥 Cloning failed - check:",
                "   • Agent name format (developer/agent-name)",
                "   • Repository accessibility",
                "   • Network connectivity"
            ])

        if validation_result and not validation_result.success:
            next_steps.extend([
                "✅ Cloning succeeded but validation failed - check:",
                "   • Required files (agent.py, agent.yaml, requirements.txt, README.md)",
                "   • File formats and content"
            ])

        if environment_result and not environment_result.success:
            next_steps.extend([
                "🌍 Environment setup failed - check:",
                "   • UV installation and availability",
                "   • pyproject.toml file presence",
                "   • System permissions"
            ])

        next_steps.extend([
            "🔧 Try running the installation again",
            "📖 Check the agent's repository for requirements",
            "💡 Consider running without environment setup: setup_environment=False"
        ])

        return next_steps
