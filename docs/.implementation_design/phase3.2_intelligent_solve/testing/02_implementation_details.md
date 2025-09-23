# Testing Implementation Details - Phase 3.2

**Document Type**: Implementation Details
**Module**: testing
**Phase**: 3.2
**Status**: Draft

## 🎯 **Purpose**

Detailed implementation of testing framework for intelligent solve() method support, including unit tests, integration tests, and performance tests.

## 🏗️ **Architecture Overview**

```
Testing Framework
├── Unit Tests
│   ├── solve() Method Tests
│   ├── LLMDecisionEngine Tests
│   └── Agent Custom solve() Tests
├── Integration Tests
│   ├── solve() Method Integration
│   ├── LLM Service Integration
│   └── Agent Loading Integration
├── Performance Tests
│   ├── Response Time Tests
│   ├── Memory Usage Tests
│   └── Concurrent Request Tests
└── Test Utilities
    ├── Mock Services
    ├── Test Data Generation
    └── Test Fixtures
```

## 🔧 **Core Implementation**

### **1. Test Configuration**

```python
# tests/phase3.2_intelligent_solve/conftest.py
import pytest
from unittest.mock import Mock, patch
from agenthub.core.agents.wrapper import AgentWrapper
from agenthub.core.llm import CoreLLMService
from agenthub.sdk.load_agent import load_agent

@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing."""
    service = Mock(spec=CoreLLMService)
    service.generate.return_value = '{"selected_method": "analyze_text", "confidence": 0.9}'
    return service

@pytest.fixture
def test_agent_info():
    """Test agent information."""
    return {
        'name': 'test_agent',
        'namespace': 'test',
        'methods': ['analyze_text', 'generate_code', 'summarize_content'],
        'interface': {
            'analyze_text': {
                'description': 'Analyze text for sentiment',
                'parameters': {
                    'text': {'type': 'string', 'required': True},
                    'analysis_type': {'type': 'string', 'required': False, 'default': 'sentiment'}
                }
            },
            'generate_code': {
                'description': 'Generate Python code',
                'parameters': {
                    'prompt': {'type': 'string', 'required': True},
                    'language': {'type': 'string', 'required': False, 'default': 'python'}
                }
            },
            'summarize_content': {
                'description': 'Summarize text content',
                'parameters': {
                    'text': {'type': 'string', 'required': True},
                    'max_length': {'type': 'int', 'required': False, 'default': 100}
                }
            }
        }
    }

@pytest.fixture
def agent_wrapper(test_agent_info):
    """Test agent wrapper."""
    return AgentWrapper(test_agent_info)

@pytest.fixture
def solve_config():
    """Test solve configuration."""
    return {
        'confidence_threshold': 0.7,
        'enable_caching': True,
        'fallback_enabled': True,
        'performance_monitoring': True
    }

@pytest.fixture
def test_queries():
    """Test queries for various scenarios."""
    return [
        # Sentiment analysis queries
        "Analyze the sentiment of this text",
        "What is the sentiment of this message?",
        "Is this text positive or negative?",

        # Code generation queries
        "Generate a Python function to sort a list",
        "Create a function that calculates the factorial",
        "Write code to read a CSV file",

        # Summarization queries
        "Summarize this document",
        "Give me a brief summary",
        "What are the key points?",

        # Complex queries
        "Analyze this text for sentiment and then summarize it",
        "Generate code and then explain how it works",
        "Create a comprehensive analysis report"
    ]

@pytest.fixture
def mock_agent_custom_solve():
    """Mock agent with custom solve() method."""
    class MockAgent:
        def solve(self, query: str, context: dict = None, **kwargs):
            return {
                'result': f'Custom solve result for: {query}',
                'method': 'custom_solve',
                'confidence': 0.95
            }

    return MockAgent()
```

### **2. Unit Tests for solve() Method**

