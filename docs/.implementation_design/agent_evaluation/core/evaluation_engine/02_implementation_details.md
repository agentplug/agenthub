# Core Evaluation Engine - Implementation Details

**Document Type**: Implementation Details  
**Author**: Assistant  
**Date Created**: 2025-06-28  
**Last Updated**: 2025-06-28  
**Status**: Draft  
**Stakeholders**: Developers, Technical Architects, QA Team  
**Feature**: Agent Evaluation System - Core Engine  
**Iteration Count**: 1  

## Overview

This document provides detailed implementation specifications for the core evaluation engine, including class hierarchies, algorithms, data flow, and code organization.

## Class Hierarchy and Architecture

### AgentWrapper Integration

The evaluation engine now includes comprehensive support for AgentHub's AgentWrapper interface, enabling seamless evaluation of prebuilt AgentHub agents.

#### AgentWrapper Detection and Execution

```python
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
            # ... generic execution logic
```

#### Method Detection

```python
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
```

#### Parameter Preparation

```python
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
```

#### Tool-Aware Evaluation

The evaluation engine automatically detects and evaluates agents with assigned tools:

- **Tool Detection**: Checks for `assigned_tools` attribute
- **Tool Metadata**: Extracts tool count and names
- **Tool Usage**: Monitors tool execution during evaluation
- **Tool Metrics**: Calculates tool-specific performance metrics

### Core Class Structure

```python
# Core evaluation engine classes
class EvaluationEngine:
    """Main evaluation engine orchestrator."""
    
    def __init__(self, config: Optional[EvaluationConfig] = None):
        self.config = config or EvaluationConfig()
        self.sample_generator = SampleGeneratorFactory.create(self.config)
        self.agent_executor = AgentExecutorFactory.create(self.config)
        self.output_analyzer = OutputAnalyzerFactory.create(self.config)
        self.metrics_calculator = MetricsCalculatorFactory.create(self.config)
        self.performance_monitor = PerformanceMonitor()
        self.logger = LoggerFactory.get_logger(__name__)
    
    def evaluate(self, agent: Any, config: Optional[EvaluationConfig] = None) -> EvaluationResult:
        """Main evaluation method."""
        pass

class SampleGeneratorFactory:
    """Factory for creating sample generators."""
    
    @staticmethod
    def create(config: EvaluationConfig) -> SampleGenerator:
        """Create appropriate sample generator based on config."""
        pass

class AgentExecutorFactory:
    """Factory for creating agent executors."""
    
    @staticmethod
    def create(config: EvaluationConfig) -> AgentExecutor:
        """Create appropriate agent executor based on config."""
        pass

class OutputAnalyzerFactory:
    """Factory for creating output analyzers."""
    
    @staticmethod
    def create(config: EvaluationConfig) -> OutputAnalyzer:
        """Create appropriate output analyzer based on config."""
        pass

class MetricsCalculatorFactory:
    """Factory for creating metrics calculators."""
    
    @staticmethod
    def create(config: EvaluationConfig) -> MetricsCalculator:
        """Create appropriate metrics calculator based on config."""
        pass
```

### Sample Generation Implementation

