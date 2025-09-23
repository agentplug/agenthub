# Core/Agents Testing Strategy - Phase 3.2

**Document Type**: Testing Strategy
**Module**: core/agents
**Phase**: 3.2
**Status**: Draft

## 🎯 **Purpose**

Comprehensive testing strategy for enhanced AgentWrapper with solve() method, LLMDecisionEngine, and agent custom solve() support.

## 🧪 **Testing Overview**

### **Test Categories**
- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **LLM Tests**: LLM service integration testing
- **Agent Tests**: Agent custom solve() testing
- **Performance Tests**: Performance and scalability testing

### **Test Coverage Targets**
- **Unit Test Coverage**: >90%
- **Integration Test Coverage**: >80%
- **LLM Test Coverage**: >85%
- **Agent Test Coverage**: >80%

## 🔧 **Unit Testing**

### **1. solve() Method Tests**

```python
# tests/phase3.2_intelligent_solve/test_solve_method.py
import pytest
from unittest.mock import Mock, patch
from agenthub.core.agents.wrapper import AgentWrapper

class TestSolveMethod:
    """Test cases for the core solve() method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.agent_info = {
            'name': 'test_agent',
            'namespace': 'test',
            'methods': ['analyze_text', 'generate_code', 'summarize_content'],
            'interface': {
                'analyze_text': {
                    'description': 'Analyze text for various purposes',
                    'parameters': {'text': 'string', 'analysis_type': 'string'}
                },
                'generate_code': {
                    'description': 'Generate code based on requirements',
                    'parameters': {'prompt': 'string', 'language': 'string'}
                }
            }
        }
        self.agent_wrapper = AgentWrapper(self.agent_info)

    def test_solve_with_agent_custom_solve(self):
        """Test solve() delegation to agent custom solve()."""
        # Mock agent with custom solve() method
        with patch.object(self.agent_wrapper, 'has_method', return_value=True):
            with patch.object(self.agent_wrapper, 'execute', return_value={'result': 'custom_solve_result'}):
                result = self.agent_wrapper.solve("Test query")

                assert result == {'result': 'custom_solve_result'}
                self.agent_wrapper.execute.assert_called_once()

    def test_solve_with_framework_method_selection(self):
        """Test solve() using framework method selection."""
        with patch.object(self.agent_wrapper, 'has_method', return_value=False):
            with patch.object(self.agent_wrapper, '_llm_method_selection') as mock_llm:
                mock_llm.return_value = {'result': 'framework_result'}

                result = self.agent_wrapper.solve("Test query")

                assert result == {'result': 'framework_result'}
                mock_llm.assert_called_once()

    def test_solve_error_handling(self):
        """Test solve() error handling."""
        with patch.object(self.agent_wrapper, 'has_method', side_effect=Exception("Test error")):
            result = self.agent_wrapper.solve("Test query")

            assert 'error' in result or 'Test error' in str(result)

    def test_solve_with_context(self):
        """Test solve() with context parameter."""
        context = {'user_id': '123', 'preferences': {'language': 'en'}}

        with patch.object(self.agent_wrapper, 'has_method', return_value=False):
            with patch.object(self.agent_wrapper, '_llm_method_selection') as mock_llm:
                mock_llm.return_value = {'result': 'context_result'}

                result = self.agent_wrapper.solve("Test query", context=context)

                assert result == {'result': 'context_result'}
                mock_llm.assert_called_once_with("Test query", context, {})

    def test_get_agent_metadata(self):
        """Test _get_agent_metadata() method."""
        metadata = self.agent_wrapper._get_agent_metadata()

        assert metadata['agent_id'] == 'test/test_agent'
        assert metadata['name'] == 'test_agent'
        assert metadata['methods'] == ['analyze_text', 'generate_code', 'summarize_content']
        assert 'interface' in metadata
        assert 'assigned_tools' in metadata

    def test_try_fallback_methods(self):
        """Test _try_fallback_methods() method."""
        result = self.agent_wrapper._try_fallback_methods("analyze this text", {}, {})

        # Should select analyze_text method based on keyword matching
        assert 'result' in result or 'error' in result

    def test_handle_solve_error(self):
        """Test _handle_solve_error() method."""
        error = Exception("Test error")
        result = self.agent_wrapper._handle_solve_error(error, "Test query", {})

        assert 'error' in result
        assert 'Test error' in str(result)
        assert 'available_methods' in result
```

