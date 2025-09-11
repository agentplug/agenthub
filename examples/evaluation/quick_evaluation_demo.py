#!/usr/bin/env python3
"""
AgentHub Evaluation Quick Demo

This example demonstrates the basic usage of the AgentHub evaluation system
with real AgentHub agents. It shows how to evaluate agents in both demo 
and benchmark modes.
"""

import sys
import os
from pathlib import Path

# Add the parent directory to the path so we can import agentmanager
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

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
    from agentmanager.evaluation import evaluate, evaluate_demo, evaluate_benchmark, generate_report
    EVALUATION_AVAILABLE = True
except ImportError:
    print("⚠️ Full AgentHub system not available, using mock evaluation")
    EVALUATION_AVAILABLE = False


class SimpleAgent:
    """A simple agent for demonstration purposes (fallback)."""
    
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


def mock_evaluate_benchmark(agent, benchmark_name="basic_qa", sample_count=5):
    """Mock benchmark evaluation function when full system is not available."""
    from datetime import datetime
    import time
    
    start_time = time.time()
    
    # Create sample data based on benchmark
    if benchmark_name == "basic_qa":
        samples = [
            "What is the capital of France?",
            "Who wrote Romeo and Juliet?",
            "What is 2 + 2?",
            "What is the largest planet in our solar system?",
            "What year did World War II end?"
        ]
    else:
        samples = [
            "Sample question 1",
            "Sample question 2", 
            "Sample question 3",
            "Sample question 4",
            "Sample question 5"
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
                'agent_type': 'AgentWrapper' if hasattr(agent, 'execute') else 'Simple',
                'benchmark': benchmark_name
            }
        )
        
        # Create metric result
        metric_result = MetricResult(
            metric_type="accuracy",
            value=0.75 + (i * 0.05),  # Simulate different scores
            confidence=0.9
        )
        
        # Create metric results
        metric_results = MetricResults(
            agent_output=agent_output,
            metrics={"accuracy": metric_result},
            timestamp=datetime.now()
        )
        
        results.append(metric_results)
    
    # Create evaluation results
    evaluation_results = EvaluationResults(
        agent_name=getattr(agent, 'agent_name', 'Unknown Agent'),
        evaluation_mode=EvaluationMode.BENCHMARK,
        results=results,
        summary_metrics={
            "success_rate": 1.0,
            "average_accuracy": sum(r.metrics["accuracy"].value for r in results) / len(results)
        },
        timestamp=datetime.now(),
        duration=time.time() - start_time,
        benchmark_name=benchmark_name
    )
    
    return evaluation_results