```python
class SampleGenerator:
    """Base sample generator implementation."""
    
    def __init__(self, config: SampleConfig):
        self.config = config
        self.templates = self._load_templates()
        self.complexity_levels = self._define_complexity_levels()
    
    def generate_samples(
        self, 
        agent_capabilities: List[str], 
        count: int,
        complexity: str = "medium"
    ) -> List[SampleInput]:
        """Generate samples based on agent capabilities."""
        samples = []
        
        # Determine sample distribution
        distribution = self._calculate_sample_distribution(agent_capabilities, count)
        
        # Generate samples for each capability
        for capability, sample_count in distribution.items():
            capability_samples = self._generate_capability_samples(
                capability, sample_count, complexity
            )
            samples.extend(capability_samples)
        
        # Shuffle and return
        random.shuffle(samples)
        return samples[:count]
    
    def _calculate_sample_distribution(
        self, 
        capabilities: List[str], 
        total_count: int
    ) -> Dict[str, int]:
        """Calculate how many samples to generate for each capability."""
        if not capabilities:
            return {"general": total_count}
        
        # Distribute samples evenly across capabilities
        base_count = total_count // len(capabilities)
        remainder = total_count % len(capabilities)
        
        distribution = {}
        for i, capability in enumerate(capabilities):
            count = base_count + (1 if i < remainder else 0)
            distribution[capability] = count
        
        return distribution
    
    def _generate_capability_samples(
        self, 
        capability: str, 
        count: int, 
        complexity: str
    ) -> List[SampleInput]:
        """Generate samples for a specific capability."""
        samples = []
        
        for _ in range(count):
            # Get template for capability and complexity
            template = self._get_template(capability, complexity)
            
            # Generate sample data
            sample_data = self._generate_sample_data(template)
            
            # Create sample input
            sample = SampleInput(
                data=sample_data,
                sample_type=self._get_sample_type(capability),
                complexity=complexity,
                metadata={
                    "capability": capability,
                    "template_id": template["id"],
                    "generated_at": datetime.now().isoformat()
                }
            )
            
            samples.append(sample)
        
        return samples
    
    def _get_template(self, capability: str, complexity: str) -> Dict[str, Any]:
        """Get template for capability and complexity."""
        templates = self.templates.get(capability, {}).get(complexity, [])
        if not templates:
            # Fallback to general templates
            templates = self.templates.get("general", {}).get(complexity, [])
        
        return random.choice(templates) if templates else self._get_default_template()
    
    def _generate_sample_data(self, template: Dict[str, Any]) -> Any:
        """Generate actual sample data from template."""
        template_type = template.get("type", "text")
        
        if template_type == "text":
            return self._generate_text_sample(template)
        elif template_type == "code":
            return self._generate_code_sample(template)
        elif template_type == "structured_data":
            return self._generate_structured_data_sample(template)
        else:
            raise ValueError(f"Unknown template type: {template_type}")

class TextSampleGenerator(SampleGenerator):
    """Text-specific sample generator."""
    
    def _generate_text_sample(self, template: Dict[str, Any]) -> str:
        """Generate text sample from template."""
        prompt_template = template["prompt"]
        variables = template.get("variables", {})
        
        # Replace variables in template
        sample_text = prompt_template.format(**variables)
        
        # Add complexity variations
        if template.get("complexity_variations"):
            sample_text = self._apply_complexity_variations(
                sample_text, template["complexity_variations"]
            )
        
        return sample_text
    
    def _apply_complexity_variations(
        self, 
        text: str, 
        variations: Dict[str, Any]
    ) -> str:
        """Apply complexity variations to text."""
        # Add length variations
        if "length_multiplier" in variations:
            multiplier = variations["length_multiplier"]
            if multiplier > 1:
                text = text * int(multiplier)
        
        # Add complexity markers
        if "complexity_markers" in variations:
            markers = variations["complexity_markers"]
            text = f"{markers['prefix']}{text}{markers['suffix']}"
        
        return text

class CodeSampleGenerator(SampleGenerator):
    """Code-specific sample generator."""
    
    def _generate_code_sample(self, template: Dict[str, Any]) -> str:
        """Generate code sample from template."""
        code_template = template["code"]
        variables = template.get("variables", {})
        
        # Replace variables in template
        sample_code = code_template.format(**variables)
        
        # Add complexity variations
        if template.get("complexity_variations"):
            sample_code = self._apply_code_complexity_variations(
                sample_code, template["complexity_variations"]
            )
        
        return sample_code
    
    def _apply_code_complexity_variations(
        self, 
        code: str, 
        variations: Dict[str, Any]
    ) -> str:
        """Apply complexity variations to code."""
        # Add error handling
        if variations.get("add_error_handling"):
            code = self._add_error_handling(code)
        
        # Add comments
        if variations.get("add_comments"):
            code = self._add_comments(code)
        
        return code
```

### Agent Execution Implementation