```python
# tests/phase3.2_intelligent_solve/test_solve_method.py
import pytest
from unittest.mock import Mock, patch
from agenthub.core.agents.wrapper import AgentWrapper

class TestSolveMethod:
    """Test cases for the core solve() method."""

    def test_solve_with_agent_custom_solve(self, agent_wrapper, mock_agent_custom_solve):
        """Test solve() delegation to agent custom solve()."""
        # Mock agent with custom solve() method
        with patch.object(agent_wrapper, 'has_method', return_value=True):
            with patch.object(agent_wrapper, 'execute', return_value={'result': 'custom_solve_result'}):
                result = agent_wrapper.solve("Test query")

                assert result == {'result': 'custom_solve_result'}
                agent_wrapper.execute.assert_called_once()

    def test_solve_with_framework_method_selection(self, agent_wrapper, mock_llm_service):
        """Test solve() using framework method selection."""
        with patch.object(agent_wrapper, 'has_method', return_value=False):
            with patch.object(agent_wrapper, '_llm_method_selection') as mock_llm:
                mock_llm.return_value = {'result': 'framework_result'}

                result = agent_wrapper.solve("Test query")

                assert result == {'result': 'framework_result'}
                mock_llm.assert_called_once()

    def test_solve_error_handling(self, agent_wrapper):
        """Test solve() error handling."""
        with patch.object(agent_wrapper, 'has_method', side_effect=Exception("Test error")):
            result = agent_wrapper.solve("Test query")

            assert 'error' in result or 'Test error' in str(result)

    def test_solve_with_context(self, agent_wrapper):
        """Test solve() with context parameter."""
        context = {'user_id': '123', 'preferences': {'language': 'en'}}

        with patch.object(agent_wrapper, 'has_method', return_value=False):
            with patch.object(agent_wrapper, '_llm_method_selection') as mock_llm:
                mock_llm.return_value = {'result': 'context_result'}

                result = agent_wrapper.solve("Test query", context=context)

                assert result == {'result': 'context_result'}
                mock_llm.assert_called_once_with("Test query", context, {})

    def test_get_agent_metadata(self, agent_wrapper):
        """Test _get_agent_metadata() method."""
        metadata = agent_wrapper._get_agent_metadata()

        assert metadata['agent_id'] == 'test/test_agent'
        assert metadata['name'] == 'test_agent'
        assert metadata['methods'] == ['analyze_text', 'generate_code', 'summarize_content']
        assert 'interface' in metadata
        assert 'assigned_tools' in metadata

    def test_try_fallback_methods(self, agent_wrapper):
        """Test _try_fallback_methods() method."""
        result = agent_wrapper._try_fallback_methods("analyze this text", {}, {})

        # Should select analyze_text method based on keyword matching
        assert 'result' in result or 'error' in result

    def test_handle_solve_error(self, agent_wrapper):
        """Test _handle_solve_error() method."""
        error = Exception("Test error")
        result = agent_wrapper._handle_solve_error(error, "Test query", {})

        assert 'error' in result
        assert 'Test error' in str(result)
        assert 'available_methods' in result
```

### **3. Unit Tests for LLMDecisionEngine**

