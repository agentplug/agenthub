"""
High-level evaluation function for AgentHub.
"""

from typing import Union, Optional, List, Dict, Any
from .core.evaluation_engine import EvaluationEngine
from .core.data_models import EvaluationConfig, EvaluationMode, SampleData
from .reporting import ReportGenerator


def evaluate(
    agent,
    mode: str = "demo",
    samples: Optional[List[SampleData]] = None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
):
    """
    Evaluate an agent using the specified mode.
    
    This is the main entry point for agent evaluation in AgentHub.
    
    Args:
        agent: The agent to evaluate (loaded via load_agent)
        mode: Evaluation mode ("demo" or "benchmark")
        samples: Sample data for evaluation (optional)
        config: Configuration dictionary (optional)
        **kwargs: Additional parameters
        
    Returns:
        EvaluationResults object with evaluation data
        
    Example:
        >>> from agentmanager import load_agent, evaluate
        >>> agent = load_agent("my/agent")
        >>> results = evaluate(agent, mode="demo")
        >>> print(f"Success rate: {results.success_rate:.2%}")
    """
    # Create evaluation config
    eval_config = EvaluationConfig()
    if config:
        for key, value in config.items():
            if hasattr(eval_config, key):
                setattr(eval_config, key, value)
    
    # Create evaluation engine
    engine = EvaluationEngine(eval_config)
    
    # Evaluate agent
    results = engine.evaluate(agent, mode=mode, samples=samples, **kwargs)
    
    return results


def evaluate_demo(
    agent,
    sample_count: int = 5,
    **kwargs
):
    """
    Quick demo evaluation of an agent.
    
    Args:
        agent: The agent to evaluate
        sample_count: Number of samples to evaluate on
        **kwargs: Additional parameters
        
    Returns:
        EvaluationResults object
    """
    config = {"sample_count": sample_count}
    return evaluate(agent, mode="demo", config=config, **kwargs)


def evaluate_benchmark(
    agent,
    benchmark_name: str = "basic_qa",
    **kwargs
):
    """
    Comprehensive benchmark evaluation of an agent.
    
    Args:
        agent: The agent to evaluate
        benchmark_name: Name of the benchmark to use
        **kwargs: Additional parameters
        
    Returns:
        EvaluationResults object
    """
    config = {"benchmark_name": benchmark_name}
    return evaluate(agent, mode="benchmark", config=config, **kwargs)


def generate_report(
    results,
    format_type: str = "html"
):
    """
    Generate a report from evaluation results.
    
    Args:
        results: EvaluationResults object
        format_type: Report format ("html", "json", "text")
        
    Returns:
        Generated report as string
    """
    generator = ReportGenerator()
    return generator.generate_report(results, format_type)


def get_available_benchmarks():
    """Get list of available benchmarks."""
    from .benchmarks import BenchmarkManager
    manager = BenchmarkManager()
    return manager.get_available_benchmarks()


def get_available_modes():
    """Get list of available evaluation modes."""
    return ["demo", "benchmark"]


def get_available_report_formats():
    """Get list of available report formats."""
    generator = ReportGenerator()
    return generator.get_available_formats()
