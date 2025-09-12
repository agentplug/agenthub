"""
AgentHub Evaluation System

This module provides comprehensive evaluation capabilities for AI agents,
including demo mode for quick assessment and benchmark mode for comprehensive testing.
"""

from .core.evaluation_engine import EvaluationEngine, DemoEvaluator, BenchmarkEvaluator
from .core.data_models import (
    EvaluationResults,
    AgentOutput,
    EvaluationContext,
    MetricResult,
    MetricResults,
    EvaluationConfig,
    EvaluationMode,
    SampleData,
    BenchmarkDefinition
)
from .metrics import (
    AccuracyMetrics,
    QualityMetrics,
    PerformanceMetrics,
    ReliabilityMetrics
)
from .benchmarks import BenchmarkManager, PredefinedBenchmarks, CustomBenchmark, PublicBenchmarkLoader
from .reporting import ReportGenerator, HTMLReporter, JSONReporter
from .evaluate import (
    evaluate,
    evaluate_demo,
    evaluate_benchmark,
    generate_report,
    get_available_benchmarks,
    get_available_modes,
    get_available_report_formats
)

__all__ = [
    'EvaluationEngine',
    'DemoEvaluator', 
    'BenchmarkEvaluator',
    'EvaluationResults',
    'AgentOutput',
    'EvaluationContext',
    'MetricResult',
    'MetricResults',
    'EvaluationConfig',
    'EvaluationMode',
    'SampleData',
    'BenchmarkDefinition',
    'AccuracyMetrics',
    'QualityMetrics',
    'PerformanceMetrics',
    'ReliabilityMetrics',
    'BenchmarkManager',
    'PredefinedBenchmarks',
    'CustomBenchmark',
    'PublicBenchmarkLoader',
    'ReportGenerator',
    'HTMLReporter',
    'JSONReporter',
    'evaluate',
    'evaluate_demo',
    'evaluate_benchmark',
    'generate_report',
    'get_available_benchmarks',
    'get_available_modes',
    'get_available_report_formats'
]

# Version information
__version__ = "1.0.0"
