"""
Adaptive resource management for AgentHub monitoring

Provides intelligent resource management with adaptive behavior,
memory management, and performance optimization for monitoring systems.
"""

import os
import psutil
import statistics
import threading
import time
from collections import deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Callable

from .config import MonitoringConfig


@dataclass
class ResourceMetrics:
    """Resource usage metrics"""
    cpu_usage: float
    memory_usage: float
    memory_available: float
    log_count: int
    analysis_duration: float
    timestamp: float


class AdaptiveResourceManager:
    """
    Adaptive resource manager for monitoring system
    
    Provides intelligent resource management with:
    - Adaptive analysis frequency based on log volume and content
    - Memory management and cleanup
    - Performance optimization
    - Resource monitoring and alerting
    """

    def __init__(self, config: MonitoringConfig):
        """
        Initialize Adaptive Resource Manager
        
        Args:
            config: Monitoring configuration
        """
        self.config = config
        self.max_memory_bytes = config.max_memory_mb * 1024 * 1024
        self.max_logs = config.max_logs
        self.analysis_interval = config.analysis_interval
        self.adaptive_analysis = config.adaptive_analysis
        
        # Resource tracking
        self.resource_metrics = deque(maxlen=100)
        self.analysis_history = deque(maxlen=50)
        self.performance_trends = {
            'cpu_trend': deque(maxlen=20),
            'memory_trend': deque(maxlen=20),
            'analysis_duration_trend': deque(maxlen=20)
        }
        
        # Adaptive behavior
        self.adaptive_frequency = self.analysis_interval
        self.last_analysis_time = 0
        self.analysis_skip_count = 0
        self.performance_thresholds = {
            'cpu_warning': 80.0,
            'cpu_critical': 95.0,
            'memory_warning': 85.0,
            'memory_critical': 95.0,
            'analysis_duration_warning': 2.0,
            'analysis_duration_critical': 5.0
        }
        
        # Thread safety
        self._lock = threading.Lock()
        
        # Callbacks for resource events
        self.resource_callbacks = {
            'memory_warning': [],
            'memory_critical': [],
            'cpu_warning': [],
            'cpu_critical': [],
            'analysis_slow': []
        }

    def should_analyze_logs(
        self, 
        new_logs: List[str], 
        last_analysis_time: float,
        force: bool = False
    ) -> bool:
        """
        Determine if logs should be analyzed based on adaptive criteria
        
        Args:
            new_logs: New log lines since last analysis
            last_analysis_time: Timestamp of last analysis
            force: Force analysis regardless of adaptive criteria
            
        Returns:
            True if logs should be analyzed
        """
        if force:
            return True
        
        current_time = time.time()
        time_since_last = current_time - last_analysis_time
        
        # Always analyze if enough time has passed
        if time_since_last >= self.adaptive_frequency:
            return True
        
        # Adaptive analysis based on log content and volume
        if self.adaptive_analysis:
            return self._should_analyze_adaptive(new_logs, time_since_last)
        
        return False

    def _should_analyze_adaptive(self, new_logs: List[str], time_since_last: float) -> bool:
        """Adaptive analysis based on log content and volume"""
        if not new_logs:
            return False
        
        # Analyze immediately if errors detected (error priority)
        if self.config.error_priority:
            error_indicators = ['error', 'exception', 'failed', 'traceback', 'critical']
            if any(any(indicator in log.lower() for indicator in error_indicators) 
                   for log in new_logs):
                return True
        
        # Analyze if high volume of logs
        if len(new_logs) > 50:
            return True
        
        # Analyze if significant time has passed
        if time_since_last > self.adaptive_frequency * 0.5:
            return True
        
        # Skip if logs are mostly repetitive
        if self._logs_are_repetitive(new_logs):
            self.analysis_skip_count += 1
            return False
        
        # Check resource constraints
        if self._is_resource_constrained():
            return False
        
        return True

    def _logs_are_repetitive(self, new_logs: List[str]) -> bool:
        """Check if logs are mostly repetitive (like progress updates)"""
        if len(new_logs) < 5:
            return False
        
        # Count unique log patterns
        unique_patterns = set()
        for log in new_logs:
            pattern = self._extract_log_pattern(log)
            unique_patterns.add(pattern)
        
        # If more than 80% of logs are the same pattern, consider repetitive
        repetition_ratio = len(unique_patterns) / len(new_logs)
        return repetition_ratio < 0.2

    def _extract_log_pattern(self, log: str) -> str:
        """Extract pattern from log line, removing variable parts"""
        import re
        # Remove timestamps
        pattern = re.sub(r'\[\d{2}:\d{2}:\d{2}\]', '[TIME]', log)
        # Remove IDs and numbers
        pattern = re.sub(r'\b\d+\b', 'N', pattern)
        # Remove file paths
        pattern = re.sub(r'/[^\s]+', '/PATH', pattern)
        # Remove variable content in brackets
        pattern = re.sub(r'\[[^\]]*\]', '[VAR]', pattern)
        return pattern

    def _is_resource_constrained(self) -> bool:
        """Check if system is resource constrained"""
        try:
            current_metrics = self._get_current_metrics()
            
            # Check CPU usage
            if current_metrics.cpu_usage > self.performance_thresholds['cpu_warning']:
                return True
            
            # Check memory usage
            if current_metrics.memory_usage > self.performance_thresholds['memory_warning']:
                return True
            
            return False
        except Exception:
            return False

    def record_analysis_performance(self, analysis_duration: float, log_volume: int):
        """Record analysis performance for adaptive behavior"""
        with self._lock:
            self.analysis_history.append({
                'duration': analysis_duration,
                'log_volume': log_volume,
                'timestamp': time.time()
            })
            
            # Update performance trends
            self.performance_trends['analysis_duration_trend'].append(analysis_duration)
            
            # Adjust adaptive frequency based on performance
            self._adjust_adaptive_frequency(analysis_duration, log_volume)
            
            # Check for performance issues
            self._check_performance_issues(analysis_duration)

    def _adjust_adaptive_frequency(self, analysis_duration: float, log_volume: int):
        """Adjust analysis frequency based on performance"""
        # If analysis is taking too long, slow down
        if analysis_duration > self.performance_thresholds['analysis_duration_warning']:
            self.adaptive_frequency = min(5.0, self.adaptive_frequency * 1.2)
        elif analysis_duration < 0.1 and log_volume < 20:
            # If analysis is very fast and low volume, speed up
            self.adaptive_frequency = max(0.5, self.adaptive_frequency * 0.9)
        
        # Adjust based on log volume
        if log_volume > 100:
            self.adaptive_frequency = min(3.0, self.adaptive_frequency * 1.1)
        elif log_volume < 10:
            self.adaptive_frequency = max(1.0, self.adaptive_frequency * 0.95)
        
        # Ensure frequency is within reasonable bounds
        self.adaptive_frequency = max(0.5, min(10.0, self.adaptive_frequency))

    def _check_performance_issues(self, analysis_duration: float):
        """Check for performance issues and trigger callbacks"""
        # Check analysis duration
        if analysis_duration > self.performance_thresholds['analysis_duration_critical']:
            self._trigger_callbacks('analysis_slow', {
                'duration': analysis_duration,
                'threshold': self.performance_thresholds['analysis_duration_critical']
            })

    def manage_log_buffer(self, logs: List[str]) -> List[str]:
        """Manage log buffer size and memory usage"""
        current_memory = self._estimate_memory_usage(logs)
        
        # If approaching memory limit, start aggressive cleanup
        if current_memory > self.max_memory_bytes * 0.8:
            logs = self._aggressive_log_cleanup(logs)
            self._trigger_callbacks('memory_warning', {
                'memory_usage': current_memory,
                'memory_limit': self.max_memory_bytes
            })
        elif len(logs) > self.max_logs * 0.8:
            logs = self._rotate_logs(logs)
        
        return logs

    def _estimate_memory_usage(self, logs: List[str]) -> int:
        """Estimate memory usage of log buffer"""
        total_chars = sum(len(log) for log in logs)
        # Rough estimate: each character is ~1 byte, plus overhead
        return int(total_chars * 1.5)

    def _rotate_logs(self, logs: List[str]) -> List[str]:
        """Rotate logs, keeping only recent ones"""
        if len(logs) <= self.max_logs:
            return logs
        
        # Keep the most recent logs
        keep_count = int(self.max_logs * 0.7)  # Keep 70% of max
        rotated_logs = logs[-keep_count:]
        
        # Add a rotation marker
        rotated_logs.insert(0, f"[{time.strftime('%H:%M:%S')}] [SYSTEM] Log rotation: {len(logs) - keep_count} lines archived")
        
        return rotated_logs

    def _aggressive_log_cleanup(self, logs: List[str]) -> List[str]:
        """Aggressive cleanup when memory is low"""
        # Keep only error logs and recent logs
        error_logs = [log for log in logs if any(word in log.lower() 
                    for word in ['error', 'exception', 'failed', 'traceback', 'critical'])]
        
        # Keep recent logs (last 20%)
        recent_logs = logs[-int(len(logs) * 0.2):]
        
        # Combine and deduplicate
        cleaned_logs = list(dict.fromkeys(error_logs + recent_logs))
        
        # Add cleanup marker
        cleaned_logs.insert(0, f"[{time.strftime('%H:%M:%S')}] [SYSTEM] Aggressive cleanup: {len(logs) - len(cleaned_logs)} lines removed")
        
        self._trigger_callbacks('memory_critical', {
            'original_count': len(logs),
            'cleaned_count': len(cleaned_logs),
            'removed_count': len(logs) - len(cleaned_logs)
        })
        
        return cleaned_logs

    def _get_current_metrics(self) -> ResourceMetrics:
        """Get current system resource metrics"""
        try:
            # Get system metrics
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory_info = psutil.virtual_memory()
            memory_usage = memory_info.percent
            memory_available = memory_info.available
            
            # Get process metrics
            process = psutil.Process()
            process_memory = process.memory_info().rss
            
            return ResourceMetrics(
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                memory_available=memory_available,
                log_count=0,  # Will be set by caller
                analysis_duration=0.0,  # Will be set by caller
                timestamp=time.time()
            )
        except Exception:
            # Fallback if psutil is not available
            return ResourceMetrics(
                cpu_usage=0.0,
                memory_usage=0.0,
                memory_available=0,
                log_count=0,
                analysis_duration=0.0,
                timestamp=time.time()
            )

    def update_resource_metrics(self, log_count: int, analysis_duration: float):
        """Update resource metrics"""
        with self._lock:
            metrics = self._get_current_metrics()
            metrics.log_count = log_count
            metrics.analysis_duration = analysis_duration
            
            self.resource_metrics.append(metrics)
            
            # Update trends
            self.performance_trends['cpu_trend'].append(metrics.cpu_usage)
            self.performance_trends['memory_trend'].append(metrics.memory_usage)
            self.performance_trends['analysis_duration_trend'].append(analysis_duration)
            
            # Check for resource warnings
            self._check_resource_warnings(metrics)

    def _check_resource_warnings(self, metrics: ResourceMetrics):
        """Check for resource warnings and trigger callbacks"""
        # CPU warnings
        if metrics.cpu_usage > self.performance_thresholds['cpu_critical']:
            self._trigger_callbacks('cpu_critical', {'cpu_usage': metrics.cpu_usage})
        elif metrics.cpu_usage > self.performance_thresholds['cpu_warning']:
            self._trigger_callbacks('cpu_warning', {'cpu_usage': metrics.cpu_usage})
        
        # Memory warnings
        if metrics.memory_usage > self.performance_thresholds['memory_critical']:
            self._trigger_callbacks('memory_critical', {'memory_usage': metrics.memory_usage})
        elif metrics.memory_usage > self.performance_thresholds['memory_warning']:
            self._trigger_callbacks('memory_warning', {'memory_usage': metrics.memory_usage})

    def _trigger_callbacks(self, event_type: str, data: Dict[str, Any]):
        """Trigger callbacks for resource events"""
        for callback in self.resource_callbacks.get(event_type, []):
            try:
                callback(event_type, data)
            except Exception as e:
                print(f"Error in resource callback: {e}")

    def add_resource_callback(self, event_type: str, callback: Callable[[str, Dict], None]):
        """Add callback for resource events"""
        if event_type in self.resource_callbacks:
            self.resource_callbacks[event_type].append(callback)

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get current performance summary"""
        with self._lock:
            if not self.resource_metrics:
                return {}
            
            recent_metrics = list(self.resource_metrics)[-10:]  # Last 10 measurements
            
            cpu_usage = [m.cpu_usage for m in recent_metrics]
            memory_usage = [m.memory_usage for m in recent_metrics]
            analysis_durations = [m.analysis_duration for m in recent_metrics]
            
            return {
                'current_cpu_usage': cpu_usage[-1] if cpu_usage else 0,
                'avg_cpu_usage': statistics.mean(cpu_usage) if cpu_usage else 0,
                'current_memory_usage': memory_usage[-1] if memory_usage else 0,
                'avg_memory_usage': statistics.mean(memory_usage) if memory_usage else 0,
                'avg_analysis_duration': statistics.mean(analysis_durations) if analysis_durations else 0,
                'adaptive_frequency': self.adaptive_frequency,
                'analysis_skip_count': self.analysis_skip_count,
                'total_measurements': len(self.resource_metrics),
                'performance_trends': {
                    'cpu_trend': list(self.performance_trends['cpu_trend']),
                    'memory_trend': list(self.performance_trends['memory_trend']),
                    'analysis_duration_trend': list(self.performance_trends['analysis_duration_trend'])
                }
            }

    def get_resource_insights(self) -> List[str]:
        """Get actionable resource insights"""
        insights = []
        summary = self.get_performance_summary()
        
        if not summary:
            return insights
        
        # CPU insights
        if summary['avg_cpu_usage'] > self.performance_thresholds['cpu_warning']:
            insights.append(f"⚠️  High CPU usage: {summary['avg_cpu_usage']:.1f}%")
        
        # Memory insights
        if summary['avg_memory_usage'] > self.performance_thresholds['memory_warning']:
            insights.append(f"💾 High memory usage: {summary['avg_memory_usage']:.1f}%")
        
        # Analysis performance insights
        if summary['avg_analysis_duration'] > self.performance_thresholds['analysis_duration_warning']:
            insights.append(f"🐌 Slow analysis: {summary['avg_analysis_duration']:.2f}s average")
        
        # Adaptive behavior insights
        if self.analysis_skip_count > 10:
            insights.append(f"⏭️  Skipped {self.analysis_skip_count} analyses due to adaptive behavior")
        
        if self.adaptive_frequency > self.analysis_interval * 2:
            insights.append(f"🔄 Analysis frequency reduced to {self.adaptive_frequency:.1f}s due to performance")
        
        return insights

    def reset_adaptive_behavior(self):
        """Reset adaptive behavior to defaults"""
        with self._lock:
            self.adaptive_frequency = self.analysis_interval
            self.analysis_skip_count = 0
            self.analysis_history.clear()
            self.performance_trends = {
                'cpu_trend': deque(maxlen=20),
                'memory_trend': deque(maxlen=20),
                'analysis_duration_trend': deque(maxlen=20)
            }

    def configure_performance_thresholds(self, thresholds: Dict[str, float]):
        """Configure performance thresholds"""
        with self._lock:
            self.performance_thresholds.update(thresholds)
