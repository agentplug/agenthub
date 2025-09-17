"""Tests for RepositoryValidator class."""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch

from agenthub.github.repository_validator import (
    RepositoryValidator,
)


class TestRepositoryValidator:
    """Test cases for RepositoryValidator class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = RepositoryValidator()
        self.temp_dir = tempfile.mkdtemp()
        self.test_repo_path = Path(self.temp_dir) / "test-agent"
        self.test_repo_path.mkdir()

        # Create a basic git repository structure
        (self.test_repo_path / ".git").mkdir()
        (self.test_repo_path / ".git" / "config").touch()

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_initialization(self):
        """Test RepositoryValidator initialization."""
        assert self.validator is not None
        assert hasattr(self.validator, "REQUIRED_FILES")
        assert hasattr(self.validator, "RECOMMENDED_FILES")
        assert "agent.py" in self.validator.REQUIRED_FILES
        assert "agent.yaml" in self.validator.REQUIRED_FILES

    def test_validate_repository_path_not_exists(self):
        """Test validation of non-existent repository path."""
        non_existent_path = "/non/existent/path"
        result = self.validator.validate_repository(non_existent_path)

        assert not result.is_valid
        assert result.local_path == non_existent_path
        assert len(result.missing_files) == len(self.validator.REQUIRED_FILES)
        assert "Repository path does not exist" in result.validation_errors[0]

    def test_validate_repository_path_not_directory(self):
        """Test validation when path is not a directory."""
        # Create a file instead of directory
        file_path = Path(self.temp_dir) / "not_a_dir"
        file_path.touch()

        result = self.validator.validate_repository(str(file_path))

        assert not result.is_valid
        assert "Path is not a directory" in result.validation_errors[0]

    def test_validate_repository_missing_required_files(self):
        """Test validation when required files are missing."""
        result = self.validator.validate_repository(str(self.test_repo_path))

        assert not result.is_valid
        assert len(result.missing_files) == len(self.validator.REQUIRED_FILES)
        assert "agent.py" in result.missing_files
        assert "agent.yaml" in result.missing_files
        # requirements.txt and README.md are recommended, not required

    def test_validate_repository_with_all_required_files(self):
        """Test validation when all required files are present."""
        # Create all required files
        (self.test_repo_path / "agent.py").touch()
        (self.test_repo_path / "agent.yaml").touch()
        (self.test_repo_path / "requirements.txt").touch()
        (self.test_repo_path / "README.md").touch()

        result = self.validator.validate_repository(str(self.test_repo_path))

        assert result.is_valid
        assert len(result.missing_files) == 0
        assert len(result.validation_errors) == 0

    def test_validate_repository_with_recommended_files(self):
        """Test validation when recommended files are present."""
        # Create required files with content (not empty)
        (self.test_repo_path / "agent.py").write_text("print('hello')")
        (self.test_repo_path / "agent.yaml").write_text("name: test")
        (self.test_repo_path / "requirements.txt").write_text("requests>=2.0.0")
        (self.test_repo_path / "README.md").write_text("# Test Agent")

        # Create recommended files
        (self.test_repo_path / "pyproject.toml").touch()
        (self.test_repo_path / "LICENSE").touch()
        (self.test_repo_path / ".gitignore").touch()

        result = self.validator.validate_repository(str(self.test_repo_path))

        assert result.is_valid
        assert len(result.warnings) == 0  # No warnings for missing recommended files

    def test_validate_repository_without_git(self):
        """Test validation when .git directory is missing."""
        # Create required files
        (self.test_repo_path / "agent.py").touch()
        (self.test_repo_path / "agent.yaml").touch()
        (self.test_repo_path / "requirements.txt").touch()
        (self.test_repo_path / "README.md").touch()

        # Remove .git directory
        shutil.rmtree(self.test_repo_path / ".git")

        result = self.validator.validate_repository(str(self.test_repo_path))

        assert result.is_valid  # Should still be valid
        assert any("git repository" in warning.lower() for warning in result.warnings)

    def test_validate_repository_empty_files(self):
        """Test validation when required files are empty."""
        # Create empty required files
        (self.test_repo_path / "agent.py").touch()
        (self.test_repo_path / "agent.yaml").touch()
        (self.test_repo_path / "requirements.txt").touch()
        (self.test_repo_path / "README.md").touch()

        result = self.validator.validate_repository(str(self.test_repo_path))

        assert result.is_valid  # Should still be valid
        assert any("empty" in warning.lower() for warning in result.warnings)

    def test_validate_file(self):
        """Test individual file validation."""
        file_path = self.test_repo_path / "test.py"
        file_path.touch()
        file_path.write_text("print('hello')")

        result = self.validator._validate_file(file_path)

        assert result.exists
        assert result.is_file
        assert result.size > 0
        assert result.is_readable
        assert len(result.validation_errors) == 0

    def test_validate_file_not_exists(self):
        """Test validation of non-existent file."""
        file_path = self.test_repo_path / "non_existent.py"

        result = self.validator._validate_file(file_path)

        assert not result.exists
        assert not result.is_file
        assert result.size == 0
        assert not result.is_readable

    def test_validate_yaml_file_valid(self):
        """Test validation of valid YAML file."""
        yaml_content = """
