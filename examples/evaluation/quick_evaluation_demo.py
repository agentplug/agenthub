#!/usr/bin/env python3
"""
AgentHub Evaluation Quick Demo

This example demonstrates the basic usage of the AgentHub evaluation system.
It shows how to evaluate agents in both demo and benchmark modes.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import agentmanager
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentmanager import load_agent, evaluate, evaluate_demo, evaluate_benchmark, generate_report


class SimpleAgent:
    """A simple agent for demonstration purposes."""
    
    def __init__(self, name="SimpleAgent"):
        self.agent_name = name
    
    def process(self, input_text):
        """Process input text and return a response."""
        # Simple response logic for demonstration
        input_lower = input_text.lower()
        
        if "capital" in input_lower and "france" in input_lower:
            return "The capital of France is Paris."
        elif "capital" in input_lower and "germany" in input_lower:
            return "The capital of Germany is Berlin."
        elif "math" in input_lower or "calculate" in input_lower:
            if "2 + 2" in input_text:
                return "2 + 2 = 4"
            elif "5 + 3" in input_text:
                return "5 + 3 = 8"
            else:
                return "I can help with basic math calculations."
        elif "hello" in input_lower or "hi" in input_lower:
            return "Hello! How can I help you today?"
        elif "write" in input_lower or "poem" in input_lower:
            return "Here's a simple poem:\n\nRoses are red,\nViolets are blue,\nAI is amazing,\nAnd so are you!"
        else:
            return f"I received your message: '{input_text}'. I'm a simple agent that can help with basic questions about capitals, math, and creative writing."


def demonstrate_demo_evaluation():
    """Demonstrate demo mode evaluation."""
    print("=" * 60)
    print("🚀 DEMO MODE EVALUATION")
    print("=" * 60)
    
    # Create a simple agent
    agent = SimpleAgent("DemoAgent")
    
    print("1. Creating a simple agent for demonstration...")
    print(f"   Agent name: {agent.agent_name}")
    
    print("\n2. Running demo evaluation...")
    print("   This will test the agent on 5 sample questions")
    
    try:
        # Run demo evaluation
        results = evaluate_demo(agent, sample_count=5)
        
        print(f"\n3. Evaluation Results:")
        print(f"   - Agent: {results.agent_name}")
        print(f"   - Mode: {results.evaluation_mode.value}")
        print(f"   - Duration: {results.duration:.2f} seconds")
        print(f"   - Total Evaluations: {results.total_evaluations}")
        print(f"   - Success Rate: {results.success_rate:.2%}")
        
        if results.summary_metrics:
            print(f"\n4. Summary Metrics:")
            for metric, value in results.summary_metrics.items():
                if isinstance(value, float):
                    print(f"   - {metric}: {value:.3f}")
                else:
                    print(f"   - {metric}: {value}")
        
        print(f"\n5. Individual Results:")
        for i, result in enumerate(results.results, 1):
            print(f"\n   Result {i}:")
            print(f"   - Input: {result.agent_output.input_text}")
            print(f"   - Output: {result.agent_output.output_text[:100]}...")
            
            if result.metrics:
                print(f"   - Metrics:")
                for metric_name, metric_result in result.metrics.items():
                    print(f"     * {metric_name}: {metric_result.value:.3f}")
        
        return results
        
    except Exception as e:
        print(f"   Error during evaluation: {e}")
        return None


def demonstrate_benchmark_evaluation():
    """Demonstrate benchmark mode evaluation."""
    print("\n" + "=" * 60)
    print("📊 BENCHMARK MODE EVALUATION")
    print("=" * 60)
    
    # Create a simple agent
    agent = SimpleAgent("BenchmarkAgent")
    
    print("1. Running benchmark evaluation...")
    print("   This will test the agent on predefined benchmark questions")
    
    try:
        # Run benchmark evaluation
        results = evaluate_benchmark(agent, benchmark_name="basic_qa")
        
        print(f"\n2. Benchmark Results:")
        print(f"   - Agent: {results.agent_name}")
        print(f"   - Mode: {results.evaluation_mode.value}")
        print(f"   - Benchmark: {results.benchmark_name}")
        print(f"   - Duration: {results.duration:.2f} seconds")
        print(f"   - Total Evaluations: {results.total_evaluations}")
        print(f"   - Success Rate: {results.success_rate:.2%}")
        
        if results.summary_metrics:
            print(f"\n3. Summary Metrics:")
            for metric, value in results.summary_metrics.items():
                if isinstance(value, float):
                    print(f"   - {metric}: {value:.3f}")
                else:
                    print(f"   - {metric}: {value}")
        
        return results
        
    except Exception as e:
        print(f"   Error during benchmark evaluation: {e}")
        return None


def demonstrate_report_generation(results):
    """Demonstrate report generation."""
    if not results:
        print("\n" + "=" * 60)
        print("📄 REPORT GENERATION (SKIPPED - No results)")
        print("=" * 60)
        return
    
    print("\n" + "=" * 60)
    print("📄 REPORT GENERATION")
    print("=" * 60)
    
    print("1. Generating HTML report...")
    try:
        html_report = generate_report(results, format_type="html")
        print(f"   ✓ HTML report generated ({len(html_report)} characters)")
        
        # Save to file
        with open("evaluation_report.html", "w", encoding="utf-8") as f:
            f.write(html_report)
        print("   ✓ Report saved to 'evaluation_report.html'")
        
    except Exception as e:
        print(f"   Error generating HTML report: {e}")
    
    print("\n2. Generating JSON report...")
    try:
        json_report = generate_report(results, format_type="json")
        print(f"   ✓ JSON report generated ({len(json_report)} characters)")
        
        # Save to file
        with open("evaluation_report.json", "w", encoding="utf-8") as f:
            f.write(json_report)
        print("   ✓ Report saved to 'evaluation_report.json'")
        
    except Exception as e:
        print(f"   Error generating JSON report: {e}")
    
    print("\n3. Generating text report...")
    try:
        text_report = generate_report(results, format_type="text")
        print(f"   ✓ Text report generated ({len(text_report)} characters)")
        print("\n   Text Report Preview:")
        print("   " + "-" * 50)
        print(text_report[:500] + "..." if len(text_report) > 500 else text_report)
        print("   " + "-" * 50)
        
    except Exception as e:
        print(f"   Error generating text report: {e}")


def demonstrate_available_options():
    """Demonstrate available evaluation options."""
    print("\n" + "=" * 60)
    print("⚙️ AVAILABLE EVALUATION OPTIONS")
    print("=" * 60)
    
    try:
        from agentmanager import get_available_modes, get_available_benchmarks, get_available_report_formats
        
        print("1. Available Evaluation Modes:")
        modes = get_available_modes()
        for mode in modes:
            print(f"   - {mode}")
        
        print("\n2. Available Benchmarks:")
        benchmarks = get_available_benchmarks()
        for benchmark in benchmarks:
            print(f"   - {benchmark}")
        
        print("\n3. Available Report Formats:")
        formats = get_available_report_formats()
        for format_type in formats:
            print(f"   - {format_type}")
            
    except Exception as e:
        print(f"   Error getting available options: {e}")


def main():
    """Run the complete evaluation demonstration."""
    print("🎯 AgentHub Evaluation Quick Demo")
    print("This demonstrates the basic usage of the AgentHub evaluation system")
    print("=" * 80)
    
    # Demonstrate available options
    demonstrate_available_options()
    
    # Run demo evaluation
    demo_results = demonstrate_demo_evaluation()
    
    # Run benchmark evaluation
    benchmark_results = demonstrate_benchmark_evaluation()
    
    # Generate reports
    if demo_results:
        demonstrate_report_generation(demo_results)
    
    print("\n" + "=" * 80)
    print("✨ Evaluation demonstration completed!")
    print("\nNext steps:")
    print("1. Try different agents: agent = load_agent('your/agent')")
    print("2. Run evaluations: results = evaluate(agent, mode='demo')")
    print("3. Generate reports: report = generate_report(results, 'html')")
    print("4. Check the generated report files in the current directory")


if __name__ == "__main__":
    main()