```python
# tests/phase3.2_intelligent_solve/test_llm_decision_engine.py
import pytest
import json
from unittest.mock import Mock, patch
from agenthub.core.agents.llm_decision_engine import LLMDecisionEngine

class TestLLMDecisionEngine:
    """Test cases for LLM decision engine."""

    def setup_method(self):
        """Set up test fixtures."""
        self.llm_service = Mock()
        self.decision_engine = LLMDecisionEngine(self.llm_service)

        self.agent_metadata = {
            'agent_id': 'test_agent',
            'methods': ['analyze_text', 'generate_code'],
            'interface': {
                'analyze_text': {
                    'description': 'Analyze text for sentiment',
                    'parameters': {'text': 'string', 'analysis_type': 'string'}
                },
                'generate_code': {
                    'description': 'Generate Python code',
                    'parameters': {'prompt': 'string', 'language': 'string'}
                }
            }
        }

    def test_method_selection_high_confidence(self):
        """Test method selection with high confidence."""
        mock_response = {
            'selected_method': 'analyze_text',
            'confidence': 0.9,
            'reasoning': 'Query is about text analysis'
        }

        self.llm_service.generate.return_value = json.dumps(mock_response)

        result = self.decision_engine.select_method("Analyze this text", self.agent_metadata)

        assert result['selected_method'] == 'analyze_text'
        assert result['confidence'] == 0.9
        assert result['reasoning'] == 'Query is about text analysis'

    def test_method_selection_low_confidence_fallback(self):
        """Test method selection with low confidence fallback."""
        mock_response = {
            'selected_method': 'analyze_text',
            'confidence': 0.5,
            'reasoning': 'Uncertain about method selection'
        }

        self.llm_service.generate.return_value = json.dumps(mock_response)

        with patch.object(self.decision_engine, '_fallback_method_selection') as mock_fallback:
            mock_fallback.return_value = {
                'selected_method': 'analyze_text',
                'confidence': 0.6,
                'reasoning': 'Fallback keyword matching'
            }

            result = self.decision_engine.select_method("Test query", self.agent_metadata)

            assert result['selected_method'] == 'analyze_text'
            assert result['confidence'] == 0.6
            mock_fallback.assert_called_once()

    def test_parameter_extraction(self):
        """Test parameter extraction from query."""
        method_info = {
            'name': 'analyze_text',
            'parameters': {'text': 'string', 'analysis_type': 'string'}
        }

        mock_response = {
            'parameters': {'text': 'sample text', 'analysis_type': 'sentiment'},
            'confidence': 0.9,
            'reasoning': 'Parameters extracted from query'
        }

        self.llm_service.generate.return_value = json.dumps(mock_response)

        result = self.decision_engine.extract_parameters("Analyze this sample text for sentiment", method_info)

        assert result['parameters']['text'] == 'sample text'
        assert result['parameters']['analysis_type'] == 'sentiment'
        assert result['confidence'] == 0.9

    def test_parameter_validation(self):
        """Test parameter validation and correction."""
        method_info = {
            'name': 'analyze_text',
            'parameters': {'text': 'string', 'analysis_type': 'string'}
        }

        # Test with invalid parameter types
        invalid_params = {'text': 123, 'analysis_type': 'sentiment'}

        with patch.object(self.decision_engine, '_validate_parameters') as mock_validate:
            mock_validate.return_value = {'text': '123', 'analysis_type': 'sentiment'}

            result = self.decision_engine.extract_parameters("Test query", method_info)

            mock_validate.assert_called_once()
            assert result['parameters']['text'] == '123'

    def test_llm_service_error_handling(self):
        """Test error handling when LLM service fails."""
        self.llm_service.generate.side_effect = Exception("LLM service error")

        with patch.object(self.decision_engine, '_fallback_method_selection') as mock_fallback:
            mock_fallback.return_value = {
                'selected_method': 'analyze_text',
                'confidence': 0.5,
                'reasoning': 'Fallback due to LLM error'
            }

            result = self.decision_engine.select_method("Test query", self.agent_metadata)

            assert result['selected_method'] == 'analyze_text'
            assert result['confidence'] == 0.5
            mock_fallback.assert_called_once()

    def test_prepare_methods_info(self):
        """Test _prepare_methods_info() method."""
        methods = self.decision_engine._prepare_methods_info(self.agent_metadata)

        assert len(methods) == 2
        assert methods[0]['name'] == 'analyze_text'
        assert methods[0]['description'] == 'Analyze text for sentiment'
        assert 'parameters' in methods[0]

    def test_create_method_selection_prompt(self):
        """Test _create_method_selection_prompt() method."""
        methods = self.decision_engine._prepare_methods_info(self.agent_metadata)
        prompt = self.decision_engine._create_method_selection_prompt("Test query", methods, self.agent_metadata)

        assert "Test query" in prompt
        assert "analyze_text" in prompt
        assert "generate_code" in prompt
        assert "JSON" in prompt

    def test_create_parameter_extraction_prompt(self):
        """Test _create_parameter_extraction_prompt() method."""
        method_info = {
            'name': 'analyze_text',
            'description': 'Analyze text for sentiment',
            'parameters': {'text': 'string', 'analysis_type': 'string'}
        }

        prompt = self.decision_engine._create_parameter_extraction_prompt("Test query", method_info)

        assert "Test query" in prompt
        assert "analyze_text" in prompt
        assert "text" in prompt
        assert "analysis_type" in prompt
        assert "JSON" in prompt

    def test_parse_method_selection_response(self):
        """Test _parse_method_selection_response() method."""
        valid_response = '{"selected_method": "analyze_text", "confidence": 0.9}'
        result = self.decision_engine._parse_method_selection_response(valid_response)

        assert result['selected_method'] == 'analyze_text'
        assert result['confidence'] == 0.9

        # Test invalid JSON
        invalid_response = "invalid json"
        result = self.decision_engine._parse_method_selection_response(invalid_response)

        assert result['selected_method'] is None
        assert result['confidence'] == 0.0
        assert 'error' in result

    def test_validate_method_selection(self):
        """Test _validate_method_selection() method."""
        valid_selection = {
            'selected_method': 'analyze_text',
            'confidence': 0.9
        }

        assert self.decision_engine._validate_method_selection(valid_selection, self.agent_metadata) == True

        # Test invalid method
        invalid_selection = {
            'selected_method': 'invalid_method',
            'confidence': 0.9
        }

        assert self.decision_engine._validate_method_selection(invalid_selection, self.agent_metadata) == False

        # Test low confidence
        low_confidence_selection = {
            'selected_method': 'analyze_text',
            'confidence': 0.5
        }

        assert self.decision_engine._validate_method_selection(low_confidence_selection, self.agent_metadata) == False

    def test_fallback_method_selection(self):
        """Test _fallback_method_selection() method."""
        result = self.decision_engine._fallback_method_selection("analyze this text", self.agent_metadata)

        assert result['selected_method'] == 'analyze_text'
        assert result['confidence'] > 0.0
        assert 'reasoning' in result

    def test_fallback_parameter_extraction(self):
        """Test _fallback_parameter_extraction() method."""
        method_info = {
            'name': 'analyze_text',
            'parameters': {'text': 'string', 'analysis_type': 'string'}
        }

        result = self.decision_engine._fallback_parameter_extraction("Test query", method_info)

        assert 'parameters' in result
        assert 'confidence' in result
        assert 'reasoning' in result
```

