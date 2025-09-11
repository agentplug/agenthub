"""
Core evaluation engine implementation.
"""

import time
import uuid
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from .data_models import (
    EvaluationResults,
    AgentOutput,
    EvaluationContext,
    EvaluationConfig,
    EvaluationMode,
    MetricResult,
    MetricResults,
    SampleData,
    EvaluationError
)


class EvaluationEngine:
    """Main evaluation engine for agent assessment."""
    
    def __init__(self, config: Optional[EvaluationConfig] = None):
        """Initialize the evaluation engine."""
        self.config = config or EvaluationConfig()
        self._demo_evaluator = DemoEvaluator(self.config)
        self._benchmark_evaluator = BenchmarkEvaluator(self.config)
    
    def evaluate(
        self,
        agent,
        mode: Union[str, EvaluationMode] = "demo",
        samples: Optional[List[SampleData]] = None,
        context: Optional[EvaluationContext] = None,
        **kwargs
    ) -> EvaluationResults:
        """
        Evaluate an agent using the specified mode.
        
        Args:
            agent: The agent to evaluate
            mode: Evaluation mode ("demo" or "benchmark")
            samples: Sample data for evaluation (optional)
            context: Evaluation context (optional)
            **kwargs: Additional parameters
            
        Returns:
            EvaluationResults object with evaluation data
        """
        # Convert string mode to enum
        if isinstance(mode, str):
            mode = EvaluationMode(mode.lower())
        
        # Set up evaluation context
        if context is None:
            context = EvaluationContext(
                evaluation_mode=mode,
                start_time=datetime.now()
            )
        
        # Update config with mode
        self.config.mode = mode
        
        # Route to appropriate evaluator
        if mode == EvaluationMode.DEMO:
            return self._demo_evaluator.evaluate(agent, samples, context, **kwargs)
        elif mode == EvaluationMode.BENCHMARK:
            return self._benchmark_evaluator.evaluate(agent, samples, context, **kwargs)
        else:
            raise ValueError(f"Unsupported evaluation mode: {mode}")
    
    def get_available_modes(self) -> List[str]:
        """Get list of available evaluation modes."""
        return [mode.value for mode in EvaluationMode]
    
    def get_evaluation_config(self) -> EvaluationConfig:
        """Get current evaluation configuration."""
        return self.config


