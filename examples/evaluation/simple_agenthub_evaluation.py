#!/usr/bin/env python3
"""
Simple AgentHub Agent Evaluation
================================

A simple example showing how to evaluate AgentHub agents
using the evaluation framework.
"""

# Import evaluation components directly to avoid dependency issues
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "agentmanager" / "evaluation" / "core"))

from data_models import (
    EvaluationResults, AgentOutput, EvaluationContext, 
    EvaluationConfig, EvaluationMode, SampleData, MetricResult,
    MetricResults
)

# Try to import the full evaluation functions, fallback to direct implementation if needed
try:
    import agentmanager as amg
    from agentmanager.evaluation import evaluate_demo, evaluate_benchmark, generate_report
    EVALUATION_AVAILABLE = True
except ImportError:
    print("⚠️ Full AgentHub system not available, using mock evaluation")
    EVALUATION_AVAILABLE = False


def mock_evaluate_demo(agent, sample_count=5):
    """Mock evaluation function when full system is not available."""
    from datetime import datetime
    import time
    
    start_time = time.time()
    
    # Create sample data
    samples = [
        "What is the capital of France?",
        "Calculate 2 + 2",
        "Write a short poem about AI",
        "Explain machine learning",
        "What is the weather like today?"
    ]
    
    results = []
    for i, sample_text in enumerate(samples[:sample_count]):
        # Execute agent
        if hasattr(agent, 'execute') and hasattr(agent, 'methods'):
            # AgentWrapper style
            method_name = 'analyze_text' if 'analyze_text' in agent.methods else agent.methods[0]
            parameters = {'text': sample_text}
            result = agent.execute(method_name, parameters)
            output_text = str(result.get('result', result)) if isinstance(result, dict) else str(result)
        else:
            # Simple agent style
            output_text = agent.process(sample_text)
        
        # Create agent output
        agent_output = AgentOutput(
            input_text=sample_text,
            output_text=output_text,
            timestamp=datetime.now(),
            metadata={
                'method_used': getattr(agent, 'methods', ['process'])[0],
                'agent_type': 'AgentWrapper' if hasattr(agent, 'execute') else 'Simple'
            }
        )
        
        # Create metric result
        metric_result = MetricResult(
            metric_type="response_quality",
            value=0.8 + (i * 0.05),  # Simulate different scores
            confidence=0.9
        )
        
        # Create metric results
        metric_results = MetricResults(
            agent_output=agent_output,
            metrics={"response_quality": metric_result},
            timestamp=datetime.now()
        )
        
        results.append(metric_results)
    
    # Create evaluation results
    evaluation_results = EvaluationResults(
        agent_name=getattr(agent, 'agent_name', 'Unknown Agent'),
        evaluation_mode=EvaluationMode.DEMO,
        results=results,
        summary_metrics={
            "success_rate": 1.0,
            "average_quality": sum(r.metrics["response_quality"].value for r in results) / len(results)
        },
        timestamp=datetime.now(),
        duration=time.time() - start_time
    )
    
    return evaluation_results


class SimpleAgent:
    """A simple agent for demonstration purposes."""
    
    def __init__(self, name="SimpleAgent"):
        self.agent_name = name
        self.methods = ['analyze_text', 'process']
    
    def process(self, input_text):
        """Process input text and return a response."""
        input_lower = input_text.lower()
        
        if "capital" in input_lower and "france" in input_lower:
            return "The capital of France is Paris."
        elif "calculate" in input_lower and "2 + 2" in input_text:
            return "2 + 2 = 4"
        elif "poem" in input_lower:
            return "Here's a simple poem:\n\nRoses are red,\nViolets are blue,\nAI is amazing,\nAnd so are you!"
        else:
            return f"I received your message: '{input_text}'. I'm a simple agent that can help with basic questions."


def main():
    """Simple evaluation example."""
    print("🚀 Simple AgentHub Agent Evaluation")
    print("=" * 40)
    
    try:
        if EVALUATION_AVAILABLE:
            # Load an AgentHub agent
            print("📥 Loading analysis-agent...")
            agent = amg.load_agent("agentplug/analysis-agent")
            
            print(f"✅ Agent loaded: {agent.agent_name}")
            print(f"📋 Available methods: {agent.methods}")
            
            # Run demo evaluation
            print("\n🔍 Running demo evaluation...")
            results = evaluate_demo(agent)
        else:
            # Use mock agent
            print("📥 Creating mock analysis-agent...")
            agent = SimpleAgent("MockAnalysisAgent")
            
            print(f"✅ Mock agent created: {agent.agent_name}")
            print(f"📋 Available methods: {agent.methods}")
            
            # Run mock evaluation
            print("\n🔍 Running mock demo evaluation...")
            results = mock_evaluate_demo(agent)
        
        # Show results
        print(f"\n📊 Results:")
        print(f"   Samples evaluated: {len(results.results)}")
        print(f"   Duration: {results.duration:.2f} seconds")
        print(f"   Success rate: {results.summary_metrics.get('success_rate', 0):.2%}")
        
        # Show a sample result
        if results.results:
            sample = results.results[0]
            print(f"\n📝 Sample Result:")
            print(f"   Input: {sample.agent_output.input_text[:100]}...")
            print(f"   Output: {sample.agent_output.output_text[:100]}...")
            print(f"   Method used: {sample.agent_output.metadata.get('method_used', 'Unknown')}")
        
        print(f"\n✅ Evaluation completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you have AgentHub agents installed and accessible.")

if __name__ == "__main__":
    main()