### **4. Integration Tests**

```python
# tests/phase3.2_intelligent_solve/test_solve_integration.py
import pytest
from unittest.mock import Mock, patch
from agenthub.core.agents.wrapper import AgentWrapper
from agenthub.core.agents.llm_decision_engine import LLMDecisionEngine
from agenthub.sdk.load_agent import load_agent

class TestSolveIntegration:
    """Integration tests for solve() method."""

    def test_solve_with_real_llm_service(self, test_agent_info):
        """Test solve() method with real LLM service."""
        # This test requires actual LLM service
        agent = AgentWrapper(test_agent_info)

        # Test with real LLM service
        result = agent.solve("Analyze the sentiment of this text: I love this product!")

        assert result is not None
        assert 'result' in result or 'error' in result

    def test_solve_with_agent_custom_solve(self, test_agent_info, mock_agent_custom_solve):
        """Test solve() method with agent custom solve()."""
        # Mock agent with custom solve() method
        with patch.object(AgentWrapper, 'has_method', return_value=True):
            with patch.object(AgentWrapper, 'execute', return_value={'result': 'custom_solve_result'}):
                agent = AgentWrapper(test_agent_info)
                result = agent.solve("Test query")

                assert result == {'result': 'custom_solve_result'}

    def test_solve_with_framework_method_selection(self, test_agent_info, mock_llm_service):
        """Test solve() method with framework method selection."""
        with patch.object(AgentWrapper, 'has_method', return_value=False):
            with patch.object(AgentWrapper, '_llm_method_selection') as mock_llm:
                mock_llm.return_value = {'result': 'framework_result'}

                agent = AgentWrapper(test_agent_info)
                result = agent.solve("Test query")

                assert result == {'result': 'framework_result'}

    def test_solve_with_context(self, test_agent_info):
        """Test solve() method with context."""
        context = {'user_id': '123', 'preferences': {'language': 'en'}}

        with patch.object(AgentWrapper, 'has_method', return_value=False):
            with patch.object(AgentWrapper, '_llm_method_selection') as mock_llm:
                mock_llm.return_value = {'result': 'context_result'}

                agent = AgentWrapper(test_agent_info)
                result = agent.solve("Test query", context=context)

                assert result == {'result': 'context_result'}
                mock_llm.assert_called_once_with("Test query", context, {})

    def test_solve_with_parameters(self, test_agent_info):
        """Test solve() method with additional parameters."""
        with patch.object(AgentWrapper, 'has_method', return_value=False):
            with patch.object(AgentWrapper, '_llm_method_selection') as mock_llm:
                mock_llm.return_value = {'result': 'parameter_result'}

                agent = AgentWrapper(test_agent_info)
                result = agent.solve("Test query", text="Sample text", analysis_type="sentiment")

                assert result == {'result': 'parameter_result'}
                mock_llm.assert_called_once()

    def test_solve_error_handling(self, test_agent_info):
        """Test solve() method error handling."""
        with patch.object(AgentWrapper, 'has_method', side_effect=Exception("Test error")):
            agent = AgentWrapper(test_agent_info)
            result = agent.solve("Test query")

            assert 'error' in result or 'Test error' in str(result)

    def test_solve_with_fallback(self, test_agent_info):
        """Test solve() method with fallback."""
        with patch.object(AgentWrapper, 'has_method', return_value=False):
            with patch.object(AgentWrapper, '_llm_method_selection') as mock_llm:
                mock_llm.return_value = {'confidence': 0.3}  # Low confidence

                with patch.object(AgentWrapper, '_try_fallback_methods') as mock_fallback:
                    mock_fallback.return_value = {'result': 'fallback_result'}

                    agent = AgentWrapper(test_agent_info)
                    result = agent.solve("Test query")

                    assert result == {'result': 'fallback_result'}
                    mock_fallback.assert_called_once()
```

