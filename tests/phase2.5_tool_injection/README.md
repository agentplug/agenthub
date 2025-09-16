# Phase 2.5 Tool Injection - Test Suite

This directory contains comprehensive unit tests for the Phase 2.5 tool injection functionality.

## 📁 Test Structure

```
tests/phase2.5_tool_injection/
├── __init__.py
├── conftest.py
├── run_tests.py
├── README.md
├── core/
│   ├── tools/
│   │   ├── test_tool_decorator.py
│   │   ├── test_tool_registry.py
│   │   └── test_tool_metadata.py
│   └── mcp/
│       └── test_mcp_client.py
├── runtime/
│   └── test_agent_wrapper.py
├── sdk/
│   └── test_load_agent.py
├── test_integration.py
└── test_performance.py
```

## 🧪 Test Categories

### **Unit Tests**
- **Core/Tools**: Tool decorator, registry, and metadata functionality
- **Core/MCP**: MCP client and server integration
- **Runtime**: Agent wrapper and tool injection
- **SDK**: Enhanced load_agent functionality

### **Integration Tests**
- Complete tool injection workflow
- Tool context generation
- Agent loading with tools
- Error handling throughout workflow

### **Performance Tests**
- Tool registration performance
- Tool execution performance
- Concurrent operations
- Memory usage stability
- Scalability benchmarks

## 🚀 Running Tests

### **Quick Start**
```bash
# Run all tests
python tests/phase2.5_tool_injection/run_tests.py

# Run specific test types
python tests/phase2.5_tool_injection/run_tests.py unit
python tests/phase2.5_tool_injection/run_tests.py integration
python tests/phase2.5_tool_injection/run_tests.py performance
```

### **Advanced Options**
```bash
# Verbose output
python tests/phase2.5_tool_injection/run_tests.py -v

# With coverage reporting
python tests/phase2.5_tool_injection/run_tests.py -c

# Parallel execution
python tests/phase2.5_tool_injection/run_tests.py -p

# Fast tests only (exclude slow/performance tests)
python tests/phase2.5_tool_injection/run_tests.py fast
```

### **Using pytest directly**
```bash
# Run all tests
pytest tests/phase2.5_tool_injection/

# Run specific test file
pytest tests/phase2.5_tool_injection/core/tools/test_tool_decorator.py

# Run with markers
pytest tests/phase2.5_tool_injection/ -m unit
pytest tests/phase2.5_tool_injection/ -m performance
pytest tests/phase2.5_tool_injection/ -m "not slow"
```

## 📊 Test Coverage

### **Core/Tools Module**
- ✅ Tool decorator functionality
- ✅ Tool registry operations
- ✅ Tool metadata management
- ✅ Tool validation
- ✅ Error handling
- ✅ Thread safety

### **Core/MCP Module**
- ✅ MCP client connection
- ✅ Tool discovery
- ✅ Tool execution
- ✅ Error handling
- ✅ Async operations

### **Runtime Module**
- ✅ Agent wrapper enhancement
- ✅ Tool context injection
- ✅ Tool execution
- ✅ Tool metadata access

### **SDK Module**
- ✅ Enhanced load_agent
- ✅ Tool assignment
- ✅ Tool validation
- ✅ Error handling

### **Integration Tests**
- ✅ Complete workflow
- ✅ Tool context generation
- ✅ Agent loading with tools
- ✅ Concurrent operations

### **Performance Tests**
- ✅ Registration performance
- ✅ Execution performance
- ✅ Memory usage
- ✅ Scalability

## 🎯 Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.performance`: Performance tests
- `@pytest.mark.slow`: Slow-running tests
- `@pytest.mark.mcp`: Tests requiring MCP server
- `@pytest.mark.concurrent`: Concurrent execution tests

## 🔧 Test Configuration

### **Fixtures**
- `reset_tool_registry`: Resets registry before each test
- `tool_registry`: Provides clean registry instance
- `mock_agent_info`: Mock agent information
- `sample_tools`: Pre-registered sample tools
- `mock_mcp_client`: Mock MCP client
- `performance_thresholds`: Performance test thresholds

### **Test Data**
- Simple tools (add, multiply, greet)
- Complex tools (data_analyzer, file_processor)
- Agent configurations
- Performance benchmarks

## 📈 Performance Benchmarks

### **Tool Registration**
- 100 tools: < 5 seconds
- 1000 tools: < 30 seconds
- Time per tool: < 50ms

### **Tool Execution**
- 1000 executions: < 1 second
- Time per execution: < 1ms
- Concurrent execution: < 2 seconds

### **Memory Usage**
- Base usage: < 10MB
- Per tool: < 1KB
- Memory increase: < 50MB for 200 tools

## 🐛 Debugging Tests

### **Verbose Output**
```bash
pytest tests/phase2.5_tool_injection/ -v -s
```

### **Debug Specific Test**
```bash
pytest tests/phase2.5_tool_injection/core/tools/test_tool_decorator.py::TestToolDecorator::test_tool_decorator_basic_functionality -v -s
```

### **Show Test Coverage**
```bash
pytest tests/phase2.5_tool_injection/ --cov=agenthub --cov-report=html
```

## 📝 Writing New Tests

### **Test Structure**
```python
class TestNewFeature:
    """Test cases for new feature."""
    
    def setup_method(self):
        """Set up test environment."""
        # Setup code here
    
    def test_feature_basic_functionality(self):
        """Test basic functionality."""
        # Test code here
    
    def test_feature_error_handling(self):
        """Test error handling."""
        # Test code here
```

### **Using Fixtures**
```python
def test_with_fixtures(tool_registry, sample_tools):
    """Test using fixtures."""
    # Use tool_registry and sample_tools
    pass
```

### **Performance Testing**
```python
def test_performance(performance_thresholds):
    """Test performance."""
    start_time = time.time()
    # Do work
    end_time = time.time()
    
    assert (end_time - start_time) < performance_thresholds["tool_execution_time"]
```

## 🚨 Known Issues

1. **MCP Server Dependency**: Some tests require MCP server to be running
2. **Async Tests**: Some async tests may need special handling
3. **Performance Tests**: May be slow on some systems
4. **Concurrent Tests**: May fail on systems with limited resources

## 📚 Dependencies

- `pytest`: Test framework
- `pytest-cov`: Coverage reporting
- `pytest-xdist`: Parallel test execution
- `psutil`: Memory usage monitoring (for performance tests)

## 🎉 Success Criteria

Tests are considered successful when:

1. **All unit tests pass** (100% pass rate)
2. **Integration tests pass** (100% pass rate)
3. **Performance tests meet thresholds** (95% pass rate)
4. **Test coverage > 90%** for core functionality
5. **No memory leaks** detected
6. **Concurrent tests pass** without race conditions

## 🔄 Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Phase 2.5 Tests
  run: |
    python tests/phase2.5_tool_injection/run_tests.py -v -c
```

## 📞 Support

For test-related issues:

1. Check test output for specific error messages
2. Verify all dependencies are installed
3. Ensure MCP server is running for MCP tests
4. Check system resources for performance tests
5. Review test configuration in `conftest.py`
