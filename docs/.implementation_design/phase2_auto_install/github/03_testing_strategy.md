# GitHub Module - Testing Strategy

**Document Type**: Testing Strategy
**Module**: GitHub Integration
**Phase**: 2 - Auto-Install
**Author**: William
**Date Created**: 2025-06-28
**Last Updated**: 2025-06-28
**Status**: Active

## 🎯 **Testing Overview**

The GitHub Integration Module testing strategy focuses on validating repository cloning, validation, and GitHub API integration with comprehensive coverage of success scenarios, error cases, and edge conditions.

### **Testing Goals**
1. **Repository Cloning**: Validate git clone operations work correctly
2. **Repository Validation**: Ensure validation logic catches all issues
3. **Error Handling**: Test graceful failure and recovery
4. **Performance**: Validate response time and resource usage targets
5. **Integration**: Test module interactions and data flow

### **Testing Approach**
- **Unit Testing**: 90%+ coverage for all components
- **Integration Testing**: Module interaction validation
- **End-to-End Testing**: Complete workflow validation
- **Performance Testing**: Response time and resource usage validation

## 🏗️ **Testing Structure**

### **Test Organization**

```
tests/phase2_foundation/github/
├── __init__.py
├── test_repository_cloner.py      # Repository cloning tests
├── test_repository_validator.py   # Repository validation tests
├── test_github_client.py          # GitHub API client tests
├── test_git_process_manager.py    # Git process management tests
├── test_url_parser.py             # URL parsing tests
├── test_error_processor.py        # Error handling tests
├── test_integration.py            # Integration tests
├── test_performance.py            # Performance tests
├── conftest.py                    # Test configuration and fixtures
└── test_data/                     # Test data and mock repositories
    ├── valid_agents/              # Valid agent repositories
    ├── invalid_agents/            # Invalid agent repositories
    └── edge_cases/                # Edge case scenarios
```

### **Test Categories**

#### **1. Unit Tests (70%)**
- **Repository Cloner**: URL parsing, path management, clone coordination
- **Repository Validator**: File validation, YAML parsing, Python validation
- **GitHub Client**: API calls, rate limiting, authentication
- **Supporting Classes**: Git process management, URL parsing, error processing

#### **2. Integration Tests (20%)**
- **Module Integration**: Components working together
- **Data Flow**: Information passing between components
- **Error Propagation**: Error handling across module boundaries

#### **3. End-to-End Tests (10%)**
- **Complete Workflows**: Full clone → validate → setup flow
- **Real Scenarios**: Testing with actual GitHub repositories
- **User Experience**: End-to-end user workflows

## 🧪 **Test Data Strategy**

### **Test Repository Types**

#### **Valid Agent Repositories**
```yaml
# test_data/valid_agents/simple_agent/
agent.yaml:
  name: "simple-agent"
  version: "1.0.0"
  description: "A simple test agent"
  author: "test-user"
  interface:
    methods:
      - name: "hello"
        description: "Say hello"
        input_schema: {}
        output_schema:
          type: "object"
          properties:
            message:
              type: "string"

agent.py: |
  def hello(input_data):
      return {"message": "Hello, World!"}

requirements.txt: |
  requests>=2.25.0

README.md: |
  # Simple Test Agent
  A simple test agent for testing purposes.
```

#### **Invalid Agent Repositories**
```yaml
# test_data/invalid_agents/missing_files/
# Only agent.yaml exists, missing other required files

# test_data/invalid_agents/invalid_yaml/
agent.yaml: |
  name: "invalid-agent"
  # Missing required fields
  description: "Invalid agent"

# test_data/invalid_agents/invalid_python/
agent.py: |
  def hello(input_data):
      # Missing return statement
      pass
```

#### **Edge Case Repositories**
```yaml
# test_data/edge_cases/large_repository/
# Repository with many files and large dependencies

# test_data/edge_cases/complex_dependencies/
requirements.txt: |
  numpy>=1.20.0
  pandas>=1.3.0
  scikit-learn>=1.0.0
  torch>=1.9.0
  transformers>=4.11.0

# test_data/edge_cases/special_characters/
agent.yaml:
  name: "special-chars-@#$%"
  description: "Agent with special characters in name"
```

