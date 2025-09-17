# Runtime Testing Strategy - Phase 2.5

**Document Type**: Testing Strategy
**Module**: runtime
**Phase**: 2.5
**Status**: Draft

## 🎯 **Purpose**

Comprehensive testing strategy for tool injection, agent context management, and MCP client integration.

## 🧪 **Testing Overview**

### **Test Categories**
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: MCP client integration testing
3. **Context Tests**: Agent context management testing
4. **Error Handling Tests**: Exception and error scenarios
5. **Performance Tests**: Tool injection and context performance

## 🔧 **Unit Tests**

### **1. ToolInjector Tests**

```python
# tests/runtime/test_tool_injector.py
import pytest
from agenthub.runtime import ToolInjector
from agenthub.core.tools import tool
from agenthub.runtime.exceptions import ToolInjectionError

class TestToolInjector:
    def test_tool_injection_basic(self):
        """Test basic tool injection"""
        # Define test tool
        @tool(name="test_tool", description="Test tool")
        def test_tool(data: str) -> dict:
            return {"result": data}

        # Create tool injector
        tool_injector = ToolInjector()

        # Inject tools into agent
        tool_metadata = tool_injector.inject_tools_into_agent(
            agent_id="agent_1",
            tool_names=["test_tool"]
        )

        # Verify injection
        assert "available_tools" in tool_metadata
        assert "test_tool" in tool_metadata["available_tools"]
        assert "tool_descriptions" in tool_metadata
        assert tool_metadata["tool_descriptions"]["test_tool"] == "Test tool"

    def test_tool_injection_with_invalid_tools(self):
        """Test tool injection with invalid tools"""
        tool_injector = ToolInjector()

        # Try to inject invalid tools
        with pytest.raises(ToolInjectionError):
            tool_injector.inject_tools_into_agent(
                agent_id="agent_1",
                tool_names=["invalid_tool", "another_invalid_tool"]
            )

    def test_tool_injection_with_mixed_tools(self):
        """Test tool injection with mixed valid and invalid tools"""
        # Define valid tool
        @tool(name="valid_tool", description="Valid tool")
        def valid_tool(data: str) -> dict:
            return {"result": data}

        tool_injector = ToolInjector()

        # Inject mixed tools
        tool_metadata = tool_injector.inject_tools_into_agent(
            agent_id="agent_1",
            tool_names=["valid_tool", "invalid_tool"]
        )

        # Should only inject valid tools
        assert "valid_tool" in tool_metadata["available_tools"]
        assert "invalid_tool" not in tool_metadata["available_tools"]

    def test_tool_descriptions(self):
        """Test tool descriptions retrieval"""
        # Define test tool
        @tool(name="description_tool", description="Tool with description")
        def description_tool(data: str) -> dict:
            return {"result": data}

        tool_injector = ToolInjector()

        # Get tool descriptions
        descriptions = tool_injector.get_tool_descriptions(["description_tool"])

        assert "description_tool" in descriptions
        assert descriptions["description_tool"] == "Tool with description"

    def test_tool_examples(self):
        """Test tool examples generation"""
        # Define test tool
        @tool(name="example_tool", description="Tool with examples")
        def example_tool(data: str, count: int = 1) -> dict:
            return {"result": data, "count": count}

        tool_injector = ToolInjector()

        # Get tool examples
        examples = tool_injector.get_tool_examples(["example_tool"])

        assert "example_tool" in examples
        assert len(examples["example_tool"]) > 0
        assert "example_tool(" in examples["example_tool"][0]

    def test_injected_tools_retrieval(self):
        """Test injected tools retrieval"""
        # Define test tool
        @tool(name="retrieval_tool", description="Tool for retrieval test")
        def retrieval_tool(data: str) -> dict:
            return {"result": data}

        tool_injector = ToolInjector()

        # Inject tools
        tool_injector.inject_tools_into_agent("agent_1", ["retrieval_tool"])

        # Get injected tools
        injected_tools = tool_injector.get_injected_tools("agent_1")

        assert injected_tools is not None
        assert "retrieval_tool" in injected_tools.available_tools
```

