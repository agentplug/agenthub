"""URL Parser for GitHub Integration.

This module provides URL parsing and validation functionality for agent names
and GitHub repository URLs.
"""

import logging
import re

logger = logging.getLogger(__name__)


class URLParser:
    """Parse and validate agent names and construct GitHub URLs."""

    def __init__(self) -> None:
        """Initialize the URL parser with validation patterns."""
        # Agent name pattern: developer/agent-name
        # Allows alphanumeric characters, hyphens, and underscores
        self.agent_pattern = re.compile(r"^[a-zA-Z0-9_-]+/[a-zA-Z0-9_-]+$")

        # GitHub base URL for repository cloning
        self.github_base_url = "https://github.com"

    def is_valid_agent_name(self, agent_name: str) -> bool:
        """
        Check if agent name follows the required format.

        Args:
            agent_name: Agent name to validate (e.g., "developer/agent-name")

        Returns:
            bool: True if the agent name is valid, False otherwise

        Example:
            >>> parser = URLParser()
            >>> parser.is_valid_agent_name("user/agent")
            True
            >>> parser.is_valid_agent_name("invalid")
            False
        """
        if not agent_name or not isinstance(agent_name, str):
            logger.debug(f"Invalid agent name type or empty: {agent_name}")
            return False

        # Check if it matches the pattern
        if not self.agent_pattern.match(agent_name):
            logger.debug(f"Agent name doesn't match pattern: {agent_name}")
            return False

        # Additional validation: ensure it has exactly one slash
        slash_count = agent_name.count("/")
        if slash_count != 1:
            logger.debug(
                f"Agent name has {slash_count} slashes, expected 1: {agent_name}"
            )
            return False

        # Ensure both parts (developer and agent) are non-empty
        parts = agent_name.split("/")
        if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
            logger.debug(f"Invalid agent name parts: {parts}")
            return False

        logger.debug(f"Agent name is valid: {agent_name}")
        return True

    def build_github_url(self, agent_name: str) -> str:
        """
        Build GitHub URL from agent name.

        Args:
            agent_name: Agent name in format "developer/agent-name"

        Returns:
            str: GitHub clone URL

        Raises:
            ValueError: If agent name format is invalid

        Example:
            >>> parser = URLParser()
            >>> parser.build_github_url("user/agent")
            'https://github.com/user/agent.git'
        """
        if not self.is_valid_agent_name(agent_name):
            raise ValueError(
                f"Invalid agent name format: {agent_name}. "
                f"Expected format: 'developer/agent-name'"
            )

        # Construct the GitHub clone URL
        github_url = f"{self.github_base_url}/{agent_name}.git"

        logger.debug(f"Built GitHub URL: {github_url} for agent: {agent_name}")
        return github_url

    def parse_agent_name(self, github_url: str) -> str | None:
        """
        Extract agent name from GitHub URL.

        Args:
            github_url: GitHub repository URL

        Returns:
            Optional[str]: Agent name if URL is valid, None otherwise

        Example:
            >>> parser = URLParser()
            >>> parser.parse_agent_name("https://github.com/user/agent.git")
            'user/agent'
        """
        if not github_url or not isinstance(github_url, str):
            return None

        # Handle various GitHub URL formats
        patterns = [
            r"https://github\.com/([^/]+/[^/]+?)(?:\.git)?/?$",
            r"git@github\.com:([^/]+/[^/]+?)(?:\.git)?/?$",
            r"http://github\.com/([^/]+/[^/]+?)(?:\.git)?/?$",
        ]

        for pattern in patterns:
            match = re.match(pattern, github_url)
            if match:
                agent_name = match.group(1)
                if self.is_valid_agent_name(agent_name):
                    logger.debug(
                        f"Parsed agent name: {agent_name} from URL: {github_url}"
                    )
                    return agent_name

        logger.debug(f"Could not parse agent name from URL: {github_url}")
        return None

    def get_repository_info(self, agent_name: str) -> dict:
        """
        Get repository information from agent name.

        Args:
            agent_name: Agent name in format "developer/agent-name"

        Returns:
            dict: Repository information including developer, agent, and URL

        Raises:
            ValueError: If agent name format is invalid
        """
        if not self.is_valid_agent_name(agent_name):
            raise ValueError(f"Invalid agent name format: {agent_name}")

        parts = agent_name.split("/")
        developer = parts[0]
        agent = parts[1]

        return {
            "agent_name": agent_name,
            "developer": developer,
            "agent": agent,
            "github_url": self.build_github_url(agent_name),
            "repository_name": f"{developer}/{agent}",
        }