### **2. LLMDecisionEngine Tests**

```python
# tests/phase3.2_intelligent_solve/test_llm_decision_engine.py
import pytest
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

### **3. Agent Custom solve() Tests**

```python
# tests/phase3.2_intelligent_solve/test_agent_custom_solve.py
import pytest
from unittest.mock import Mock, patch
from agenthub.core.agents.agent_solve_interface import AgentSolveInterface

class TestAgentCustomSolve:
    """Test cases for agent custom solve() methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.agent_wrapper = Mock()
        self.agent = AgentSolveInterface(self.agent_wrapper)

    def test_analyze_query_with_llm(self):
        """Test query analysis using LLM service."""
        mock_llm_response = {
            'intent': 'analyze text',
            'complexity': 'moderate',
            'required_capabilities': ['text_analysis'],
            'parameters': {'text': 'sample text'},
            'context_needed': ['user_preferences'],
            'estimated_steps': 2
        }

        with patch.object(self.agent, 'llm_service') as mock_llm:
            mock_llm.generate.return_value = json.dumps(mock_llm_response)

            result = self.agent._analyze_query("Analyze this sample text")

            assert result['intent'] == 'analyze text'
            assert result['complexity'] == 'moderate'
            assert result['estimated_steps'] == 2

    def test_analyze_query_fallback(self):
        """Test query analysis fallback when LLM fails."""
        with patch.object(self.agent, 'llm_service') as mock_llm:
            mock_llm.generate.side_effect = Exception("LLM error")

            result = self.agent._analyze_query("Test query")

            assert result['intent'] == 'unknown'
            assert result['complexity'] == 'simple'
            assert result['estimated_steps'] == 1

    def test_basic_query_analysis(self):
        """Test basic query analysis without LLM."""
        result = self.agent._basic_query_analysis("Test query")

        assert result['intent'] == 'unknown'
        assert result['complexity'] == 'simple'
        assert result['required_capabilities'] == []
        assert result['parameters'] == {}
        assert result['context_needed'] == []
        assert result['estimated_steps'] == 1

    def test_parse_analysis_response(self):
        """Test parsing of LLM analysis response."""
        valid_response = '{"intent": "analyze text", "complexity": "moderate"}'
        result = self.agent._parse_analysis_response(valid_response)

        assert result['intent'] == 'analyze text'
        assert result['complexity'] == 'moderate'

        # Test invalid JSON
        invalid_response = "invalid json"
        result = self.agent._parse_analysis_response(invalid_response)

        assert result['intent'] == 'unknown'
        assert result['complexity'] == 'simple'
```

## 🔗 **Integration Testing**

### **1. solve() Method Integration Tests**

```python
# tests/phase3.2_intelligent_solve/test_solve_integration.py
import pytest
from agenthub.core.agents.wrapper import AgentWrapper
from agenthub.core.agents.llm_decision_engine import LLMDecisionEngine

class TestSolveIntegration:
    """Integration tests for solve() method."""

    def test_solve_with_real_llm_service(self):
        """Test solve() method with real LLM service."""
        # This test requires actual LLM service
        agent_info = {
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

        agent = AgentWrapper(agent_info)

        # Test with real LLM service
        result = agent.solve("Analyze the sentiment of this text: I love this product!")

        assert result is not None
        assert 'result' in result or 'error' in result

    def test_solve_with_agent_custom_solve(self):
        """Test solve() method with agent custom solve()."""
        # Mock agent with custom solve() method
        class MockAgent:
            def solve(self, query: str, context: dict = None, **kwargs):
                return {'result': f'Custom solve result for: {query}'}

        # This would require actual agent implementation
        # For now, test the delegation logic
        pass
```

### **2. LLM Service Integration Tests**

```python
# tests/phase3.2_intelligent_solve/test_llm_integration.py
import pytest
from agenthub.core.llm import CoreLLMService
from agenthub.core.agents.llm_decision_engine import LLMDecisionEngine

class TestLLMIntegration:
    """Integration tests for LLM service."""

    def test_method_selection_with_real_llm(self):
        """Test method selection with real LLM service."""
        llm_service = CoreLLMService()
        decision_engine = LLMDecisionEngine(llm_service)

        agent_metadata = {
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

        result = decision_engine.select_method("Analyze this text", agent_metadata)

        assert 'selected_method' in result
        assert 'confidence' in result
        assert result['confidence'] > 0.0

    def test_parameter_extraction_with_real_llm(self):
        """Test parameter extraction with real LLM service."""
        llm_service = CoreLLMService()
        decision_engine = LLMDecisionEngine(llm_service)

        method_info = {
            'name': 'analyze_text',
            'description': 'Analyze text for sentiment',
            'parameters': {'text': 'string', 'analysis_type': 'string'}
        }

        result = decision_engine.extract_parameters("Analyze this text for sentiment", method_info)

        assert 'parameters' in result
        assert 'confidence' in result
        assert 'text' in result['parameters']
        assert 'analysis_type' in result['parameters']
```

## 📊 **Performance Testing**

### **1. solve() Method Performance Tests**

```python
# tests/phase3.2_intelligent_solve/test_solve_performance.py
import pytest
import time
from agenthub.core.agents.wrapper import AgentWrapper

class TestSolvePerformance:
    """Performance tests for solve() method."""

    def test_solve_response_time(self):
        """Test solve() method response time."""
        agent_info = self._create_test_agent_info()
        agent = AgentWrapper(agent_info)

        start_time = time.time()
        result = agent.solve("Test query")
        end_time = time.time()

        response_time = end_time - start_time

        # Should respond within 5 seconds
        assert response_time < 5.0
        assert result is not None

    def test_concurrent_solve_requests(self):
        """Test concurrent solve() requests."""
        import threading
        import queue

        agent_info = self._create_test_agent_info()
        agent = AgentWrapper(agent_info)

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

    def test_memory_usage(self):
        """Test memory usage during solve() operations."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        agent_info = self._create_test_agent_info()
        agent = AgentWrapper(agent_info)

        # Perform multiple solve operations
        for i in range(100):
            result = agent.solve(f"Test query {i}")

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024

    def _create_test_agent_info(self):
        """Create test agent info."""
        return {
            'name': 'test_agent',
            'namespace': 'test',
            'methods': ['analyze_text', 'generate_code'],
            'interface': {
                'analyze_text': {
                    'description': 'Analyze text',
                    'parameters': {'text': 'string'}
                }
            }
        }
