#!/usr/bin/env python3
"""
Direct test of evaluation system components without AgentHub dependencies.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def test_direct_imports():
    """Test direct imports of evaluation modules."""
    print("Testing direct imports...")
    
    try:
        # Import directly from the evaluation module
        sys.path.insert(0, str(Path(__file__).parent / "agentmanager" / "evaluation"))
        
        from core.data_models import (
            EvaluationResults, AgentOutput, EvaluationContext, 
            MetricResult, MetricResults, EvaluationConfig, EvaluationMode,
            SampleData, BenchmarkDefinition
        )
        print("✓ Core data models imported successfully")
        
        from metrics.accuracy_metrics import AccuracyMetrics
        from metrics.quality_metrics import QualityMetrics
        from metrics.performance_metrics import PerformanceMetrics
        from metrics.reliability_metrics import ReliabilityMetrics
        print("✓ Metrics modules imported successfully")
        
        from benchmarks.benchmark_manager import BenchmarkManager
        print("✓ Benchmark manager imported successfully")
        
        from reporting.report_generator import ReportGenerator
        print("✓ Report generator imported successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Direct imports failed: {e}")
        return False


def test_data_models_direct():
    """Test data model creation directly."""
    print("\nTesting data models directly...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "agentmanager" / "evaluation"))
        from core.data_models import (
            AgentOutput, MetricResult, MetricResults, EvaluationResults,
            EvaluationMode, SampleData, BenchmarkDefinition
        )
        
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
        
        return True
        
    except Exception as e:
        print(f"✗ Data models test failed: {e}")
        return False


def test_metrics_direct():
    """Test metrics calculation directly."""
    print("\nTesting metrics calculation directly...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "agentmanager" / "evaluation"))
        from metrics.accuracy_metrics import AccuracyMetrics
        from metrics.quality_metrics import QualityMetrics
        from metrics.performance_metrics import PerformanceMetrics
        from metrics.reliability_metrics import ReliabilityMetrics
        
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


def test_benchmark_direct():
    """Test benchmark management directly."""
    print("\nTesting benchmark management directly...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "agentmanager" / "evaluation"))
        from benchmarks.benchmark_manager import BenchmarkManager
        
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


def test_reporting_direct():
    """Test report generation directly."""
    print("\nTesting report generation directly...")
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "agentmanager" / "evaluation"))
        from reporting.report_generator import ReportGenerator
        from core.data_models import (
            EvaluationResults, EvaluationMode, AgentOutput, MetricResult, MetricResults
        )
        
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
        with open("direct_test_report.html", "w", encoding="utf-8") as f:
            f.write(html_report)
        print("✓ HTML report saved to direct_test_report.html")
        
        with open("direct_test_report.json", "w", encoding="utf-8") as f:
            f.write(json_report)
        print("✓ JSON report saved to direct_test_report.json")
        
        return True
        
    except Exception as e:
        print(f"✗ Report generation test failed: {e}")
        return False


def main():
    """Run all direct tests."""
    print("🧪 AgentHub Evaluation System Direct Test")
    print("=" * 60)
    
    tests = [
        test_direct_imports,
        test_data_models_direct,
        test_metrics_direct,
        test_benchmark_direct,
        test_reporting_direct
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
        print("- direct_test_report.html (HTML report example)")
        print("- direct_test_report.json (JSON report example)")
    else:
        print("⚠ Some tests failed. Check the output above for details.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
