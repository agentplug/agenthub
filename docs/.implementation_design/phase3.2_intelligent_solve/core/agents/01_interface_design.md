# Core/Agents Interface Design - Phase 3.2

**Document Type**: Interface Design
**Module**: core/agents
**Phase**: 3.2
**Status**: Draft

## 🎯 **Purpose**

Define the public interfaces for intelligent solve() method, LLM decision engine, and agent custom solve() support.

## 🔧 **Core Interfaces**

### **1. solve() Method Interface**

```python
from agenthub.core.agents import AgentWrapper
from typing import Any, Dict, Optional

# Enhanced AgentWrapper with solve() method
class AgentWrapper:
    def solve(self, query: str, context: Dict = None, **kwargs) -> Any:
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
        pass
```

**Parameters**:
- `query`: Natural language description of the problem
- `context`: Additional context for decision making
- `**kwargs`: Additional parameters to pass to selected method

**Returns**: Result from the best matching method or agent custom solve

### **2. LLMDecisionEngine Interface**

```python
from agenthub.core.agents import LLMDecisionEngine
from typing import Dict, List, Any

# LLM decision engine for method selection
class LLMDecisionEngine:
    def __init__(self, llm_service=None):
        """Initialize LLM decision engine with existing CoreLLMService."""
        pass

    def select_method(self, query: str, agent_metadata: Dict) -> Dict:
        """
        Select best method using LLM analysis.

        Args:
            query: Natural language query
            agent_metadata: Agent metadata including methods and interface

        Returns:
            Dictionary with selected method, confidence, and reasoning
        """
        pass

    def extract_parameters(self, query: str, method_info: Dict) -> Dict:
        """
        Extract parameters from natural language query.

        Args:
            query: Natural language query
            method_info: Method information including parameters

        Returns:
            Dictionary with extracted parameters and confidence
        """
        pass
```

### **3. Agent Custom solve() Interface**

```python
from agenthub.core.agents import AgentSolveInterface
from typing import Any, Dict, Optional

# Base interface for agent custom solve() methods
class AgentSolveInterface:
    def solve(self, query: str, context: Dict = None, **kwargs) -> Any:
        """
        Agent-specific solve method with LLM decision making.

        Integrates with existing AgentHub patterns:
        - Uses existing CoreLLMService for LLM operations
        - Leverages existing tool and knowledge management
        - Follows current error handling patterns

        Args:
            query: Natural language description of the problem
            context: Additional context from framework
            **kwargs: Additional parameters

        Returns:
            Solution to the problem
        """
        pass
```

### **4. Method Selection Response Interface**

```python
from typing import Dict, List, Any

MethodSelectionResponse = {
    "selected_method": str,           # Name of selected method
    "confidence": float,              # Confidence score (0.0 to 1.0)
    "reasoning": str,                 # Explanation of selection
    "alternative_methods": List[str], # Alternative method suggestions
    "method_info": Dict[str, Any]     # Method information for execution
}

ParameterExtractionResponse = {
    "parameters": Dict[str, Any],     # Extracted parameters
    "confidence": float,              # Confidence score (0.0 to 1.0)
    "reasoning": str,                 # Explanation of extraction
    "missing_parameters": List[str],  # Parameters that couldn't be extracted
    "extracted_values": Dict[str, str] # How each parameter was extracted
}
```

## 🔄 **Integration Points**

### **1. Existing AgentWrapper Integration**

```python
# Uses existing methods
if self.has_method('solve'):
    return self._delegate_to_agent_solve(query, context, **kwargs)

# Uses existing execute() method
return self.execute(selection['method'], parameters)
```

### **2. Existing LLM Service Integration**

```python
# Uses existing CoreLLMService
from ..llm import CoreLLMService
self.llm_service = llm_service or CoreLLMService()

# Uses existing generate() method
response = self.llm_service.generate(
    prompt,
    system_prompt="...",
    return_json=True
)
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

## 🎯 **Error Handling Interface**

### **1. solve() Method Error Handling**

```python
def solve(self, query: str, context: Dict = None, **kwargs) -> Any:
    try:
        # Main solve logic
        pass
    except Exception as e:
        logger.error(f"Solve method failed: {e}")
        return self._handle_solve_error(e, query, context)

def _handle_solve_error(self, error: Exception, query: str, context: Dict) -> Any:
    """Handle solve() method errors with helpful messages."""
    pass
```

### **2. LLM Decision Engine Error Handling**

```python
def select_method(self, query: str, agent_metadata: Dict) -> Dict:
    try:
        # LLM method selection
        pass
    except Exception as e:
        logger.error(f"LLM method selection failed: {e}")
        return self._fallback_method_selection(query, agent_metadata)

def _fallback_method_selection(self, query: str, agent_metadata: Dict) -> Dict:
    """Fallback method selection when LLM fails."""
    pass
```

## 📊 **Performance Interface**

### **1. Caching Interface**

```python
class LLMDecisionEngine:
    def __init__(self, llm_service=None):
        self.cache = {}  # Cache for method selections

    def _get_cached_selection(self, query: str, agent_id: str) -> Optional[Dict]:
        """Get cached method selection."""
        pass

    def _cache_selection(self, query: str, agent_id: str, selection: Dict):
        """Cache method selection result."""
        pass
```

### **2. Performance Monitoring Interface**

```python
class SolvePerformanceMonitor:
    def track_solve_request(self, query: str, response_time: float, success: bool):
        """Track solve() method performance."""
        pass

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for solve() method."""
        pass
```

## 🔧 **Configuration Interface**

### **1. solve() Method Configuration**

```python
class SolveConfig:
    def __init__(self):
        self.confidence_threshold = 0.7
        self.max_retries = 3
        self.enable_caching = True
        self.enable_analytics = True
        self.fallback_strategy = "confidence_based"
```

### **2. LLM Decision Engine Configuration**

```python
class LLMDecisionConfig:
    def __init__(self):
        self.model = "gpt-4"
        self.temperature = 0.1
        self.max_tokens = 500
        self.timeout = 30
        self.retry_count = 3
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
def validate_performance(self, test_queries: List[str]) -> Dict[str, float]:
    """Validate solve() method performance."""
    pass
```

## 🔗 **Dependencies**

- **CoreLLMService**: For LLM operations
- **AgentWrapper**: Existing agent wrapper functionality
- **Tool Management**: Existing tool registry and management
- **Knowledge Management**: Existing knowledge injection and retrieval
- **Error Handling**: Existing error handling patterns
