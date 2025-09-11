#!/usr/bin/env python3
"""
AgentHub Evaluation Integration Example

This example shows how to integrate the evaluation system with existing
AgentHub agents and workflows.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import agentmanager
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentmanager import load_agent, evaluate, generate_report
from agentmanager.evaluation import EvaluationConfig, SampleData


def demonstrate_agent_integration():
    """Demonstrate integration with existing AgentHub agents."""
    print("=" * 60)
    print("🔗 AGENT INTEGRATION DEMONSTRATION")
    print("=" * 60)
    
    print("1. Loading an agent using AgentHub's load_agent function...")
    
    try:
        # This would work with real agents from the registry
        # For demonstration, we'll create a mock agent
        class MockAgentHubAgent:
            def __init__(self):
                self.agent_name = "MockAgentHubAgent"
                self.tools = ["web_search", "file_operations"]
            
            def process(self, input_text):
                """Process input using agent capabilities."""
                if "search" in input_text.lower():
                    return f"I would search the web for: {input_text}"
                elif "file" in input_text.lower():
                    return f"I would perform file operations for: {input_text}"
                else:
                    return f"Processed: {input_text} using my available tools"
        
        # Create mock agent
        agent = MockAgentHubAgent()
        print(f"   ✓ Loaded agent: {agent.agent_name}")
        print(f"   ✓ Available tools: {agent.tools}")
        
        print("\n2. Running evaluation on the agent...")
        
        # Run evaluation
        results = evaluate(agent, mode="demo", config={"sample_count": 3})
        
        print(f"   ✓ Evaluation completed")
        print(f"   - Success rate: {results.success_rate:.2%}")
        print(f"   - Duration: {results.duration:.2f}s")
        
        return agent, results
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return None, None


def demonstrate_custom_evaluation_workflow():
    """Demonstrate a custom evaluation workflow."""
    print("\n" + "=" * 60)
    print("⚙️ CUSTOM EVALUATION WORKFLOW")
    print("=" * 60)
    
    print("1. Creating custom evaluation samples...")
    
    # Define custom samples for a specific use case
    custom_samples = [
        SampleData(
            input_text="Analyze the sentiment of this text: 'I love this product!'",
            expected_output="Positive sentiment",
            difficulty="easy",
            category="sentiment_analysis"
        ),
        SampleData(
            input_text="Translate 'Hello world' to Spanish",
            expected_output="Hola mundo",
            difficulty="easy",
            category="translation"
        ),
        SampleData(
            input_text="Summarize this article about AI developments",
            expected_output="A concise summary of AI developments",
            difficulty="medium",
            category="summarization"
        )
    ]
    
    print(f"   ✓ Created {len(custom_samples)} custom samples")
    
    print("\n2. Setting up custom evaluation configuration...")
    
    # Create custom configuration
    config = EvaluationConfig(
        mode="demo",
        sample_count=len(custom_samples),
        parallel_processing=True,
        max_workers=2,
        timeout_seconds=30
    )
    
    print("   ✓ Custom configuration created")
    
    print("\n3. Running custom evaluation...")
    
    # Create a mock agent for the workflow
    class WorkflowAgent:
        def __init__(self):
            self.agent_name = "WorkflowAgent"
        
        def process(self, input_text):
            """Process input for specific workflow tasks."""
            if "sentiment" in input_text.lower():
                return "This text shows positive sentiment with high confidence."
            elif "translate" in input_text.lower():
                return "Hola mundo"
            elif "summarize" in input_text.lower():
                return "AI developments are advancing rapidly with new breakthroughs in machine learning, natural language processing, and computer vision technologies."
            else:
                return f"Processed workflow task: {input_text}"
    
    agent = WorkflowAgent()
    
    try:
        # Run evaluation with custom samples
        results = evaluate(agent, mode="demo", samples=custom_samples, config=config)
        
        print(f"   ✓ Custom evaluation completed")
        print(f"   - Success rate: {results.success_rate:.2%}")
        print(f"   - Duration: {results.duration:.2f}s")
        
        return results
        
    except Exception as e:
        print(f"   ✗ Error during custom evaluation: {e}")
        return None


def demonstrate_continuous_evaluation():
    """Demonstrate continuous evaluation monitoring."""
    print("\n" + "=" * 60)
    print("🔄 CONTINUOUS EVALUATION MONITORING")
    print("=" * 60)
    
    print("1. Setting up continuous evaluation...")
    
    class EvolvingAgent:
        def __init__(self, version="1.0"):
            self.agent_name = f"EvolvingAgent-v{version}"
            self.version = version
            self.performance_history = []
        
        def process(self, input_text):
            """Process input with version-specific behavior."""
            # Simulate different performance based on version
            if self.version == "1.0":
                return f"Basic response v1.0: {input_text}"
            elif self.version == "2.0":
                return f"Improved response v2.0: {input_text} (with better understanding)"
            else:
                return f"Advanced response v{self.version}: {input_text} (with full capabilities)"
    
    print("2. Evaluating different agent versions...")
    
    versions = ["1.0", "2.0", "3.0"]
    version_results = []
    
    for version in versions:
        print(f"\n   Evaluating version {version}...")
        
        agent = EvolvingAgent(version)
        
        try:
            results = evaluate(agent, mode="demo", config={"sample_count": 3})
            version_results.append((version, results))
            
            print(f"   ✓ Version {version} - Success rate: {results.success_rate:.2%}")
            
        except Exception as e:
            print(f"   ✗ Error evaluating version {version}: {e}")
    
    print("\n3. Performance comparison across versions:")
    print("   " + "-" * 40)
    print(f"   {'Version':<8} {'Success Rate':<12} {'Duration':<10}")
    print("   " + "-" * 40)
    
    for version, results in version_results:
        success_rate = f"{results.success_rate:.1%}"
        duration = f"{results.duration:.2f}s"
        print(f"   {version:<8} {success_rate:<12} {duration:<10}")
    
    print("   " + "-" * 40)
    
    return version_results


def demonstrate_automated_reporting():
    """Demonstrate automated reporting workflow."""
    print("\n" + "=" * 60)
    print("📊 AUTOMATED REPORTING WORKFLOW")
    print("=" * 60)
    
    print("1. Running evaluation for automated reporting...")
    
    # Create a simple agent
    class ReportAgent:
        def __init__(self):
            self.agent_name = "ReportAgent"
        
        def process(self, input_text):
            return f"Generated report for: {input_text}"
    
    agent = ReportAgent()
    
    try:
        # Run evaluation
        results = evaluate(agent, mode="demo", config={"sample_count": 3})
        
        print("2. Generating automated reports...")
        
        # Generate multiple report formats
        formats = ["html", "json", "text"]
        generated_files = []
        
        for format_type in formats:
            try:
                report = generate_report(results, format_type)
                filename = f"automated_report.{format_type}"
                
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(report)
                
                generated_files.append(filename)
                print(f"   ✓ Generated {format_type.upper()} report: {filename}")
                
            except Exception as e:
                print(f"   ✗ Error generating {format_type} report: {e}")
        
        print(f"\n3. Generated {len(generated_files)} report files:")
        for filename in generated_files:
            print(f"   - {filename}")
        
        return generated_files
        
    except Exception as e:
        print(f"   ✗ Error in automated reporting: {e}")
        return []


def main():
    """Run the integration demonstration."""
    print("🎯 AgentHub Evaluation Integration Example")
    print("This demonstrates how to integrate evaluation with existing workflows")
    print("=" * 80)
    
    # Demonstrate agent integration
    agent, results = demonstrate_agent_integration()
    
    # Demonstrate custom evaluation workflow
    custom_results = demonstrate_custom_evaluation_workflow()
    
    # Demonstrate continuous evaluation
    version_results = demonstrate_continuous_evaluation()
    
    # Demonstrate automated reporting
    report_files = demonstrate_automated_reporting()
    
    print("\n" + "=" * 80)
    print("✨ Integration demonstration completed!")
    print("\nKey takeaways:")
    print("1. Evaluation integrates seamlessly with existing AgentHub agents")
    print("2. Custom evaluation workflows can be easily created")
    print("3. Continuous evaluation helps track agent performance over time")
    print("4. Automated reporting can be integrated into CI/CD pipelines")
    print("\nGenerated files:")
    for filename in report_files:
        print(f"- {filename}")
    print("\nNext steps:")
    print("1. Integrate evaluation into your agent development process")
    print("2. Set up automated evaluation in your CI/CD pipeline")
    print("3. Create custom benchmarks for your specific use cases")
    print("4. Use evaluation results to improve agent performance")


if __name__ == "__main__":
    main()
