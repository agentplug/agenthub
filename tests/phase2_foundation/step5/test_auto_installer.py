"""Tests for AutoInstaller - Complete Installation Workflow.

This module tests the AutoInstaller class that provides end-to-end
agent installation from GitHub repositories.
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from agenthub.github.auto_installer import (
    AutoInstaller,
    InstallationError,
    InstallationResult,
)
from agenthub.github.repository_cloner import CloneResult, RepositoryCloner
from agenthub.github.repository_validator import RepositoryValidator, ValidationResult
from agenthub.github.url_parser import URLParser


class TestAutoInstaller:
    """Test the AutoInstaller class functionality."""

    @pytest.fixture
    def temp_storage_path(self):
        """Create a temporary storage path for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_clone_result(self):
        """Create a mock successful clone result."""
        return CloneResult(
            success=True,
            local_path="/tmp/test/agent",
            agent_name="test/agent",
            github_url="https://github.com/test/agent.git",
            clone_time_seconds=1.5,
        )

    @pytest.fixture
    def mock_validation_result(self):
        """Create a mock successful validation result."""
        return ValidationResult(
            is_valid=True,
            local_path="/tmp/test/agent",
            missing_files=[],
            validation_errors=[],
            warnings=[],
            validation_time=0.1,
            repository_info={
                "total_files": "15",
                "python_files": "8",
                "has_pyproject_toml": "True",
            },
        )

    @pytest.fixture
    def auto_installer(self, temp_storage_path):
        """Create an AutoInstaller instance for testing."""
        return AutoInstaller(
            base_storage_path=temp_storage_path, setup_environment=False
        )

    def test_auto_installer_initialization(self, temp_storage_path):
        """Test AutoInstaller initialization."""
        installer = AutoInstaller(base_storage_path=temp_storage_path)

        assert installer.base_storage_path == Path(temp_storage_path)
        assert isinstance(installer.url_parser, URLParser)
        assert isinstance(installer.repository_cloner, RepositoryCloner)
        assert isinstance(installer.repository_validator, RepositoryValidator)
        assert installer.setup_environment is True

    def test_auto_installer_initialization_without_environment(self, temp_storage_path):
        """Test AutoInstaller initialization without environment setup."""
        installer = AutoInstaller(
            base_storage_path=temp_storage_path, setup_environment=False
        )

        assert installer.setup_environment is False
        assert installer.environment_setup is None

    def test_auto_installer_initialization_custom_storage(self, temp_storage_path):
        """Test AutoInstaller initialization with custom storage path."""
        custom_path = temp_storage_path
        installer = AutoInstaller(base_storage_path=custom_path)

        assert installer.base_storage_path == Path(custom_path)
        assert installer.repository_cloner.base_storage_path == Path(custom_path)

    @patch("agenthub.github.auto_installer.ENVIRONMENT_AVAILABLE", False)
    def test_auto_installer_environment_not_available(self, temp_storage_path):
        """Test AutoInstaller when environment setup is not available."""
        installer = AutoInstaller(
            base_storage_path=temp_storage_path, setup_environment=True
        )

        assert installer.setup_environment is False
        assert installer.environment_setup is None

    def test_install_agent_invalid_name_format(self, auto_installer):
        """Test installation with invalid agent name format."""
        result = auto_installer.install_agent("invalid-name")

        assert result.success is False
        assert result.agent_name == "invalid-name"
        assert "Invalid agent name format" in result.error_message
        assert result.local_path == ""
        assert result.github_url == ""

    def test_install_agent_empty_name(self, auto_installer):
        """Test installation with empty agent name."""
        result = auto_installer.install_agent("")

        assert result.success is False
        assert result.agent_name == ""
        assert "Invalid agent name format" in result.error_message

    def test_install_agent_none_name(self, auto_installer):
        """Test installation with None agent name."""
        result = auto_installer.install_agent(None)

        assert result.success is False
        assert result.agent_name is None
        assert "Invalid agent name format" in result.error_message

    @patch.object(RepositoryCloner, "clone_agent")
    def test_install_agent_clone_failure(self, mock_clone, auto_installer):
        """Test installation when repository cloning fails."""
        # Mock clone failure
        mock_clone.return_value = CloneResult(
            success=False,
            local_path="",
            agent_name="test/agent",
            github_url="https://github.com/test/agent.git",
            error_message="Repository not found",
        )

        result = auto_installer.install_agent("test/agent")

        assert result.success is False
        assert "Repository cloning failed" in result.error_message
        assert result.clone_result is not None
        assert result.clone_result.success is False

    @patch.object(RepositoryCloner, "clone_agent")
    @patch.object(RepositoryValidator, "validate_repository")
    def test_install_agent_validation_failure(
        self, mock_validate, mock_clone, auto_installer, mock_clone_result
    ):
        """Test installation when repository validation fails."""
        # Mock successful clone
        mock_clone.return_value = mock_clone_result

        # Mock validation failure
        mock_validate.return_value = ValidationResult(
            is_valid=False,
            local_path="/tmp/test/agent",
            missing_files=["agent.py", "requirements.txt"],
            validation_errors=["Missing required files"],
            warnings=[],
            validation_time=0.1,
            repository_info={},
        )

        result = auto_installer.install_agent("test/agent")

        assert result.success is False
        assert "Repository validation failed" in result.error_message
        assert result.validation_result is not None
        assert result.validation_result.is_valid is False
        assert "agent.py" in result.validation_result.missing_files

    @patch.object(RepositoryCloner, "clone_agent")
    @patch.object(RepositoryValidator, "validate_repository")
    def test_install_agent_success_basic(
        self,
        mock_validate,
        mock_clone,
        auto_installer,
        mock_clone_result,
        mock_validation_result,
    ):
        """Test successful installation without environment setup."""
        # Mock successful clone
        mock_clone.return_value = mock_clone_result

        # Mock successful validation
        mock_validate.return_value = mock_validation_result

        result = auto_installer.install_agent("test/agent")

        assert result.success is True
        assert result.agent_name == "test/agent"
        assert result.local_path == "/tmp/test/agent"
        assert result.github_url == "https://github.com/test/agent.git"
        assert result.clone_result is not None
        assert result.validation_result is not None
        assert result.installation_time_seconds is not None
        assert result.installation_time_seconds >= 0  # Allow 0 in test environment

    @patch.object(RepositoryCloner, "clone_agent")
    @patch.object(RepositoryValidator, "validate_repository")
    def test_install_agent_success_with_environment(
        self,
        mock_validate,
        mock_clone,
        temp_storage_path,
        mock_clone_result,
        mock_validation_result,
    ):
        """Test successful installation with environment setup."""
        # Mock environment setup availability
        with patch("agenthub.github.auto_installer.ENVIRONMENT_AVAILABLE", True):
            with patch(
                "agenthub.github.auto_installer.EnvironmentSetup"
            ) as mock_env_class:
                # Mock environment setup instance
                mock_env = Mock()
                mock_env.setup_environment.return_value = Mock(
                    success=True,
                    venv_path="/tmp/test/agent/.venv",
                    setup_time_seconds=2.0,
                    warnings=[],
                    next_steps=[],
                )
                mock_env.install_dependencies.return_value = Mock(
                    success=True,
                    agent_path="/tmp/test/agent",
                    venv_path="/tmp/test/agent/.venv",
                    install_time_seconds=5.0,
                    installed_packages=["requests", "pandas"],
                    warnings=[],
                )
                mock_env_class.return_value = mock_env

                installer = AutoInstaller(
                    base_storage_path=temp_storage_path, setup_environment=True
                )

                # Mock successful clone
                mock_clone.return_value = mock_clone_result

                # Mock successful validation
                mock_validate.return_value = mock_validation_result

                result = installer.install_agent("test/agent")

                assert result.success is True
                assert result.environment_result is not None
                assert result.dependency_result is not None
                assert result.environment_result.success is True
                assert result.dependency_result.success is True

    def test_get_next_steps_for_success_basic(
        self, auto_installer, mock_clone_result, mock_validation_result
    ):
        """Test getting next steps for successful installation without environment."""
        next_steps = auto_installer._get_next_steps_for_success(
            "test/agent", mock_clone_result, mock_validation_result
        )

        assert "✅ Agent 'test/agent' installed successfully!" in next_steps
        assert "📁 Local path: /tmp/test/agent" in next_steps

    def test_get_next_steps_for_success_with_environment(
        self, auto_installer, mock_clone_result, mock_validation_result
    ):
        """Test getting next steps for successful installation with environment."""
        mock_env_result = Mock(success=True, venv_path="/tmp/test/agent/.venv")
        mock_dep_result = Mock(success=True, installed_packages=["requests", "pandas"])

        next_steps = auto_installer._get_next_steps_for_success(
            "test/agent",
            mock_clone_result,
            mock_validation_result,
            mock_env_result,
            mock_dep_result,
        )

        assert "🌍 Virtual environment created successfully" in next_steps
        assert "📚 Dependencies installed successfully" in next_steps

    def test_get_next_steps_for_validation_failure(self, auto_installer):
        """Test getting next steps for validation failure."""
        mock_validation_result = Mock(
            is_valid=False,
            local_path="/tmp/test/agent",
            missing_files=["agent.py", "requirements.txt"],
        )

        next_steps = auto_installer._get_next_steps_for_failure(
            "test/agent", None, mock_validation_result, None
        )

        assert any("Repository validation failed" in step for step in next_steps)

    def test_collect_all_warnings(self, auto_installer, mock_validation_result):
        """Test collecting all warnings from installation steps."""
        mock_env_result = Mock(warnings=["Environment warning"])
        mock_dep_result = Mock(warnings=["Dependency warning"])

        warnings = auto_installer._collect_all_warnings(
            mock_validation_result, mock_env_result, mock_dep_result
        )

        assert len(warnings) == 2
        assert "Environment warning" in warnings
        assert "Dependency warning" in warnings

    def test_collect_all_warnings_none(self, auto_installer, mock_validation_result):
        """Test collecting warnings when some results are None."""
        warnings = auto_installer._collect_all_warnings(
            mock_validation_result, None, None
        )

        assert len(warnings) == 0

    def test_get_installation_summary_success(
        self, auto_installer, mock_clone_result, mock_validation_result
    ):
        """Test getting installation summary for successful installation."""
        result = InstallationResult(
            success=True,
            agent_name="test/agent",
            local_path="/tmp/test/agent",
            github_url="https://github.com/test/agent.git",
            clone_result=mock_clone_result,
            validation_result=mock_validation_result,
            installation_time_seconds=3.5,
        )

        summary = auto_installer.get_installation_summary(result)

        assert "🎉 Agent Installation Successful!" in summary
        assert "Agent: test/agent" in summary
        assert "Location: /tmp/test/agent" in summary
        assert "Time: 3.50s" in summary
        assert "Total Files: 15" in summary

    def test_get_installation_summary_failure(self, auto_installer):
        """Test getting installation summary for failed installation."""
        result = InstallationResult(
            success=False,
            agent_name="test/agent",
            local_path="",
            github_url="",
            error_message="Test error message",
        )

        summary = auto_installer.get_installation_summary(result)

        assert "❌ Agent Installation Failed!" in summary
        assert "Agent: test/agent" in summary
        assert "Error: Test error message" in summary

    @patch.object(RepositoryCloner, "list_cloned_agents")
    def test_list_installed_agents(self, mock_list, auto_installer):
        """Test listing installed agents."""
        mock_list.return_value = [
            {"name": "test/agent1", "path": "/tmp/agent1"},
            {"name": "test/agent2", "path": "/tmp/agent2"},
        ]

        agents = auto_installer.list_installed_agents()

        assert len(agents) == 2
        assert agents[0]["name"] == "test/agent1"
        assert agents[1]["name"] == "test/agent2"

    @patch.object(RepositoryCloner, "remove_agent")
    def test_remove_agent(self, mock_remove, auto_installer):
        """Test removing an agent."""
        mock_remove.return_value = True

        result = auto_installer.remove_agent("test/agent")

        assert result is True
        mock_remove.assert_called_once_with("test/agent")

    def test_install_agent_exception_handling(self, auto_installer):
        """Test exception handling during installation."""
        # Mock URLParser to raise an exception
        auto_installer.url_parser.is_valid_agent_name = Mock(
            side_effect=Exception("Test exception")
        )

        result = auto_installer.install_agent("test/agent")

        assert result.success is False
        assert "Unexpected error during installation" in result.error_message
        assert "Test exception" in result.error_message


