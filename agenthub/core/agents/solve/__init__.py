"""
Solve Module for AgentHub

This module provides solve-specific functionality for agent method selection
and parameter extraction using a combined LLM approach for optimal performance.
"""

from .engine import SolveEngine
from .framework_handler import FrameworkSolveHandler

__all__ = [
    "FrameworkSolveHandler",
    "SolveEngine",
]
