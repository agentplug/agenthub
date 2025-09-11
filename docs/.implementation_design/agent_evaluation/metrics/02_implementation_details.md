# Metrics Engine - Implementation Details

**Document Type**: Implementation Details  
**Author**: Assistant  
**Date Created**: 2025-06-28  
**Last Updated**: 2025-06-28  
**Status**: Draft  
**Stakeholders**: Developers, Technical Architects, QA Team  
**Component**: Metrics Engine  
**Iteration Count**: 1  

## Overview

This document provides detailed implementation specifications for the Metrics Engine, including class hierarchies, algorithms, data structures, and performance optimizations.

## Class Hierarchy

### 1. Base Classes

#### BaseMetric
```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MetricConfig:
    """Configuration for metric calculations."""
    cache_enabled: bool = True
    parallel_processing: bool = True
    max_workers: int = 4
    timeout_seconds: int = 300
    memory_limit_mb: int = 1024
    custom_metrics: Optional[Dict[str, Any]] = None

class BaseMetric(ABC):
    """Abstract base class for all metrics."""
    
    def __init__(self, config: Optional[MetricConfig] = None):
        self.config = config or MetricConfig()
        self._cache = {} if self.config.cache_enabled else None
        self._validation_rules = []
        self._setup_validation_rules()
    
    @abstractmethod
    def calculate(
        self, 
        agent_output: 'AgentOutput', 
        context: Optional['EvaluationContext'] = None
    ) -> 'MetricResult':
        """Calculate the metric value."""
        pass
    
    @abstractmethod
    def validate_input(self, agent_output: 'AgentOutput') -> bool:
        """Validate input data for metric calculation."""
        pass
    
    def normalize(self, value: float) -> float:
        """Normalize metric value to [0, 1] range."""
        # Default implementation - can be overridden
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
    
    def _setup_validation_rules(self):
        """Setup validation rules for the metric."""
        pass
    
    def _get_cached_result(self, key: str) -> Optional[float]:
        """Get cached result if available."""
        if self._cache and key in self._cache:
            return self._cache[key]
        return None
    
    def _cache_result(self, key: str, value: float):
        """Cache result for future use."""
        if self._cache is not None:
            self._cache[key] = value
```

#### MetricCalculator
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple
import hashlib
import json

