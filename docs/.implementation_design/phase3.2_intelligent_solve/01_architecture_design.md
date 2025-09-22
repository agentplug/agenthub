# Phase 3.2: Intelligent Solve() Architecture Design

## 1. System Overview

The intelligent `solve()` method provides a natural language interface to agent capabilities, using LLM-powered decision making to automatically select and execute the most appropriate methods.

## 2. Architecture Components

### 2.1 Framework solve() Method

```python
class AgentWrapper:
    def solve(self, query: str, context: dict = None, **kwargs) -> Any:
        """
        Intelligent solve method with LLM-powered decision making.

        Integrates with existing AgentWrapper patterns:
        - Uses existing has_method() and execute() methods
        - Leverages current tool and knowledge management
        - Follows existing error handling patterns

        Args:
            query: Natural language description of the problem/task
            context: Additional context for decision making
            **kwargs: Additional parameters to pass to selected method

        Returns:
            Result from the best matching method or agent custom solve
        """
        logger.info(f"Solving query: {query}")

        try:
            # 1. Check if agent has custom solve() method using existing has_method()
            if self.has_method('solve'):
                logger.info("Delegating to agent custom solve()")
                return self._delegate_to_agent_solve(query, context, **kwargs)

            # 2. Use LLM to select best method from agent metadata
            logger.info("Using framework method selection")
            return self._llm_method_selection(query, context, **kwargs)

        except Exception as e:
            logger.error(f"Solve method failed: {e}")
            return self._handle_solve_error(e, query, context)

    def _delegate_to_agent_solve(self, query: str, context: dict, **kwargs) -> Any:
        """Delegate to agent's custom solve() method using existing execute() pattern."""
        return self.execute('solve', {
            'query': query,
            'context': context,
            **kwargs
        })

    def _llm_method_selection(self, query: str, context: dict, **kwargs) -> Any:
        """Use LLM to select and execute the best method."""
        # Initialize LLM decision engine if not already done
        if not hasattr(self, '_llm_engine'):
            self._llm_engine = LLMDecisionEngine()

        # Select best method using existing agent metadata
        selection = self._llm_engine.select_method(query, self._get_agent_metadata())

        if selection['confidence'] < 0.7:
            # Try fallback methods
            return self._try_fallback_methods(query, context, **kwargs)

        # Extract parameters
        parameters = self._llm_engine.extract_parameters(query, selection['method_info'])

        # Execute selected method using existing execute() method
        return self.execute(selection['method'], parameters)
```

### 2.2 LLM Decision Engine

```python
class LLMDecisionEngine:
    """LLM-powered decision making for method selection and parameter extraction.

    Integrates with existing CoreLLMService and follows current patterns:
    - Uses existing CoreLLMService for LLM operations
    - Leverages existing agent metadata structure
    - Follows current error handling patterns
    """

    def __init__(self, llm_service=None):
        # Use existing CoreLLMService or create new instance
        from ..llm import CoreLLMService
        self.llm_service = llm_service or CoreLLMService()
        self.cache = {}

    def select_method(self, query: str, agent_metadata: dict) -> dict:
        """Select best method based on query and agent capabilities."""
        # Check cache first
        cache_key = f"{agent_metadata.get('agent_id', 'unknown')}:{hash(query)}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Prepare method information using existing agent structure
        methods_info = self._prepare_methods_info(agent_metadata)

        # Create prompt for method selection
        prompt = self._create_method_selection_prompt(query, methods_info)

        # Call LLM using existing CoreLLMService
        response = self.llm_service.generate(
            prompt,
            system_prompt="You are an AI assistant that selects the best method for solving user queries.",
            return_json=True
        )

        # Parse response
        selection = self._parse_method_selection_response(response)

        # Cache result
        self.cache[cache_key] = selection

        return selection

    def extract_parameters(self, query: str, method_info: dict) -> dict:
        """Extract parameters from natural language query."""
        # Create parameter extraction prompt
        prompt = self._create_parameter_extraction_prompt(query, method_info)

        # Call LLM using existing CoreLLMService
        response = self.llm_service.generate(
            prompt,
            system_prompt="You are an AI assistant that extracts parameters from natural language queries.",
            return_json=True
        )

        # Parse and validate parameters
        parameters = self._parse_parameter_extraction_response(response)

        return self._validate_parameters(parameters, method_info)

    def _prepare_methods_info(self, agent_metadata: dict) -> list:
        """Prepare method information using existing agent structure."""
        methods = []

        # Use existing methods list and interface structure
        for method_name in agent_metadata.get('methods', []):
            method_info = agent_metadata.get('interface', {}).get(method_name, {})

            methods.append({
                'name': method_name,
                'description': method_info.get('description', 'No description available'),
                'parameters': method_info.get('parameters', {}),
                'return_type': method_info.get('return_type', 'unknown')
            })

        return methods
```

