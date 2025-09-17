"""Environment Management Module for Agent Hub Phase 2.

This module provides virtual environment creation, dependency management,
and environment validation for auto-installed agents.
"""

__version__ = "0.1.0"
__author__ = "William"

# Import implemented components
from .environment_setup import (
    DependencyInstallResult,
    EnvironmentSetup,
    EnvironmentSetupError,
    EnvironmentSetupResult,
    UVNotAvailableError,
)

# Future imports will be added as components are implemented
# from .virtual_environment import VirtualEnvironmentCreator
# from .dependency_manager import DependencyManager

__all__ = [
    "EnvironmentSetup",
    "EnvironmentSetupResult",
    "DependencyInstallResult",
    "EnvironmentSetupError",
    "UVNotAvailableError",
    # Will be populated as more components are implemented
]
