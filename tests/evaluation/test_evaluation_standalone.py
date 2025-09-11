#!/usr/bin/env python3
"""
Standalone test for the evaluation system without AgentHub dependencies.
"""

import sys
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_evaluation_imports():
    """Test that evaluation modules can be imported independently."""
    print("Testing evaluation imports...")
    
    try:
        # Test core data models
        from agentmanager.evaluation.core.data_models import (
            EvaluationResults, AgentOutput, EvaluationContext, 
            MetricResult, MetricResults, EvaluationConfig, EvaluationMode,
            SampleData, BenchmarkDefinition
        )
        print("✓ Core data models imported successfully")
    except ImportError as e:
        print(f"✗ Core data models import failed: {e}")
        return False
    
    try:
        # Test metrics
        from agentmanager.evaluation.metrics.accuracy_metrics import AccuracyMetrics
        from agentmanager.evaluation.metrics.quality_metrics import QualityMetrics
        from agentmanager.evaluation.metrics.performance_metrics import PerformanceMetrics
        from agentmanager.evaluation.metrics.reliability_metrics import ReliabilityMetrics
        print("✓ Metrics modules imported successfully")
    except ImportError as e:
        print(f"✗ Metrics import failed: {e}")
        return False
    
    try:
        # Test benchmarks
        from agentmanager.evaluation.benchmarks.benchmark_manager import BenchmarkManager
        print("✓ Benchmark manager imported successfully")
    except ImportError as e:
        print(f"✗ Benchmark manager import failed: {e}")
        return False
    
    try:
        # Test reporting
        from agentmanager.evaluation.reporting.report_generator import ReportGenerator
        print("✓ Report generator imported successfully")
    except ImportError as e:
        print(f"✗ Report generator import failed: {e}")
        return False
    
    return True


def test_data_models():
    """Test data model creation and functionality."""
    print("\nTesting data models...")
    
    try:
        from agentmanager.evaluation.core.data_models import (
            AgentOutput, MetricResult, MetricResults, EvaluationResults,
            EvaluationMode, SampleData, BenchmarkDefinition
        )
        from datetime import datetime
        
        # Test AgentOutput creation
        agent_output = AgentOutput(
            input_text="Test input",
            output_text="Test output",
            timestamp=datetime.now()
        )
        print("✓ AgentOutput created successfully")
        
        # Test MetricResult creation
        metric_result = MetricResult(
            metric_type="test",
            value=0.95,
            timestamp=datetime.now()
        )
        print("✓ MetricResult created successfully")
        
        # Test MetricResults creation
        metric_results = MetricResults(
            agent_output=agent_output,
            metrics={"test_metric": metric_result},
            timestamp=datetime.now()
        )
        print("✓ MetricResults created successfully")
        
        # Test EvaluationResults creation
        results = EvaluationResults(
            agent_name="TestAgent",
            evaluation_mode=EvaluationMode.DEMO,
            results=[metric_results],
            summary_metrics={"test_avg": 0.95},
            timestamp=datetime.now(),
            duration=1.0
        )
        print("✓ EvaluationResults created successfully")
        print(f"  - Success rate: {results.success_rate:.2%}")
        print(f"  - Total evaluations: {results.total_evaluations}")
        
        # Test SampleData creation
        sample = SampleData(
            input_text="Test question",
            expected_output="Test answer",
            difficulty="easy",
            category="test"
        )
        print("✓ SampleData created successfully")
        
        # Test BenchmarkDefinition creation
        benchmark = BenchmarkDefinition(
            name="test_benchmark",
            description="Test benchmark",
            samples=[sample],
            metrics=["accuracy", "quality"]
        )
        print("✓ BenchmarkDefinition created successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Data models test failed: {e}")
        return False