class MetricCalculator:
    """Core metric calculation engine."""
    
    def __init__(self, config: Optional[MetricConfig] = None):
        self.config = config or MetricConfig()
        self._metrics_registry = {}
        self._executor = ThreadPoolExecutor(max_workers=self.config.max_workers)
        self._setup_metrics_registry()
    
    def _setup_metrics_registry(self):
        """Setup registry of available metrics."""
        from .accuracy import ExactMatchMetric, SemanticSimilarityMetric
        from .quality import RelevanceScoreMetric, CompletenessScoreMetric
        from .performance import ResponseTimeMetric, ThroughputMetric
        from .reliability import ConsistencyScoreMetric, StabilityScoreMetric
        
        self._metrics_registry = {
            # Accuracy metrics
            "exact_match": ExactMatchMetric(self.config),
            "semantic_similarity": SemanticSimilarityMetric(self.config),
            "f1_score": F1ScoreMetric(self.config),
            "bleu_score": BLEUScoreMetric(self.config),
            "rouge_score": ROUGEScoreMetric(self.config),
            
            # Quality metrics
            "relevance_score": RelevanceScoreMetric(self.config),
            "completeness_score": CompletenessScoreMetric(self.config),
            "coherence_score": CoherenceScoreMetric(self.config),
            "clarity_score": ClarityScoreMetric(self.config),
            "factual_accuracy": FactualAccuracyMetric(self.config),
            "safety_score": SafetyScoreMetric(self.config),
            
            # Performance metrics
            "response_time": ResponseTimeMetric(self.config),
            "throughput": ThroughputMetric(self.config),
            "resource_usage": ResourceUsageMetric(self.config),
            "error_rate": ErrorRateMetric(self.config),
            
            # Reliability metrics
            "consistency_score": ConsistencyScoreMetric(self.config),
            "stability_score": StabilityScoreMetric(self.config),
            "robustness_score": RobustnessScoreMetric(self.config),
            "reproducibility_score": ReproducibilityScoreMetric(self.config),
        }
    
    def calculate_metrics(
        self, 
        agent_outputs: List['AgentOutput'], 
        metric_types: List[str],
        context: Optional['EvaluationContext'] = None
    ) -> List['MetricResults']:
        """Calculate specified metrics for agent outputs."""
        # Validate inputs
        self._validate_inputs(agent_outputs, metric_types)
        
        # Calculate metrics
        if self.config.parallel_processing and len(agent_outputs) > 1:
            return self._calculate_metrics_parallel(agent_outputs, metric_types, context)
        else:
            return self._calculate_metrics_sequential(agent_outputs, metric_types, context)
    
    def _calculate_metrics_parallel(
        self, 
        agent_outputs: List['AgentOutput'], 
        metric_types: List[str],
        context: Optional['EvaluationContext'] = None
    ) -> List['MetricResults']:
        """Calculate metrics in parallel."""
        results = []
        future_to_output = {}
        
        # Submit tasks
        for i, agent_output in enumerate(agent_outputs):
            future = self._executor.submit(
                self._calculate_single_output_metrics,
                agent_output, metric_types, context
            )
            future_to_output[future] = (i, agent_output)
        
        # Collect results
        for future in as_completed(future_to_output):
            try:
                result = future.result(timeout=self.config.timeout_seconds)
                results.append(result)
            except Exception as e:
                # Handle individual failures gracefully
                i, agent_output = future_to_output[future]
                error_result = self._create_error_result(agent_output, metric_types, str(e))
                results.append(error_result)
        
        return results
    
    def _calculate_metrics_sequential(
        self, 
        agent_outputs: List['AgentOutput'], 
        metric_types: List[str],
        context: Optional['EvaluationContext'] = None
    ) -> List['MetricResults']:
        """Calculate metrics sequentially."""
        results = []
        for agent_output in agent_outputs:
            try:
                result = self._calculate_single_output_metrics(agent_output, metric_types, context)
                results.append(result)
            except Exception as e:
                error_result = self._create_error_result(agent_output, metric_types, str(e))
                results.append(error_result)
        return results
    
    def _calculate_single_output_metrics(
        self, 
        agent_output: 'AgentOutput', 
        metric_types: List[str],
        context: Optional['EvaluationContext'] = None
    ) -> 'MetricResults':
        """Calculate metrics for a single agent output."""
        metrics = {}
        
        for metric_type in metric_types:
            try:
                metric = self._get_metric(metric_type)
                result = metric.calculate(agent_output, context)
                metrics[metric_type] = result
            except Exception as e:
                # Create error result for failed metric
                error_result = MetricResult(
                    metric_type=metric_type,
                    value=0.0,
                    metadata={"error": str(e), "error_type": type(e).__name__}
                )
                metrics[metric_type] = error_result
        
        return MetricResults(
            agent_output=agent_output,
            metrics=metrics,
            timestamp=datetime.now()
        )
    
    def _get_metric(self, metric_type: str) -> BaseMetric:
        """Get metric instance by type."""
        if metric_type not in self._metrics_registry:
            raise InvalidMetricTypeError(f"Unknown metric type: {metric_type}")
        return self._metrics_registry[metric_type]
    
    def _validate_inputs(self, agent_outputs: List['AgentOutput'], metric_types: List[str]):
        """Validate input parameters."""
        if not agent_outputs:
            raise ValueError("agent_outputs cannot be empty")
        if not metric_types:
            raise ValueError("metric_types cannot be empty")
        
        for metric_type in metric_types:
            if metric_type not in self._metrics_registry:
                raise InvalidMetricTypeError(f"Unknown metric type: {metric_type}")
    
    def _create_error_result(
        self, 
        agent_output: 'AgentOutput', 
        metric_types: List[str], 
        error_message: str
    ) -> 'MetricResults':
        """Create error result for failed calculation."""
        metrics = {}
        for metric_type in metric_types:
            metrics[metric_type] = MetricResult(
                metric_type=metric_type,
                value=0.0,
                metadata={"error": error_message, "error_type": "CalculationError"}
            )
        
        return MetricResults(
            agent_output=agent_output,
            metrics=metrics,
            timestamp=datetime.now()
        )
    
    def get_available_metrics(self) -> List[str]:
        """Get list of available metric types."""
        return list(self._metrics_registry.keys())
    
    def validate_metric_type(self, metric_type: str) -> bool:
        """Validate if a metric type is supported."""
        return metric_type in self._metrics_registry
