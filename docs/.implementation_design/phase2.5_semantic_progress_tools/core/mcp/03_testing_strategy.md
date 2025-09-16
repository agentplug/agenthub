# Core/MCP Testing Strategy - Phase 2.5

**Document Type**: Testing Strategy
**Module**: core/mcp
**Phase**: 2.5
**Status**: Draft

## 🎯 **Purpose**

Comprehensive testing strategy for MCP server management, tool routing, context tracking, and FastMCP integration.

## 🧪 **Testing Overview**

### **Test Categories**
1. **Unit Tests**: Individual component testing
2. **Integration Tests**: FastMCP integration testing
3. **Concurrency Tests**: Thread safety and concurrent execution
4. **Error Handling Tests**: Exception and error scenarios
5. **Performance Tests**: Tool execution and routing performance

## 🔧 **Unit Tests**

### **1. AgentToolManager Tests**

```python
# tests/core/mcp/test_manager.py
import pytest
import asyncio
from agenthub.core.mcp import AgentToolManager, ToolExecutionContext
from agenthub.core.mcp.exceptions import ToolAccessDeniedError, ToolExecutionError

class TestAgentToolManager:
    def test_tool_assignment(self):
        """Test tool assignment to agent"""
        manager = AgentToolManager()

        # Assign tools to agent
        assigned_tools = manager.assign_tools_to_agent(
            agent_id="agent_1",
            tool_names=["tool1", "tool2", "invalid_tool"]
        )

        # Should only assign valid tools
        assert "tool1" in assigned_tools
        assert "tool2" in assigned_tools
        assert "invalid_tool" not in assigned_tools

        # Verify assignment
        agent_tools = manager.get_agent_tools("agent_1")
        assert set(agent_tools) == {"tool1", "tool2"}

    def test_tool_access_validation(self):
        """Test tool access validation"""
        manager = AgentToolManager()

        # Assign tools to agent
        manager.assign_tools_to_agent("agent_1", ["tool1", "tool2"])

        # Valid access
        assert manager.validate_tool_access("agent_1", "tool1") == True
        assert manager.validate_tool_access("agent_1", "tool2") == True

        # Invalid access
        assert manager.validate_tool_access("agent_1", "tool3") == False
        assert manager.validate_tool_access("agent_2", "tool1") == False

    @pytest.mark.asyncio
    async def test_tool_execution(self):
        """Test tool execution"""
        manager = AgentToolManager()

        # Mock tool execution
        with pytest.MonkeyPatch().context() as m:
            m.setattr(manager, 'client', None)
            m.setattr(manager, '_ensure_client', lambda: None)

            # Mock MCP client
            class MockClient:
                async def call_tool(self, tool_name, arguments):
                    class MockResult:
                        content = [type('obj', (object,), {'text': '{"result": "success"}'})]
                    return MockResult()

            manager.client = MockClient()

            # Execute tool
            result = await manager.execute_tool("test_tool", {"data": "test"})
            assert result == '{"result": "success"}'

    @pytest.mark.asyncio
    async def test_tool_execution_with_agent_id(self):
        """Test tool execution with agent ID validation"""
        manager = AgentToolManager()

        # Assign tools to agent
        manager.assign_tools_to_agent("agent_1", ["tool1"])

        # Mock tool execution
        with pytest.MonkeyPatch().context() as m:
            m.setattr(manager, 'client', None)
            m.setattr(manager, '_ensure_client', lambda: None)

            class MockClient:
                async def call_tool(self, tool_name, arguments):
                    class MockResult:
                        content = [type('obj', (object,), {'text': '{"result": "success"}'})]
                    return MockResult()

            manager.client = MockClient()

            # Valid execution
            result = await manager.execute_tool("tool1", {"data": "test"}, "agent_1")
            assert result == '{"result": "success"}'

            # Invalid execution - tool not assigned to agent
            with pytest.raises(ToolAccessDeniedError):
                await manager.execute_tool("tool2", {"data": "test"}, "agent_1")

    def test_execution_context_creation(self):
        """Test execution context creation"""
        manager = AgentToolManager()

        execution_id = manager._create_execution_context(
            agent_id="agent_1",
            tool_name="test_tool",
            arguments={"data": "test"}
        )

        assert execution_id in manager.execution_contexts
        context = manager.execution_contexts[execution_id]
        assert context.agent_id == "agent_1"
        assert context.tool_name == "test_tool"
        assert context.arguments == {"data": "test"}
        assert context.status == "pending"

    def test_execution_context_update(self):
        """Test execution context update"""
        manager = AgentToolManager()

        execution_id = manager._create_execution_context(
            agent_id="agent_1",
            tool_name="test_tool",
            arguments={"data": "test"}
        )

        # Update context
        manager._update_execution_context(execution_id, "completed", "result")

        context = manager.execution_contexts[execution_id]
        assert context.status == "completed"
        assert context.result == "result"
```

