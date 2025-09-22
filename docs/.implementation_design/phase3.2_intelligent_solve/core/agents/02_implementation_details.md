# Core/Agents Implementation Details - Phase 3.2

**Document Type**: Implementation Details
**Module**: core/agents
**Phase**: 3.2
**Status**: Draft

## 🎯 **Purpose**

Detailed implementation of enhanced AgentWrapper with solve() method, LLMDecisionEngine, and agent custom solve() support.

## 🏗️ **Architecture Overview**

```
User Query
├── solve() method call
├── Agent custom solve() check
└── Framework method selection

Core/Agents Module
├── Enhanced AgentWrapper
│   ├── solve() method
│   ├── _delegate_to_agent_solve()
│   └── _llm_method_selection()
├── LLMDecisionEngine
│   ├── select_method()
│   ├── extract_parameters()
│   └── _fallback_method_selection()
└── AgentSolveInterface
    ├── solve() base interface
    └── LLM integration helpers

Existing Integration
├── CoreLLMService
├── AgentWrapper (existing)
├── Tool Management
└── Knowledge Management
```

## 🔧 **Core Implementation**

### **1. Enhanced AgentWrapper Class**

```python
# agenthub/core/agents/wrapper.py
# Add to existing AgentWrapper class

def solve(self, query: str, context: dict = None, **kwargs) -> Any:
    """
    Intelligent solve method with LLM-powered decision making.

    Integrates with existing AgentWrapper patterns:
    - Uses existing has_method() and execute() methods
    - Leverages current tool and knowledge management
    - Follows existing error handling patterns
    - Maintains backward compatibility

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
        from .llm_decision_engine import LLMDecisionEngine
        self._llm_engine = LLMDecisionEngine()

    # Select best method using existing agent metadata structure
    selection = self._llm_engine.select_method(query, self._get_agent_metadata())

    if selection['confidence'] < 0.7:
        # Try fallback methods
        return self._try_fallback_methods(query, context, **kwargs)

    # Extract parameters
    parameters = self._llm_engine.extract_parameters(query, selection['method_info'])

    # Execute selected method using existing execute() method
    return self.execute(selection['method'], parameters)

def _get_agent_metadata(self) -> dict:
    """Get agent metadata in format expected by LLM decision engine."""
    return {
        'agent_id': self.agent_id,
        'name': self.name,
        'namespace': self.namespace,
        'description': self.description,
        'methods': self.methods,
        'interface': self.interface,
        'assigned_tools': self.assigned_tools,
        'knowledge_available': self.is_knowledge_available()
    }

def _try_fallback_methods(self, query: str, context: dict, **kwargs) -> Any:
    """Try fallback methods when LLM selection fails."""
    # Simple keyword matching fallback
    query_lower = query.lower()
    method_scores = {}

    for method in self.methods:
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
            logger.info(f"Using fallback method selection: {best_method}")
            return self.execute(best_method, {'query': query, **kwargs})

    # Last resort: return helpful error message
    return {
        'error': 'Unable to determine appropriate method for query',
        'query': query,
        'available_methods': self.methods,
        'suggestion': 'Try being more specific about what you want to accomplish'
    }

def _handle_solve_error(self, error: Exception, query: str, context: dict) -> Any:
    """Handle solve() method errors with helpful messages."""
    logger.error(f"Solve method error: {error}")

    return {
        'error': f'Solve method failed: {str(error)}',
        'query': query,
        'available_methods': self.methods,
        'suggestion': 'Try calling a specific method directly or check agent capabilities'
    }
```

### **2. LLMDecisionEngine Class**

