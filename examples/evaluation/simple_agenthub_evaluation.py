#!/usr/bin/env python3
"""
Simple AgentHub Agent Evaluation
================================

A simple example showing how to evaluate AgentHub agents
using the evaluation framework.
"""

import agentmanager as amg
from agentmanager.evaluation import evaluate_demo, evaluate_benchmark

def main():
    """Simple evaluation example."""
    print("🚀 Simple AgentHub Agent Evaluation")
    print("=" * 40)
    
    try:
        # Load an AgentHub agent
        print("📥 Loading analysis-agent...")
        agent = amg.load_agent("agentplug/analysis-agent")
        
        print(f"✅ Agent loaded: {agent.agent_name}")
        print(f"📋 Available methods: {agent.methods}")
        
        # Run demo evaluation
        print("\n🔍 Running demo evaluation...")
        results = evaluate_demo(agent)
        
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