```python
class AgentExecutor:
    """Base agent executor implementation."""
    
    def __init__(self, config: EvaluationConfig):
        self.config = config
        self.timeout = config.timeout or 30
        self.max_memory = config.max_memory or 1024
        self.logger = LoggerFactory.get_logger(__name__)
    
    async def execute_agent(
        self, 
        agent: Any, 
        input_data: Any,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """Execute agent with input data."""
        start_time = time.time()
        memory_before = self._get_memory_usage()
        
        try:
            # Validate agent compatibility
            if not self.validate_agent(agent):
                raise AgentCompatibilityError("Agent is not compatible with evaluation system")
            
            # Prepare execution context
            execution_context = self._prepare_execution_context(agent, input_data)
            
            # Execute agent with timeout
            execution_timeout = timeout or self.timeout
            result = await asyncio.wait_for(
                self._execute_agent_async(agent, execution_context),
                timeout=execution_timeout
            )
            
            # Calculate execution metrics
            execution_time = time.time() - start_time
            memory_after = self._get_memory_usage()
            memory_usage = memory_after - memory_before
            
            return {
                "output": result,
                "execution_time": execution_time,
                "memory_usage": memory_usage,
                "success": True,
                "error": None,
                "metadata": {
                    "agent_type": type(agent).__name__,
                    "input_type": type(input_data).__name__,
                    "execution_context": execution_context
                }
            }
            
        except asyncio.TimeoutError:
            raise TimeoutError(f"Agent execution timed out after {execution_timeout} seconds")
        except Exception as e:
            self.logger.error(f"Agent execution failed: {str(e)}")
            return {
                "output": None,
                "execution_time": time.time() - start_time,
                "memory_usage": 0,
                "success": False,
                "error": str(e),
                "metadata": {}
            }
    
    def _prepare_execution_context(self, agent: Any, input_data: Any) -> Dict[str, Any]:
        """Prepare execution context for agent."""
        return {
            "input_data": input_data,
            "agent_capabilities": self.get_agent_capabilities(agent),
            "execution_mode": "evaluation",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _execute_agent_async(self, agent: Any, context: Dict[str, Any]) -> Any:
        """Execute agent asynchronously."""
        # This is a placeholder - actual implementation depends on agent interface
        if hasattr(agent, 'execute_async'):
            return await agent.execute_async(context["input_data"])
        elif hasattr(agent, 'execute'):
            return agent.execute(context["input_data"])
        else:
            raise AgentCompatibilityError("Agent does not support execution interface")

class AgentHubExecutor(AgentExecutor):
    """AgentHub-specific agent executor."""
    
    def __init__(self, config: EvaluationConfig, agent_runtime, tool_registry):
        super().__init__(config)
        self.agent_runtime = agent_runtime
        self.tool_registry = tool_registry
    
    async def _execute_agent_async(self, agent: Any, context: Dict[str, Any]) -> Any:
        """Execute agent using AgentHub runtime."""
        # Use AgentHub runtime for execution
        result = self.agent_runtime.execute_agent(
            agent.namespace,
            agent.name,
            "evaluate",  # Method name
            {"input": context["input_data"]},
            tool_context=self._prepare_tool_context()
        )
        
        if "error" in result:
            raise ExecutionError(f"Agent execution failed: {result['error']}")
        
        return result.get("result")
    
    def _prepare_tool_context(self) -> Dict[str, Any]:
        """Prepare tool context for agent execution."""
        return {
            "available_tools": self.tool_registry.get_available_tools(),
            "tool_descriptions": self._get_tool_descriptions(),
            "tool_usage_examples": self._get_tool_usage_examples()
        }
```

### Output Analysis Implementation