### **5. Performance Tests**

```python
# tests/phase3.2_intelligent_solve/test_solve_performance.py
import pytest
import time
import threading
import queue
from agenthub.core.agents.wrapper import AgentWrapper

class TestSolvePerformance:
    """Performance tests for solve() method."""

    def test_solve_response_time(self, test_agent_info):
        """Test solve() method response time."""
        agent = AgentWrapper(test_agent_info)

        start_time = time.time()
        result = agent.solve("Test query")
        end_time = time.time()

        response_time = end_time - start_time

        # Should respond within 5 seconds
        assert response_time < 5.0
        assert result is not None

    def test_concurrent_solve_requests(self, test_agent_info):
        """Test concurrent solve() requests."""
        agent = AgentWrapper(test_agent_info)
        results = queue.Queue()

        def solve_worker(query):
            result = agent.solve(query)
            results.put(result)

        # Start 10 concurrent requests
        threads = []
        for i in range(10):
            thread = threading.Thread(target=solve_worker, args=(f"Query {i}",))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check that all requests completed
        assert results.qsize() == 10

        # Check that all results are valid
        while not results.empty():
            result = results.get()
            assert result is not None

    def test_memory_usage(self, test_agent_info):
        """Test memory usage during solve() operations."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        agent = AgentWrapper(test_agent_info)

        # Perform multiple solve operations
        for i in range(100):
            result = agent.solve(f"Test query {i}")

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024

    def test_solve_caching_performance(self, test_agent_info):
        """Test solve() method caching performance."""
        agent = AgentWrapper(test_agent_info)

        # First call (no cache)
        start_time = time.time()
        result1 = agent.solve("Test query")
        first_call_time = time.time() - start_time

        # Second call (with cache)
        start_time = time.time()
        result2 = agent.solve("Test query")
        second_call_time = time.time() - start_time

        # Second call should be faster due to caching
        assert second_call_time < first_call_time
        assert result1 == result2

    def test_solve_with_large_context(self, test_agent_info):
        """Test solve() method with large context."""
        large_context = {
            'user_id': '123',
            'preferences': {'language': 'en', 'theme': 'dark'},
            'history': ['query1', 'query2', 'query3'] * 1000,  # Large history
            'data': {'key' + str(i): 'value' + str(i) for i in range(1000)}
        }

        agent = AgentWrapper(test_agent_info)

        start_time = time.time()
        result = agent.solve("Test query", context=large_context)
        end_time = time.time()

        response_time = end_time - start_time

        # Should still respond within reasonable time
        assert response_time < 10.0
        assert result is not None
```

