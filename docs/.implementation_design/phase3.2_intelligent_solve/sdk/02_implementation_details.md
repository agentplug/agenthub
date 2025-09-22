# SDK Implementation Details - Phase 3.2

**Document Type**: Implementation Details
**Module**: sdk
**Phase**: 3.2
**Status**: Draft

## 🎯 **Purpose**

Detailed implementation of SDK components for intelligent solve() method support, including user-facing APIs, agent loading, and solve() method execution.

## 🏗️ **Architecture Overview**

```
SDK Components
├── User-Facing APIs
│   ├── load_agent()
│   ├── agent.solve()
│   └── solve() Configuration
├── Agent Loading
│   ├── Agent Discovery
│   ├── Agent Validation
│   └── Agent Initialization
├── Solve() Execution
│   ├── Method Selection
│   ├── Parameter Extraction
│   └── Result Processing
└── Error Handling
    ├── User-Friendly Errors
    ├── Fallback Strategies
    └── Debug Information
```

## 🔧 **Core Implementation**

### **1. Enhanced load_agent() Function**

```python
# agenthub/sdk/load_agent.py
# Add to existing load_agent.py

def load_agent(
    agent_id: str,
    namespace: str = None,
    solve_config: dict = None,
    **kwargs
) -> AgentWrapper:
    """
    Load agent with enhanced solve() method support.

    Integrates with existing load_agent patterns:
    - Uses existing agent discovery and validation
    - Leverages current agent loading framework
    - Follows existing error handling patterns
    - Maintains backward compatibility

    Args:
        agent_id: Agent identifier
        namespace: Agent namespace (optional)
        solve_config: Configuration for solve() method
        **kwargs: Additional parameters for agent loading

    Returns:
        AgentWrapper with enhanced solve() method

    Example:
        # Load agent with solve() support
        agent = ah.load_agent("text_analyzer", solve_config={
            'confidence_threshold': 0.8,
            'enable_caching': True,
            'fallback_enabled': True
        })

        # Use solve() method
        result = agent.solve("Analyze the sentiment of this text")
    """
    logger.info(f"Loading agent with solve() support: {agent_id}")

    try:
        # Load agent using existing framework
        agent_wrapper = _load_agent_internal(agent_id, namespace, **kwargs)

        # Enhance with solve() method support
        if solve_config:
            _configure_solve_method(agent_wrapper, solve_config)

        # Initialize solve() method if not already present
        if not hasattr(agent_wrapper, 'solve'):
            _initialize_solve_method(agent_wrapper)

        logger.info(f"Agent loaded successfully with solve() support: {agent_id}")
        return agent_wrapper

    except Exception as e:
        logger.error(f"Failed to load agent with solve() support: {e}")
        raise AgentLoadError(f"Failed to load agent {agent_id}: {str(e)}")

def _configure_solve_method(agent_wrapper: AgentWrapper, solve_config: dict):
    """Configure solve() method with user preferences."""
    logger.info("Configuring solve() method")

    # Set confidence threshold
    if 'confidence_threshold' in solve_config:
        agent_wrapper._solve_confidence_threshold = solve_config['confidence_threshold']

    # Enable/disable caching
    if 'enable_caching' in solve_config:
        agent_wrapper._solve_caching_enabled = solve_config['enable_caching']

    # Enable/disable fallback
    if 'fallback_enabled' in solve_config:
        agent_wrapper._solve_fallback_enabled = solve_config['fallback_enabled']

    # Set LLM service configuration
    if 'llm_config' in solve_config:
        agent_wrapper._solve_llm_config = solve_config['llm_config']

    # Set performance monitoring
    if 'performance_monitoring' in solve_config:
        agent_wrapper._solve_performance_monitoring = solve_config['performance_monitoring']

    logger.info("Solve() method configured successfully")

def _initialize_solve_method(agent_wrapper: AgentWrapper):
    """Initialize solve() method for agent wrapper."""
    logger.info("Initializing solve() method")

    # Add solve() method to agent wrapper
    agent_wrapper.solve = _create_solve_method(agent_wrapper)

    # Initialize solve() configuration
    agent_wrapper._solve_confidence_threshold = 0.7
    agent_wrapper._solve_caching_enabled = True
    agent_wrapper._solve_fallback_enabled = True
    agent_wrapper._solve_llm_config = {}
    agent_wrapper._solve_performance_monitoring = True

    logger.info("Solve() method initialized successfully")

def _create_solve_method(agent_wrapper: AgentWrapper):
    """Create solve() method for agent wrapper."""
    def solve(query: str, context: dict = None, **kwargs) -> Any:
        """
        Intelligent solve method with LLM-powered decision making.

        This method provides a user-friendly interface for solving problems
        using natural language queries. It automatically selects the best
        method and extracts parameters from the query.

        Args:
            query: Natural language description of the problem/task
            context: Additional context for decision making
            **kwargs: Additional parameters to pass to selected method

        Returns:
            Result from the best matching method or agent custom solve

        Example:
            # Simple query
            result = agent.solve("Analyze the sentiment of this text")

            # Query with context
            result = agent.solve(
                "Generate a summary",
                context={'user_id': '123', 'preferences': {'language': 'en'}}
            )

            # Query with additional parameters
            result = agent.solve(
                "Analyze this text",
                text="Sample text to analyze",
                analysis_type="sentiment"
            )
        """
        logger.info(f"Executing solve() for query: {query}")

        try:
            # Check if agent has custom solve() method
            if agent_wrapper.has_method('solve'):
                logger.info("Delegating to agent custom solve()")
                return _delegate_to_agent_solve(agent_wrapper, query, context, **kwargs)

            # Use framework method selection
            logger.info("Using framework method selection")
            return _execute_framework_solve(agent_wrapper, query, context, **kwargs)

        except Exception as e:
            logger.error(f"Solve method failed: {e}")
            return _handle_solve_error(agent_wrapper, e, query, context)

    return solve

def _delegate_to_agent_solve(agent_wrapper: AgentWrapper, query: str, context: dict, **kwargs) -> Any:
    """Delegate to agent's custom solve() method."""
    return agent_wrapper.execute('solve', {
        'query': query,
        'context': context,
        **kwargs
    })

def _execute_framework_solve(agent_wrapper: AgentWrapper, query: str, context: dict, **kwargs) -> Any:
    """Execute framework method selection and execution."""
    # Initialize LLM decision engine if not already done
    if not hasattr(agent_wrapper, '_llm_engine'):
        from ..core.agents.llm_decision_engine import LLMDecisionEngine
        agent_wrapper._llm_engine = LLMDecisionEngine()

    # Select best method
    selection = agent_wrapper._llm_engine.select_method(query, agent_wrapper._get_agent_metadata())

    # Check confidence threshold
    confidence_threshold = getattr(agent_wrapper, '_solve_confidence_threshold', 0.7)
    if selection['confidence'] < confidence_threshold:
        # Try fallback methods
        return _try_fallback_methods(agent_wrapper, query, context, **kwargs)

    # Extract parameters
    parameters = agent_wrapper._llm_engine.extract_parameters(query, selection['method_info'])

    # Execute selected method
    return agent_wrapper.execute(selection['method'], parameters)

def _try_fallback_methods(agent_wrapper: AgentWrapper, query: str, context: dict, **kwargs) -> Any:
    """Try fallback methods when LLM selection fails."""
    fallback_enabled = getattr(agent_wrapper, '_solve_fallback_enabled', True)

    if not fallback_enabled:
        return {
            'error': 'Method selection failed and fallback is disabled',
            'query': query,
            'available_methods': agent_wrapper.methods,
            'suggestion': 'Try being more specific about what you want to accomplish'
        }

    logger.info("Attempting fallback method selection")

    # Simple keyword matching fallback
    query_lower = query.lower()
    method_scores = {}

    for method in agent_wrapper.methods:
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
            return agent_wrapper.execute(best_method, {'query': query, **kwargs})

    # Last resort: return helpful error message
    return {
        'error': 'Unable to determine appropriate method for query',
        'query': query,
        'available_methods': agent_wrapper.methods,
        'suggestion': 'Try being more specific about what you want to accomplish'
    }

def _handle_solve_error(agent_wrapper: AgentWrapper, error: Exception, query: str, context: dict) -> Any:
    """Handle solve() method errors with helpful messages."""
    logger.error(f"Solve method error: {error}")

    return {
        'error': f'Solve method failed: {str(error)}',
        'query': query,
        'available_methods': agent_wrapper.methods,
        'suggestion': 'Try calling a specific method directly or check agent capabilities',
        'debug_info': {
            'agent_id': agent_wrapper.agent_id,
            'namespace': agent_wrapper.namespace,
            'error_type': type(error).__name__
        }
    }
```

