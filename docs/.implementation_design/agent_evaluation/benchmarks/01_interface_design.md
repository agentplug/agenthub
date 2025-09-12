# Benchmark Framework - Interface Design

**Document Type**: Interface Design  
**Author**: Assistant  
**Date Created**: 2025-06-28  
**Last Updated**: 2025-06-28  
**Status**: Draft  
**Stakeholders**: Developers, Technical Architects, QA Team  
**Feature**: Agent Evaluation System - Benchmark Framework  
**Iteration Count**: 1  

## Overview

This document defines the APIs, interfaces, and contracts for the benchmark framework. It specifies how benchmarks are loaded, executed, and integrated with the evaluation system.

## Publicly Available Benchmarks

### Supported Public Benchmarks

The benchmark framework prioritizes integration with well-established, publicly available benchmarks that are widely used in the AI/ML community:

#### Code Generation Benchmarks
- **HumanEval**: 164 hand-written programming problems with test cases
- **MBPP (Mostly Basic Python Problems)**: 974 Python programming problems
- **CodeXGLUE**: Multi-lingual code generation and understanding tasks

#### Text Analysis Benchmarks
- **GLUE (General Language Understanding Evaluation)**: 9 sentence-level tasks
- **SuperGLUE**: 8 more challenging language understanding tasks
- **SQuAD (Stanford Question Answering Dataset)**: Reading comprehension tasks

#### Reasoning Benchmarks
- **GSM8K (Grade School Math 8K)**: 8,500 grade school math word problems
- **HellaSwag**: Commonsense reasoning with 70,000 multiple choice questions
- **ARC (AI2 Reasoning Challenge)**: Science exam questions requiring reasoning

#### Domain-Specific Benchmarks
- **MMLU (Massive Multitask Language Understanding)**: 57 tasks across various domains
- **Big-Bench**: Large-scale benchmark with 200+ tasks
- **HELM (Holistic Evaluation of Language Models)**: Comprehensive evaluation suite

### Public Benchmark Integration

```python
class PublicBenchmarkLoader:
    """Loader for publicly available benchmarks."""
    
    def __init__(self):
        self.supported_benchmarks = {
            "humaneval": {
                "name": "HumanEval",
                "description": "Code generation benchmark with 164 problems",
                "source": "https://github.com/openai/human-eval",
                "format": "jsonl",
                "metrics": ["pass_at_k", "exact_match"]
            },
            "glue": {
                "name": "GLUE",
                "description": "General Language Understanding Evaluation",
                "source": "https://gluebenchmark.com/",
                "format": "tsv",
                "metrics": ["accuracy", "f1", "matthews_correlation"]
            },
            "gsm8k": {
                "name": "GSM8K",
                "description": "Grade School Math 8K problems",
                "source": "https://github.com/openai/grade-school-math",
                "format": "jsonl",
                "metrics": ["accuracy", "exact_match"]
            }
        }
    
    def load_benchmark(self, benchmark_name: str) -> PublicBenchmark:
        """Load a publicly available benchmark."""
        if benchmark_name not in self.supported_benchmarks:
            raise ValueError(f"Unsupported public benchmark: {benchmark_name}")
        
        benchmark_info = self.supported_benchmarks[benchmark_name]
        return PublicBenchmark(
            name=benchmark_info["name"],
            source=benchmark_info["source"],
            format=benchmark_info["format"],
            metrics=benchmark_info["metrics"]
        )
    
    def is_supported(self, benchmark_name: str) -> bool:
        """Check if a benchmark is supported."""
        return benchmark_name in self.supported_benchmarks
    
    def list_supported(self) -> List[str]:
        """List all supported public benchmarks."""
        return list(self.supported_benchmarks.keys())
    
    def get_benchmark_info(self, benchmark_name: str) -> Dict[str, Any]:
        """Get information about a public benchmark."""
        if not self.is_supported(benchmark_name):
            raise ValueError(f"Unsupported public benchmark: {benchmark_name}")
        return self.supported_benchmarks[benchmark_name]
```

## Core Benchmark Interface

### Base Benchmark Interface

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

class BenchmarkType(Enum):
    """Benchmark type enumeration."""
    PUBLIC = "public"          # Publicly available benchmarks (GLUE, HumanEval, etc.)
    PREDEFINED = "predefined"  # AgentHub predefined benchmarks
    CUSTOM = "custom"          # User-defined custom benchmarks
    FILE_BASED = "file_based"  # File-based benchmarks
    API_BASED = "api_based"    # API-based benchmarks

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
class BenchmarkSample:
    """Single benchmark sample."""
    input_data: Any
    expected_output: Optional[Any] = None
    metadata: Dict[str, Any] = None
    category: Optional[str] = None
    complexity: str = "medium"
    weight: float = 1.0

