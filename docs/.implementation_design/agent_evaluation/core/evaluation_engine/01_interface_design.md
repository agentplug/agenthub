# Core Evaluation Engine - Interface Design

**Document Type**: Interface Design  
**Author**: Assistant  
**Date Created**: 2025-06-28  
**Last Updated**: 2025-06-28  
**Status**: Draft  
**Stakeholders**: Developers, Technical Architects, QA Team  
**Feature**: Agent Evaluation System - Core Engine  
**Iteration Count**: 1  

## Overview

This document defines the APIs, interfaces, and contracts for the core evaluation engine. It specifies how the evaluation engine interacts with other components and provides a clear contract for implementation.

## Public API Interface

### Main Evaluation API

```python
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum

class EvaluationMode(Enum):
    """Evaluation mode enumeration."""
    DEMO = "demo"
    BENCHMARK = "benchmark"
    CUSTOM = "custom"

@dataclass
class EvaluationConfig:
    """Configuration for evaluation runs."""
    mode: EvaluationMode
    samples: Optional[int] = None
    benchmark: Optional[str] = None
    custom_benchmark: Optional[Dict[str, Any]] = None
    timeout: Optional[int] = None
    max_memory: Optional[int] = None
    output_format: str = "interactive"
    verbose: bool = False

@dataclass
class SampleResult:
    """Result for a single sample evaluation."""
    input_data: Any
    output_data: Any
    execution_time: float
    memory_usage: int
    quality_score: float
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class EvaluationResult:
    """Complete evaluation result."""
    agent_id: str
    mode: EvaluationMode
    samples: List[SampleResult]
    metrics: Dict[str, float]
    summary: Dict[str, Any]
    execution_time: float
    total_memory_usage: int
    success: bool
    error: Optional[str] = None
    recommendations: List[str] = None

class EvaluationEngine:
    """Main evaluation engine interface."""
    
    def __init__(self, config: Optional[EvaluationConfig] = None):
        """Initialize the evaluation engine."""
        pass
    
    def evaluate(
        self, 
        agent: Any, 
        config: Optional[EvaluationConfig] = None
    ) -> EvaluationResult:
        """
        Evaluate an agent using the specified configuration.
        
        Args:
            agent: Agent instance to evaluate
            config: Evaluation configuration
            
        Returns:
            EvaluationResult: Complete evaluation results
            
        Raises:
            EvaluationError: If evaluation fails
            ValidationError: If configuration is invalid
        """
        pass
    
    def evaluate_demo(
        self, 
        agent: Any, 
        samples: int = 5
    ) -> EvaluationResult:
        """
        Quick demo evaluation of an agent.
        
        Args:
            agent: Agent instance to evaluate
            samples: Number of samples to generate
            
        Returns:
            EvaluationResult: Demo evaluation results
        """
        pass
    
    def evaluate_benchmark(
        self, 
        agent: Any, 
        benchmark: str,
        custom_params: Optional[Dict[str, Any]] = None
    ) -> EvaluationResult:
        """
        Comprehensive benchmark evaluation of an agent.
        
        Args:
            agent: Agent instance to evaluate
            benchmark: Benchmark name to use
            custom_params: Custom benchmark parameters
            
        Returns:
            EvaluationResult: Benchmark evaluation results
        """
        pass
    
    def evaluate_custom(
        self, 
        agent: Any, 
        custom_benchmark: Dict[str, Any]
    ) -> EvaluationResult:
        """
        Custom evaluation of an agent.
        
        Args:
            agent: Agent instance to evaluate
            custom_benchmark: Custom benchmark configuration
            
        Returns:
            EvaluationResult: Custom evaluation results
        """
        pass
```

## Internal Component Interfaces

### Sample Generator Interface

