"""Repository validation for Agent Hub Phase 2.

This module provides repository validation functionality to ensure
agent repositories meet AgentHub requirements before installation.
"""

import logging
import os
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of repository validation."""

    is_valid: bool
    local_path: str
    missing_files: list[str]
    validation_errors: list[str]
    warnings: list[str]
    validation_time: float
    repository_info: dict[str, str]


@dataclass
class FileValidationResult:
    """Result of individual file validation."""

    file_path: str
    exists: bool
    is_file: bool
    size: int
    is_readable: bool
    validation_errors: list[str]


class RepositoryValidator:
    """Validates agent repository structure and requirements."""

    # Base required files for AgentHub compatibility
    BASE_REQUIRED_FILES = [
        "agent.yaml",  # Interface definition and configuration
    ]

    # Optional but recommended files
    RECOMMENDED_FILES = [
        "requirements.txt",  # Dependencies (optional with installation commands)
        "README.md",  # Documentation
        "pyproject.toml",  # UV project configuration
        "LICENSE",  # License information
        ".gitignore",  # Git ignore file
    ]

    def __init__(self) -> None:
        """Initialize the repository validator."""
        self.logger = logger

    def _get_required_files(self, repo_path: Path) -> list[str]:
        """
        Get the required files based on agent configuration.

        Args:
            repo_path: Path to the repository

        Returns:
            List of required file names
        """
        required_files = self.BASE_REQUIRED_FILES.copy()

        # Check agent.yaml or agent.yml to determine script file requirement
        agent_yaml_path = repo_path / "agent.yaml"
        agent_yml_path = repo_path / "agent.yml"

        agent_config_path = None
        if agent_yaml_path.exists():
            agent_config_path = agent_yaml_path
        elif agent_yml_path.exists():
            agent_config_path = agent_yml_path

        if agent_config_path:
            try:
                import yaml

                with open(agent_config_path) as f:
                    agent_config = yaml.safe_load(f)

                if agent_config and "dana_version" in agent_config:
                    required_files.append("agent.na")
                    self.logger.info("Dana agent detected - requiring agent.na")
                else:
                    required_files.append("agent.py")
                    self.logger.info("Python agent detected - requiring agent.py")
            except Exception as e:
                self.logger.warning(
                    f"Failed to parse agent.yaml: {e}, defaulting to agent.py"
                )
                required_files.append("agent.py")
        else:
            # Default to agent.py if no agent.yaml
            required_files.append("agent.py")
            self.logger.info("No agent.yaml found - defaulting to agent.py")

        return required_files

    def validate_repository(self, local_path: str) -> ValidationResult:
        """
        Validate repository structure and requirements.

        Args:
            local_path: Path to the local repository

        Returns:
            ValidationResult with validation status and details
        """
        import time

        start_time = time.time()

        self.logger.info(f"Validating repository at: {local_path}")

        # Convert to Path object for easier handling
        repo_path = Path(local_path)

        # Check if path exists and is a directory
        if not repo_path.exists():
            return ValidationResult(
                is_valid=False,
                local_path=local_path,
                missing_files=self.BASE_REQUIRED_FILES,
                validation_errors=[f"Repository path does not exist: {local_path}"],
                warnings=[],
                validation_time=time.time() - start_time,
                repository_info={},
            )

        if not repo_path.is_dir():
            return ValidationResult(
                is_valid=False,
                local_path=local_path,
                missing_files=self.BASE_REQUIRED_FILES,
                validation_errors=[f"Path is not a directory: {local_path}"],
                warnings=[],
                validation_time=time.time() - start_time,
                repository_info={},
            )

        # Get dynamic required files based on agent configuration
        required_files = self._get_required_files(repo_path)

        # Validate required files
        missing_files = []
        validation_errors = []
        warnings = []

        # Special handling for agent config files (agent.yaml or agent.yml)
        agent_config_found = False
        for config_file in ["agent.yaml", "agent.yml"]:
            config_path = repo_path / config_file
            if config_path.exists():
                agent_config_found = True
                file_result = self._validate_file(config_path)
                if not file_result.is_file:
                    validation_errors.append(
                        f"Required file is not a file: {config_file}"
                    )
                elif not file_result.is_readable:
                    validation_errors.append(
                        f"Required file is not readable: {config_file}"
                    )
                break

        if not agent_config_found:
            missing_files.append("agent.yaml")
            validation_errors.append("Required file missing: agent.yaml (or agent.yml)")

        # Validate other required files
        for required_file in required_files:
            if required_file in ["agent.yaml", "agent.yml"]:
                continue  # Already handled above

            file_path = repo_path / required_file
            file_result = self._validate_file(file_path)

            if not file_result.exists:
                missing_files.append(required_file)
                validation_errors.append(f"Required file missing: {required_file}")
            elif not file_result.is_file:
                validation_errors.append(
                    f"Required file is not a file: {required_file}"
                )
            elif not file_result.is_readable:
                validation_errors.append(
                    f"Required file is not readable: {required_file}"
                )
            elif file_result.size == 0:
                warnings.append(f"Required file is empty: {required_file}")

        # Check recommended files
        for recommended_file in self.RECOMMENDED_FILES:
            file_path = repo_path / recommended_file
            if not file_path.exists():
                warnings.append(f"Recommended file missing: {recommended_file}")

        # Check for .git directory (should be a git repository)
        git_path = repo_path / ".git"
        if not git_path.exists() or not git_path.is_dir():
            warnings.append(
                "Repository is not a git repository (.git directory missing)"
            )

        # Determine if repository is valid
        is_valid = len(missing_files) == 0 and len(validation_errors) == 0

        # Collect repository information
        repository_info = self._collect_repository_info(repo_path)

        validation_time = time.time() - start_time

        self.logger.info(f"Repository validation completed in {validation_time:.2f}s")
        self.logger.info(
            f"Valid: {is_valid}, Missing files: {len(missing_files)}, "
            f"Errors: {len(validation_errors)}"
        )

        return ValidationResult(
            is_valid=is_valid,
            local_path=local_path,
            missing_files=missing_files,
            validation_errors=validation_errors,
            warnings=warnings,
            validation_time=validation_time,
            repository_info=repository_info,
        )

    def _validate_file(self, file_path: Path) -> FileValidationResult:
        """
        Validate an individual file.

        Args:
            file_path: Path to the file to validate

        Returns:
            FileValidationResult with file validation details
        """
        validation_errors = []

        # Check if file exists
        exists = file_path.exists()
        is_file = file_path.is_file() if exists else False
        size = file_path.stat().st_size if exists and is_file else 0
        is_readable = os.access(file_path, os.R_OK) if exists and is_file else False

        # Additional validation for specific file types
        if exists and is_file:
            if file_path.name == "agent.yaml":
                yaml_errors = self._validate_yaml_file(file_path)
                validation_errors.extend(yaml_errors)
            elif file_path.name == "requirements.txt":
                req_errors = self._validate_requirements_file(file_path)
                validation_errors.extend(req_errors)

        return FileValidationResult(
            file_path=str(file_path),
            exists=exists,
            is_file=is_file,
            size=size,
            is_readable=is_readable,
            validation_errors=validation_errors,
        )

    def _validate_yaml_file(self, yaml_path: Path) -> list[str]:
        """
        Validate agent.yaml file structure.

        Args:
            yaml_path: Path to agent.yaml file

        Returns:
            List of validation errors
        """
        errors = []

        try:
            import yaml

            with open(yaml_path, encoding="utf-8") as f:
                yaml_content = yaml.safe_load(f)

            if not yaml_content:
                errors.append("agent.yaml is empty or invalid YAML")
                return errors

            # Check required fields
            required_fields = ["name", "version", "description", "interface"]
            for field in required_fields:
                if field not in yaml_content:
                    errors.append(f"Missing required field in agent.yaml: {field}")

            # Check interface structure
            if "interface" in yaml_content:
                interface = yaml_content["interface"]
                if not isinstance(interface, dict):
                    errors.append("Interface field must be a dictionary")
                elif "methods" not in interface:
                    errors.append("Interface must contain 'methods' section")

            # Check setup configuration if present
            if "setup" in yaml_content:
                setup = yaml_content["setup"]
                if not isinstance(setup, dict):
                    errors.append("Setup field must be a dictionary")
                elif "commands" not in setup:
                    errors.append("Setup must contain 'commands' section")
                elif not isinstance(setup["commands"], list):
                    errors.append("Setup commands must be a list")

        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML format: {e}")
        except Exception as e:
            errors.append(f"Error reading agent.yaml: {e}")

        return errors

    def _validate_requirements_file(self, req_path: Path) -> list[str]:
        """
        Validate requirements.txt file.

        Args:
            req_path: Path to requirements.txt file

        Returns:
            List of validation errors
        """
        errors = []

        try:
            with open(req_path, encoding="utf-8") as f:
                content = f.read().strip()

            if not content:
                errors.append("requirements.txt is empty")
                return errors

            # Basic validation - check for common issues
            lines = content.split("\n")
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line and not line.startswith("#"):
                    # Check for basic package format
                    if "==" in line and line.count("==") > 1:
                        errors.append(
                            f"Line {i}: Multiple version specifiers in '{line}'"
                        )
                    elif ">=" in line and "<" in line:
                        errors.append(
                            f"Line {i}: Conflicting version constraints in '{line}'"
                        )

        except Exception as e:
            errors.append(f"Error reading requirements.txt: {e}")

        return errors

    def _collect_repository_info(self, repo_path: Path) -> dict[str, str]:
        """
        Collect basic repository information.

        Args:
            repo_path: Path to the repository

        Returns:
            Dictionary with repository information
        """
        info = {}

        try:
            # Get repository name from path
            info["name"] = repo_path.name

            # Check if it's a git repository
            git_path = repo_path / ".git"
            if git_path.exists() and git_path.is_dir():
                info["git_repository"] = "Yes"

                # Try to get git remote origin
                try:
                    import subprocess

                    result = subprocess.run(
                        ["git", "remote", "get-url", "origin"],
                        cwd=repo_path,
                        capture_output=True,
                        text=True,
                        timeout=10,
                    )
                    if result.returncode == 0:
                        info["git_remote"] = result.stdout.strip()
                except Exception:
                    info["git_remote"] = "Unknown"
            else:
                info["git_repository"] = "No"

            # Count Python files
            python_files = list(repo_path.rglob("*.py"))
            info["python_files"] = str(len(python_files))

            # Get total file count
            all_files = list(repo_path.rglob("*"))
            info["total_files"] = str(len(all_files))

        except Exception as e:
            info["error"] = f"Error collecting repository info: {e}"

        return info

    def get_validation_summary(self, result: ValidationResult) -> str:
        """
        Get a human-readable validation summary.

        Args:
            result: ValidationResult from validate_repository

        Returns:
            Formatted validation summary string
        """
        summary = f"Repository Validation Summary: {result.local_path}\n"
        summary += "=" * 50 + "\n"

        if result.is_valid:
            summary += "✅ Repository is VALID and ready for AgentHub installation\n"
        else:
            summary += "❌ Repository is INVALID and cannot be installed\n"

        summary += f"\nValidation completed in {result.validation_time:.2f}s\n"

        if result.missing_files:
            summary += f"\n❌ Missing required files ({len(result.missing_files)}):\n"
            for file in result.missing_files:
                summary += f"   - {file}\n"

        if result.validation_errors:
            summary += f"\n❌ Validation errors ({len(result.validation_errors)}):\n"
            for error in result.validation_errors:
                summary += f"   - {error}\n"

        if result.warnings:
            summary += f"\n⚠️  Warnings ({len(result.warnings)}):\n"
            for warning in result.warnings:
                summary += f"   - {warning}\n"

        if result.repository_info:
            summary += "\n📊 Repository Information:\n"
            for key, value in result.repository_info.items():
                summary += f"   {key}: {value}\n"

        return summary
