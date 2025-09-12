"""
Data models for the evaluation system.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum


class EvaluationMode(Enum):
    """Evaluation modes."""
    DEMO = "demo"
    BENCHMARK = "benchmark"
    CUSTOM = "custom"


class MetricType(Enum):
    """Metric types."""
    ACCURACY = "accuracy"
    QUALITY = "quality"
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"


@dataclass
class AgentOutput:
    """Represents a single agent output."""
    input_text: str
    output_text: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None


@dataclass
class MetricResult:
    """Represents a single metric calculation result."""
    metric_type: str
    value: float
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MetricResults:
    """Represents results for multiple metrics."""
    agent_output: AgentOutput
    metrics: Dict[str, MetricResult]
    summary: Optional[Dict[str, float]] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class EvaluationContext:
    """Context for evaluation operations."""
    expected_outputs: Optional[List[str]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    benchmark_name: Optional[str] = None
    evaluation_mode: EvaluationMode = EvaluationMode.DEMO
    custom_parameters: Optional[Dict[str, Any]] = None


@dataclass
class EvaluationConfig:
    """Configuration for evaluation operations."""
    mode: EvaluationMode = EvaluationMode.DEMO
    sample_count: int = 5
    timeout_seconds: int = 300
    parallel_processing: bool = True
    max_workers: int = 4
    cache_enabled: bool = True
    custom_metrics: Optional[List[str]] = None
    benchmark_name: Optional[str] = None


@dataclass
class EvaluationResults:
    """Results of an evaluation operation."""
    agent_name: str
    evaluation_mode: EvaluationMode
    results: List[MetricResults]
    summary_metrics: Dict[str, float]
    timestamp: datetime
    duration: float
    benchmark_name: Optional[str] = None
    total_evaluations: int = 0
    success_rate: float = 0.0
    error_count: int = 0
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Calculate derived fields after initialization."""
        self.total_evaluations = len(self.results)
        if self.total_evaluations > 0:
            self.success_rate = sum(1 for r in self.results if r.metrics) / self.total_evaluations
            self.error_count = self.total_evaluations - int(self.success_rate * self.total_evaluations)


@dataclass
class SampleData:
    """Sample data for evaluation."""
    input_text: str
    expected_output: Optional[str] = None
    context: Optional[Dict[str, Any]] = None
    difficulty: Optional[str] = None  # "easy", "medium", "hard"
    category: Optional[str] = None


@dataclass
class PublicBenchmark:
    """Publicly available benchmark definition."""
    name: str
    source: str
    format: str
    metrics: List[str]
    description: str = ""
    version: str = "latest"
    license: str = "varies"
    citation: str = ""

@dataclass
class BenchmarkDefinition:
    """Definition of a benchmark."""
    name: str
    description: str
    samples: List[SampleData]
    metrics: List[str]
    evaluation_criteria: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
    benchmark_type: str = "predefined"  # "public", "predefined", "custom"


@dataclass
class EvaluationError:
    """Error that occurred during evaluation."""
    error_type: str
    error_message: str
    timestamp: datetime
    context: Optional[Dict[str, Any]] = None
    recoverable: bool = True