```python
class OutputAnalyzer:
    """Base output analyzer implementation."""
    
    def __init__(self, config: EvaluationConfig):
        self.config = config
        self.quality_thresholds = self._define_quality_thresholds()
        self.analysis_metrics = self._define_analysis_metrics()
    
    def analyze_output(
        self, 
        input_data: Any, 
        output_data: Any,
        expected_output: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Analyze agent output quality and characteristics."""
        analysis_results = {}
        
        # Basic analysis
        analysis_results.update(self._analyze_basic_characteristics(output_data))
        
        # Quality analysis
        analysis_results.update(self._analyze_quality(input_data, output_data))
        
        # Capability analysis
        analysis_results.update(self._analyze_capabilities(input_data, output_data))
        
        # Performance analysis
        analysis_results.update(self._analyze_performance(output_data))
        
        # Error analysis
        analysis_results.update(self._analyze_errors(output_data))
        
        # Comparative analysis (if expected output provided)
        if expected_output is not None:
            analysis_results.update(self._analyze_comparison(output_data, expected_output))
        
        return analysis_results
    
    def _analyze_basic_characteristics(self, output_data: Any) -> Dict[str, Any]:
        """Analyze basic output characteristics."""
        return {
            "output_type": type(output_data).__name__,
            "output_length": len(str(output_data)) if output_data else 0,
            "is_empty": not bool(output_data),
            "is_none": output_data is None,
            "data_type": self._get_data_type(output_data)
        }
    
    def _analyze_quality(self, input_data: Any, output_data: Any) -> Dict[str, Any]:
        """Analyze output quality."""
        quality_metrics = {}
        
        # Relevance analysis
        quality_metrics["relevance_score"] = self._calculate_relevance_score(input_data, output_data)
        
        # Completeness analysis
        quality_metrics["completeness_score"] = self._calculate_completeness_score(input_data, output_data)
        
        # Coherence analysis
        quality_metrics["coherence_score"] = self._calculate_coherence_score(output_data)
        
        # Overall quality score
        quality_metrics["overall_quality_score"] = self._calculate_overall_quality_score(quality_metrics)
        
        return quality_metrics
    
    def _analyze_capabilities(self, input_data: Any, output_data: Any) -> Dict[str, Any]:
        """Analyze agent capabilities based on output."""
        capabilities = []
        strengths = []
        weaknesses = []
        
        # Analyze based on output characteristics
        if self._demonstrates_text_processing(output_data):
            capabilities.append("text_processing")
            strengths.append("Good text processing capabilities")
        
        if self._demonstrates_code_generation(output_data):
            capabilities.append("code_generation")
            strengths.append("Effective code generation")
        
        if self._demonstrates_reasoning(output_data):
            capabilities.append("reasoning")
            strengths.append("Strong reasoning abilities")
        
        # Identify weaknesses
        if self._has_limitations(output_data):
            weaknesses.append("Some limitations in output quality")
        
        return {
            "capabilities": capabilities,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "capability_confidence": self._calculate_capability_confidence(capabilities)
        }
    
    def _analyze_performance(self, output_data: Any) -> Dict[str, Any]:
        """Analyze performance characteristics."""
        return {
            "response_efficiency": self._calculate_response_efficiency(output_data),
            "resource_usage": self._calculate_resource_usage(output_data),
            "scalability_indicators": self._analyze_scalability_indicators(output_data)
        }
    
    def _analyze_errors(self, output_data: Any) -> Dict[str, Any]:
        """Analyze errors and issues in output."""
        errors = []
        warnings = []
        
        # Check for common error patterns
        if self._has_syntax_errors(output_data):
            errors.append("Syntax errors detected")
        
        if self._has_logic_errors(output_data):
            errors.append("Logic errors detected")
        
        if self._has_incomplete_output(output_data):
            warnings.append("Incomplete output detected")
        
        return {
            "errors": errors,
            "warnings": warnings,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "has_critical_errors": len(errors) > 0
        }

class TextOutputAnalyzer(OutputAnalyzer):
    """Text-specific output analyzer."""
    
    def _calculate_relevance_score(self, input_data: Any, output_data: Any) -> float:
        """Calculate relevance score for text output."""
        if not output_data or not isinstance(output_data, str):
            return 0.0
        
        # Use semantic similarity for relevance
        input_text = str(input_data)
        output_text = str(output_data)
        
        # Simple relevance calculation (can be enhanced with NLP models)
        relevance_score = self._calculate_semantic_similarity(input_text, output_text)
        
        return min(max(relevance_score, 0.0), 1.0)
    
    def _calculate_completeness_score(self, input_data: Any, output_data: Any) -> float:
        """Calculate completeness score for text output."""
        if not output_data or not isinstance(output_data, str):
            return 0.0
        
        # Check if output addresses the input requirements
        input_requirements = self._extract_requirements(input_data)
        addressed_requirements = self._count_addressed_requirements(output_data, input_requirements)
        
        if not input_requirements:
            return 1.0  # No specific requirements to address
        
        return addressed_requirements / len(input_requirements)
    
    def _calculate_coherence_score(self, output_data: Any) -> float:
        """Calculate coherence score for text output."""
        if not output_data or not isinstance(output_data, str):
            return 0.0
        
        # Analyze text coherence using various metrics
        coherence_metrics = []
        
        # Sentence structure coherence
        coherence_metrics.append(self._analyze_sentence_structure(output_data))
        
        # Topic coherence
        coherence_metrics.append(self._analyze_topic_coherence(output_data))
        
        # Logical flow coherence
        coherence_metrics.append(self._analyze_logical_flow(output_data))
        
        return sum(coherence_metrics) / len(coherence_metrics)
```

