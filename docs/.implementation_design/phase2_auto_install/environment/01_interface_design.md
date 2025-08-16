# Environment Module - Interface Design

**Document Type**: Detailed Interface Design
**Module**: Environment Management
**Phase**: 2 - Auto-Install
**Author**: William
**Date Created**: 2025-06-28
**Last Updated**: 2025-06-28
**Status**: Active

## 🎯 **Public Interfaces**

### **Environment Setup Interface**

```python
class EnvironmentSetup:
    """Coordinate the complete environment setup process for agents."""

    def setup_environment(self, agent_path: str, requirements_path: str) -> EnvironmentSetupResult:
        """
        Set up a complete virtual environment for an agent.

        Args:
            agent_path: Path to the agent directory
            requirements_path: Path to requirements.txt file

        Returns:
            EnvironmentSetupResult with setup status and environment details

        Raises:
            EnvironmentSetupError: If environment setup fails
            RequirementsError: If requirements.txt is invalid or installation fails
            VirtualEnvironmentError: If virtual environment creation fails
        """
        pass

    def validate_environment(self, env_path: str) -> EnvironmentValidationResult:
        """Validate that an environment is properly configured and functional."""
        pass

    def cleanup_failed_setup(self, agent_path: str):
        """Clean up resources from a failed environment setup."""
        pass
```

### **Virtual Environment Creator Interface**

```python
class VirtualEnvironmentCreator:
    """Create and configure Python virtual environments."""

    def create_environment(self, target_path: str, python_version: Optional[str] = None) -> str:
        """
        Create a new virtual environment.

        Args:
            target_path: Path where environment should be created
            python_version: Optional Python version specification

        Returns:
            Path to the created virtual environment

        Raises:
            VirtualEnvironmentError: If environment creation fails
            PythonVersionError: If specified Python version is not available
        """
        pass

    def activate_environment(self, env_path: str) -> EnvironmentContext:
        """Activate a virtual environment and return context manager."""
        pass

    def deactivate_environment(self, env_path: str):
        """Deactivate a virtual environment."""
        pass

    def get_python_executable(self, env_path: str) -> str:
        """Get the Python executable path for a virtual environment."""
        pass

    def get_environment_info(self, env_path: str) -> EnvironmentInfo:
        """Get detailed information about a virtual environment."""
        pass
```

### **Dependency Manager Interface**

```python
class DependencyManager:
    """Install and manage Python dependencies in virtual environments."""

    def install_dependencies(self, env_path: str, requirements_path: str) -> DependencyInstallResult:
        """
        Install dependencies from requirements.txt in a virtual environment.

        Args:
            env_path: Path to the virtual environment
            requirements_path: Path to requirements.txt file

        Returns:
            DependencyInstallResult with installation status and details

        Raises:
            RequirementsError: If requirements.txt is invalid
            InstallationError: If dependency installation fails
            ConflictError: If dependency conflicts cannot be resolved
        """
        pass

    def validate_requirements(self, requirements_path: str) -> RequirementsValidationResult:
        """Validate requirements.txt format and content."""
        pass

    def resolve_conflicts(self, requirements: List[str]) -> ConflictResolutionResult:
        """Resolve dependency conflicts in requirements."""
        pass

    def get_installed_packages(self, env_path: str) -> List[PackageInfo]:
        """Get list of installed packages in a virtual environment."""
        pass

    def check_package_health(self, env_path: str) -> PackageHealthResult:
        """Check the health and compatibility of installed packages."""
        pass
```

### **Environment Validator Interface**

```python
class EnvironmentValidator:
    """Validate virtual environment configuration and functionality."""

    def validate_environment(self, env_path: str) -> EnvironmentValidationResult:
        """
        Validate that a virtual environment is properly configured.

        Args:
            env_path: Path to the virtual environment

        Returns:
            EnvironmentValidationResult with validation details
        """
        pass

    def test_python_functionality(self, env_path: str) -> PythonTestResult:
        """Test basic Python functionality in the environment."""
        pass

    def test_package_imports(self, env_path: str, packages: List[str]) -> ImportTestResult:
        """Test that specified packages can be imported."""
        pass

    def check_environment_isolation(self, env_path: str) -> IsolationTestResult:
        """Verify that the environment is properly isolated."""
        pass
```