@dataclass
class BenchmarkResult:
    """Benchmark execution result."""
    sample: BenchmarkSample
    agent_output: Any
    metrics: Dict[str, float]
    execution_time: float
    success: bool
    error: Optional[str] = None

class Benchmark(ABC):
    """Base benchmark interface."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.samples: List[BenchmarkSample] = []
        self.metrics: List[str] = []
    
    @abstractmethod
    def load_samples(self) -> List[BenchmarkSample]:
        """Load benchmark samples."""
        pass
    
    @abstractmethod
    def evaluate_sample(
        self, 
        sample: BenchmarkSample, 
        agent_output: Any
    ) -> Dict[str, float]:
        """Evaluate a single sample."""
        pass
    
    @abstractmethod
    def get_metrics(self) -> List[str]:
        """Get available metrics for this benchmark."""
        pass
    
    def validate_sample(self, sample: BenchmarkSample) -> bool:
        """Validate a benchmark sample."""
        return (
            sample.input_data is not None and
            sample.complexity in ["low", "medium", "high"] and
            sample.weight > 0
        )
    
    def get_sample_count(self) -> int:
        """Get total number of samples."""
        return len(self.samples)
    
    def get_samples_by_category(self, category: str) -> List[BenchmarkSample]:
        """Get samples by category."""
        return [s for s in self.samples if s.category == category]
    
    def get_samples_by_complexity(self, complexity: str) -> List[BenchmarkSample]:
        """Get samples by complexity level."""
        return [s for s in self.samples if s.complexity == complexity]
```

### Predefined Benchmark Interface

```python
class PredefinedBenchmark(Benchmark):
    """Interface for predefined benchmarks."""
    
    def __init__(self, name: str, dataset_path: str, description: str = ""):
        super().__init__(name, description)
        self.dataset_path = dataset_path
        self._loaded = False
    
    def load_samples(self) -> List[BenchmarkSample]:
        """Load samples from predefined dataset."""
        if not self._loaded:
            self.samples = self._load_from_dataset()
            self._loaded = True
        return self.samples
    
    def _load_from_dataset(self) -> List[BenchmarkSample]:
        """Load samples from dataset file."""
        # Implementation depends on dataset format
        pass
    
    def get_benchmark_info(self) -> Dict[str, Any]:
        """Get benchmark information."""
        return {
            "name": self.name,
            "description": self.description,
            "dataset_path": self.dataset_path,
            "sample_count": len(self.samples),
            "metrics": self.get_metrics(),
            "categories": list(set(s.category for s in self.samples if s.category))
        }
```

### Custom Benchmark Interface

```python
class CustomBenchmark(Benchmark):
    """Interface for custom benchmarks."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config.get("description", ""))
        self.config = config
        self.evaluation_function = config.get("evaluation_function")
        self.sample_generator = config.get("sample_generator")
    
    def load_samples(self) -> List[BenchmarkSample]:
        """Load samples from custom configuration."""
        if not self.samples:
            self.samples = self._load_from_config()
        return self.samples
    
    def _load_from_config(self) -> List[BenchmarkSample]:
        """Load samples from configuration."""
        samples = []
        
        # Load from samples list
        if "samples" in self.config:
            for sample_data in self.config["samples"]:
                sample = BenchmarkSample(
                    input_data=sample_data["input"],
                    expected_output=sample_data.get("expected_output"),
                    metadata=sample_data.get("metadata", {}),
                    category=sample_data.get("category"),
                    complexity=sample_data.get("complexity", "medium"),
                    weight=sample_data.get("weight", 1.0)
                )
                samples.append(sample)
        
        # Generate samples using generator
        elif self.sample_generator:
            samples = self._generate_samples()
        
        return samples
    
    def _generate_samples(self) -> List[BenchmarkSample]:
        """Generate samples using sample generator."""
        # Implementation depends on sample generator
        pass
    
    def evaluate_sample(
        self, 
        sample: BenchmarkSample, 
        agent_output: Any
    ) -> Dict[str, float]:
        """Evaluate sample using custom evaluation function."""
        if self.evaluation_function:
            return self.evaluation_function(sample, agent_output)
        else:
            return self._default_evaluation(sample, agent_output)
    
    def _default_evaluation(
        self, 
        sample: BenchmarkSample, 
        agent_output: Any
    ) -> Dict[str, float]:
        """Default evaluation function."""
        return {
            "accuracy": 1.0 if agent_output == sample.expected_output else 0.0,
            "success": 1.0 if agent_output is not None else 0.0
        }
