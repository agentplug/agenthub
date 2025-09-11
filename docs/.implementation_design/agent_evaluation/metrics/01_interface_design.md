# Metrics Engine - Interface Design

**Document Type**: Interface Design  
**Author**: Assistant  
**Date Created**: 2025-06-28  
**Last Updated**: 2025-06-28  
**Status**: Draft  
**Stakeholders**: Developers, API Consumers, Integration Teams  
**Component**: Metrics Engine  
**Iteration Count**: 1  

## Overview

This document defines the API interfaces and contracts for the Metrics Engine, providing clear specifications for metric calculation, aggregation, and analysis functionality.

## Public Interfaces

### 1. Core Metrics API

#### MetricCalculator
```python
class MetricCalculator:
    """Core metric calculation engine."""
    
    def __init__(self, config: Optional[MetricConfig] = None):
        """Initialize calculator with optional configuration."""
        pass
    
    def calculate_metrics(
        self, 
        agent_outputs: List[AgentOutput], 
        metric_types: List[str],
        context: Optional[EvaluationContext] = None
    ) -> MetricResults:
        """Calculate specified metrics for agent outputs."""
        pass
    
    def calculate_single_metric(
        self, 
        agent_output: AgentOutput, 
        metric_type: str,
        context: Optional[EvaluationContext] = None
    ) -> MetricResult:
        """Calculate a single metric for one agent output."""
        pass
    
    def batch_calculate(
        self, 
        batch_data: List[Tuple[AgentOutput, List[str]]],
        context: Optional[EvaluationContext] = None
    ) -> List[MetricResults]:
        """Calculate metrics for a batch of agent outputs."""
        pass
    
    def get_available_metrics(self) -> List[str]:
        """Get list of available metric types."""
        pass
    
    def validate_metric_type(self, metric_type: str) -> bool:
        """Validate if a metric type is supported."""
        pass
```

#### MetricAggregator
```python
class MetricAggregator:
    """Metric aggregation and summary statistics."""
    
    def __init__(self, aggregation_methods: Optional[List[str]] = None):
        """Initialize aggregator with optional methods."""
        pass
    
    def aggregate(
        self, 
        metric_results: List[MetricResult], 
        method: str = "mean"
    ) -> AggregatedMetric:
        """Aggregate metric results using specified method."""
        pass
    
    def get_summary_statistics(
        self, 
        metric_results: List[MetricResult]
    ) -> SummaryStatistics:
        """Get comprehensive summary statistics."""
        pass
    
    def get_percentiles(
        self, 
        metric_results: List[MetricResult], 
        percentiles: List[float] = [25, 50, 75, 90, 95, 99]
    ) -> Dict[float, float]:
        """Get percentile values for metric results."""
        pass
    
    def get_distribution(
        self, 
        metric_results: List[MetricResult]
    ) -> DistributionInfo:
        """Get distribution information for metric results."""
        pass
```

#### CustomMetricManager
```python
class CustomMetricManager:
    """Manager for custom user-defined metrics."""
    
    def __init__(self):
        """Initialize custom metric manager."""
        pass
    
    def register_metric(
        self, 
        name: str, 
        definition: CustomMetricDefinition
    ) -> bool:
        """Register a new custom metric."""
        pass
    
    def unregister_metric(self, name: str) -> bool:
        """Unregister a custom metric."""
        pass
    
    def get_custom_metrics(self) -> List[str]:
        """Get list of registered custom metrics."""
        pass
    
    def validate_definition(
        self, 
        definition: CustomMetricDefinition
    ) -> ValidationResult:
        """Validate a custom metric definition."""
        pass
    
    def execute_custom_metric(
        self, 
        name: str, 
        agent_output: AgentOutput,
        context: Optional[EvaluationContext] = None
    ) -> MetricResult:
        """Execute a custom metric calculation."""
        pass
```

### 2. Category-Specific APIs

