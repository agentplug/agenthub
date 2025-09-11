#!/usr/bin/env python3
"""
Direct Evaluation Framework Test

This test directly imports and tests the evaluation framework components
without going through the full AgentHub system.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Direct import of evaluation components
try:
    from agentmanager.evaluation.core.data_models import (
        EvaluationResults, AgentOutput, EvaluationContext, 
        EvaluationConfig, EvaluationMode, SampleData, MetricResult
    )
    from agentmanager.evaluation.core.evaluation_engine import (
        EvaluationEngine, DemoEvaluator, BenchmarkEvaluator
    )
    print("✅ Successfully imported evaluation framework components")
except Exception as e:
    print(f"❌ Failed to import evaluation components: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


class MockAgentWrapper:
    """Mock AgentWrapper that simulates AgentHub agent behavior."""
    
    def __init__(self, name="MockAgent", methods=None, tools=None):
        self.agent_name = name
        self.methods = methods or ['analyze_text', 'process']
        self.assigned_tools = tools or []
        self.namespace = "mock"
        self.version = "1.0.0"
        self.description = "Mock agent for testing"
    
    def execute(self, method_name, parameters):
        """Execute a method with parameters."""
        if method_name not in self.methods:
            raise ValueError(f"Method '{method_name}' not available")
        
        # Simulate different responses based on method and input
        input_text = parameters.get('text', parameters.get('input', ''))
        
        if method_name == 'analyze_text':
            return {
                'result': f"Analysis of: {input_text[:50]}...",
                'summary': f"Mock analysis completed for: {input_text[:30]}...",
                'confidence': 0.85
            }
        elif method_name == 'generate_code':
            return {
                'result': f"# Generated code for: {input_text[:50]}...\nprint('Hello World')",
                'language': 'python',
                'complexity': 'simple'
            }
        elif method_name == 'process':
            return f"Processed: {input_text}"
        else:
            return f"Mock response for {method_name}: {input_text}"
    
    def get_method_info(self, method_name):
        """Get method information."""
        if method_name == 'analyze_text':
            return {
                'parameters': {
                    'text': {'type': 'string', 'description': 'Text to analyze'}
                },
                'description': 'Analyze text content'
            }
        elif method_name == 'generate_code':
            return {
                'parameters': {
                    'prompt': {'type': 'string', 'description': 'Code generation prompt'}
                },
                'description': 'Generate code based on prompt'
            }
        else:
            return {
                'parameters': {
                    'input': {'type': 'string', 'description': 'Input text'}
                },
                'description': f'Execute {method_name} method'
            }
    
    def has_method(self, method_name):
        """Check if method exists."""
        return method_name in self.methods


def test_demo_evaluator():
    """Test the DemoEvaluator directly."""
    print("=" * 60)
    print("🔍 TESTING DEMO EVALUATOR")
    print("=" * 60)
    
    # Create mock agent
    agent = MockAgentWrapper("TestAgent", methods=['analyze_text', 'process'])
    print(f"✓ Created mock agent: {agent.agent_name}")
    print(f"✓ Available methods: {agent.methods}")
    
    try:
        # Create evaluator
        config = EvaluationConfig(mode=EvaluationMode.DEMO, sample_count=3)
        evaluator = DemoEvaluator(config)
        
        # Run evaluation
        print("\nRunning demo evaluation...")
        results = evaluator.evaluate(agent)
        
        print(f"\n✅ Demo evaluation completed!")
        print(f"   - Agent: {results.agent_name}")
        print(f"   - Mode: {results.evaluation_mode}")
        print(f"   - Duration: {results.duration:.2f} seconds")
        print(f"   - Samples: {len(results.results)}")
        print(f"   - Success rate: {results.summary_metrics.get('success_rate', 0):.2%}")
        
        # Show sample results
        print(f"\n📝 Sample Results:")
        for i, result in enumerate(results.results[:2]):  # Show first 2
            print(f"   Sample {i+1}:")
            print(f"     Input: {result.agent_output.input_text[:60]}...")
            print(f"     Output: {result.agent_output.output_text[:60]}...")
            print(f"     Method: {result.agent_output.metadata.get('method_used', 'Unknown')}")
            print()
        
        return results
        
    except Exception as e:
        print(f"❌ Demo evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_benchmark_evaluator():
    """Test the BenchmarkEvaluator directly."""
    print("=" * 60)
    print("📊 TESTING BENCHMARK EVALUATOR")
    print("=" * 60)
    
    # Create mock agent with tools
    agent = MockAgentWrapper(
        "TestAgentWithTools", 
        methods=['generate_code', 'analyze_text'],
        tools=['web_search', 'file_operations']
    )
    print(f"✓ Created mock agent: {agent.agent_name}")
    print(f"✓ Available methods: {agent.methods}")
    print(f"✓ Assigned tools: {agent.assigned_tools}")
    
    try:
        # Create evaluator
        config = EvaluationConfig(mode=EvaluationMode.BENCHMARK, sample_count=3)
        evaluator = BenchmarkEvaluator(config)
        
        # Run evaluation
        print("\nRunning benchmark evaluation...")
        results = evaluator.evaluate(agent)
        
        print(f"\n✅ Benchmark evaluation completed!")
        print(f"   - Agent: {results.agent_name}")
        print(f"   - Mode: {results.evaluation_mode}")
        print(f"   - Duration: {results.duration:.2f} seconds")
        print(f"   - Samples: {len(results.results)}")
        print(f"   - Success rate: {results.summary_metrics.get('success_rate', 0):.2%}")
        
        return results
        
    except Exception as e:
        print(f"❌ Benchmark evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_evaluation_engine():
    """Test the main EvaluationEngine."""
    print("=" * 60)
    print("🚀 TESTING EVALUATION ENGINE")
    print("=" * 60)
    
    # Create mock agent
    agent = MockAgentWrapper("TestAgent", methods=['analyze_text'])
    print(f"✓ Created mock agent: {agent.agent_name}")
    
    try:
        # Create engine
        config = EvaluationConfig(mode=EvaluationMode.DEMO, sample_count=2)
        engine = EvaluationEngine(config)
        
        # Run evaluation
        print("\nRunning evaluation engine...")
        results = engine.evaluate(agent, mode=EvaluationMode.DEMO)
        
        print(f"\n✅ Evaluation engine completed!")
        print(f"   - Agent: {results.agent_name}")
        print(f"   - Mode: {results.evaluation_mode}")
        print(f"   - Duration: {results.duration:.2f} seconds")
        print(f"   - Samples: {len(results.results)}")
        
        return results
        
    except Exception as e:
        print(f"❌ Evaluation engine failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Run all tests."""
    print("🚀 AgentHub Evaluation Framework Direct Test")
    print("=" * 60)
    print("Testing evaluation framework components directly")
    print()
    
    # Test demo evaluator
    demo_results = test_demo_evaluator()
    
    # Test benchmark evaluator
    benchmark_results = test_benchmark_evaluator()
    
    # Test evaluation engine
    engine_results = test_evaluation_engine()
    
    print("\n" + "=" * 60)
    print("🎉 TESTING COMPLETED")
    print("=" * 60)
    
    success_count = sum([1 for r in [demo_results, benchmark_results, engine_results] if r is not None])
    total_tests = 3
    
    if success_count == total_tests:
        print("✅ All tests passed successfully!")
        print("   - Demo evaluator: Working")
        print("   - Benchmark evaluator: Working")
        print("   - Evaluation engine: Working")
    else:
        print(f"⚠️ {success_count}/{total_tests} tests passed. Check the output above for details.")


if __name__ == "__main__":
    main()
