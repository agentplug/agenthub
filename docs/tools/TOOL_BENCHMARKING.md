# Tool Benchmarking Guide

## Overview

This guide explains how to benchmark tools in AgentHub to ensure optimal performance, reliability, and resource usage. Proper benchmarking helps identify performance bottlenecks and ensures tools meet quality standards.

## Benchmarking Strategy

### 1. Performance Metrics

#### Response Time
- **Target**: < 2 seconds for most tools
- **Critical**: < 5 seconds for complex operations
- **Measurement**: Average, median, 95th percentile

#### Throughput
- **Target**: Handle 100+ requests per minute
- **Measurement**: Requests per second (RPS)
- **Load Testing**: Concurrent request handling

#### Resource Usage
- **Memory**: Peak memory consumption
- **CPU**: CPU usage during execution
- **Network**: Bandwidth utilization
- **Storage**: Disk I/O and temporary file usage

### 2. Reliability Metrics

#### Success Rate
- **Target**: > 99% success rate
- **Measurement**: Successful executions / Total executions
- **Error Analysis**: Categorize and track error types

#### Error Recovery
- **Timeout Handling**: Graceful timeout management
- **Retry Logic**: Automatic retry for transient failures
- **Fallback Mechanisms**: Alternative execution paths

## Benchmarking Framework

### Basic Benchmark Template

```python
import time
import statistics
from typing import List, Dict, Any

class ToolBenchmark:
    def __init__(self, tool_func, tool_name: str):
        self.tool_func = tool_func
        self.tool_name = tool_name
        self.results = []
    
    def run_benchmark(
        self, 
        test_cases: List[Dict[str, Any]], 
        iterations: int = 100
    ) -> Dict[str, Any]:
        """Run benchmark tests on the tool."""
        results = {
            "tool_name": self.tool_name,
            "test_cases": [],
            "summary": {}
        }
        
        for test_case in test_cases:
            case_results = self._run_test_case(test_case, iterations)
            results["test_cases"].append(case_results)
        
        results["summary"] = self._calculate_summary(results["test_cases"])
        return results
    
    def _run_test_case(self, test_case: Dict[str, Any], iterations: int) -> Dict[str, Any]:
        """Run a single test case multiple times."""
        args = test_case["args"]
        expected_success = test_case.get("expected_success", True)
        
        times = []
        successes = 0
        errors = []
        
        for _ in range(iterations):
            start_time = time.time()
            try:
                result = self.tool_func(**args)
                end_time = time.time()
                
                times.append(end_time - start_time)
                
                if result.get("success", False) == expected_success:
                    successes += 1
                else:
                    errors.append(f"Unexpected result: {result}")
                    
            except Exception as e:
                end_time = time.time()
                times.append(end_time - start_time)
                errors.append(str(e))
        
        return {
            "test_name": test_case["name"],
            "iterations": iterations,
            "success_rate": successes / iterations,
            "avg_time": statistics.mean(times),
            "median_time": statistics.median(times),
            "p95_time": self._percentile(times, 95),
            "min_time": min(times),
            "max_time": max(times),
            "errors": errors[:5]  # First 5 errors
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data."""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def _calculate_summary(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall summary statistics."""
        all_times = []
        all_success_rates = []
        
        for case in test_cases:
            all_times.extend([case["avg_time"]])
            all_success_rates.append(case["success_rate"])
        
        return {
            "overall_avg_time": statistics.mean(all_times),
            "overall_success_rate": statistics.mean(all_success_rates),
            "total_test_cases": len(test_cases),
            "performance_grade": self._grade_performance(all_times, all_success_rates)
        }
    
    def _grade_performance(self, times: List[float], success_rates: List[float]) -> str:
        """Grade overall performance."""
        avg_time = statistics.mean(times)
        avg_success = statistics.mean(success_rates)
        
        if avg_success >= 0.99 and avg_time <= 1.0:
            return "A"
        elif avg_success >= 0.95 and avg_time <= 2.0:
            return "B"
        elif avg_success >= 0.90 and avg_time <= 5.0:
            return "C"
        else:
            return "D"
```

### Web Search Tool Benchmark