def test_metrics_calculation():
    """Test metrics calculation functionality."""
    print("\nTesting metrics calculation...")
    
    try:
        from agentmanager.evaluation.metrics.accuracy_metrics import AccuracyMetrics
        from agentmanager.evaluation.metrics.quality_metrics import QualityMetrics
        from agentmanager.evaluation.metrics.performance_metrics import PerformanceMetrics
        from agentmanager.evaluation.metrics.reliability_metrics import ReliabilityMetrics
        
        # Test accuracy metrics
        exact_match = AccuracyMetrics.exact_match("Paris", "Paris")
        print(f"✓ Exact match calculation: {exact_match}")
        
        partial_match = AccuracyMetrics.partial_match("The capital is Paris", "Paris", threshold=0.5)
        print(f"✓ Partial match calculation: {partial_match}")
        
        keyword_overlap = AccuracyMetrics.keyword_overlap("Paris is the capital", "capital of France is Paris")
        print(f"✓ Keyword overlap calculation: {keyword_overlap}")
        
        # Test quality metrics
        relevance = QualityMetrics.relevance_score("Paris is the capital of France", "What is the capital of France?")
        print(f"✓ Relevance score calculation: {relevance}")
        
        coherence = QualityMetrics.coherence_score("Paris is the capital of France. It is a beautiful city.")
        print(f"✓ Coherence score calculation: {coherence}")
        
        clarity = QualityMetrics.clarity_score("Paris is the capital of France.")
        print(f"✓ Clarity score calculation: {clarity}")
        
        # Test performance metrics
        from datetime import datetime
        start_time = datetime.now()
        end_time = datetime.now()
        response_time = PerformanceMetrics.response_time(start_time, end_time)
        print(f"✓ Response time calculation: {response_time}")
        
        # Test reliability metrics
        consistency = ReliabilityMetrics.consistency_score(["Paris", "Paris", "Paris"])
        print(f"✓ Consistency score calculation: {consistency}")
        
        return True
        
    except Exception as e:
        print(f"✗ Metrics calculation test failed: {e}")
        return False


def test_benchmark_management():
    """Test benchmark management functionality."""
    print("\nTesting benchmark management...")
    
    try:
        from agentmanager.evaluation.benchmarks.benchmark_manager import BenchmarkManager
        
        # Create benchmark manager
        manager = BenchmarkManager()
        print("✓ Benchmark manager created")
        
        # Get available benchmarks
        benchmarks = manager.get_available_benchmarks()
        print(f"✓ Available benchmarks: {benchmarks}")
        
        # Test getting a specific benchmark
        if benchmarks:
            benchmark = manager.get_benchmark(benchmarks[0])
            if benchmark:
                print(f"✓ Retrieved benchmark: {benchmark.name}")
                print(f"  - Description: {benchmark.description}")
                print(f"  - Sample count: {len(benchmark.samples)}")
                print(f"  - Metrics: {benchmark.metrics}")
        
        return True
        
    except Exception as e:
        print(f"✗ Benchmark management test failed: {e}")
        return False


def test_report_generation():
    """Test report generation functionality."""
    print("\nTesting report generation...")
    
    try:
        from agentmanager.evaluation.reporting.report_generator import ReportGenerator
        from agentmanager.evaluation.core.data_models import (
            EvaluationResults, EvaluationMode, AgentOutput, MetricResult, MetricResults
        )
        from datetime import datetime
        
        # Create mock evaluation results
        agent_output = AgentOutput(
            input_text="What is the capital of France?",
            output_text="The capital of France is Paris.",
            timestamp=datetime.now()
        )
        
        metric_result = MetricResult(
            metric_type="accuracy",
            value=1.0,
            timestamp=datetime.now()
        )
        
        metric_results = MetricResults(
            agent_output=agent_output,
            metrics={"accuracy": metric_result},
            timestamp=datetime.now()
        )
        
        results = EvaluationResults(
            agent_name="TestAgent",
            evaluation_mode=EvaluationMode.DEMO,
            results=[metric_results],
            summary_metrics={"accuracy_avg": 1.0, "quality_score_avg": 0.95},
            timestamp=datetime.now(),
            duration=0.5
        )
        
        # Create report generator
        generator = ReportGenerator()
        print("✓ Report generator created")
        
        # Test HTML report generation
        html_report = generator.generate_report(results, "html")
        print(f"✓ HTML report generated ({len(html_report)} characters)")
        
        # Test JSON report generation
        json_report = generator.generate_report(results, "json")
        print(f"✓ JSON report generated ({len(json_report)} characters)")
        
        # Test text report generation
        text_report = generator.generate_report(results, "text")
        print(f"✓ Text report generated ({len(text_report)} characters)")
        
        # Save reports to files for inspection
        with open("test_report.html", "w", encoding="utf-8") as f:
            f.write(html_report)
        print("✓ HTML report saved to test_report.html")
        
        with open("test_report.json", "w", encoding="utf-8") as f:
            f.write(json_report)
        print("✓ JSON report saved to test_report.json")
        
        return True
        
    except Exception as e:
        print(f"✗ Report generation test failed: {e}")
        return False


def main():
    """Run all standalone tests."""
    print("🧪 AgentHub Evaluation System Standalone Test")
    print("=" * 60)
    
    tests = [
        test_evaluation_imports,
        test_data_models,
        test_metrics_calculation,
        test_benchmark_management,
        test_report_generation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The evaluation system is working correctly.")
        print("\nGenerated files:")
        print("- test_report.html (HTML report example)")
        print("- test_report.json (JSON report example)")
    else:
        print("⚠ Some tests failed. Check the output above for details.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
