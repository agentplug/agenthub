# AgentHub Evaluation Examples

This directory contains examples demonstrating how to use the AgentHub evaluation system for assessing AI agent performance.

## Examples Overview

### 1. Quick Evaluation Demo (`quick_evaluation_demo.py`)
**Purpose**: Basic introduction to the evaluation system  
**Difficulty**: Beginner  
**Duration**: 5-10 minutes  

This example demonstrates:
- Basic agent evaluation in demo mode
- Benchmark evaluation
- Simple report generation
- Available evaluation options

**Run it:**
```bash
python examples/evaluation/quick_evaluation_demo.py
```

### 2. Advanced Evaluation Example (`advanced_evaluation_example.py`)
**Purpose**: Comprehensive evaluation features  
**Difficulty**: Intermediate  
**Duration**: 15-20 minutes  

This example demonstrates:
- Custom benchmark creation
- Multiple agent evaluation
- Comparative analysis
- Detailed reporting
- Benchmark management

**Run it:**
```bash
python examples/evaluation/advanced_evaluation_example.py
```

### 3. Integration Example (`integration_example.py`)
**Purpose**: Integration with existing workflows  
**Difficulty**: Intermediate  
**Duration**: 10-15 minutes  

This example demonstrates:
- Integration with existing AgentHub agents
- Custom evaluation workflows
- Continuous evaluation monitoring
- Automated reporting

**Run it:**
```bash
python examples/evaluation/integration_example.py
```

### 4. AgentHub Agent Evaluation (`agenthub_agent_evaluation.py`)
**Purpose**: Evaluate prebuilt AgentHub agents  
**Difficulty**: Beginner to Intermediate  
**Duration**: 15-20 minutes  

This example demonstrates:
- Evaluating prebuilt agents (analysis-agent, coding-agent, scientific-paper-analyzer)
- AgentWrapper interface support
- Tool-aware evaluation
- Custom evaluation configurations
- Agent comparison
- Report generation

**Run it:**
```bash
python examples/evaluation/agenthub_agent_evaluation.py
```

### 5. Simple AgentHub Evaluation (`simple_agenthub_evaluation.py`)
**Purpose**: Quick evaluation of AgentHub agents  
**Difficulty**: Beginner  
**Duration**: 5 minutes  

This example demonstrates:
- Basic AgentHub agent evaluation
- Simple demo mode usage
- Quick results overview

**Run it:**
```bash
python examples/evaluation/simple_agenthub_evaluation.py
```

## Quick Start

### Basic Evaluation
```python
from agentmanager import load_agent, evaluate

# Load an agent
agent = load_agent("your/agent")

# Run demo evaluation
results = evaluate(agent, mode="demo")

# Check results
print(f"Success rate: {results.success_rate:.2%}")
print(f"Duration: {results.duration:.2f}s")
```

### Benchmark Evaluation
```python
from agentmanager import evaluate_benchmark

# Run benchmark evaluation
results = evaluate_benchmark(agent, benchmark_name="basic_qa")

# Generate report
from agentmanager import generate_report
report = generate_report(results, format_type="html")
```

### Custom Evaluation
```python
from agentmanager.evaluation import SampleData, EvaluationConfig

# Create custom samples
samples = [
    SampleData(
        input_text="What is the capital of France?",
        expected_output="Paris",
        difficulty="easy",
        category="geography"
    )
]

# Run custom evaluation
results = evaluate(agent, mode="demo", samples=samples)
```

## Available Features

### Evaluation Modes
- **Demo Mode**: Quick assessment with 5 sample questions
- **Benchmark Mode**: Comprehensive testing with predefined benchmarks

### Predefined Benchmarks
- `basic_qa`: Basic question and answer
- `math`: Mathematics problems
- `creative_writing`: Creative writing tasks
- `code_generation`: Programming challenges

### Metrics
- **Accuracy**: Exact match, partial match, keyword overlap
- **Quality**: Relevance, coherence, clarity, completeness
- **Performance**: Response time, throughput, resource usage
- **Reliability**: Error detection, consistency, stability

