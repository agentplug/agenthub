# AgentHub Tool Benchmarking System

A comprehensive benchmarking framework for evaluating the performance, accuracy, and reliability of AgentHub tools.

## Overview

This benchmarking system provides standardized testing and evaluation of both built-in tools and MCP tools in the AgentHub ecosystem. It measures performance across multiple dimensions including execution time, memory usage, accuracy, and reliability.

## Features

- **Multi-dimensional Metrics**: Performance, accuracy, reliability, and usability
- **Tool Coverage**: Built-in tools (web, document) and MCP tools
- **Automated Testing**: Comprehensive test suites with configurable parameters
- **Multiple Output Formats**: JSON, HTML, CSV reports with charts and analysis
- **CI/CD Integration**: Automated benchmarking in continuous integration
- **Quality Gates**: Performance thresholds and regression detection
- **Real-world Testing**: Both synthetic and real-world test scenarios

## Quick Start

### 1. Run Basic Benchmark

```bash
# Run all enabled tools
python examples/benchmarking/run_benchmarks.py

# Run specific tools
python examples/benchmarking/run_benchmarks.py --tools web_search,document_parse

# Quick benchmark (fewer tests)
python examples/benchmarking/run_benchmarks.py --quick
```

### 2. Custom Configuration

```bash
# Use custom config file
python examples/benchmarking/run_benchmarks.py --config my_config.yaml

# Specify output directory and formats
python examples/benchmarking/run_benchmarks.py --output results --format json,html,csv
```

### 3. Programmatic Usage

```python
from examples.benchmarking.tool_benchmark_example import ToolBenchmarker

# Create benchmarker
benchmarker = ToolBenchmarker()

# Run specific tool benchmarks
web_results = benchmarker.benchmark_web_search()
doc_results = benchmarker.benchmark_document_parse()

# Generate report
report = benchmarker.generate_report()
benchmarker.print_summary()
```

## Tool Categories

### Web Tools
- **web_search**: Multi-engine web search with relevance scoring
- **web_scrape**: Content extraction from web pages
- **web_summarize**: Text summarization of web content
- **web_analyze**: Content analysis and insights extraction

### Document Tools
- **document_parse**: Multi-format document parsing (TXT, MD, HTML, JSON, CSV, PDF, DOCX)
- **document_search**: Semantic search with vector similarity
- **document_chunk**: Intelligent text segmentation
- **document_extract_metadata**: Comprehensive metadata extraction

## Metrics Measured

### Performance Metrics
- **Execution Time**: Wall-clock time for tool execution
- **Memory Usage**: Peak and average memory consumption
- **CPU Utilization**: CPU usage during execution
- **Throughput**: Operations per second
- **Latency**: Response time distribution (P50, P95, P99)

### Accuracy Metrics
- **Precision**: Correct results / Total results
- **Recall**: Correct results / Expected results
- **F1 Score**: Harmonic mean of precision and recall
- **Semantic Similarity**: For search and analysis tools
- **Content Quality**: For parsing and extraction tools

### Reliability Metrics
- **Success Rate**: Successful operations / Total operations
- **Error Handling**: Graceful failure handling
- **Consistency**: Result consistency across multiple runs
- **Stability**: Performance over extended periods

### Usability Metrics
- **API Simplicity**: Ease of use and parameter clarity
- **Error Messages**: Clarity and helpfulness of error messages
- **Integration Complexity**: Ease of integration with agents

## Configuration

### Basic Configuration

```yaml
# benchmark_config.yaml
benchmark:
  name: "AgentHub Tool Performance Benchmark"
  timeout: 300
  max_retries: 3

tools:
  web_search:
    enabled: true
    test_queries:
      - "Python programming tutorial"
      - "Machine learning best practices"
    engines: ["duckduckgo", "google"]
    max_results: 5

  document_parse:
    enabled: true
    test_files:
      - type: "txt"
        content: "sample_report.txt"
    extract_metadata: true
    extract_tables: true

thresholds:
  execution_time:
    excellent: 1.0
    good: 3.0
    acceptable: 10.0
    poor: 30.0
  
  accuracy:
    excellent: 0.95
    good: 0.85
    acceptable: 0.75
    poor: 0.60
```

### Advanced Configuration

```yaml
# Advanced settings
test_data:
  synthetic:
    enabled: true
    document_count: 100
    query_count: 50
    
  stress_testing:
    enabled: true
    concurrent_requests: 10
    duration_minutes: 5

quality_evaluation:
  search_relevance:
    method: "semantic_similarity"
    model: "all-MiniLM-L6-v2"
    threshold: 0.7

ci_cd:
  enabled: true
  quality_gates:
    min_success_rate: 0.90
    max_avg_execution_time: 10.0
    min_avg_accuracy: 0.80
```

