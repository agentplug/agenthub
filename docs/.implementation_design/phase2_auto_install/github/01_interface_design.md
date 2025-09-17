# GitHub Module - Interface Design

**Document Type**: Detailed Interface Design
**Module**: GitHub Integration
**Phase**: 2 - Auto-Install
**Author**: William
**Date Created**: 2025-06-28
**Last Updated**: 2025-06-28
**Status**: Active

## 🎯 **Public Interfaces**

### **Repository Cloner Interface**

```python
class RepositoryCloner:
    """Clone agent repositories from GitHub to local storage."""

    def clone_agent(self, agent_name: str, target_path: Optional[str] = None) -> str:
        """
        Clone an agent repository from GitHub.

        Args:
            agent_name: Repository name in format "developer/agent-name"
            target_path: Optional local path for cloning (defaults to ~/.agenthub/agents/)

        Returns:
            Local path where repository was cloned

        Raises:
            RepositoryNotFoundError: If repository doesn't exist or is inaccessible
            CloneFailedError: If git clone operation fails
            InvalidAgentNameError: If agent_name format is invalid
        """
        pass

    def clone_to_specific_path(self, agent_name: str, target_path: str) -> str:
        """Clone repository to a specific local path."""
        pass

    def get_clone_status(self, agent_name: str) -> CloneStatus:
        """Get the current status of a clone operation."""
        pass
```

### **Repository Validator Interface**

```python
class RepositoryValidator:
    """Validate that cloned repositories meet required standards."""

    def validate_repository(self, local_path: str) -> ValidationResult:
        """
        Validate a cloned repository meets all requirements.

        Args:
            local_path: Path to the local repository

        Returns:
            ValidationResult with detailed validation information

        Raises:
            ValidationError: If validation fails with details
        """
        pass

    def validate_required_files(self, local_path: str) -> List[FileValidationResult]:
        """Check that all required files are present and valid."""
        pass

    def validate_agent_yaml(self, yaml_path: str) -> YamlValidationResult:
        """Validate agent.yaml format and content."""
        pass

    def validate_agent_py(self, py_path: str, yaml_data: dict) -> PyValidationResult:
        """Validate agent.py implements methods defined in agent.yaml."""
        pass

    def validate_requirements_txt(self, requirements_path: str) -> RequirementsValidationResult:
        """Validate requirements.txt format and content."""
        pass
```

### **GitHub Client Interface**

```python
class GitHubClient:
    """Interact with GitHub API for enhanced validation (optional)."""

    def check_repository_exists(self, agent_name: str) -> bool:
        """Check if a repository exists and is accessible."""
        pass

    def get_repository_metadata(self, agent_name: str) -> RepositoryMetadata:
        """Get basic repository metadata (stars, last updated, etc.)."""
        pass

    def get_rate_limit_status(self) -> RateLimitStatus:
        """Get current GitHub API rate limit status."""
        pass

    def is_authenticated(self) -> bool:
        """Check if GitHub API authentication is available."""
        pass
```

## 🔧 **Data Models**

### **CloneStatus Enum**

```python
from enum import Enum

class CloneStatus(Enum):
    """Status of a repository clone operation."""
    NOT_STARTED = "not_started"
    CLONING = "cloning"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
```

### **ValidationResult Class**

```python
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class ValidationResult:
    """Result of repository validation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    file_validation: Dict[str, FileValidationResult]
    yaml_validation: YamlValidationResult
    py_validation: PyValidationResult
    requirements_validation: RequirementsValidationResult
    overall_score: float  # 0.0 to 1.0
    validation_time: float  # seconds
```

### **FileValidationResult Class**

```python
@dataclass
class FileValidationResult:
    """Result of file validation."""
    file_path: str
    exists: bool
    is_readable: bool
    size_bytes: int
    last_modified: datetime
    validation_errors: List[str]
    validation_warnings: List[str]
```

### **YamlValidationResult Class**

```python
@dataclass
class YamlValidationResult:
    """Result of agent.yaml validation."""
    is_valid: bool
    parsed_data: Dict[str, Any]
    required_fields: List[str]
    missing_fields: List[str]
    invalid_fields: List[str]
    validation_errors: List[str]
```

### **PyValidationResult Class**

```python
@dataclass
class PyValidationResult:
    """Result of agent.py validation."""
    is_valid: bool
    implemented_methods: List[str]
    missing_methods: List[str]
    method_signatures: Dict[str, str]
    validation_errors: List[str]
```

### **RequirementsValidationResult Class**

```python
@dataclass
class RequirementsValidationResult:
    """Result of requirements.txt validation."""
    is_valid: bool
    packages: List[str]
    parsed_requirements: List[Requirement]
    validation_errors: List[str]
    dependency_count: int
```

## 🚨 **Exception Classes**

### **RepositoryNotFoundError**

```python
class RepositoryNotFoundError(Exception):
    """Raised when a GitHub repository cannot be found or accessed."""

    def __init__(self, agent_name: str, reason: str = None):
        self.agent_name = agent_name
        self.reason = reason
        super().__init__(f"Repository '{agent_name}' not found or inaccessible: {reason}")
```

### **CloneFailedError**

```python
class CloneFailedError(Exception):
    """Raised when git clone operation fails."""

    def __init__(self, agent_name: str, git_output: str = None, exit_code: int = None):
        self.agent_name = agent_name
        self.git_output = git_output
        self.exit_code = exit_code
        super().__init__(f"Failed to clone repository '{agent_name}': {git_output}")
```