### **2. AgentContextManager Tests**

```python
# tests/runtime/test_context_manager.py
import pytest
from agenthub.runtime import AgentContextManager
from agenthub.runtime.exceptions import AgentContextError

class TestAgentContextManager:
    def test_create_agent_context(self):
        """Test agent context creation"""
        context_manager = AgentContextManager()

        # Create agent context
        agent_context = context_manager.create_agent_context(
            agent_id="agent_1",
            base_context={"name": "Test Agent", "capabilities": ["analysis"]},
            tool_metadata={
                "available_tools": ["tool1", "tool2"],
                "tool_descriptions": {"tool1": "Tool 1", "tool2": "Tool 2"},
                "tool_usage_examples": {"tool1": ["tool1('data')"], "tool2": ["tool2('file')"]}
            }
        )

        # Verify context creation
        assert agent_context["agent_id"] == "agent_1"
        assert agent_context["base_context"]["name"] == "Test Agent"
        assert "tool1" in agent_context["tools"]["available_tools"]
        assert "tool2" in agent_context["tools"]["available_tools"]
        assert agent_context["tool_access"]["tool1"] == True
        assert agent_context["tool_access"]["tool2"] == True

    def test_create_duplicate_agent_context(self):
        """Test creating duplicate agent context"""
        context_manager = AgentContextManager()

        # Create first context
        context_manager.create_agent_context(
            agent_id="agent_1",
            base_context={"name": "Test Agent"},
            tool_metadata={"available_tools": ["tool1"]}
        )

        # Try to create duplicate context
        with pytest.raises(AgentContextError):
            context_manager.create_agent_context(
                agent_id="agent_1",
                base_context={"name": "Another Agent"},
                tool_metadata={"available_tools": ["tool2"]}
            )

    def test_update_agent_context(self):
        """Test agent context update"""
        context_manager = AgentContextManager()

        # Create agent context
        context_manager.create_agent_context(
            agent_id="agent_1",
            base_context={"name": "Test Agent"},
            tool_metadata={"available_tools": ["tool1"]}
        )

        # Update context
        updated_context = context_manager.update_agent_context(
            agent_id="agent_1",
            updates={
                "base_context": {"name": "Updated Agent", "version": "2.0"},
                "tool_access": {"tool1": False, "tool2": True}
            }
        )

        # Verify update
        assert updated_context["base_context"]["name"] == "Updated Agent"
        assert updated_context["base_context"]["version"] == "2.0"
        assert updated_context["tool_access"]["tool1"] == False
        assert updated_context["tool_access"]["tool2"] == True

    def test_get_agent_context(self):
        """Test getting agent context"""
        context_manager = AgentContextManager()

        # Create agent context
        original_context = context_manager.create_agent_context(
            agent_id="agent_1",
            base_context={"name": "Test Agent"},
            tool_metadata={"available_tools": ["tool1"]}
        )

        # Get agent context
        retrieved_context = context_manager.get_agent_context("agent_1")

        # Verify retrieval
        assert retrieved_context is not None
        assert retrieved_context["agent_id"] == "agent_1"
        assert retrieved_context["base_context"]["name"] == "Test Agent"

    def test_get_nonexistent_agent_context(self):
        """Test getting nonexistent agent context"""
        context_manager = AgentContextManager()

        # Try to get nonexistent context
        context = context_manager.get_agent_context("nonexistent_agent")

        assert context is None

    def test_cleanup_agent_context(self):
        """Test agent context cleanup"""
        context_manager = AgentContextManager()

        # Create agent context
        context_manager.create_agent_context(
            agent_id="agent_1",
            base_context={"name": "Test Agent"},
            tool_metadata={"available_tools": ["tool1"]}
        )

        # Verify context exists
        assert context_manager.get_agent_context("agent_1") is not None

        # Cleanup context
        cleanup_result = context_manager.cleanup_agent_context("agent_1")

        # Verify cleanup
        assert cleanup_result == True
        assert context_manager.get_agent_context("agent_1") is None

    def test_cleanup_nonexistent_agent_context(self):
        """Test cleanup of nonexistent agent context"""
        context_manager = AgentContextManager()

        # Try to cleanup nonexistent context
        cleanup_result = context_manager.cleanup_agent_context("nonexistent_agent")

        assert cleanup_result == False

    def test_list_agent_contexts(self):
        """Test listing agent contexts"""
        context_manager = AgentContextManager()

        # Create multiple contexts
        context_manager.create_agent_context(
            agent_id="agent_1",
            base_context={"name": "Agent 1"},
            tool_metadata={"available_tools": ["tool1"]}
        )
        context_manager.create_agent_context(
            agent_id="agent_2",
            base_context={"name": "Agent 2"},
            tool_metadata={"available_tools": ["tool2"]}
        )

        # List contexts
        context_ids = context_manager.list_agent_contexts()

        assert "agent_1" in context_ids
        assert "agent_2" in context_ids
        assert len(context_ids) == 2
```

