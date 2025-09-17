"""Test Repository Cloner functionality."""

import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

import agenthub
from agenthub.github.repository_cloner import (
    CloneError,
    CloneResult,
    GitNotAvailableError,
    RepositoryCloner,
    RepositoryNotFoundError,
)


class TestRepositoryCloner:
    """Test RepositoryCloner basic functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        # Use a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()
        self.cloner = RepositoryCloner(base_storage_path=self.temp_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        # Clean up temporary directory
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        """Test RepositoryCloner initialization."""
        # Test default initialization
        default_cloner = RepositoryCloner()
        expected_default = Path.home() / ".agenthub" / "agents"
        assert default_cloner.base_storage_path == expected_default

        # Test custom path initialization
        assert self.cloner.base_storage_path == Path(self.temp_dir)
        assert self.cloner.base_storage_path.exists()

    def test_get_agent_storage_path(self):
        """Test agent storage path generation."""
        # Test normal agent name
        path = self.cloner._get_agent_storage_path("user/agent")
        expected = Path(self.temp_dir) / "user" / "agent"
        assert path == expected

        # Test agent name with hyphens
        path = self.cloner._get_agent_storage_path("test-user/awesome-agent")
        expected = Path(self.temp_dir) / "test-user" / "awesome-agent"
        assert path == expected

    @patch("subprocess.run")
    def test_check_git_available_success(self, mock_run):
        """Test git availability check when git is available."""
        mock_run.return_value = Mock(returncode=0)

        result = self.cloner._check_git_available()
        assert result is True

        mock_run.assert_called_once_with(
            ["git", "--version"], capture_output=True, text=True, timeout=10
        )

    @patch("subprocess.run")
    def test_check_git_available_failure(self, mock_run):
        """Test git availability check when git is not available."""
        mock_run.return_value = Mock(returncode=1)

        result = self.cloner._check_git_available()
        assert result is False

    @patch("subprocess.run")
    def test_check_git_available_not_found(self, mock_run):
        """Test git availability check when git command is not found."""
        mock_run.side_effect = FileNotFoundError()

        result = self.cloner._check_git_available()
        assert result is False


class TestCloneAgent:
    """Test the main clone_agent functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cloner = RepositoryCloner(base_storage_path=self.temp_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_clone_agent_invalid_name(self):
        """Test clone_agent with invalid agent name."""
        with pytest.raises(ValueError, match="Invalid agent name format"):
            self.cloner.clone_agent("invalid-name")

    @patch.object(RepositoryCloner, "_check_git_available")
    def test_clone_agent_git_not_available(self, mock_git_check):
        """Test clone_agent when git is not available."""
        mock_git_check.return_value = False

        with pytest.raises(GitNotAvailableError, match="Git is not available"):
            self.cloner.clone_agent("user/agent")

    @patch.object(RepositoryCloner, "_check_git_available")
    @patch.object(RepositoryCloner, "_execute_git_clone")
    def test_clone_agent_success(self, mock_git_clone, mock_git_check):
        """Test successful agent cloning."""
        mock_git_check.return_value = True
        mock_git_clone.return_value = Mock(returncode=0, stderr="")

        result = self.cloner.clone_agent("user/agent")

        assert isinstance(result, CloneResult)
        assert result.success is True
        assert result.agent_name == "user/agent"
        assert result.github_url == "https://github.com/user/agent.git"
        assert result.local_path == str(Path(self.temp_dir) / "user" / "agent")
        assert result.clone_time_seconds is not None
        assert result.error_message is None

    @patch.object(RepositoryCloner, "_check_git_available")
    @patch.object(RepositoryCloner, "_execute_git_clone")
    def test_clone_agent_repository_not_found(self, mock_git_clone, mock_git_check):
        """Test clone_agent when repository is not found."""
        mock_git_check.return_value = True
        mock_git_clone.return_value = Mock(
            returncode=1,
            stderr="fatal: repository 'https://github.com/user/agent.git' not found",
        )

        with pytest.raises(RepositoryNotFoundError, match="Repository not found"):
            self.cloner.clone_agent("user/agent")

    @patch.object(RepositoryCloner, "_check_git_available")
    @patch.object(RepositoryCloner, "_execute_git_clone")
    def test_clone_agent_generic_error(self, mock_git_clone, mock_git_check):
        """Test clone_agent with generic git error."""
        mock_git_check.return_value = True
        mock_git_clone.return_value = Mock(
            returncode=1, stderr="fatal: some other git error"
        )

        with pytest.raises(CloneError, match="Git clone failed"):
            self.cloner.clone_agent("user/agent")

    @patch.object(RepositoryCloner, "_check_git_available")
    @patch.object(RepositoryCloner, "_execute_git_clone")
    def test_clone_agent_with_custom_path(self, mock_git_clone, mock_git_check):
        """Test clone_agent with custom target path."""
        mock_git_check.return_value = True
        mock_git_clone.return_value = Mock(returncode=0, stderr="")

        custom_path = str(Path(self.temp_dir) / "custom_location")
        result = self.cloner.clone_agent("user/agent", target_path=custom_path)

        assert result.success is True
        assert result.local_path == custom_path


class TestAgentManagement:
    """Test agent management functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cloner = RepositoryCloner(base_storage_path=self.temp_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_is_agent_cloned_false(self):
        """Test is_agent_cloned when agent is not cloned."""
        assert self.cloner.is_agent_cloned("user/agent") is False

    def test_is_agent_cloned_invalid_name(self):
        """Test is_agent_cloned with invalid agent name."""
        assert self.cloner.is_agent_cloned("invalid") is False

    def test_is_agent_cloned_true(self):
        """Test is_agent_cloned when agent is cloned."""
        # Create a mock cloned agent directory
        agent_path = Path(self.temp_dir) / "user" / "agent"
        agent_path.mkdir(parents=True)
        (agent_path / "test_file.txt").write_text("test content")

        assert self.cloner.is_agent_cloned("user/agent") is True

    def test_get_agent_path_not_cloned(self):
        """Test get_agent_path when agent is not cloned."""
        assert self.cloner.get_agent_path("user/agent") is None

    def test_get_agent_path_cloned(self):
        """Test get_agent_path when agent is cloned."""
        # Create a mock cloned agent directory
        agent_path = Path(self.temp_dir) / "user" / "agent"
        agent_path.mkdir(parents=True)
        (agent_path / "test_file.txt").write_text("test content")

        result = self.cloner.get_agent_path("user/agent")
        assert result == str(agent_path)

    def test_list_cloned_agents_empty(self):
        """Test list_cloned_agents when no agents are cloned."""
        result = self.cloner.list_cloned_agents()
        assert result == {}

    def test_list_cloned_agents_with_agents(self):
        """Test list_cloned_agents with cloned agents."""
        # Create mock cloned agents
        agents = ["user/agent1", "developer/agent2", "company/tool"]
        for agent in agents:
            parts = agent.split("/")
            developer_dir = Path(self.temp_dir) / parts[0]
            developer_dir.mkdir(parents=True, exist_ok=True)
            agent_path = developer_dir / parts[1]
            agent_path.mkdir(parents=True)
            (agent_path / "test_file.txt").write_text("test content")

        result = self.cloner.list_cloned_agents()

        assert len(result) == 3
        for agent in agents:
            assert agent in result
            parts = agent.split("/")
            expected_path = str(Path(self.temp_dir) / parts[0] / parts[1])
            assert result[agent] == expected_path

    def test_remove_agent_not_found(self):
        """Test remove_agent when agent is not found."""
        assert self.cloner.remove_agent("user/agent") is False

    def test_remove_agent_invalid_name(self):
        """Test remove_agent with invalid agent name."""
        assert self.cloner.remove_agent("invalid") is False

    def test_remove_agent_success(self):
        """Test successful agent removal."""
        # Create a mock cloned agent directory
        agent_path = Path(self.temp_dir) / "user" / "agent"
        agent_path.mkdir(parents=True)
        (agent_path / "test_file.txt").write_text("test content")

        # Verify it exists
        assert self.cloner.is_agent_cloned("user/agent") is True

        # Remove it
        assert self.cloner.remove_agent("user/agent") is True

        # Verify it's gone
        assert self.cloner.is_agent_cloned("user/agent") is False


class TestGitCloneExecution:
    """Test git clone command execution."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cloner = RepositoryCloner(base_storage_path=self.temp_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    @patch("subprocess.run")
    def test_execute_git_clone_success(self, mock_run):
        """Test successful git clone execution."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        github_url = "https://github.com/user/agent.git"
        target_path = Path(self.temp_dir) / "test_clone"

        result = self.cloner._execute_git_clone(github_url, target_path)

        assert result.returncode == 0
        mock_run.assert_called_once_with(
            ["git", "clone", "--recursive", github_url, str(target_path)],
            capture_output=True,
            text=True,
            timeout=300,
        )

    @patch("subprocess.run")
    def test_execute_git_clone_timeout(self, mock_run):
        """Test git clone timeout."""
        mock_run.side_effect = subprocess.TimeoutExpired("git", 300)

        github_url = "https://github.com/user/agent.git"
        target_path = Path(self.temp_dir) / "test_clone"

        with pytest.raises(CloneError, match="Clone operation timed out"):
            self.cloner._execute_git_clone(github_url, target_path)


class TestIntegration:
    """Test integration with other components."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.cloner = RepositoryCloner(base_storage_path=self.temp_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        if Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)

    def test_import_from_module(self):
        """Test that RepositoryCloner can be imported from the github module."""
        from agenthub.github import RepositoryCloner as ModuleRepositoryCloner
        from agenthub.github.repository_cloner import (
            RepositoryCloner as DirectRepositoryCloner,
        )

        # Both imports should work and be the same class
        assert ModuleRepositoryCloner is DirectRepositoryCloner

        # Should be able to instantiate
        cloner1 = ModuleRepositoryCloner()
        cloner2 = DirectRepositoryCloner()

        # Should have the same functionality
        assert cloner1.base_storage_path == cloner2.base_storage_path

    def test_module_exports(self):
        """Test that the github module properly exports RepositoryCloner."""

        # RepositoryCloner should be in __all__
        assert "RepositoryCloner" in agenthub.github.__all__
        assert "CloneResult" in agenthub.github.__all__
        assert "CloneError" in agenthub.github.__all__
        assert "RepositoryNotFoundError" in agenthub.github.__all__
        assert "GitNotAvailableError" in agenthub.github.__all__

        # Should be accessible as attributes
        assert hasattr(agenthub.github, "RepositoryCloner")
        assert hasattr(agenthub.github, "CloneResult")
        assert hasattr(agenthub.github, "CloneError")

        # Should be the correct classes
        cloner = agenthub.github.RepositoryCloner()
        expected_path = Path.home() / ".agenthub" / "agents"
        assert cloner.base_storage_path == expected_path

    def test_url_parser_integration(self):
        """Test integration with URLParser."""
        # RepositoryCloner should use URLParser internally
        assert hasattr(self.cloner, "url_parser")

        # Should validate agent names correctly
        assert self.cloner.url_parser.is_valid_agent_name("user/agent") is True
        assert self.cloner.url_parser.is_valid_agent_name("invalid") is False

        # Should build GitHub URLs correctly
        url = self.cloner.url_parser.build_github_url("user/agent")
        assert url == "https://github.com/user/agent.git"


class TestBackwardCompatibility:
    """Test that RepositoryCloner doesn't break existing functionality."""

    def test_existing_imports_still_work(self):
        """Test that existing module imports still work."""
        # These should still work after adding RepositoryCloner
        from agenthub import load_agent
        from agenthub.core.agents.loader import AgentLoader
        from agenthub.github import URLParser
        from agenthub.storage.local_storage import LocalStorage

        # Should be able to instantiate existing components
        storage = LocalStorage()
        loader = AgentLoader(storage)
        parser = URLParser()

        assert storage is not None
        assert loader is not None
        assert parser is not None
        assert callable(load_agent)

    def test_no_side_effects(self):
        """Test that importing RepositoryCloner has no side effects."""
        # Import RepositoryCloner
        # Existing functionality should still work
        from agenthub.core.agents.loader import AgentLoader
        from agenthub.github import URLParser
        from agenthub.github.repository_cloner import RepositoryCloner
        from agenthub.storage.local_storage import LocalStorage

        storage = LocalStorage()
        loader = AgentLoader(storage)
        parser = URLParser()

        # Creating RepositoryCloner should not affect existing components
        cloner = RepositoryCloner()
        expected_path = Path.home() / ".agenthub" / "agents"
        assert cloner.base_storage_path == expected_path

        # Existing components should still work normally
        assert loader.storage is storage
        assert parser.is_valid_agent_name("user/agent")


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