### Report Formats
- **HTML**: Rich, interactive web reports
- **JSON**: Machine-readable data export
- **Text**: Simple text-based reports

## Configuration Options

### EvaluationConfig
```python
from agentmanager.evaluation import EvaluationConfig

config = EvaluationConfig(
    mode="demo",                    # "demo" or "benchmark"
    sample_count=5,                 # Number of samples
    timeout_seconds=300,            # Timeout per evaluation
    parallel_processing=True,       # Enable parallel processing
    max_workers=4,                  # Number of worker threads
    cache_enabled=True,             # Enable result caching
    custom_metrics=None,            # Custom metrics to calculate
    benchmark_name=None             # Benchmark name for benchmark mode
)
```

### Custom Samples
```python
from agentmanager.evaluation import SampleData

sample = SampleData(
    input_text="Your question here",
    expected_output="Expected answer (optional)",
    difficulty="easy",              # "easy", "medium", "hard"
    category="your_category",       # Custom category
    context={"key": "value"}        # Additional context
)
```

## Best Practices

### 1. Start with Demo Mode
Begin with demo mode to quickly assess agent performance:
```python
results = evaluate(agent, mode="demo")
```

### 2. Use Appropriate Benchmarks
Choose benchmarks that match your agent's intended use case:
```python
# For Q&A agents
results = evaluate_benchmark(agent, "basic_qa")

# For creative agents
results = evaluate_benchmark(agent, "creative_writing")
```

### 3. Create Custom Benchmarks
For specific use cases, create custom benchmarks:
```python
from agentmanager.evaluation import CustomBenchmark, BenchmarkManager

# Create custom benchmark
benchmark = CustomBenchmark(
    name="my_custom_benchmark",
    samples=my_samples,
    metrics=["accuracy", "quality_score"]
)

# Register and use
manager = BenchmarkManager()
manager.register_benchmark(benchmark.to_definition())
```

### 4. Monitor Performance Over Time
Set up continuous evaluation to track improvements:
```python
# Evaluate different versions
v1_results = evaluate(agent_v1, mode="benchmark")
v2_results = evaluate(agent_v2, mode="benchmark")

# Compare results
print(f"V1 success rate: {v1_results.success_rate:.2%}")
print(f"V2 success rate: {v2_results.success_rate:.2%}")
```

### 5. Generate Comprehensive Reports
Use different report formats for different purposes:
```python
# HTML for human review
html_report = generate_report(results, "html")

# JSON for programmatic analysis
json_data = generate_report(results, "json")

# Text for simple summaries
text_report = generate_report(results, "text")
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure you're running from the correct directory
   - Check that AgentHub is properly installed

2. **Agent Loading Errors**
   - Verify agent name format: "namespace/agent"
   - Check that the agent exists in the registry

3. **Evaluation Timeouts**
   - Increase timeout_seconds in configuration
   - Check agent performance and complexity

4. **Memory Issues**
   - Reduce sample_count for large evaluations
   - Disable parallel_processing if needed

### Getting Help

- Check the main AgentHub documentation
- Review the evaluation system design documents
- Look at the example code for patterns
- Check error messages for specific guidance

## Next Steps

1. **Run the Examples**: Start with the quick demo to understand the basics
2. **Create Custom Benchmarks**: Define benchmarks for your specific use cases
3. **Integrate with Workflows**: Add evaluation to your development process
4. **Monitor Performance**: Set up continuous evaluation and monitoring
5. **Optimize Agents**: Use evaluation results to improve agent performance

## Contributing

To contribute new examples or improve existing ones:

1. Follow the existing code style and structure
2. Add comprehensive docstrings and comments
3. Include error handling and validation
4. Test examples with different agent types
5. Update this README with new examples

---

**Note**: These examples are designed to work with the AgentHub evaluation system. Make sure you have the latest version installed and that all dependencies are properly configured.