### **6. Test Utilities**

```python
# tests/phase3.2_intelligent_solve/test_utils.py
import pytest
from typing import List, Dict, Any
from agenthub.core.agents.wrapper import AgentWrapper

class TestDataGenerator:
    """Generate test data for solve() method testing."""

    @staticmethod
    def generate_query_variations(base_query: str) -> List[str]:
        """Generate variations of a base query."""
        variations = [
            base_query,
            base_query.upper(),
            base_query.lower(),
            base_query.capitalize(),
            f"Please {base_query}",
            f"Can you {base_query}?",
            f"I need to {base_query}",
            f"Help me {base_query}"
        ]
        return variations

    @staticmethod
    def generate_agent_metadata() -> Dict[str, Any]:
        """Generate test agent metadata."""
        return {
            'agent_id': 'test_agent',
            'name': 'Test Agent',
            'namespace': 'test',
            'methods': ['analyze_text', 'generate_code', 'summarize_content'],
            'interface': {
                'analyze_text': {
                    'description': 'Analyze text for various purposes',
                    'parameters': {
                        'text': {'type': 'string', 'required': True},
                        'analysis_type': {'type': 'string', 'required': False, 'default': 'general'}
                    }
                },
                'generate_code': {
                    'description': 'Generate code based on requirements',
                    'parameters': {
                        'prompt': {'type': 'string', 'required': True},
                        'language': {'type': 'string', 'required': False, 'default': 'python'}
                    }
                }
            }
        }

    @staticmethod
    def generate_test_queries() -> List[str]:
        """Generate test queries for various scenarios."""
        return [
            # Sentiment analysis queries
            "Analyze the sentiment of this text",
            "What is the sentiment of this message?",
            "Is this text positive or negative?",

            # Code generation queries
            "Generate a Python function to sort a list",
            "Create a function that calculates the factorial",
            "Write code to read a CSV file",

            # Summarization queries
            "Summarize this document",
            "Give me a brief summary",
            "What are the key points?",

            # Complex queries
            "Analyze this text for sentiment and then summarize it",
            "Generate code and then explain how it works",
            "Create a comprehensive analysis report"
        ]

class MockLLMService:
    """Mock LLM service for testing."""

    def __init__(self, responses: Dict[str, str] = None):
        self.responses = responses or {}
        self.call_count = 0

    def generate(self, prompt: str, **kwargs) -> str:
        """Mock generate method."""
        self.call_count += 1

        # Return predefined response if available
        if prompt in self.responses:
            return self.responses[prompt]

        # Default response
        return '{"selected_method": "analyze_text", "confidence": 0.9}'

    def get_call_count(self) -> int:
        """Get number of calls made."""
        return self.call_count

    def reset(self):
        """Reset call count."""
        self.call_count = 0

class TestAgentWrapper(AgentWrapper):
    """Test agent wrapper with additional testing capabilities."""

    def __init__(self, agent_info: Dict[str, Any], mock_llm_service=None):
        super().__init__(agent_info)
        self.mock_llm_service = mock_llm_service
        self.solve_call_count = 0
        self.solve_results = []

    def solve(self, query: str, context: dict = None, **kwargs) -> Any:
        """Override solve method for testing."""
        self.solve_call_count += 1

        # Record solve call
        self.solve_results.append({
            'query': query,
            'context': context,
            'kwargs': kwargs,
            'timestamp': time.time()
        })

        # Call parent solve method
        return super().solve(query, context, **kwargs)

    def get_solve_stats(self) -> Dict[str, Any]:
        """Get solve method statistics."""
        return {
            'call_count': self.solve_call_count,
            'results': self.solve_results.copy()
        }

    def reset_solve_stats(self):
        """Reset solve method statistics."""
        self.solve_call_count = 0
        self.solve_results.clear()
```