```python
from abc import ABC, abstractmethod
from typing import List, Any, Dict

class SampleGenerator(ABC):
    """Interface for sample input generation."""
    
    @abstractmethod
    def generate_samples(
        self, 
        agent_capabilities: List[str], 
        count: int,
        complexity: str = "medium"
    ) -> List[Any]:
        """
        Generate sample inputs for agent evaluation.
        
        Args:
            agent_capabilities: List of agent capabilities
            count: Number of samples to generate
            complexity: Sample complexity level
            
        Returns:
            List of sample inputs
        """
        pass
    
    @abstractmethod
    def get_sample_types(self) -> List[str]:
        """Get supported sample types."""
        pass
    
    @abstractmethod
    def validate_sample(self, sample: Any) -> bool:
        """Validate a generated sample."""
        pass

class TextSampleGenerator(SampleGenerator):
    """Text-based sample generator."""
    pass

class CodeSampleGenerator(SampleGenerator):
    """Code-based sample generator."""
    pass

class StructuredDataSampleGenerator(SampleGenerator):
    """Structured data sample generator."""
    pass
```

### Agent Executor Interface

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import asyncio

class AgentExecutor(ABC):
    """Interface for agent execution."""
    
    @abstractmethod
    async def execute_agent(
        self, 
        agent: Any, 
        input_data: Any,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute an agent with given input.
        
        Args:
            agent: Agent instance to execute
            input_data: Input data for the agent
            timeout: Execution timeout in seconds
            
        Returns:
            Execution result dictionary
        """
        pass
    
    @abstractmethod
    def validate_agent(self, agent: Any) -> bool:
        """Validate agent compatibility."""
        pass
    
    @abstractmethod
    def get_agent_capabilities(self, agent: Any) -> List[str]:
        """Get agent capabilities."""
        pass

class AgentHubExecutor(AgentExecutor):
    """AgentHub-specific agent executor."""
    pass
```

### Output Analyzer Interface

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple

class OutputAnalyzer(ABC):
    """Interface for output analysis."""
    
    @abstractmethod
    def analyze_output(
        self, 
        input_data: Any, 
        output_data: Any,
        expected_output: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Analyze agent output quality and characteristics.
        
        Args:
            input_data: Original input data
            output_data: Agent output data
            expected_output: Expected output (if available)
            
        Returns:
            Analysis results dictionary
        """
        pass
    
    @abstractmethod
    def calculate_quality_score(
        self, 
        analysis_results: Dict[str, Any]
    ) -> float:
        """Calculate overall quality score."""
        pass
    
    @abstractmethod
    def get_analysis_metrics(self) -> List[str]:
        """Get available analysis metrics."""
        pass

class TextOutputAnalyzer(OutputAnalyzer):
    """Text output analyzer."""
    pass

class CodeOutputAnalyzer(OutputAnalyzer):
    """Code output analyzer."""
    pass

class StructuredDataOutputAnalyzer(OutputAnalyzer):
    """Structured data output analyzer."""
    pass
```

### Metrics Calculator Interface

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class MetricsCalculator(ABC):
    """Interface for metrics calculation."""
    
    @abstractmethod
    def calculate_metrics(
        self, 
        sample_results: List[SampleResult]
    ) -> Dict[str, float]:
        """
        Calculate evaluation metrics from sample results.
        
        Args:
            sample_results: List of sample evaluation results
            
        Returns:
            Dictionary of calculated metrics
        """
        pass
    
    @abstractmethod
    def get_metric_definitions(self) -> Dict[str, str]:
        """Get metric definitions and descriptions."""
        pass
    
    @abstractmethod
    def validate_metrics(self, metrics: Dict[str, float]) -> bool:
        """Validate calculated metrics."""
        pass

class AccuracyMetricsCalculator(MetricsCalculator):
    """Accuracy metrics calculator."""
    pass

class QualityMetricsCalculator(MetricsCalculator):
    """Quality metrics calculator."""
    pass

class PerformanceMetricsCalculator(MetricsCalculator):
    """Performance metrics calculator."""
    pass

class ReliabilityMetricsCalculator(MetricsCalculator):
    """Reliability metrics calculator."""
    pass
```

## Data Models and Schemas

### Core Data Models

```python
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from enum import Enum

class SampleType(Enum):
    """Sample type enumeration."""
    TEXT = "text"
    CODE = "code"
    STRUCTURED_DATA = "structured_data"
    MIXED = "mixed"

class QualityLevel(Enum):
    """Quality level enumeration."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    FAILED = "failed"

@dataclass
class SampleInput:
    """Sample input data structure."""
    data: Any
    sample_type: SampleType
    complexity: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class SampleOutput:
    """Sample output data structure."""
    data: Any
    execution_time: float
    memory_usage: int
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class QualityAnalysis:
    """Quality analysis results."""
    overall_score: float
    quality_level: QualityLevel
    metrics: Dict[str, float]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    analysis_details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CapabilityAnalysis:
    """Agent capability analysis."""
    capabilities: List[str]
    strengths: List[str]
    limitations: List[str]
    use_cases: List[str]
    confidence_scores: Dict[str, float]
    recommendations: List[str]
```

### Configuration Schemas

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from enum import Enum

class ComplexityLevel(str, Enum):
    """Complexity level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    EXPERT = "expert"

class OutputFormat(str, Enum):
    """Output format enumeration."""
    INTERACTIVE = "interactive"
    JSON = "json"
    CSV = "csv"
    PDF = "pdf"

class EvaluationConfigSchema(BaseModel):
    """Evaluation configuration schema."""
    mode: EvaluationMode
    samples: Optional[int] = Field(None, ge=1, le=100)
    benchmark: Optional[str] = Field(None, min_length=1)
    custom_benchmark: Optional[Dict[str, Any]] = None
    timeout: Optional[int] = Field(None, ge=1, le=3600)
    max_memory: Optional[int] = Field(None, ge=100, le=10000)
    output_format: OutputFormat = OutputFormat.INTERACTIVE
    verbose: bool = False
    complexity: ComplexityLevel = ComplexityLevel.MEDIUM
    
    @validator('samples')
    def validate_samples(cls, v, values):
        if values.get('mode') == EvaluationMode.DEMO and v is None:
            return 5
        return v
    
    @validator('benchmark')
    def validate_benchmark(cls, v, values):
        if values.get('mode') == EvaluationMode.BENCHMARK and v is None:
            raise ValueError('Benchmark must be specified for benchmark mode')
        return v

class SampleConfigSchema(BaseModel):
    """Sample generation configuration schema."""
    count: int = Field(5, ge=1, le=50)
    complexity: ComplexityLevel = ComplexityLevel.MEDIUM
    sample_types: List[SampleType] = Field(default_factory=lambda: [SampleType.TEXT])
    diversity: float = Field(0.7, ge=0.0, le=1.0)
    custom_prompts: Optional[List[str]] = None
```

## Error Handling Contracts

### Exception Hierarchy

```python
class EvaluationError(Exception):
    """Base evaluation error."""
    pass

class ValidationError(EvaluationError):
    """Configuration validation error."""
    pass

class AgentCompatibilityError(EvaluationError):
    """Agent compatibility error."""
    pass

class ExecutionError(EvaluationError):
    """Agent execution error."""
    pass

class TimeoutError(EvaluationError):
    """Evaluation timeout error."""
    pass

class ResourceError(EvaluationError):
    """Resource limitation error."""
    pass

class BenchmarkError(EvaluationError):
    """Benchmark-related error."""
    pass

class MetricsError(EvaluationError):
    """Metrics calculation error."""
    pass
```

### Error Response Format

```python
@dataclass
class ErrorResponse:
    """Standardized error response format."""
    error_type: str
    error_message: str
    error_code: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)
```

## Integration Points

### AgentHub Integration

```python
class AgentHubIntegration:
    """Integration with AgentHub components."""
    
    def __init__(self, agent_runtime, storage, tool_registry):
        self.agent_runtime = agent_runtime
        self.storage = storage
        self.tool_registry = tool_registry
    
    def load_agent(self, agent_id: str) -> Any:
        """Load agent using AgentHub runtime."""
        pass
    
    def execute_agent(self, agent: Any, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent using AgentHub runtime."""
        pass
    
    def get_agent_capabilities(self, agent: Any) -> List[str]:
        """Get agent capabilities from AgentHub."""
        pass
    
    def store_evaluation_result(self, result: EvaluationResult) -> str:
        """Store evaluation result in AgentHub storage."""
        pass
```

### CLI Integration

```python
class CLIInterface:
    """Command-line interface for evaluation engine."""
    
    def __init__(self, evaluation_engine: EvaluationEngine):
        self.evaluation_engine = evaluation_engine
    
    def run_demo_evaluation(self, agent_id: str, samples: int = 5) -> None:
        """Run demo evaluation from CLI."""
        pass
    
    def run_benchmark_evaluation(self, agent_id: str, benchmark: str) -> None:
        """Run benchmark evaluation from CLI."""
        pass
    
    def run_custom_evaluation(self, agent_id: str, config_file: str) -> None:
        """Run custom evaluation from CLI."""
        pass
```

### SDK Integration

```python
class SDKInterface:
    """Python SDK interface for evaluation engine."""
    
    def __init__(self, evaluation_engine: EvaluationEngine):
        self.evaluation_engine = evaluation_engine
    
    def evaluate(self, agent: Any, **kwargs) -> EvaluationResult:
        """Main evaluation function for SDK."""
        pass
    
    def evaluate_demo(self, agent: Any, samples: int = 5) -> EvaluationResult:
        """Demo evaluation for SDK."""
        pass
    
    def evaluate_benchmark(self, agent: Any, benchmark: str, **kwargs) -> EvaluationResult:
        """Benchmark evaluation for SDK."""
        pass
```

## Performance Contracts

### Performance Requirements

```python
@dataclass
class PerformanceRequirements:
    """Performance requirements specification."""
    demo_mode_max_time: float = 30.0  # seconds
    benchmark_mode_max_time: float = 300.0  # seconds
    max_memory_usage: int = 1024  # MB
    min_success_rate: float = 0.99
    max_concurrent_evaluations: int = 100
    max_response_time: float = 0.1  # seconds for API calls
```

### Performance Monitoring

```python
class PerformanceMonitor:
    """Performance monitoring interface."""
    
    def start_timer(self, operation: str) -> str:
        """Start timing an operation."""
        pass
    
    def end_timer(self, timer_id: str) -> float:
        """End timing and return duration."""
        pass
    
    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a performance metric."""
        pass
    
    def get_metrics(self) -> Dict[str, float]:
        """Get current performance metrics."""
        pass
```

## Testing Contracts

### Test Interface

```python
class TestInterface:
    """Interface for testing the evaluation engine."""
    
    def create_mock_agent(self, capabilities: List[str]) -> Any:
        """Create a mock agent for testing."""
        pass
    
    def create_test_samples(self, count: int, sample_type: SampleType) -> List[Any]:
        """Create test samples for testing."""
        pass
    
    def validate_evaluation_result(self, result: EvaluationResult) -> bool:
        """Validate evaluation result structure."""
        pass
    
    def measure_performance(self, operation: callable) -> Dict[str, float]:
        """Measure operation performance."""
        pass
```

## Next Steps

1. **Implementation**: Implement the core evaluation engine based on these interfaces
2. **Testing**: Create comprehensive tests for all interfaces
3. **Documentation**: Generate API documentation from interfaces
4. **Validation**: Validate interfaces with stakeholders
5. **Integration**: Integrate with existing AgentHub components

---

**Note**: These interfaces represent the current understanding of the evaluation engine design. They should be reviewed and validated with the development team before implementation begins.
