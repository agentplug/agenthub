"""Tests for EnvironmentManager class."""

import sys
from pathlib import Path

import pytest

from agenthub.runtime.environment_manager import EnvironmentManager


class TestEnvironmentManager:
    """Test cases for EnvironmentManager class."""

    def test_init(self):
        """Test EnvironmentManager initialization."""
        em = EnvironmentManager()
        assert em is not None

    def test_get_agent_venv_path(self, temp_dir: Path):
        """Test get_agent_venv_path returns correct path."""
        em = EnvironmentManager()
        agent_path = temp_dir / "test-agent"

        venv_path = em.get_agent_venv_path(str(agent_path))
        expected_path = agent_path / ".venv"

        assert venv_path == expected_path

    def test_get_python_executable_nonexistent_venv(self, temp_dir: Path):
        """Test get_python_executable raises error for nonexistent venv."""
        em = EnvironmentManager()
        agent_path = temp_dir / "nonexistent-agent"

        with pytest.raises(RuntimeError, match="Virtual environment not found"):
            em.get_python_executable(str(agent_path))

    def test_get_python_executable_existing_venv(self, temp_dir: Path):
        """Test get_python_executable returns correct path for existing venv."""
        em = EnvironmentManager()
        agent_path = temp_dir / "test-agent"
        venv_path = agent_path / ".venv"

        # Create mock virtual environment structure
        venv_path.mkdir(parents=True)

        if sys.platform == "win32":
            scripts_dir = venv_path / "Scripts"
            scripts_dir.mkdir()
            python_exe = scripts_dir / "python.exe"
            expected_path = str(python_exe)
        else:
            bin_dir = venv_path / "bin"
            bin_dir.mkdir()
            python_exe = bin_dir / "python"
            expected_path = str(python_exe)

        # Create mock Python executable
        python_exe.touch()

        result = em.get_python_executable(str(agent_path))
        assert result == expected_path

    def test_get_python_executable_missing_executable(self, temp_dir: Path):
        """Test get_python_executable raises error when executable is missing."""
        em = EnvironmentManager()
        agent_path = temp_dir / "test-agent"
        venv_path = agent_path / ".venv"

        # Create venv directory but no Python executable
        venv_path.mkdir(parents=True)
        if sys.platform == "win32":
            (venv_path / "Scripts").mkdir()
        else:
            (venv_path / "bin").mkdir()

        with pytest.raises(RuntimeError, match="Python executable not found"):
            em.get_python_executable(str(agent_path))