### **2. Solve() Configuration Class**

```python
# agenthub/sdk/solve_config.py
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class SolveConfig:
    """Configuration for solve() method."""

    # Confidence threshold for method selection
    confidence_threshold: float = 0.7

    # Enable/disable caching
    enable_caching: bool = True

    # Enable/disable fallback methods
    fallback_enabled: bool = True

    # LLM service configuration
    llm_config: Dict[str, Any] = None

    # Performance monitoring
    performance_monitoring: bool = True

    # Cache TTL in seconds
    cache_ttl: int = 300

    # Maximum retries for LLM calls
    max_retries: int = 3

    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60

    def __post_init__(self):
        """Post-initialization validation."""
        if self.confidence_threshold < 0.0 or self.confidence_threshold > 1.0:
            raise ValueError("Confidence threshold must be between 0.0 and 1.0")

        if self.cache_ttl < 0:
            raise ValueError("Cache TTL must be non-negative")

        if self.max_retries < 0:
            raise ValueError("Max retries must be non-negative")

        if self.rate_limit_requests < 0:
            raise ValueError("Rate limit requests must be non-negative")

        if self.rate_limit_window < 0:
            raise ValueError("Rate limit window must be non-negative")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'confidence_threshold': self.confidence_threshold,
            'enable_caching': self.enable_caching,
            'fallback_enabled': self.fallback_enabled,
            'llm_config': self.llm_config or {},
            'performance_monitoring': self.performance_monitoring,
            'cache_ttl': self.cache_ttl,
            'max_retries': self.max_retries,
            'rate_limit_requests': self.rate_limit_requests,
            'rate_limit_window': self.rate_limit_window
        }

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'SolveConfig':
        """Create from dictionary."""
        return cls(**config_dict)

    @classmethod
    def default(cls) -> 'SolveConfig':
        """Create default configuration."""
        return cls()

    @classmethod
    def high_confidence(cls) -> 'SolveConfig':
        """Create high confidence configuration."""
        return cls(confidence_threshold=0.9, fallback_enabled=False)

    @classmethod
    def fast_mode(cls) -> 'SolveConfig':
        """Create fast mode configuration."""
        return cls(
            confidence_threshold=0.5,
            enable_caching=True,
            cache_ttl=600,
            max_retries=1
        )

    @classmethod
    def debug_mode(cls) -> 'SolveConfig':
        """Create debug mode configuration."""
        return cls(
            confidence_threshold=0.3,
            fallback_enabled=True,
            performance_monitoring=True,
            llm_config={'debug': True}
        )
```

