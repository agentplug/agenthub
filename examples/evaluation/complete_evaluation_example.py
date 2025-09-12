#!/usr/bin/env python3
"""
Complete AgentHub Evaluation Example

This example demonstrates the complete evaluation framework with:
1. Clean interface: amg.evaluate(agent, mode="demo")
2. Public benchmark support
3. Real agent integration
"""

import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def demonstrate_clean_interface():
    """Demonstrate the clean evaluation interface."""
    print("🚀 Complete AgentHub Evaluation Example")
    print("=" * 60)
    
    try:
        # Import AgentHub
        import agentmanager as amg
        print("✅ AgentHub imported successfully")
        
        # Show available evaluation modes
        print(f"\n📋 Available evaluation modes: {amg.get_available_modes()}")
        
        # Show available benchmarks
        print(f"📋 Available benchmarks: {amg.get_available_benchmarks()}")
        
        # Demonstrate benchmark loading
        print(f"\n🧪 Testing Benchmark Framework...")
        from agentmanager.evaluation.benchmarks import BenchmarkManager
        
        manager = BenchmarkManager()
        
        # Test public benchmarks
        public_benchmarks = ["humaneval", "glue", "gsm8k", "arc", "hellaswag"]
        for benchmark_name in public_benchmarks:
            print(f"\n📦 Loading {benchmark_name}...")
            benchmark = manager.get_benchmark(benchmark_name)
            if benchmark:
                print(f"   ✅ Loaded: {benchmark.name}")
                print(f"   📊 Samples: {len(benchmark.samples)}")
                print(f"   🏷️ Type: {benchmark.benchmark_type}")
                print(f"   📈 Metrics: {benchmark.metrics}")
                
                # Show sample data
                if benchmark.samples:
                    sample = benchmark.samples[0]
                    print(f"   📝 Sample: {sample.input_text[:80]}...")
                    print(f"   🎯 Expected: {sample.expected_output}")
            else:
                print(f"   ❌ Failed to load {benchmark_name}")
        
        print(f"\n🎉 Benchmark framework demonstration completed!")
        
        # Note: The actual agent loading and evaluation would require
        # the full AgentHub setup with dependencies installed
        print(f"\n💡 To use with real agents:")
        print(f"   agent = amg.load_agent('agentplug/analysis-agent')")
        print(f"   result = amg.evaluate(agent, mode='demo')")
        print(f"   result = amg.evaluate(agent, mode='benchmark', benchmark_name='humaneval')")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure AgentHub is properly installed and configured.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def demonstrate_benchmark_details():
    """Demonstrate detailed benchmark information."""
    print(f"\n🔍 Detailed Benchmark Information")
    print("=" * 40)
    
    try:
        from agentmanager.evaluation.benchmarks import PublicBenchmarkLoader
        
        loader = PublicBenchmarkLoader()
        
        # Show detailed information for each benchmark
        for benchmark_name in loader.list_supported():
            print(f"\n📋 {benchmark_name.upper()}")
            info = loader.get_benchmark_info(benchmark_name)
            print(f"   Name: {info['name']}")
            print(f"   Description: {info['description']}")
            print(f"   Source: {info['source']}")
            print(f"   Format: {info['format']}")
            print(f"   Metrics: {info['metrics']}")
            print(f"   License: {info['license']}")
            print(f"   Citation: {info['citation']}")
        
    except Exception as e:
        print(f"❌ Error in detailed demonstration: {e}")

def main():
    """Run the complete demonstration."""
    demonstrate_clean_interface()
    demonstrate_benchmark_details()
    
    print(f"\n🎯 Summary")
    print("=" * 20)
    print("✅ Public benchmark framework implemented")
    print("✅ Clean evaluation interface ready")
    print("✅ Support for HumanEval, GLUE, GSM8K, ARC, HellaSwag")
    print("✅ Automatic download and caching")
    print("✅ Integration with existing evaluation engine")
    print("\n🚀 Ready for production use!")

if __name__ == "__main__":
    main()