### Metrics Calculation Implementation

```python
class MetricsCalculator:
    """Base metrics calculator implementation."""
    
    def __init__(self, config: EvaluationConfig):
        self.config = config
        self.metric_definitions = self._load_metric_definitions()
        self.calculation_weights = self._define_calculation_weights()
    
    def calculate_metrics(self, sample_results: List[SampleResult]) -> Dict[str, float]:
        """Calculate evaluation metrics from sample results."""
        if not sample_results:
            return {}
        
        metrics = {}
        
        # Calculate accuracy metrics
        metrics.update(self._calculate_accuracy_metrics(sample_results))
        
        # Calculate quality metrics
        metrics.update(self._calculate_quality_metrics(sample_results))
        
        # Calculate performance metrics
        metrics.update(self._calculate_performance_metrics(sample_results))
        
        # Calculate reliability metrics
        metrics.update(self._calculate_reliability_metrics(sample_results))
        
        # Calculate overall metrics
        metrics.update(self._calculate_overall_metrics(sample_results, metrics))
        
        return metrics
    
    def _calculate_accuracy_metrics(self, sample_results: List[SampleResult]) -> Dict[str, float]:
        """Calculate accuracy-related metrics."""
        successful_results = [r for r in sample_results if r.success and not r.error]
        
        if not successful_results:
            return {
                "accuracy": 0.0,
                "precision": 0.0,
                "recall": 0.0,
                "f1_score": 0.0
            }
        
        # Calculate basic accuracy
        accuracy = len(successful_results) / len(sample_results)
        
        # Calculate precision, recall, F1 (simplified for this context)
        precision = self._calculate_precision(successful_results)
        recall = self._calculate_recall(successful_results)
        f1_score = self._calculate_f1_score(precision, recall)
        
        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score
        }
    
    def _calculate_quality_metrics(self, sample_results: List[SampleResult]) -> Dict[str, float]:
        """Calculate quality-related metrics."""
        quality_scores = [r.quality_score for r in sample_results if r.quality_score is not None]
        
        if not quality_scores:
            return {
                "average_quality": 0.0,
                "quality_consistency": 0.0,
                "quality_improvement": 0.0
            }
        
        average_quality = sum(quality_scores) / len(quality_scores)
        quality_consistency = 1.0 - self._calculate_standard_deviation(quality_scores)
        
        return {
            "average_quality": average_quality,
            "quality_consistency": quality_consistency,
            "quality_improvement": self._calculate_quality_improvement(quality_scores)
        }
    
    def _calculate_performance_metrics(self, sample_results: List[SampleResult]) -> Dict[str, float]:
        """Calculate performance-related metrics."""
        execution_times = [r.execution_time for r in sample_results if r.execution_time is not None]
        memory_usages = [r.memory_usage for r in sample_results if r.memory_usage is not None]
        
        if not execution_times:
            return {
                "average_execution_time": 0.0,
                "execution_time_consistency": 0.0,
                "average_memory_usage": 0.0,
                "memory_efficiency": 0.0
            }
        
        average_execution_time = sum(execution_times) / len(execution_times)
        execution_time_consistency = 1.0 - (self._calculate_standard_deviation(execution_times) / average_execution_time)
        
        average_memory_usage = sum(memory_usages) / len(memory_usages) if memory_usages else 0.0
        memory_efficiency = self._calculate_memory_efficiency(memory_usages)
        
        return {
            "average_execution_time": average_execution_time,
            "execution_time_consistency": execution_time_consistency,
            "average_memory_usage": average_memory_usage,
            "memory_efficiency": memory_efficiency
        }
    
    def _calculate_reliability_metrics(self, sample_results: List[SampleResult]) -> Dict[str, float]:
        """Calculate reliability-related metrics."""
        total_samples = len(sample_results)
        successful_samples = len([r for r in sample_results if r.success and not r.error])
        error_samples = len([r for r in sample_results if r.error is not None])
        
        success_rate = successful_samples / total_samples if total_samples > 0 else 0.0
        error_rate = error_samples / total_samples if total_samples > 0 else 0.0
        reliability_score = success_rate * (1.0 - error_rate)
        
        return {
            "success_rate": success_rate,
            "error_rate": error_rate,
            "reliability_score": reliability_score,
            "consistency_score": self._calculate_consistency_score(sample_results)
        }
    
    def _calculate_overall_metrics(
        self, 
        sample_results: List[SampleResult], 
        individual_metrics: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate overall evaluation metrics."""
        # Weighted combination of individual metrics
        weights = self.calculation_weights
        
        overall_score = (
            individual_metrics.get("accuracy", 0.0) * weights["accuracy"] +
            individual_metrics.get("average_quality", 0.0) * weights["quality"] +
            individual_metrics.get("reliability_score", 0.0) * weights["reliability"] +
            individual_metrics.get("memory_efficiency", 0.0) * weights["efficiency"]
        )
        
        return {
            "overall_score": overall_score,
            "evaluation_completeness": self._calculate_evaluation_completeness(sample_results),
            "confidence_level": self._calculate_confidence_level(sample_results, individual_metrics)
        }
```