### **3. Solve() Result Processing**

```python
# agenthub/sdk/solve_result.py
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
import json

@dataclass
class SolveResult:
    """Result of solve() method execution."""

    # Main result data
    result: Any

    # Metadata
    method_used: Optional[str] = None
    confidence: float = 0.0
    processing_time: float = 0.0

    # Success/failure
    success: bool = True
    error: Optional[str] = None

    # Debug information
    debug_info: Dict[str, Any] = None

    # Alternative methods
    alternative_methods: List[str] = None

    # Parameter information
    parameters_used: Dict[str, Any] = None
    missing_parameters: List[str] = None

    def __post_init__(self):
        """Post-initialization validation."""
        if self.debug_info is None:
            self.debug_info = {}

        if self.alternative_methods is None:
            self.alternative_methods = []

        if self.parameters_used is None:
            self.parameters_used = {}

        if self.missing_parameters is None:
            self.missing_parameters = []

    def is_successful(self) -> bool:
        """Check if solve() was successful."""
        return self.success and self.error is None

    def get_result(self) -> Any:
        """Get the main result."""
        if self.is_successful():
            return self.result
        else:
            raise SolveError(f"Solve failed: {self.error}")

    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information."""
        return self.debug_info.copy()

    def get_performance_info(self) -> Dict[str, Any]:
        """Get performance information."""
        return {
            'processing_time': self.processing_time,
            'method_used': self.method_used,
            'confidence': self.confidence,
            'success': self.success
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'result': self.result,
            'method_used': self.method_used,
            'confidence': self.confidence,
            'processing_time': self.processing_time,
            'success': self.success,
            'error': self.error,
            'debug_info': self.debug_info,
            'alternative_methods': self.alternative_methods,
            'parameters_used': self.parameters_used,
            'missing_parameters': self.missing_parameters
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SolveResult':
        """Create from dictionary."""
        return cls(**data)

    def __str__(self) -> str:
        """String representation."""
        if self.is_successful():
            return f"SolveResult(success=True, method={self.method_used}, confidence={self.confidence:.2f})"
        else:
            return f"SolveResult(success=False, error={self.error})"

    def __repr__(self) -> str:
        """Detailed representation."""
        return f"SolveResult(result={self.result}, method_used={self.method_used}, confidence={self.confidence}, success={self.success})"

class SolveError(Exception):
    """Exception raised when solve() method fails."""

    def __init__(self, message: str, debug_info: Dict[str, Any] = None):
        super().__init__(message)
        self.debug_info = debug_info or {}

    def get_debug_info(self) -> Dict[str, Any]:
        """Get debug information."""
        return self.debug_info.copy()
```

