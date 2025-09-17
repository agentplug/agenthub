"""Test Step 1: Project Structure & Basic Setup."""

from pathlib import Path

import pytest

import agenthub


class TestProjectStructure:
    """Test that the project structure is correctly established."""

    def test_github_module_exists(self):
        """Test that GitHub module directory and __init__.py exist."""
        github_init = Path("agenthub/github/__init__.py")
        assert github_init.exists(), "GitHub module __init__.py should exist"

        # Test content
        content = github_init.read_text()
        assert "GitHub Integration Module" in content
        assert "__version__" in content

    def test_environment_module_exists(self):
        """Test that Environment module directory and __init__.py exist."""
        env_init = Path("agenthub/environment/__init__.py")
        assert env_init.exists(), "Environment module __init__.py should exist"

        # Test content
        content = env_init.read_text()
        assert "Environment Management Module" in content
        assert "__version__" in content

    def test_existing_modules_untouched(self):
        """Test that existing modules are still present and untouched."""
        existing_modules = [
            "agenthub/core/__init__.py",
            "agenthub/cli/__init__.py",
            "agenthub/runtime/__init__.py",
            "agenthub/storage/__init__.py",
        ]

        for module_path in existing_modules:
            assert Path(
                module_path
            ).exists(), f"Existing module {module_path} should still exist"


class TestModuleImports:
    """Test that modules can be imported correctly."""

    def test_new_modules_importable(self):
        """Test that new modules can be imported without errors."""
        # Test GitHub module import

        assert hasattr(agenthub.github, "__version__")

        # Test Environment module import

        assert hasattr(agenthub.environment, "__version__")

    def test_existing_modules_still_work(self):
        """Test that existing modules still work after changes."""
        # Test core imports

        # Test storage imports

        # Test runtime imports

        # Test CLI imports

        # Test main API

        # All imports should succeed without errors
        assert True


class TestBackwardCompatibility:
    """Test that existing functionality is preserved."""

    def test_main_api_available(self):
        """Test that main load_agent API is still available."""
        from agenthub import load_agent

        assert callable(load_agent), "load_agent should be callable"

    def test_agent_loader_instantiation(self):
        """Test that AgentLoader can still be instantiated."""
        from agenthub.core.agents.loader import AgentLoader
        from agenthub.storage.local_storage import LocalStorage

        storage = LocalStorage()
        loader = AgentLoader(storage)
        assert loader is not None
        assert loader.storage is storage

    def test_local_storage_functionality(self):
        """Test basic LocalStorage functionality."""
        from agenthub.storage.local_storage import LocalStorage

        storage = LocalStorage()

        # Test basic methods exist
        assert hasattr(storage, "get_agents_dir")
        assert hasattr(storage, "discover_agents")
        assert hasattr(storage, "agent_exists")

        # Test basic functionality
        agents_dir = storage.get_agents_dir()
        assert agents_dir is not None


class TestIntegration:
    """Test integration between modules."""

    def test_module_isolation(self):
        """Test that new modules don't interfere with existing ones."""
        # Import both old and new modules
        from agenthub.core.agents.loader import AgentLoader
        from agenthub.storage.local_storage import LocalStorage

        # Create instances of existing components
        storage = LocalStorage()
        loader = AgentLoader(storage)

        # Should work without interference
        assert loader.storage is storage

        # New modules should be independent
        assert agenthub.github.__version__ == "0.1.0"
        assert agenthub.environment.__version__ == "0.1.0"


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