### **Mock Data Providers**

```python
class TestRepositoryProvider:
    """Provide test repositories for testing."""

    def __init__(self, base_path: str = "/tmp/test_repos"):
        self.base_path = base_path
        self.created_repos = []

    def create_test_repository(self, name: str, structure: Dict[str, str]) -> str:
        """Create a test repository with specified structure."""
        repo_path = os.path.join(self.base_path, name)
        os.makedirs(repo_path, exist_ok=True)

        # Create files according to structure
        for file_path, content in structure.items():
            full_path = os.path.join(repo_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            with open(full_path, 'w') as f:
                f.write(content)

        # Initialize git repository
        subprocess.run(['git', 'init'], cwd=repo_path, capture_output=True)
        subprocess.run(['git', 'add', '.'], cwd=repo_path, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial commit'], cwd=repo_path, capture_output=True)

        self.created_repos.append(repo_path)
        return repo_path

    def cleanup_test_repositories(self):
        """Clean up all created test repositories."""
        for repo_path in self.created_repos:
            if os.path.exists(repo_path):
                shutil.rmtree(repo_path)
        self.created_repos.clear()
```

## 🔧 **Test Implementation**

### **Repository Cloner Tests**

```python
import pytest
from unittest.mock import Mock, patch
from agenthub.github.repository_cloner import RepositoryCloner
from agenthub.github.exceptions import RepositoryNotFoundError, CloneFailedError, InvalidAgentNameError

class TestRepositoryCloner:
    """Test Repository Cloner functionality."""

    def test_valid_agent_name(self):
        """Test that valid agent names are accepted."""
        cloner = RepositoryCloner()

        valid_names = [
            "user/agent",
            "developer/awesome-agent",
            "test-user/test_agent",
            "org123/agent-456"
        ]

        for name in valid_names:
            assert cloner.url_parser.is_valid_agent_name(name)

    def test_invalid_agent_name(self):
        """Test that invalid agent names are rejected."""
        cloner = RepositoryCloner()

        invalid_names = [
            "invalid",           # Missing slash
            "user/",            # Missing agent name
            "/agent",           # Missing username
            "user/agent/extra", # Too many parts
            "user@agent",       # Invalid characters
            ""                  # Empty string
        ]

        for name in invalid_names:
            assert not cloner.url_parser.is_valid_agent_name(name)

    @patch('agenthub.github.git_process_manager.GitProcessManager')
    def test_successful_clone(self, mock_git_manager):
        """Test successful repository cloning."""
        # Setup mock
        mock_git_manager.return_value.clone_repository.return_value = Mock(
            success=True,
            output="Cloning into 'test-repo'...",
            exit_code=0,
            target_path="/tmp/test-repo"
        )

        cloner = RepositoryCloner()
        result = cloner.clone_agent("test-user/test-agent")

        assert result == "/tmp/test-repo"
        mock_git_manager.return_value.clone_repository.assert_called_once()

    @patch('agenthub.github.git_process_manager.GitProcessManager')
    def test_clone_failure(self, mock_git_manager):
        """Test handling of clone failures."""
        # Setup mock
        mock_git_manager.return_value.clone_repository.return_value = Mock(
            success=False,
            output="Repository not found",
            exit_code=128,
            target_path="/tmp/test-repo"
        )

        cloner = RepositoryCloner()

        with pytest.raises(CloneFailedError) as exc_info:
            cloner.clone_agent("test-user/nonexistent-agent")

        assert "Repository not found" in str(exc_info.value)

    def test_invalid_agent_name_error(self):
        """Test that invalid agent names raise appropriate errors."""
        cloner = RepositoryCloner()

        with pytest.raises(InvalidAgentNameError):
            cloner.clone_agent("invalid-name")

    @patch('os.path.exists')
    @patch('agenthub.github.git_process_manager.GitProcessManager')
    def test_already_cloned_repository(self, mock_git_manager, mock_exists):
        """Test that already cloned repositories are not re-cloned."""
        # Setup mocks
        mock_exists.return_value = True
        mock_git_manager.return_value.get_remote_url.return_value = "https://github.com/test-user/test-agent.git"

        cloner = RepositoryCloner()
        result = cloner.clone_agent("test-user/test-agent")

        # Should return existing path without cloning
        assert result == "/tmp/test-user_test-agent"
        mock_git_manager.return_value.clone_repository.assert_not_called()
```