```python
from agenthub.core.tools.builtin.web.search import web_search

# Define test cases
test_cases = [
    {
        "name": "simple_query",
        "args": {"query": "Python programming"},
        "expected_success": True
    },
    {
        "name": "complex_query",
        "args": {"query": "machine learning artificial intelligence deep learning"},
        "expected_success": True
    },
    {
        "name": "empty_query",
        "args": {"query": ""},
        "expected_success": False
    },
    {
        "name": "special_characters",
        "args": {"query": "C++ & Java @#$%"},
        "expected_success": True
    }
]

# Run benchmark
benchmark = ToolBenchmark(web_search, "web_search")
results = benchmark.run_benchmark(test_cases, iterations=50)
print(f"Benchmark Results: {results['summary']}")
```

## Tool-Specific Benchmarks

### Web Search Tool

#### Performance Targets
- **Response Time**: < 5 seconds (network dependent)
- **Success Rate**: > 95%
- **Concurrent Requests**: Handle 10+ simultaneous requests

#### Test Cases
```python
web_search_tests = [
    # Basic functionality
    {"query": "Python", "expected_results": 5},
    {"query": "machine learning", "expected_results": 5},
    
    # Edge cases
    {"query": "", "expected_error": True},
    {"query": "x" * 1000, "expected_results": 5},  # Long query
    
    # Special characters
    {"query": "C++ programming", "expected_results": 5},
    {"query": "@#$%^&*()", "expected_results": 5},
]
```

### File Operations Tool

#### Performance Targets
- **Response Time**: < 100ms for small files
- **Success Rate**: > 99%
- **File Size Limit**: Handle files up to 100MB

#### Test Cases
```python
file_ops_tests = [
    # Basic operations
    {"operation": "write", "path": "/tmp/test.txt", "content": "test"},
    {"operation": "read", "path": "/tmp/test.txt"},
    {"operation": "exists", "path": "/tmp/test.txt"},
    {"operation": "delete", "path": "/tmp/test.txt"},
    
    # Edge cases
    {"operation": "read", "path": "/nonexistent.txt", "expected_error": True},
    {"operation": "write", "path": "/invalid/path/file.txt", "expected_error": True},
]
```

### RAG Query Tool

#### Performance Targets
- **Response Time**: < 3 seconds
- **Success Rate**: > 95%
- **Result Relevance**: > 80% relevance score

#### Test Cases
```python
rag_query_tests = [
    # Knowledge queries
    {"query": "What is machine learning?", "expected_results": 5},
    {"query": "Python best practices", "expected_results": 5},
    
    # Context queries
    {"query": "Explain this code", "context": "def hello(): print('world')"},
    
    # Edge cases
    {"query": "", "expected_error": True},
    {"query": "x" * 500, "expected_results": 5},  # Long query
]
```

## Load Testing

### Concurrent Request Testing

```python
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

async def load_test_tool(tool_func, test_case, concurrent_requests: int = 10):
    """Test tool performance under concurrent load."""
    
    async def single_request():
        start_time = time.time()
        try:
            result = tool_func(**test_case["args"])
            end_time = time.time()
            return {
                "success": True,
                "time": end_time - start_time,
                "result": result
            }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "time": end_time - start_time,
                "error": str(e)
            }
    
    # Run concurrent requests
    tasks = [single_request() for _ in range(concurrent_requests)]
    results = await asyncio.gather(*tasks)
    
    # Analyze results
    success_count = sum(1 for r in results if r["success"])
    times = [r["time"] for r in results]
    
    return {
        "concurrent_requests": concurrent_requests,
        "success_rate": success_count / concurrent_requests,
        "avg_response_time": statistics.mean(times),
        "max_response_time": max(times),
        "min_response_time": min(times)
    }

# Example usage
async def test_web_search_load():
    test_case = {"args": {"query": "Python programming"}}
    results = await load_test_tool(web_search, test_case, concurrent_requests=20)
    print(f"Load test results: {results}")
```

## Performance Monitoring

### Real-time Monitoring

```python
import psutil
import time
from contextlib import contextmanager

@contextmanager
def monitor_resources():
    """Monitor resource usage during tool execution."""
    # Get initial resource usage
    process = psutil.Process()
    initial_memory = process.memory_info().rss
    initial_cpu = process.cpu_percent()
    
    start_time = time.time()
    
    try:
        yield
    finally:
        end_time = time.time()
        final_memory = process.memory_info().rss
        final_cpu = process.cpu_percent()
        
        print(f"Execution time: {end_time - start_time:.2f}s")
        print(f"Memory usage: {initial_memory} -> {final_memory} bytes")
        print(f"CPU usage: {initial_cpu} -> {final_cpu}%")

# Usage
with monitor_resources():
    result = web_search("Python programming")
```