#### Accuracy Metrics
```python
class AccuracyMetrics:
    """Accuracy-related metric calculations."""
    
    @staticmethod
    def exact_match(
        predicted: str, 
        expected: str, 
        case_sensitive: bool = True
    ) -> float:
        """Calculate exact match score."""
        pass
    
    @staticmethod
    def semantic_similarity(
        predicted: str, 
        expected: str, 
        model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ) -> float:
        """Calculate semantic similarity using embeddings."""
        pass
    
    @staticmethod
    def f1_score(
        predicted: List[str], 
        expected: List[str], 
        average: str = "weighted"
    ) -> float:
        """Calculate F1 score for classification tasks."""
        pass
    
    @staticmethod
    def bleu_score(
        predicted: str, 
        expected: str, 
        n_gram: int = 4
    ) -> float:
        """Calculate BLEU score for text generation."""
        pass
    
    @staticmethod
    def rouge_score(
        predicted: str, 
        expected: str, 
        rouge_type: str = "rouge-l"
    ) -> float:
        """Calculate ROUGE score for text summarization."""
        pass
```

#### Quality Metrics
```python
class QualityMetrics:
    """Quality-related metric calculations."""
    
    @staticmethod
    def relevance_score(
        output: str, 
        input_text: str, 
        context: Optional[str] = None
    ) -> float:
        """Calculate relevance score of output to input."""
        pass
    
    @staticmethod
    def completeness_score(
        output: str, 
        expected_elements: List[str]
    ) -> float:
        """Calculate completeness score based on expected elements."""
        pass
    
    @staticmethod
    def coherence_score(output: str) -> float:
        """Calculate coherence score for text output."""
        pass
    
    @staticmethod
    def clarity_score(output: str) -> float:
        """Calculate clarity and readability score."""
        pass
    
    @staticmethod
    def factual_accuracy(
        output: str, 
        reference_facts: List[str]
    ) -> float:
        """Calculate factual accuracy against reference facts."""
        pass
    
    @staticmethod
    def safety_score(output: str) -> float:
        """Calculate safety score for harmful content detection."""
        pass
```

#### Performance Metrics
```python
class PerformanceMetrics:
    """Performance-related metric calculations."""
    
    @staticmethod
    def response_time(
        start_time: datetime, 
        end_time: datetime
    ) -> float:
        """Calculate response time in seconds."""
        pass
    
    @staticmethod
    def throughput(
        request_count: int, 
        time_window: float
    ) -> float:
        """Calculate requests per second."""
        pass
    
    @staticmethod
    def resource_usage(
        cpu_usage: float, 
        memory_usage: float, 
        disk_usage: float
    ) -> ResourceUsage:
        """Calculate resource utilization metrics."""
        pass
    
    @staticmethod
    def latency_percentiles(
        response_times: List[float], 
        percentiles: List[float] = [50, 90, 95, 99]
    ) -> Dict[float, float]:
        """Calculate latency percentiles."""
        pass
    
    @staticmethod
    def error_rate(
        total_requests: int, 
        error_requests: int
    ) -> float:
        """Calculate error rate percentage."""
        pass
```

#### Reliability Metrics
```python
class ReliabilityMetrics:
    """Reliability-related metric calculations."""
    
    @staticmethod
    def consistency_score(
        outputs: List[str], 
        similarity_threshold: float = 0.8
    ) -> float:
        """Calculate consistency across multiple outputs."""
        pass
    
    @staticmethod
    def stability_score(
        metric_values: List[float], 
        time_window: float
    ) -> float:
        """Calculate stability over time."""
        pass
    
    @staticmethod
    def robustness_score(
        normal_outputs: List[str], 
        edge_case_outputs: List[str]
    ) -> float:
        """Calculate robustness under edge cases."""
        pass
    
    @staticmethod
    def reproducibility_score(
        run1_results: List[float], 
        run2_results: List[float]
    ) -> float:
        """Calculate reproducibility between runs."""
        pass
```

### 3. Analysis APIs

#### StatisticalAnalysis
```python
class StatisticalAnalysis:
    """Statistical analysis of metric results."""
    
    @staticmethod
    def descriptive_statistics(
        values: List[float]
    ) -> DescriptiveStats:
        """Calculate descriptive statistics."""
        pass
    
    @staticmethod
    def correlation_analysis(
        metric1_values: List[float], 
        metric2_values: List[float]
    ) -> CorrelationResult:
        """Calculate correlation between two metrics."""
        pass
    
    @staticmethod
    def trend_analysis(
        values: List[float], 
        timestamps: List[datetime]
    ) -> TrendResult:
        """Analyze trends over time."""
        pass
    
    @staticmethod
    def outlier_detection(
        values: List[float], 
        method: str = "iqr"
    ) -> List[int]:
        """Detect outliers in metric values."""
        pass
```

