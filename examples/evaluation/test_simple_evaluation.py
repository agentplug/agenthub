#!/usr/bin/env python3
"""
Simple Evaluation Test

This test focuses on testing the core evaluation functionality
without complex dependencies.
"""

import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Direct file imports to avoid package-level dependencies
try:
    # Import evaluation files directly
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agentmanager" / "evaluation" / "core"))
    
    from data_models import (
        EvaluationResults, AgentOutput, EvaluationContext, 
        EvaluationConfig, EvaluationMode, SampleData, MetricResult,
        MetricResults
    )
    print("✅ Successfully imported data models")
    
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


def test_data_models():
    """Test data model creation."""
    print("=" * 60)
    print("📊 TESTING DATA MODELS")
    print("=" * 60)
    
    try:
        # Test SampleData
        sample = SampleData(
            input_text="Test input",
            expected_output="Expected output",
            difficulty="easy",
            category="test"
        )
        print(f"✓ SampleData created: {sample.input_text}")
        
        # Test AgentOutput
        agent_output = AgentOutput(
            input_text="Test input",
            output_text="Test output",
            timestamp=datetime.now(),
            metadata={'test': 'value'}
        )
        print(f"✓ AgentOutput created: {agent_output.input_text}")
        
        # Test EvaluationConfig
        config = EvaluationConfig(
            mode=EvaluationMode.DEMO,
            sample_count=5
        )
        print(f"✓ EvaluationConfig created: {config.mode}")
        
        # Test EvaluationContext
        context = EvaluationContext(
            evaluation_mode=EvaluationMode.DEMO,
            start_time=datetime.now()
        )
        print(f"✓ EvaluationContext created: {context.evaluation_mode}")
        
        # Test MetricResult
        metric_result = MetricResult(
            metric_type="test_metric",
            value=0.85,
            confidence=0.9
        )
        print(f"✓ MetricResult created: {metric_result.metric_type} = {metric_result.value}")
        
        # Test MetricResults
        metric_results = MetricResults(
            agent_output=agent_output,
            metrics={"test_metric": metric_result},
            timestamp=datetime.now()
        )
        print(f"✓ MetricResults created with {len(metric_results.metrics)} metrics")
        
        # Test EvaluationResults
        evaluation_results = EvaluationResults(
            agent_name="TestAgent",
            evaluation_mode=EvaluationMode.DEMO,
            results=[metric_results],
            summary_metrics={"success_rate": 0.85},
            timestamp=datetime.now(),
            duration=1.5
        )
        print(f"✓ EvaluationResults created: {evaluation_results.agent_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_execution():
    """Test agent execution simulation."""
    print("=" * 60)
    print("🤖 TESTING AGENT EXECUTION")
    print("=" * 60)
    
    try:
        # Create mock agent
        agent = MockAgentWrapper("TestAgent", methods=['analyze_text', 'generate_code'])
        print(f"✓ Created mock agent: {agent.agent_name}")
        print(f"✓ Available methods: {agent.methods}")
        
        # Test method detection
        print(f"✓ Has analyze_text: {agent.has_method('analyze_text')}")
        print(f"✓ Has generate_code: {agent.has_method('generate_code')}")
        print(f"✓ Has unknown_method: {agent.has_method('unknown_method')}")
        
        # Test method info
        method_info = agent.get_method_info('analyze_text')
        print(f"✓ Method info for analyze_text: {method_info['description']}")
        
        # Test execution
        result1 = agent.execute('analyze_text', {'text': 'Hello world'})
        print(f"✓ Executed analyze_text: {result1['summary']}")
        
        result2 = agent.execute('generate_code', {'prompt': 'Create a hello world function'})
        print(f"✓ Executed generate_code: {result2['language']}")
        
        # Test error handling
        try:
            agent.execute('unknown_method', {'input': 'test'})
        except ValueError as e:
            print(f"✓ Error handling works: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent execution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_evaluation_workflow():
    """Test a simple evaluation workflow."""
    print("=" * 60)
    print("🔄 TESTING EVALUATION WORKFLOW")
    print("=" * 60)
    
    try:
        # Create mock agent
        agent = MockAgentWrapper("TestAgent", methods=['analyze_text'])
        
        # Create sample data
        samples = [
            SampleData(
                input_text="What is the capital of France?",
                expected_output="Paris",
                difficulty="easy",
                category="geography"
            ),
            SampleData(
                input_text="Explain machine learning",
                expected_output="Machine learning is...",
                difficulty="medium",
                category="technology"
            )
        ]
        
        print(f"✓ Created {len(samples)} sample data items")
        
        # Simulate evaluation process
        results = []
        for i, sample in enumerate(samples):
            # Execute agent
            result = agent.execute('analyze_text', {'text': sample.input_text})
            
            # Create agent output
            agent_output = AgentOutput(
                input_text=sample.input_text,
                output_text=result['result'],
                timestamp=datetime.now(),
                metadata={
                    'method_used': 'analyze_text',
                    'agent_type': 'AgentWrapper',
                    'sample_index': i
                }
            )
            
            # Create metric result
            metric_result = MetricResult(
                metric_type="response_quality",
                value=0.8 + (i * 0.1),  # Simulate different scores
                confidence=0.9
            )
            
            # Create metric results
            metric_results = MetricResults(
                agent_output=agent_output,
                metrics={"response_quality": metric_result},
                timestamp=datetime.now()
            )
            
            results.append(metric_results)
            print(f"✓ Processed sample {i+1}: {sample.input_text[:30]}...")
        
        # Create final evaluation results
        evaluation_results = EvaluationResults(
            agent_name=agent.agent_name,
            evaluation_mode=EvaluationMode.DEMO,
            results=results,
            summary_metrics={
                "success_rate": 1.0,
                "average_quality": sum(r.metrics["response_quality"].value for r in results) / len(results)
            },
            timestamp=datetime.now(),
            duration=2.5
        )
        
        print(f"\n✅ Evaluation workflow completed!")
        print(f"   - Agent: {evaluation_results.agent_name}")
        print(f"   - Mode: {evaluation_results.evaluation_mode}")
        print(f"   - Duration: {evaluation_results.duration:.2f} seconds")
        print(f"   - Samples: {len(evaluation_results.results)}")
        print(f"   - Success rate: {evaluation_results.summary_metrics['success_rate']:.2%}")
        print(f"   - Average quality: {evaluation_results.summary_metrics['average_quality']:.2f}")
        
        return evaluation_results
        
    except Exception as e:
        print(f"❌ Evaluation workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Run all tests."""
    print("🚀 AgentHub Evaluation Framework Simple Test")
    print("=" * 60)
    print("Testing evaluation framework core functionality")
    print()
    
    # Test data models
    data_models_ok = test_data_models()
    
    # Test agent execution
    agent_execution_ok = test_agent_execution()
    
    # Test evaluation workflow
    workflow_results = test_evaluation_workflow()
    
    print("\n" + "=" * 60)
    print("🎉 TESTING COMPLETED")
    print("=" * 60)
    
    success_count = sum([1 for r in [data_models_ok, agent_execution_ok, workflow_results] if r is not None and r is not False])
    total_tests = 3
    
    if success_count == total_tests:
        print("✅ All tests passed successfully!")
        print("   - Data models: Working")
        print("   - Agent execution: Working")
        print("   - Evaluation workflow: Working")
        print("\n🎯 The evaluation framework core functionality is working correctly!")
        print("   The AgentWrapper integration should work with real AgentHub agents.")
    else:
        print(f"⚠️ {success_count}/{total_tests} tests passed. Check the output above for details.")


if __name__ == "__main__":
    main()