## Data Flow and Processing

### Main Evaluation Flow

```python
class EvaluationFlow:
    """Main evaluation flow implementation."""
    
    def __init__(self, evaluation_engine: EvaluationEngine):
        self.evaluation_engine = evaluation_engine
        self.logger = LoggerFactory.get_logger(__name__)
    
    async def execute_evaluation(
        self, 
        agent: Any, 
        config: EvaluationConfig
    ) -> EvaluationResult:
        """Execute complete evaluation flow."""
        try:
            # Phase 1: Preparation
            self.logger.info("Starting evaluation preparation")
            preparation_result = await self._prepare_evaluation(agent, config)
            
            # Phase 2: Sample Generation
            self.logger.info("Generating samples")
            samples = await self._generate_samples(agent, config)
            
            # Phase 3: Agent Execution
            self.logger.info("Executing agent on samples")
            execution_results = await self._execute_agent_on_samples(agent, samples)
            
            # Phase 4: Output Analysis
            self.logger.info("Analyzing outputs")
            analysis_results = await self._analyze_outputs(samples, execution_results)
            
            # Phase 5: Metrics Calculation
            self.logger.info("Calculating metrics")
            metrics = await self._calculate_metrics(analysis_results)
            
            # Phase 6: Result Compilation
            self.logger.info("Compiling results")
            result = await self._compile_results(agent, config, samples, execution_results, metrics)
            
            self.logger.info("Evaluation completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Evaluation failed: {str(e)}")
            return self._create_error_result(agent, config, str(e))
    
    async def _prepare_evaluation(self, agent: Any, config: EvaluationConfig) -> Dict[str, Any]:
        """Prepare evaluation environment."""
        # Validate agent compatibility
        if not self.evaluation_engine.agent_executor.validate_agent(agent):
            raise AgentCompatibilityError("Agent is not compatible")
        
        # Get agent capabilities
        capabilities = self.evaluation_engine.agent_executor.get_agent_capabilities(agent)
        
        # Initialize performance monitoring
        self.evaluation_engine.performance_monitor.start_timer("total_evaluation")
        
        return {
            "agent_capabilities": capabilities,
            "preparation_time": time.time(),
            "compatibility_verified": True
        }
    
    async def _generate_samples(self, agent: Any, config: EvaluationConfig) -> List[SampleInput]:
        """Generate samples for evaluation."""
        capabilities = self.evaluation_engine.agent_executor.get_agent_capabilities(agent)
        
        if config.mode == EvaluationMode.DEMO:
            samples = self.evaluation_engine.sample_generator.generate_samples(
                capabilities, config.samples or 5, config.complexity
            )
        elif config.mode == EvaluationMode.BENCHMARK:
            # Load benchmark samples
            samples = await self._load_benchmark_samples(config.benchmark, config.samples)
        else:
            # Custom benchmark samples
            samples = await self._load_custom_samples(config.custom_benchmark)
        
        return samples
    
    async def _execute_agent_on_samples(
        self, 
        agent: Any, 
        samples: List[SampleInput]
    ) -> List[SampleResult]:
        """Execute agent on all samples."""
        results = []
        
        for i, sample in enumerate(samples):
            self.logger.debug(f"Executing sample {i+1}/{len(samples)}")
            
            try:
                execution_result = await self.evaluation_engine.agent_executor.execute_agent(
                    agent, sample.data, self.evaluation_engine.config.timeout
                )
                
                sample_result = SampleResult(
                    input_data=sample.data,
                    output_data=execution_result["output"],
                    execution_time=execution_result["execution_time"],
                    memory_usage=execution_result["memory_usage"],
                    quality_score=0.0,  # Will be calculated in analysis phase
                    error=execution_result.get("error"),
                    metadata={
                        "sample_index": i,
                        "sample_type": sample.sample_type.value,
                        "complexity": sample.complexity,
                        "execution_success": execution_result["success"]
                    }
                )
                
                results.append(sample_result)
                
            except Exception as e:
                self.logger.error(f"Sample {i+1} execution failed: {str(e)}")
                
                sample_result = SampleResult(
                    input_data=sample.data,
                    output_data=None,
                    execution_time=0.0,
                    memory_usage=0,
                    quality_score=0.0,
                    error=str(e),
                    metadata={
                        "sample_index": i,
                        "sample_type": sample.sample_type.value,
                        "complexity": sample.complexity,
                        "execution_success": False
                    }
                )
                
                results.append(sample_result)
        
        return results
    
    async def _analyze_outputs(
        self, 
        samples: List[SampleInput], 
        execution_results: List[SampleResult]
    ) -> List[SampleResult]:
        """Analyze agent outputs."""
        analyzed_results = []
        
        for sample, result in zip(samples, execution_results):
            if result.success and result.output_data is not None:
                # Analyze output
                analysis = self.evaluation_engine.output_analyzer.analyze_output(
                    sample.data, result.output_data
                )
                
                # Update result with analysis
                result.quality_score = analysis.get("overall_quality_score", 0.0)
                result.metadata.update(analysis)
            
            analyzed_results.append(result)
        
        return analyzed_results
    
    async def _calculate_metrics(self, analysis_results: List[SampleResult]) -> Dict[str, float]:
        """Calculate evaluation metrics."""
        return self.evaluation_engine.metrics_calculator.calculate_metrics(analysis_results)
    
    async def _compile_results(
        self, 
        agent: Any, 
        config: EvaluationConfig,
        samples: List[SampleInput],
        execution_results: List[SampleResult],
        metrics: Dict[str, float]
    ) -> EvaluationResult:
        """Compile final evaluation results."""
        total_execution_time = self.evaluation_engine.performance_monitor.end_timer("total_evaluation")
        total_memory_usage = sum(r.memory_usage for r in execution_results)
        
        # Calculate success rate
        successful_results = [r for r in execution_results if r.success and not r.error]
        success = len(successful_results) / len(execution_results) > 0.5
        
        # Generate summary
        summary = self._generate_summary(execution_results, metrics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(execution_results, metrics)
        
        return EvaluationResult(
            agent_id=getattr(agent, 'id', str(id(agent))),
            mode=config.mode,
            samples=execution_results,
            metrics=metrics,
            summary=summary,
            execution_time=total_execution_time,
            total_memory_usage=total_memory_usage,
            success=success,
            error=None,
            recommendations=recommendations
        )
```