```

## Benchmark Manager Interface

### Main Benchmark Manager

```python
class BenchmarkManager:
    """Main benchmark management interface."""
    
    def __init__(self, storage_path: str = "benchmarks/"):
        self.storage_path = storage_path
        self.loaded_benchmarks: Dict[str, Benchmark] = {}
        self.registry = BenchmarkRegistry()
        self.public_loader = PublicBenchmarkLoader()
    
    def load(self, benchmark_name: str) -> Benchmark:
        """Load a benchmark by name, prioritizing public benchmarks."""
        if benchmark_name in self.loaded_benchmarks:
            return self.loaded_benchmarks[benchmark_name]
        
        # Priority order: Public -> Predefined -> Custom
        if self.public_loader.is_supported(benchmark_name):
            benchmark = self._load_public(benchmark_name)
        elif self.registry.is_predefined(benchmark_name):
            benchmark = self._load_predefined(benchmark_name)
        else:
            benchmark = self._load_custom(benchmark_name)
        
        self.loaded_benchmarks[benchmark_name] = benchmark
        return benchmark
    
    def _load_public(self, benchmark_name: str) -> Benchmark:
        """Load a publicly available benchmark."""
        return self.public_loader.load_benchmark(benchmark_name)
    
    def load_custom(self, config_path: str) -> Benchmark:
        """Load custom benchmark from configuration file."""
        config = self._load_config(config_path)
        benchmark = CustomBenchmark(config["name"], config)
        self.loaded_benchmarks[config["name"]] = benchmark
        return benchmark
    
    def list_available(self) -> List[str]:
        """List all available benchmarks."""
        public = self.public_loader.list_supported()
        predefined = self.registry.list_predefined()
        custom = self._list_custom_benchmarks()
        return public + predefined + custom
    
    def get_benchmark_info(self, benchmark_name: str) -> Dict[str, Any]:
        """Get benchmark information."""
        benchmark = self.load(benchmark_name)
        return benchmark.get_benchmark_info()
    
    def validate_benchmark(self, benchmark_name: str) -> bool:
        """Validate benchmark configuration."""
        try:
            benchmark = self.load(benchmark_name)
            samples = benchmark.load_samples()
            return all(benchmark.validate_sample(sample) for sample in samples)
        except Exception:
            return False
    
    def _load_predefined(self, benchmark_name: str) -> Benchmark:
        """Load predefined benchmark."""
        benchmark_info = self.registry.get_predefined_info(benchmark_name)
        return PredefinedBenchmark(
            name=benchmark_name,
            dataset_path=benchmark_info["dataset_path"],
            description=benchmark_info["description"]
        )
    
    def _load_custom(self, benchmark_name: str) -> Benchmark:
        """Load custom benchmark."""
        config_path = f"{self.storage_path}/{benchmark_name}.json"
        return self.load_custom(config_path)
```

### Benchmark Registry

```python
class BenchmarkRegistry:
    """Registry for predefined benchmarks."""
    
    def __init__(self):
        self.predefined_benchmarks = {
            "code_generation": {
                "name": "Code Generation Benchmark",
                "description": "Benchmark for code generation capabilities",
                "dataset_path": "benchmarks/predefined/code_generation.json",
                "metrics": ["accuracy", "code_quality", "functionality"],
                "categories": ["algorithms", "data_structures", "apis"]
            },
            "text_analysis": {
                "name": "Text Analysis Benchmark",
                "description": "Benchmark for text analysis capabilities",
                "dataset_path": "benchmarks/predefined/text_analysis.json",
                "metrics": ["accuracy", "relevance", "coherence"],
                "categories": ["summarization", "classification", "extraction"]
            },
            "reasoning": {
                "name": "Reasoning Benchmark",
                "description": "Benchmark for reasoning capabilities",
                "dataset_path": "benchmarks/predefined/reasoning.json",
                "metrics": ["accuracy", "logical_consistency", "problem_solving"],
                "categories": ["mathematical", "logical", "commonsense"]
            }
        }
    
    def is_predefined(self, benchmark_name: str) -> bool:
        """Check if benchmark is predefined."""
        return benchmark_name in self.predefined_benchmarks
    
    def list_predefined(self) -> List[str]:
        """List all predefined benchmarks."""
        return list(self.predefined_benchmarks.keys())
    
    def get_predefined_info(self, benchmark_name: str) -> Dict[str, Any]:
        """Get predefined benchmark information."""
        if not self.is_predefined(benchmark_name):
            raise ValueError(f"Predefined benchmark '{benchmark_name}' not found")
        return self.predefined_benchmarks[benchmark_name]
    
    def register_predefined(self, name: str, info: Dict[str, Any]) -> None:
        """Register a new predefined benchmark."""
        self.predefined_benchmarks[name] = info