### **3. MCPClientManager Tests**

```python
# tests/runtime/test_mcp_client_manager.py
import pytest
import asyncio
from agenthub.runtime import MCPClientManager
from agenthub.core.tools import tool
from agenthub.runtime.exceptions import MCPClientError

class TestMCPClientManager:
    @pytest.mark.asyncio
    async def test_create_client_for_agent(self):
        """Test creating MCP client for agent"""
        # Define test tool
        @tool(name="client_test_tool", description="Client test tool")
        def client_test_tool(data: str) -> dict:
            return {"result": data}

        client_manager = MCPClientManager(max_clients=5)

        # Create client for agent
        client = await client_manager.get_client_for_agent("agent_1")

        assert client is not None
        assert "agent_1" in client_manager._clients

    @pytest.mark.asyncio
    async def test_client_reuse(self):
        """Test client reuse for same agent"""
        client_manager = MCPClientManager(max_clients=5)

        # Get client twice for same agent
        client1 = await client_manager.get_client_for_agent("agent_1")
        client2 = await client_manager.get_client_for_agent("agent_1")

        # Should return same client
        assert client1 is client2

    @pytest.mark.asyncio
    async def test_client_limit(self):
        """Test client limit enforcement"""
        client_manager = MCPClientManager(max_clients=2)

        # Create clients up to limit
        client1 = await client_manager.get_client_for_agent("agent_1")
        client2 = await client_manager.get_client_for_agent("agent_2")

        # Verify we have 2 clients
        assert len(client_manager._clients) == 2

        # Create third client should reuse one of the existing
        client3 = await client_manager.get_client_for_agent("agent_3")

        # Should still have 2 clients
        assert len(client_manager._clients) == 2

    @pytest.mark.asyncio
    async def test_tool_execution(self):
        """Test tool execution via MCP client"""
        # Define test tool
        @tool(name="execution_test_tool", description="Execution test tool")
        def execution_test_tool(data: str) -> dict:
            return {"result": f"processed_{data}"}

        client_manager = MCPClientManager()

        # Execute tool
        result = await client_manager.execute_tool(
            agent_id="agent_1",
            tool_name="execution_test_tool",
            arguments={"data": "test"}
        )

        assert result == '{"result": "processed_test"}'

    @pytest.mark.asyncio
    async def test_tool_execution_error(self):
        """Test tool execution error handling"""
        # Define error tool
        @tool(name="error_tool", description="Tool that raises error")
        def error_tool(data: str) -> dict:
            raise Exception("Tool execution failed")

        client_manager = MCPClientManager()

        # Execute tool should raise error
        with pytest.raises(MCPClientError):
            await client_manager.execute_tool(
                agent_id="agent_1",
                tool_name="error_tool",
                arguments={"data": "test"}
            )

    @pytest.mark.asyncio
    async def test_close_client_for_agent(self):
        """Test closing client for specific agent"""
        client_manager = MCPClientManager()

        # Create client for agent
        await client_manager.get_client_for_agent("agent_1")

        # Verify client exists
        assert "agent_1" in client_manager._clients

        # Close client for agent
        close_result = await client_manager.close_client_for_agent("agent_1")

        # Verify client is closed
        assert close_result == True
        assert "agent_1" not in client_manager._clients

    @pytest.mark.asyncio
    async def test_close_all_clients(self):
        """Test closing all clients"""
        client_manager = MCPClientManager()

        # Create multiple clients
        await client_manager.get_client_for_agent("agent_1")
        await client_manager.get_client_for_agent("agent_2")

        # Verify clients exist
        assert len(client_manager._clients) == 2

        # Close all clients
        close_result = await client_manager.close_all_clients()

        # Verify all clients are closed
        assert close_result == True
        assert len(client_manager._clients) == 0

    def test_client_status(self):
        """Test client status retrieval"""
        client_manager = MCPClientManager(max_clients=5)

        # Get initial status
        status = client_manager.get_client_status()

        assert status["total_clients"] == 0
        assert status["max_clients"] == 5
        assert status["agents"] == []
```

