# Runtime Implementation Details - Phase 3.2

**Document Type**: Implementation Details
**Module**: runtime
**Phase**: 3.2
**Status**: Draft

## 🎯 **Purpose**

Detailed implementation of runtime components for intelligent solve() method support, including agent execution, method selection, and performance monitoring.

## 🏗️ **Architecture Overview**

```
Runtime Components
├── Agent Execution
│   ├── solve() Method Execution
│   ├── Method Selection
│   └── Parameter Extraction
├── Performance Monitoring
│   ├── Execution Metrics
│   ├── LLM Performance
│   └── Error Tracking
├── Caching
│   ├── Method Selection Cache
│   ├── Parameter Cache
│   └── Result Cache
└── Error Handling
    ├── Execution Errors
    ├── LLM Errors
    └── Fallback Strategies
```

## 🔧 **Core Implementation**

### **1. Enhanced Agent Runtime**

```python
# agenthub/runtime/agent_runtime.py
# Add to existing AgentRuntime class

def solve(self, query: str, context: dict = None, **kwargs) -> Any:
    """
    Execute solve() method with intelligent method selection.

    Integrates with existing runtime patterns:
    - Uses existing agent execution framework
    - Leverages current error handling
    - Follows existing performance monitoring
    - Maintains backward compatibility

    Args:
        query: Natural language description of the problem
        context: Additional context for execution
        **kwargs: Additional parameters

    Returns:
        Result from solve() method execution
    """
    logger.info(f"Executing solve() for query: {query}")

    try:
        # Check if agent has custom solve() method
        if self.agent_wrapper.has_method('solve'):
            logger.info("Executing agent custom solve()")
            return self._execute_agent_solve(query, context, **kwargs)

        # Use framework method selection
        logger.info("Executing framework method selection")
        return self._execute_framework_solve(query, context, **kwargs)

    except Exception as e:
        logger.error(f"Solve execution failed: {e}")
        return self._handle_solve_execution_error(e, query, context)

def _execute_agent_solve(self, query: str, context: dict, **kwargs) -> Any:
    """Execute agent's custom solve() method."""
    start_time = time.time()

    try:
        # Execute using existing agent execution framework
        result = self.agent_wrapper.execute('solve', {
            'query': query,
            'context': context,
            **kwargs
        })

        # Record performance metrics
        execution_time = time.time() - start_time
        self._record_solve_performance('agent_custom_solve', execution_time, True)

        return result

    except Exception as e:
        execution_time = time.time() - start_time
        self._record_solve_performance('agent_custom_solve', execution_time, False)
        raise

def _execute_framework_solve(self, query: str, context: dict, **kwargs) -> Any:
    """Execute framework method selection and execution."""
    start_time = time.time()

    try:
        # Initialize LLM decision engine if not already done
        if not hasattr(self, '_llm_engine'):
            from ..core.agents.llm_decision_engine import LLMDecisionEngine
            self._llm_engine = LLMDecisionEngine()

        # Select best method
        selection = self._llm_engine.select_method(query, self.agent_wrapper._get_agent_metadata())

        if selection['confidence'] < 0.7:
            # Try fallback methods
            return self._try_fallback_execution(query, context, **kwargs)

        # Extract parameters
        parameters = self._llm_engine.extract_parameters(query, selection['method_info'])

        # Execute selected method
        result = self.agent_wrapper.execute(selection['method'], parameters)

        # Record performance metrics
        execution_time = time.time() - start_time
        self._record_solve_performance('framework_solve', execution_time, True)

        return result

    except Exception as e:
        execution_time = time.time() - start_time
        self._record_solve_performance('framework_solve', execution_time, False)
        raise

def _try_fallback_execution(self, query: str, context: dict, **kwargs) -> Any:
    """Try fallback execution methods."""
    logger.info("Attempting fallback execution methods")

    # Simple keyword matching fallback
    query_lower = query.lower()
    method_scores = {}

    for method in self.agent_wrapper.methods:
        score = 0
        method_lower = method.lower()

        # Check for keyword matches
        if any(keyword in query_lower for keyword in method_lower.split('_')):
            score += 0.5

        # Check for common patterns
        if 'analyze' in query_lower and 'analyze' in method_lower:
            score += 0.3
        if 'generate' in query_lower and 'generate' in method_lower:
            score += 0.3
        if 'summarize' in query_lower and 'summarize' in method_lower:
            score += 0.3

        method_scores[method] = score

    # Select method with highest score
    if method_scores:
        best_method = max(method_scores, key=method_scores.get)
        best_score = method_scores[best_method]

        if best_score > 0.3:  # Minimum threshold for fallback
            logger.info(f"Using fallback method: {best_method}")
            return self.agent_wrapper.execute(best_method, {'query': query, **kwargs})

    # Last resort: return helpful error message
    return {
        'error': 'Unable to determine appropriate method for query',
        'query': query,
        'available_methods': self.agent_wrapper.methods,
        'suggestion': 'Try being more specific about what you want to accomplish'
    }

def _record_solve_performance(self, operation: str, execution_time: float, success: bool):
    """Record solve() performance metrics."""
    if not hasattr(self, '_solve_performance_metrics'):
        self._solve_performance_metrics = {
            'total_calls': 0,
            'success_count': 0,
            'error_count': 0,
            'total_execution_time': 0.0,
            'average_execution_time': 0.0,
            'min_execution_time': float('inf'),
            'max_execution_time': 0.0
        }

    metrics = self._solve_performance_metrics
    metrics['total_calls'] += 1
    metrics['total_execution_time'] += execution_time
    metrics['average_execution_time'] = metrics['total_execution_time'] / metrics['total_calls']
    metrics['min_execution_time'] = min(metrics['min_execution_time'], execution_time)
    metrics['max_execution_time'] = max(metrics['max_execution_time'], execution_time)

    if success:
        metrics['success_count'] += 1
    else:
        metrics['error_count'] += 1

    # Log performance metrics
    logger.info(f"Solve performance - Operation: {operation}, Time: {execution_time:.2f}s, Success: {success}")

def _handle_solve_execution_error(self, error: Exception, query: str, context: dict) -> Any:
    """Handle solve() execution errors."""
    logger.error(f"Solve execution error: {error}")

    return {
        'error': f'Solve execution failed: {str(error)}',
        'query': query,
        'available_methods': self.agent_wrapper.methods,
        'suggestion': 'Try calling a specific method directly or check agent capabilities'
    }

def get_solve_performance_metrics(self) -> dict:
    """Get solve() performance metrics."""
    if not hasattr(self, '_solve_performance_metrics'):
        return {
            'total_calls': 0,
            'success_count': 0,
            'error_count': 0,
            'average_execution_time': 0.0,
            'min_execution_time': 0.0,
            'max_execution_time': 0.0
        }

    return self._solve_performance_metrics.copy()
```

