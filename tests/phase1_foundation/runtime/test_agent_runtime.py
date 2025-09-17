"""Tests for AgentRuntime class."""

import sys
from pathlib import Path

import pytest

from agenthub.runtime.agent_runtime import AgentRuntime


class TestAgentRuntime:
    """Test cases for AgentRuntime class."""

    def test_init_without_storage(self):
        """Test AgentRuntime initialization without storage."""
        runtime = AgentRuntime()
        assert runtime.process_manager is not None
        assert runtime.environment_manager is not None
        assert runtime.storage is None

    def test_init_with_storage(self):
        """Test AgentRuntime initialization with storage."""
        mock_storage = object()
        runtime = AgentRuntime(storage=mock_storage)
        assert runtime.storage is mock_storage

    def test_load_agent_manifest_nonexistent_directory(self):
        """Test load_agent_manifest raises error for nonexistent directory."""
        runtime = AgentRuntime()

        with pytest.raises(FileNotFoundError, match="Agent directory does not exist"):
            runtime.load_agent_manifest("/nonexistent/path")

    def test_load_agent_manifest_missing_file(self, temp_dir: Path):
        """Test load_agent_manifest raises error for missing manifest."""
        runtime = AgentRuntime()
        agent_dir = temp_dir / "test-agent"
        agent_dir.mkdir()

        with pytest.raises(ValueError, match="Agent manifest not found"):
            runtime.load_agent_manifest(str(agent_dir))

    def test_load_agent_manifest_invalid_yaml(self, temp_dir: Path):
        """Test load_agent_manifest raises error for invalid YAML."""
        runtime = AgentRuntime()
        agent_dir = temp_dir / "test-agent"
        agent_dir.mkdir()

        # Create invalid YAML
        manifest_path = agent_dir / "agent.yaml"
        manifest_path.write_text("invalid: yaml: content: [")

        with pytest.raises(ValueError, match="Invalid YAML in manifest"):
            runtime.load_agent_manifest(str(agent_dir))

    def test_load_agent_manifest_missing_required_fields(self, temp_dir: Path):
        """Test load_agent_manifest raises error for missing required fields."""
        runtime = AgentRuntime()
        agent_dir = temp_dir / "test-agent"
        agent_dir.mkdir()

        # Create manifest missing required fields
        manifest_path = agent_dir / "agent.yaml"
        manifest_path.write_text("description: Test agent")

        with pytest.raises(ValueError, match="Missing required field in manifest"):
            runtime.load_agent_manifest(str(agent_dir))

    def test_load_agent_manifest_success(
        self, sample_agent_manifest: dict, temp_dir: Path
    ):
        """Test successful agent manifest loading."""
        runtime = AgentRuntime()
        agent_dir = temp_dir / "test-agent"
        agent_dir.mkdir()

        # Create valid manifest
        manifest_path = agent_dir / "agent.yaml"
        import yaml

        with open(manifest_path, "w") as f:
            yaml.dump(sample_agent_manifest, f)

        result = runtime.load_agent_manifest(str(agent_dir))
        assert result["name"] == sample_agent_manifest["name"]
        assert result["interface"] == sample_agent_manifest["interface"]

    def test_validate_method_success(self, mock_agent_directory: Path):
        """Test successful method validation."""
        runtime = AgentRuntime()

        result = runtime.validate_method(str(mock_agent_directory), "test_method")
        assert result is True

    def test_validate_method_invalid_method(self, mock_agent_directory: Path):
        """Test method validation with invalid method."""
        runtime = AgentRuntime()

        result = runtime.validate_method(
            str(mock_agent_directory), "nonexistent_method"
        )
        assert result is False

    def test_validate_method_invalid_agent(self):
        """Test method validation with invalid agent path."""
        runtime = AgentRuntime()

        result = runtime.validate_method("/nonexistent/path", "test_method")
        assert result is False

    def test_get_available_methods_success(self, mock_agent_directory: Path):
        """Test getting available methods for valid agent."""
        runtime = AgentRuntime()

        methods = runtime.get_available_methods(str(mock_agent_directory))
        assert "test_method" in methods

    def test_get_available_methods_invalid_agent(self):
        """Test getting available methods for invalid agent."""
        runtime = AgentRuntime()

        methods = runtime.get_available_methods("/nonexistent/path")
        assert methods == []

    def test_get_agent_info_success(self, mock_agent_directory: Path):
        """Test getting agent info for valid agent."""
        runtime = AgentRuntime()

        # Create mock virtual environment for structure validation
        venv_path = mock_agent_directory / ".venv"
        if sys.platform == "win32":
            python_dir = venv_path / "Scripts"
            python_exe = python_dir / "python.exe"
        else:
            python_dir = venv_path / "bin"
            python_exe = python_dir / "python"

        python_dir.mkdir(parents=True)
        python_exe.touch()

        info = runtime.get_agent_info(str(mock_agent_directory))

        assert info["name"] == "test-agent"
        assert "test_method" in info["methods"]
        assert info["path"] == str(mock_agent_directory)

    def test_get_agent_info_invalid_agent(self):
        """Test getting agent info for invalid agent."""
        runtime = AgentRuntime()

        info = runtime.get_agent_info("/nonexistent/path")
        assert "error" in info
        assert info["valid_structure"] is False

    def test_execute_agent_without_storage(self, mock_agent_directory: Path):
        """Test execute_agent without storage (direct path)."""
        runtime = AgentRuntime()

        # This should fail because we're using direct path construction
        # and the agent won't be found in the default location
        result = runtime.execute_agent("test", "test-agent", "test_method", {})
        assert "error" in result
        assert "Invalid agent structure" in result["error"]

    def test_execute_agent_with_storage_nonexistent_agent(self):
        """Test execute_agent with storage for nonexistent agent."""

        # Mock storage that returns False for agent_exists
        class MockStorage:
            def agent_exists(self, namespace, agent_name):
                return False

        runtime = AgentRuntime(storage=MockStorage())

        result = runtime.execute_agent("test", "nonexistent-agent", "test_method", {})
        assert "error" in result
        assert "Agent not found" in result["error"]

    def test_execute_agent_invalid_method(self, mock_agent_directory: Path):
        """Test execute_agent with invalid method."""
        # Create mock virtual environment for structure validation
        venv_path = mock_agent_directory / ".venv"
        if sys.platform == "win32":
            python_dir = venv_path / "Scripts"
            python_exe = python_dir / "python.exe"
        else:
            python_dir = venv_path / "bin"
            python_exe = python_dir / "python"

        python_dir.mkdir(parents=True)
        python_exe.touch()

        # Mock storage that finds the agent
        class MockStorage:
            def agent_exists(self, namespace, agent_name):
                return True

            def get_agent_path(self, namespace, agent_name):
                return mock_agent_directory

        runtime = AgentRuntime(storage=MockStorage())

        result = runtime.execute_agent("test", "test-agent", "invalid_method", {})
        assert "error" in result
        assert "Method 'invalid_method' not found" in result["error"]
        assert "available_methods" in result
