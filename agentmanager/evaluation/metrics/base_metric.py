"""
Base metric class for evaluation metrics.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from ..core.data_models import AgentOutput, EvaluationContext, MetricResult


@dataclass
class MetricConfig:
    """Configuration for metric calculations."""
    cache_enabled: bool = True
    parallel_processing: bool = True
    max_workers: int = 4
    timeout_seconds: int = 300
    memory_limit_mb: int = 1024


class BaseMetric(ABC):
    """Abstract base class for all metrics."""
    
    def __init__(self, config: Optional[MetricConfig] = None):
        """Initialize metric with configuration."""
        self.config = config or MetricConfig()
        self._cache = {} if self.config.cache_enabled else None
    
    @abstractmethod
    def calculate(
        self, 
        agent_output: AgentOutput, 
        context: Optional[EvaluationContext] = None
    ) -> MetricResult:
        """Calculate the metric value."""
        pass
    
    @abstractmethod
    def validate_input(self, agent_output: AgentOutput) -> bool:
        """Validate input data for metric calculation."""
        pass
    
    def normalize(self, value: float) -> float:
        """Normalize metric value to [0, 1] range."""
        return max(0.0, min(1.0, value))
    
    def aggregate(self, values: List[float], method: str = "mean") -> float:
        """Aggregate multiple metric values."""
        if not values:
            return 0.0
        
        if method == "mean":
            return sum(values) / len(values)
        elif method == "median":
            sorted_values = sorted(values)
            n = len(sorted_values)
            return (sorted_values[n//2-1] + sorted_values[n//2]) / 2 if n % 2 == 0 else sorted_values[n//2]
        elif method == "max":
            return max(values)
        elif method == "min":
            return min(values)
        else:
            raise ValueError(f"Unknown aggregation method: {method}")
    
    def _get_cached_result(self, key: str) -> Optional[float]:
        """Get cached result if available."""
        if self._cache and key in self._cache:
            return self._cache[key]
        return None
    
    def _cache_result(self, key: str, value: float):
        """Cache result for future use."""
        if self._cache is not None:
            self._cache[key] = value
