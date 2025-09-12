#!/usr/bin/env python3
"""
Clean AgentHub Evaluation Example

This example demonstrates the clean, simple interface for evaluating agents:
    import agentmanager as amg
    agent = amg.load_agent("agentplug/analysis-agent")
    evaluation_result = amg.evaluate(agent, mode="demo")
"""

import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def main():
    """Run a clean evaluation example."""
    print("🚀 Clean AgentHub Evaluation Example")
    print("=" * 50)
    
    try:
        # Import AgentHub
        import agentmanager as amg
        print("✅ AgentHub imported successfully")
        
        # Test benchmark framework
        print("\n🧪 Testing Benchmark Framework...")
        from agentmanager.evaluation.benchmarks import BenchmarkManager
        
        manager = BenchmarkManager()
        available_benchmarks = manager.get_available_benchmarks()
        print(f"✅ Available benchmarks: {available_benchmarks}")
        
        # Test loading a public benchmark
        print("\n📦 Loading HumanEval benchmark...")
        humaneval = manager.get_benchmark("humaneval")
        if humaneval:
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
        else:
            print("❌ Failed to load HumanEval benchmark")
        
        # Test loading another benchmark
        print("\n📦 Loading GLUE benchmark...")
        glue = manager.get_benchmark("glue")
        if glue:
            print(f"✅ Loaded: {glue.name}")
            print(f"   Samples: {len(glue.samples)}")
            print(f"   Type: {glue.benchmark_type}")
        else:
            print("❌ Failed to load GLUE benchmark")
        
        print("\n🎉 Benchmark framework test completed successfully!")
        
        # Note: The actual agent loading and evaluation would require
        # the full AgentHub setup with dependencies installed
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure AgentHub is properly installed and configured.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
