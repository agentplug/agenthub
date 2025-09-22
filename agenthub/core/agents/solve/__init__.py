"""Solve module for intelligent agent method selection.

This module provides:
- SolveEngine: Main orchestrator for solve functionality
- AgentSolveInterface: Interface for custom solve methods
- SolveResult: Standardized result format
- CustomSolveHandler: Handles agents with custom solve methods
- FrameworkSolveHandler: Handles framework-level solve using LLM
"""

from .custom_handler import CustomSolveHandler
from .engine import SolveEngine
from .framework_handler import FrameworkSolveHandler
from .interface import AgentSolveInterface
from .result import SolveResult

__all__ = [
    "SolveEngine",
    "AgentSolveInterface",
    "SolveResult",
    "CustomSolveHandler",
    "FrameworkSolveHandler",
]