## Performance Optimizations

### Caching Strategy

```python
class EvaluationCache:
    """Caching system for evaluation results."""
    
    def __init__(self, max_size: int = 1000, ttl: int = 3600):
        self.cache = {}
        self.max_size = max_size
        self.ttl = ttl
        self.access_times = {}
    
    def get_cache_key(self, agent_id: str, config: EvaluationConfig) -> str:
        """Generate cache key for evaluation."""
        config_hash = hashlib.md5(str(config).encode()).hexdigest()
        return f"{agent_id}:{config_hash}"
    
    def get(self, key: str) -> Optional[EvaluationResult]:
        """Get cached result."""
        if key in self.cache:
            if time.time() - self.access_times[key] < self.ttl:
                self.access_times[key] = time.time()
                return self.cache[key]
            else:
                del self.cache[key]
                del self.access_times[key]
        return None
    
    def set(self, key: str, result: EvaluationResult) -> None:
        """Cache result."""
        if len(self.cache) >= self.max_size:
            self._evict_oldest()
        
        self.cache[key] = result
        self.access_times[key] = time.time()
    
    def _evict_oldest(self) -> None:
        """Evict oldest cached item."""
        oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
        del self.cache[oldest_key]
        del self.access_times[oldest_key]
```

### Parallel Processing

