"""Test URL Parser functionality."""

import pytest

import agenthub
from agenthub.github.url_parser import URLParser


class TestURLParserValidation:
    """Test agent name validation functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = URLParser()

    def test_valid_agent_names(self):
        """Test that valid agent names are accepted."""
        valid_names = [
            "user/agent",
            "developer/awesome-agent",
            "test-user/test_agent",
            "org123/agent-456",
            "company/my_agent",
            "dev_123/agent_v2",
            "a/b",  # Minimal valid case
            "very-long-developer-name/very-long-agent-name-with-many-parts",
        ]

        for name in valid_names:
            assert self.parser.is_valid_agent_name(name), f"Should be valid: {name}"

    def test_invalid_agent_names(self):
        """Test that invalid agent names are rejected."""
        invalid_names = [
            "invalid",  # Missing slash
            "user/",  # Missing agent name
            "/agent",  # Missing username
            "user/agent/extra",  # Too many parts
            "user@agent",  # Invalid characters
            "",  # Empty string
            "user//agent",  # Double slash
            " user/agent",  # Leading space
            "user/agent ",  # Trailing space
            "user/ agent",  # Space in agent name
            "user /agent",  # Space in username
            "user/",  # Empty agent name
            "/",  # Just slash
            "//",  # Double slash only
            None,  # None value
            123,  # Non-string
            "user.agent",  # Dot instead of slash
            "user\\agent",  # Backslash instead of slash
        ]

        for name in invalid_names:
            assert not self.parser.is_valid_agent_name(
                name
            ), f"Should be invalid: {name}"

    def test_edge_cases(self):
        """Test edge cases for agent name validation."""
        # Test with special characters that might be valid
        edge_cases = [
            ("user-123/agent-456", True),
            ("user_name/agent_name", True),
            ("123user/456agent", True),
            ("user123/agent456", True),
            ("a-b/c-d", True),
            ("a_b/c_d", True),
        ]

        for name, expected in edge_cases:
            result = self.parser.is_valid_agent_name(name)
            assert (
                result == expected
            ), f"Agent name: {name}, expected: {expected}, got: {result}"


class TestURLConstruction:
    """Test GitHub URL construction functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = URLParser()

    def test_build_github_url_valid(self):
        """Test GitHub URL construction with valid agent names."""
        test_cases = [
            ("user/agent", "https://github.com/user/agent.git"),
            (
                "developer/awesome-agent",
                "https://github.com/developer/awesome-agent.git",
            ),
            ("test-user/test_agent", "https://github.com/test-user/test_agent.git"),
            ("org123/agent-456", "https://github.com/org123/agent-456.git"),
        ]

        for agent_name, expected_url in test_cases:
            result = self.parser.build_github_url(agent_name)
            assert (
                result == expected_url
            ), f"Agent: {agent_name}, expected: {expected_url}, got: {result}"

    def test_build_github_url_invalid(self):
        """Test that invalid agent names raise ValueError."""
        invalid_names = ["invalid", "user/", "/agent", "user/agent/extra", "", None]

        for name in invalid_names:
            with pytest.raises(ValueError, match="Invalid agent name format"):
                self.parser.build_github_url(name)


class TestURLParsing:
    """Test URL parsing functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = URLParser()

    def test_parse_agent_name_valid_urls(self):
        """Test parsing agent names from valid GitHub URLs."""
        test_cases = [
            ("https://github.com/user/agent.git", "user/agent"),
            ("https://github.com/user/agent", "user/agent"),
            ("https://github.com/user/agent/", "user/agent"),
            ("http://github.com/user/agent.git", "user/agent"),
            ("git@github.com:user/agent.git", "user/agent"),
            ("git@github.com:user/agent", "user/agent"),
        ]

        for url, expected_name in test_cases:
            result = self.parser.parse_agent_name(url)
            assert (
                result == expected_name
            ), f"URL: {url}, expected: {expected_name}, got: {result}"

    def test_parse_agent_name_invalid_urls(self):
        """Test that invalid URLs return None."""
        invalid_urls = [
            "https://gitlab.com/user/agent.git",  # Wrong host
            "https://github.com/user",  # Missing agent name
            "https://github.com/",  # Missing everything
            "not-a-url",  # Not a URL
            "",  # Empty string
            None,  # None value
            "https://github.com/user/agent/extra",  # Too many parts
        ]

        for url in invalid_urls:
            result = self.parser.parse_agent_name(url)
            assert result is None, f"URL: {url} should return None, got: {result}"


class TestRepositoryInfo:
    """Test repository information extraction."""

    def setup_method(self):
        """Set up test fixtures."""
        self.parser = URLParser()

    def test_get_repository_info_valid(self):
        """Test getting repository information from valid agent names."""
        agent_name = "developer/awesome-agent"
        info = self.parser.get_repository_info(agent_name)

        expected = {
            "agent_name": "developer/awesome-agent",
            "developer": "developer",
            "agent": "awesome-agent",
            "github_url": "https://github.com/developer/awesome-agent.git",
            "repository_name": "developer/awesome-agent",
        }

        assert info == expected

    def test_get_repository_info_invalid(self):
        """Test that invalid agent names raise ValueError."""
        with pytest.raises(ValueError, match="Invalid agent name format"):
            self.parser.get_repository_info("invalid-name")


class TestIntegration:
    """Test integration with the module system."""

    def test_import_from_module(self):
        """Test that URLParser can be imported from the github module."""
        from agenthub.github import URLParser as ModuleURLParser
        from agenthub.github.url_parser import URLParser as DirectURLParser

        # Both imports should work and be the same class
        assert ModuleURLParser is DirectURLParser

        # Should be able to instantiate
        parser1 = ModuleURLParser()
        parser2 = DirectURLParser()

        # Should have the same functionality
        test_name = "user/agent"
        assert parser1.is_valid_agent_name(test_name) == parser2.is_valid_agent_name(
            test_name
        )
        assert parser1.build_github_url(test_name) == parser2.build_github_url(
            test_name
        )

    def test_module_exports(self):
        """Test that the github module properly exports URLParser."""

        # URLParser should be in __all__
        assert "URLParser" in agenthub.github.__all__

        # Should be accessible as attribute
        assert hasattr(agenthub.github, "URLParser")

        # Should be the correct class
        parser = agenthub.github.URLParser()
        assert parser.is_valid_agent_name("user/agent")


class TestBackwardCompatibility:
    """Test that URLParser doesn't break existing functionality."""

    def test_existing_imports_still_work(self):
        """Test that existing module imports still work."""
        # These should still work after adding URLParser
        from agenthub import load_agent
        from agenthub.core.agents.loader import AgentLoader
        from agenthub.storage.local_storage import LocalStorage

        # Should be able to instantiate existing components
        storage = LocalStorage()
        loader = AgentLoader(storage)

        assert storage is not None
        assert loader is not None
        assert callable(load_agent)

    def test_no_side_effects(self):
        """Test that importing URLParser has no side effects."""
        # Import URLParser
        # Existing functionality should still work
        from agenthub.core.agents.loader import AgentLoader
        from agenthub.github.url_parser import URLParser
        from agenthub.storage.local_storage import LocalStorage

        storage = LocalStorage()
        loader = AgentLoader(storage)

        # Creating URLParser should not affect existing components
        parser = URLParser()
        assert parser.is_valid_agent_name("user/agent")

        # Existing components should still work normally
        assert loader.storage is storage


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])