## 🔗 **Integration Tests**

### **1. Tool Injection Integration Tests**

```python
# tests/runtime/test_tool_injection_integration.py
import pytest
import asyncio
from agenthub.runtime import get_tool_injector, get_context_manager, get_client_manager
from agenthub.core.tools import tool

class TestToolInjectionIntegration:
    @pytest.mark.asyncio
    async def test_complete_tool_injection_flow(self):
        """Test complete tool injection flow"""
        # Define test tools
        @tool(name="integration_tool1", description="Integration tool 1")
        def integration_tool1(data: str) -> dict:
            return {"tool": "1", "data": data}

        @tool(name="integration_tool2", description="Integration tool 2")
        def integration_tool2(data: str) -> dict:
            return {"tool": "2", "data": data}

        # Get managers
        tool_injector = get_tool_injector()
        context_manager = get_context_manager()
        client_manager = get_client_manager()

        # Inject tools into agent
        tool_metadata = tool_injector.inject_tools_into_agent(
            agent_id="agent_1",
            tool_names=["integration_tool1", "integration_tool2"]
        )

        # Create agent context
        agent_context = context_manager.create_agent_context(
            agent_id="agent_1",
            base_context={"name": "Integration Test Agent"},
            tool_metadata=tool_metadata
        )

        # Verify context creation
        assert "integration_tool1" in agent_context["tools"]["available_tools"]
        assert "integration_tool2" in agent_context["tools"]["available_tools"]

        # Execute tools
        result1 = await client_manager.execute_tool(
            agent_id="agent_1",
            tool_name="integration_tool1",
            arguments={"data": "test1"}
        )

        result2 = await client_manager.execute_tool(
            agent_id="agent_1",
            tool_name="integration_tool2",
            arguments={"data": "test2"}
        )

        # Verify tool execution
        assert result1 == '{"tool": "1", "data": "test1"}'
        assert result2 == '{"tool": "2", "data": "test2"}'

    @pytest.mark.asyncio
    async def test_tool_injection_with_multiple_agents(self):
        """Test tool injection with multiple agents"""
        # Define test tools
        @tool(name="multi_agent_tool1", description="Multi-agent tool 1")
        def multi_agent_tool1(data: str) -> dict:
            return {"agent": "1", "data": data}

        @tool(name="multi_agent_tool2", description="Multi-agent tool 2")
        def multi_agent_tool2(data: str) -> dict:
            return {"agent": "2", "data": data}

        # Get managers
        tool_injector = get_tool_injector()
        context_manager = get_context_manager()
        client_manager = get_client_manager()

        # Inject different tools to different agents
        tool_metadata1 = tool_injector.inject_tools_into_agent(
            agent_id="agent_1",
            tool_names=["multi_agent_tool1"]
        )

        tool_metadata2 = tool_injector.inject_tools_into_agent(
            agent_id="agent_2",
            tool_names=["multi_agent_tool2"]
        )

        # Create contexts for both agents
        context1 = context_manager.create_agent_context(
            agent_id="agent_1",
            base_context={"name": "Agent 1"},
            tool_metadata=tool_metadata1
        )

        context2 = context_manager.create_agent_context(
            agent_id="agent_2",
            base_context={"name": "Agent 2"},
            tool_metadata=tool_metadata2
        )

        # Execute tools for each agent
        result1 = await client_manager.execute_tool(
            agent_id="agent_1",
            tool_name="multi_agent_tool1",
            arguments={"data": "test1"}
        )

        result2 = await client_manager.execute_tool(
            agent_id="agent_2",
            tool_name="multi_agent_tool2",
            arguments={"data": "test2"}
        )

        # Verify results
        assert result1 == '{"agent": "1", "data": "test1"}'
        assert result2 == '{"agent": "2", "data": "test2"}'
```