```python
# agenthub/core/agents/llm_decision_engine.py
import json
import logging
from typing import Dict, List, Any, Optional
from ..llm import CoreLLMService

logger = logging.getLogger(__name__)

class LLMDecisionEngine:
    """LLM-powered decision making for method selection and parameter extraction.

    Integrates with existing CoreLLMService and follows current patterns:
    - Uses existing CoreLLMService for LLM operations
    - Leverages existing agent metadata structure
    - Follows current error handling patterns
    """

    def __init__(self, llm_service: CoreLLMService = None):
        # Use existing CoreLLMService or create new instance
        self.llm_service = llm_service or CoreLLMService()
        self.cache = {}
        self.confidence_threshold = 0.7

    def select_method(self, query: str, agent_metadata: dict) -> dict:
        """Select best method using LLM analysis."""
        # Check cache first
        cache_key = f"{agent_metadata.get('agent_id', 'unknown')}:{hash(query)}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Prepare method information using existing agent structure
        methods_info = self._prepare_methods_info(agent_metadata)

        # Create prompt for method selection
        prompt = self._create_method_selection_prompt(query, methods_info, agent_metadata)

        try:
            # Call LLM using existing CoreLLMService
            response = self.llm_service.generate(
                prompt,
                system_prompt="You are an AI assistant that selects the best method for solving user queries.",
                return_json=True
            )

            # Parse response
            selection = self._parse_method_selection_response(response)

            # Validate selection
            if not self._validate_method_selection(selection, agent_metadata):
                selection = self._fallback_method_selection(query, agent_metadata)

            # Cache result
            self.cache[cache_key] = selection

            return selection

        except Exception as e:
            logger.error(f"LLM method selection failed: {e}")
            return self._fallback_method_selection(query, agent_metadata)

    def extract_parameters(self, query: str, method_info: dict) -> dict:
        """Extract parameters using LLM analysis."""
        # Create parameter extraction prompt
        prompt = self._create_parameter_extraction_prompt(query, method_info)

        try:
            # Call LLM using existing CoreLLMService
            response = self.llm_service.generate(
                prompt,
                system_prompt="You are an AI assistant that extracts parameters from natural language queries.",
                return_json=True
            )

            # Parse and validate parameters
            extraction = self._parse_parameter_extraction_response(response)
            validated_params = self._validate_parameters(extraction['parameters'], method_info)

            return {
                'parameters': validated_params,
                'confidence': extraction['confidence'],
                'reasoning': extraction['reasoning']
            }

        except Exception as e:
            logger.error(f"LLM parameter extraction failed: {e}")
            return self._fallback_parameter_extraction(query, method_info)

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

    def _create_method_selection_prompt(self, query: str, methods: list, agent_info: dict) -> str:
        """Create method selection prompt."""
        methods_details = []
        for method in methods:
            params = list(method['parameters'].keys()) if method['parameters'] else []
            methods_details.append(
                f"- {method['name']}: {method['description']} (Parameters: {', '.join(params)})"
            )

        return f"""
You are an AI assistant that selects the best method for solving user queries.

Agent Information:
- Name: {agent_info.get('name', 'Unknown')}
- Description: {agent_info.get('description', 'No description')}
- Available Methods: {len(methods)} methods

User Query: "{query}"

Available Methods:
{chr(10).join(methods_details)}

Task: Select the most appropriate method and provide confidence score.

Instructions:
1. Analyze the user query to understand the intent
2. Match the intent to the most appropriate method
3. Consider method descriptions and parameter requirements
4. Provide confidence score (0.0 to 1.0)
5. If no method is suitable, suggest the closest alternative

Response Format (JSON):
{{
    "selected_method": "method_name",
    "confidence": 0.95,
    "reasoning": "Why this method was selected",
    "alternative_methods": ["method1", "method2"],
    "extracted_intent": "What the user wants to accomplish"
}}
"""

    def _create_parameter_extraction_prompt(self, query: str, method_info: dict) -> str:
        """Create parameter extraction prompt."""
        params = method_info.get('parameters', {})
        param_details = []

        for param_name, param_info in params.items():
            if isinstance(param_info, dict):
                param_type = param_info.get('type', 'unknown')
                param_desc = param_info.get('description', 'No description')
                param_details.append(f"- {param_name} ({param_type}): {param_desc}")
            else:
                param_details.append(f"- {param_name}: {param_info}")

        return f"""
You are an AI assistant that extracts parameters from natural language queries.

Method: {method_info.get('name', 'unknown')}
Method Description: {method_info.get('description', 'No description')}

User Query: "{query}"

Parameter Requirements:
{chr(10).join(param_details)}

Instructions:
1. Analyze the query for parameter values
2. Map query content to method parameters
3. Use default values when parameters are not specified
4. Validate parameter types and formats
5. Provide confidence score for parameter extraction

Response Format (JSON):
{{
    "parameters": {{
        "param1": "value1",
        "param2": "value2"
    }},
    "confidence": 0.90,
    "reasoning": "How parameters were extracted",
    "missing_parameters": ["param3"],
    "extracted_values": {{
        "param1": "extracted from 'specific text'"
    }}
}}
"""

    def _parse_method_selection_response(self, response: str) -> dict:
        """Parse LLM response for method selection."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM method selection response")
            return {
                'selected_method': None,
                'confidence': 0.0,
                'reasoning': 'Failed to parse LLM response',
                'error': 'Invalid JSON response from LLM'
            }

    def _parse_parameter_extraction_response(self, response: str) -> dict:
        """Parse LLM response for parameter extraction."""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM parameter extraction response")
            return {
                'parameters': {},
                'confidence': 0.0,
                'reasoning': 'Failed to parse LLM response',
                'error': 'Invalid JSON response from LLM'
            }

    def _validate_method_selection(self, selection: dict, agent_metadata: dict) -> bool:
        """Validate that selected method exists and is appropriate."""
        if not selection or 'selected_method' not in selection:
            return False

        selected_method = selection['selected_method']
        available_methods = agent_metadata.get('methods', [])

        if selected_method not in available_methods:
            logger.warning(f"Selected method {selected_method} not in available methods")
            return False

        if selection.get('confidence', 0) < self.confidence_threshold:
            logger.warning(f"Low confidence method selection: {selection['confidence']}")
            return False

        return True

    def _validate_parameters(self, parameters: dict, method_info: dict) -> dict:
        """Validate and clean extracted parameters."""
        method_params = method_info.get('parameters', {})
        validated_params = {}

        for param_name, param_value in parameters.items():
            if param_name in method_params:
                # Basic type validation
                param_info = method_params[param_name]
                if isinstance(param_info, dict):
                    expected_type = param_info.get('type', 'string')
                    validated_params[param_name] = self._convert_parameter_type(param_value, expected_type)
                else:
                    validated_params[param_name] = param_value
            else:
                logger.warning(f"Unknown parameter: {param_name}")

        return validated_params

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

    def _fallback_method_selection(self, query: str, agent_metadata: dict) -> dict:
        """Fallback method selection when LLM fails."""
        available_methods = agent_metadata.get('methods', [])

        if not available_methods:
            return {
                'selected_method': None,
                'confidence': 0.0,
                'reasoning': 'No methods available',
                'error': 'No methods available for this agent'
            }

        # Simple keyword matching fallback
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

    def _fallback_parameter_extraction(self, query: str, method_info: dict) -> dict:
        """Fallback parameter extraction when LLM fails."""
        # Simple parameter extraction based on common patterns
        parameters = {}

        # Extract text parameter if method has text parameter
        method_params = method_info.get('parameters', {})
        if 'text' in method_params:
            parameters['text'] = query

        return {
            'parameters': parameters,
            'confidence': 0.3,
            'reasoning': 'Fallback parameter extraction',
            'missing_parameters': list(method_params.keys())
        }
```