```python
class ParallelEvaluator:
    """Parallel evaluation processing."""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
    
    async def evaluate_samples_parallel(
        self, 
        agent: Any, 
        samples: List[SampleInput]
    ) -> List[SampleResult]:
        """Evaluate samples in parallel."""
        tasks = []
        
        for sample in samples:
            task = asyncio.create_task(
                self._evaluate_single_sample(agent, sample)
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(SampleResult(
                    input_data=samples[i].data,
                    output_data=None,
                    execution_time=0.0,
                    memory_usage=0,
                    quality_score=0.0,
                    error=str(result)
                ))
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def _evaluate_single_sample(
        self, 
        agent: Any, 
        sample: SampleInput
    ) -> SampleResult:
        """Evaluate a single sample."""
        # Implementation for single sample evaluation
        pass
```

## Code Organization

### Directory Structure

```
agentmanager/evaluation/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── evaluation_engine.py
│   ├── sample_generator.py
│   ├── agent_executor.py
│   ├── output_analyzer.py
│   ├── metrics_calculator.py
│   └── performance_monitor.py
├── generators/
│   ├── __init__.py
│   ├── text_generator.py
│   ├── code_generator.py
│   └── structured_data_generator.py
├── analyzers/
│   ├── __init__.py
│   ├── text_analyzer.py
│   ├── code_analyzer.py
│   └── structured_data_analyzer.py
├── calculators/
│   ├── __init__.py
│   ├── accuracy_calculator.py
│   ├── quality_calculator.py
│   ├── performance_calculator.py
│   └── reliability_calculator.py
├── utils/
│   ├── __init__.py
│   ├── cache.py
│   ├── parallel_processor.py
│   └── validators.py
└── config/
    ├── __init__.py
    ├── templates.py
    └── thresholds.py
```

### Module Dependencies

```python
# Core module dependencies
evaluation_engine.py:
    - sample_generator.py
    - agent_executor.py
    - output_analyzer.py
    - metrics_calculator.py
    - performance_monitor.py

sample_generator.py:
    - generators/text_generator.py
    - generators/code_generator.py
    - generators/structured_data_generator.py
    - config/templates.py

agent_executor.py:
    - utils/validators.py
    - (AgentHub runtime integration)

output_analyzer.py:
    - analyzers/text_analyzer.py
    - analyzers/code_analyzer.py
    - analyzers/structured_data_analyzer.py

metrics_calculator.py:
    - calculators/accuracy_calculator.py
    - calculators/quality_calculator.py
    - calculators/performance_calculator.py
    - calculators/reliability_calculator.py
```

## Next Steps

1. **Implementation**: Begin implementing the core evaluation engine classes
2. **Testing**: Create unit tests for each component
3. **Integration**: Integrate with AgentHub runtime and components
4. **Performance**: Optimize for performance requirements
5. **Documentation**: Generate API documentation from interfaces

---

**Note**: This implementation design represents the current understanding of how to implement the core evaluation engine. The design should be reviewed and validated with the development team before implementation begins.