### **2. Tool Execution Queue Tests**

```python
# tests/core/mcp/test_queue.py
import pytest
import asyncio
from agenthub.core.mcp import ToolExecutionQueue, QueuedToolExecution
from agenthub.core.mcp.exceptions import ToolTimeoutError, ToolExecutionError

class TestToolExecutionQueue:
    @pytest.mark.asyncio
    async def test_enqueue_tool_execution(self):
        """Test enqueuing tool execution"""
        queue = ToolExecutionQueue()

        execution_id = await queue.enqueue_tool_execution(
            tool_name="test_tool",
            arguments={"data": "test"},
            agent_id="agent_1"
        )

        assert execution_id.startswith("queue_")
        assert queue.queue.qsize() == 1

    @pytest.mark.asyncio
    async def test_tool_execution_processing(self):
        """Test tool execution processing"""
        queue = ToolExecutionQueue()

        # Mock tool execution
        with pytest.MonkeyPatch().context() as m:
            m.setattr(queue, '_execute_queued_tool', lambda x: "success")

            # Enqueue execution
            execution_id = await queue.enqueue_tool_execution(
                tool_name="test_tool",
                arguments={"data": "test"},
                agent_id="agent_1"
            )

            # Process queue
            await queue._process_queue()

            # Queue should be empty
            assert queue.queue.qsize() == 0

    @pytest.mark.asyncio
    async def test_tool_execution_timeout(self):
        """Test tool execution timeout"""
        queue = ToolExecutionQueue()

        # Mock slow tool execution
        async def slow_tool_execution(queued_execution):
            await asyncio.sleep(2.0)  # Longer than timeout
            return "success"

        with pytest.MonkeyPatch().context() as m:
            m.setattr(queue, '_execute_queued_tool', slow_tool_execution)

            # Enqueue execution with short timeout
            execution_id = await queue.enqueue_tool_execution(
                tool_name="slow_tool",
                arguments={"data": "test"},
                agent_id="agent_1"
            )

            # Process queue
            with pytest.raises(ToolTimeoutError):
                await queue._process_queue()

    @pytest.mark.asyncio
    async def test_cancel_execution(self):
        """Test canceling queued execution"""
        queue = ToolExecutionQueue()

        # Enqueue execution
        execution_id = await queue.enqueue_tool_execution(
            tool_name="test_tool",
            arguments={"data": "test"},
            agent_id="agent_1"
        )

        # Cancel execution
        cancelled = await queue.cancel_execution(execution_id)
        assert cancelled == False  # Not yet running

        # Start processing
        process_task = asyncio.create_task(queue._process_queue())

        # Cancel execution while running
        cancelled = await queue.cancel_execution(execution_id)
        assert cancelled == True

        # Stop processing
        process_task.cancel()

    def test_queue_status(self):
        """Test queue status"""
        queue = ToolExecutionQueue()

        status = queue.get_queue_status()
        assert "queue_size" in status
        assert "running" in status
        assert "active_executions" in status
        assert status["queue_size"] == 0
        assert status["running"] == False
        assert status["active_executions"] == 0
```

## 🔗 **Integration Tests**

### **1. FastMCP Integration Tests**

