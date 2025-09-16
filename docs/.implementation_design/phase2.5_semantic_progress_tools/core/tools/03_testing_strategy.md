# Core/Tools Testing Strategy - Phase 2.5

**Document Type**: Testing Strategy
**Module**: core/tools
**Phase**: 2.5
**Status**: Draft

## 🎯 **Purpose**

Comprehensive testing strategy for tool registry, decorator, metadata management, and FastMCP integration.

## 🧪 **Testing Overview**

### **Test Categories**
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: FastMCP integration testing
3. **Concurrency Tests**: Thread safety and concurrent access
4. **Error Handling Tests**: Exception and error scenarios
5. **Performance Tests**: Tool registration and execution performance

## 🔧 **Unit Tests**

### **1. Tool Registry Tests**

```python
# tests/core/tools/test_registry.py
import pytest
from agenthub.core.tools import ToolRegistry, ToolMetadata

class TestToolRegistry:
    def test_singleton_pattern(self):
        """Test that ToolRegistry is a singleton"""
        registry1 = ToolRegistry()
        registry2 = ToolRegistry()
        assert registry1 is registry2

    def test_tool_registration(self):
        """Test tool registration"""
        registry = ToolRegistry()

        def test_tool(data: str) -> dict:
            return {"result": data}

        registry.register_tool("test_tool", test_tool, "Test tool")

        assert "test_tool" in registry.get_available_tools()
        assert registry.get_tool_metadata("test_tool") is not None

    def test_tool_name_conflict(self):
        """Test tool name conflict handling"""
        registry = ToolRegistry()

        def tool1(data: str) -> dict:
            return {"result": data}

        def tool2(data: str) -> dict:
            return {"result": data}

        registry.register_tool("test_tool", tool1, "Test tool 1")

        with pytest.raises(ToolNameConflictError):
            registry.register_tool("test_tool", tool2, "Test tool 2")

    def test_tool_validation(self):
        """Test tool validation"""
        registry = ToolRegistry()

        # Test non-callable tool
        with pytest.raises(ToolValidationError):
            registry.register_tool("test_tool", "not_callable", "Test tool")

        # Test empty function
        def empty_tool():
            pass

        with pytest.raises(ToolValidationError):
            registry.register_tool("test_tool", empty_tool, "Test tool")
```

### **2. Tool Decorator Tests**

```python
# tests/core/tools/test_decorator.py
import pytest
from agenthub.core.tools import tool, get_available_tools

class TestToolDecorator:
    def test_tool_decorator_basic(self):
        """Test basic tool decorator functionality"""
        @tool(name="test_tool", description="Test tool")
        def test_function(data: str) -> dict:
            return {"result": data}

        assert "test_tool" in get_available_tools()
        assert test_function("test") == {"result": "test"}

    def test_tool_decorator_without_description(self):
        """Test tool decorator without description"""
        @tool(name="test_tool2")
        def test_function2(data: str) -> dict:
            return {"result": data}

        assert "test_tool2" in get_available_tools()

    def test_tool_decorator_metadata(self):
        """Test tool decorator creates correct metadata"""
        @tool(name="metadata_tool", description="Metadata test tool")
        def metadata_function(data: str) -> dict:
            return {"result": data}

        from agenthub.core.tools import get_tool_metadata
        metadata = get_tool_metadata("metadata_tool")

        assert metadata.name == "metadata_tool"
        assert metadata.description == "Metadata test tool"
        assert metadata.function == metadata_function
        assert metadata.namespace == "custom"
```

### **3. Tool Validation Tests**

```python
# tests/core/tools/test_validator.py
import pytest
from agenthub.core.tools.validator import ToolValidator
from agenthub.core.tools.exceptions import ToolValidationError, ToolNameConflictError

class TestToolValidator:
    def test_validate_tool_name(self):
        """Test tool name validation"""
        existing_tools = ["existing_tool"]

        # Valid names
        assert ToolValidator.validate_tool_name("valid_tool", existing_tools) == True
        assert ToolValidator.validate_tool_name("another_tool", existing_tools) == True

        # Invalid names
        with pytest.raises(ToolValidationError):
            ToolValidator.validate_tool_name("", existing_tools)

        with pytest.raises(ToolValidationError):
            ToolValidator.validate_tool_name(None, existing_tools)

        with pytest.raises(ToolNameConflictError):
            ToolValidator.validate_tool_name("existing_tool", existing_tools)

    def test_validate_tool_function(self):
        """Test tool function validation"""
        def valid_tool(data: str) -> dict:
            return {"result": data}

        def invalid_tool():
            pass

        assert ToolValidator.validate_tool_function(valid_tool) == True

        with pytest.raises(ToolValidationError):
            ToolValidator.validate_tool_function(invalid_tool)

        with pytest.raises(ToolValidationError):
            ToolValidator.validate_tool_function("not_callable")
```