### **2. Context Management Integration Tests**

```python
# tests/runtime/test_context_management_integration.py
import pytest
from agenthub.runtime import get_tool_injector, get_context_manager
from agenthub.core.tools import tool

class TestContextManagementIntegration:
    def test_context_lifecycle_management(self):
        """Test complete context lifecycle management"""
        # Define test tool
        @tool(name="lifecycle_tool", description="Lifecycle test tool")
        def lifecycle_tool(data: str) -> dict:
            return {"result": data}

        # Get managers
        tool_injector = get_tool_injector()
        context_manager = get_context_manager()

        # Inject tools
        tool_metadata = tool_injector.inject_tools_into_agent(
            agent_id="agent_1",
            tool_names=["lifecycle_tool"]
        )

        # Create context
        agent_context = context_manager.create_agent_context(
            agent_id="agent_1",
            base_context={"name": "Lifecycle Test Agent"},
            tool_metadata=tool_metadata
        )

        # Verify context creation
        assert agent_context["agent_id"] == "agent_1"
        assert "lifecycle_tool" in agent_context["tools"]["available_tools"]

        # Update context
        updated_context = context_manager.update_agent_context(
            agent_id="agent_1",
            updates={
                "base_context": {"name": "Updated Lifecycle Test Agent", "version": "2.0"}
            }
        )

        # Verify context update
        assert updated_context["base_context"]["name"] == "Updated Lifecycle Test Agent"
        assert updated_context["base_context"]["version"] == "2.0"

        # Get context
        retrieved_context = context_manager.get_agent_context("agent_1")

        # Verify context retrieval
        assert retrieved_context["agent_id"] == "agent_1"
        assert retrieved_context["base_context"]["name"] == "Updated Lifecycle Test Agent"

        # Cleanup context
        cleanup_result = context_manager.cleanup_agent_context("agent_1")

        # Verify context cleanup
        assert cleanup_result == True
        assert context_manager.get_agent_context("agent_1") is None
```

## ⚡ **Performance Tests**

### **1. Tool Injection Performance Tests**

```python
# tests/runtime/test_performance.py
import pytest
import time
from agenthub.runtime import get_tool_injector, get_context_manager
from agenthub.core.tools import tool

class TestPerformance:
    def test_tool_injection_performance(self):
        """Test tool injection performance"""
        # Define multiple test tools
        for i in range(10):
            @tool(name=f"perf_tool_{i}", description=f"Performance tool {i}")
            def perf_tool(data: str) -> dict:
                return {"result": data}

        tool_injector = get_tool_injector()

        # Measure injection time
        start_time = time.time()

        tool_metadata = tool_injector.inject_tools_into_agent(
            agent_id="agent_1",
            tool_names=[f"perf_tool_{i}" for i in range(10)]
        )

        end_time = time.time()
        injection_time = end_time - start_time

        # Should complete in reasonable time
        assert injection_time < 2.0  # 2 seconds for 10 tools
        assert len(tool_metadata["available_tools"]) == 10

    def test_context_creation_performance(self):
        """Test context creation performance"""
        # Define test tool
        @tool(name="context_perf_tool", description="Context performance tool")
        def context_perf_tool(data: str) -> dict:
            return {"result": data}

        tool_injector = get_tool_injector()
        context_manager = get_context_manager()

        # Inject tools
        tool_metadata = tool_injector.inject_tools_into_agent(
            agent_id="agent_1",
            tool_names=["context_perf_tool"]
        )

        # Measure context creation time
        start_time = time.time()

        agent_context = context_manager.create_agent_context(
            agent_id="agent_1",
            base_context={"name": "Performance Test Agent"},
            tool_metadata=tool_metadata
        )

        end_time = time.time()
        creation_time = end_time - start_time

        # Should complete in reasonable time
        assert creation_time < 0.1  # 100ms for context creation
        assert agent_context["agent_id"] == "agent_1"

    def test_context_update_performance(self):
        """Test context update performance"""
        # Define test tool
        @tool(name="update_perf_tool", description="Update performance tool")
        def update_perf_tool(data: str) -> dict:
            return {"result": data}

        tool_injector = get_tool_injector()
        context_manager = get_context_manager()

        # Create initial context
        tool_metadata = tool_injector.inject_tools_into_agent(
            agent_id="agent_1",
            tool_names=["update_perf_tool"]
        )

        context_manager.create_agent_context(
            agent_id="agent_1",
            base_context={"name": "Performance Test Agent"},
            tool_metadata=tool_metadata
        )

        # Measure context update time
        start_time = time.time()

        for i in range(100):
            context_manager.update_agent_context(
                agent_id="agent_1",
                updates={"base_context": {"update_count": i}}
            )

        end_time = time.time()
        update_time = end_time - start_time

        # Should complete in reasonable time
        assert update_time < 1.0  # 1 second for 100 updates
```

