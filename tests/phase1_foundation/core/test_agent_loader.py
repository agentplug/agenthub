"""Tests for AgentLoader class."""

from pathlib import Path

import pytest

from agenthub.core.agents.loader import AgentLoader, AgentLoadError


class TestAgentLoader:
    """Test cases for AgentLoader class."""

    def test_init_without_storage(self):
        """Test AgentLoader initialization without storage."""
        loader = AgentLoader()
        assert loader is not None
        assert loader.storage is None

    def test_init_with_storage(self):
        """Test AgentLoader initialization with storage."""
        mock_storage = object()
        loader = AgentLoader(storage=mock_storage)
        assert loader.storage is mock_storage

    def test_load_agent_by_path_valid(self, mock_agent_directory: Path):
        """Test loading a valid agent by path."""
        loader = AgentLoader()

        # Create virtual environment for structure validation
        venv_path = mock_agent_directory / ".venv"
        import sys

        if sys.platform == "win32":
            python_dir = venv_path / "Scripts"
            python_exe = python_dir / "python.exe"
        else:
            python_dir = venv_path / "bin"
            python_exe = python_dir / "python"

        python_dir.mkdir(parents=True)
        python_exe.touch()

        agent_info = loader.load_agent_by_path(str(mock_agent_directory))

        assert agent_info["name"] == "test-agent"
        assert agent_info["version"] == "1.0.0"
        assert agent_info["path"] == str(mock_agent_directory)
        assert "manifest" in agent_info
        assert "methods" in agent_info

    def test_load_agent_by_path_nonexistent(self):
        """Test loading nonexistent agent by path."""
        loader = AgentLoader()

        with pytest.raises(AgentLoadError, match="Agent directory does not exist"):
            loader.load_agent_by_path("/nonexistent/path")

    def test_load_agent_by_path_invalid_structure(self, temp_dir: Path):
        """Test loading agent with invalid structure."""
        loader = AgentLoader()

        # Create directory without required files
        agent_dir = temp_dir / "invalid-agent"
        agent_dir.mkdir()

        with pytest.raises(AgentLoadError, match="Invalid agent structure"):
            loader.load_agent_by_path(str(agent_dir))

    def test_load_agent_with_storage(self, mock_agent_directory: Path):
        """Test loading agent using storage."""

        # Mock storage that finds the agent
        class MockStorage:
            def agent_exists(self, namespace, agent_name):
                return True

            def get_agent_path(self, namespace, agent_name):
                return mock_agent_directory

        # Create virtual environment
        venv_path = mock_agent_directory / ".venv"
        import sys

        if sys.platform == "win32":
            python_dir = venv_path / "Scripts"
            python_exe = python_dir / "python.exe"
        else:
            python_dir = venv_path / "bin"
            python_exe = python_dir / "python"

        python_dir.mkdir(parents=True)
        python_exe.touch()

        loader = AgentLoader(storage=MockStorage())

        agent_info = loader.load_agent("test", "test-agent")

        assert agent_info["name"] == "test-agent"
        assert agent_info["namespace"] == "test"
        assert agent_info["agent_name"] == "test-agent"

    def test_load_agent_not_found_with_storage(self):
        """Test loading nonexistent agent with storage."""

        # Mock storage that doesn't find the agent
        class MockStorage:
            def agent_exists(self, namespace, agent_name):
                return False

        loader = AgentLoader(storage=MockStorage())

        with pytest.raises(AgentLoadError, match="Agent not found"):
            loader.load_agent("test", "nonexistent-agent")

    def test_load_agent_without_storage(self):
        """Test loading agent without storage should raise error."""
        loader = AgentLoader()

        with pytest.raises(AgentLoadError, match="No storage provided"):
            loader.load_agent("test", "test-agent")

    def test_validate_agent_structure_valid(self, mock_agent_directory: Path):
        """Test validating valid agent structure."""
        loader = AgentLoader()

        # Create virtual environment
        venv_path = mock_agent_directory / ".venv"
        import sys

        if sys.platform == "win32":
            python_dir = venv_path / "Scripts"
            python_exe = python_dir / "python.exe"
        else:
            python_dir = venv_path / "bin"
            python_exe = python_dir / "python"

        python_dir.mkdir(parents=True)
        python_exe.touch()

        result = loader.validate_agent_structure(str(mock_agent_directory))
        assert result is True

    def test_validate_agent_structure_missing_files(self, temp_dir: Path):
        """Test validating agent with missing files."""
        loader = AgentLoader()

        # Create directory with some but not all required files
        agent_dir = temp_dir / "incomplete-agent"
        agent_dir.mkdir()
        (agent_dir / "agent.py").touch()  # Missing agent.yaml

        result = loader.validate_agent_structure(str(agent_dir))
        assert result is False

    def test_validate_agent_structure_missing_venv(self, temp_dir: Path):
        """Test validating agent with missing virtual environment."""
        loader = AgentLoader()

        # Create directory with files but no venv
        agent_dir = temp_dir / "no-venv-agent"
        agent_dir.mkdir()
        (agent_dir / "agent.py").touch()
        (agent_dir / "agent.yaml").touch()

        result = loader.validate_agent_structure(str(agent_dir), require_venv=True)
        assert result is False

    def test_discover_agents_with_storage(self):
        """Test discovering agents using storage."""

        # Mock storage with some agents
        class MockStorage:
            def discover_agents(self):
                return [
                    {"namespace": "test", "name": "agent1", "path": "/path/to/agent1"},
                    {"namespace": "test", "name": "agent2", "path": "/path/to/agent2"},
                ]

        loader = AgentLoader(storage=MockStorage())

        agents = loader.discover_agents()

        assert len(agents) == 2
        assert agents[0]["name"] == "agent1"
        assert agents[1]["name"] == "agent2"

    def test_discover_agents_without_storage(self):
        """Test discovering agents without storage should raise error."""
        loader = AgentLoader()

        with pytest.raises(AgentLoadError, match="No storage provided"):
            loader.discover_agents()
