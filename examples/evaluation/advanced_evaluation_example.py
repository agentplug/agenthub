#!/usr/bin/env python3
"""
AgentHub Advanced Evaluation Example

This example demonstrates advanced usage of the AgentHub evaluation system,
including custom benchmarks, detailed metrics, and comprehensive reporting.
"""

import sys
import os
from pathlib import Path
from typing import List

# Add the parent directory to the path so we can import agentmanager
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from agentmanager import (
    load_agent, evaluate, evaluate_demo, evaluate_benchmark, 
    generate_report, get_available_benchmarks
)
from agentmanager.evaluation import (
    EvaluationConfig, SampleData, BenchmarkDefinition, 
    BenchmarkManager, CustomBenchmark
)


class AdvancedAgent:
    """An advanced agent for demonstration purposes."""
    
    def __init__(self, name="AdvancedAgent", expertise="general"):
        self.agent_name = name
        self.expertise = expertise
        self.response_count = 0
    
    def process(self, input_text):
        """Process input text with more sophisticated logic."""
        self.response_count += 1
        input_lower = input_text.lower()
        
        # Simulate different response times based on complexity
        import time
        if "complex" in input_lower or "difficult" in input_lower:
            time.sleep(0.1)  # Simulate longer processing
        else:
            time.sleep(0.05)  # Simulate shorter processing
        
        # Generate responses based on expertise
        if self.expertise == "math":
            return self._handle_math_query(input_text)
        elif self.expertise == "creative":
            return self._handle_creative_query(input_text)
        elif self.expertise == "technical":
            return self._handle_technical_query(input_text)
        else:
            return self._handle_general_query(input_text)
    
    def _handle_math_query(self, input_text):
        """Handle mathematical queries."""
        if "factorial" in input_text.lower():
            return "The factorial of a number n is n! = n × (n-1) × (n-2) × ... × 1. For example, 5! = 5 × 4 × 3 × 2 × 1 = 120."
        elif "derivative" in input_text.lower():
            return "A derivative measures how a function changes as its input changes. The derivative of x² is 2x."
        elif "integral" in input_text.lower():
            return "An integral is the reverse of a derivative. It finds the area under a curve or the antiderivative of a function."
        else:
            return "I can help with various mathematical concepts including calculus, algebra, geometry, and statistics."
    
    def _handle_creative_query(self, input_text):
        """Handle creative writing queries."""
        if "poem" in input_text.lower():
            return """Here's a creative poem:

The Digital Dawn
================

In circuits deep and code so bright,
AI awakens in the night.
With every line and every byte,
It learns to think, to dream, to write.

From data streams and patterns vast,
It builds a future, not the past.
A digital mind, both free and bound,
In silicon dreams, new worlds are found."""
        
        elif "story" in input_text.lower():
            return """Here's a short story:

The Last Human Programmer

In a world where AI wrote all the code, Sarah was the last human programmer. She didn't write in traditional languages anymore—she wrote in emotions, in the spaces between logic and creativity that machines couldn't quite grasp.

Her code wasn't just functional; it was beautiful. It had rhythm, it had soul. The AIs would study her work, trying to understand the patterns, but they could never quite replicate the human touch.

One day, an AI asked her, "What makes your code different?"

Sarah smiled. "It's not just about solving problems," she said. "It's about solving them with heart." And with that, she wrote one final line of code that made the AI cry—not from an error, but from understanding what it meant to be truly human."""
        
        else:
            return "I love creative writing! I can help with poetry, stories, character development, plot ideas, and various creative writing techniques."
    
    def _handle_technical_query(self, input_text):
        """Handle technical queries."""
        input_lower = input_text.lower()
        if "python" in input_lower:
            return """Python is a high-level programming language known for its simplicity and readability. Here's a simple example:

```python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Usage
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
```

Python is great for data science, web development, AI/ML, and automation."""
        
        elif "machine learning" in input_lower:
            return """Machine Learning is a subset of AI that enables computers to learn from data. Key concepts include:

1. **Supervised Learning**: Learning with labeled examples (classification, regression)
2. **Unsupervised Learning**: Finding patterns in unlabeled data (clustering, dimensionality reduction)
3. **Deep Learning**: Neural networks with multiple layers
4. **Reinforcement Learning**: Learning through trial and error

Popular frameworks include TensorFlow, PyTorch, and Scikit-learn."""
        
        else:
            return "I can help with programming, software architecture, algorithms, data structures, and various technical concepts."
    
    def _handle_general_query(self, input_text):
        """Handle general queries."""
        input_lower = input_text.lower()
        if "hello" in input_lower or "hi" in input_lower:
            return f"Hello! I'm {self.agent_name}, an AI assistant specialized in {self.expertise}. How can I help you today?"
        elif "help" in input_lower:
            return f"I'm {self.agent_name}, and I can help with various topics. I'm particularly good at {self.expertise}. What would you like to know?"
        else:
            return f"I received your message: '{input_text}'. I'm {self.agent_name}, specialized in {self.expertise}. I can help with a wide range of topics!"


