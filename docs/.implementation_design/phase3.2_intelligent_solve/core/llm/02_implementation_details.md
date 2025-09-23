# Core/LLM Implementation Details - Phase 3.2

**Document Type**: Implementation Details
**Module**: core/llm
**Phase**: 3.2
**Status**: Draft

## 🎯 **Purpose**

Detailed implementation of SolveLLMService for intelligent solve() method support, including prompt templates, error handling, and performance optimization.

## 🏗️ **Architecture Overview**

```
SolveLLMService
├── Method Selection
│   ├── Prompt Templates
│   ├── Response Parsing
│   └── Validation
├── Parameter Extraction
│   ├── Prompt Templates
│   ├── Response Parsing
│   └── Validation
├── Error Handling
│   ├── LLM Service Errors
│   ├── Response Parsing Errors
│   └── Validation Errors
└── Performance
    ├── Caching
    ├── Rate Limiting
    └── Monitoring
```

## 🔧 **Core Implementation**

### **1. SolveLLMService Class**

```python
# agenthub/core/llm/solve_llm_service.py
import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from .llm_service import CoreLLMService

logger = logging.getLogger(__name__)

@dataclass
class MethodSelectionResult:
    """Result of method selection process."""
    selected_method: str
    confidence: float
    reasoning: str
    alternative_methods: List[str]
    extracted_intent: str
    processing_time: float

@dataclass
class ParameterExtractionResult:
    """Result of parameter extraction process."""
    parameters: Dict[str, Any]
    confidence: float
    reasoning: str
    missing_parameters: List[str]
    extracted_values: Dict[str, str]
    processing_time: float

class SolveLLMService:
    """LLM service specialized for solve() method operations.

    Integrates with existing CoreLLMService and provides:
    - Method selection with confidence scoring
    - Parameter extraction with validation
    - Error handling and fallback strategies
    - Performance monitoring and caching
    """

    def __init__(self, llm_service: CoreLLMService = None):
        """Initialize SolveLLMService with existing CoreLLMService."""
        self.llm_service = llm_service or CoreLLMService()
        self.rate_limiter = RateLimiter()
        self.performance_monitor = PerformanceMonitor()

        # Configuration
        self.confidence_threshold = 0.7
        self.max_retries = 3
        self.rate_limit_requests = 100  # per minute

    def select_method(
        self,
        query: str,
        agent_metadata: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> MethodSelectionResult:
        """Select best method using LLM analysis."""
        start_time = time.time()

        try:
            # Rate limiting
            self.rate_limiter.wait_if_needed()

            # Prepare method information
            methods_info = self._prepare_methods_info(agent_metadata)

            # Create and send prompt
            prompt = self._create_method_selection_prompt(query, methods_info, agent_metadata, context)
            response = self._call_llm_with_retry(prompt, "method_selection")

            # Parse and validate response
            result = self._parse_method_selection_response(response)
            result = self._validate_method_selection(result, agent_metadata)

            # Add processing time
            result.processing_time = time.time() - start_time

            # Log performance
            self.performance_monitor.record_method_selection(result)

            return result

        except Exception as e:
            logger.error(f"Method selection failed: {e}")
            return self._handle_method_selection_error(e, query, agent_metadata, start_time)

    def extract_parameters(
        self,
        query: str,
        method_info: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> ParameterExtractionResult:
        """Extract parameters using LLM analysis."""
        start_time = time.time()

        try:
            # Rate limiting
            self.rate_limiter.wait_if_needed()

            # Create and send prompt
            prompt = self._create_parameter_extraction_prompt(query, method_info, context)
            response = self._call_llm_with_retry(prompt, "parameter_extraction")

            # Parse and validate response
            result = self._parse_parameter_extraction_response(response)
            result = self._validate_parameter_extraction(result, method_info)

            # Add processing time
            result.processing_time = time.time() - start_time

            # Log performance
            self.performance_monitor.record_parameter_extraction(result)

            return result

        except Exception as e:
            logger.error(f"Parameter extraction failed: {e}")
            return self._handle_parameter_extraction_error(e, query, method_info, start_time)

    def _prepare_methods_info(self, agent_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prepare method information for LLM analysis."""
        methods = []

        # Use existing agent structure
        for method_name in agent_metadata.get('methods', []):
            method_info = agent_metadata.get('interface', {}).get(method_name, {})

            # Extract parameter information
            parameters = method_info.get('parameters', {})
            param_details = []

            for param_name, param_info in parameters.items():
                if isinstance(param_info, dict):
                    param_type = param_info.get('type', 'unknown')
                    param_desc = param_info.get('description', 'No description')
                    param_required = param_info.get('required', False)
                    param_default = param_info.get('default', None)

                    param_details.append({
                        'name': param_name,
                        'type': param_type,
                        'description': param_desc,
                        'required': param_required,
                        'default': param_default
                    })
                else:
                    param_details.append({
                        'name': param_name,
                        'type': 'string',
                        'description': str(param_info),
                        'required': True,
                        'default': None
                    })

            methods.append({
                'name': method_name,
                'description': method_info.get('description', 'No description available'),
                'parameters': param_details,
                'return_type': method_info.get('return_type', 'unknown')
            })

        return methods

    def _create_method_selection_prompt(
        self,
        query: str,
        methods: List[Dict[str, Any]],
        agent_info: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> str:
        """Create method selection prompt."""
        # Build methods details
        methods_details = []
        for method in methods:
            params = [f"{p['name']} ({p['type']})" for p in method['parameters']]
            methods_details.append(
                f"- {method['name']}: {method['description']}\n"
                f"  Parameters: {', '.join(params) if params else 'None'}\n"
                f"  Return Type: {method['return_type']}"
            )

        # Build context information
        context_info = ""
        if context:
            context_info = f"\nAdditional Context:\n{json.dumps(context, indent=2)}"

        # Build agent capabilities
        capabilities = []
        if agent_info.get('assigned_tools'):
            capabilities.append(f"Tools: {', '.join(agent_info['assigned_tools'])}")
        if agent_info.get('knowledge_available'):
            capabilities.append("Knowledge Base: Available")

        capabilities_info = ""
        if capabilities:
            capabilities_info = f"\nAgent Capabilities:\n{chr(10).join(capabilities)}"

        return f"""
You are an AI assistant that selects the best method for solving user queries.

Agent Information:
- Name: {agent_info.get('name', 'Unknown')}
- Description: {agent_info.get('description', 'No description')}
- Available Methods: {len(methods)} methods
{capabilities_info}

User Query: "{query}"
{context_info}

Available Methods:
{chr(10).join(methods_details)}

Task: Select the most appropriate method and provide confidence score.

Instructions:
1. Analyze the user query to understand the intent and requirements
2. Match the intent to the most appropriate method based on:
   - Method description and purpose
   - Parameter requirements and types
   - Return type expectations
   - Agent capabilities and tools
3. Consider the complexity and scope of the request
4. Provide confidence score (0.0 to 1.0) based on:
   - How well the method matches the intent
   - Whether all required parameters can be extracted
   - Whether the method can fulfill the user's needs
5. If no method is suitable, suggest the closest alternative
6. Consider context and agent capabilities when making decisions

Response Format (JSON):
{{
    "selected_method": "method_name",
    "confidence": 0.95,
    "reasoning": "Detailed explanation of why this method was selected",
    "alternative_methods": ["method1", "method2"],
    "extracted_intent": "What the user wants to accomplish",
    "parameter_confidence": 0.90,
    "complexity_assessment": "simple|moderate|complex",
    "estimated_processing_time": "seconds"
}}
"""

    def _create_parameter_extraction_prompt(
        self,
        query: str,
        method_info: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> str:
        """Create parameter extraction prompt."""
        # Build parameter details
        param_details = []
        for param in method_info.get('parameters', []):
            param_details.append(
                f"- {param['name']} ({param['type']}): {param['description']}\n"
                f"  Required: {param['required']}\n"
                f"  Default: {param['default'] if param['default'] is not None else 'None'}"
            )

        # Build context information
        context_info = ""
        if context:
            context_info = f"\nAdditional Context:\n{json.dumps(context, indent=2)}"

        return f"""
You are an AI assistant that extracts parameters from natural language queries.

Method: {method_info.get('name', 'unknown')}
Method Description: {method_info.get('description', 'No description')}

User Query: "{query}"
{context_info}

Parameter Requirements:
{chr(10).join(param_details)}

Instructions:
1. Analyze the query for parameter values and requirements
2. Map query content to method parameters using:
   - Direct value extraction
   - Context inference
   - Default value application
   - Type conversion and validation
3. Handle missing parameters by:
   - Using default values when available
   - Inferring values from context
   - Marking as missing when not available
4. Validate parameter types and formats
5. Provide confidence score for parameter extraction
6. Explain reasoning for each parameter extraction

Response Format (JSON):
{{
    "parameters": {{
        "param1": "value1",
        "param2": "value2"
    }},
    "confidence": 0.90,
    "reasoning": "Detailed explanation of parameter extraction",
    "missing_parameters": ["param3"],
    "extracted_values": {{
        "param1": "extracted from 'specific text'",
        "param2": "inferred from context"
    }},
    "type_conversions": {{
        "param1": "string -> int"
    }},
    "default_values_used": {{
        "param2": "default_value"
    }}
}}
"""

    def _call_llm_with_retry(self, prompt: str, operation: str) -> str:
        """Call LLM service with retry logic."""
        for attempt in range(self.max_retries):
            try:
                response = self.llm_service.generate(
                    prompt,
                    system_prompt=f"You are an AI assistant specialized in {operation}.",
                    return_json=True
                )
                return response
            except Exception as e:
                logger.warning(f"LLM call attempt {attempt + 1} failed: {e}")
                if attempt == self.max_retries - 1:
                    raise
                time.sleep(2 ** attempt)  # Exponential backoff

        raise Exception("All LLM call attempts failed")

    def _parse_method_selection_response(self, response: str) -> MethodSelectionResult:
        """Parse LLM response for method selection."""
        try:
            data = json.loads(response)
            return MethodSelectionResult(
                selected_method=data.get('selected_method'),
                confidence=data.get('confidence', 0.0),
                reasoning=data.get('reasoning', 'No reasoning provided'),
                alternative_methods=data.get('alternative_methods', []),
                extracted_intent=data.get('extracted_intent', 'Unknown intent'),
                processing_time=0.0  # Will be set later
            )
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse method selection response: {e}")
            return MethodSelectionResult(
                selected_method=None,
                confidence=0.0,
                reasoning=f"Failed to parse LLM response: {e}",
                alternative_methods=[],
                extracted_intent="Unknown",
                processing_time=0.0
            )

    def _parse_parameter_extraction_response(self, response: str) -> ParameterExtractionResult:
        """Parse LLM response for parameter extraction."""
        try:
            data = json.loads(response)
            return ParameterExtractionResult(
                parameters=data.get('parameters', {}),
                confidence=data.get('confidence', 0.0),
                reasoning=data.get('reasoning', 'No reasoning provided'),
                missing_parameters=data.get('missing_parameters', []),
                extracted_values=data.get('extracted_values', {}),
                processing_time=0.0  # Will be set later
            )
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse parameter extraction response: {e}")
            return ParameterExtractionResult(
                parameters={},
                confidence=0.0,
                reasoning=f"Failed to parse LLM response: {e}",
                missing_parameters=[],
                extracted_values={},
                processing_time=0.0
            )

    def _validate_method_selection(self, result: MethodSelectionResult, agent_metadata: Dict[str, Any]) -> MethodSelectionResult:
        """Validate method selection result."""
        available_methods = agent_metadata.get('methods', [])

        # Check if selected method exists
        if result.selected_method and result.selected_method not in available_methods:
            logger.warning(f"Selected method {result.selected_method} not in available methods")
            result.selected_method = None
            result.confidence = 0.0
            result.reasoning = "Selected method not available"

        # Check confidence threshold
        if result.confidence < self.confidence_threshold:
            logger.warning(f"Low confidence method selection: {result.confidence}")
            result.confidence = min(result.confidence, 0.6)  # Cap at 0.6 for low confidence

        return result

    def _validate_parameter_extraction(self, result: ParameterExtractionResult, method_info: Dict[str, Any]) -> ParameterExtractionResult:
        """Validate parameter extraction result."""
        method_params = method_info.get('parameters', [])
        param_names = [p['name'] for p in method_params]

        # Validate parameter names
        valid_params = {}
        for param_name, param_value in result.parameters.items():
            if param_name in param_names:
                valid_params[param_name] = param_value
            else:
                logger.warning(f"Unknown parameter: {param_name}")

        result.parameters = valid_params

        # Check confidence threshold
        if result.confidence < self.confidence_threshold:
            logger.warning(f"Low confidence parameter extraction: {result.confidence}")
            result.confidence = min(result.confidence, 0.6)  # Cap at 0.6 for low confidence

        return result


    def _handle_method_selection_error(
        self,
        error: Exception,
        query: str,
        agent_metadata: Dict[str, Any],
        start_time: float
    ) -> MethodSelectionResult:
        """Handle method selection errors."""
        processing_time = time.time() - start_time

        logger.error(f"Method selection error: {error}")

        return MethodSelectionResult(
            selected_method=None,
            confidence=0.0,
            reasoning=f"Method selection failed: {str(error)}",
            alternative_methods=[],
            extracted_intent="Unknown",
            processing_time=processing_time
        )

    def _handle_parameter_extraction_error(
        self,
        error: Exception,
        query: str,
        method_info: Dict[str, Any],
        start_time: float
    ) -> ParameterExtractionResult:
        """Handle parameter extraction errors."""
        processing_time = time.time() - start_time

        logger.error(f"Parameter extraction error: {error}")

        return ParameterExtractionResult(
            parameters={},
            confidence=0.0,
            reasoning=f"Parameter extraction failed: {str(error)}",
            missing_parameters=[],
            extracted_values={},
            processing_time=processing_time
        )
```

