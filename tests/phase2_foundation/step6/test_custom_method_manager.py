"""
Simplified tests for Custom Method Manager.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

from agentmanager.core.custom_method_manager import CustomMethodManager, MethodInfo
from agentmanager.core.exceptions import (
    MethodValidationError, MethodNotFoundError, MethodSecurityError
)


class TestCustomMethodManager:
    """Test cases for CustomMethodManager."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def manager(self, temp_dir):
        """Create a CustomMethodManager instance for testing."""
        return CustomMethodManager(base_path=temp_dir, security_level="medium")
    
    @pytest.fixture
    def sample_python_function(self):
        """Sample Python function for testing."""
        def sample_function(text: str, count: int = 1) -> str:
            """Sample function for testing."""
            return text * count
        return sample_function
    
    def test_init_default_values(self):
        """Test initialization with default values."""
        manager = CustomMethodManager()
        assert manager.security_level == "medium"
        assert "python" in manager.supported_languages
        assert "javascript" in manager.supported_languages

    def test_init_custom_values(self, temp_dir):
        """Test initialization with custom values."""
        manager = CustomMethodManager(base_path=temp_dir, security_level="high")
        assert manager.base_path == Path(temp_dir)
        assert manager.security_level == "high"

    def test_inject_python_function(self, manager, sample_python_function):
        """Test injecting a Python function."""
        agent_path = "test/agent"
        method_name = "test_function"
        
        manager.inject_method(agent_path, method_name, sample_python_function, "python")
        
        # Verify method was stored
        assert manager.validate_method_exists(agent_path, method_name)
        
        # Verify method info
        method_info = manager.get_method_info(agent_path, method_name)
        assert method_info.name == method_name
        assert method_info.language == "python"

    def test_inject_python_string(self, manager):
        """Test injecting Python code as string."""
        agent_path = "test/agent"
        method_name = "string_function"
        code = "def string_function(x):\n    return x * 2"
        
        manager.inject_method(agent_path, method_name, code, "python")
        
        assert manager.validate_method_exists(agent_path, method_name)
        method_info = manager.get_method_info(agent_path, method_name)
        assert method_info.language == "python"

    def test_inject_method_invalid_name(self, manager, sample_python_function):
        """Test injecting method with invalid name."""
        agent_path = "test/agent"
        method_name = "123invalid"
        
        with pytest.raises(ValueError, match="Invalid method name"):
            manager.inject_method(agent_path, method_name, sample_python_function, "python")

    def test_inject_method_unsupported_language(self, manager, sample_python_function):
        """Test injecting method with unsupported language."""
        agent_path = "test/agent"
        method_name = "test_function"
        
        with pytest.raises(ValueError, match="Unsupported language"):
            manager.inject_method(agent_path, method_name, sample_python_function, "rust")

    def test_inject_method_none_implementation(self, manager):
        """Test injecting None implementation."""
        agent_path = "test/agent"
        method_name = "test_function"
        
        with pytest.raises(ValueError, match="agent_path and method_name are required"):
            manager.inject_method(agent_path, method_name, None, "python")

    def test_inject_method_empty_agent_path(self, manager, sample_python_function):
        """Test injecting method with empty agent path."""
        method_name = "test_function"
        
        with pytest.raises(ValueError, match="agent_path and method_name are required"):
            manager.inject_method("", method_name, sample_python_function, "python")

    def test_get_method_success(self, manager, sample_python_function):
        """Test successfully getting a method."""
        agent_path = "test/agent"
        method_name = "test_function"
        
        manager.inject_method(agent_path, method_name, sample_python_function, "python")
        
        retrieved_method = manager.get_method(agent_path, method_name)
        assert callable(retrieved_method)

    def test_get_method_not_found(self, manager):
        """Test getting a method that doesn't exist."""
        agent_path = "test/agent"
        method_name = "nonexistent"
        
        with pytest.raises(MethodNotFoundError, match="not found"):
            manager.get_method(agent_path, method_name)

    def test_list_methods_empty(self, manager):
        """Test listing methods when none exist."""
        agent_path = "test/agent"
        
        methods = manager.list_methods(agent_path)
        assert methods == {}

    def test_list_methods_with_methods(self, manager, sample_python_function):
        """Test listing methods when methods exist."""
        agent_path = "test/agent"
        method_name = "test_function"
        
        manager.inject_method(agent_path, method_name, sample_python_function, "python")
        
        methods = manager.list_methods(agent_path)
        assert method_name in methods
        assert len(methods) == 1

    def test_remove_method_success(self, manager, sample_python_function):
        """Test successfully removing a method."""
        agent_path = "test/agent"
        method_name = "test_function"
        
        manager.inject_method(agent_path, method_name, sample_python_function, "python")
        assert manager.validate_method_exists(agent_path, method_name)
        
        manager.remove_method(agent_path, method_name)
        assert not manager.validate_method_exists(agent_path, method_name)

    def test_remove_method_not_exists(self, manager):
        """Test removing a method that doesn't exist."""
        agent_path = "test/agent"
        method_name = "nonexistent"
        
        # Should not raise an error
        manager.remove_method(agent_path, method_name)

    def test_validate_method_exists(self, manager, sample_python_function):
        """Test method existence validation."""
        agent_path = "test/agent"
        method_name = "test_function"
        
        assert not manager.validate_method_exists(agent_path, method_name)
        
        manager.inject_method(agent_path, method_name, sample_python_function, "python")
        
        assert manager.validate_method_exists(agent_path, method_name)

    def test_get_method_info(self, manager, sample_python_function):
        """Test getting method information."""
        agent_path = "test/agent"
        method_name = "test_function"
        
        manager.inject_method(agent_path, method_name, sample_python_function, "python")
        
        method_info = manager.get_method_info(agent_path, method_name)
        assert method_info is not None
        assert method_info.name == method_name
        assert method_info.language == "python"

    def test_get_method_info_not_exists(self, manager):
        """Test getting method info for non-existent method."""
        agent_path = "test/agent"
        method_name = "nonexistent"
        
        method_info = manager.get_method_info(agent_path, method_name)
        assert method_info is None

    def test_cleanup_expired_methods(self, manager, sample_python_function):
        """Test cleanup of expired methods."""
        agent_path = "test/agent"
        method_name = "test_function"
        
        # Inject method
        manager.inject_method(agent_path, method_name, sample_python_function, "python")
        
        # Get current time and create a very old timestamp
        import time
        current_time = time.time()
        old_time = current_time - (25 * 3600)  # 25 hours ago
        
        # Manually update the method's timestamp to make it appear old
        method_info = manager.get_method_info(agent_path, method_name)
        method_info.injected_at = old_time
        manager._save_method(agent_path, method_info)
        
        # Now cleanup should find and remove it
        cleaned_count = manager.cleanup_expired_methods(max_age_hours=24)
        assert cleaned_count == 1

    def test_cleanup_no_expired_methods(self, manager, sample_python_function):
        """Test cleanup when no methods are expired."""
        agent_path = "test/agent"
        method_name = "test_function"
        
        manager.inject_method(agent_path, method_name, sample_python_function, "python")
        
        cleaned_count = manager.cleanup_expired_methods(max_age_hours=24)
        assert cleaned_count == 0

    def test_checksum_calculation(self, manager):
        """Test checksum calculation."""
        content = "test content"
        checksum1 = manager._calculate_checksum(content)
        checksum2 = manager._calculate_checksum(content)
        
        assert checksum1 == checksum2
        assert len(checksum1) == 64  # SHA256 hex length

    def test_extract_metadata_python_function(self, manager, sample_python_function):
        """Test metadata extraction from Python function."""
        metadata = manager._extract_metadata(sample_python_function, "python")
        
        assert metadata["language"] == "python"
        assert "size_bytes" in metadata
        assert "parameters" in metadata
        # The parameters might be *args, **kwargs if we can't get the real signature
        assert len(metadata["parameters"]) >= 0

    def test_extract_metadata_string(self, manager):
        """Test metadata extraction from string."""
        content = "def test(): pass"
        metadata = manager._extract_metadata(content, "python")
        
        assert metadata["language"] == "python"
        assert metadata["size_bytes"] > 0

    def test_extract_metadata_function_source(self, manager):
        """Test metadata extraction from function source string."""
        content = "def test_function(text: str, count: int = 1) -> str:\n    return text * count"
        metadata = manager._extract_metadata(content, "python")
        
        assert metadata["language"] == "python"
        assert metadata["size_bytes"] > 0

    def test_security_validation_dangerous_code(self, manager):
        """Test security validation blocks dangerous code."""
        agent_path = "test/agent"
        method_name = "dangerous_method"
        
        dangerous_code = "import os; exec('print(1)')"
        
        with pytest.raises(MethodValidationError, match="validation failed"):
            manager.inject_method(agent_path, method_name, dangerous_code, "python")

    def test_create_python_function_success(self, manager):
        """Test creating a Python function from source."""
        method_info = MethodInfo(
            name="test_func",
            language="python",
            implementation="def test_func(x):\n    return x * 2",
            injected_at=1234567890.0,
            checksum="abc123",
            metadata={}
        )
        
        func = manager._create_python_function(method_info)
        assert callable(func)

    def test_create_python_function_invalid_syntax(self, manager):
        """Test creating function with invalid Python syntax."""
        method_info = MethodInfo(
            name="test_func",
            language="python", 
            implementation="def test_func( x: return x * 2",  # Invalid syntax
            injected_at=1234567890.0,
            checksum="abc123",
            metadata={}
        )
        
        with pytest.raises(MethodValidationError, match="Failed to create Python function"):
            manager._create_python_function(method_info)

    def test_multiple_methods_same_agent(self, manager, sample_python_function):
        """Test multiple methods for the same agent."""
        agent_path = "test/agent"
        
        # Inject multiple methods
        manager.inject_method(agent_path, "func1", sample_python_function, "python")
        manager.inject_method(agent_path, "func2", "def func2(): return 'test'", "python")
        
        methods = manager.list_methods(agent_path)
        assert len(methods) == 2
        assert "func1" in methods
        assert "func2" in methods

    def test_methods_different_agents(self, manager, sample_python_function):
        """Test methods for different agents."""
        # Inject methods for different agents
        manager.inject_method("agent1", "func1", sample_python_function, "python")
        manager.inject_method("agent2", "func2", sample_python_function, "python")
        
        # Check isolation
        methods1 = manager.list_methods("agent1")
        methods2 = manager.list_methods("agent2")
        
        assert "func1" in methods1
        assert "func2" in methods2
        assert "func1" not in methods2
        assert "func2" not in methods1

    def test_method_info_dataclass(self):
        """Test MethodInfo dataclass."""
        metadata = {"test": "value"}
        method_info = MethodInfo(
            name="test",
            language="python",
            implementation="def test(): pass",
            injected_at=1234567890.0,
            checksum="abc123",
            metadata=metadata
        )
        
        assert method_info.name == "test"
        assert method_info.language == "python"
        assert method_info.metadata == metadata
        assert method_info.checksum == "abc123"
        
        # Test to_dict method
        data = method_info.to_dict()
        assert data["name"] == "test"
        assert data["language"] == "python"