```

### 2. Accuracy Metrics Implementation

#### ExactMatchMetric
```python
import difflib
from typing import Optional

class ExactMatchMetric(BaseMetric):
    """Exact match metric calculation."""
    
    def __init__(self, config: Optional[MetricConfig] = None):
        super().__init__(config)
        self.case_sensitive = True
        self.normalize_whitespace = True
    
    def calculate(
        self, 
        agent_output: 'AgentOutput', 
        context: Optional['EvaluationContext'] = None
    ) -> 'MetricResult':
        """Calculate exact match score."""
        if not self.validate_input(agent_output):
            raise MetricValidationError("Invalid agent output for exact match")
        
        predicted = agent_output.output_text
        expected = context.expected_output if context else ""
        
        if not expected:
            return MetricResult(
                metric_type="exact_match",
                value=0.0,
                metadata={"error": "No expected output provided"}
            )
        
        # Normalize text if needed
        if self.normalize_whitespace:
            predicted = self._normalize_whitespace(predicted)
            expected = self._normalize_whitespace(expected)
        
        # Case sensitivity
        if not self.case_sensitive:
            predicted = predicted.lower()
            expected = expected.lower()
        
        # Calculate exact match
        is_exact_match = predicted == expected
        score = 1.0 if is_exact_match else 0.0
        
        return MetricResult(
            metric_type="exact_match",
            value=score,
            metadata={
                "case_sensitive": self.case_sensitive,
                "normalize_whitespace": self.normalize_whitespace,
                "predicted_length": len(predicted),
                "expected_length": len(expected)
            }
        )
    
    def validate_input(self, agent_output: 'AgentOutput') -> bool:
        """Validate input for exact match calculation."""
        return (
            hasattr(agent_output, 'output_text') and 
            agent_output.output_text is not None
        )
    
    def _normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace in text."""
        import re
        return re.sub(r'\s+', ' ', text.strip())
```

#### SemanticSimilarityMetric
```python
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class SemanticSimilarityMetric(BaseMetric):
    """Semantic similarity metric using sentence embeddings."""
    
    def __init__(self, config: Optional[MetricConfig] = None):
        super().__init__(config)
        self.model_name = "sentence-transformers/all-MiniLM-L6-v2"
        self._model = None
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model."""
        try:
            self._model = SentenceTransformer(self.model_name)
        except Exception as e:
            raise MetricCalculationError(f"Failed to load model: {e}")
    
    def calculate(
        self, 
        agent_output: 'AgentOutput', 
        context: Optional['EvaluationContext'] = None
    ) -> 'MetricResult':
        """Calculate semantic similarity score."""
        if not self.validate_input(agent_output):
            raise MetricValidationError("Invalid agent output for semantic similarity")
        
        predicted = agent_output.output_text
        expected = context.expected_output if context else ""
        
        if not expected:
            return MetricResult(
                metric_type="semantic_similarity",
                value=0.0,
                metadata={"error": "No expected output provided"}
            )
        
        try:
            # Generate embeddings
            embeddings = self._model.encode([predicted, expected])
            predicted_embedding = embeddings[0].reshape(1, -1)
            expected_embedding = embeddings[1].reshape(1, -1)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(predicted_embedding, expected_embedding)[0][0]
            
            return MetricResult(
                metric_type="semantic_similarity",
                value=float(similarity),
                metadata={
                    "model_name": self.model_name,
                    "predicted_length": len(predicted),
                    "expected_length": len(expected),
                    "embedding_dimension": len(embeddings[0])
                }
            )
        except Exception as e:
            return MetricResult(
                metric_type="semantic_similarity",
                value=0.0,
                metadata={"error": str(e), "error_type": type(e).__name__}
            )
    
    def validate_input(self, agent_output: 'AgentOutput') -> bool:
        """Validate input for semantic similarity calculation."""
        return (
            hasattr(agent_output, 'output_text') and 
            agent_output.output_text is not None and
            len(agent_output.output_text.strip()) > 0
        )