### **Repository Validator Tests**

```python
import pytest
import tempfile
import os
from unittest.mock import Mock, patch
from agenthub.github.repository_validator import RepositoryValidator
from agenthub.github.exceptions import ValidationError

class TestRepositoryValidator:
    """Test Repository Validator functionality."""

    def test_required_files_validation(self):
        """Test validation of required files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test repository structure
            self._create_test_repository(temp_dir, {
                'agent.yaml': 'name: test-agent',
                'agent.py': 'def hello(): pass',
                'requirements.txt': 'requests>=2.25.0',
                'README.md': '# Test Agent'
            })

            validator = RepositoryValidator()
            result = validator.validate_repository(temp_dir)

            assert result.is_valid
            assert len(result.errors) == 0

    def test_missing_required_files(self):
        """Test validation fails when required files are missing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create incomplete repository
            self._create_test_repository(temp_dir, {
                'agent.yaml': 'name: test-agent'
                # Missing other required files
            })

            validator = RepositoryValidator()
            result = validator.validate_repository(temp_dir)

            assert not result.is_valid
            assert len(result.errors) > 0
            assert "Missing required file" in str(result.errors)

    def test_invalid_yaml_format(self):
        """Test validation fails with invalid YAML."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create repository with invalid YAML
            self._create_test_repository(temp_dir, {
                'agent.yaml': 'name: test-agent\n  invalid: indentation',
                'agent.py': 'def hello(): pass',
                'requirements.txt': 'requests>=2.25.0',
                'README.md': '# Test Agent'
            })

            validator = RepositoryValidator()
            result = validator.validate_repository(temp_dir)

            assert not result.is_valid
            assert any("YAML" in error for error in result.errors)

    def test_python_validation(self):
        """Test validation of Python code against YAML interface."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create repository with interface mismatch
            self._create_test_repository(temp_dir, {
                'agent.yaml': '''
                name: test-agent
                interface:
                  methods:
                    - name: hello
                      description: Say hello
                ''',
                'agent.py': '''
                def goodbye():  # Wrong method name
                    return {"message": "Goodbye"}
                ''',
                'requirements.txt': 'requests>=2.25.0',
                'README.md': '# Test Agent'
            })

            validator = RepositoryValidator()
            result = validator.validate_repository(temp_dir)

            assert not result.is_valid
            assert any("method" in error.lower() for error in result.errors)

    def _create_test_repository(self, base_path: str, files: Dict[str, str]):
        """Helper method to create test repository structure."""
        for file_path, content in files.items():
            full_path = os.path.join(base_path, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)

            with open(full_path, 'w') as f:
                f.write(content)
```

### **GitHub Client Tests**

```python
import pytest
from unittest.mock import Mock, patch
from agenthub.github.github_client import GitHubClient
from agenthub.github.exceptions import GitHubAPIError, RateLimitExceededError

class TestGitHubClient:
    """Test GitHub Client functionality."""

    @patch('requests.Session')
    def test_repository_exists_check(self, mock_session):
        """Test checking if repository exists."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_session.return_value.request.return_value = mock_response

        client = GitHubClient()
        exists = client.check_repository_exists("test-user/test-agent")

        assert exists
        mock_session.return_value.request.assert_called_once()

    @patch('requests.Session')
    def test_repository_not_found(self, mock_session):
        """Test handling of non-existent repositories."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_session.return_value.request.return_value = mock_response

        client = GitHubClient()
        exists = client.check_repository_exists("test-user/nonexistent-agent")

        assert not exists

    @patch('requests.Session')
    def test_rate_limit_exceeded(self, mock_session):
        """Test handling of rate limit exceeded."""
        # Setup mock response
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "API rate limit exceeded"
        mock_session.return_value.request.return_value = mock_response

        client = GitHubClient()

        with pytest.raises(RateLimitExceededError):
            client.get_repository_metadata("test-user/test-agent")

    @patch('requests.Session')
    def test_authentication_status(self, mock_session):
        """Test authentication status checking."""
        # Test without authentication
        mock_session.return_value.auth = None
        client = GitHubClient()
        assert not client.is_authenticated()

        # Test with authentication
        mock_session.return_value.auth = ("username", "password")
        assert client.is_authenticated()

    @patch('os.environ.get')
    def test_github_token_authentication(self, mock_env_get):
        """Test GitHub token authentication setup."""
        mock_env_get.return_value = "test-token"

        with patch('requests.Session') as mock_session:
            client = GitHubClient()

            # Verify token was set in headers
            mock_session.return_value.headers.update.assert_called_once()
            call_args = mock_session.return_value.headers.update.call_args[0][0]
            assert call_args['Authorization'] == 'token test-token'
```