### **3. AgentSolveInterface Class**

```python
# agenthub/core/agents/agent_solve_interface.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class AgentSolveInterface(ABC):
    """Base interface for agent custom solve() methods.

    Integrates with existing AgentHub patterns:
    - Uses existing CoreLLMService for LLM operations
    - Leverages existing tool and knowledge management
    - Follows current error handling patterns
    """

    def __init__(self, agent_wrapper=None):
        self.agent_wrapper = agent_wrapper
        self.llm_service = None
        self._initialize_llm_service()

    def _initialize_llm_service(self):
        """Initialize LLM service for agent custom solve()."""
        try:
            from ..llm import CoreLLMService
            self.llm_service = CoreLLMService()
        except ImportError:
            logger.warning("LLM service not available for agent custom solve()")

    @abstractmethod
    def solve(self, query: str, context: Dict = None, **kwargs) -> Any:
        """
        Agent-specific solve method with LLM decision making.

        Args:
            query: Natural language description of the problem
            context: Additional context from framework
            **kwargs: Additional parameters

        Returns:
            Solution to the problem
        """
        pass

    def _analyze_query(self, query: str) -> Dict:
        """Analyze query to understand intent and requirements."""
        if not self.llm_service:
            return self._basic_query_analysis(query)

        prompt = f"""
        Analyze this query to understand the user's intent and requirements:

        Query: "{query}"

        Provide analysis in JSON format:
        {{
            "intent": "What the user wants to accomplish",
            "complexity": "simple|moderate|complex",
            "required_capabilities": ["capability1", "capability2"],
            "parameters": {{"param1": "value1"}},
            "context_needed": ["context1", "context2"],
            "estimated_steps": 3
        }}
        """

        try:
            response = self.llm_service.generate(prompt, return_json=True)
            return self._parse_analysis_response(response)
        except Exception as e:
            logger.error(f"Query analysis failed: {e}")
            return self._basic_query_analysis(query)

    def _basic_query_analysis(self, query: str) -> Dict:
        """Basic query analysis without LLM."""
        return {
            "intent": "unknown",
            "complexity": "simple",
            "required_capabilities": [],
            "parameters": {},
            "context_needed": [],
            "estimated_steps": 1
        }

    def _parse_analysis_response(self, response: str) -> Dict:
        """Parse LLM analysis response."""
        try:
            import json
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Failed to parse LLM analysis response")
            return self._basic_query_analysis("")
```