## 🔗 **Integration Tests**

### **1. FastMCP Integration Tests**

```python
# tests/core/tools/test_fastmcp_integration.py
import pytest
import asyncio
from fastmcp import Client
from agenthub.core.tools import tool, get_mcp_server

class TestFastMCPIntegration:
    @pytest.mark.asyncio
    async def test_tool_execution_via_mcp(self):
        """Test tool execution through MCP"""
        @tool(name="mcp_test_tool", description="MCP test tool")
        def mcp_test_tool(data: str) -> dict:
            return {"result": f"processed_{data}"}

        mcp_server = get_mcp_server()

        # Create MCP client
        client = Client(mcp_server)

        async with client:
            # Execute tool via MCP
            result = await client.call_tool("mcp_test_tool", {"data": "test"})
            assert result.content[0].text == '{"result": "processed_test"}'

    @pytest.mark.asyncio
    async def test_multiple_tools_via_mcp(self):
        """Test multiple tools through MCP"""
        @tool(name="tool1", description="Tool 1")
        def tool1(data: str) -> dict:
            return {"tool": "1", "data": data}

        @tool(name="tool2", description="Tool 2")
        def tool2(data: str) -> dict:
            return {"tool": "2", "data": data}

        mcp_server = get_mcp_server()
        client = Client(mcp_server)

        async with client:
            # List available tools
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools.tools]
            assert "tool1" in tool_names
            assert "tool2" in tool_names

            # Execute both tools
            result1 = await client.call_tool("tool1", {"data": "test1"})
            result2 = await client.call_tool("tool2", {"data": "test2"})

            assert result1.content[0].text == '{"tool": "1", "data": "test1"}'
            assert result2.content[0].text == '{"tool": "2", "data": "test2"}'
```

### **2. Tool Metadata Tests**

```python
# tests/core/tools/test_metadata.py
import pytest
from agenthub.core.tools import tool, get_tool_metadata

class TestToolMetadata:
    def test_tool_metadata_creation(self):
        """Test tool metadata creation"""
        @tool(name="metadata_test", description="Metadata test tool")
        def metadata_test(data: str, optional: int = 10) -> dict:
            return {"result": data, "optional": optional}

        metadata = get_tool_metadata("metadata_test")

        assert metadata.name == "metadata_test"
        assert metadata.description == "Metadata test tool"
        assert metadata.function == metadata_test
        assert metadata.namespace == "custom"

        # Check parameters
        assert "data" in metadata.parameters
        assert metadata.parameters["data"]["type"] == str
        assert metadata.parameters["data"]["required"] == True

        assert "optional" in metadata.parameters
        assert metadata.parameters["optional"]["type"] == int
        assert metadata.parameters["optional"]["required"] == False

    def test_tool_metadata_nonexistent(self):
        """Test getting metadata for nonexistent tool"""
        metadata = get_tool_metadata("nonexistent_tool")
        assert metadata is None
```

## ⚡ **Concurrency Tests**

### **1. Thread Safety Tests**

```python
# tests/core/tools/test_concurrency.py
import pytest
import threading
import time
from agenthub.core.tools import tool, get_available_tools

class TestConcurrency:
    def test_concurrent_tool_registration(self):
        """Test concurrent tool registration"""
        def register_tool(tool_id: int):
            @tool(name=f"concurrent_tool_{tool_id}", description=f"Tool {tool_id}")
            def tool_function(data: str) -> dict:
                return {"tool_id": tool_id, "data": data}

        # Register tools concurrently
        threads = []
        for i in range(10):
            thread = threading.Thread(target=register_tool, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check that all tools were registered
        available_tools = get_available_tools()
        for i in range(10):
            assert f"concurrent_tool_{i}" in available_tools

    def test_concurrent_tool_execution(self):
        """Test concurrent tool execution"""
        @tool(name="concurrent_execution_tool", description="Concurrent execution test")
        def concurrent_tool(data: str) -> dict:
            time.sleep(0.1)  # Simulate work
            return {"result": data}

        results = []

        def execute_tool(data: str):
            result = concurrent_tool(data)
            results.append(result)

        # Execute tool concurrently
        threads = []
        for i in range(5):
            thread = threading.Thread(target=execute_tool, args=(f"data_{i}",))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Check that all executions completed
        assert len(results) == 5
        for i in range(5):
            assert {"result": f"data_{i}"} in results
```