### **4. Solve() Method Decorators**

```python
# agenthub/sdk/solve_decorators.py
from functools import wraps
from typing import Callable, Any, Dict
import time
import logging

logger = logging.getLogger(__name__)

def solve_method(func: Callable) -> Callable:
    """Decorator for agent custom solve() methods."""

    @wraps(func)
    def wrapper(self, query: str, context: Dict = None, **kwargs) -> Any:
        """Wrapper for solve() method."""
        logger.info(f"Executing custom solve() method: {func.__name__}")

        start_time = time.time()

        try:
            # Execute the custom solve() method
            result = func(self, query, context, **kwargs)

            # Record performance
            execution_time = time.time() - start_time
            logger.info(f"Custom solve() completed in {execution_time:.2f}s")

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Custom solve() failed after {execution_time:.2f}s: {e}")
            raise

    return wrapper

def solve_config(config: Dict[str, Any]) -> Callable:
    """Decorator for configuring solve() method."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, query: str, context: Dict = None, **kwargs) -> Any:
            """Wrapper with configuration."""
            # Apply configuration
            original_config = getattr(self, '_solve_config', {})
            self._solve_config = {**original_config, **config}

            # Execute the method
            return func(self, query, context, **kwargs)

        return wrapper

    return decorator

def solve_performance_monitoring(func: Callable) -> Callable:
    """Decorator for performance monitoring of solve() methods."""

    @wraps(func)
    def wrapper(self, query: str, context: Dict = None, **kwargs) -> Any:
        """Wrapper with performance monitoring."""
        start_time = time.time()

        try:
            result = func(self, query, context, **kwargs)

            # Record performance metrics
            execution_time = time.time() - start_time
            self._record_solve_performance(func.__name__, execution_time, True)

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            self._record_solve_performance(func.__name__, execution_time, False)
            raise

    return wrapper

def solve_error_handling(func: Callable) -> Callable:
    """Decorator for error handling of solve() methods."""

    @wraps(func)
    def wrapper(self, query: str, context: Dict = None, **kwargs) -> Any:
        """Wrapper with error handling."""
        try:
            return func(self, query, context, **kwargs)

        except Exception as e:
            logger.error(f"Solve method error: {e}")

            # Return user-friendly error message
            return {
                'error': f'Solve method failed: {str(e)}',
                'query': query,
                'suggestion': 'Try calling a specific method directly or check agent capabilities',
                'debug_info': {
                    'error_type': type(e).__name__,
                    'method': func.__name__
                }
            }

    return wrapper
```

