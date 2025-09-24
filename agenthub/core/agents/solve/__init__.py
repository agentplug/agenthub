"""
Solve Module for AgentHub

This module provides solve-specific functionality for agent method selection
and parameter extraction using a combined LLM approach for optimal performance.
"""

from .custom_handler import CustomSolveHandler
from .engine import SolveEngine
from .framework_handler import FrameworkSolveHandler
from .interface import AgentSolveInterface
from .result import SolveResult

__all__ = [
    "AgentSolveInterface",
    "CustomSolveHandler",
    "FrameworkSolveHandler",
    "SolveEngine",
    "SolveResult",
]