### **2. Method Selection Runtime**

```python
# agenthub/runtime/method_selection_runtime.py
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MethodSelectionResult:
    """Result of method selection process."""
    selected_method: str
    confidence: float
    reasoning: str
    alternative_methods: List[str]
    processing_time: float
    success: bool

class MethodSelectionRuntime:
    """Runtime for method selection operations."""

    def __init__(self, llm_engine=None):
        """Initialize method selection runtime."""
        self.llm_engine = llm_engine
        self.cache = {}
        self.performance_metrics = {
            'total_selections': 0,
            'successful_selections': 0,
            'failed_selections': 0,
            'average_processing_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }

    def select_method(self, query: str, agent_metadata: Dict[str, Any], context: Dict[str, Any] = None) -> MethodSelectionResult:
        """Select best method for query."""
        start_time = time.time()

        try:
            # Check cache first
            cache_key = self._generate_cache_key(query, agent_metadata)
            if cache_key in self.cache:
                self.performance_metrics['cache_hits'] += 1
                logger.info("Using cached method selection result")
                return self.cache[cache_key]

            self.performance_metrics['cache_misses'] += 1

            # Use LLM engine for method selection
            if self.llm_engine:
                selection = self.llm_engine.select_method(query, agent_metadata, context)
            else:
                selection = self._fallback_method_selection(query, agent_metadata)

            # Create result
            result = MethodSelectionResult(
                selected_method=selection.get('selected_method'),
                confidence=selection.get('confidence', 0.0),
                reasoning=selection.get('reasoning', 'No reasoning provided'),
                alternative_methods=selection.get('alternative_methods', []),
                processing_time=time.time() - start_time,
                success=selection.get('confidence', 0.0) > 0.5
            )

            # Cache result
            self.cache[cache_key] = result

            # Update performance metrics
            self._update_performance_metrics(result)

            return result

        except Exception as e:
            logger.error(f"Method selection failed: {e}")
            return MethodSelectionResult(
                selected_method=None,
                confidence=0.0,
                reasoning=f"Method selection failed: {str(e)}",
                alternative_methods=[],
                processing_time=time.time() - start_time,
                success=False
            )

    def _fallback_method_selection(self, query: str, agent_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback method selection when LLM is not available."""
        available_methods = agent_metadata.get('methods', [])

        if not available_methods:
            return {
                'selected_method': None,
                'confidence': 0.0,
                'reasoning': 'No methods available',
                'alternative_methods': []
            }

        # Simple keyword matching
        query_lower = query.lower()
        method_scores = {}

        for method in available_methods:
            score = 0
            method_lower = method.lower()

            # Check for keyword matches
            if any(keyword in query_lower for keyword in method_lower.split('_')):
                score += 0.5

            # Check for common patterns
            if 'analyze' in query_lower and 'analyze' in method_lower:
                score += 0.3
            if 'generate' in query_lower and 'generate' in method_lower:
                score += 0.3
            if 'summarize' in query_lower and 'summarize' in method_lower:
                score += 0.3

            method_scores[method] = score

        # Select method with highest score
        if method_scores:
            best_method = max(method_scores, key=method_scores.get)
            best_score = method_scores[best_method]

            return {
                'selected_method': best_method,
                'confidence': min(best_score, 0.6),  # Cap at 0.6 for fallback
                'reasoning': 'Fallback keyword matching',
                'alternative_methods': list(method_scores.keys())
            }

        # Last resort: select first available method
        return {
            'selected_method': available_methods[0],
            'confidence': 0.3,
            'reasoning': 'Last resort: first available method',
            'alternative_methods': available_methods[1:]
        }

    def _generate_cache_key(self, query: str, agent_metadata: Dict[str, Any]) -> str:
        """Generate cache key for method selection."""
        # Create a hash of the query and relevant metadata
        key_data = {
            'query': query,
            'agent_id': agent_metadata.get('agent_id', 'unknown'),
            'methods': sorted(agent_metadata.get('methods', [])),
            'interface': agent_metadata.get('interface', {})
        }
        return f"method_selection:{hash(str(key_data))}"

    def _update_performance_metrics(self, result: MethodSelectionResult):
        """Update performance metrics."""
        self.performance_metrics['total_selections'] += 1

        if result.success:
            self.performance_metrics['successful_selections'] += 1
        else:
            self.performance_metrics['failed_selections'] += 1

        # Update average processing time
        total_time = self.performance_metrics['average_processing_time'] * (self.performance_metrics['total_selections'] - 1)
        total_time += result.processing_time
        self.performance_metrics['average_processing_time'] = total_time / self.performance_metrics['total_selections']

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return self.performance_metrics.copy()

    def clear_cache(self):
        """Clear method selection cache."""
        self.cache.clear()
        logger.info("Method selection cache cleared")
```

