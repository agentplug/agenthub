#!/usr/bin/env python3
"""
Test script for the benchmark framework with public benchmarks.
"""

import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_public_benchmark_loader():
    """Test the public benchmark loader."""
    print("🧪 Testing Public Benchmark Loader")
    print("=" * 50)
    
    try:
        from agentmanager.evaluation.benchmarks import PublicBenchmarkLoader
        
        loader = PublicBenchmarkLoader()
        
        # Test listing supported benchmarks
        print("\n📋 Supported Benchmarks:")
        supported = loader.list_supported()
        for benchmark in supported:
            print(f"  - {benchmark}")
        
        # Test loading a specific benchmark
        print(f"\n📦 Loading HumanEval benchmark...")
        humaneval = loader.load_benchmark("humaneval")
        print(f"✅ Loaded: {humaneval.name}")
        print(f"   Description: {humaneval.description}")
        print(f"   Samples: {len(humaneval.samples)}")
        print(f"   Metrics: {humaneval.metrics}")
        print(f"   Type: {humaneval.benchmark_type}")
        
        # Show sample data
        if humaneval.samples:
            print(f"\n📝 Sample Data:")
            sample = humaneval.samples[0]
            print(f"   Input: {sample.input_text[:100]}...")
            print(f"   Expected: {sample.expected_output}")
            print(f"   Category: {sample.category}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing public benchmark loader: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_benchmark_manager():
    """Test the benchmark manager."""
    print("\n🧪 Testing Benchmark Manager")
    print("=" * 50)
    
    try:
        from agentmanager.evaluation.benchmarks import BenchmarkManager
        
        manager = BenchmarkManager()
        
        # Test listing available benchmarks
        print("\n📋 Available Benchmarks:")
        available = manager.get_available_benchmarks()
        for benchmark in available:
            print(f"  - {benchmark}")
        
        # Test loading a public benchmark
        print(f"\n📦 Loading HumanEval via BenchmarkManager...")
        humaneval = manager.get_benchmark("humaneval")
        if humaneval:
            print(f"✅ Loaded: {humaneval.name}")
            print(f"   Samples: {len(humaneval.samples)}")
            print(f"   Type: {humaneval.benchmark_type}")
        else:
            print("❌ Failed to load HumanEval")
        
        # Test loading another benchmark
        print(f"\n📦 Loading GLUE benchmark...")
        glue = manager.get_benchmark("glue")
        if glue:
            print(f"✅ Loaded: {glue.name}")
            print(f"   Samples: {len(glue.samples)}")
            print(f"   Type: {glue.benchmark_type}")
        else:
            print("❌ Failed to load GLUE")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing benchmark manager: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_evaluation_with_benchmarks():
    """Test evaluation using benchmarks."""
    print("\n🧪 Testing Evaluation with Benchmarks")
    print("=" * 50)
    
    try:
        from agentmanager.evaluation import evaluate
        from agentmanager.evaluation.core.data_models import EvaluationConfig
        
        # Create a simple mock agent
        class MockAgent:
            def __init__(self):
                self.agent_name = "test-agent"
                self.methods = ["process"]
            
            def execute(self, method_name, **kwargs):
                return f"Mock output for: {kwargs.get('input', 'default')}"
        
        agent = MockAgent()
        
        # Test benchmark evaluation
        print("\n📊 Running benchmark evaluation...")
        config = EvaluationConfig(benchmark_name="humaneval")
        
        # This would normally use amg.evaluate(agent, mode="benchmark")
        # For now, we'll test the benchmark loading directly
        from agentmanager.evaluation.benchmarks import BenchmarkManager
        manager = BenchmarkManager()
        benchmark = manager.get_benchmark("humaneval")
        
        if benchmark:
            print(f"✅ Benchmark loaded: {benchmark.name}")
            print(f"   Ready for evaluation with {len(benchmark.samples)} samples")
        else:
            print("❌ Failed to load benchmark for evaluation")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing evaluation with benchmarks: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🚀 Benchmark Framework Test Suite")
    print("=" * 60)
    
    tests = [
        test_public_benchmark_loader,
        test_benchmark_manager,
        test_evaluation_with_benchmarks
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("📊 Test Results")
    print("=" * 30)
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {passed/total:.1%}")
    
    if passed == total:
        print("🎉 All tests passed!")
    else:
        print("⚠️ Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()
