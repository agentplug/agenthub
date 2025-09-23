# Core/LLM Interface Design - Phase 3.2

**Document Type**: Interface Design
**Module**: core/llm
**Phase**: 3.2
**Status**: Draft

## 🎯 **Purpose**

Define the public interfaces for LLM integration in the intelligent solve() method, including method selection and parameter extraction.

## 🔧 **Core Interfaces**

### **1. SolveLLMService Interface**

```python
from agenthub.core.llm import SolveLLMService
from typing import Dict, List, Any, Optional

# Specialized LLM service for solve() method operations
class SolveLLMService:
    def __init__(self, llm_service=None):
        """
        Initialize SolveLLMService with existing CoreLLMService.

        Args:
            llm_service: Existing CoreLLMService instance or None
        """
        pass

    def generate_method_selection(self, query: str, methods: List[Dict]) -> Dict:
        """
        Generate method selection using LLM analysis.

        Args:
            query: Natural language query
            methods: List of available methods with metadata

        Returns:
            Dictionary with selected method, confidence, and reasoning
        """
        pass

    def generate_parameter_extraction(self, query: str, method_info: Dict) -> Dict:
        """
        Generate parameter extraction using LLM analysis.

        Args:
            query: Natural language query
            method_info: Method information including parameters

        Returns:
            Dictionary with extracted parameters and confidence
        """
        pass
```

### **2. Method Selection Prompt Interface**

```python
from agenthub.core.llm import MethodSelectionPrompt
from typing import Dict, List

# Method selection prompt templates
class MethodSelectionPrompt:
    def create_prompt(self, query: str, methods: List[Dict], agent_info: Dict) -> str:
        """
        Create method selection prompt.

        Args:
            query: Natural language query
            methods: List of available methods
            agent_info: Agent information and context

        Returns:
            Formatted prompt for LLM
        """
        pass

    def parse_response(self, response: str) -> Dict:
        """
        Parse LLM response for method selection.

        Args:
            response: Raw LLM response

        Returns:
            Parsed method selection result
        """
        pass
```

### **3. Parameter Extraction Prompt Interface**

```python
from agenthub.core.llm import ParameterExtractionPrompt
from typing import Dict, List

# Parameter extraction prompt templates
class ParameterExtractionPrompt:
    def create_prompt(self, query: str, method_info: Dict) -> str:
        """
        Create parameter extraction prompt.

        Args:
            query: Natural language query
            method_info: Method information including parameters

        Returns:
            Formatted prompt for LLM
        """
        pass

    def parse_response(self, response: str) -> Dict:
        """
        Parse LLM response for parameter extraction.

        Args:
            response: Raw LLM response

        Returns:
            Parsed parameter extraction result
        """
        pass
```

### **4. LLM Error Handling Interface**

```python
from agenthub.core.llm import LLMErrorHandler
from typing import Dict, Any

# LLM error handling and fallback mechanisms
class LLMErrorHandler:
    def handle_llm_error(self, error: Exception, query: str, context: Dict) -> Dict:
        """
        Handle LLM errors with appropriate fallbacks.

        Args:
            error: Exception that occurred
            query: Original query
            context: Additional context

        Returns:
            Fallback response or error information
        """
        pass

    def handle_rate_limit_error(self, error: Exception, query: str) -> Dict:
        """Handle rate limit errors."""
        pass

    def handle_timeout_error(self, error: Exception, query: str) -> Dict:
        """Handle timeout errors."""
        pass

    def handle_invalid_response_error(self, error: Exception, query: str) -> Dict:
        """Handle invalid response errors."""
        pass
```

## 🔄 **Integration Points**

### **1. Existing CoreLLMService Integration**

```python
# Uses existing CoreLLMService
from ..llm import CoreLLMService

class SolveLLMService:
    def __init__(self, llm_service: CoreLLMService = None):
        self.llm_service = llm_service or CoreLLMService()

    def generate_method_selection(self, query: str, methods: List[Dict]) -> Dict:
        # Uses existing generate() method
        response = self.llm_service.generate(
            prompt,
            system_prompt="You are an AI assistant that selects the best method for solving user queries.",
            return_json=True
        )
```