### Continuous Monitoring

```python
class ToolMonitor:
    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        self.metrics = []
    
    def record_execution(self, success: bool, execution_time: float, memory_usage: int):
        """Record tool execution metrics."""
        self.metrics.append({
            "timestamp": time.time(),
            "success": success,
            "execution_time": execution_time,
            "memory_usage": memory_usage
        })
    
    def get_performance_summary(self, time_window: int = 3600):
        """Get performance summary for the last hour."""
        cutoff_time = time.time() - time_window
        recent_metrics = [m for m in self.metrics if m["timestamp"] > cutoff_time]
        
        if not recent_metrics:
            return {"error": "No metrics in time window"}
        
        success_rate = sum(1 for m in recent_metrics if m["success"]) / len(recent_metrics)
        avg_time = statistics.mean([m["execution_time"] for m in recent_metrics])
        avg_memory = statistics.mean([m["memory_usage"] for m in recent_metrics])
        
        return {
            "tool_name": self.tool_name,
            "time_window": time_window,
            "total_executions": len(recent_metrics),
            "success_rate": success_rate,
            "avg_execution_time": avg_time,
            "avg_memory_usage": avg_memory
        }
```

## Benchmarking Best Practices

### 1. Test Environment
- **Consistent Environment**: Use the same hardware/software setup
- **Network Conditions**: Test with realistic network conditions
- **Resource Isolation**: Ensure no other processes interfere

### 2. Test Data
- **Realistic Data**: Use real-world data for testing
- **Edge Cases**: Test boundary conditions and error cases
- **Data Variety**: Test with different data types and sizes

### 3. Measurement Accuracy
- **Multiple Runs**: Run tests multiple times for statistical significance
- **Warm-up**: Allow system to warm up before benchmarking
- **Outlier Handling**: Identify and handle outliers appropriately

### 4. Reporting
- **Clear Metrics**: Report key performance indicators clearly
- **Comparative Analysis**: Compare against baseline and targets
- **Trend Analysis**: Track performance over time

## Performance Optimization

### Common Optimizations

#### 1. Caching
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def cached_operation(param: str) -> str:
    """Cache expensive operations."""
    # Expensive computation
    return result
```

#### 2. Connection Pooling
```python
import aiohttp

# Reuse HTTP connections
async with aiohttp.ClientSession() as session:
    # Multiple requests using same session
    pass
```

#### 3. Async Operations
```python
import asyncio

async def async_operation():
    """Use async for I/O operations."""
    await asyncio.sleep(0.1)  # Non-blocking operation
```

#### 4. Resource Limits
```python
import resource

# Set memory limits
resource.setrlimit(resource.RLIMIT_AS, (100 * 1024 * 1024, -1))  # 100MB limit
```

## Benchmark Results Interpretation

### Performance Grades

- **Grade A**: Excellent performance, meets all targets
- **Grade B**: Good performance, minor optimizations needed
- **Grade C**: Acceptable performance, improvements recommended
- **Grade D**: Poor performance, significant optimization required

### Action Items

#### Grade A
- Continue monitoring
- Document best practices
- Consider for production deployment

#### Grade B
- Optimize slow operations
- Review error handling
- Consider caching strategies

#### Grade C
- Major performance review
- Optimize critical paths
- Consider architectural changes

#### Grade D
- Complete redesign consideration
- Not recommended for production
- Significant development required

## Tools for Benchmarking

### Built-in Tools
- **time.time()**: Basic timing measurement
- **cProfile**: Python profiling
- **memory_profiler**: Memory usage analysis

### External Tools
- **Apache Bench**: HTTP load testing
- **JMeter**: Advanced load testing
- **Prometheus**: Metrics collection and monitoring
- **Grafana**: Metrics visualization

## Conclusion

Proper benchmarking ensures tools meet performance and reliability standards. Regular benchmarking helps identify performance regressions and optimization opportunities. Use this guide to establish benchmarking practices for all AgentHub tools.