class DemoEvaluator:
    """Demo mode evaluator for quick agent assessment."""
    
    def __init__(self, config: EvaluationConfig):
        """Initialize demo evaluator."""
        self.config = config
        self._sample_generator = SampleGenerator()
        self._metrics_calculator = MetricsCalculator()
    
    def evaluate(
        self,
        agent,
        samples: Optional[List[SampleData]] = None,
        context: Optional[EvaluationContext] = None,
        **kwargs
    ) -> EvaluationResults:
        """Evaluate agent in demo mode."""
        start_time = time.time()
        
        # Generate samples if not provided
        if samples is None:
            samples = self._sample_generator.generate_demo_samples(self.config.sample_count)
        
        # Set up context
        if context is None:
            context = EvaluationContext(
                evaluation_mode=EvaluationMode.DEMO,
                start_time=datetime.now()
            )
        
        # Evaluate agent on samples
        results = []
        for sample in samples:
            try:
                # Execute agent
                agent_output = self._execute_agent(agent, sample.input_text)
                
                # Calculate basic metrics
                metrics = self._calculate_demo_metrics(agent_output, sample, context)
                
                # Create metric results
                metric_results = MetricResults(
                    agent_output=agent_output,
                    metrics=metrics,
                    timestamp=datetime.now()
                )
                
                results.append(metric_results)
                
            except Exception as e:
                # Handle errors gracefully
                error_result = self._create_error_result(sample, str(e))
                results.append(error_result)
        
        # Calculate summary metrics
        summary_metrics = self._calculate_summary_metrics(results)
        
        # Create evaluation results
        evaluation_results = EvaluationResults(
            agent_name=getattr(agent, 'agent_name', 'Unknown Agent'),
            evaluation_mode=EvaluationMode.DEMO,
            results=results,
            summary_metrics=summary_metrics,
            timestamp=datetime.now(),
            duration=time.time() - start_time,
            benchmark_name=None
        )
        
        return evaluation_results
    
    def _execute_agent(self, agent, input_text: str, method_name: str = None) -> AgentOutput:
        """Execute agent with input text, supporting AgentWrapper interface."""
        start_time = datetime.now()
        
        try:
            # Check if this is an AgentWrapper instance
            if hasattr(agent, 'execute') and hasattr(agent, 'methods'):
                # Use AgentWrapper's execute method
                method_name = method_name or self._detect_primary_method(agent)
                parameters = self._prepare_parameters(agent, method_name, input_text)
                
                result = agent.execute(method_name, parameters)
                output_text = self._extract_output_from_result(result)
                
                # Extract additional metadata from AgentWrapper
                metadata = {
                    'start_time': start_time.isoformat(),
                    'end_time': datetime.now().isoformat(),
                    'response_time': (datetime.now() - start_time).total_seconds(),
                    'method_used': method_name,
                    'parameters': parameters,
                    'agent_type': 'AgentWrapper'
                }
                
                # Add tool information if available
                if hasattr(agent, 'assigned_tools') and agent.assigned_tools:
                    metadata['assigned_tools'] = agent.assigned_tools
                    metadata['tool_count'] = len(agent.assigned_tools)
                
            else:
                # Fallback to generic agent execution
                if hasattr(agent, 'process') or hasattr(agent, 'run') or hasattr(agent, 'execute'):
                    if hasattr(agent, 'process'):
                        output_text = agent.process(input_text)
                    elif hasattr(agent, 'run'):
                        output_text = agent.run(input_text)
                    else:
                        output_text = agent.execute(input_text)
                else:
                    # Try to call the agent directly
                    output_text = agent(input_text)
                
                metadata = {
                    'start_time': start_time.isoformat(),
                    'end_time': datetime.now().isoformat(),
                    'response_time': (datetime.now() - start_time).total_seconds(),
                    'agent_type': 'Generic'
                }
            
            return AgentOutput(
                input_text=input_text,
                output_text=str(output_text),
                timestamp=datetime.now(),
                metadata=metadata
            )
            
        except Exception as e:
            # Return error output
            return AgentOutput(
                input_text=input_text,
                output_text=f"Error: {str(e)}",
                timestamp=datetime.now(),
                metadata={
                    'error': str(e), 
                    'error_type': type(e).__name__,
                    'agent_type': 'AgentWrapper' if hasattr(agent, 'execute') and hasattr(agent, 'methods') else 'Generic'
                }
            )
    
    def _detect_primary_method(self, agent) -> str:
        """Detect the primary method to use for evaluation."""
        if not hasattr(agent, 'methods') or not agent.methods:
            raise ValueError("Agent has no available methods")
        
        # Priority order for method selection based on common AgentHub patterns
        priority_methods = [
            'analyze_text',      # analysis-agent
            'generate_code',     # coding-agent  
            'analyze_paper',     # scientific-paper-analyzer
            'process',           # generic
            'run',               # generic
            'execute'            # generic
        ]
        
        for method in priority_methods:
            if method in agent.methods:
                return method
        
        # Fallback to first available method
        return agent.methods[0]
    
    def _prepare_parameters(self, agent, method_name: str, input_text: str) -> dict:
        """Prepare parameters based on method signature."""
        try:
            method_info = agent.get_method_info(method_name)
            interface_params = method_info.get("parameters", {})
            
            # Map input_text to the primary parameter
            if interface_params:
                # Find the first string parameter
                for param_name, param_info in interface_params.items():
                    param_type = param_info.get("type", "").lower()
                    if param_type == "string" or "text" in param_name.lower() or "input" in param_name.lower():
                        return {param_name: input_text}
                
                # Try common parameter names
                common_names = ['text', 'input', 'prompt', 'query', 'data', 'content']
                for name in common_names:
                    if name in interface_params:
                        return {name: input_text}
                
                # Last resort: use first parameter
                first_param = list(interface_params.keys())[0]
                return {first_param: input_text}
            
            return {}
        except Exception:
            # Fallback to simple text parameter
            return {'text': input_text}
    
    def _extract_output_from_result(self, result) -> str:
        """Extract output text from agent execution result."""
        if isinstance(result, dict):
            # Try common result keys
            for key in ['result', 'output', 'response', 'data', 'content']:
                if key in result:
                    return str(result[key])
            # If no common key found, convert entire dict to string
            return str(result)
        elif isinstance(result, str):
            return result
        else:
            return str(result)
    
    def _calculate_demo_metrics(
        self, 
        agent_output: AgentOutput, 
        sample: SampleData, 
        context: EvaluationContext
    ) -> Dict[str, MetricResult]:
        """Calculate basic metrics for demo mode."""
        metrics = {}
        
        # Response time metric
        if 'response_time' in agent_output.metadata:
            metrics['response_time'] = MetricResult(
                metric_type='performance',
                value=agent_output.metadata['response_time'],
                metadata={'unit': 'seconds'}
            )
        
        # Output length metric
        metrics['output_length'] = MetricResult(
            metric_type='quality',
            value=len(agent_output.output_text),
            metadata={'unit': 'characters'}
        )
        
        # Basic quality metric (simple heuristic)
        quality_score = self._calculate_basic_quality(agent_output, sample)
        metrics['quality_score'] = MetricResult(
            metric_type='quality',
            value=quality_score,
            metadata={'method': 'basic_heuristic'}
        )
        
        # Error detection
        has_error = 'Error:' in agent_output.output_text
        metrics['error_detected'] = MetricResult(
            metric_type='reliability',
            value=1.0 if has_error else 0.0,
            metadata={'error_detected': has_error}
        )
        
        return metrics
    
    def _calculate_basic_quality(self, agent_output: AgentOutput, sample: SampleData) -> float:
        """Calculate basic quality score using simple heuristics."""
        output_text = agent_output.output_text.lower()
        
        # Check for common quality indicators
        quality_indicators = 0
        total_checks = 0
        
        # Length check (not too short, not too long)
        output_length = len(agent_output.output_text)
        if 10 <= output_length <= 1000:
            quality_indicators += 1
        total_checks += 1
        
        # Check for complete sentences
        if '.' in agent_output.output_text or '!' in agent_output.output_text or '?' in agent_output.output_text:
            quality_indicators += 1
        total_checks += 1
        
        # Check for relevant keywords (simple heuristic)
        input_words = set(agent_output.input_text.lower().split())
        output_words = set(output_text.split())
        if input_words.intersection(output_words):
            quality_indicators += 1
        total_checks += 1
        
        # Check for error indicators
        error_indicators = ['error', 'exception', 'failed', 'unable', 'cannot']
        if not any(indicator in output_text for indicator in error_indicators):
            quality_indicators += 1
        total_checks += 1
        
        return quality_indicators / total_checks if total_checks > 0 else 0.0
    
    def _calculate_summary_metrics(self, results: List[MetricResults]) -> Dict[str, float]:
        """Calculate summary metrics from individual results."""
        summary = {}
        
        # Collect all metric values by type
        metric_values = {}
        for result in results:
            for metric_name, metric_result in result.metrics.items():
                if metric_name not in metric_values:
                    metric_values[metric_name] = []
                metric_values[metric_name].append(metric_result.value)
        
        # Calculate averages
        for metric_name, values in metric_values.items():
            if values:
                summary[f"{metric_name}_avg"] = sum(values) / len(values)
                summary[f"{metric_name}_min"] = min(values)
                summary[f"{metric_name}_max"] = max(values)
        
        return summary
    
    def _create_error_result(self, sample: SampleData, error_message: str) -> MetricResults:
        """Create error result for failed evaluation."""
        error_output = AgentOutput(
            input_text=sample.input_text,
            output_text=f"Error: {error_message}",
            timestamp=datetime.now(),
            metadata={'error': error_message}
        )
        
        error_metrics = {
            'error_detected': MetricResult(
                metric_type='reliability',
                value=1.0,
                metadata={'error': error_message}
            )
        }
        
        return MetricResults(
            agent_output=error_output,
            metrics=error_metrics,
            timestamp=datetime.now()
        )


