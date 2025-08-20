"""
End-to-End Tests for Custom Method Injection System

This module tests the complete workflow from method injection to execution
through the AgentWrapper and integration with the core agent system.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

import agentmanager as amg
from agentmanager.core.agent_wrapper import AgentWrapper, AgentExecutionError
from agentmanager.core.custom_method_manager import CustomMethodManager
from agentmanager.core.exceptions import MethodValidationError, MethodNotFoundError, MethodInjectionError


class TestCustomMethodInjectionE2E:
    """End-to-end tests for the complete custom method injection workflow."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_agent_info(self):
        """Create mock agent information."""
        return {
            "name": "test-agent",
            "namespace": "test",
            "agent_name": "test-agent", 
            "path": "/test/path",
            "version": "1.0.0",
            "description": "Test agent for e2e testing",
            "methods": ["existing_method", "generate_code"],
            "dependencies": [],
            "manifest": {
                "interface": {
                    "methods": {
                        "existing_method": {
                            "description": "Existing built-in method",
                            "parameters": {"input": {"type": "string"}}
                        },
                        "generate_code": {
                            "description": "Generate code",
                            "parameters": {"prompt": {"type": "string"}}
                        }
                    }
                }
            }
        }
    
    @pytest.fixture
    def sample_text_analyzer(self):
        """Sample Python function for text analysis."""
        def analyze_sentiment(text: str) -> dict:
            """Analyze sentiment of input text."""
            if not text:
                return {"error": "Empty text"}
            
            positive_words = ["good", "great", "excellent", "amazing", "love"]
            negative_words = ["bad", "terrible", "awful", "hate", "horrible"]
            
            text_lower = text.lower()
            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)
            
            if positive_count > negative_count:
                sentiment = "positive"
                score = min(1.0, positive_count / 5.0)
            elif negative_count > positive_count:
                sentiment = "negative" 
                score = max(-1.0, -negative_count / 5.0)
            else:
                sentiment = "neutral"
                score = 0.0
                
            return {
                "sentiment": sentiment,
                "score": score,
                "positive_indicators": positive_count,
                "negative_indicators": negative_count,
                "analyzed_text": text[:50] + "..." if len(text) > 50 else text
            }
        
        return analyze_sentiment
    
    @pytest.fixture
    def sample_data_processor(self):
        """Sample function for data processing."""
        def process_data(data: list, operation: str = "sum") -> dict:
            """Process numerical data with various operations."""
            if not data:
                return {"error": "Empty data"}
            
            try:
                numeric_data = [float(x) for x in data]
            except (ValueError, TypeError):
                return {"error": "Non-numeric data provided"}
            
            if operation == "sum":
                result = sum(numeric_data)
            elif operation == "avg" or operation == "average":
                result = sum(numeric_data) / len(numeric_data)
            elif operation == "max":
                result = max(numeric_data)
            elif operation == "min":
                result = min(numeric_data)
            elif operation == "count":
                result = len(numeric_data)
            else:
                return {"error": f"Unknown operation: {operation}"}
            
            return {
                "operation": operation,
                "result": result,
                "data_points": len(numeric_data),
                "original_data": data
            }
        
        return process_data

    def test_complete_injection_and_execution_workflow(self, mock_agent_info, sample_text_analyzer, temp_dir):
        """Test the complete workflow from injection to execution."""
        # Create custom method manager
        manager = CustomMethodManager(base_path=temp_dir, security_level="medium")
        
        # Create agent wrapper
        wrapper = AgentWrapper(mock_agent_info, custom_method_manager=manager)
        
        # Step 1: Verify agent has built-in methods
        assert wrapper.has_method("existing_method")
        assert wrapper.has_method("generate_code")
        assert not wrapper.has_method("analyze_sentiment")
        
        # Step 2: Inject custom method
        result = wrapper.inject_custom_method("analyze_sentiment", sample_text_analyzer, "python")
        assert result["success"] is True
        assert result["method_name"] == "analyze_sentiment"
        
        # Step 3: Verify method is now available
        assert wrapper.has_method("analyze_sentiment")
        assert wrapper.is_custom_method("analyze_sentiment")
        assert not wrapper.is_custom_method("existing_method")
        
        # Step 4: Execute custom method directly
        test_text = "This is a great and amazing product that I love!"
        result = wrapper.analyze_sentiment(test_text)
        
        assert result["sentiment"] == "positive"
        assert result["score"] > 0
        assert result["positive_indicators"] >= 2
        assert "analyzed_text" in result
        
        # Step 5: Test with negative sentiment
        negative_text = "This is terrible and awful, I hate it!"
        result = wrapper.analyze_sentiment(negative_text)
        
        assert result["sentiment"] == "negative"
        assert result["score"] < 0
        assert result["negative_indicators"] >= 2
        
        # Step 6: List all methods (built-in + custom)
        all_methods = wrapper.methods
        assert "existing_method" in all_methods
        assert "generate_code" in all_methods
        # Note: Custom methods might not be in the main methods list
        # but should be accessible via has_method and direct calls
        
        # Step 7: List custom methods specifically
        custom_methods = wrapper.list_custom_methods()
        assert len(custom_methods) == 1
        assert custom_methods[0]["name"] == "analyze_sentiment"
        assert custom_methods[0]["language"] == "python"
        
        # Step 8: Get custom method info
        method_info = wrapper.get_method_info("analyze_sentiment")
        assert method_info is not None
        assert "description" in method_info
        
        # Step 9: Remove custom method
        wrapper.remove_custom_method("analyze_sentiment")
        assert not wrapper.has_method("analyze_sentiment")
        assert not wrapper.is_custom_method("analyze_sentiment")
        
        # Step 10: Verify method is no longer callable
        with pytest.raises(AttributeError):
            wrapper.analyze_sentiment("test")

    def test_multiple_custom_methods_workflow(self, mock_agent_info, sample_text_analyzer, sample_data_processor, temp_dir):
        """Test workflow with multiple custom methods."""
        manager = CustomMethodManager(base_path=temp_dir, security_level="medium")
        wrapper = AgentWrapper(mock_agent_info, custom_method_manager=manager)
        
        # Inject multiple methods
        wrapper.inject_custom_method("analyze_sentiment", sample_text_analyzer, "python")
        wrapper.inject_custom_method("process_data", sample_data_processor, "python")
        
        # Verify both methods are available
        assert wrapper.has_method("analyze_sentiment")
        assert wrapper.has_method("process_data")
        assert wrapper.is_custom_method("analyze_sentiment")
        assert wrapper.is_custom_method("process_data")
        
        # Test sentiment analysis
        sentiment_result = wrapper.analyze_sentiment("This is great!")
        assert sentiment_result["sentiment"] == "positive"
        
        # Test data processing
        data_result = wrapper.process_data([1, 2, 3, 4, 5], "avg")
        assert data_result["result"] == 3.0
        assert data_result["operation"] == "avg"
        
        # Test chaining methods (using output of one as input to another)
        data_summary = wrapper.process_data([1, 2, 3, 4, 5], "sum")
        analysis_text = f"The sum is {data_summary['result']}, which is excellent!"
        sentiment = wrapper.analyze_sentiment(analysis_text)
        
        assert sentiment["sentiment"] == "positive"
        
        # List all custom methods
        custom_methods = wrapper.list_custom_methods()
        assert len(custom_methods) == 2
        method_names = [m["name"] for m in custom_methods]
        assert "analyze_sentiment" in method_names
        assert "process_data" in method_names

    def test_string_based_method_injection(self, mock_agent_info, temp_dir):
        """Test injection of string-based Python code."""
        manager = CustomMethodManager(base_path=temp_dir, security_level="medium")
        wrapper = AgentWrapper(mock_agent_info, custom_method_manager=manager)
        
        # Define method as string
        string_method = """
def calculate_fibonacci(n: int) -> dict:
    \"\"\"Calculate Fibonacci sequence up to n terms.\"\"\"
    if n <= 0:
        return {"error": "n must be positive"}
    
    sequence = []
    a, b = 0, 1
    
    for _ in range(n):
        sequence.append(a)
        a, b = b, a + b
    
    return {
        "sequence": sequence,
        "count": len(sequence),
        "last_value": sequence[-1] if sequence else 0
    }
"""
        
        # Inject string method
        result = wrapper.inject_custom_method("calculate_fibonacci", string_method, "python")
        assert result["success"] is True
        
        # Execute string method
        fib_result = wrapper.calculate_fibonacci(8)
        assert fib_result["count"] == 8
        assert fib_result["sequence"] == [0, 1, 1, 2, 3, 5, 8, 13]
        assert fib_result["last_value"] == 13

    def test_security_validation_e2e(self, mock_agent_info, temp_dir):
        """Test end-to-end security validation."""
        manager = CustomMethodManager(base_path=temp_dir, security_level="high")
        wrapper = AgentWrapper(mock_agent_info, custom_method_manager=manager)
        
        # Test dangerous code injection
        dangerous_code = """
def dangerous_method():
    import os
    exec('print("This is dangerous!")')
    return "executed"
"""
        
        with pytest.raises(MethodInjectionError, match="Method validation failed"):
            wrapper.inject_custom_method("dangerous_method", dangerous_code, "python")
        
        # Test safe code passes
        safe_code = """
def safe_method(x: int) -> int:
    return x * 2
"""
        
        result = wrapper.inject_custom_method("safe_method", safe_code, "python")
        assert result["success"] is True
        
        # Execute safe method
        assert wrapper.safe_method(5) == 10

    def test_method_persistence_and_reload(self, mock_agent_info, temp_dir):
        """Test that methods persist and can be reloaded."""
        # Use string-based method to test persistence (since callable functions aren't persisted)
        sentiment_method = '''
def analyze_sentiment(text: str) -> dict:
    """Analyze sentiment of input text."""
    if not text:
        return {"error": "Empty text"}
    
    positive_words = ["good", "great", "excellent", "amazing", "love"]
    negative_words = ["bad", "terrible", "awful", "hate", "horrible"]
    
    text_lower = text.lower()
    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)
    
    if positive_count > negative_count:
        sentiment = "positive"
        score = min(1.0, positive_count / 5.0)
    elif negative_count > positive_count:
        sentiment = "negative" 
        score = max(-1.0, -negative_count / 5.0)
    else:
        sentiment = "neutral"
        score = 0.0
        
    return {
        "sentiment": sentiment,
        "score": score,
        "positive_indicators": positive_count,
        "negative_indicators": negative_count,
        "analyzed_text": text[:50] + "..." if len(text) > 50 else text
    }
'''
        
        # Create first manager and inject method
        manager1 = CustomMethodManager(base_path=temp_dir, security_level="medium")
        wrapper1 = AgentWrapper(mock_agent_info, custom_method_manager=manager1)
        
        wrapper1.inject_custom_method("analyze_sentiment", sentiment_method, "python")
        result1 = wrapper1.analyze_sentiment("Great product!")
        assert result1["sentiment"] == "positive"
        
        # Create second manager pointing to same storage
        manager2 = CustomMethodManager(base_path=temp_dir, security_level="medium")
        wrapper2 = AgentWrapper(mock_agent_info, custom_method_manager=manager2)
        
        # Method should be available in second instance
        assert wrapper2.has_method("analyze_sentiment")
        result2 = wrapper2.analyze_sentiment("Great product!")
        assert result2["sentiment"] == "positive"
        assert result1 == result2

    def test_method_error_handling_e2e(self, mock_agent_info, temp_dir):
        """Test error handling in end-to-end scenarios."""
        manager = CustomMethodManager(base_path=temp_dir, security_level="medium")
        wrapper = AgentWrapper(mock_agent_info, custom_method_manager=manager)
        
        # Test error in method execution
        error_method = """
def error_method(x):
    if x == "error":
        raise ValueError("Intentional error")
    return f"Success: {x}"
"""
        
        wrapper.inject_custom_method("error_method", error_method, "python")
        
        # Test successful execution
        result = wrapper.error_method("test")
        assert "Success: test" == result
        
        # Test error handling (wrapped in AgentExecutionError)
        with pytest.raises(AgentExecutionError, match="Intentional error"):
            wrapper.error_method("error")

    def test_custom_method_context_and_metadata(self, mock_agent_info, sample_text_analyzer, temp_dir):
        """Test custom method context and metadata functionality."""
        manager = CustomMethodManager(base_path=temp_dir, security_level="medium")
        wrapper = AgentWrapper(mock_agent_info, custom_method_manager=manager)
        
        # Inject method
        wrapper.inject_custom_method("analyze_sentiment", sample_text_analyzer, "python")
        
        # Get custom method context
        context = wrapper.get_custom_method_context()
        assert "methods" in context
        assert "total_methods" in context
        assert context["total_methods"] == 1
        assert "analyze_sentiment" in context["methods"]
        
        method_context = context["methods"]["analyze_sentiment"]
        assert method_context["language"] == "python"
        assert "injected_at" in method_context
        assert "metadata" in method_context

    def test_agent_manager_integration(self, temp_dir):
        """Test integration with the agent manager loading system."""
        # This test would require actual agent loading, which we'll simulate
        
        # Mock the agent loading process
        mock_agent_info = {
            "name": "coding-agent",
            "namespace": "agentplug", 
            "agent_name": "coding-agent",
            "path": "/mock/path",
            "version": "1.0.0",
            "description": "Mock coding agent",
            "methods": ["generate_code", "explain_code"],
            "dependencies": [],
            "manifest": {
                "interface": {
                    "methods": {
                        "generate_code": {
                            "description": "Generate code from prompt",
                            "parameters": {"prompt": {"type": "string"}}
                        }
                    }
                }
            }
        }
        
        # Simulate agentmanager.load_agent() functionality
        manager = CustomMethodManager(base_path=temp_dir, security_level="medium")
        agent = AgentWrapper(mock_agent_info, custom_method_manager=manager)
        
        # Test that we can inject methods into a "loaded" agent
        def custom_validator(code: str) -> dict:
            """Validate code quality."""
            lines = code.split('\n')
            return {
                "line_count": len(lines),
                "has_functions": "def " in code,
                "has_classes": "class " in code,
                "estimated_complexity": min(10, len(lines) / 5)
            }
        
        agent.inject_custom_method("validate_code", custom_validator, "python")
        
        # Test the injected method
        test_code = """
def hello_world():
    print("Hello, World!")
    return "Hello"

class Greeter:
    def greet(self, name):
        return f"Hello, {name}!"
"""
        
        validation_result = agent.validate_code(test_code)
        assert validation_result["line_count"] > 5
        assert validation_result["has_functions"] is True
        assert validation_result["has_classes"] is True
        assert validation_result["estimated_complexity"] > 0

    def test_performance_with_multiple_methods(self, mock_agent_info, temp_dir):
        """Test performance with multiple method injections and executions."""
        import time
        
        manager = CustomMethodManager(base_path=temp_dir, security_level="low")  # Lower security for speed
        wrapper = AgentWrapper(mock_agent_info, custom_method_manager=manager)
        
        # Inject multiple methods
        methods_to_inject = []
        for i in range(5):
            method_code = f"""
def method_{i}(x):
    return x * {i + 1} + {i}
"""
            methods_to_inject.append((f"method_{i}", method_code))
        
        # Time the injection process
        start_time = time.time()
        for method_name, method_code in methods_to_inject:
            wrapper.inject_custom_method(method_name, method_code, "python")
        injection_time = time.time() - start_time
        
        # Verify all methods are available
        for i in range(5):
            assert wrapper.has_method(f"method_{i}")
        
        # Time the execution process
        start_time = time.time()
        results = []
        for i in range(5):
            result = getattr(wrapper, f"method_{i}")(10)
            results.append(result)
        execution_time = time.time() - start_time
        
        # Verify results
        expected_results = [10, 21, 32, 43, 54]  # Based on formula x * (i+1) + i with x=10
        assert results == expected_results
        
        # Performance assertions (these are loose bounds for testing)
        assert injection_time < 2.0  # Should inject 5 methods in under 2 seconds
        assert execution_time < 1.0   # Should execute 5 methods in under 1 second
        
        print(f"Performance metrics - Injection: {injection_time:.3f}s, Execution: {execution_time:.3f}s")