## 🔧 **Data Models**

### **EnvironmentSetupResult Class**

```python
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class EnvironmentSetupResult:
    """Result of environment setup operation."""
    success: bool
    environment_path: str
    python_executable: str
    setup_time: float  # seconds
    installed_packages: List[PackageInfo]
    warnings: List[str]
    errors: List[str]
    setup_log: str
    validation_result: Optional[EnvironmentValidationResult] = None
```

### **EnvironmentValidationResult Class**

```python
@dataclass
class EnvironmentValidationResult:
    """Result of environment validation."""
    is_valid: bool
    validation_time: float  # seconds
    python_version: str
    python_executable: str
    package_count: int
    validation_errors: List[str]
    validation_warnings: List[str]
    test_results: Dict[str, bool]
    overall_score: float  # 0.0 to 1.0
```

### **EnvironmentInfo Class**

```python
@dataclass
class EnvironmentInfo:
    """Information about a virtual environment."""
    path: str
    python_version: str
    python_executable: str
    creation_time: datetime
    last_modified: datetime
    size_bytes: int
    package_count: int
    is_active: bool
    platform: str
    architecture: str
```

### **DependencyInstallResult Class**

```python
@dataclass
class DependencyInstallResult:
    """Result of dependency installation."""
    success: bool
    installed_packages: List[PackageInfo]
    failed_packages: List[FailedPackage]
    installation_time: float  # seconds
    total_packages: int
    successful_installations: int
    failed_installations: int
    warnings: List[str]
    installation_log: str
```

### **PackageInfo Class**

```python
@dataclass
class PackageInfo:
    """Information about an installed package."""
    name: str
    version: str
    location: str
    dependencies: List[str]
    size_bytes: int
    install_time: datetime
    is_editable: bool
    metadata: Dict[str, Any]
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
    validation_warnings: List[str]
    dependency_count: int
    has_conflicts: bool
    conflict_details: List[str]
```

### **ConflictResolutionResult Class**

```python
@dataclass
class ConflictResolutionResult:
    """Result of dependency conflict resolution."""
    resolved: bool
    original_requirements: List[str]
    resolved_requirements: List[str]
    conflicts_resolved: List[str]
    remaining_conflicts: List[str]
    resolution_strategy: str
    resolution_notes: str
```

### **EnvironmentContext Class**

```python
from contextlib import AbstractContextManager

class EnvironmentContext(AbstractContextManager):
    """Context manager for virtual environment activation."""

    def __enter__(self) -> 'EnvironmentContext':
        """Activate the virtual environment."""
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Deactivate the virtual environment."""
        pass

    def run_command(self, command: List[str], **kwargs) -> subprocess.CompletedProcess:
        """Run a command in the activated environment."""
        pass

    def get_env_vars(self) -> Dict[str, str]:
        """Get environment variables for the activated environment."""
        pass
```

## 🚨 **Exception Classes**

### **EnvironmentSetupError**

```python
class EnvironmentSetupError(Exception):
    """Raised when environment setup fails."""

    def __init__(self, agent_path: str, reason: str = None, details: Dict[str, Any] = None):
        self.agent_path = agent_path
        self.reason = reason
        self.details = details or {}
        super().__init__(f"Environment setup failed for '{agent_path}': {reason}")
```

### **VirtualEnvironmentError**

```python
class VirtualEnvironmentError(Exception):
    """Raised when virtual environment creation or management fails."""

    def __init__(self, env_path: str, operation: str, reason: str = None):
        self.env_path = env_path
        self.operation = operation
        self.reason = reason
        super().__init__(f"Virtual environment {operation} failed for '{env_path}': {reason}")
```

### **RequirementsError**

```python
class RequirementsError(Exception):
    """Raised when requirements.txt processing fails."""

    def __init__(self, requirements_path: str, reason: str = None, details: Dict[str, Any] = None):
        self.requirements_path = requirements_path
        self.reason = reason
        self.details = details or {}
        super().__init__(f"Requirements processing failed for '{requirements_path}': {reason}")
```

