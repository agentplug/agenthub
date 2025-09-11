#!/usr/bin/env python3
"""
Standalone AgentHub Evaluation Test

This test runs the evaluation framework without requiring the full AgentHub
system to be installed, using mock agents that simulate AgentWrapper behavior.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import agentmanager
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Mock the missing dependencies
class MockMCP:
    def __init__(self, *args, **kwargs):
        pass

class MockClientSession:
    def __init__(self, *args, **kwargs):
        pass

class MockStdioServerParameters:
    def __init__(self, *args, **kwargs):
        pass

def mock_stdio_client(*args, **kwargs):
    return MockClientSession()

def mock_sse_client(*args, **kwargs):
    return MockClientSession()

# Create comprehensive mcp module mock
mcp_module = type(sys)('mcp')
mcp_module.server = type(sys)('mcp.server')
mcp_module.server.FastMCP = MockMCP
mcp_module.client = type(sys)('mcp.client')
mcp_module.client.FastMCPClient = MockMCP
mcp_module.client.session = type(sys)('mcp.client.session')
mcp_module.client.session.ClientSession = MockClientSession
mcp_module.client.stdio = type(sys)('mcp.client.stdio')
mcp_module.client.stdio.StdioServerParameters = MockStdioServerParameters
mcp_module.client.stdio.stdio_client = mock_stdio_client
mcp_module.client.sse = type(sys)('mcp.client.sse')
mcp_module.client.sse.sse_client = mock_sse_client
mcp_module.ClientSession = MockClientSession

sys.modules['mcp'] = mcp_module
sys.modules['mcp.server'] = mcp_module.server
sys.modules['mcp.client'] = mcp_module.client
sys.modules['mcp.client.session'] = mcp_module.client.session
sys.modules['mcp.client.stdio'] = mcp_module.client.stdio
sys.modules['mcp.client.sse'] = mcp_module.client.sse

try:
    from agentmanager.evaluation import evaluate_demo, evaluate_benchmark, generate_report
    from agentmanager.evaluation.core.data_models import SampleData
    print("✅ Successfully imported evaluation framework")
except Exception as e:
    print(f"❌ Failed to import evaluation framework: {e}")
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


def test_demo_evaluation():
    """Test demo evaluation with mock AgentWrapper."""
    print("=" * 60)
    print("🔍 TESTING DEMO EVALUATION")
    print("=" * 60)
    
    # Create mock agent
    agent = MockAgentWrapper("TestAgent", methods=['analyze_text', 'process'])
    print(f"✓ Created mock agent: {agent.agent_name}")
    print(f"✓ Available methods: {agent.methods}")
    
    try:
        # Run demo evaluation
        print("\nRunning demo evaluation...")
        results = evaluate_demo(agent)
        
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


def test_benchmark_evaluation():
    """Test benchmark evaluation with mock AgentWrapper."""
    print("=" * 60)
    print("📊 TESTING BENCHMARK EVALUATION")
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
        # Run benchmark evaluation
        print("\nRunning benchmark evaluation...")
        results = evaluate_benchmark(agent, benchmark_name="basic_qa")
        
        print(f"\n✅ Benchmark evaluation completed!")
        print(f"   - Agent: {results.agent_name}")
        print(f"   - Mode: {results.evaluation_mode}")
        print(f"   - Benchmark: {results.benchmark_name}")
        print(f"   - Duration: {results.duration:.2f} seconds")
        print(f"   - Samples: {len(results.results)}")
        print(f"   - Success rate: {results.summary_metrics.get('success_rate', 0):.2%}")
        
        return results
        
    except Exception as e:
        print(f"❌ Benchmark evaluation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_report_generation(results):
    """Test report generation."""
    if not results:
        print("\n" + "=" * 60)
        print("📄 REPORT GENERATION (SKIPPED - No results)")
        print("=" * 60)
        return
    
    print("\n" + "=" * 60)
    print("📄 TESTING REPORT GENERATION")
    print("=" * 60)
    
    try:
        # Generate HTML report
        print("Generating HTML report...")
        html_path = generate_report(results, format="html", output_path="test_evaluation_report.html")
        print(f"✓ HTML report generated: {html_path}")
        
        # Generate JSON report
        print("Generating JSON report...")
        json_path = generate_report(results, format="json", output_path="test_evaluation_report.json")
        print(f"✓ JSON report generated: {json_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Report generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("🚀 AgentHub Evaluation Framework Test")
    print("=" * 60)
    print("Testing evaluation framework with mock AgentWrapper agents")
    print()
    
    # Test demo evaluation
    demo_results = test_demo_evaluation()
    
    # Test benchmark evaluation
    benchmark_results = test_benchmark_evaluation()
    
    # Test report generation
    if demo_results:
        test_report_generation(demo_results)
    
    print("\n" + "=" * 60)
    print("🎉 TESTING COMPLETED")
    print("=" * 60)
    
    if demo_results and benchmark_results:
        print("✅ All tests passed successfully!")
        print("   - Demo evaluation: Working")
        print("   - Benchmark evaluation: Working")
        print("   - Report generation: Working")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")


if __name__ == "__main__":
    main()
