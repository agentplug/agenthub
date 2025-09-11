#!/usr/bin/env python3
"""
AgentHub Agent Evaluation Examples
==================================

This example demonstrates how to use the evaluation framework
to evaluate prebuilt AgentHub agents like analysis-agent,
coding-agent, and scientific-paper-analyzer.

The evaluation framework now properly supports AgentWrapper
interface used by all AgentHub agents.
"""

import agentmanager as amg
from agentmanager.evaluation import (
    evaluate, 
    evaluate_demo, 
    evaluate_benchmark,
    generate_report,
    EvaluationConfig,
    EvaluationMode
)

def example_1_analysis_agent_demo():
    """Evaluate analysis-agent in demo mode."""
    print("🔍 Example 1: Analysis Agent Demo Evaluation")
    print("=" * 50)
    
    try:
        # Load the analysis agent
        agent = amg.load_agent("agentplug/analysis-agent")
        print(f"✅ Loaded agent: {agent.agent_name}")
        print(f"📋 Available methods: {agent.methods}")
        
        # Run demo evaluation
        results = evaluate_demo(agent)
        
        print(f"\n📊 Evaluation Results:")
        print(f"   Mode: {results.evaluation_mode}")
        print(f"   Samples evaluated: {len(results.results)}")
        print(f"   Duration: {results.duration:.2f} seconds")
        print(f"   Success rate: {results.summary_metrics.get('success_rate', 0):.2%}")
        
        # Show sample results
        print(f"\n📝 Sample Results:")
        for i, result in enumerate(results.results[:3]):  # Show first 3
            print(f"   Sample {i+1}:")
            print(f"     Input: {result.agent_output.input_text[:100]}...")
            print(f"     Output: {result.agent_output.output_text[:100]}...")
            print(f"     Method used: {result.agent_output.metadata.get('method_used', 'Unknown')}")
            print()
        
        return results
        
    except Exception as e:
        print(f"❌ Error evaluating analysis agent: {e}")
        return None

def example_2_coding_agent_with_tools():
    """Evaluate coding-agent with tools in demo mode."""
    print("💻 Example 2: Coding Agent with Tools Demo Evaluation")
    print("=" * 60)
    
    try:
        # Load coding agent with math tools
        agent = amg.load_agent("agentplug/coding-agent", tools=["add", "multiply"])
        print(f"✅ Loaded agent: {agent.agent_name}")
        print(f"📋 Available methods: {agent.methods}")
        print(f"🔧 Assigned tools: {agent.assigned_tools}")
        
        # Run demo evaluation
        results = evaluate_demo(agent)
        
        print(f"\n📊 Evaluation Results:")
        print(f"   Mode: {results.evaluation_mode}")
        print(f"   Samples evaluated: {len(results.results)}")
        print(f"   Duration: {results.duration:.2f} seconds")
        print(f"   Success rate: {results.summary_metrics.get('success_rate', 0):.2%}")
        
        # Show tool usage information
        tool_usage_count = 0
        for result in results.results:
            if result.agent_output.metadata.get('assigned_tools'):
                tool_usage_count += 1
        
        print(f"   Samples with tool access: {tool_usage_count}/{len(results.results)}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error evaluating coding agent: {e}")
        return None

def example_3_custom_evaluation_config():
    """Evaluate with custom configuration."""
    print("⚙️ Example 3: Custom Evaluation Configuration")
    print("=" * 50)
    
    try:
        # Load agent
        agent = amg.load_agent("agentplug/analysis-agent")
        
        # Create custom config
        config = EvaluationConfig(
            mode=EvaluationMode.DEMO,
            sample_count=5,
            parallel_processing=True,
            max_workers=2
        )
        
        # Run evaluation with custom config
        from agentmanager.evaluation.core.evaluation_engine import EvaluationEngine
        engine = EvaluationEngine(config)
        results = engine.evaluate(agent)
        
        print(f"✅ Custom evaluation completed:")
        print(f"   Samples: {len(results.results)}")
        print(f"   Duration: {results.duration:.2f} seconds")
        print(f"   Parallel processing: {config.parallel_processing}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error in custom evaluation: {e}")
        return None