```python
# tests/core/mcp/test_fastmcp_integration.py
import pytest
import asyncio
from fastmcp import FastMCP, Client
from agenthub.core.tools import tool, get_mcp_server
from agenthub.core.mcp import get_tool_manager

class TestFastMCPIntegration:
    @pytest.mark.asyncio
    async def test_tool_execution_via_mcp(self):
        """Test tool execution through MCP"""
        # Define test tool
        @tool(name="mcp_integration_tool", description="MCP integration test")
        def mcp_integration_tool(data: str) -> dict:
            return {"result": f"processed_{data}"}

        # Get MCP server and tool manager
        mcp_server = get_mcp_server()
        tool_manager = get_tool_manager()

        # Assign tool to agent
        tool_manager.assign_tools_to_agent("agent_1", ["mcp_integration_tool"])

        # Execute tool via MCP
        result = await tool_manager.execute_tool(
            "mcp_integration_tool",
            {"data": "test"},
            "agent_1"
        )

        assert result == '{"result": "processed_test"}'

    @pytest.mark.asyncio
    async def test_multiple_tools_via_mcp(self):
        """Test multiple tools through MCP"""
        # Define test tools
        @tool(name="tool1", description="Tool 1")
        def tool1(data: str) -> dict:
            return {"tool": "1", "data": data}

        @tool(name="tool2", description="Tool 2")
        def tool2(data: str) -> dict:
            return {"tool": "2", "data": data}

        # Get MCP server and tool manager
        mcp_server = get_mcp_server()
        tool_manager = get_tool_manager()

        # Assign tools to agent
        tool_manager.assign_tools_to_agent("agent_1", ["tool1", "tool2"])

        # Execute both tools
        result1 = await tool_manager.execute_tool("tool1", {"data": "test1"}, "agent_1")
        result2 = await tool_manager.execute_tool("tool2", {"data": "test2"}, "agent_1")

        assert result1 == '{"tool": "1", "data": "test1"}'
        assert result2 == '{"tool": "2", "data": "test2"}'

    @pytest.mark.asyncio
    async def test_tool_execution_with_retry(self):
        """Test tool execution with retry logic"""
        # Define flaky tool
        call_count = 0

        @tool(name="flaky_tool", description="Flaky tool for retry test")
        def flaky_tool(data: str) -> dict:
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return {"result": f"success_after_{call_count}_calls"}

        # Get tool manager
        tool_manager = get_tool_manager()

        # Execute tool with retry
        result = await tool_manager.execute_tool_with_retry(
            "flaky_tool",
            {"data": "test"},
            "agent_1",
            max_retries=3
        )

        assert result == '{"result": "success_after_3_calls"}'
        assert call_count == 3
```

### **2. Tool Routing Tests**

```python
# tests/core/mcp/test_routing.py
import pytest
import asyncio
from agenthub.core.mcp import get_tool_manager
from agenthub.core.tools import tool

class TestToolRouting:
    @pytest.mark.asyncio
    async def test_tool_routing_per_agent(self):
        """Test tool routing per agent"""
        # Define tools
        @tool(name="agent1_tool", description="Tool for agent 1")
        def agent1_tool(data: str) -> dict:
            return {"agent": "1", "data": data}

        @tool(name="agent2_tool", description="Tool for agent 2")
        def agent2_tool(data: str) -> dict:
            return {"agent": "2", "data": data}

        # Get tool manager
        tool_manager = get_tool_manager()

        # Assign different tools to different agents
        tool_manager.assign_tools_to_agent("agent_1", ["agent1_tool"])
        tool_manager.assign_tools_to_agent("agent_2", ["agent2_tool"])

        # Execute tools
        result1 = await tool_manager.execute_tool("agent1_tool", {"data": "test"}, "agent_1")
        result2 = await tool_manager.execute_tool("agent2_tool", {"data": "test"}, "agent_2")

        assert result1 == '{"agent": "1", "data": "test"}'
        assert result2 == '{"agent": "2", "data": "test"}'

        # Test cross-agent access denial
        with pytest.raises(ToolAccessDeniedError):
            await tool_manager.execute_tool("agent1_tool", {"data": "test"}, "agent_2")

    @pytest.mark.asyncio
    async def test_tool_routing_with_shared_tools(self):
        """Test tool routing with shared tools"""
        # Define shared tool
        @tool(name="shared_tool", description="Shared tool")
        def shared_tool(data: str) -> dict:
            return {"shared": True, "data": data}

        # Get tool manager
        tool_manager = get_tool_manager()

        # Assign shared tool to multiple agents
        tool_manager.assign_tools_to_agent("agent_1", ["shared_tool"])
        tool_manager.assign_tools_to_agent("agent_2", ["shared_tool"])

        # Both agents should be able to use the tool
        result1 = await tool_manager.execute_tool("shared_tool", {"data": "test1"}, "agent_1")
        result2 = await tool_manager.execute_tool("shared_tool", {"data": "test2"}, "agent_2")

        assert result1 == '{"shared": true, "data": "test1"}'
        assert result2 == '{"shared": true, "data": "test2"}'
```