### **Integration Tests**

```python
import pytest
from unittest.mock import patch
from agenthub.github.repository_cloner import RepositoryCloner
from agenthub.github.repository_validator import RepositoryValidator
from agenthub.github.github_client import GitHubClient

class TestGitHubIntegration:
    """Test integration between GitHub module components."""

    @patch('agenthub.github.git_process_manager.GitProcessManager')
    def test_clone_and_validate_workflow(self, mock_git_manager):
        """Test complete clone and validate workflow."""
        # Setup mocks
        mock_git_manager.return_value.clone_repository.return_value = Mock(
            success=True,
            output="Cloning...",
            exit_code=0,
            target_path="/tmp/test-repo"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test repository
            self._create_test_repository(temp_dir, {
                'agent.yaml': 'name: test-agent',
                'agent.py': 'def hello(): return {"message": "Hello"}',
                'requirements.txt': 'requests>=2.25.0',
                'README.md': '# Test Agent'
            })

            # Test clone
            cloner = RepositoryCloner()
            local_path = cloner.clone_agent("test-user/test-agent")

            # Test validation
            validator = RepositoryValidator()
            result = validator.validate_repository(local_path)

            assert result.is_valid
            assert len(result.errors) == 0

    @patch('agenthub.github.github_client.GitHubClient')
    def test_github_api_integration(self, mock_github_client):
        """Test integration with GitHub API."""
        # Setup mock
        mock_github_client.return_value.check_repository_exists.return_value = True
        mock_github_client.return_value.get_repository_metadata.return_value = Mock(
            name="test-agent",
            stars=10,
            last_updated="2025-06-28T10:00:00Z"
        )

        client = GitHubClient()

        # Test repository existence check
        exists = client.check_repository_exists("test-user/test-agent")
        assert exists

        # Test metadata retrieval
        metadata = client.get_repository_metadata("test-user/test-agent")
        assert metadata.name == "test-agent"
        assert metadata.stars == 10
```

## 📊 **Performance Testing**

### **Response Time Tests**

```python
import time
import pytest
from agenthub.github.repository_cloner import RepositoryCloner
from agenthub.github.repository_validator import RepositoryValidator

class TestGitHubPerformance:
    """Test performance characteristics of GitHub module."""

    def test_clone_performance_target(self):
        """Test that cloning meets performance targets."""
        cloner = RepositoryCloner()

        start_time = time.time()

        # Mock clone operation
        with patch.object(cloner.git_manager, 'clone_repository') as mock_clone:
            mock_clone.return_value = Mock(success=True, target_path="/tmp/test")
            cloner.clone_agent("test-user/test-agent")

        elapsed_time = time.time() - start_time

        # Should complete in under 1 second (with mocking)
        assert elapsed_time < 1.0

    def test_validation_performance_target(self):
        """Test that validation meets performance targets."""
        validator = RepositoryValidator()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test repository
            self._create_test_repository(temp_dir, {
                'agent.yaml': 'name: test-agent',
                'agent.py': 'def hello(): pass',
                'requirements.txt': 'requests>=2.25.0',
                'README.md': '# Test Agent'
            })

            start_time = time.time()
            result = validator.validate_repository(temp_dir)
            elapsed_time = time.time() - start_time

            # Should complete in under 10 seconds
            assert elapsed_time < 10.0
            assert result.is_valid
```

### **Resource Usage Tests**