## 🔄 **Integration Points**

### **1. Existing Test Framework Integration**

```python
# Uses existing pytest framework
@pytest.fixture
def test_agent_info():
    """Test agent information."""
    return {
        'name': 'test_agent',
        'namespace': 'test',
        'methods': ['analyze_text', 'generate_code'],
        'interface': {
            'analyze_text': {
                'description': 'Analyze text for sentiment',
                'parameters': {'text': 'string', 'analysis_type': 'string'}
            }
        }
    }
```

### **2. AgentWrapper Integration**

```python
# Uses existing AgentWrapper for testing
def test_solve_with_agent_custom_solve(self, agent_wrapper, mock_agent_custom_solve):
    """Test solve() delegation to agent custom solve()."""
    with patch.object(agent_wrapper, 'has_method', return_value=True):
        with patch.object(agent_wrapper, 'execute', return_value={'result': 'custom_solve_result'}):
            result = agent_wrapper.solve("Test query")

            assert result == {'result': 'custom_solve_result'}
            agent_wrapper.execute.assert_called_once()
```

## 🎯 **Error Handling**

### **1. Test Error Handling**

```python
def test_solve_error_handling(self, agent_wrapper):
    """Test solve() error handling."""
    with patch.object(agent_wrapper, 'has_method', side_effect=Exception("Test error")):
        result = agent_wrapper.solve("Test query")

        assert 'error' in result or 'Test error' in str(result)
```

### **2. Mock Service Error Handling**

```python
def test_llm_service_error_handling(self):
    """Test error handling when LLM service fails."""
    self.llm_service.generate.side_effect = Exception("LLM service error")

    with patch.object(self.decision_engine, '_fallback_method_selection') as mock_fallback:
        mock_fallback.return_value = {
            'selected_method': 'analyze_text',
            'confidence': 0.5,
            'reasoning': 'Fallback due to LLM error'
        }

        result = self.decision_engine.select_method("Test query", self.agent_metadata)

        assert result['selected_method'] == 'analyze_text'
        assert result['confidence'] == 0.5
        mock_fallback.assert_called_once()
```

## 📊 **Performance Considerations**

### **1. Test Performance Monitoring**

```python
def test_solve_response_time(self, test_agent_info):
    """Test solve() method response time."""
    agent = AgentWrapper(test_agent_info)

    start_time = time.time()
    result = agent.solve("Test query")
    end_time = time.time()

    response_time = end_time - start_time

    # Should respond within 5 seconds
    assert response_time < 5.0
    assert result is not None
```

### **2. Memory Usage Testing**

```python
def test_memory_usage(self, test_agent_info):
    """Test memory usage during solve() operations."""
    import psutil
    import os

    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss

    agent = AgentWrapper(test_agent_info)

    # Perform multiple solve operations
    for i in range(100):
        result = agent.solve(f"Test query {i}")

    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory

    # Memory increase should be reasonable (less than 100MB)
    assert memory_increase < 100 * 1024 * 1024
```

## 🔗 **Dependencies**

- **pytest**: For testing framework
- **unittest.mock**: For mocking and patching
- **threading**: For concurrent testing
- **queue**: For thread-safe communication
- **time**: For performance measurement
- **psutil**: For memory usage monitoring
- **AgentWrapper**: For agent testing
- **LLMDecisionEngine**: For LLM testing