```

## Data Models and Schemas

### Benchmark Configuration Schema

```python
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union

class BenchmarkSampleSchema(BaseModel):
    """Schema for benchmark sample."""
    input: Any
    expected_output: Optional[Any] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    category: Optional[str] = None
    complexity: str = Field("medium", regex="^(low|medium|high)$")
    weight: float = Field(1.0, ge=0.0, le=10.0)

class BenchmarkConfigSchema(BaseModel):
    """Schema for benchmark configuration."""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field("", max_length=500)
    type: str = Field("custom", regex="^(predefined|custom|file_based|api_based)$")
    samples: List[BenchmarkSampleSchema] = Field(default_factory=list)
    metrics: List[str] = Field(default_factory=lambda: ["accuracy", "success"])
    evaluation_function: Optional[str] = None
    sample_generator: Optional[Dict[str, Any]] = None
    filters: Optional[Dict[str, Any]] = None
    
    @validator('samples')
    def validate_samples(cls, v):
        if not v:
            raise ValueError("At least one sample is required")
        return v
    
    @validator('metrics')
    def validate_metrics(cls, v):
        if not v:
            raise ValueError("At least one metric is required")
        return v

class PredefinedBenchmarkSchema(BaseModel):
    """Schema for predefined benchmark."""
    name: str
    description: str
    dataset_path: str
    metrics: List[str]
    categories: List[str]
    version: str = "1.0.0"
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
```

### Benchmark Result Schema

```python
class BenchmarkResultSchema(BaseModel):
    """Schema for benchmark result."""
    sample: BenchmarkSampleSchema
    agent_output: Any
    metrics: Dict[str, float] = Field(default_factory=dict)
    execution_time: float = Field(ge=0.0)
    success: bool
    error: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

class BenchmarkExecutionResultSchema(BaseModel):
    """Schema for complete benchmark execution result."""
    benchmark_name: str
    agent_id: str
    total_samples: int
    successful_samples: int
    failed_samples: int
    execution_time: float
    results: List[BenchmarkResultSchema]
    summary_metrics: Dict[str, float]
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
```

## Error Handling

### Benchmark Exceptions

```python
class BenchmarkError(Exception):
    """Base benchmark error."""
    pass

class BenchmarkNotFoundError(BenchmarkError):
    """Benchmark not found error."""
    pass

class BenchmarkValidationError(BenchmarkError):
    """Benchmark validation error."""
    pass

class BenchmarkExecutionError(BenchmarkError):
    """Benchmark execution error."""
    pass

class BenchmarkLoadError(BenchmarkError):
    """Benchmark loading error."""
    pass

class BenchmarkConfigError(BenchmarkError):
    """Benchmark configuration error."""
    pass
```

### Error Response Format

```python
@dataclass
class BenchmarkErrorResponse:
    """Standardized error response for benchmarks."""
    error_type: str
    error_message: str
    benchmark_name: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    suggestions: List[str] = field(default_factory=list)