### **InstallationError**

```python
class InstallationError(Exception):
    """Raised when package installation fails."""

    def __init__(self, package_name: str, env_path: str, reason: str = None, output: str = None):
        self.package_name = package_name
        self.env_path = env_path
        self.reason = reason
        self.output = output
        super().__init__(f"Package '{package_name}' installation failed in '{env_path}': {reason}")
```

### **ConflictError**

```python
class ConflictError(Exception):
    """Raised when dependency conflicts cannot be resolved."""

    def __init__(self, conflicts: List[str], requirements: List[str], reason: str = None):
        self.conflicts = conflicts
        self.requirements = requirements
        self.reason = reason
        super().__init__(f"Dependency conflicts detected: {conflicts}. Reason: {reason}")
```

### **PythonVersionError**

```python
class PythonVersionError(Exception):
    """Raised when specified Python version is not available."""

    def __init__(self, requested_version: str, available_versions: List[str]):
        self.requested_version = requested_version
        self.available_versions = available_versions
        super().__init__(f"Python version '{requested_version}' not available. Available: {available_versions}")
```

## 🔗 **Module Integration Points**

### **With Core Module**

```python
# Core module uses Environment module for agent setup
from agentmanager.environment.environment_setup import EnvironmentSetup

class AutoInstaller:
    def __init__(self):
        self.env_setup = EnvironmentSetup()

    def install_agent(self, agent_name: str) -> InstallationResult:
        # Clone and validate repository...

        # Set up environment
        env_result = self.env_setup.setup_environment(
            agent_path=local_path,
            requirements_path=os.path.join(local_path, 'requirements.txt')
        )

        if not env_result.success:
            raise EnvironmentSetupError(local_path, "Environment setup failed")

        # Continue with installation...
```

### **With Storage Module**

```python
# Environment module provides environment information to storage
from agentmanager.storage.metadata_manager import MetadataManager

class EnvironmentSetup:
    def __init__(self):
        self.metadata_manager = MetadataManager()

    def setup_environment(self, agent_path: str, requirements_path: str) -> EnvironmentSetupResult:
        # Set up environment...

        # Store environment metadata
        self.metadata_manager.store_environment_info(agent_path, env_result)

        return env_result
```

### **With GitHub Module**

```python
# Environment module uses GitHub module for repository information
from agentmanager.github.github_client import GitHubClient

class EnvironmentSetup:
    def __init__(self):
        self.github_client = GitHubClient()

    def setup_environment(self, agent_name: str, agent_path: str, requirements_path: str):
        # Get repository metadata for environment configuration
        metadata = self.github_client.get_repository_metadata(agent_name)

        # Use metadata for environment setup...
```

## 📊 **Performance Requirements**

### **Response Time Targets**
- **Environment Creation**: < 30 seconds for typical agents
- **Dependency Installation**: < 2 minutes for typical agents
- **Environment Validation**: < 10 seconds
- **Package Health Check**: < 15 seconds

### **Resource Usage Targets**
- **Memory**: < 200MB during environment setup
- **Disk Space**: < 100MB overhead per agent environment
- **CPU**: Efficient use of available CPU resources

### **Scalability Targets**
- **Concurrent Setups**: Support 3+ simultaneous environment setups
- **Environment Count**: Support 50+ agent environments
- **Package Complexity**: Handle complex dependency trees efficiently

## 🧪 **Testing Interfaces**

### **Mock Implementations**