## Test Suites

### Web Tools Test Suite

#### Search Tests
- Query diversity testing (factual, exploratory, technical)
- Result quality evaluation (relevance, freshness, diversity)
- Rate limiting and throttling behavior
- Error handling with invalid queries

#### Scraping Tests
- Content extraction accuracy across page types
- Robustness with malformed HTML and dynamic content
- Anti-bot measure handling
- Performance with large pages and concurrent requests

### Document Tools Test Suite

#### Parsing Tests
- Format support across all supported types
- Content preservation accuracy
- Metadata extraction quality
- Error handling with corrupted files

#### Search Tests
- Semantic search accuracy with various queries
- Performance with large document collections
- Relevance ranking and scoring
- Scalability with growing collections

## Output Formats

### JSON Report
```json
{
  "timestamp": "2024-01-15T10:30:00",
  "total_tests": 25,
  "tools": {
    "web_search": {
      "total_tests": 5,
      "successful_tests": 5,
      "success_rate": 1.0,
      "average_execution_time": 2.3,
      "average_accuracy": 0.87,
      "test_details": [...]
    }
  }
}
```

### HTML Report
- Interactive web-based reports with charts
- Tool comparison matrices
- Performance trend analysis
- Executive summary and detailed results

### CSV Report
- Tabular data for spreadsheet analysis
- Individual test results
- Aggregated metrics by tool
- Machine-readable format for further processing

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/benchmark.yml
name: Tool Benchmarking
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run benchmarks
        run: python examples/benchmarking/run_benchmarks.py
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: benchmark-results
          path: benchmark_results/
```

### Quality Gates

- **Performance Regression**: Detect performance degradation
- **Accuracy Thresholds**: Ensure minimum accuracy standards
- **Reliability Requirements**: Validate success rate requirements
- **Usability Standards**: Check API usability and documentation

## Advanced Features

### Stress Testing
- High-volume operation testing
- Memory leak detection
- Resource exhaustion testing
- Concurrent request handling

### Comparative Analysis
- Built-in vs MCP tool comparison
- Different implementation comparison
- Cross-environment performance analysis
- Historical trend analysis

### Real-world Testing
- Production usage pattern simulation
- User feedback integration
- Error rate monitoring
- Performance tracking

## Best Practices

### 1. Regular Benchmarking
- Run benchmarks on every tool update
- Monitor performance trends over time
- Set up automated regression detection

### 2. Comprehensive Testing
- Test with diverse, realistic data
- Include edge cases and error conditions
- Validate across different environments

### 3. Performance Monitoring
- Track key metrics continuously
- Set up alerts for performance degradation
- Monitor resource usage patterns

### 4. Quality Assurance
- Maintain high test coverage
- Validate accuracy with ground truth data
- Ensure consistent, reliable results

## Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Ensure project root is in Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

#### 2. Missing Dependencies
```bash
# Install required packages
pip install sentence-transformers psutil requests beautifulsoup4
```

#### 3. Memory Issues
```bash
# Run with memory monitoring
python -m memory_profiler examples/benchmarking/run_benchmarks.py
```

#### 4. Network Timeouts
```yaml
# Increase timeout in config
tools:
  web_search:
    timeout: 60
  web_scrape:
    timeout: 60
```

### Debug Mode

```bash
# Enable verbose output
python examples/benchmarking/run_benchmarks.py --verbose

# Run single tool for debugging
python examples/benchmarking/run_benchmarks.py --tools web_search --verbose
```

## Contributing

### Adding New Tools

1. Create tool-specific test class
2. Implement benchmark methods
3. Add configuration options
4. Update documentation

### Adding New Metrics

1. Define metric calculation logic
2. Add to metrics collector
3. Update report generation
4. Add to configuration schema

### Improving Test Data

1. Add realistic test datasets
2. Create synthetic data generators
3. Improve ground truth data
4. Expand test coverage

## Future Enhancements

- Machine learning-based performance prediction
- Anomaly detection in tool behavior
- Predictive maintenance for tool optimization
- Cross-platform performance comparison
- Third-party tool benchmarking
- Mobile-friendly reporting interface

## Support

For questions, issues, or contributions:

1. Check the troubleshooting section
2. Review existing issues on GitHub
3. Create a new issue with detailed information
4. Contribute improvements via pull requests

## License

This benchmarking system is part of the AgentHub project and follows the same license terms.