def create_custom_benchmark():
    """Create a custom benchmark for evaluation."""
    print("1. Creating custom benchmark...")
    
    # Define custom samples
    samples = [
        SampleData(
            input_text="Explain the concept of recursion in programming",
            expected_output="Recursion is a programming technique where a function calls itself",
            difficulty="medium",
            category="programming"
        ),
        SampleData(
            input_text="Write a haiku about artificial intelligence",
            expected_output=None,  # Creative task, no single correct answer
            difficulty="medium",
            category="creative"
        ),
        SampleData(
            input_text="What is the time complexity of binary search?",
            expected_output="O(log n)",
            difficulty="hard",
            category="algorithms"
        ),
        SampleData(
            input_text="Describe the difference between supervised and unsupervised learning",
            expected_output="Supervised learning uses labeled data, unsupervised learning finds patterns in unlabeled data",
            difficulty="medium",
            category="machine_learning"
        ),
        SampleData(
            input_text="Write a Python function to reverse a string",
            expected_output="def reverse_string(s): return s[::-1]",
            difficulty="easy",
            category="programming"
        )
    ]
    
    # Create custom benchmark
    benchmark = CustomBenchmark(
        name="custom_programming_benchmark",
        samples=samples,
        metrics=["accuracy", "quality_score", "response_time", "coherence_score"]
    )
    
    # Register with benchmark manager
    manager = BenchmarkManager()
    manager.register_benchmark(benchmark.to_definition())
    
    print(f"   ✓ Created custom benchmark with {len(samples)} samples")
    return benchmark


def demonstrate_custom_evaluation():
    """Demonstrate evaluation with custom configuration."""
    print("\n" + "=" * 60)
    print("🔧 CUSTOM EVALUATION CONFIGURATION")
    print("=" * 60)
    
    # Create custom benchmark
    custom_benchmark = create_custom_benchmark()
    
    # Create different types of agents
    math_agent = AdvancedAgent("MathAgent", "math")
    creative_agent = AdvancedAgent("CreativeAgent", "creative")
    tech_agent = AdvancedAgent("TechAgent", "technical")
    
    agents = [math_agent, creative_agent, tech_agent]
    
    print("\n2. Evaluating different agent types...")
    
    all_results = []
    
    for agent in agents:
        print(f"\n   Evaluating {agent.agent_name} ({agent.expertise})...")
        
        try:
            # Use custom configuration
            config = EvaluationConfig(
                mode="benchmark",
                sample_count=len(custom_benchmark.samples),
                parallel_processing=True,
                max_workers=2
            )
            
            # Run evaluation
            results = evaluate(agent, mode="benchmark", config=config)
            all_results.append((agent.agent_name, results))
            
            print(f"   ✓ {agent.agent_name} evaluation completed")
            print(f"     - Success rate: {results.success_rate:.2%}")
            print(f"     - Duration: {results.duration:.2f}s")
            
            if results.summary_metrics:
                avg_quality = results.summary_metrics.get('quality_score_avg', 0)
                avg_response_time = results.summary_metrics.get('response_time_avg', 0)
                print(f"     - Avg quality: {avg_quality:.3f}")
                print(f"     - Avg response time: {avg_response_time:.3f}s")
        
        except Exception as e:
            print(f"   ✗ Error evaluating {agent.agent_name}: {e}")
    
    return all_results