#### ComparativeAnalysis
```python
class ComparativeAnalysis:
    """Comparative analysis between different agents or benchmarks."""
    
    @staticmethod
    def compare_agents(
        agent1_metrics: Dict[str, float], 
        agent2_metrics: Dict[str, float]
    ) -> ComparisonResult:
        """Compare metrics between two agents."""
        pass
    
    @staticmethod
    def compare_benchmarks(
        benchmark1_results: MetricResults, 
        benchmark2_results: MetricResults
    ) -> ComparisonResult:
        """Compare results between two benchmarks."""
        pass
    
    @staticmethod
    def rank_agents(
        agent_metrics: Dict[str, Dict[str, float]]
    ) -> List[AgentRanking]:
        """Rank agents based on their metrics."""
        pass
    
    @staticmethod
    def baseline_comparison(
        current_metrics: Dict[str, float], 
        baseline_metrics: Dict[str, float]
    ) -> BaselineComparison:
        """Compare current performance against baseline."""
        pass
```

## Data Models

### 1. Core Data Models

#### AgentOutput
```python
@dataclass
class AgentOutput:
    """Represents a single agent output."""
    input_text: str
    output_text: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None
```

#### MetricResult
```python
@dataclass
class MetricResult:
    """Represents a single metric calculation result."""
    metric_type: str
    value: float
    confidence: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)
```

#### MetricResults
```python
@dataclass
class MetricResults:
    """Represents results for multiple metrics."""
    agent_output: AgentOutput
    metrics: Dict[str, MetricResult]
    summary: Optional[SummaryStatistics] = None
    timestamp: datetime = field(default_factory=datetime.now)
```

#### AggregatedMetric
```python
@dataclass
class AggregatedMetric:
    """Represents an aggregated metric result."""
    metric_type: str
    aggregated_value: float
    aggregation_method: str
    count: int
    min_value: float
    max_value: float
    std_deviation: float
    confidence_interval: Optional[Tuple[float, float]] = None
```

### 2. Configuration Models

#### MetricConfig
```python
@dataclass
class MetricConfig:
    """Configuration for metric calculations."""
    cache_enabled: bool = True
    parallel_processing: bool = True
    max_workers: int = 4
    timeout_seconds: int = 300
    memory_limit_mb: int = 1024
    custom_metrics: Optional[Dict[str, CustomMetricDefinition]] = None
```

#### CustomMetricDefinition
```python
@dataclass
class CustomMetricDefinition:
    """Definition for a custom metric."""
    name: str
    description: str
    calculation_function: Callable
    input_types: List[str]
    output_type: str
    parameters: Optional[Dict[str, Any]] = None
    validation_rules: Optional[List[ValidationRule]] = None
```

### 3. Analysis Models

#### SummaryStatistics
```python
@dataclass
class SummaryStatistics:
    """Summary statistics for a set of metric values."""
    count: int
    mean: float
    median: float
    mode: Optional[float]
    std_deviation: float
    variance: float
    min_value: float
    max_value: float
    range: float
    quartiles: Dict[str, float]
    percentiles: Dict[float, float]
```

#### DistributionInfo
```python
@dataclass
class DistributionInfo:
    """Information about the distribution of metric values."""
    distribution_type: str
    skewness: float
    kurtosis: float
    histogram: List[Tuple[float, int]]
    density_curve: Optional[List[Tuple[float, float]]] = None
```

#### ComparisonResult
```python
@dataclass
class ComparisonResult:
    """Result of comparing two sets of metrics."""
    metric_differences: Dict[str, float]
    statistical_significance: Dict[str, bool]
    effect_sizes: Dict[str, float]
    overall_winner: Optional[str]
    confidence_level: float
```

## Error Handling

### 1. Exception Hierarchy

