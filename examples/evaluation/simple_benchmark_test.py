#!/usr/bin/env python3
"""
Simple test for benchmark framework.
"""

import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def main():
    print("Starting benchmark test...")
    
    try:
        print("Importing PublicBenchmarkLoader...")
        from agentmanager.evaluation.benchmarks.public_benchmark_loader import PublicBenchmarkLoader
        print("✅ Import successful")
        
        print("Creating loader...")
        loader = PublicBenchmarkLoader()
        print("✅ Loader created")
        
        print("Listing supported benchmarks...")
        supported = loader.list_supported()
        print(f"✅ Supported benchmarks: {supported}")
        
        print("Loading HumanEval...")
        humaneval = loader.load_benchmark("humaneval")
        print(f"✅ Loaded HumanEval: {humaneval.name}")
        print(f"   Samples: {len(humaneval.samples)}")
        
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