## ⚡ **Concurrency Tests**

### **1. Concurrent Tool Execution Tests**

```python
# tests/core/mcp/test_concurrency.py
import pytest
import asyncio
import threading
from agenthub.core.mcp import get_tool_manager
from agenthub.core.tools import tool

class TestConcurrency:
    @pytest.mark.asyncio
    async def test_concurrent_tool_execution(self):
        """Test concurrent tool execution"""
        # Define test tool
        @tool(name="concurrent_tool", description="Concurrent execution test")
        def concurrent_tool(data: str) -> dict:
            return {"result": data, "thread": threading.current_thread().ident}

        # Get tool manager
        tool_manager = get_tool_manager()
        tool_manager.assign_tools_to_agent("agent_1", ["concurrent_tool"])

        # Execute tool concurrently
        tasks = []
        for i in range(10):
            task = tool_manager.execute_tool(
                "concurrent_tool",
                {"data": f"test_{i}"},
                "agent_1"
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        # All executions should succeed
        assert len(results) == 10
        for i, result in enumerate(results):
            assert f"test_{i}" in result

    @pytest.mark.asyncio
    async def test_concurrent_tool_assignment(self):
        """Test concurrent tool assignment"""
        tool_manager = get_tool_manager()

        # Assign tools concurrently
        tasks = []
        for i in range(10):
            task = asyncio.create_task(
                tool_manager.assign_tools_to_agent(f"agent_{i}", [f"tool_{i}"])
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        # All assignments should succeed
        assert len(results) == 10
        for i, result in enumerate(results):
            assert f"tool_{i}" in result

    @pytest.mark.asyncio
    async def test_concurrent_tool_execution_with_queue(self):
        """Test concurrent tool execution with queue"""
        from agenthub.core.mcp import get_execution_queue

        # Define test tool
        @tool(name="queued_tool", description="Queued execution test")
        def queued_tool(data: str) -> dict:
            return {"result": data, "queued": True}

        # Get execution queue
        execution_queue = get_execution_queue()

        # Enqueue multiple executions
        execution_ids = []
        for i in range(5):
            execution_id = await execution_queue.enqueue_tool_execution(
                "queued_tool",
                {"data": f"test_{i}"},
                "agent_1"
            )
            execution_ids.append(execution_id)

        # Process queue
        await execution_queue._process_queue()

        # All executions should be processed
        assert execution_queue.queue.qsize() == 0
```

## 🚨 **Error Handling Tests**

### **1. Tool Execution Error Tests**