```

### 3. Quality Metrics Implementation

#### RelevanceScoreMetric
```python
import re
from typing import List, Dict
from collections import Counter

class RelevanceScoreMetric(BaseMetric):
    """Relevance score metric based on keyword overlap and semantic analysis."""
    
    def __init__(self, config: Optional[MetricConfig] = None):
        super().__init__(config)
        self.min_keyword_overlap = 0.1
        self.semantic_weight = 0.7
        self.keyword_weight = 0.3
    
    def calculate(
        self, 
        agent_output: 'AgentOutput', 
        context: Optional['EvaluationContext'] = None
    ) -> 'MetricResult':
        """Calculate relevance score."""
        if not self.validate_input(agent_output):
            raise MetricValidationError("Invalid agent output for relevance score")
        
        output_text = agent_output.output_text
        input_text = agent_output.input_text
        
        # Calculate keyword overlap
        keyword_score = self._calculate_keyword_overlap(output_text, input_text)
        
        # Calculate semantic relevance (simplified)
        semantic_score = self._calculate_semantic_relevance(output_text, input_text)
        
        # Combine scores
        relevance_score = (
            self.keyword_weight * keyword_score + 
            self.semantic_weight * semantic_score
        )
        
        return MetricResult(
            metric_type="relevance_score",
            value=relevance_score,
            metadata={
                "keyword_score": keyword_score,
                "semantic_score": semantic_score,
                "keyword_weight": self.keyword_weight,
                "semantic_weight": self.semantic_weight
            }
        )
    
    def _calculate_keyword_overlap(self, output: str, input_text: str) -> float:
        """Calculate keyword overlap between output and input."""
        # Extract keywords (simple word-based approach)
        output_words = set(self._extract_keywords(output))
        input_words = set(self._extract_keywords(input_text))
        
        if not input_words:
            return 0.0
        
        overlap = len(output_words.intersection(input_words))
        return overlap / len(input_words)
    
    def _calculate_semantic_relevance(self, output: str, input_text: str) -> float:
        """Calculate semantic relevance (simplified version)."""
        # This is a simplified implementation
        # In practice, you might use more sophisticated NLP techniques
        
        # Check for question-answer alignment
        if self._is_question(input_text) and self._is_answer(output):
            return 0.8
        
        # Check for topic alignment
        topic_score = self._calculate_topic_alignment(output, input_text)
        return topic_score
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # Simple keyword extraction (remove stop words, punctuation)
        import string
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        
        words = re.findall(r'\b\w+\b', text.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return keywords
    
    def _is_question(self, text: str) -> bool:
        """Check if text is a question."""
        return text.strip().endswith('?') or text.strip().startswith(('what', 'how', 'why', 'when', 'where', 'who'))
    
    def _is_answer(self, text: str) -> bool:
        """Check if text appears to be an answer."""
        # Simple heuristics
        answer_indicators = ["is", "are", "was", "were", "will", "can", "should", "would", "could"]
        return any(indicator in text.lower() for indicator in answer_indicators)
    
    def _calculate_topic_alignment(self, output: str, input_text: str) -> float:
        """Calculate topic alignment between output and input."""
        # Simplified topic alignment calculation
        output_words = set(self._extract_keywords(output))
        input_words = set(self._extract_keywords(input_text))
        
        if not input_words:
            return 0.0
        
        common_words = output_words.intersection(input_words)
        return len(common_words) / len(input_words)
    
    def validate_input(self, agent_output: 'AgentOutput') -> bool:
        """Validate input for relevance score calculation."""
        return (
            hasattr(agent_output, 'output_text') and 
            hasattr(agent_output, 'input_text') and
            agent_output.output_text is not None and
            agent_output.input_text is not None
        )
```

### 4. Performance Metrics Implementation

#### ResponseTimeMetric
```python
from datetime import datetime
from typing import Optional

class ResponseTimeMetric(BaseMetric):
    """Response time metric calculation."""
    
    def __init__(self, config: Optional[MetricConfig] = None):
        super().__init__(config)
        self.time_unit = "seconds"  # or "milliseconds"
    
    def calculate(
        self, 
        agent_output: 'AgentOutput', 
        context: Optional['EvaluationContext'] = None
    ) -> 'MetricResult':
        """Calculate response time."""
        if not self.validate_input(agent_output):
            raise MetricValidationError("Invalid agent output for response time")
        
        # Get timing information from metadata or context
        start_time = self._get_start_time(agent_output, context)
        end_time = self._get_end_time(agent_output, context)
        
        if not start_time or not end_time:
            return MetricResult(
                metric_type="response_time",
                value=0.0,
                metadata={"error": "Timing information not available"}
            )
        
        # Calculate response time
        response_time = (end_time - start_time).total_seconds()
        
        # Convert to milliseconds if needed
        if self.time_unit == "milliseconds":
            response_time *= 1000
        
        return MetricResult(
            metric_type="response_time",
            value=response_time,
            metadata={
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "time_unit": self.time_unit
            }
        )
    
    def _get_start_time(self, agent_output: 'AgentOutput', context: Optional['EvaluationContext']) -> Optional[datetime]:
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
    
    def _get_end_time(self, agent_output: 'AgentOutput', context: Optional['EvaluationContext']) -> Optional[datetime]:
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
    
    def validate_input(self, agent_output: 'AgentOutput') -> bool:
        """Validate input for response time calculation."""
        return (
            hasattr(agent_output, 'timestamp') and 
            agent_output.timestamp is not None
        )
```

### 5. Aggregation Implementation

#### MetricAggregator
```python
import statistics
from typing import Dict, List, Optional, Tuple
import numpy as np

class MetricAggregator:
    """Metric aggregation and summary statistics."""
    
    def __init__(self, aggregation_methods: Optional[List[str]] = None):
        self.aggregation_methods = aggregation_methods or [
            "mean", "median", "mode", "std", "min", "max", "percentiles"
        ]
    
    def aggregate(
        self, 
        metric_results: List['MetricResult'], 
        method: str = "mean"
    ) -> 'AggregatedMetric':
        """Aggregate metric results using specified method."""
        if not metric_results:
            raise ValueError("Cannot aggregate empty metric results")
        
        values = [result.value for result in metric_results]
        metric_type = metric_results[0].metric_type
        
        # Validate all results have same metric type
        for result in metric_results[1:]:
            if result.metric_type != metric_type:
                raise ValueError("All metric results must have same metric type")
        
        # Calculate aggregated value
        if method == "mean":
            aggregated_value = statistics.mean(values)
        elif method == "median":
            aggregated_value = statistics.median(values)
        elif method == "mode":
            try:
                aggregated_value = statistics.mode(values)
            except statistics.StatisticsError:
                # If no unique mode, use median
                aggregated_value = statistics.median(values)
        elif method == "max":
            aggregated_value = max(values)
        elif method == "min":
            aggregated_value = min(values)
        else:
            raise ValueError(f"Unknown aggregation method: {method}")
        
        # Calculate additional statistics
        std_deviation = statistics.stdev(values) if len(values) > 1 else 0.0
        min_value = min(values)
        max_value = max(values)
        
        return AggregatedMetric(
            metric_type=metric_type,
            aggregated_value=aggregated_value,
            aggregation_method=method,
            count=len(values),
            min_value=min_value,
            max_value=max_value,
            std_deviation=std_deviation
        )
    
    def get_summary_statistics(
        self, 
        metric_results: List['MetricResult']
    ) -> 'SummaryStatistics':
        """Get comprehensive summary statistics."""
        if not metric_results:
            return SummaryStatistics(
                count=0, mean=0.0, median=0.0, mode=None,
                std_deviation=0.0, variance=0.0,
                min_value=0.0, max_value=0.0, range=0.0,
                quartiles={}, percentiles={}
            )
        
        values = [result.value for result in metric_results]
        
        # Basic statistics
        count = len(values)
        mean = statistics.mean(values)
        median = statistics.median(values)
        
        try:
            mode = statistics.mode(values)
        except statistics.StatisticsError:
            mode = None
        
        std_deviation = statistics.stdev(values) if count > 1 else 0.0
        variance = statistics.variance(values) if count > 1 else 0.0
        min_value = min(values)
        max_value = max(values)
        range_value = max_value - min_value
        
        # Quartiles
        quartiles = self._calculate_quartiles(values)
        
        # Percentiles
        percentiles = self._calculate_percentiles(values)
        
        return SummaryStatistics(
            count=count,
            mean=mean,
            median=median,
            mode=mode,
            std_deviation=std_deviation,
            variance=variance,
            min_value=min_value,
            max_value=max_value,
            range=range_value,
            quartiles=quartiles,
            percentiles=percentiles
        )
    
    def _calculate_quartiles(self, values: List[float]) -> Dict[str, float]:
        """Calculate quartiles for values."""
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        if n == 0:
            return {"q1": 0.0, "q2": 0.0, "q3": 0.0}
        
        q1_idx = int(0.25 * n)
        q2_idx = int(0.5 * n)
        q3_idx = int(0.75 * n)
        
        return {
            "q1": sorted_values[q1_idx],
            "q2": sorted_values[q2_idx],
            "q3": sorted_values[q3_idx]
        }
    
    def _calculate_percentiles(
        self, 
        values: List[float], 
        percentiles: List[float] = [25, 50, 75, 90, 95, 99]
    ) -> Dict[float, float]:
        """Calculate percentiles for values."""
        if not values:
            return {p: 0.0 for p in percentiles}
        
        sorted_values = sorted(values)
        result = {}
        
        for p in percentiles:
            idx = int((p / 100) * (len(sorted_values) - 1))
            result[p] = sorted_values[idx]
        
        return result
```

## Data Flow Implementation

### 1. Input Processing Pipeline

```python
class DataProcessor:
    """Data preprocessing for metric calculations."""
    
    def __init__(self):
        self.validators = []
        self.normalizers = []
        self._setup_default_processors()
    
    def _setup_default_processors(self):
        """Setup default data processors."""
        self.validators = [
            self._validate_agent_output,
            self._validate_text_content,
            self._validate_timing_data
        ]
        
        self.normalizers = [
            self._normalize_text,
            self._normalize_timestamps,
            self._normalize_metadata
        ]
    
    def process_agent_output(self, agent_output: 'AgentOutput') -> 'AgentOutput':
        """Process agent output through validation and normalization."""
        # Validate
        for validator in self.validators:
            if not validator(agent_output):
                raise MetricValidationError(f"Validation failed: {validator.__name__}")
        
        # Normalize
        processed_output = agent_output
        for normalizer in self.normalizers:
            processed_output = normalizer(processed_output)
        
        return processed_output
    
    def _validate_agent_output(self, agent_output: 'AgentOutput') -> bool:
        """Validate agent output structure."""
        return (
            hasattr(agent_output, 'input_text') and
            hasattr(agent_output, 'output_text') and
            hasattr(agent_output, 'timestamp') and
            agent_output.input_text is not None and
            agent_output.output_text is not None and
            agent_output.timestamp is not None
        )
    
    def _validate_text_content(self, agent_output: 'AgentOutput') -> bool:
        """Validate text content."""
        return (
            isinstance(agent_output.input_text, str) and
            isinstance(agent_output.output_text, str) and
            len(agent_output.input_text.strip()) > 0 and
            len(agent_output.output_text.strip()) > 0
        )
    
    def _validate_timing_data(self, agent_output: 'AgentOutput') -> bool:
        """Validate timing data."""
        return isinstance(agent_output.timestamp, datetime)
    
    def _normalize_text(self, agent_output: 'AgentOutput') -> 'AgentOutput':
        """Normalize text content."""
        # Create a copy to avoid modifying original
        normalized_output = AgentOutput(
            input_text=agent_output.input_text.strip(),
            output_text=agent_output.output_text.strip(),
            timestamp=agent_output.timestamp,
            metadata=agent_output.metadata,
            context=agent_output.context
        )
        return normalized_output
    
    def _normalize_timestamps(self, agent_output: 'AgentOutput') -> 'AgentOutput':
        """Normalize timestamps."""
        # Ensure timestamp is timezone-aware
        if agent_output.timestamp.tzinfo is None:
            from datetime import timezone
            normalized_timestamp = agent_output.timestamp.replace(tzinfo=timezone.utc)
        else:
            normalized_timestamp = agent_output.timestamp
        
        normalized_output = AgentOutput(
            input_text=agent_output.input_text,
            output_text=agent_output.output_text,
            timestamp=normalized_timestamp,
            metadata=agent_output.metadata,
            context=agent_output.context
        )
        return normalized_output
    
    def _normalize_metadata(self, agent_output: 'AgentOutput') -> 'AgentOutput':
        """Normalize metadata."""
        normalized_metadata = agent_output.metadata or {}
        
        normalized_output = AgentOutput(
            input_text=agent_output.input_text,
            output_text=agent_output.output_text,
            timestamp=agent_output.timestamp,
            metadata=normalized_metadata,
            context=agent_output.context
        )
        return normalized_output
```

### 2. Caching Implementation

```python
import hashlib
import json
from typing import Any, Optional
from datetime import datetime, timedelta

class MetricCache:
    """Caching system for metric calculations."""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 3600):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache = {}
        self._access_times = {}
        self._creation_times = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self._cache:
            return None
        
        # Check TTL
        if self._is_expired(key):
            self._remove(key)
            return None
        
        # Update access time
        self._access_times[key] = datetime.now()
        return self._cache[key]
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        # Remove oldest entries if cache is full
        if len(self._cache) >= self.max_size:
            self._evict_oldest()
        
        self._cache[key] = value
        self._access_times[key] = datetime.now()
        self._creation_times[key] = datetime.now()
    
    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired."""
        if key not in self._creation_times:
            return True
        
        age = datetime.now() - self._creation_times[key]
        return age.total_seconds() > self.ttl_seconds
    
    def _evict_oldest(self) -> None:
        """Evict oldest cache entry."""
        if not self._access_times:
            return
        
        oldest_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        self._remove(oldest_key)
    
    def _remove(self, key: str) -> None:
        """Remove entry from cache."""
        self._cache.pop(key, None)
        self._access_times.pop(key, None)
        self._creation_times.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
        self._access_times.clear()
        self._creation_times.clear()
    
    def generate_key(self, agent_output: 'AgentOutput', metric_type: str, context: Optional[Dict] = None) -> str:
        """Generate cache key for metric calculation."""
        # Create hashable representation
        data = {
            "input_text": agent_output.input_text,
            "output_text": agent_output.output_text,
            "metric_type": metric_type,
            "context": context or {}
        }
        
        # Generate hash
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.md5(data_str.encode()).hexdigest()
```

## Performance Optimizations

### 1. Parallel Processing

```python
import asyncio
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import List, Callable, Any

class ParallelProcessor:
    """Parallel processing utilities for metric calculations."""
    
    def __init__(self, max_workers: int = 4, use_processes: bool = False):
        self.max_workers = max_workers
        self.use_processes = use_processes
        self._executor = None
    
    def __enter__(self):
        """Context manager entry."""
        if self.use_processes:
            self._executor = ProcessPoolExecutor(max_workers=self.max_workers)
        else:
            self._executor = ThreadPoolExecutor(max_workers=self.max_workers)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._executor:
            self._executor.shutdown(wait=True)
    
    def map_parallel(
        self, 
        func: Callable, 
        iterable: List[Any], 
        chunksize: int = 1
    ) -> List[Any]:
        """Map function over iterable in parallel."""
        if not self._executor:
            raise RuntimeError("ParallelProcessor must be used as context manager")
        
        return list(self._executor.map(func, iterable, chunksize=chunksize))
    
    def submit_parallel(
        self, 
        func: Callable, 
        *args, 
        **kwargs
    ) -> Any:
        """Submit function for parallel execution."""
        if not self._executor:
            raise RuntimeError("ParallelProcessor must be used as context manager")
        
        return self._executor.submit(func, *args, **kwargs)
```

### 2. Memory Management

```python
import gc
import psutil
from typing import List, Optional

class MemoryManager:
    """Memory management for metric calculations."""
    
    def __init__(self, max_memory_mb: int = 1024):
        self.max_memory_mb = max_memory_mb
        self._memory_threshold = max_memory_mb * 0.8  # 80% threshold
    
    def check_memory_usage(self) -> bool:
        """Check if memory usage is within limits."""
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        return memory_mb < self._memory_threshold
    
    def cleanup_memory(self) -> None:
        """Clean up memory by forcing garbage collection."""
        gc.collect()
    
    def process_in_batches(
        self, 
        data: List[Any], 
        batch_size: int = 100
    ) -> List[Any]:
        """Process data in batches to manage memory."""
        results = []
        
        for i in range(0, len(data), batch_size):
            batch = data[i:i + batch_size]
            
            # Process batch
            batch_results = self._process_batch(batch)
            results.extend(batch_results)
            
            # Cleanup after each batch
            self.cleanup_memory()
            
            # Check memory usage
            if not self.check_memory_usage():
                raise MemoryError("Memory usage exceeded threshold")
        
        return results
    
    def _process_batch(self, batch: List[Any]) -> List[Any]:
        """Process a single batch."""
        # This would be implemented based on specific use case
        return batch
```

## Error Handling Implementation

### 1. Exception Classes

```python
class MetricsError(Exception):
    """Base exception for metrics engine errors."""
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "METRICS_ERROR"
        self.details = details or {}
        self.timestamp = datetime.now()

class MetricCalculationError(MetricsError):
    """Error during metric calculation."""
    def __init__(self, message: str, metric_type: str = None, details: dict = None):
        super().__init__(message, "CALCULATION_ERROR", details)
        self.metric_type = metric_type

class InvalidMetricTypeError(MetricsError):
    """Invalid metric type specified."""
    def __init__(self, message: str, metric_type: str = None, details: dict = None):
        super().__init__(message, "INVALID_METRIC_TYPE", details)
        self.metric_type = metric_type

class MetricValidationError(MetricsError):
    """Error during metric validation."""
    def __init__(self, message: str, validation_rule: str = None, details: dict = None):
        super().__init__(message, "VALIDATION_ERROR", details)
        self.validation_rule = validation_rule

class AggregationError(MetricsError):
    """Error during metric aggregation."""
    def __init__(self, message: str, aggregation_method: str = None, details: dict = None):
        super().__init__(message, "AGGREGATION_ERROR", details)
        self.aggregation_method = aggregation_method
```

### 2. Error Recovery

```python
class ErrorRecovery:
    """Error recovery mechanisms for metric calculations."""
    
    def __init__(self):
        self.retry_attempts = 3
        self.retry_delay = 1.0  # seconds
    
    def calculate_with_retry(
        self, 
        metric_func: Callable, 
        *args, 
        **kwargs
    ) -> Any:
        """Calculate metric with retry on failure."""
        last_exception = None
        
        for attempt in range(self.retry_attempts):
            try:
                return metric_func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                else:
                    break
        
        # All retries failed
        raise MetricCalculationError(
            f"Metric calculation failed after {self.retry_attempts} attempts",
            details={"last_exception": str(last_exception)}
        )
    
    def fallback_calculation(
        self, 
        primary_func: Callable, 
        fallback_func: Callable, 
        *args, 
        **kwargs
    ) -> Any:
        """Try primary calculation, fallback on failure."""
        try:
            return primary_func(*args, **kwargs)
        except Exception as e:
            try:
                return fallback_func(*args, **kwargs)
            except Exception as fallback_e:
                raise MetricCalculationError(
                    "Both primary and fallback calculations failed",
                    details={
                        "primary_error": str(e),
                        "fallback_error": str(fallback_e)
                    }
                )
```

---

**Note**: This implementation provides a comprehensive foundation for the metrics engine while maintaining simplicity and performance. The design follows KISS and YAGNI principles, focusing on essential functionality while providing extensibility for future enhancements.