### **2. Rate Limiter Class**

```python
# agenthub/core/llm/rate_limiter.py
import time
import threading
from collections import deque

class RateLimiter:
    """Rate limiter for LLM service calls."""

    def __init__(self, max_requests: int = 100, time_window: int = 60):
        """Initialize rate limiter.

        Args:
            max_requests: Maximum requests per time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
        self.lock = threading.Lock()

    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        with self.lock:
            now = time.time()

            # Remove old requests outside time window
            while self.requests and self.requests[0] <= now - self.time_window:
                self.requests.popleft()

            # Check if we need to wait
            if len(self.requests) >= self.max_requests:
                # Calculate wait time
                oldest_request = self.requests[0]
                wait_time = self.time_window - (now - oldest_request) + 1

                if wait_time > 0:
                    logger.info(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                    time.sleep(wait_time)

            # Add current request
            self.requests.append(now)
```

### **3. Performance Monitor Class**

```python
# agenthub/core/llm/performance_monitor.py
import time
import statistics
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class PerformanceMetrics:
    """Performance metrics for LLM operations."""
    operation: str
    total_calls: int
    average_response_time: float
    min_response_time: float
    max_response_time: float
    success_rate: float
    error_count: int

class PerformanceMonitor:
    """Monitor performance of LLM operations."""

    def __init__(self):
        """Initialize performance monitor."""
        self.metrics = {}
        self.call_history = []
        self.max_history = 1000  # Keep last 1000 calls

    def record_method_selection(self, result: MethodSelectionResult):
        """Record method selection performance."""
        self._record_operation('method_selection', result.processing_time, result.confidence > 0)

    def record_parameter_extraction(self, result: ParameterExtractionResult):
        """Record parameter extraction performance."""
        self._record_operation('parameter_extraction', result.processing_time, result.confidence > 0)

    def _record_operation(self, operation: str, response_time: float, success: bool):
        """Record operation performance."""
        # Add to call history
        self.call_history.append({
            'operation': operation,
            'response_time': response_time,
            'success': success,
            'timestamp': time.time()
        })

        # Keep only recent history
        if len(self.call_history) > self.max_history:
            self.call_history = self.call_history[-self.max_history:]

        # Update metrics
        if operation not in self.metrics:
            self.metrics[operation] = {
                'total_calls': 0,
                'response_times': [],
                'success_count': 0,
                'error_count': 0
            }

        metrics = self.metrics[operation]
        metrics['total_calls'] += 1
        metrics['response_times'].append(response_time)

        if success:
            metrics['success_count'] += 1
        else:
            metrics['error_count'] += 1

    def get_metrics(self, operation: str = None) -> Dict[str, Any]:
        """Get performance metrics."""
        if operation:
            return self._get_operation_metrics(operation)
        else:
            return {op: self._get_operation_metrics(op) for op in self.metrics.keys()}

    def _get_operation_metrics(self, operation: str) -> PerformanceMetrics:
        """Get metrics for specific operation."""
        if operation not in self.metrics:
            return PerformanceMetrics(
                operation=operation,
                total_calls=0,
                average_response_time=0.0,
                min_response_time=0.0,
                max_response_time=0.0,
                success_rate=0.0,
                error_count=0
            )

        metrics = self.metrics[operation]
        response_times = metrics['response_times']

        if not response_times:
            return PerformanceMetrics(
                operation=operation,
                total_calls=0,
                average_response_time=0.0,
                min_response_time=0.0,
                max_response_time=0.0,
                success_rate=0.0,
                error_count=0
            )

        return PerformanceMetrics(
            operation=operation,
            total_calls=metrics['total_calls'],
            average_response_time=statistics.mean(response_times),
            min_response_time=min(response_times),
            max_response_time=max(response_times),
            success_rate=metrics['success_count'] / metrics['total_calls'],
            error_count=metrics['error_count']
        )

    def get_recent_performance(self, operation: str, minutes: int = 5) -> Dict[str, Any]:
        """Get recent performance metrics."""
        cutoff_time = time.time() - (minutes * 60)
        recent_calls = [
            call for call in self.call_history
            if call['operation'] == operation and call['timestamp'] >= cutoff_time
        ]

        if not recent_calls:
            return {
                'calls': 0,
                'average_response_time': 0.0,
                'success_rate': 0.0
            }

        response_times = [call['response_time'] for call in recent_calls]
        success_count = sum(1 for call in recent_calls if call['success'])

        return {
            'calls': len(recent_calls),
            'average_response_time': statistics.mean(response_times),
            'success_rate': success_count / len(recent_calls)
        }
```