```python
class MockEnvironmentSetup(EnvironmentSetup):
    """Mock implementation for testing."""

    def __init__(self, mock_results: Dict[str, EnvironmentSetupResult]):
        super().__init__()
        self.mock_results = mock_results
        self.setup_calls = []

    def setup_environment(self, agent_path: str, requirements_path: str) -> EnvironmentSetupResult:
        """Mock environment setup."""
        self.setup_calls.append({
            'agent_path': agent_path,
            'requirements_path': requirements_path
        })

        if agent_path in self.mock_results:
            return self.mock_results[agent_path]

        # Default success result
        return EnvironmentSetupResult(
            success=True,
            environment_path=f"/tmp/mock_env_{agent_path}",
            python_executable="/usr/bin/python3",
            setup_time=1.0,
            installed_packages=[],
            warnings=[],
            errors=[],
            setup_log="Mock setup completed"
        )

    def get_setup_calls(self) -> List[Dict[str, str]]:
        """Get list of setup calls made during testing."""
        return self.setup_calls.copy()
```

### **Test Data Providers**

```python
class TestEnvironmentProvider:
    """Provide test environments for testing."""

    def create_test_environment(self, name: str, packages: List[str] = None) -> str:
        """Create a test virtual environment."""
        pass

    def cleanup_test_environment(self, env_path: str):
        """Clean up a test environment."""
        pass

    def create_test_requirements(self, packages: List[str]) -> str:
        """Create a test requirements.txt file."""
        pass
```

## 📚 **Usage Examples**

### **Basic Environment Setup**

```python
from agentmanager.environment.environment_setup import EnvironmentSetup

env_setup = EnvironmentSetup()

try:
    result = env_setup.setup_environment(
        agent_path="/path/to/agent",
        requirements_path="/path/to/agent/requirements.txt"
    )

    if result.success:
        print(f"Environment setup successful!")
        print(f"Environment path: {result.environment_path}")
        print(f"Python executable: {result.python_executable}")
        print(f"Setup time: {result.setup_time:.2f} seconds")
    else:
        print("Environment setup failed:")
        for error in result.errors:
            print(f"  - {error}")

except EnvironmentSetupError as e:
    print(f"Environment setup error: {e}")
```

### **Virtual Environment Management**

```python
from agentmanager.environment.virtual_environment import VirtualEnvironmentCreator

env_creator = VirtualEnvironmentCreator()

# Create environment
env_path = env_creator.create_environment("/tmp/my_agent_env")

# Get environment info
env_info = env_creator.get_environment_info(env_path)
print(f"Python version: {env_info.python_version}")
print(f"Package count: {env_info.package_count}")

# Activate environment
with env_creator.activate_environment(env_path) as env:
    # Run commands in activated environment
    result = env.run_command(["python", "--version"])
    print(f"Python version: {result.stdout}")
```

### **Dependency Management**

```python
from agentmanager.environment.dependency_manager import DependencyManager

dep_manager = DependencyManager()

# Validate requirements
validation = dep_manager.validate_requirements("/path/to/requirements.txt")
if not validation.is_valid:
    print("Requirements validation failed:")
    for error in validation.validation_errors:
        print(f"  - {error}")
    return

# Install dependencies
result = dep_manager.install_dependencies(
    env_path="/tmp/my_agent_env",
    requirements_path="/path/to/requirements.txt"
)

if result.success:
    print(f"Successfully installed {result.successful_installations} packages")
    print(f"Installation time: {result.installation_time:.2f} seconds")
else:
    print("Dependency installation failed:")
    for failed in result.failed_packages:
        print(f"  - {failed.name}: {failed.reason}")
```

### **Environment Validation**

```python
from agentmanager.environment.environment_validator import EnvironmentValidator

validator = EnvironmentValidator()

# Validate environment
validation = validator.validate_environment("/tmp/my_agent_env")

if validation.is_valid:
    print("Environment validation passed!")
    print(f"Python version: {validation.python_version}")
    print(f"Package count: {validation.package_count}")
    print(f"Overall score: {validation.overall_score:.2f}")
else:
    print("Environment validation failed:")
    for error in validation.validation_errors:
        print(f"  - {error}")

# Test specific packages
import_result = validator.test_package_imports(
    "/tmp/my_agent_env",
    ["requests", "numpy", "pandas"]
)

for package, success in import_result.import_results.items():
    status = "✓" if success else "✗"
    print(f"{status} {package}")
```

This interface design provides the foundation for implementing the Environment Management Module with clear contracts, error handling, and integration points for virtual environment creation and dependency management.