### **3. Parameter Extraction Runtime**

```python
# agenthub/runtime/parameter_extraction_runtime.py
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ParameterExtractionResult:
    """Result of parameter extraction process."""
    parameters: Dict[str, Any]
    confidence: float
    reasoning: str
    missing_parameters: List[str]
    extracted_values: Dict[str, str]
    processing_time: float
    success: bool

class ParameterExtractionRuntime:
    """Runtime for parameter extraction operations."""

    def __init__(self, llm_engine=None):
        """Initialize parameter extraction runtime."""
        self.llm_engine = llm_engine
        self.cache = {}
        self.performance_metrics = {
            'total_extractions': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'average_processing_time': 0.0,
            'cache_hits': 0,
            'cache_misses': 0
        }

    def extract_parameters(self, query: str, method_info: Dict[str, Any], context: Dict[str, Any] = None) -> ParameterExtractionResult:
        """Extract parameters from query."""
        start_time = time.time()

        try:
            # Check cache first
            cache_key = self._generate_cache_key(query, method_info)
            if cache_key in self.cache:
                self.performance_metrics['cache_hits'] += 1
                logger.info("Using cached parameter extraction result")
                return self.cache[cache_key]

            self.performance_metrics['cache_misses'] += 1

            # Use LLM engine for parameter extraction
            if self.llm_engine:
                extraction = self.llm_engine.extract_parameters(query, method_info, context)
            else:
                extraction = self._fallback_parameter_extraction(query, method_info)

            # Create result
            result = ParameterExtractionResult(
                parameters=extraction.get('parameters', {}),
                confidence=extraction.get('confidence', 0.0),
                reasoning=extraction.get('reasoning', 'No reasoning provided'),
                missing_parameters=extraction.get('missing_parameters', []),
                extracted_values=extraction.get('extracted_values', {}),
                processing_time=time.time() - start_time,
                success=extraction.get('confidence', 0.0) > 0.5
            )

            # Cache result
            self.cache[cache_key] = result

            # Update performance metrics
            self._update_performance_metrics(result)

            return result

        except Exception as e:
            logger.error(f"Parameter extraction failed: {e}")
            return ParameterExtractionResult(
                parameters={},
                confidence=0.0,
                reasoning=f"Parameter extraction failed: {str(e)}",
                missing_parameters=[],
                extracted_values={},
                processing_time=time.time() - start_time,
                success=False
            )

    def _fallback_parameter_extraction(self, query: str, method_info: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback parameter extraction when LLM is not available."""
        method_params = method_info.get('parameters', [])
        parameters = {}

        # Simple parameter extraction based on common patterns
        for param in method_params:
            param_name = param['name']
            param_type = param.get('type', 'string')
            param_default = param.get('default')

            # Try to extract parameter value
            if param_name.lower() in query.lower():
                # Extract value after parameter name
                query_lower = query.lower()
                param_index = query_lower.find(param_name.lower())
                if param_index != -1:
                    # Look for value after parameter name
                    value_start = param_index + len(param_name)
                    if value_start < len(query):
                        value_text = query[value_start:].strip()
                        # Extract value (simple heuristic)
                        if value_text.startswith(':'):
                            value_text = value_text[1:].strip()
                        if value_text.startswith('='):
                            value_text = value_text[1:].strip()

                        # Take first word or phrase as value
                        value = value_text.split()[0] if value_text else None
                        if value:
                            parameters[param_name] = self._convert_parameter_type(value, param_type)

            # Use default value if not extracted
            if param_name not in parameters and param_default is not None:
                parameters[param_name] = param_default

        return {
            'parameters': parameters,
            'confidence': 0.3,  # Low confidence for fallback
            'reasoning': 'Fallback parameter extraction',
            'missing_parameters': [p['name'] for p in method_params if p['name'] not in parameters],
            'extracted_values': {name: str(value) for name, value in parameters.items()}
        }

    def _convert_parameter_type(self, value: Any, expected_type: str) -> Any:
        """Convert parameter value to expected type."""
        try:
            if expected_type == 'int':
                return int(value)
            elif expected_type == 'float':
                return float(value)
            elif expected_type == 'bool':
                return bool(value)
            else:
                return str(value)
        except (ValueError, TypeError):
            logger.warning(f"Failed to convert {value} to {expected_type}")
            return value

    def _generate_cache_key(self, query: str, method_info: Dict[str, Any]) -> str:
        """Generate cache key for parameter extraction."""
        # Create a hash of the query and method info
        key_data = {
            'query': query,
            'method_name': method_info.get('name', 'unknown'),
            'parameters': method_info.get('parameters', [])
        }
        return f"parameter_extraction:{hash(str(key_data))}"

    def _update_performance_metrics(self, result: ParameterExtractionResult):
        """Update performance metrics."""
        self.performance_metrics['total_extractions'] += 1

        if result.success:
            self.performance_metrics['successful_extractions'] += 1
        else:
            self.performance_metrics['failed_extractions'] += 1

        # Update average processing time
        total_time = self.performance_metrics['average_processing_time'] * (self.performance_metrics['total_extractions'] - 1)
        total_time += result.processing_time
        self.performance_metrics['average_processing_time'] = total_time / self.performance_metrics['total_extractions']

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics."""
        return self.performance_metrics.copy()

    def clear_cache(self):
        """Clear parameter extraction cache."""
        self.cache.clear()
        logger.info("Parameter extraction cache cleared")
```