def mock_generate_report(results, format_type="html", output_path=None):
    """Mock report generation function when full system is not available."""
    if output_path is None:
        output_path = f"evaluation_report.{format_type}"
    
    if format_type == "html":
        content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>AgentHub Evaluation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
        .metric {{ margin: 10px 0; }}
        .result {{ border: 1px solid #ddd; padding: 10px; margin: 10px 0; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>AgentHub Evaluation Report</h1>
        <p><strong>Agent:</strong> {results.agent_name}</p>
        <p><strong>Mode:</strong> {results.evaluation_mode.value}</p>
        <p><strong>Duration:</strong> {results.duration:.2f} seconds</p>
        <p><strong>Samples:</strong> {len(results.results)}</p>
    </div>
    
    <h2>Summary Metrics</h2>
    {''.join(f'<div class="metric"><strong>{k}:</strong> {v:.3f}</div>' for k, v in results.summary_metrics.items())}
    
    <h2>Individual Results</h2>
    {''.join(f'''
    <div class="result">
        <h3>Sample {i+1}</h3>
        <p><strong>Input:</strong> {r.agent_output.input_text}</p>
        <p><strong>Output:</strong> {r.agent_output.output_text[:200]}...</p>
        <p><strong>Method:</strong> {r.agent_output.metadata.get('method_used', 'Unknown')}</p>
    </div>
    ''' for i, r in enumerate(results.results))}
</body>
</html>
        """
    elif format_type == "json":
        import json
        content = json.dumps({
            "agent_name": results.agent_name,
            "evaluation_mode": results.evaluation_mode.value,
            "duration": results.duration,
            "sample_count": len(results.results),
            "summary_metrics": results.summary_metrics,
            "results": [
                {
                    "input": r.agent_output.input_text,
                    "output": r.agent_output.output_text,
                    "method": r.agent_output.metadata.get('method_used', 'Unknown'),
                    "metrics": {k: v.value for k, v in r.metrics.items()}
                }
                for r in results.results
            ]
        }, indent=2)
    else:  # text
        content = f"""
AgentHub Evaluation Report
========================

Agent: {results.agent_name}
Mode: {results.evaluation_mode.value}
Duration: {results.duration:.2f} seconds
Samples: {len(results.results)}

Summary Metrics:
{chr(10).join(f'  {k}: {v:.3f}' for k, v in results.summary_metrics.items())}

Individual Results:
{chr(10).join(f'''
Sample {i+1}:
  Input: {r.agent_output.input_text}
  Output: {r.agent_output.output_text[:100]}...
  Method: {r.agent_output.metadata.get('method_used', 'Unknown')}
''' for i, r in enumerate(results.results))}
        """
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return output_path


def demonstrate_demo_evaluation():
    """Demonstrate demo mode evaluation with AgentHub agents."""
    print("=" * 60)
    print("🚀 DEMO MODE EVALUATION")
    print("=" * 60)
    
    print("1. Loading AgentHub analysis-agent...")
    try:
        if EVALUATION_AVAILABLE:
            agent = amg.load_agent("agentplug/analysis-agent")
            print(f"   ✓ Agent loaded: {agent.agent_name}")
            print(f"   ✓ Available methods: {agent.methods}")
            
            print("\n2. Running demo evaluation...")
            print("   This will test the agent on 5 sample questions")
            
            # Run demo evaluation
            results = evaluate_demo(agent, sample_count=5)
        else:
            # Use mock agent
            agent = SimpleAgent("MockAnalysisAgent")
            agent.methods = ['analyze_text', 'process']
            print(f"   ✓ Mock agent created: {agent.agent_name}")
            print(f"   ✓ Available methods: {agent.methods}")
            
            print("\n2. Running mock demo evaluation...")
            print("   This will test the agent on 5 sample questions")
            
            # Run mock evaluation
            results = mock_evaluate_demo(agent, sample_count=5)
        
        print(f"\n3. Evaluation Results:")
        print(f"   - Agent: {results.agent_name}")
        print(f"   - Mode: {results.evaluation_mode.value}")
        print(f"   - Duration: {results.duration:.2f} seconds")
        print(f"   - Total Evaluations: {len(results.results)}")
        print(f"   - Success Rate: {results.summary_metrics.get('success_rate', 0):.2%}")
        
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
            print(f"   - Method used: {result.agent_output.metadata.get('method_used', 'Unknown')}")
            
            if result.metrics:
                print(f"   - Metrics:")
                for metric_name, metric_result in result.metrics.items():
                    print(f"     * {metric_name}: {metric_result.value:.3f}")
        
        return results
        
    except Exception as e:
        print(f"   ❌ Error loading AgentHub agent: {e}")
        print("   🔄 Falling back to simple mock agent...")
        
        # Fallback to simple agent
        agent = SimpleAgent("DemoAgent")
        agent.methods = ['process']
        print(f"   ✓ Mock agent created: {agent.agent_name}")
        
        try:
            results = mock_evaluate_demo(agent, sample_count=5)
            print(f"\n3. Evaluation Results:")
            print(f"   - Agent: {results.agent_name}")
            print(f"   - Mode: {results.evaluation_mode.value}")
            print(f"   - Duration: {results.duration:.2f} seconds")
            print(f"   - Total Evaluations: {len(results.results)}")
            print(f"   - Success Rate: {results.summary_metrics.get('success_rate', 0):.2%}")
            return results
        except Exception as e2:
            print(f"   ❌ Error during evaluation: {e2}")
            return None


def demonstrate_benchmark_evaluation():
    """Demonstrate benchmark mode evaluation with AgentHub agents."""
    print("\n" + "=" * 60)
    print("📊 BENCHMARK MODE EVALUATION")
    print("=" * 60)
    
    print("1. Loading AgentHub coding-agent...")
    try:
        if EVALUATION_AVAILABLE:
            agent = amg.load_agent("agentplug/coding-agent")
            print(f"   ✓ Agent loaded: {agent.agent_name}")
            print(f"   ✓ Available methods: {agent.methods}")
            
            print("\n2. Running benchmark evaluation...")
            print("   This will test the agent on predefined benchmark questions")
            
            # Run benchmark evaluation
            results = evaluate_benchmark(agent, benchmark_name="basic_qa")
        else:
            # Use mock agent
            agent = SimpleAgent("MockCodingAgent")
            agent.methods = ['generate_code', 'analyze_text']
            print(f"   ✓ Mock agent created: {agent.agent_name}")
            print(f"   ✓ Available methods: {agent.methods}")
            
            print("\n2. Running mock benchmark evaluation...")
            print("   This will test the agent on predefined benchmark questions")
            
            # Run mock benchmark evaluation
            results = mock_evaluate_benchmark(agent, benchmark_name="basic_qa")
        
        print(f"\n3. Benchmark Results:")
        print(f"   - Agent: {results.agent_name}")
        print(f"   - Mode: {results.evaluation_mode.value}")
        print(f"   - Benchmark: {results.benchmark_name}")
        print(f"   - Duration: {results.duration:.2f} seconds")
        print(f"   - Total Evaluations: {len(results.results)}")
        print(f"   - Success Rate: {results.summary_metrics.get('success_rate', 0):.2%}")
        
        if results.summary_metrics:
            print(f"\n4. Summary Metrics:")
            for metric, value in results.summary_metrics.items():
                if isinstance(value, float):
                    print(f"   - {metric}: {value:.3f}")
                else:
                    print(f"   - {metric}: {value}")
        
        return results
        
    except Exception as e:
        print(f"   ❌ Error loading AgentHub agent: {e}")
        print("   🔄 Falling back to simple mock agent...")
        
        # Fallback to simple agent
        agent = SimpleAgent("BenchmarkAgent")
        agent.methods = ['process']
        print(f"   ✓ Mock agent created: {agent.agent_name}")
        
        try:
            results = mock_evaluate_benchmark(agent, benchmark_name="basic_qa")
            print(f"\n2. Benchmark Results:")
            print(f"   - Agent: {results.agent_name}")
            print(f"   - Mode: {results.evaluation_mode.value}")
            print(f"   - Benchmark: {results.benchmark_name}")
            print(f"   - Duration: {results.duration:.2f} seconds")
            print(f"   - Total Evaluations: {len(results.results)}")
            print(f"   - Success Rate: {results.summary_metrics.get('success_rate', 0):.2%}")
            return results
        except Exception as e2:
            print(f"   ❌ Error during benchmark evaluation: {e2}")
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
        if EVALUATION_AVAILABLE:
            html_report = generate_report(results, format_type="html")
            print(f"   ✓ HTML report generated ({len(html_report)} characters)")
            
            # Save to file
            with open("evaluation_report.html", "w", encoding="utf-8") as f:
                f.write(html_report)
            print("   ✓ Report saved to 'evaluation_report.html'")
        else:
            html_report = mock_generate_report(results, format_type="html")
            print(f"   ✓ HTML report generated: {html_report}")
        
    except Exception as e:
        print(f"   Error generating HTML report: {e}")
    
    print("\n2. Generating JSON report...")
    try:
        if EVALUATION_AVAILABLE:
            json_report = generate_report(results, format_type="json")
            print(f"   ✓ JSON report generated ({len(json_report)} characters)")
            
            # Save to file
            with open("evaluation_report.json", "w", encoding="utf-8") as f:
                f.write(json_report)
            print("   ✓ Report saved to 'evaluation_report.json'")
        else:
            json_report = mock_generate_report(results, format_type="json")
            print(f"   ✓ JSON report generated: {json_report}")
        
    except Exception as e:
        print(f"   Error generating JSON report: {e}")
    
    print("\n3. Generating text report...")
    try:
        if EVALUATION_AVAILABLE:
            text_report = generate_report(results, format_type="text")
            print(f"   ✓ Text report generated ({len(text_report)} characters)")
            print("\n   Text Report Preview:")
            print("   " + "-" * 50)
            print(text_report[:500] + "..." if len(text_report) > 500 else text_report)
            print("   " + "-" * 50)
        else:
            text_report = mock_generate_report(results, format_type="text")
            print(f"   ✓ Text report generated: {text_report}")
        
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
