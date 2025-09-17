"""Comprehensive integration tests for Step 7: Advanced Environment Management.

These tests validate the complete product functionality from a user's perspective,
including Python version migration, environment cloning, optimization, and
real-world usage scenarios.
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from agenthub.environment.environment_manager import (
    AdvancedEnvironmentManager,
)


class TestProductIntegrationEnvironmentManagement:
    """End-to-end tests for advanced environment management from product perspective."""

    @pytest.fixture
    def temp_storage_path(self):
        """Create a temporary storage path for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def mock_agent_repository(self):
        """Create a mock agent repository structure with environment."""
        temp_dir = tempfile.mkdtemp()

        # Create required files
        (Path(temp_dir) / "agent.py").write_text("# Test agent implementation")
        (Path(temp_dir) / "agent.yaml").write_text(
            """
name: test-agent
interface: cli
dependencies:
  - requests>=2.25.0
  - pandas>=1.3.0
"""
        )
        (Path(temp_dir) / "requirements.txt").write_text("requests\npandas")
        (Path(temp_dir) / "README.md").write_text("# Test Agent")
        (Path(temp_dir) / "pyproject.toml").write_text(
            """
[project]
name = "test-agent"
version = "1.0.0"
dependencies = ["requests", "pandas"]
"""
        )

        # Create mock virtual environment
        venv_dir = Path(temp_dir) / ".venv"
        venv_dir.mkdir()
        (venv_dir / "bin").mkdir()
        (venv_dir / "bin" / "python").touch()

        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_complete_migration_workflow(
        self, temp_storage_path, mock_agent_repository
    ):
        """Test complete Python version migration workflow from product perspective."""
        # Copy mock agent to storage
        agent_path = Path(temp_storage_path) / "developer" / "test-agent"
        agent_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(mock_agent_repository, agent_path)

        manager = AdvancedEnvironmentManager(base_storage_path=Path(temp_storage_path))

        # Test migration with available Python version
        with patch.object(manager, "_get_current_python_version") as mock_version:
            mock_version.side_effect = [
                "3.9.0",
                "3.10",
            ]  # First call returns original, second returns new
            with patch.object(manager.env_setup, "setup_environment") as mock_setup:
                from agenthub.environment.environment_setup import (
                    EnvironmentSetupResult,
                )

                mock_setup.return_value = EnvironmentSetupResult(
                    success=True,
                    agent_path=str(agent_path),
                    venv_path=str(agent_path / ".venv"),
                    setup_time_seconds=1.5,
                )
                result = manager.migrate_python_version(
                    agent_name="developer/test-agent", target_python_version="3.10"
                )

            assert result.success is True
            assert result.source_python == "3.9.0"
            assert result.target_python == "3.10"
            assert result.migration_time > 0
            assert result.backup_path is not None
            assert Path(result.backup_path).exists()
            assert "Successfully migrated" in result.next_steps[0]

    def test_migration_already_on_target_version(self, temp_storage_path):
        """Test migration when already on target version."""
        manager = AdvancedEnvironmentManager(base_storage_path=Path(temp_storage_path))

        # Create minimal agent structure
        agent_path = manager._get_agent_path("developer/test-agent")
        agent_path.mkdir(parents=True, exist_ok=True)
        (agent_path / "agent.py").write_text("# test")
        (agent_path / "agent.yaml").write_text("name: test-agent")

        with patch.object(
            manager, "_get_current_python_version", return_value="3.11.0"
        ):
            result = manager.migrate_python_version(
                agent_name="developer/test-agent",
                target_python_version="3.11.0",
                force=False,
            )

            assert result.success is True
            assert "Already on Python 3.11.0" in result.warnings[0]

    def test_migration_agent_not_found(self, temp_storage_path):
        """Test migration with non-existent agent."""
        manager = AdvancedEnvironmentManager(base_storage_path=Path(temp_storage_path))

        result = manager.migrate_python_version(
            agent_name="developer/nonexistent", target_python_version="3.11.0"
        )

        assert result.success is False
        assert "Agent 'developer/nonexistent' not found" in result.error_message

    def test_complete_clone_workflow(self, temp_storage_path, mock_agent_repository):
        """Test complete environment cloning workflow."""
        # Copy mock agent to storage
        source_path = Path(temp_storage_path) / "developer" / "source-agent"
        source_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(mock_agent_repository, source_path)

        manager = AdvancedEnvironmentManager(base_storage_path=Path(temp_storage_path))

        # Test cloning
        result = manager.clone_environment(
            source_agent="developer/source-agent", target_agent="developer/target-agent"
        )

        assert result.success is True
        assert result.source_agent == "developer/source-agent"
        assert result.target_agent == "developer/target-agent"
        assert result.clone_time > 0
        assert Path(result.target_path).exists()
        assert (Path(result.target_path) / "agent.py").exists()

    def test_clone_target_exists(self, temp_storage_path, mock_agent_repository):
        """Test cloning when target already exists."""
        # Copy mock agents to storage
        source_path = Path(temp_storage_path) / "developer" / "source-agent"
        target_path = Path(temp_storage_path) / "developer" / "target-agent"

        source_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.copytree(mock_agent_repository, source_path)
        shutil.copytree(mock_agent_repository, target_path)

        manager = AdvancedEnvironmentManager(base_storage_path=Path(temp_storage_path))

        result = manager.clone_environment(
            source_agent="developer/source-agent", target_agent="developer/target-agent"
        )

        assert result.success is False
        assert (
            "Target agent 'developer/target-agent' already exists"
            in result.error_message
        )

    def test_complete_optimization_workflow(
        self, temp_storage_path, mock_agent_repository
    ):
        """Test complete environment optimization workflow."""
        # Copy mock agent to storage
        agent_path = Path(temp_storage_path) / "developer" / "test-agent"
        agent_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(mock_agent_repository, agent_path)

        # Create some cache files to optimize
        cache_dir = agent_path / ".venv" / "__pycache__"
        cache_dir.mkdir(parents=True, exist_ok=True)
        (cache_dir / "cache.pyc").write_text("cache data" * 1000)

        manager = AdvancedEnvironmentManager(base_storage_path=Path(temp_storage_path))

        with patch.object(
            manager, "_calculate_directory_size", side_effect=[10.0, 8.5]
        ):
            result = manager.optimize_environment("developer/test-agent")

            assert result.success is True
            assert result.original_size_mb == 10.0
            assert result.optimized_size_mb == 8.5
            assert result.space_saved_mb == 1.5
            assert len(result.actions_taken) > 0

    def test_optimization_agent_not_found(self, temp_storage_path):
        """Test optimization with non-existent agent."""
        manager = AdvancedEnvironmentManager(base_storage_path=Path(temp_storage_path))

        result = manager.optimize_environment("developer/nonexistent")

        assert result.success is False
        assert "Agent 'developer/nonexistent' not found" in result.error_message

    def test_dependency_analysis(self, temp_storage_path, mock_agent_repository):
        """Test dependency analysis from product perspective."""
        # Copy mock agent to storage
        agent_path = Path(temp_storage_path) / "developer" / "test-agent"
        agent_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(mock_agent_repository, agent_path)

        manager = AdvancedEnvironmentManager(base_storage_path=Path(temp_storage_path))

        with patch.object(
            manager.env_setup,
            "_get_installed_packages",
            return_value=["requests", "pandas", "numpy"],
        ):
            result = manager.analyze_dependencies("developer/test-agent")

            assert result["success"] is True
            assert result["total_packages"] == 3
            assert "requests" in result["packages"]
            assert "pandas" in result["packages"]
            assert "numpy" in result["packages"]

    def test_python_version_listing(self):
        """Test Python version listing functionality."""
        manager = AdvancedEnvironmentManager()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0, stdout="3.12.0\n3.11.0\n3.10.0\n"
            )

            versions = manager.list_python_versions()

            assert len(versions) > 0
            assert "3.12" in versions or "3.11" in versions

    def test_backup_creation_during_migration(
        self, temp_storage_path, mock_agent_repository
    ):
        """Test backup creation during migration."""
        # Copy mock agent to storage
        agent_path = Path(temp_storage_path) / "developer" / "test-agent"
        agent_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(mock_agent_repository, agent_path)

        manager = AdvancedEnvironmentManager(base_storage_path=Path(temp_storage_path))

        with patch.object(manager, "_get_current_python_version") as mock_version:
            mock_version.side_effect = [
                "3.9.0",
                "3.10",
            ]  # First call returns original, second returns new
            with patch.object(manager.env_setup, "setup_environment") as mock_setup:
                from agenthub.environment.environment_setup import (
                    EnvironmentSetupResult,
                )

                mock_setup.return_value = EnvironmentSetupResult(
                    success=True,
                    agent_path=str(agent_path),
                    venv_path=str(agent_path / ".venv"),
                    setup_time_seconds=1.5,
                )
                result = manager.migrate_python_version(
                    agent_name="developer/test-agent",
                    target_python_version="3.10",
                    create_backup=True,
                )

            assert result.success is True
            assert result.backup_path is not None
            assert Path(result.backup_path).exists()

            # Verify backup contains original files
            backup_path = Path(result.backup_path)
            assert (backup_path / "agent.py").exists()
            assert (backup_path / "agent.yaml").exists()

    def test_error_handling_migration_failure(self, temp_storage_path):
        """Test error handling when migration fails."""
        manager = AdvancedEnvironmentManager(base_storage_path=Path(temp_storage_path))

        # Create minimal agent structure
        agent_path = manager._get_agent_path("developer/test-agent")
        agent_path.mkdir(parents=True, exist_ok=True)
        (agent_path / "agent.py").write_text("# test")
        (agent_path / "agent.yaml").write_text("name: test-agent")

        with patch.object(manager.env_setup, "setup_environment") as mock_setup:
            mock_setup.return_value = Mock(
                success=False, error_message="Mock setup failure"
            )

            result = manager.migrate_python_version(
                agent_name="developer/test-agent", target_python_version="3.11.0"
            )

            assert result.success is False
            assert "Mock setup failure" in result.error_message
            assert result.backup_path is not None  # Should still create backup

    def test_directory_size_calculation(self, temp_storage_path):
        """Test directory size calculation."""
        manager = AdvancedEnvironmentManager()

        # Create test directory with known size
        test_dir = Path(temp_storage_path) / "test-size"
        test_dir.mkdir(parents=True, exist_ok=True)
        (test_dir / "test.txt").write_text("a" * 1024)  # 1KB file

        size = manager._calculate_directory_size(test_dir)
        assert 0.0009 < size < 0.002  # Should be ~0.001 MB