## 🔄 **Integration Points**

### **1. AgentWrapper Integration**

```python
# Uses existing AgentWrapper methods
def solve(self, query: str, context: dict = None, **kwargs) -> Any:
    if self.agent_wrapper.has_method('solve'):
        return self._execute_agent_solve(query, context, **kwargs)

    return self._execute_framework_solve(query, context, **kwargs)

# Uses existing execute() method
def _execute_agent_solve(self, query: str, context: dict, **kwargs) -> Any:
    return self.agent_wrapper.execute('solve', {
        'query': query,
        'context': context,
        **kwargs
    })
```

### **2. LLM Engine Integration**

```python
# Uses LLM decision engine
def _execute_framework_solve(self, query: str, context: dict, **kwargs) -> Any:
    if not hasattr(self, '_llm_engine'):
        from ..core.agents.llm_decision_engine import LLMDecisionEngine
        self._llm_engine = LLMDecisionEngine()

    selection = self._llm_engine.select_method(query, self.agent_wrapper._get_agent_metadata())
    parameters = self._llm_engine.extract_parameters(query, selection['method_info'])

    return self.agent_wrapper.execute(selection['method'], parameters)
```

## 🎯 **Error Handling**

### **1. Execution Error Handling**

```python
def solve(self, query: str, context: dict = None, **kwargs) -> Any:
    try:
        # Main solve logic
        pass
    except Exception as e:
        logger.error(f"Solve execution failed: {e}")
        return self._handle_solve_execution_error(e, query, context)
```

