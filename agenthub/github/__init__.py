"""GitHub Integration Module for Agent Hub Phase 2.

This module provides GitHub repository integration for agent auto-installation,
including repository cloning, validation, and GitHub API integration.
"""

__version__ = "0.1.0"
__author__ = "William"

# Import implemented components
from .auto_installer import AutoInstaller, InstallationError, InstallationResult
from .repository_cloner import (
    CloneError,
    CloneResult,
    GitNotAvailableError,
    RepositoryCloner,
    RepositoryNotFoundError,
)
from .repository_validator import (
    FileValidationResult,
    RepositoryValidator,
    ValidationResult,
)
from .url_parser import URLParser

# Future imports will be added as components are implemented
# from .github_client import GitHubClient

__all__ = [
    "URLParser",
    "RepositoryCloner",
    "CloneResult",
    "CloneError",
    "RepositoryNotFoundError",
    "GitNotAvailableError",
    "RepositoryValidator",
    "ValidationResult",
    "FileValidationResult",
    "AutoInstaller",
    "InstallationResult",
    "InstallationError",
    # Will be populated as more components are implemented
]