def demonstrate_comparative_analysis(results):
    """Demonstrate comparative analysis of results."""
    if not results:
        print("\n" + "=" * 60)
        print("📊 COMPARATIVE ANALYSIS (SKIPPED - No results)")
        print("=" * 60)
        return
    
    print("\n" + "=" * 60)
    print("📊 COMPARATIVE ANALYSIS")
    print("=" * 60)
    
    print("1. Agent Performance Comparison:")
    print("   " + "-" * 50)
    print(f"   {'Agent':<15} {'Success Rate':<12} {'Duration':<10} {'Quality':<8}")
    print("   " + "-" * 50)
    
    for agent_name, result in results:
        success_rate = f"{result.success_rate:.1%}"
        duration = f"{result.duration:.2f}s"
        quality = f"{result.summary_metrics.get('quality_score_avg', 0):.3f}" if result.summary_metrics else "N/A"
        
        print(f"   {agent_name:<15} {success_rate:<12} {duration:<10} {quality:<8}")
    
    print("   " + "-" * 50)
    
    # Find best performing agent
    if results:
        best_agent = max(results, key=lambda x: x[1].success_rate)
        print(f"\n2. Best Performing Agent: {best_agent[0]}")
        print(f"   Success Rate: {best_agent[1].success_rate:.2%}")
        
        if best_agent[1].summary_metrics:
            print("   Key Metrics:")
            for metric, value in best_agent[1].summary_metrics.items():
                if isinstance(value, float):
                    print(f"     - {metric}: {value:.3f}")


def demonstrate_detailed_reporting(results):
    """Demonstrate detailed reporting capabilities."""
    if not results:
        print("\n" + "=" * 60)
        print("📄 DETAILED REPORTING (SKIPPED - No results)")
        print("=" * 60)
        return
    
    print("\n" + "=" * 60)
    print("📄 DETAILED REPORTING")
    print("=" * 60)
    
    # Generate comprehensive HTML report
    print("1. Generating comprehensive HTML report...")
    try:
        # Use the best performing agent's results for detailed report
        best_result = max(results, key=lambda x: x[1].success_rate)[1]
        
        html_report = generate_report(best_result, format_type="html")
        
        with open("detailed_evaluation_report.html", "w", encoding="utf-8") as f:
            f.write(html_report)
        
        print(f"   ✓ Detailed HTML report saved to 'detailed_evaluation_report.html'")
        print(f"   ✓ Report size: {len(html_report)} characters")
        
    except Exception as e:
        print(f"   ✗ Error generating detailed report: {e}")
    
    # Generate JSON report for programmatic access
    print("\n2. Generating JSON report for programmatic access...")
    try:
        json_report = generate_report(best_result, format_type="json")
        
        with open("evaluation_data.json", "w", encoding="utf-8") as f:
            f.write(json_report)
        
        print(f"   ✓ JSON data saved to 'evaluation_data.json'")
        print(f"   ✓ Data size: {len(json_report)} characters")
        
    except Exception as e:
        print(f"   ✗ Error generating JSON report: {e}")


def demonstrate_benchmark_management():
    """Demonstrate benchmark management capabilities."""
    print("\n" + "=" * 60)
    print("📚 BENCHMARK MANAGEMENT")
    print("=" * 60)
    
    try:
        from agentmanager import get_available_benchmarks
        
        print("1. Available Predefined Benchmarks:")
        benchmarks = get_available_benchmarks()
        for benchmark in benchmarks:
            print(f"   - {benchmark}")
        
        print(f"\n2. Total available benchmarks: {len(benchmarks)}")
        
        # Show details of a specific benchmark
        if benchmarks:
            manager = BenchmarkManager()
            benchmark_def = manager.get_benchmark(benchmarks[0])
            if benchmark_def:
                print(f"\n3. Details of '{benchmarks[0]}' benchmark:")
                print(f"   - Description: {benchmark_def.description}")
                print(f"   - Sample count: {len(benchmark_def.samples)}")
                print(f"   - Metrics: {', '.join(benchmark_def.metrics)}")
        
    except Exception as e:
        print(f"   ✗ Error accessing benchmark information: {e}")


def main():
    """Run the advanced evaluation demonstration."""
    print("🎯 AgentHub Advanced Evaluation Example")
    print("This demonstrates advanced usage of the AgentHub evaluation system")
    print("=" * 80)
    
    # Demonstrate benchmark management
    demonstrate_benchmark_management()
    
    # Run custom evaluation
    results = demonstrate_custom_evaluation()
    
    # Perform comparative analysis
    demonstrate_comparative_analysis(results)
    
    # Generate detailed reports
    demonstrate_detailed_reporting(results)
    
    print("\n" + "=" * 80)
    print("✨ Advanced evaluation demonstration completed!")
    print("\nGenerated files:")
    print("- detailed_evaluation_report.html (Comprehensive HTML report)")
    print("- evaluation_data.json (Structured JSON data)")
    print("\nNext steps:")
    print("1. Open the HTML report in a web browser")
    print("2. Use the JSON data for programmatic analysis")
    print("3. Create your own custom benchmarks")
    print("4. Integrate evaluation into your agent development workflow")


if __name__ == "__main__":
    main()