## 🔄 **Integration Points**

### **1. Existing load_agent() Integration**

```python
# Uses existing load_agent() function
def load_agent(agent_id: str, namespace: str = None, solve_config: dict = None, **kwargs) -> AgentWrapper:
    # Load agent using existing framework
    agent_wrapper = _load_agent_internal(agent_id, namespace, **kwargs)

    # Enhance with solve() method support
    if solve_config:
        _configure_solve_method(agent_wrapper, solve_config)

    return agent_wrapper
```

### **2. AgentWrapper Integration**

```python
# Uses existing AgentWrapper methods
def _delegate_to_agent_solve(agent_wrapper: AgentWrapper, query: str, context: dict, **kwargs) -> Any:
    return agent_wrapper.execute('solve', {
        'query': query,
        'context': context,
        **kwargs
    })

def _execute_framework_solve(agent_wrapper: AgentWrapper, query: str, context: dict, **kwargs) -> Any:
    selection = agent_wrapper._llm_engine.select_method(query, agent_wrapper._get_agent_metadata())
    parameters = agent_wrapper._llm_engine.extract_parameters(query, selection['method_info'])

    return agent_wrapper.execute(selection['method'], parameters)
```

## 🎯 **Error Handling**

### **1. User-Friendly Error Messages**

```python
def _handle_solve_error(agent_wrapper: AgentWrapper, error: Exception, query: str, context: dict) -> Any:
    """Handle solve() method errors with helpful messages."""
    return {
        'error': f'Solve method failed: {str(error)}',
        'query': query,
        'available_methods': agent_wrapper.methods,
        'suggestion': 'Try calling a specific method directly or check agent capabilities',
        'debug_info': {
            'agent_id': agent_wrapper.agent_id,
            'namespace': agent_wrapper.namespace,
            'error_type': type(error).__name__
        }
    }
```

### **2. Configuration Validation**

```python
def __post_init__(self):
    """Post-initialization validation."""
    if self.confidence_threshold < 0.0 or self.confidence_threshold > 1.0:
        raise ValueError("Confidence threshold must be between 0.0 and 1.0")

    if self.cache_ttl < 0:
        raise ValueError("Cache TTL must be non-negative")
```

## 📊 **Performance Considerations**

### **1. Caching Strategy**

```python
def _execute_framework_solve(agent_wrapper: AgentWrapper, query: str, context: dict, **kwargs) -> Any:
    # Check cache first
    cache_enabled = getattr(agent_wrapper, '_solve_caching_enabled', True)
    if cache_enabled:
        cache_key = f"solve:{hash(query)}:{agent_wrapper.agent_id}"
        if cache_key in agent_wrapper._solve_cache:
            return agent_wrapper._solve_cache[cache_key]

    # Execute and cache result
    result = _execute_method_selection(agent_wrapper, query, context, **kwargs)

    if cache_enabled:
        agent_wrapper._solve_cache[cache_key] = result

    return result
```

### **2. Performance Monitoring**

```python
def _record_solve_performance(self, method_name: str, execution_time: float, success: bool):
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
- **Dataclasses**: For configuration and result structures
- **Functools**: For decorators