## 🚨 **Error Handling Tests**

### **1. Exception Tests**

```python
# tests/core/tools/test_errors.py
import pytest
from agenthub.core.tools import tool
from agenthub.core.tools.exceptions import (
    ToolRegistrationError,
    ToolNameConflictError,
    ToolValidationError,
    ToolExecutionError,
    ToolNotFoundError
)

class TestErrorHandling:
    def test_tool_name_conflict_error(self):
        """Test tool name conflict error"""
        @tool(name="conflict_tool", description="First tool")
        def tool1(data: str) -> dict:
            return {"result": data}

        with pytest.raises(ToolNameConflictError):
            @tool(name="conflict_tool", description="Second tool")
            def tool2(data: str) -> dict:
                return {"result": data}

    def test_tool_validation_error(self):
        """Test tool validation error"""
        with pytest.raises(ToolValidationError):
            @tool(name="invalid_tool", description="Invalid tool")
            def invalid_tool():
                pass  # No parameters

    def test_reserved_name_error(self):
        """Test reserved name error"""
        with pytest.raises(ToolValidationError):
            @tool(name="list_tools", description="Reserved name")
            def reserved_tool(data: str) -> dict:
                return {"result": data}
```

## 📊 **Performance Tests**

### **1. Tool Registration Performance**

```python
# tests/core/tools/test_performance.py
import pytest
import time
from agenthub.core.tools import tool

class TestPerformance:
    def test_tool_registration_performance(self):
        """Test tool registration performance"""
        start_time = time.time()

        # Register 100 tools
        for i in range(100):
            @tool(name=f"perf_tool_{i}", description=f"Performance tool {i}")
            def perf_tool(data: str) -> dict:
                return {"result": data}

        end_time = time.time()
        registration_time = end_time - start_time

        # Should complete in reasonable time (adjust threshold as needed)
        assert registration_time < 5.0  # 5 seconds for 100 tools

    def test_tool_execution_performance(self):
        """Test tool execution performance"""
        @tool(name="perf_execution_tool", description="Performance execution test")
        def perf_execution_tool(data: str) -> dict:
            return {"result": data}

        start_time = time.time()

        # Execute tool 1000 times
        for i in range(1000):
            result = perf_execution_tool(f"data_{i}")
            assert result == {"result": f"data_{i}"}

        end_time = time.time()
        execution_time = end_time - start_time

        # Should complete in reasonable time
        assert execution_time < 1.0  # 1 second for 1000 executions
```

## 🎯 **Test Coverage Goals**

- **Unit Tests**: 95%+ coverage for core functionality
- **Integration Tests**: 90%+ coverage for FastMCP integration
- **Concurrency Tests**: 100% coverage for thread safety
- **Error Handling Tests**: 100% coverage for exception scenarios
- **Performance Tests**: Baseline performance metrics

## 🚀 **Test Execution**

### **Running Tests**
```bash
# Run all tests
pytest tests/core/tools/

# Run specific test categories
pytest tests/core/tools/test_registry.py
pytest tests/core/tools/test_fastmcp_integration.py
pytest tests/core/tools/test_concurrency.py

# Run with coverage
pytest tests/core/tools/ --cov=agenthub.core.tools --cov-report=html
```

### **Continuous Integration**
- All tests must pass before merge
- Performance tests must meet baseline metrics
- Coverage must meet minimum thresholds
- Concurrency tests must pass on multiple platforms

## 🎯 **Success Criteria**

- ✅ All unit tests pass
- ✅ All integration tests pass
- ✅ All concurrency tests pass
- ✅ All error handling tests pass
- ✅ Performance tests meet baseline metrics
- ✅ Test coverage meets minimum thresholds
- ✅ Tests run reliably in CI/CD pipeline