```

## Integration Points

### Evaluation Engine Integration

```python
class EvaluationEngineIntegration:
    """Integration with evaluation engine."""
    
    def __init__(self, evaluation_engine, benchmark_manager):
        self.evaluation_engine = evaluation_engine
        self.benchmark_manager = benchmark_manager
    
    def run_benchmark_evaluation(
        self, 
        agent: Any, 
        benchmark_name: str,
        samples: Optional[int] = None
    ) -> Dict[str, Any]:
        """Run benchmark evaluation using evaluation engine."""
        benchmark = self.benchmark_manager.load(benchmark_name)
        
        if samples:
            benchmark_samples = benchmark.samples[:samples]
        else:
            benchmark_samples = benchmark.load_samples()
        
        results = []
        for sample in benchmark_samples:
            # Execute agent on sample
            execution_result = self.evaluation_engine.execute_agent(
                agent, sample.input_data
            )
            
            # Evaluate sample
            metrics = benchmark.evaluate_sample(
                sample, execution_result["output"]
            )
            
            result = BenchmarkResult(
                sample=sample,
                agent_output=execution_result["output"],
                metrics=metrics,
                execution_time=execution_result["execution_time"],
                success=execution_result["success"],
                error=execution_result.get("error")
            )
            results.append(result)
        
        return {
            "benchmark_name": benchmark_name,
            "total_samples": len(results),
            "successful_samples": len([r for r in results if r.success]),
            "results": results,
            "summary_metrics": self._calculate_summary_metrics(results)
        }
    
    def _calculate_summary_metrics(self, results: List[BenchmarkResult]) -> Dict[str, float]:
        """Calculate summary metrics from results."""
        if not results:
            return {}
        
        summary = {}
        for metric in results[0].metrics.keys():
            values = [r.metrics[metric] for r in results if metric in r.metrics]
            if values:
                summary[f"average_{metric}"] = sum(values) / len(values)
                summary[f"max_{metric}"] = max(values)
                summary[f"min_{metric}"] = min(values)
        
        return summary
```

### CLI Integration

```python
class BenchmarkCLI:
    """CLI interface for benchmark management."""
    
    def __init__(self, benchmark_manager: BenchmarkManager):
        self.benchmark_manager = benchmark_manager
    
    def list_benchmarks(self) -> None:
        """List available benchmarks."""
        benchmarks = self.benchmark_manager.list_available()
        print("Available benchmarks:")
        for benchmark_name in benchmarks:
            info = self.benchmark_manager.get_benchmark_info(benchmark_name)
            print(f"  {benchmark_name}: {info['description']}")
    
    def show_benchmark_info(self, benchmark_name: str) -> None:
        """Show detailed benchmark information."""
        try:
            info = self.benchmark_manager.get_benchmark_info(benchmark_name)
            print(f"Benchmark: {info['name']}")
            print(f"Description: {info['description']}")
            print(f"Sample count: {info['sample_count']}")
            print(f"Metrics: {', '.join(info['metrics'])}")
            if 'categories' in info:
                print(f"Categories: {', '.join(info['categories'])}")
        except Exception as e:
            print(f"Error: {e}")
    
    def validate_benchmark(self, benchmark_name: str) -> None:
        """Validate benchmark configuration."""
        if self.benchmark_manager.validate_benchmark(benchmark_name):
            print(f"Benchmark '{benchmark_name}' is valid")
        else:
            print(f"Benchmark '{benchmark_name}' is invalid")
```

## Performance Contracts

### Performance Requirements

```python
@dataclass
class BenchmarkPerformanceRequirements:
    """Performance requirements for benchmarks."""
    max_load_time: float = 5.0  # seconds
    max_execution_time: float = 300.0  # seconds
    max_memory_usage: int = 1024  # MB
    min_success_rate: float = 0.99
    max_concurrent_benchmarks: int = 5
```

### Performance Monitoring

```python
class BenchmarkPerformanceMonitor:
    """Performance monitoring for benchmarks."""
    
    def __init__(self):
        self.metrics = {}
        self.timers = {}
    
    def start_timer(self, operation: str) -> str:
        """Start timing an operation."""
        timer_id = f"{operation}_{int(time.time())}"
        self.timers[timer_id] = time.time()
        return timer_id
    
    def end_timer(self, timer_id: str) -> float:
        """End timing and return duration."""
        if timer_id in self.timers:
            duration = time.time() - self.timers[timer_id]
            del self.timers[timer_id]
            return duration
        return 0.0
    
    def record_metric(self, name: str, value: float, tags: Dict[str, str] = None):
        """Record a performance metric."""
        if name not in self.metrics:
            self.metrics[name] = []
        self.metrics[name].append({
            "value": value,
            "tags": tags or {},
            "timestamp": time.time()
        })
    
    def get_metrics(self) -> Dict[str, List[Dict]]:
        """Get all performance metrics."""
        return self.metrics.copy()
```

## Next Steps

1. **Implementation**: Implement the benchmark framework based on these interfaces
2. **Testing**: Create comprehensive tests for all interfaces
3. **Documentation**: Generate API documentation from interfaces
4. **Validation**: Validate interfaces with stakeholders
5. **Integration**: Integrate with evaluation engine and other components

---

**Note**: These interfaces represent the current understanding of the benchmark framework design. They should be reviewed and validated with the development team before implementation begins.