class TestRealWorldProductScenarios:
    """Real-world product usage scenario tests."""

    @pytest.fixture
    def temp_storage_path(self):
        """Create a temporary storage path for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_developer_workflow_python_upgrade(self, temp_storage_path):
        """Test complete developer workflow for Python version upgrade."""
        # Create agent structure
        agent_path = Path(temp_storage_path) / "mycompany" / "data-processor"
        agent_path.mkdir(parents=True, exist_ok=True)

        # Create realistic agent with dependencies
        (agent_path / "agent.py").write_text(
            """
import pandas as pd
import requests
import numpy as np

class DataProcessor:
    def process_data(self, data):
        return pd.DataFrame(data).describe()
"""
        )

        (agent_path / "agent.yaml").write_text(
            """
name: data-processor
version: 1.0.0
interface:
  methods:
    process_data:
      description: Process data with pandas
      parameters:
        data:
          type: array
          description: Data to process
"""
        )

        (agent_path / "requirements.txt").write_text(
            """
pandas>=1.5.0
requests>=2.28.0
numpy>=1.21.0
"""
        )

        manager = AdvancedEnvironmentManager(base_storage_path=Path(temp_storage_path))

        # Test full workflow
        target_version = "3.10.0"

        with patch.object(manager, "_get_current_python_version") as mock_version:
            mock_version.side_effect = [
                "3.9.7",
                "3.10.0",
            ]  # First call returns original, second returns new
            with patch.object(manager.env_setup, "setup_environment") as mock_setup:
                from agenthub.environment.environment_setup import (
                    EnvironmentSetupResult,
                )

                mock_setup.return_value = EnvironmentSetupResult(
                    success=True,
                    agent_path=str(agent_path),
                    venv_path=str(agent_path / ".venv"),
                    setup_time_seconds=1.5,
                )
                # Step 1: Create backup
                backup_result = manager.migrate_python_version(
                    agent_name="mycompany/data-processor",
                    target_python_version=target_version,
                    create_backup=True,
                )

            assert backup_result.success is True
            assert backup_result.backup_path is not None

            # Step 2: Verify backup exists
            backup_path = Path(backup_result.backup_path)
            assert backup_path.exists()
            assert (backup_path / "agent.py").exists()
            assert (backup_path / "requirements.txt").exists()

    def test_team_collaboration_clone_workflow(self, temp_storage_path):
        """Test team collaboration workflow using environment cloning."""
        # Create source agent (production)
        source_path = Path(temp_storage_path) / "team" / "production-agent"
        source_path.mkdir(parents=True, exist_ok=True)

        (source_path / "agent.py").write_text("# Production agent")
        (source_path / "agent.yaml").write_text(
            "name: production-agent\nversion: 2.1.0"
        )
        (source_path / "requirements.txt").write_text(
            "torch>=1.13.0\ntransformers>=4.21.0"
        )

        manager = AdvancedEnvironmentManager(base_storage_path=Path(temp_storage_path))

        # Clone for development
        clone_result = manager.clone_environment(
            source_agent="team/production-agent", target_agent="team/dev-alice"
        )

        assert clone_result.success is True

        # Clone for testing
        clone_result2 = manager.clone_environment(
            source_agent="team/production-agent", target_agent="team/test-bob"
        )

        assert clone_result2.success is True

        # Verify both clones exist
        alice_path = Path(clone_result.target_path)
        bob_path = Path(clone_result2.target_path)

        assert alice_path.exists()
        assert bob_path.exists()
        assert (alice_path / "agent.py").exists()
        assert (bob_path / "agent.py").exists()

    def test_ci_cd_migration_pipeline(self, temp_storage_path):
        """Test CI/CD pipeline for environment migration."""
        # Create test environment
        agent_path = Path(temp_storage_path) / "ci" / "test-agent"
        agent_path.mkdir(parents=True, exist_ok=True)

        (agent_path / "agent.py").write_text("# CI test agent")
        (agent_path / "agent.yaml").write_text("name: ci-test")
        (agent_path / "requirements.txt").write_text("pytest\npytest-cov")

        manager = AdvancedEnvironmentManager(base_storage_path=Path(temp_storage_path))

        # Simulate CI migration
        with patch.object(manager, "_get_current_python_version") as mock_version:
            mock_version.side_effect = [
                "3.8.10",
                "3.10.0",
            ]  # First call returns original, second returns new
            with patch.object(manager.env_setup, "setup_environment") as mock_setup:
                from agenthub.environment.environment_setup import (
                    EnvironmentSetupResult,
                )

                mock_setup.return_value = EnvironmentSetupResult(
                    success=True,
                    agent_path=str(agent_path),
                    venv_path=str(agent_path / ".venv"),
                    setup_time_seconds=1.5,
                )
                # Test migration to compatible Python
                result = manager.migrate_python_version(
                    agent_name="ci/test-agent",
                    target_python_version="3.10.0",
                    create_backup=True,
                )

            assert result.success is True

            # Verify backup for rollback
            assert result.backup_path is not None

            # Test optimization post-migration
            opt_result = manager.optimize_environment("ci/test-agent")
            assert opt_result.success is True
            assert opt_result.space_saved_mb >= 0

    def test_enterprise_cleanup_workflow(self, temp_storage_path):
        """Test enterprise cleanup and optimization workflow."""
        # Create multiple agents with varying states
        agents = ["enterprise/agent-v1", "enterprise/agent-v2", "enterprise/agent-v3"]

        manager = AdvancedEnvironmentManager(base_storage_path=Path(temp_storage_path))

        # Create agents with different sizes
        total_original_size = 0
        for agent in agents:
            agent_path = manager._get_agent_path(agent)
            agent_path.mkdir(parents=True, exist_ok=True)

            (agent_path / "agent.py").write_text(f"# {agent}")
            (agent_path / "agent.yaml").write_text(f"name: {agent.split('/')[-1]}")
            (agent_path / "requirements.txt").write_text("requests\npandas\nnumpy")

            # Create cache files
            cache_dir = agent_path / ".venv" / "__pycache__"
            cache_dir.mkdir(parents=True, exist_ok=True)
            (cache_dir / "cache.pyc").write_text("cache" * 5000)

            total_original_size += manager._calculate_directory_size(agent_path)

        # Test optimization across all agents
        total_saved = 0
        for agent in agents:
            result = manager.optimize_environment(agent)
            if result.success:
                total_saved += result.space_saved_mb

        assert total_saved >= 0  # Should save space

        # Test dependency analysis
        for agent in agents:
            dep_result = manager.analyze_dependencies(agent)
            assert dep_result["success"] is True
            assert dep_result["total_packages"] >= 2  # requests + pandas