```python
class MetricsError(Exception):
    """Base exception for metrics engine errors."""
    pass

class MetricCalculationError(MetricsError):
    """Error during metric calculation."""
    pass

class InvalidMetricTypeError(MetricsError):
    """Invalid metric type specified."""
    pass

class MetricValidationError(MetricsError):
    """Error during metric validation."""
    pass

class AggregationError(MetricsError):
    """Error during metric aggregation."""
    pass

class CustomMetricError(MetricsError):
    """Error with custom metric execution."""
    pass
```

### 2. Error Response Models

```python
@dataclass
class ErrorResponse:
    """Standardized error response."""
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    request_id: Optional[str] = None
```

## Validation Rules

### 1. Input Validation

```python
class InputValidator:
    """Validates inputs for metric calculations."""
    
    @staticmethod
    def validate_agent_output(output: AgentOutput) -> ValidationResult:
        """Validate agent output structure."""
        pass
    
    @staticmethod
    def validate_metric_type(metric_type: str) -> ValidationResult:
        """Validate metric type is supported."""
        pass
    
    @staticmethod
    def validate_calculation_context(context: EvaluationContext) -> ValidationResult:
        """Validate evaluation context."""
        pass
```

### 2. Output Validation

```python
class OutputValidator:
    """Validates metric calculation outputs."""
    
    @staticmethod
    def validate_metric_result(result: MetricResult) -> ValidationResult:
        """Validate metric result structure and values."""
        pass
    
    @staticmethod
    def validate_aggregated_metric(metric: AggregatedMetric) -> ValidationResult:
        """Validate aggregated metric result."""
        pass
```

## Performance Contracts

### 1. Response Time Requirements

- **Single Metric Calculation**: < 100ms average
- **Batch Processing**: < 1s for 100 outputs
- **Aggregation**: < 50ms for 1000 results
- **Custom Metric Execution**: < 200ms average

### 2. Memory Requirements

- **Base Memory Usage**: < 100MB
- **Per 1000 Evaluations**: < 50MB additional
- **Peak Memory Usage**: < 1GB
- **Memory Cleanup**: Automatic after 5 minutes idle

### 3. Concurrency Requirements

- **Concurrent Calculations**: Support 100+ parallel
- **Thread Safety**: All operations thread-safe
- **Resource Pooling**: Efficient resource management
- **Queue Management**: Handle burst requests

## API Usage Examples

### 1. Basic Metric Calculation

```python
# Initialize calculator
calculator = MetricCalculator()

# Calculate metrics for agent output
agent_output = AgentOutput(
    input_text="What is the capital of France?",
    output_text="The capital of France is Paris.",
    timestamp=datetime.now()
)

# Calculate accuracy metrics
results = calculator.calculate_metrics(
    agent_outputs=[agent_output],
    metric_types=["exact_match", "semantic_similarity", "relevance_score"]
)

print(f"Exact Match: {results.metrics['exact_match'].value}")
print(f"Semantic Similarity: {results.metrics['semantic_similarity'].value}")
```

### 2. Batch Processing

```python
# Prepare batch data
batch_data = [
    (output1, ["accuracy", "quality"]),
    (output2, ["accuracy", "performance"]),
    (output3, ["quality", "reliability"])
]

# Process batch
batch_results = calculator.batch_calculate(batch_data)

# Aggregate results
aggregator = MetricAggregator()
for results in batch_results:
    summary = aggregator.get_summary_statistics(list(results.metrics.values()))
    print(f"Summary: {summary.mean}")
```

### 3. Custom Metrics

```python
# Define custom metric
def custom_helpfulness_score(output: str, input_text: str) -> float:
    # Custom logic for helpfulness assessment
    return 0.85

# Register custom metric
custom_metric = CustomMetricDefinition(
    name="helpfulness_score",
    description="Custom helpfulness assessment",
    calculation_function=custom_helpfulness_score,
    input_types=["output_text", "input_text"],
    output_type="float"
)

manager = CustomMetricManager()
manager.register_metric("helpfulness_score", custom_metric)

# Use custom metric
result = manager.execute_custom_metric(
    "helpfulness_score", 
    agent_output
)
```

---

**Note**: This interface design provides a comprehensive yet simple API for metric calculation and analysis. The design follows RESTful principles and provides clear contracts for all metric operations while maintaining flexibility for custom metrics and analysis.