## 🔄 **Integration Points**

### **1. CoreLLMService Integration**

```python
# Uses existing CoreLLMService
def __init__(self, llm_service: CoreLLMService = None):
    self.llm_service = llm_service or CoreLLMService()

# Uses existing generate() method
def _call_llm_with_retry(self, prompt: str, operation: str) -> str:
    response = self.llm_service.generate(
        prompt,
        system_prompt=f"You are an AI assistant specialized in {operation}.",
        return_json=True
    )
    return response
```

### **2. AgentWrapper Integration**

```python
# Used by AgentWrapper for method selection
def _llm_method_selection(self, query: str, context: dict, **kwargs) -> Any:
    if not hasattr(self, '_solve_llm_service'):
        from ..llm import SolveLLMService
        self._solve_llm_service = SolveLLMService()

    selection = self._solve_llm_service.select_method(query, self._get_agent_metadata(), context)
    parameters = self._solve_llm_service.extract_parameters(query, selection.method_info, context)

    return self.execute(selection.selected_method, parameters)
```

## 🎯 **Error Handling**

### **1. LLM Service Errors**

```python
def _call_llm_with_retry(self, prompt: str, operation: str) -> str:
    """Call LLM service with retry logic."""
    for attempt in range(self.max_retries):
        try:
            response = self.llm_service.generate(prompt, return_json=True)
            return response
        except Exception as e:
            logger.warning(f"LLM call attempt {attempt + 1} failed: {e}")
            if attempt == self.max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

### **2. Response Parsing Errors**

```python
def _parse_method_selection_response(self, response: str) -> MethodSelectionResult:
    """Parse LLM response for method selection."""
    try:
        data = json.loads(response)
        return MethodSelectionResult(...)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse method selection response: {e}")
        return MethodSelectionResult(
            selected_method=None,
            confidence=0.0,
            reasoning=f"Failed to parse LLM response: {e}",
            ...
        )