```python
import psutil
import pytest
from agenthub.github.repository_cloner import RepositoryCloner

class TestGitHubResourceUsage:
    """Test resource usage characteristics."""

    def test_memory_usage_during_clone(self):
        """Test memory usage during cloning operations."""
        process = psutil.Process()
        initial_memory = process.memory_info().rss

        cloner = RepositoryCloner()

        # Mock clone operation
        with patch.object(cloner.git_manager, 'clone_repository') as mock_clone:
            mock_clone.return_value = Mock(success=True, target_path="/tmp/test")
            cloner.clone_agent("test-user/test-agent")

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be under 100MB
        assert memory_increase < 100 * 1024 * 1024  # 100MB in bytes
```

## 🚨 **Error Handling Tests**

### **Network Error Tests**

```python
import pytest
from unittest.mock import patch
from agenthub.github.repository_cloner import RepositoryCloner
from agenthub.github.exceptions import CloneFailedError

class TestGitHubErrorHandling:
    """Test error handling scenarios."""

    @patch('agenthub.github.git_process_manager.GitProcessManager')
    def test_network_timeout_handling(self, mock_git_manager):
        """Test handling of network timeouts."""
        # Setup mock to simulate timeout
        mock_git_manager.return_value.clone_repository.side_effect = Exception("Network timeout")

        cloner = RepositoryCloner()

        with pytest.raises(Exception) as exc_info:
            cloner.clone_agent("test-user/test-agent")

        assert "Network timeout" in str(exc_info.value)

    @patch('agenthub.github.git_process_manager.GitProcessManager')
    def test_git_executable_not_found(self, mock_git_manager):
        """Test handling when git executable is not found."""
        # Setup mock to simulate git not found
        mock_git_manager.return_value.git_path = None

        cloner = RepositoryCloner()

        with patch.object(cloner.git_manager, 'clone_repository') as mock_clone:
            mock_clone.return_value = Mock(
                success=False,
                output="Git executable not found",
                exit_code=-1,
                target_path="/tmp/test"
            )

            with pytest.raises(CloneFailedError) as exc_info:
                cloner.clone_agent("test-user/test-agent")

            assert "Git executable not found" in str(exc_info.value)
```

## 📋 **Test Execution**

### **Running Tests**

```bash
# Run all GitHub module tests
pytest tests/phase2_foundation/github/ -v

# Run specific test categories
pytest tests/phase2_foundation/github/ -k "test_clone" -v
pytest tests/phase2_foundation/github/ -k "test_validation" -v
pytest tests/phase2_foundation/github/ -k "test_performance" -v

# Run with coverage
pytest tests/phase2_foundation/github/ --cov=agenthub.github --cov-report=html

# Run performance tests only
pytest tests/phase2_foundation/github/test_performance.py -v
```

### **Test Configuration**

```python
# conftest.py
import pytest
import tempfile
import shutil
from pathlib import Path

@pytest.fixture(scope="session")
def test_data_dir():
    """Provide test data directory for all tests."""
    base_dir = Path(__file__).parent / "test_data"
    base_dir.mkdir(exist_ok=True)
    yield base_dir

    # Cleanup after all tests
    if base_dir.exists():
        shutil.rmtree(base_dir)

@pytest.fixture
def temp_repo_dir():
    """Provide temporary directory for repository tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_github_config():
    """Provide mock GitHub configuration."""
    return {
        'base_path': '/tmp/test_agents',
        'github_token': 'test-token',
        'git_timeout': 60,
        'min_validation_score': 0.8
    }
```

## 📊 **Success Metrics**

### **Test Coverage Targets**
- **Overall Coverage**: 90%+ for all modules
- **Critical Paths**: 100% coverage for error handling
- **Integration Points**: 100% coverage for module interactions

### **Performance Targets**
- **Response Time**: All operations meet specified targets
- **Resource Usage**: Memory and disk usage within limits
- **Scalability**: Support for concurrent operations

### **Quality Targets**
- **Error Handling**: All error scenarios properly handled
- **Edge Cases**: All edge cases covered and handled
- **User Experience**: Clear error messages and feedback

This testing strategy ensures comprehensive validation of the GitHub Integration Module with robust test coverage, performance validation, and quality assurance.
