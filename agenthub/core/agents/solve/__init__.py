"""
Solve Module for AgentHub

This module provides solve-specific functionality for agent method selection
and parameter extraction using generalized LLM components.
"""

from .custom_handler import CustomSolveHandler
from .engine import SolveEngine
from .framework_handler import FrameworkSolveHandler
from .interface import AgentSolveInterface
from .method_selector import AgentMethodSelector
from .parameter_extractor import AgentParameterExtractor
from .result import SolveResult

__all__ = [
    "AgentSolveInterface",
    "CustomSolveHandler",
    "FrameworkSolveHandler",
    "AgentMethodSelector",
    "AgentParameterExtractor",
    "SolveEngine",
    "SolveResult",
]
