"""GitHub Integration Module for Agent Hub Phase 2.

This module provides GitHub repository integration for agent auto-installation,
including repository cloning, validation, and GitHub API integration.
"""

__version__ = "0.1.0"
__author__ = "William"

# Import implemented components
from .url_parser import URLParser
from .repository_cloner import RepositoryCloner, CloneResult, CloneError, RepositoryNotFoundError, GitNotAvailableError
from .repository_validator import RepositoryValidator, ValidationResult, FileValidationResult

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
    # Will be populated as more components are implemented
]