### **InvalidAgentNameError**

```python
class InvalidAgentNameError(Exception):
    """Raised when agent name format is invalid."""

    def __init__(self, agent_name: str, expected_format: str = "developer/agent-name"):
        self.agent_name = agent_name
        self.expected_format = expected_format
        super().__init__(f"Invalid agent name '{agent_name}'. Expected format: {expected_format}")
```

### **ValidationError**

```python
class ValidationError(Exception):
    """Raised when repository validation fails."""

    def __init__(self, local_path: str, validation_result: ValidationResult):
        self.local_path = local_path
        self.validation_result = validation_result
        super().__init__(f"Repository validation failed for '{local_path}': {validation_result.errors}")
```

## 🔗 **Module Integration Points**

### **With Core Module**

```python
# Core module calls GitHub module
from agenthub.github.repository_cloner import RepositoryCloner
from agenthub.github.repository_validator import RepositoryValidator

class AutoInstaller:
    def __init__(self):
        self.cloner = RepositoryCloner()
        self.validator = RepositoryValidator()

    def install_agent(self, agent_name: str) -> InstallationResult:
        # Clone repository
        local_path = self.cloner.clone_agent(agent_name)

        # Validate repository
        validation_result = self.validator.validate_repository(local_path)

        if not validation_result.is_valid:
            raise ValidationError(local_path, validation_result)

        # Continue with installation...
```

### **With Storage Module**

```python
# GitHub module provides repository information to storage
from agenthub.storage.metadata_manager import MetadataManager

class RepositoryValidator:
    def __init__(self):
        self.metadata_manager = MetadataManager()

    def validate_repository(self, local_path: str) -> ValidationResult:
        # Validate repository...

        # Store validation metadata
        self.metadata_manager.store_validation_result(local_path, validation_result)

        return validation_result
```

### **With Environment Module**

```python
# Environment module uses GitHub module for repository information
from agenthub.github.github_client import GitHubClient

class EnvironmentSetup:
    def __init__(self):
        self.github_client = GitHubClient()

    def setup_environment(self, agent_name: str, local_path: str):
        # Get repository metadata for environment setup
        metadata = self.github_client.get_repository_metadata(agent_name)

        # Use metadata for environment configuration...
```

## 📊 **Performance Requirements**

### **Response Time Targets**
- **Repository Cloning**: < 30 seconds for typical agents (< 10MB)
- **Repository Validation**: < 10 seconds for typical agents
- **GitHub API Calls**: < 5 seconds for metadata retrieval
- **Error Handling**: < 1 second for error detection and reporting

### **Resource Usage Targets**
- **Memory**: < 100MB during cloning and validation
- **Disk I/O**: Efficient file operations with minimal overhead
- **Network**: Efficient use of bandwidth with retry logic

### **Scalability Targets**
- **Concurrent Operations**: Support 3+ simultaneous clone operations
- **Repository Size**: Handle repositories up to 100MB efficiently
- **Validation Complexity**: Support agents with complex dependency structures

## 🧪 **Testing Interfaces**

### **Mock Interfaces for Testing**

```python
class MockRepositoryCloner(RepositoryCloner):
    """Mock implementation for testing."""

    def __init__(self, mock_responses: Dict[str, str]):
        self.mock_responses = mock_responses

    def clone_agent(self, agent_name: str, target_path: Optional[str] = None) -> str:
        if agent_name in self.mock_responses:
            return self.mock_responses[agent_name]
        raise RepositoryNotFoundError(agent_name, "Mock: Repository not found")
```

### **Test Data Interfaces**

```python
class TestRepositoryProvider:
    """Provide test repositories for testing."""

    def create_test_repository(self, name: str, structure: Dict[str, str]) -> str:
        """Create a test repository with specified structure."""
        pass

    def cleanup_test_repository(self, path: str):
        """Clean up a test repository."""
        pass
```

## 📚 **Usage Examples**

### **Basic Repository Cloning**

```python
from agenthub.github.repository_cloner import RepositoryCloner

cloner = RepositoryCloner()

try:
    local_path = cloner.clone_agent("otherdev/awesome-agent")
    print(f"Repository cloned to: {local_path}")
except RepositoryNotFoundError as e:
    print(f"Repository not found: {e}")
except CloneFailedError as e:
    print(f"Clone failed: {e}")
```

### **Repository Validation**

```python
from agenthub.github.repository_validator import RepositoryValidator

validator = RepositoryValidator()

try:
    result = validator.validate_repository("/path/to/cloned/repo")

    if result.is_valid:
        print("Repository validation passed!")
        print(f"Overall score: {result.overall_score:.2f}")
    else:
        print("Repository validation failed:")
        for error in result.errors:
            print(f"  - {error}")

except ValidationError as e:
    print(f"Validation error: {e}")
```

### **GitHub API Integration**

```python
from agenthub.github.github_client import GitHubClient

client = GitHubClient()

if client.is_authenticated():
    metadata = client.get_repository_metadata("otherdev/awesome-agent")
    print(f"Repository stars: {metadata.stars}")
    print(f"Last updated: {metadata.last_updated}")
else:
    print("GitHub API authentication not available")
```

This interface design provides the foundation for implementing the GitHub Integration Module with clear contracts, error handling, and integration points.