## 🚨 **Error Handling Tests**

### **1. Tool Injection Error Tests**

```python
# tests/runtime/test_errors.py
import pytest
from agenthub.runtime import ToolInjector, AgentContextManager, MCPClientManager
from agenthub.runtime.exceptions import (
    ToolInjectionError,
    AgentContextError,
    MCPClientError
)

class TestErrorHandling:
    def test_tool_injection_error(self):
        """Test tool injection error handling"""
        tool_injector = ToolInjector()

        # Try to inject invalid tools
        with pytest.raises(ToolInjectionError):
            tool_injector.inject_tools_into_agent(
                agent_id="agent_1",
                tool_names=["invalid_tool"]
            )

    def test_agent_context_error(self):
        """Test agent context error handling"""
        context_manager = AgentContextManager()

        # Try to create duplicate context
        context_manager.create_agent_context(
            agent_id="agent_1",
            base_context={"name": "Test Agent"},
            tool_metadata={"available_tools": ["tool1"]}
        )

        with pytest.raises(AgentContextError):
            context_manager.create_agent_context(
                agent_id="agent_1",
                base_context={"name": "Another Agent"},
                tool_metadata={"available_tools": ["tool2"]}
            )

    @pytest.mark.asyncio
    async def test_mcp_client_error(self):
        """Test MCP client error handling"""
        client_manager = MCPClientManager()

        # Try to execute tool without creating client
        with pytest.raises(MCPClientError):
            await client_manager.execute_tool(
                agent_id="agent_1",
                tool_name="nonexistent_tool",
                arguments={"data": "test"}
            )
```

## 🎯 **Test Coverage Goals**

- **Unit Tests**: 95%+ coverage for core functionality
- **Integration Tests**: 90%+ coverage for MCP integration
- **Context Tests**: 100% coverage for context management
- **Error Handling Tests**: 100% coverage for exception scenarios
- **Performance Tests**: Baseline performance metrics

## 🚀 **Test Execution**

### **Running Tests**
```bash
# Run all tests
pytest tests/runtime/

# Run specific test categories
pytest tests/runtime/test_tool_injector.py
pytest tests/runtime/test_context_manager.py
pytest tests/runtime/test_mcp_client_manager.py

# Run with coverage
pytest tests/runtime/ --cov=agenthub.runtime --cov-report=html
```

### **Continuous Integration**
- All tests must pass before merge
- Performance tests must meet baseline metrics
- Coverage must meet minimum thresholds
- Context tests must pass on multiple platforms

## 🎯 **Success Criteria**

- ✅ All unit tests pass
- ✅ All integration tests pass
- ✅ All context tests pass
- ✅ All error handling tests pass
- ✅ Performance tests meet baseline metrics
- ✅ Test coverage meets minimum thresholds
- ✅ Tests run reliably in CI/CD pipeline