```

### **3. Validation Errors**

```python
def _validate_method_selection(self, result: MethodSelectionResult, agent_metadata: Dict[str, Any]) -> MethodSelectionResult:
    """Validate method selection result."""
    available_methods = agent_metadata.get('methods', [])

    # Check if selected method exists
    if result.selected_method and result.selected_method not in available_methods:
        logger.warning(f"Selected method {result.selected_method} not in available methods")
        result.selected_method = None
        result.confidence = 0.0
        result.reasoning = "Selected method not available"

    return result
```

## 📊 **Performance Considerations**

### **1. Caching Strategy**

```python
def select_method(self, query: str, agent_metadata: Dict[str, Any], context: Dict[str, Any] = None) -> MethodSelectionResult:
    # Check cache first
    cache_key = self._generate_cache_key('method_selection', query, agent_metadata)
    if cache_key in self.cache:
        cached_result = self.cache[cache_key]
        if time.time() - cached_result['timestamp'] < self.cache_ttl:
            return cached_result['result']

    # Generate and cache result
    result = self._generate_method_selection(query, agent_metadata, context)
    self.cache[cache_key] = {
        'result': result,
        'timestamp': time.time()
    }
    return result
```

### **2. Rate Limiting**

```python
def select_method(self, query: str, agent_metadata: Dict[str, Any], context: Dict[str, Any] = None) -> MethodSelectionResult:
    # Rate limiting
    self.rate_limiter.wait_if_needed()

    # Continue with method selection
    ...
```

### **3. Performance Monitoring**

```python
def select_method(self, query: str, agent_metadata: Dict[str, Any], context: Dict[str, Any] = None) -> MethodSelectionResult:
    start_time = time.time()

    try:
        result = self._execute_method_selection(query, agent_metadata, context)
        result.processing_time = time.time() - start_time

        # Log performance
        self.performance_monitor.record_method_selection(result)

        return result
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Method selection failed after {processing_time:.2f}s: {e}")
        raise
```

## 🔗 **Dependencies**

- **CoreLLMService**: For LLM operations
- **AgentWrapper**: For agent metadata and method execution
- **Logging**: For error handling and monitoring
- **Threading**: For rate limiting and concurrent operations
- **JSON**: For response parsing and validation