name: "test-agent"
version: "1.0.0"
description: "A test agent"
interface:
  methods:
    test_method:
      description: "Test method"
      parameters: {}
"""
        yaml_path = self.test_repo_path / "agent.yaml"
        yaml_path.write_text(yaml_content)

        errors = self.validator._validate_yaml_file(yaml_path)

        assert len(errors) == 0

    def test_validate_yaml_file_invalid_format(self):
        """Test validation of invalid YAML file."""
        invalid_yaml = """
name: "test-agent"
version: "1.0.0"
description: "A test agent"
interface:
  methods:
    test_method:
      description: "Test method"
      parameters: {}
      - invalid: yaml
"""
        yaml_path = self.test_repo_path / "agent.yaml"
        yaml_path.write_text(invalid_yaml)

        errors = self.validator._validate_yaml_file(yaml_path)

        assert len(errors) > 0
        assert any("Invalid YAML format" in error for error in errors)

    def test_validate_yaml_file_missing_required_fields(self):
        """Test validation of YAML file with missing required fields."""
        yaml_content = """
name: "test-agent"
# Missing version, description, interface
"""
        yaml_path = self.test_repo_path / "agent.yaml"
        yaml_path.write_text(yaml_content)

        errors = self.validator._validate_yaml_file(yaml_path)

        assert len(errors) > 0
        assert any("Missing required field" in error for error in errors)

    def test_validate_yaml_file_invalid_interface_structure(self):
        """Test validation of YAML file with invalid interface structure."""
        yaml_content = """
name: "test-agent"
version: "1.0.0"
description: "A test agent"
interface: "not a dict"
"""
        yaml_path = self.test_repo_path / "agent.yaml"
        yaml_path.write_text(yaml_content)

        errors = self.validator._validate_yaml_file(yaml_path)

        assert len(errors) > 0
        assert any("Interface field must be a dictionary" in error for error in errors)

    def test_validate_requirements_file_valid(self):
        """Test validation of valid requirements.txt file."""
        req_content = """
# Core dependencies
requests>=2.28.0
pyyaml>=6.0.0

# Optional dependencies
pytest>=7.0.0
"""
        req_path = self.test_repo_path / "requirements.txt"
        req_path.write_text(req_content)

        errors = self.validator._validate_requirements_file(req_path)

        assert len(errors) == 0

    def test_validate_requirements_file_empty(self):
        """Test validation of empty requirements.txt file."""
        req_path = self.test_repo_path / "requirements.txt"
        req_path.touch()

        errors = self.validator._validate_requirements_file(req_path)

        assert len(errors) > 0
        assert any("empty" in error for error in errors)

    def test_validate_requirements_file_invalid_format(self):
        """Test validation of requirements.txt with invalid format."""
        req_content = """
