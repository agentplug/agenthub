"""
Benchmark framework for evaluation.
"""

from .benchmark_manager import BenchmarkManager
from .predefined_benchmarks import PredefinedBenchmarks
from .custom_benchmark import CustomBenchmark

__all__ = [
    'BenchmarkManager',
    'PredefinedBenchmarks',
    'CustomBenchmark'
]