```python
# tests/core/mcp/test_errors.py
import pytest
import asyncio
from agenthub.core.mcp import get_tool_manager
from agenthub.core.mcp.exceptions import (
    ToolExecutionError,
    ToolAccessDeniedError,
    ToolTimeoutError
)
from agenthub.core.tools import tool

class TestErrorHandling:
    @pytest.mark.asyncio
    async def test_tool_execution_error(self):
        """Test tool execution error handling"""
        # Define error tool
        @tool(name="error_tool", description="Tool that raises error")
        def error_tool(data: str) -> dict:
            raise Exception("Tool execution failed")

        # Get tool manager
        tool_manager = get_tool_manager()
        tool_manager.assign_tools_to_agent("agent_1", ["error_tool"])

        # Execute tool should raise error
        with pytest.raises(ToolExecutionError):
            await tool_manager.execute_tool("error_tool", {"data": "test"}, "agent_1")

    @pytest.mark.asyncio
    async def test_tool_access_denied_error(self):
        """Test tool access denied error"""
        # Define tool
        @tool(name="restricted_tool", description="Restricted tool")
        def restricted_tool(data: str) -> dict:
            return {"result": data}

        # Get tool manager
        tool_manager = get_tool_manager()

        # Don't assign tool to agent
        tool_manager.assign_tools_to_agent("agent_1", [])

        # Execute tool should raise access denied error
        with pytest.raises(ToolAccessDeniedError):
            await tool_manager.execute_tool("restricted_tool", {"data": "test"}, "agent_1")

    @pytest.mark.asyncio
    async def test_tool_timeout_error(self):
        """Test tool timeout error"""
        from agenthub.core.mcp import get_execution_queue

        # Define slow tool
        @tool(name="slow_tool", description="Slow tool")
        def slow_tool(data: str) -> dict:
            import time
            time.sleep(2.0)  # Longer than timeout
            return {"result": data}

        # Get execution queue
        execution_queue = get_execution_queue()

        # Enqueue execution with short timeout
        execution_id = await execution_queue.enqueue_tool_execution(
            "slow_tool",
            {"data": "test"},
            "agent_1"
        )

        # Process queue should raise timeout error
        with pytest.raises(ToolTimeoutError):
            await execution_queue._process_queue()
```

## 📊 **Performance Tests**

### **1. Tool Execution Performance Tests**

```python
# tests/core/mcp/test_performance.py
import pytest
import asyncio
import time
from agenthub.core.mcp import get_tool_manager
from agenthub.core.tools import tool

class TestPerformance:
    @pytest.mark.asyncio
    async def test_tool_execution_performance(self):
        """Test tool execution performance"""
        # Define performance test tool
        @tool(name="perf_tool", description="Performance test tool")
        def perf_tool(data: str) -> dict:
            return {"result": data}

        # Get tool manager
        tool_manager = get_tool_manager()
        tool_manager.assign_tools_to_agent("agent_1", ["perf_tool"])

        # Measure execution time
        start_time = time.time()

        # Execute tool 100 times
        for i in range(100):
            result = await tool_manager.execute_tool(
                "perf_tool",
                {"data": f"test_{i}"},
                "agent_1"
            )
            assert result == f'{{"result": "test_{i}"}}'

        end_time = time.time()
        execution_time = end_time - start_time

        # Should complete in reasonable time
        assert execution_time < 5.0  # 5 seconds for 100 executions

    @pytest.mark.asyncio
    async def test_concurrent_tool_execution_performance(self):
        """Test concurrent tool execution performance"""
        # Define performance test tool
        @tool(name="concurrent_perf_tool", description="Concurrent performance test tool")
        def concurrent_perf_tool(data: str) -> dict:
            return {"result": data}

        # Get tool manager
        tool_manager = get_tool_manager()
        tool_manager.assign_tools_to_agent("agent_1", ["concurrent_perf_tool"])

        # Measure concurrent execution time
        start_time = time.time()

        # Execute tool concurrently
        tasks = []
        for i in range(50):
            task = tool_manager.execute_tool(
                "concurrent_perf_tool",
                {"data": f"test_{i}"},
                "agent_1"
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        end_time = time.time()
        execution_time = end_time - start_time

        # Should complete in reasonable time
        assert execution_time < 3.0  # 3 seconds for 50 concurrent executions
        assert len(results) == 50
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
pytest tests/core/mcp/

# Run specific test categories
pytest tests/core/mcp/test_manager.py
pytest tests/core/mcp/test_fastmcp_integration.py
pytest tests/core/mcp/test_concurrency.py

# Run with coverage
pytest tests/core/mcp/ --cov=agenthub.core.mcp --cov-report=html
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