requests==2.28.0==invalid
pytest>=7.0.0<8.0.0
"""
        req_path = self.test_repo_path / "requirements.txt"
        req_path.write_text(req_content)

        errors = self.validator._validate_requirements_file(req_path)

        assert len(errors) > 0
        assert any("Multiple version specifiers" in error for error in errors)
        assert any("Conflicting version constraints" in error for error in errors)

    def test_collect_repository_info(self):
        """Test collection of repository information."""
        # Create test directory first
        (self.test_repo_path / "test").mkdir()

        # Create some Python files
        (self.test_repo_path / "main.py").touch()
        (self.test_repo_path / "utils.py").touch()
        (self.test_repo_path / "test" / "test_main.py").touch()

        info = self.validator._collect_repository_info(self.test_repo_path)

        assert "name" in info
        assert info["name"] == "test-agent"
        assert "git_repository" in info
        assert info["git_repository"] == "Yes"
        assert "python_files" in info
        assert int(info["python_files"]) >= 3
        assert "total_files" in info

    def test_collect_repository_info_without_git(self):
        """Test collection of repository information without git."""
        # Remove .git directory
        shutil.rmtree(self.test_repo_path / ".git")

        info = self.validator._collect_repository_info(self.test_repo_path)

        assert info["git_repository"] == "No"
        assert "git_remote" not in info

    @patch("subprocess.run")
    def test_collect_repository_info_git_remote_success(self, mock_run):
        """Test successful git remote origin retrieval."""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "https://github.com/user/test-agent.git"

        info = self.validator._collect_repository_info(self.test_repo_path)

        assert info["git_remote"] == "https://github.com/user/test-agent.git"
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_collect_repository_info_git_remote_failure(self, mock_run):
        """Test failed git remote origin retrieval."""
        # Mock the subprocess.run to raise an exception
        mock_run.side_effect = Exception("Git command failed")

        info = self.validator._collect_repository_info(self.test_repo_path)

        # Should still have git_repository = "Yes" but git_remote = "Unknown"
        assert info["git_repository"] == "Yes"
        assert info["git_remote"] == "Unknown"

    def test_get_validation_summary_valid_repository(self):
        """Test validation summary for valid repository."""
        # Create all required files
        (self.test_repo_path / "agent.py").touch()
        (self.test_repo_path / "agent.yaml").touch()
        (self.test_repo_path / "requirements.txt").touch()
        (self.test_repo_path / "README.md").touch()

        result = self.validator.validate_repository(str(self.test_repo_path))
        summary = self.validator.get_validation_summary(result)

        assert "✅ Repository is VALID" in summary
        assert "ready for AgentHub installation" in summary
        assert "❌ Missing required files" not in summary
        assert "❌ Validation errors" not in summary

    def test_get_validation_summary_invalid_repository(self):
        """Test validation summary for invalid repository."""
        result = self.validator.validate_repository(str(self.test_repo_path))
        summary = self.validator.get_validation_summary(result)

        assert "❌ Repository is INVALID" in summary
        assert "cannot be installed" in summary
        assert "❌ Missing required files" in summary
        assert "agent.py" in summary
        assert "agent.yaml" in summary

    def test_get_validation_summary_with_warnings(self):
        """Test validation summary with warnings."""
        # Create required files but make them empty
        (self.test_repo_path / "agent.py").touch()
        (self.test_repo_path / "agent.yaml").touch()
        (self.test_repo_path / "requirements.txt").touch()
        (self.test_repo_path / "README.md").touch()

        result = self.validator.validate_repository(str(self.test_repo_path))
        summary = self.validator.get_validation_summary(result)

        assert "✅ Repository is VALID" in summary
        assert "⚠️  Warnings" in summary
        assert "empty" in summary

    def test_validation_performance(self):
        """Test that validation completes in reasonable time."""
        # Create all required files
        (self.test_repo_path / "agent.py").touch()
        (self.test_repo_path / "agent.yaml").touch()
        (self.test_repo_path / "requirements.txt").touch()
        (self.test_repo_path / "README.md").touch()

        result = self.validator.validate_repository(str(self.test_repo_path))

        assert result.validation_time < 1.0  # Should complete in under 1 second
        assert result.validation_time > 0.0  # Should take some time

    def test_validation_with_large_repository(self):
        """Test validation with a repository containing many files."""
        # Create many files to test performance
        for i in range(100):
            (self.test_repo_path / f"file_{i}.txt").touch()

        # Create required files
        (self.test_repo_path / "agent.py").touch()
        (self.test_repo_path / "agent.yaml").touch()
        (self.test_repo_path / "requirements.txt").touch()
        (self.test_repo_path / "README.md").touch()

        result = self.validator.validate_repository(str(self.test_repo_path))

        assert result.is_valid
        assert result.validation_time < 2.0  # Should complete in under 2 seconds
        assert (
            int(result.repository_info["total_files"]) >= 104
        )  # 100 + 4 required + .git


class TestRepositoryValidatorIntegration:
    """Integration tests for RepositoryValidator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = RepositoryValidator()
        self.temp_dir = tempfile.mkdtemp()

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_validation_workflow(self):
        """Test complete validation workflow."""
        # Create a realistic agent repository structure
        repo_path = Path(self.temp_dir) / "realistic-agent"
        repo_path.mkdir()

        # Create .git directory
        (repo_path / ".git").mkdir()
        (repo_path / ".git" / "config").touch()

        # Create required files with realistic content
        (repo_path / "agent.py").write_text(
            """
from agenthub import Agent

class TestAgent(Agent):
    def run(self, input_data):
        return {"result": "success"}
"""
        )

        (repo_path / "agent.yaml").write_text(
            """
name: "test-agent"
version: "1.0.0"
description: "A test agent for validation"
interface:
  methods:
    run:
      description: "Run the agent"
      parameters:
        input_data:
          type: "string"
          description: "Input data"
          required: true
"""
        )

        (repo_path / "requirements.txt").write_text(
            """
agenthub>=0.1.0
pyyaml>=6.0.0
"""
        )

        (repo_path / "README.md").write_text(
            """
# Test Agent

A test agent for validation testing.
"""
        )

        # Create recommended files
        (repo_path / "pyproject.toml").write_text(
            """
[project]
name = "test-agent"
version = "1.0.0"
"""
        )

        (repo_path / "LICENSE").write_text("MIT License")
        (repo_path / ".gitignore").write_text("*.pyc\n__pycache__/")

        # Validate the repository
        result = self.validator.validate_repository(str(repo_path))

        # Assertions
        assert result.is_valid
        assert len(result.missing_files) == 0
        assert len(result.validation_errors) == 0
        assert len(result.warnings) == 0

        # Check repository info
        assert result.repository_info["name"] == "realistic-agent"
        assert result.repository_info["git_repository"] == "Yes"
        assert int(result.repository_info["python_files"]) >= 1
        assert int(result.repository_info["total_files"]) >= 8

        # Test validation summary
        summary = self.validator.get_validation_summary(result)
        assert "✅ Repository is VALID" in summary
        assert "ready for AgentHub installation" in summary