class BenchmarkEvaluator:
    """Benchmark mode evaluator for comprehensive testing."""
    
    def __init__(self, config: EvaluationConfig):
        """Initialize benchmark evaluator."""
        self.config = config
        self._sample_generator = SampleGenerator()
        self._metrics_calculator = MetricsCalculator()
    
    def evaluate(
        self,
        agent,
        samples: Optional[List[SampleData]] = None,
        context: Optional[EvaluationContext] = None,
        **kwargs
    ) -> EvaluationResults:
        """Evaluate agent in benchmark mode."""
        start_time = time.time()
        
        # Generate samples if not provided
        if samples is None:
            samples = self._sample_generator.generate_benchmark_samples(
                self.config.benchmark_name or "default"
            )
        
        # Set up context
        if context is None:
            context = EvaluationContext(
                evaluation_mode=EvaluationMode.BENCHMARK,
                start_time=datetime.now(),
                benchmark_name=self.config.benchmark_name
            )
        
        # Evaluate agent on samples
        results = []
        if self.config.parallel_processing and len(samples) > 1:
            results = self._evaluate_parallel(agent, samples, context)
        else:
            results = self._evaluate_sequential(agent, samples, context)
        
        # Calculate summary metrics
        summary_metrics = self._calculate_summary_metrics(results)
        
        # Create evaluation results
        evaluation_results = EvaluationResults(
            agent_name=getattr(agent, 'agent_name', 'Unknown Agent'),
            evaluation_mode=EvaluationMode.BENCHMARK,
            results=results,
            summary_metrics=summary_metrics,
            timestamp=datetime.now(),
            duration=time.time() - start_time,
            benchmark_name=self.config.benchmark_name
        )
        
        return evaluation_results
    
    def _evaluate_sequential(
        self, 
        agent, 
        samples: List[SampleData], 
        context: EvaluationContext
    ) -> List[MetricResults]:
        """Evaluate samples sequentially."""
        results = []
        for sample in samples:
            try:
                result = self._evaluate_single_sample(agent, sample, context)
                results.append(result)
            except Exception as e:
                error_result = self._create_error_result(sample, str(e))
                results.append(error_result)
        return results
    
    def _evaluate_parallel(
        self, 
        agent, 
        samples: List[SampleData], 
        context: EvaluationContext
    ) -> List[MetricResults]:
        """Evaluate samples in parallel."""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
            # Submit all tasks
            future_to_sample = {
                executor.submit(self._evaluate_single_sample, agent, sample, context): sample
                for sample in samples
            }
            
            # Collect results
            for future in as_completed(future_to_sample):
                try:
                    result = future.result(timeout=self.config.timeout_seconds)
                    results.append(result)
                except Exception as e:
                    sample = future_to_sample[future]
                    error_result = self._create_error_result(sample, str(e))
                    results.append(error_result)
        
        return results
    
    def _evaluate_single_sample(
        self, 
        agent, 
        sample: SampleData, 
        context: EvaluationContext
    ) -> MetricResults:
        """Evaluate a single sample."""
        # Execute agent
        agent_output = self._execute_agent(agent, sample.input_text)
        
        # Calculate comprehensive metrics
        metrics = self._calculate_benchmark_metrics(agent_output, sample, context)
        
        # Create metric results
        return MetricResults(
            agent_output=agent_output,
            metrics=metrics,
            timestamp=datetime.now()
        )
    
    def _execute_agent(self, agent, input_text: str, method_name: str = None) -> AgentOutput:
        """Execute agent with input text, supporting AgentWrapper interface."""
        start_time = datetime.now()
        
        try:
            # Check if this is an AgentWrapper instance
            if hasattr(agent, 'execute') and hasattr(agent, 'methods'):
                # Use AgentWrapper's execute method
                method_name = method_name or self._detect_primary_method(agent)
                parameters = self._prepare_parameters(agent, method_name, input_text)
                
                result = agent.execute(method_name, parameters)
                output_text = self._extract_output_from_result(result)
                
                # Extract additional metadata from AgentWrapper
                metadata = {
                    'start_time': start_time.isoformat(),
                    'end_time': datetime.now().isoformat(),
                    'response_time': (datetime.now() - start_time).total_seconds(),
                    'method_used': method_name,
                    'parameters': parameters,
                    'agent_type': 'AgentWrapper'
                }
                
                # Add tool information if available
                if hasattr(agent, 'assigned_tools') and agent.assigned_tools:
                    metadata['assigned_tools'] = agent.assigned_tools
                    metadata['tool_count'] = len(agent.assigned_tools)
                
            else:
                # Fallback to generic agent execution
                if hasattr(agent, 'process') or hasattr(agent, 'run') or hasattr(agent, 'execute'):
                    if hasattr(agent, 'process'):
                        output_text = agent.process(input_text)
                    elif hasattr(agent, 'run'):
                        output_text = agent.run(input_text)
                    else:
                        output_text = agent.execute(input_text)
                else:
                    # Try to call the agent directly
                    output_text = agent(input_text)
                
                metadata = {
                    'start_time': start_time.isoformat(),
                    'end_time': datetime.now().isoformat(),
                    'response_time': (datetime.now() - start_time).total_seconds(),
                    'agent_type': 'Generic'
                }
            
            return AgentOutput(
                input_text=input_text,
                output_text=str(output_text),
                timestamp=datetime.now(),
                metadata=metadata
            )
            
        except Exception as e:
            # Return error output
            return AgentOutput(
                input_text=input_text,
                output_text=f"Error: {str(e)}",
                timestamp=datetime.now(),
                metadata={
                    'error': str(e), 
                    'error_type': type(e).__name__,
                    'agent_type': 'AgentWrapper' if hasattr(agent, 'execute') and hasattr(agent, 'methods') else 'Generic'
                }
            )
    
    def _detect_primary_method(self, agent) -> str:
        """Detect the primary method to use for evaluation."""
        if not hasattr(agent, 'methods') or not agent.methods:
            raise ValueError("Agent has no available methods")
        
        # Priority order for method selection based on common AgentHub patterns
        priority_methods = [
            'analyze_text',      # analysis-agent
            'generate_code',     # coding-agent  
            'analyze_paper',     # scientific-paper-analyzer
            'process',           # generic
            'run',               # generic
            'execute'            # generic
        ]
        
        for method in priority_methods:
            if method in agent.methods:
                return method
        
        # Fallback to first available method
        return agent.methods[0]
    
    def _prepare_parameters(self, agent, method_name: str, input_text: str) -> dict:
        """Prepare parameters based on method signature."""
        try:
            method_info = agent.get_method_info(method_name)
            interface_params = method_info.get("parameters", {})
            
            # Map input_text to the primary parameter
            if interface_params:
                # Find the first string parameter
                for param_name, param_info in interface_params.items():
                    param_type = param_info.get("type", "").lower()
                    if param_type == "string" or "text" in param_name.lower() or "input" in param_name.lower():
                        return {param_name: input_text}
                
                # Try common parameter names
                common_names = ['text', 'input', 'prompt', 'query', 'data', 'content']
                for name in common_names:
                    if name in interface_params:
                        return {name: input_text}
                
                # Last resort: use first parameter
                first_param = list(interface_params.keys())[0]
                return {first_param: input_text}
            
            return {}
        except Exception:
            # Fallback to simple text parameter
            return {'text': input_text}
    
    def _extract_output_from_result(self, result) -> str:
        """Extract output text from agent execution result."""
        if isinstance(result, dict):
            # Try common result keys
            for key in ['result', 'output', 'response', 'data', 'content']:
                if key in result:
                    return str(result[key])
            # If no common key found, convert entire dict to string
            return str(result)
        elif isinstance(result, str):
            return result
        else:
            return str(result)
    
    def _calculate_benchmark_metrics(
        self, 
        agent_output: AgentOutput, 
        sample: SampleData, 
        context: EvaluationContext
    ) -> Dict[str, MetricResult]:
        """Calculate comprehensive metrics for benchmark mode."""
        metrics = {}
        
        # Performance metrics
        if 'response_time' in agent_output.metadata:
            metrics['response_time'] = MetricResult(
                metric_type='performance',
                value=agent_output.metadata['response_time'],
                metadata={'unit': 'seconds'}
            )
        
        # Quality metrics
        metrics['output_length'] = MetricResult(
            metric_type='quality',
            value=len(agent_output.output_text),
            metadata={'unit': 'characters'}
        )
        
        # Accuracy metrics (if expected output provided)
        if sample.expected_output:
            accuracy = self._calculate_accuracy(agent_output.output_text, sample.expected_output)
            metrics['accuracy'] = MetricResult(
                metric_type='accuracy',
                value=accuracy,
                metadata={'method': 'exact_match'}
            )
        
        # Quality score
        quality_score = self._calculate_quality_score(agent_output, sample)
        metrics['quality_score'] = MetricResult(
            metric_type='quality',
            value=quality_score,
            metadata={'method': 'comprehensive'}
        )
        
        # Reliability metrics
        has_error = 'Error:' in agent_output.output_text
        metrics['error_detected'] = MetricResult(
            metric_type='reliability',
            value=1.0 if has_error else 0.0,
            metadata={'error_detected': has_error}
        )
        
        return metrics
    
    def _calculate_accuracy(self, predicted: str, expected: str) -> float:
        """Calculate accuracy score."""
        if not expected:
            return 0.0
        
        # Simple exact match for now
        return 1.0 if predicted.strip().lower() == expected.strip().lower() else 0.0
    
    def _calculate_quality_score(self, agent_output: AgentOutput, sample: SampleData) -> float:
        """Calculate comprehensive quality score."""
        output_text = agent_output.output_text.lower()
        
        quality_indicators = 0
        total_checks = 0
        
        # Length appropriateness
        output_length = len(agent_output.output_text)
        if 10 <= output_length <= 2000:
            quality_indicators += 1
        total_checks += 1
        
        # Completeness (has some structure)
        if any(punct in agent_output.output_text for punct in '.!?'):
            quality_indicators += 1
        total_checks += 1
        
        # Relevance (contains input keywords)
        input_words = set(agent_output.input_text.lower().split())
        output_words = set(output_text.split())
        if input_words.intersection(output_words):
            quality_indicators += 1
        total_checks += 1
        
        # No error indicators
        error_indicators = ['error', 'exception', 'failed', 'unable', 'cannot', 'sorry']
        if not any(indicator in output_text for indicator in error_indicators):
            quality_indicators += 1
        total_checks += 1
        
        return quality_indicators / total_checks if total_checks > 0 else 0.0
    
    def _calculate_summary_metrics(self, results: List[MetricResults]) -> Dict[str, float]:
        """Calculate summary metrics from individual results."""
        summary = {}
        
        # Collect all metric values by type
        metric_values = {}
        for result in results:
            for metric_name, metric_result in result.metrics.items():
                if metric_name not in metric_values:
                    metric_values[metric_name] = []
                metric_values[metric_name].append(metric_result.value)
        
        # Calculate statistics
        for metric_name, values in metric_values.items():
            if values:
                summary[f"{metric_name}_avg"] = sum(values) / len(values)
                summary[f"{metric_name}_min"] = min(values)
                summary[f"{metric_name}_max"] = max(values)
                summary[f"{metric_name}_std"] = self._calculate_std(values)
        
        return summary
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5
    
    def _create_error_result(self, sample: SampleData, error_message: str) -> MetricResults:
        """Create error result for failed evaluation."""
        error_output = AgentOutput(
            input_text=sample.input_text,
            output_text=f"Error: {error_message}",
            timestamp=datetime.now(),
            metadata={'error': error_message}
        )
        
        error_metrics = {
            'error_detected': MetricResult(
                metric_type='reliability',
                value=1.0,
                metadata={'error': error_message}
            )
        }
        
        return MetricResults(
            agent_output=error_output,
            metrics=error_metrics,
            timestamp=datetime.now()
        )


