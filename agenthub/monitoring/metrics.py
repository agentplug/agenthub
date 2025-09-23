"""Performance monitoring and metrics collection."""

import threading
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any


@dataclass
class MetricPoint:
    """A single metric data point."""

    timestamp: datetime
    value: float
    tags: dict[str, str] = field(default_factory=dict)


@dataclass
class ToolExecutionMetric:
    """Metrics for tool execution."""

    tool_name: str
    agent_id: str
    execution_time: float
    success: bool
    error_type: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)


class MetricsCollector:
    """Collects and stores performance metrics."""

    def __init__(self, max_metrics: int = 10000) -> None:
        """Initialize metrics collector.

        Args:
            max_metrics: Maximum number of metrics to keep in memory
        """
        self.max_metrics = max_metrics
        self._metrics: dict[str, deque] = defaultdict(lambda: deque(maxlen=max_metrics))
        self._tool_executions: list[ToolExecutionMetric] = []
        self._lock = threading.Lock()

    def record_metric(
        self, name: str, value: float, tags: dict[str, str] | None = None
    ) -> None:
        """Record a metric value.

        Args:
            name: Metric name
            value: Metric value
            tags: Optional tags for the metric
        """
        with self._lock:
            metric_point = MetricPoint(
                timestamp=datetime.now(), value=value, tags=tags or {}
            )
            self._metrics[name].append(metric_point)

    def record_tool_execution(
        self,
        tool_name: str,
        agent_id: str,
        execution_time: float,
        success: bool,
        error_type: str | None = None,
    ) -> None:
        """Record a tool execution metric.

        Args:
            tool_name: Name of the tool executed
            agent_id: ID of the agent that executed the tool
            execution_time: Time taken to execute the tool
            success: Whether the execution was successful
            error_type: Type of error if execution failed
        """
        with self._lock:
            metric = ToolExecutionMetric(
                tool_name=tool_name,
                agent_id=agent_id,
                execution_time=execution_time,
                success=success,
                error_type=error_type,
            )
            self._tool_executions.append(metric)

            # Keep only recent metrics
            if len(self._tool_executions) > self.max_metrics:
                self._tool_executions = self._tool_executions[-self.max_metrics :]

    def get_metric_stats(
        self, name: str, duration: timedelta | None = None
    ) -> dict[str, Any]:
        """Get statistics for a metric.

        Args:
            name: Metric name
            duration: Optional duration to filter metrics

        Returns:
            Dictionary with metric statistics
        """
        with self._lock:
            if name not in self._metrics:
                return {}

            metrics = list(self._metrics[name])

            if duration:
                cutoff = datetime.now() - duration
                metrics = [m for m in metrics if m.timestamp >= cutoff]

            if not metrics:
                return {}

            values = [m.value for m in metrics]

            return {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "latest": values[-1] if values else None,
            }

    def get_tool_usage_stats(self, duration: timedelta | None = None) -> dict[str, Any]:
        """Get tool usage statistics.

        Args:
            duration: Optional duration to filter metrics

        Returns:
            Dictionary with tool usage statistics
        """
        with self._lock:
            if duration:
                cutoff = datetime.now() - duration
                metrics = [m for m in self._tool_executions if m.timestamp >= cutoff]
            else:
                metrics = self._tool_executions

            if not metrics:
                return {}

            # Group by tool name
            tool_stats: dict[str, dict[str, Any]] = defaultdict(
                lambda: {"count": 0, "success_count": 0, "total_time": 0.0}
            )

            for metric in metrics:
                tool_stats[metric.tool_name]["count"] += 1
                tool_stats[metric.tool_name]["total_time"] += metric.execution_time
                if metric.success:
                    tool_stats[metric.tool_name]["success_count"] += 1

            # Calculate averages and success rates
            result = {}
            for tool_name, stats in tool_stats.items():
                result[tool_name] = {
                    "total_executions": stats["count"],
                    "success_rate": (
                        stats["success_count"] / stats["count"]
                        if stats["count"] > 0
                        else 0
                    ),
                    "avg_execution_time": (
                        stats["total_time"] / stats["count"]
                        if stats["count"] > 0
                        else 0
                    ),
                    "total_execution_time": stats["total_time"],
                }

            return result

    def get_agent_stats(self, duration: timedelta | None = None) -> dict[str, Any]:
        """Get agent usage statistics.

        Args:
            duration: Optional duration to filter metrics

        Returns:
            Dictionary with agent usage statistics
        """
        with self._lock:
            if duration:
                cutoff = datetime.now() - duration
                metrics = [m for m in self._tool_executions if m.timestamp >= cutoff]
            else:
                metrics = self._tool_executions

            if not metrics:
                return {}

            # Group by agent ID
            agent_stats: dict[str, dict[str, Any]] = defaultdict(
                lambda: {
                    "count": 0,
                    "success_count": 0,
                    "total_time": 0.0,
                    "tools_used": set(),
                }
            )

            for metric in metrics:
                agent_stats[metric.agent_id]["count"] += 1
                agent_stats[metric.agent_id]["total_time"] += metric.execution_time
                agent_stats[metric.agent_id]["tools_used"].add(metric.tool_name)
                if metric.success:
                    agent_stats[metric.agent_id]["success_count"] += 1

            # Calculate averages and success rates
            result = {}
            for agent_id, stats in agent_stats.items():
                result[agent_id] = {
                    "total_executions": stats["count"],
                    "success_rate": (
                        stats["success_count"] / stats["count"]
                        if stats["count"] > 0
                        else 0
                    ),
                    "avg_execution_time": (
                        stats["total_time"] / stats["count"]
                        if stats["count"] > 0
                        else 0
                    ),
                    "total_execution_time": stats["total_time"],
                    "unique_tools_used": len(stats["tools_used"]),
                    "tools_used": list(stats["tools_used"]),
                }

            return result

    def clear_metrics(self) -> None:
        """Clear all metrics."""
        with self._lock:
            self._metrics.clear()
            self._tool_executions.clear()


# Global metrics collector
_metrics_collector: MetricsCollector | None = None


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector."""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = MetricsCollector()
    return _metrics_collector


def record_metric(name: str, value: float, tags: dict[str, str] | None = None) -> None:
    """Record a metric value."""
    get_metrics_collector().record_metric(name, value, tags)


def record_tool_execution(
    tool_name: str,
    agent_id: str,
    execution_time: float,
    success: bool,
    error_type: str | None = None,
) -> None:
    """Record a tool execution metric."""
    get_metrics_collector().record_tool_execution(
        tool_name, agent_id, execution_time, success, error_type
    )