class TestCustomMethodCLIIntegration:
    """Test CLI integration for custom method management."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_cli_method_injection_simulation(self, temp_dir):
        """Simulate CLI method injection workflow."""
        # This simulates what the CLI would do
        manager = CustomMethodManager(base_path=temp_dir, security_level="medium")
        
        # Simulate reading method from file (like CLI would)
        method_content = """
def text_summarizer(text: str, max_length: int = 100) -> str:
    '''Summarize text to maximum length.'''
    if len(text) <= max_length:
        return text
    
    sentences = text.split('. ')
    summary = ""
    for sentence in sentences:
        if len(summary + sentence) <= max_length - 3:
            summary += sentence + ". "
        else:
            break
    
    if not summary:
        summary = text[:max_length-3] + "..."
    
    return summary.strip()
"""
        
        # Inject method (simulating CLI command)
        agent_path = "test/agent"
        method_name = "text_summarizer"
        
        manager.inject_method(agent_path, method_name, method_content, "python")
        
        # Verify injection worked
        assert manager.validate_method_exists(agent_path, method_name)
        
        # Test execution
        method = manager.get_method(agent_path, method_name)
        long_text = "This is a very long text that needs to be summarized. " * 10
        summary = method(long_text, 50)
        
        assert len(summary) <= 50
        assert "This is a very long text" in summary


class TestCustomMethodRealWorldScenarios:
    """Test real-world scenarios and use cases."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_coding_agent(self):
        """Mock a coding agent."""
        return {
            "name": "coding-agent",
            "namespace": "agentplug",
            "agent_name": "coding-agent",
            "path": "/agents/coding-agent",
            "version": "1.2.0",
            "description": "AI coding assistant",
            "methods": ["generate_code", "explain_code", "refactor_code"],
            "dependencies": [],
            "manifest": {
                "interface": {
                    "methods": {
                        "generate_code": {
                            "description": "Generate code from natural language",
                            "parameters": {"prompt": {"type": "string"}}
                        },
                        "explain_code": {
                            "description": "Explain what code does",
                            "parameters": {"code": {"type": "string"}}
                        }
                    }
                }
            }
        }
    
    def test_code_quality_extension_scenario(self, mock_coding_agent, temp_dir):
        """Test scenario: Adding code quality analysis to a coding agent."""
        manager = CustomMethodManager(base_path=temp_dir, security_level="medium")
        agent = AgentWrapper(mock_coding_agent, custom_method_manager=manager)
        
        # Add code quality analysis method
        quality_analyzer = """
def analyze_code_quality(code: str) -> dict:
    '''Analyze code quality metrics.'''
    lines = [line.strip() for line in code.split('\\n') if line.strip()]
    
    # Basic metrics
    total_lines = len(lines)
    comment_lines = len([line for line in lines if line.startswith('#')])
    function_count = len([line for line in lines if line.strip().startswith('def ')])
    class_count = len([line for line in lines if line.strip().startswith('class ')])
    
    # Calculate metrics
    comment_ratio = comment_lines / total_lines if total_lines > 0 else 0
    avg_line_length = sum(len(line) for line in lines) / total_lines if total_lines > 0 else 0
    
    # Quality score (0-100)
    quality_score = 100
    if comment_ratio < 0.1:
        quality_score -= 20
    if avg_line_length > 100:
        quality_score -= 15
    if function_count == 0 and total_lines > 5:
        quality_score -= 25
    
    return {
        "total_lines": total_lines,
        "comment_lines": comment_lines,
        "comment_ratio": round(comment_ratio, 2),
        "function_count": function_count,
        "class_count": class_count,
        "avg_line_length": round(avg_line_length, 1),
        "quality_score": max(0, quality_score),
        "recommendations": _get_quality_recommendations(comment_ratio, avg_line_length, function_count)
    }

def _get_quality_recommendations(comment_ratio, avg_line_length, function_count):
    recommendations = []
    if comment_ratio < 0.1:
        recommendations.append("Add more comments to improve readability")
    if avg_line_length > 100:
        recommendations.append("Consider breaking long lines for better readability")
    if function_count == 0:
        recommendations.append("Consider organizing code into functions")
    return recommendations
"""
        
        # Inject the quality analyzer
        agent.inject_custom_method("analyze_code_quality", quality_analyzer, "python")
        
        # Test with sample code
        sample_code = """
# This is a sample Python function
def calculate_area(radius):
    pi = 3.14159
    return pi * radius * radius

class Circle:
    def __init__(self, radius):
        self.radius = radius
    
    def area(self):
        return calculate_area(self.radius)
"""
        
        quality_result = agent.analyze_code_quality(sample_code)
        
        assert quality_result["total_lines"] > 0
        assert quality_result["comment_lines"] >= 1
        assert quality_result["function_count"] >= 1
        assert quality_result["class_count"] >= 1
        assert quality_result["quality_score"] > 50
        assert isinstance(quality_result["recommendations"], list)

    def test_a_b_testing_scenario(self, mock_coding_agent, temp_dir):
        """Test scenario: A/B testing different algorithm implementations."""
        manager = CustomMethodManager(base_path=temp_dir, security_level="medium")
        agent = AgentWrapper(mock_coding_agent, custom_method_manager=manager)
        
        # Algorithm A: Simple sorting
        algorithm_a = """
def sort_algorithm_a(data: list) -> dict:
    '''Simple bubble sort implementation.'''
    import time
    start_time = time.time()
    
    arr = data.copy()
    n = len(arr)
    
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    
    end_time = time.time()
    
    return {
        "algorithm": "bubble_sort",
        "sorted_data": arr,
        "original_data": data,
        "execution_time": end_time - start_time,
        "comparisons": n * (n - 1) // 2
    }
"""
        
        # Algorithm B: Built-in sorting
        algorithm_b = """
def sort_algorithm_b(data: list) -> dict:
    '''Built-in sort implementation.'''
    import time
    start_time = time.time()
    
    arr = data.copy()
    arr.sort()
    
    end_time = time.time()
    
    return {
        "algorithm": "builtin_sort",
        "sorted_data": arr,
        "original_data": data,
        "execution_time": end_time - start_time,
        "comparisons": "optimized"
    }
"""
        
        # Test Algorithm A
        agent.inject_custom_method("sort_test", algorithm_a, "python")
        test_data = [64, 34, 25, 12, 22, 11, 90]
        result_a = agent.sort_test(test_data)
        
        # Switch to Algorithm B
        agent.remove_custom_method("sort_test")
        agent.inject_custom_method("sort_test", algorithm_b, "python")
        result_b = agent.sort_test(test_data)
        
        # Compare results
        assert result_a["sorted_data"] == result_b["sorted_data"]  # Same result
        assert result_a["algorithm"] != result_b["algorithm"]      # Different algorithms
        # Note: For small datasets, timing differences may be negligible
        assert result_b["execution_time"] <= result_a["execution_time"]  # B should be faster or equal

    def test_user_customization_scenario(self, mock_coding_agent, temp_dir):
        """Test scenario: User-specific customizations."""
        # Create separate storage for each user
        user1_dir = Path(temp_dir) / "user1"
        user2_dir = Path(temp_dir) / "user2"
        user1_dir.mkdir()
        user2_dir.mkdir()
        
        manager1 = CustomMethodManager(base_path=str(user1_dir), security_level="medium")
        manager2 = CustomMethodManager(base_path=str(user2_dir), security_level="medium")
        
        # User 1: Prefers verbose logging
        agent_user1 = AgentWrapper(mock_coding_agent, custom_method_manager=manager1)
        
        verbose_logger = """
def custom_log(message: str, level: str = "INFO") -> dict:
    '''Verbose logging with timestamp and details.'''
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] [{level.upper()}] {message}"
    
    return {
        "formatted_message": formatted_message,
        "timestamp": timestamp,
        "level": level.upper(),
        "original_message": message,
        "user_preference": "verbose"
    }
"""
        
        agent_user1.inject_custom_method("log_message", verbose_logger, "python")
        
        # User 2: Prefers minimal logging (different agent instance)
        agent_user2 = AgentWrapper(mock_coding_agent, custom_method_manager=manager2)
        
        minimal_logger = """
def custom_log(message: str, level: str = "INFO") -> dict:
    '''Minimal logging.'''
    return {
        "formatted_message": f"{level[0].upper()}: {message}",
        "level": level.upper(),
        "original_message": message,
        "user_preference": "minimal"
    }
"""
        
        agent_user2.inject_custom_method("log_message", minimal_logger, "python")
        
        # Test both customizations
        test_message = "Testing custom logging"
        
        result1 = agent_user1.log_message(test_message, "DEBUG")
        result2 = agent_user2.log_message(test_message, "DEBUG")
        
        assert result1["user_preference"] == "verbose"
        assert result2["user_preference"] == "minimal"
        assert len(result1["formatted_message"]) > len(result2["formatted_message"])
        assert "timestamp" in result1
        assert "timestamp" not in result2


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