def example_4_benchmark_evaluation():
    """Evaluate agent in benchmark mode."""
    print("🏆 Example 4: Benchmark Evaluation")
    print("=" * 40)
    
    try:
        # Load agent
        agent = amg.load_agent("agentplug/analysis-agent")
        
        # Run benchmark evaluation
        results = evaluate_benchmark(agent, benchmark_name="text_analysis")
        
        print(f"✅ Benchmark evaluation completed:")
        print(f"   Mode: {results.evaluation_mode}")
        print(f"   Benchmark: {results.benchmark_name}")
        print(f"   Samples: {len(results.results)}")
        print(f"   Duration: {results.duration:.2f} seconds")
        
        # Show detailed metrics
        if results.summary_metrics:
            print(f"\n📈 Summary Metrics:")
            for metric_name, metric_value in results.summary_metrics.items():
                if isinstance(metric_value, (int, float)):
                    print(f"   {metric_name}: {metric_value:.3f}")
                else:
                    print(f"   {metric_name}: {metric_value}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error in benchmark evaluation: {e}")
        return None

def example_5_generate_evaluation_report():
    """Generate HTML report from evaluation results."""
    print("📄 Example 5: Generate Evaluation Report")
    print("=" * 45)
    
    try:
        # Load and evaluate agent
        agent = amg.load_agent("agentplug/analysis-agent")
        results = evaluate_demo(agent)
        
        # Generate HTML report
        report_path = generate_report(results, format="html", output_path="evaluation_report.html")
        
        print(f"✅ Report generated: {report_path}")
        print(f"   Format: HTML")
        print(f"   Agent: {results.agent_name}")
        print(f"   Samples: {len(results.results)}")
        
        return report_path
        
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return None

def example_6_compare_agents():
    """Compare multiple agents side by side."""
    print("🔄 Example 6: Compare Multiple Agents")
    print("=" * 45)
    
    try:
        agents = {
            "analysis-agent": amg.load_agent("agentplug/analysis-agent"),
            "coding-agent": amg.load_agent("agentplug/coding-agent")
        }
        
        results = {}
        
        for name, agent in agents.items():
            print(f"\n🔍 Evaluating {name}...")
            results[name] = evaluate_demo(agent)
        
        # Compare results
        print(f"\n📊 Comparison Results:")
        print(f"{'Agent':<20} {'Samples':<10} {'Duration':<12} {'Success Rate':<15}")
        print("-" * 60)
        
        for name, result in results.items():
            success_rate = result.summary_metrics.get('success_rate', 0)
            print(f"{name:<20} {len(result.results):<10} {result.duration:<12.2f} {success_rate:<15.2%}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error comparing agents: {e}")
        return None

def main():
    """Run all evaluation examples."""
    print("🚀 AgentHub Agent Evaluation Examples")
    print("=" * 50)
    print("This demonstrates how to evaluate prebuilt AgentHub agents")
    print("using the evaluation framework with proper AgentWrapper support.")
    print()
    
    # Run examples
    examples = [
        example_1_analysis_agent_demo,
        example_2_coding_agent_with_tools,
        example_3_custom_evaluation_config,
        example_4_benchmark_evaluation,
        example_5_generate_evaluation_report,
        example_6_compare_agents
    ]
    
    for i, example_func in enumerate(examples, 1):
        try:
            print(f"\n{'='*60}")
            result = example_func()
            if result:
                print(f"✅ Example {i} completed successfully")
            else:
                print(f"⚠️ Example {i} completed with issues")
        except Exception as e:
            print(f"❌ Example {i} failed: {e}")
        
        # Pause between examples
        if i < len(examples):
            input(f"\n⏸️ Press Enter to continue to example {i+1}...")
    
    print(f"\n🎉 All examples completed!")
    print("Check the generated 'evaluation_report.html' for detailed results.")

if __name__ == "__main__":
    main()
