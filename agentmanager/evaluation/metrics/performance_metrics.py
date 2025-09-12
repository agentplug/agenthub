"""
Performance metrics for evaluation.
"""

from datetime import datetime
from typing import Optional, Dict, List
from .base_metric import BaseMetric
from ..core.data_models import AgentOutput, EvaluationContext, MetricResult


class PerformanceMetrics:
    """Performance-related metric calculations."""
    
    @staticmethod
    def response_time(
        start_time: datetime, 
        end_time: datetime
    ) -> float:
        """Calculate response time in seconds."""
        return (end_time - start_time).total_seconds()
    
    @staticmethod
    def throughput(
        request_count: int, 
        time_window: float
    ) -> float:
        """Calculate requests per second."""
        return request_count / time_window if time_window > 0 else 0.0
    
    @staticmethod
    def resource_usage(
        cpu_usage: float, 
        memory_usage: float, 
        disk_usage: float
    ) -> Dict[str, float]:
        """Calculate resource utilization metrics."""
        return {
            "cpu_usage": cpu_usage,
            "memory_usage": memory_usage,
            "disk_usage": disk_usage
        }
    
    @staticmethod
    def latency_percentiles(
        response_times: list, 
        percentiles: list = [50, 90, 95, 99]
    ) -> Dict[float, float]:
        """Calculate latency percentiles."""
        if not response_times:
            return {p: 0.0 for p in percentiles}
        
        sorted_times = sorted(response_times)
        result = {}
        
        for p in percentiles:
            idx = int((p / 100) * (len(sorted_times) - 1))
            result[p] = sorted_times[idx]
        
        return result
    
    @staticmethod
    def error_rate(
        total_requests: int, 
        error_requests: int
    ) -> float:
        """Calculate error rate percentage."""
        return (error_requests / total_requests * 100) if total_requests > 0 else 0.0


class ResponseTimeMetric(BaseMetric):
    """Response time metric implementation."""
    
    def __init__(self, config=None, time_unit: str = "seconds"):
        """Initialize response time metric."""
        super().__init__(config)
        self.time_unit = time_unit
    
    def calculate(
        self, 
        agent_output: AgentOutput, 
        context: Optional[EvaluationContext] = None
    ) -> MetricResult:
        """Calculate response time."""
        if not self.validate_input(agent_output):
            raise ValueError("Invalid agent output for response time")
        
        # Get timing information from metadata or context
        start_time = self._get_start_time(agent_output, context)
        end_time = self._get_end_time(agent_output, context)
        
        if not start_time or not end_time:
            return MetricResult(
                metric_type="performance",
                value=0.0,
                metadata={"error": "Timing information not available"}
            )
        
        # Calculate response time
        response_time = PerformanceMetrics.response_time(start_time, end_time)
        
        # Convert to milliseconds if needed
        if self.time_unit == "milliseconds":
            response_time *= 1000
        
        return MetricResult(
            metric_type="performance",
            value=response_time,
            metadata={
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "time_unit": self.time_unit
            }
        )
    
    def _get_start_time(self, agent_output: AgentOutput, context: Optional[EvaluationContext]) -> Optional[datetime]:
        """Get start time from agent output or context."""
        if hasattr(agent_output, 'metadata') and agent_output.metadata:
            start_time = agent_output.metadata.get('start_time')
            if isinstance(start_time, str):
                return datetime.fromisoformat(start_time)
            elif isinstance(start_time, datetime):
                return start_time
        
        if context and hasattr(context, 'start_time'):
            return context.start_time
        
        return None
    
    def _get_end_time(self, agent_output: AgentOutput, context: Optional[EvaluationContext]) -> Optional[datetime]:
        """Get end time from agent output or context."""
        if hasattr(agent_output, 'metadata') and agent_output.metadata:
            end_time = agent_output.metadata.get('end_time')
            if isinstance(end_time, str):
                return datetime.fromisoformat(end_time)
            elif isinstance(end_time, datetime):
                return end_time
        
        if context and hasattr(context, 'end_time'):
            return context.end_time
        
        return agent_output.timestamp
    
    def validate_input(self, agent_output: AgentOutput) -> bool:
        """Validate input for response time calculation."""
        return (
            hasattr(agent_output, 'timestamp') and 
            agent_output.timestamp is not None
        )


class ThroughputMetric(BaseMetric):
    """Throughput metric implementation."""
    
    def __init__(self, config=None, time_window: float = 60.0):
        """Initialize throughput metric."""
        super().__init__(config)
        self.time_window = time_window
    
    def calculate(
        self, 
        agent_output: AgentOutput, 
        context: Optional[EvaluationContext] = None
    ) -> MetricResult:
        """Calculate throughput."""
        if not self.validate_input(agent_output):
            raise ValueError("Invalid agent output for throughput")
        
        # This is a simplified implementation
        # In practice, throughput would be calculated across multiple requests
        throughput = 1.0 / self.time_window  # 1 request per time window
        
        return MetricResult(
            metric_type="performance",
            value=throughput,
            metadata={
                "time_window": self.time_window,
                "unit": "requests_per_second"
            }
        )
    
    def validate_input(self, agent_output: AgentOutput) -> bool:
        """Validate input for throughput calculation."""
        return True  # Throughput can be calculated for any output
