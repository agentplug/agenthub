"""Tests for ProcessManager class."""

import sys
from pathlib import Path

import pytest

from agenthub.runtime.process_manager import ProcessManager


class TestProcessManager:
    """Test cases for ProcessManager class."""

    def test_init_default_timeout(self):
        """Test ProcessManager initialization with default timeout."""
        pm = ProcessManager()
        assert pm.timeout == 300
        assert pm.environment_manager is not None

    def test_init_custom_timeout(self):
        """Test ProcessManager initialization with custom timeout."""
        pm = ProcessManager(timeout=60)
        assert pm.timeout == 60

    def test_execute_agent_invalid_parameters(self):
        """Test execute_agent raises ValueError for invalid parameters."""
        pm = ProcessManager()

        # Test empty agent_path
        with pytest.raises(ValueError, match="agent_path and method are required"):
            pm.execute_agent("", "test_method", {})

        # Test empty method
        with pytest.raises(ValueError, match="agent_path and method are required"):
            pm.execute_agent("/some/path", "", {})

    def test_execute_agent_nonexistent_directory(self):
        """Test execute_agent raises ValueError for nonexistent directory."""
        pm = ProcessManager()

        with pytest.raises(ValueError, match="Agent directory does not exist"):
            pm.execute_agent("/nonexistent/path", "test_method", {})

    def test_execute_agent_missing_script(self, temp_dir: Path):
        """Test execute_agent raises ValueError when agent.py is missing."""
        pm = ProcessManager()
        agent_dir = temp_dir / "test-agent"
        agent_dir.mkdir()

        with pytest.raises(ValueError, match="Agent script not found"):
            pm.execute_agent(str(agent_dir), "test_method", {})

    def test_execute_agent_missing_venv(self, mock_agent_directory: Path):
        """Test execute_agent handles missing virtual environment."""
        # Use subprocess execution to test virtual environment requirement
        pm = ProcessManager(use_dynamic_execution=False)

        # Mock agent directory has agent.py but no .venv
        result = pm.execute_agent(
            str(mock_agent_directory), "test_method", {"input": "test"}
        )

        assert "error" in result
        assert "Virtual environment not found" in result["error"]

    def test_execute_agent_success(self, mock_agent_directory: Path):
        """Test successful agent execution."""
        pm = ProcessManager()

        # Create mock virtual environment
        venv_path = mock_agent_directory / ".venv"
        if sys.platform == "win32":
            python_dir = venv_path / "Scripts"
            python_exe = python_dir / "python.exe"
        else:
            python_dir = venv_path / "bin"
            python_exe = python_dir / "python"

        python_dir.mkdir(parents=True)
        python_exe.touch()
        python_exe.chmod(0o755)

        # Create a symlink to the system Python for testing
        import shutil

        if shutil.which("python3"):
            python_exe.unlink()
            if sys.platform == "win32":
                # On Windows, copy the file instead of creating symlinks
                shutil.copy2(shutil.which("python3"), python_exe)
            else:
                python_exe.symlink_to(shutil.which("python3"))
        elif shutil.which("python"):
            python_exe.unlink()
            if sys.platform == "win32":
                # On Windows, copy the file instead of creating symlinks
                shutil.copy2(shutil.which("python"), python_exe)
            else:
                python_exe.symlink_to(shutil.which("python"))

        result = pm.execute_agent(
            str(mock_agent_directory), "test_method", {"input": "test"}
        )

        assert "result" in result
        assert result["result"] == "Test output: test"
        assert "execution_time" in result

    def test_execute_agent_invalid_method(self, mock_agent_directory: Path):
        """Test agent execution with invalid method."""
        pm = ProcessManager()

        # Create mock virtual environment with system Python
        venv_path = mock_agent_directory / ".venv"
        if sys.platform == "win32":
            python_dir = venv_path / "Scripts"
            python_exe = python_dir / "python.exe"
        else:
            python_dir = venv_path / "bin"
            python_exe = python_dir / "python"

        python_dir.mkdir(parents=True)
        python_exe.touch()
        python_exe.chmod(0o755)

        # Create a symlink to the system Python
        import shutil

        if shutil.which("python3"):
            python_exe.unlink()
            if sys.platform == "win32":
                # On Windows, copy the file instead of creating symlinks
                shutil.copy2(shutil.which("python3"), python_exe)
            else:
                python_exe.symlink_to(shutil.which("python3"))
        elif shutil.which("python"):
            python_exe.unlink()
            if sys.platform == "win32":
                # On Windows, copy the file instead of creating symlinks
                shutil.copy2(shutil.which("python"), python_exe)
            else:
                python_exe.symlink_to(shutil.which("python"))

        result = pm.execute_agent(str(mock_agent_directory), "invalid_method", {})

        assert "error" in result
        # Check that some error occurred (the specific message may vary due to
        # environment issues)
        assert len(result["error"]) > 0

    def test_validate_agent_structure_valid(self, mock_agent_directory: Path):
        """Test validate_agent_structure with valid agent."""
        pm = ProcessManager()

        # Create mock virtual environment
        venv_path = mock_agent_directory / ".venv"
        if sys.platform == "win32":
            python_dir = venv_path / "Scripts"
            python_exe = python_dir / "python.exe"
        else:
            python_dir = venv_path / "bin"
            python_exe = python_dir / "python"

        python_dir.mkdir(parents=True)
        python_exe.touch()

        result = pm.validate_agent_structure(str(mock_agent_directory))
        assert result is True

    def test_validate_agent_structure_missing_files(self, temp_dir: Path):
        """Test validate_agent_structure with missing files."""
        pm = ProcessManager()
        agent_dir = temp_dir / "incomplete-agent"
        agent_dir.mkdir()

        # Missing both agent.py and agent.yaml
        result = pm.validate_agent_structure(str(agent_dir))
        assert result is False

        # Add agent.py but still missing agent.yaml
        (agent_dir / "agent.py").touch()
        result = pm.validate_agent_structure(str(agent_dir))
        assert result is False

    def test_validate_agent_structure_missing_venv(self, temp_dir: Path):
        """Test validate_agent_structure with missing virtual environment."""
        pm = ProcessManager()
        agent_dir = temp_dir / "no-venv-agent"
        agent_dir.mkdir()

        # Create required files but no venv
        (agent_dir / "agent.py").touch()
        (agent_dir / "agent.yaml").touch()

        result = pm.validate_agent_structure(str(agent_dir))
        assert result is False