```

## 🎯 **Test Data and Fixtures**

### **1. Test Data Generation**

```python
# tests/phase3.2_intelligent_solve/test_data.py
class TestDataGenerator:
    """Generate test data for solve() method testing."""

    @staticmethod
    def generate_query_variations(base_query: str) -> list:
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
    def generate_agent_metadata() -> dict:
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
    def generate_test_queries() -> list:
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
```

### **2. Test Configuration**

```python
# tests/phase3.2_intelligent_solve/conftest.py
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing."""
    service = Mock()
    service.generate.return_value = '{"selected_method": "analyze_text", "confidence": 0.9}'
    return service

@pytest.fixture
def test_agent_info():
    """Test agent information."""
    return {
        'name': 'test_agent',
        'namespace': 'test',
        'methods': ['analyze_text', 'generate_code'],
        'interface': {
            'analyze_text': {
                'description': 'Analyze text',
                'parameters': {'text': 'string'}
            }
        }
    }

@pytest.fixture
def agent_wrapper(test_agent_info):
    """Test agent wrapper."""
    from agenthub.core.agents.wrapper import AgentWrapper
    return AgentWrapper(test_agent_info)
```

## 🎯 **Success Criteria**

### **1. Test Coverage**
- [ ] Unit test coverage >90%
- [ ] Integration test coverage >80%
- [ ] LLM test coverage >85%
- [ ] Agent test coverage >80%

### **2. Performance Benchmarks**
- [ ] Average response time <2 seconds
- [ ] 95th percentile response time <5 seconds
- [ ] Memory usage <100MB per request
- [ ] Concurrent request handling (10+ requests)

### **3. Accuracy Metrics**
- [ ] Method selection accuracy >85%
- [ ] Parameter extraction accuracy >80%
- [ ] Error handling success rate >95%

### **4. Reliability**
- [ ] Test suite runs in <10 minutes
- [ ] All tests pass consistently
- [ ] No flaky tests
- [ ] Comprehensive error scenarios covered