### **2. Method Selection Error Handling**

```python
def select_method(self, query: str, agent_metadata: Dict[str, Any], context: Dict[str, Any] = None) -> MethodSelectionResult:
    try:
        # Method selection logic
        pass
    except Exception as e:
        logger.error(f"Method selection failed: {e}")
        return MethodSelectionResult(
            selected_method=None,
            confidence=0.0,
            reasoning=f"Method selection failed: {str(e)}",
            alternative_methods=[],
            processing_time=time.time() - start_time,
            success=False
        )
```

## 📊 **Performance Considerations**

### **1. Caching Strategy**

```python
def select_method(self, query: str, agent_metadata: Dict[str, Any], context: Dict[str, Any] = None) -> MethodSelectionResult:
    # Check cache first
    cache_key = self._generate_cache_key(query, agent_metadata)
    if cache_key in self.cache:
        self.performance_metrics['cache_hits'] += 1
        return self.cache[cache_key]

    # Generate and cache result
    result = self._execute_method_selection(query, agent_metadata, context)
    self.cache[cache_key] = result
    return result
```

### **2. Performance Monitoring**

```python
def _record_solve_performance(self, operation: str, execution_time: float, success: bool):
    """Record solve() performance metrics."""
    if not hasattr(self, '_solve_performance_metrics'):
        self._solve_performance_metrics = {
            'total_calls': 0,
            'success_count': 0,
            'error_count': 0,
            'total_execution_time': 0.0,
            'average_execution_time': 0.0
        }

    metrics = self._solve_performance_metrics
    metrics['total_calls'] += 1
    metrics['total_execution_time'] += execution_time
    metrics['average_execution_time'] = metrics['total_execution_time'] / metrics['total_calls']

    if success:
        metrics['success_count'] += 1
    else:
        metrics['error_count'] += 1
```

## 🔗 **Dependencies**

- **AgentWrapper**: For agent execution and metadata
- **LLMDecisionEngine**: For method selection and parameter extraction
- **Logging**: For error handling and monitoring
- **Time**: For performance measurement
- **Dataclasses**: For result structures