### 2.3 Agent Custom solve() Support

```python
# Example agent with custom solve() method
class SpecializedAgent:
    def solve(self, query: str, context: dict = None, **kwargs):
        """Agent-specific solve method with LLM decision making.

        Integrates with existing AgentWrapper patterns:
        - Receives query and context from framework
        - Can use existing tool and knowledge management
        - Can call other agent methods using existing patterns
        - Full control over problem-solving strategy
        """
        # Use existing LLM service if available
        from agenthub.core.llm import CoreLLMService
        llm_service = CoreLLMService()

        # Analyze query using LLM
        analysis = self._analyze_query_with_llm(query, llm_service)

        # Decide approach based on analysis
        approach = self._determine_approach(analysis)

        # Execute approach using existing patterns
        return self._execute_approach(approach, query, context, **kwargs)

    def _analyze_query_with_llm(self, query: str, llm_service):
        """Analyze query using existing LLM service."""
        prompt = f"Analyze this query: {query}"
        response = llm_service.generate(prompt, return_json=True)
        return self._parse_analysis(response)
```

## 3. Decision Flow

### 3.1 Primary Path: Agent Custom solve()

```
User Query → Framework solve() → Agent Custom solve() → LLM Analysis → Execute Logic
```

**When to use:**
- Agent has specialized problem-solving logic
- Complex multi-step workflows
- Agent-specific optimizations
- Custom tool usage patterns

### 3.2 Fallback Path: Method Selection

```
User Query → Framework solve() → LLM Method Selection → Parameter Extraction → Execute Method
```

**When to use:**
- Agent doesn't have custom solve()
- Simple single-method tasks
- Standard problem-solving patterns

## 4. LLM Integration Points

### 4.1 Method Selection Prompt

```python
METHOD_SELECTION_PROMPT = """
You are an AI assistant that selects the best method for solving user queries.

Agent: {agent_name}
Available Methods: {methods}
User Query: {query}

Select the most appropriate method and extract parameters.

Response format:
{
    "selected_method": "method_name",
    "confidence": 0.95,
    "parameters": {"param1": "value1"},
    "reasoning": "Why this method was selected"
}
"""
```

### 4.2 Parameter Extraction Prompt

```python
PARAMETER_EXTRACTION_PROMPT = """
Extract parameters for method '{method_name}' from the user query.

Method Description: {method_description}
Method Parameters: {method_parameters}
User Query: {query}

Extract and map parameters appropriately.

Response format:
{
    "parameters": {"param1": "value1", "param2": "value2"},
    "confidence": 0.90,
    "reasoning": "How parameters were extracted"
}
"""
```

## 5. Error Handling and Fallbacks

### 5.1 Confidence-Based Fallbacks

```python
def _execute_with_fallback(self, method, parameters, query):
    """Execute method with confidence-based fallbacks."""
    confidence_threshold = 0.7

    if method.confidence < confidence_threshold:
        # Try alternative methods
        alternatives = self._get_alternative_methods(query)
        for alt_method in alternatives:
            if alt_method.confidence > confidence_threshold:
                return self._execute_method(alt_method, parameters)

    return self._execute_method(method, parameters)
```

### 5.2 Error Recovery

```python
def _handle_execution_error(self, error, method, query):
    """Handle method execution errors with intelligent recovery."""
    if "parameter" in str(error).lower():
        # Try to fix parameter issues
        return self._retry_with_parameter_fix(method, query)
    elif "method not found" in str(error).lower():
        # Try alternative method selection
        return self._retry_with_alternative_method(query)
    else:
        # Return helpful error message
        return self._create_helpful_error(error, method, query)
```