## 🔄 **Integration Points**

### **1. Existing AgentWrapper Integration**

```python
# Uses existing methods and patterns
if self.has_method('solve'):
    return self._delegate_to_agent_solve(query, context, **kwargs)

return self.execute(selection['method'], parameters)
```

### **2. Existing LLM Service Integration**

```python
# Uses existing CoreLLMService
from ..llm import CoreLLMService
self.llm_service = llm_service or CoreLLMService()

# Uses existing generate() method
response = self.llm_service.generate(prompt, return_json=True)
```

### **3. Existing Tool and Knowledge Integration**

```python
# Uses existing tool management
tools = self.agent_wrapper.get_assigned_tools()
knowledge = self.agent_wrapper.get_knowledge()

# Uses existing knowledge management
if self.agent_wrapper.is_knowledge_available():
    knowledge = self.agent_wrapper.get_knowledge()
```

## 🎯 **Error Handling**

### **1. solve() Method Error Handling**

```python
def solve(self, query: str, context: dict = None, **kwargs) -> Any:
    try:
        # Main solve logic
        pass
    except Exception as e:
        logger.error(f"Solve method failed: {e}")
        return self._handle_solve_error(e, query, context)
```

### **2. LLM Decision Engine Error Handling**

```python
def select_method(self, query: str, agent_metadata: dict) -> dict:
    try:
        # LLM method selection
        pass
    except Exception as e:
        logger.error(f"LLM method selection failed: {e}")
        return self._fallback_method_selection(query, agent_metadata)
```

## 📊 **Performance Considerations**

### **1. Caching Strategy**

```python
class LLMDecisionEngine:
    def __init__(self, llm_service: CoreLLMService = None):
        self.cache = {}  # Cache for method selections

    def select_method(self, query: str, agent_metadata: dict) -> dict:
        # Check cache first
        cache_key = f"{agent_metadata.get('agent_id', 'unknown')}:{hash(query)}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Generate and cache result
        result = self._generate_method_selection(query, agent_metadata)
        self.cache[cache_key] = result
        return result
```

### **2. Performance Monitoring**

```python
def solve(self, query: str, context: dict = None, **kwargs) -> Any:
    start_time = time.time()

    try:
        result = self._execute_solve_logic(query, context, **kwargs)
        execution_time = time.time() - start_time

        # Log performance metrics
        logger.info(f"Solve method completed in {execution_time:.2f}s")

        return result
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Solve method failed after {execution_time:.2f}s: {e}")
        raise
```

## 🔗 **Dependencies**

- **CoreLLMService**: For LLM operations
- **AgentWrapper**: Existing agent wrapper functionality
- **Tool Management**: Existing tool registry and management
- **Knowledge Management**: Existing knowledge injection and retrieval
- **Error Handling**: Existing error handling patterns