class SampleGenerator:
    """Generates sample data for evaluation."""
    
    def generate_demo_samples(self, count: int = 5) -> List[SampleData]:
        """Generate demo samples for quick assessment."""
        samples = [
            SampleData(
                input_text="What is the capital of France?",
                expected_output="Paris",
                difficulty="easy",
                category="geography"
            ),
            SampleData(
                input_text="Explain the concept of machine learning in simple terms.",
                expected_output=None,
                difficulty="medium",
                category="technology"
            ),
            SampleData(
                input_text="Write a short poem about the ocean.",
                expected_output=None,
                difficulty="medium",
                category="creative"
            ),
            SampleData(
                input_text="What is 2 + 2?",
                expected_output="4",
                difficulty="easy",
                category="math"
            ),
            SampleData(
                input_text="Describe the process of photosynthesis.",
                expected_output=None,
                difficulty="hard",
                category="science"
            )
        ]
        
        return samples[:count]
    
    def generate_benchmark_samples(self, benchmark_name: str) -> List[SampleData]:
        """Generate benchmark samples for comprehensive testing."""
        # For now, return demo samples
        # In a full implementation, this would load from benchmark definitions
        return self.generate_demo_samples(10)


class MetricsCalculator:
    """Calculates various metrics for evaluation."""
    
    def __init__(self):
        """Initialize metrics calculator."""
        pass
    
    def calculate_metrics(
        self, 
        agent_output: AgentOutput, 
        sample: SampleData, 
        context: EvaluationContext
    ) -> Dict[str, MetricResult]:
        """Calculate all relevant metrics."""
        metrics = {}
        
        # This would be expanded with more sophisticated metric calculations
        # For now, return basic metrics
        
        return metrics