class TestInstallationResult:
    """Test the InstallationResult dataclass."""

    def test_installation_result_creation(self):
        """Test creating an InstallationResult instance."""
        result = InstallationResult(
            success=True,
            agent_name="test/agent",
            local_path="/tmp/test/agent",
            github_url="https://github.com/test/agent.git",
        )

        assert result.success is True
        assert result.agent_name == "test/agent"
        assert result.local_path == "/tmp/test/agent"
        assert result.github_url == "https://github.com/test/agent.git"
        assert result.clone_result is None
        assert result.validation_result is None
        assert result.environment_result is None
        assert result.dependency_result is None
        assert result.installation_time_seconds is None
        assert result.error_message is None
        assert result.warnings == []
        assert result.next_steps == []

    def test_installation_result_with_optional_fields(self):
        """Test creating an InstallationResult with optional fields."""
        result = InstallationResult(
            success=False,
            agent_name="test/agent",
            local_path="",
            github_url="",
            error_message="Test error",
            warnings=["Warning 1", "Warning 2"],
            next_steps=["Step 1", "Step 2"],
        )

        assert result.success is False
        assert result.error_message == "Test error"
        assert len(result.warnings) == 2
        assert len(result.next_steps) == 2


class TestInstallationError:
    """Test the InstallationError exception."""

    def test_installation_error_creation(self):
        """Test creating an InstallationError instance."""
        error = InstallationError("Test error message")

        assert str(error) == "Test error message"
        assert isinstance(error, Exception)