### **2. Existing Error Handling Integration**

```python
# Uses existing error handling patterns
try:
    response = self.llm_service.generate(prompt, return_json=True)
except Exception as e:
    logger.error(f"LLM generation failed: {e}")
    return self._fallback_response()
```

### **3. Existing Caching Integration**

```python
# Uses existing caching patterns
def generate_method_selection(self, query: str, methods: List[Dict]) -> Dict:
    # Check cache first
    cache_key = f"method_selection:{hash(query)}"
    if cache_key in self.cache:
        return self.cache[cache_key]

    # Generate response
    response = self.llm_service.generate(prompt, return_json=True)

    # Cache result
    self.cache[cache_key] = response
    return response
```

## 🎯 **Prompt Template Interface**

### **1. Method Selection Prompt Template**

```python
METHOD_SELECTION_PROMPT = """
You are an AI assistant that selects the best method for solving user queries.

Agent Information:
- Name: {agent_name}
- Description: {agent_description}
- Available Methods: {methods_list}

User Query: "{query}"

Task: Select the most appropriate method and provide confidence score.

Available Methods:
{methods_details}

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
```

### **2. Parameter Extraction Prompt Template**

```python
PARAMETER_EXTRACTION_PROMPT = """
You are an AI assistant that extracts parameters from natural language queries.

Method: {method_name}
Method Description: {method_description}
Method Parameters: {method_parameters}

User Query: "{query}"

Task: Extract and map parameters from the query to the method parameters.

Parameter Requirements:
{parameter_details}

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
```

## 📊 **Performance Interface**

### **1. LLM Performance Monitoring**

```python
class LLMPerformanceMonitor:
    def track_llm_request(self, operation: str, response_time: float, success: bool):
        """Track LLM request performance."""
        pass

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get LLM performance metrics."""
        pass

    def get_accuracy_metrics(self) -> Dict[str, float]:
        """Get LLM accuracy metrics."""
        pass
```

### **2. Caching Interface**

```python
class LLMCache:
    def get_cached_response(self, cache_key: str) -> Optional[Dict]:
        """Get cached LLM response."""
        pass

    def cache_response(self, cache_key: str, response: Dict, ttl: int = 3600):
        """Cache LLM response."""
        pass

    def clear_cache(self):
        """Clear LLM cache."""
        pass
```

## 🔧 **Configuration Interface**

### **1. SolveLLMService Configuration**

```python
class SolveLLMConfig:
    def __init__(self):
        self.model = "gpt-4"
        self.temperature = 0.1
        self.max_tokens = 500
        self.timeout = 30
        self.retry_count = 3
        self.enable_caching = True
        self.cache_ttl = 3600
        self.confidence_threshold = 0.7
```

### **2. Prompt Configuration**

```python
class PromptConfig:
    def __init__(self):
        self.method_selection_prompt = METHOD_SELECTION_PROMPT
        self.parameter_extraction_prompt = PARAMETER_EXTRACTION_PROMPT
        self.system_prompts = {
            "method_selection": "You are an AI assistant that selects the best method for solving user queries.",
            "parameter_extraction": "You are an AI assistant that extracts parameters from natural language queries."
        }
```

## 🎯 **Success Criteria Interface**

### **1. Method Selection Accuracy**

```python
def validate_method_selection_accuracy(self, test_cases: List[Dict]) -> Dict[str, float]:
    """Validate method selection accuracy against test cases."""
    pass
```

### **2. Parameter Extraction Accuracy**

```python
def validate_parameter_extraction_accuracy(self, test_cases: List[Dict]) -> Dict[str, float]:
    """Validate parameter extraction accuracy against test cases."""
    pass
```

### **3. Performance Validation**

```python
def validate_llm_performance(self, test_queries: List[str]) -> Dict[str, float]:
    """Validate LLM service performance."""
    pass
```

## 🔗 **Dependencies**

- **CoreLLMService**: Existing LLM service for base functionality
- **aisuite**: LLM provider integration
- **Error Handling**: Existing error handling patterns
- **Caching**: Existing caching mechanisms
- **Logging**: Existing logging infrastructure