## 6. Context Integration

### 6.1 Agent Knowledge Integration

```python
def _enhance_query_with_context(self, query: str, context: dict) -> str:
    """Enhance query with agent knowledge and context."""
    enhanced_query = query

    # Add agent knowledge if available
    if self.is_knowledge_available():
        knowledge = self.get_knowledge()
        enhanced_query = f"Context: {knowledge}\n\nQuery: {query}"

    # Add tool context if available
    if self.assigned_tools:
        tool_context = self.get_tool_context_json()
        enhanced_query = f"Available Tools: {tool_context}\n\n{enhanced_query}"

    return enhanced_query
```

### 6.2 Tool Integration

```python
def _integrate_tools_in_decision(self, query: str, method_info: dict) -> dict:
    """Integrate available tools in method selection decision."""
    if not self.assigned_tools:
        return method_info

    # Enhance method selection with tool capabilities
    tool_enhanced_query = f"Query: {query}\nAvailable Tools: {self.assigned_tools}"

    # Use LLM to consider tools in method selection
    enhanced_selection = self.llm_engine.select_method_with_tools(
        tool_enhanced_query,
        method_info
    )

    return enhanced_selection
```

## 7. Performance Considerations

### 7.1 Caching Strategy

```python
class SolveCache:
    """Cache for solve() method selections and results."""

    def __init__(self):
        self.method_selections = {}  # Cache method selections
        self.parameter_extractions = {}  # Cache parameter extractions
        self.results = {}  # Cache results for identical queries

    def get_cached_selection(self, query: str, agent_id: str) -> dict:
        """Get cached method selection."""
        cache_key = f"{agent_id}:{hash(query)}"
        return self.method_selections.get(cache_key)

    def cache_selection(self, query: str, agent_id: str, selection: dict):
        """Cache method selection."""
        cache_key = f"{agent_id}:{hash(query)}"
        self.method_selections[cache_key] = selection
```

### 7.2 Async Support

```python
async def solve_async(self, query: str, context: dict = None, **kwargs) -> Any:
    """Async version of solve() for better performance."""
    # Async LLM calls
    # Async method execution
    # Better resource utilization
    pass
```

## 8. Monitoring and Analytics

### 8.1 Decision Tracking

```python
class SolveAnalytics:
    """Track and analyze solve() method decisions."""

    def track_decision(self, query: str, method: str, confidence: float, success: bool):
        """Track decision outcomes for analysis."""
        pass

    def get_accuracy_metrics(self) -> dict:
        """Get accuracy metrics for method selection."""
        pass

    def get_improvement_suggestions(self) -> list:
        """Get suggestions for improving method selection."""
        pass
```

## 9. Configuration Options

### 9.1 LLM Configuration

```python
class SolveConfig:
    """Configuration for solve() method behavior."""

    def __init__(self):
        self.llm_model = "gpt-4"
        self.confidence_threshold = 0.7
        self.max_retries = 3
        self.enable_caching = True
        self.enable_analytics = True
        self.fallback_strategy = "confidence_based"
```

### 9.2 Agent-Specific Configuration

```python
# Agent can override solve() configuration
class MyAgent:
    def __init__(self):
        self.solve_config = SolveConfig(
            confidence_threshold=0.8,
            max_retries=5,
            fallback_strategy="exhaustive"
        )
```

## 10. Testing Strategy

### 10.1 Unit Tests

- Method selection accuracy
- Parameter extraction correctness
- Error handling scenarios
- Fallback mechanisms

### 10.2 Integration Tests

- End-to-end solve() workflows
- Agent custom solve() integration
- LLM service integration
- Tool integration

### 10.3 Performance Tests

- Response time benchmarks
- Memory usage optimization
- Concurrent request handling
- Cache effectiveness

## 11. Success Metrics

- **Accuracy**: 90%+ correct method selection
- **Performance**: <2s average response time
- **User Satisfaction**: Natural language understanding
- **Reliability**: 99%+ successful executions
- **Flexibility**: Support for diverse agent types
