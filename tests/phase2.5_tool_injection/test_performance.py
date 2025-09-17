"""Performance tests for Phase 2.5 tool injection functionality."""

import threading
import time
from unittest.mock import patch

from agenthub.core.tools.decorator import tool
from agenthub.core.tools.registry import ToolRegistry


class TestToolInjectionPerformance:
    """Performance tests for tool injection functionality."""

    def setup_method(self):
        """Set up test environment before each test."""
        # Reset the registry for each test
        ToolRegistry._instance = None
        self.registry = ToolRegistry()

        # Patch the global registry to use our test instance
        self.registry_patcher = patch(
            "agenthub.core.tools.registry._registry", self.registry
        )
        self.registry_patcher.start()

        # Also patch the decorator's registry reference
        self.decorator_patcher = patch(
            "agenthub.core.tools.decorator._registry", self.registry
        )
        self.decorator_patcher.start()

    def teardown_method(self):
        """Clean up after each test."""
        if hasattr(self, "registry_patcher"):
            self.registry_patcher.stop()
        if hasattr(self, "decorator_patcher"):
            self.decorator_patcher.stop()

    def test_tool_registration_performance(self):
        """Test tool registration performance with many tools."""
        start_time = time.time()

        # Register 100 tools
        for i in range(100):

            @tool(name=f"perf_tool_{i}", description=f"Performance test tool {i}")
            def perf_tool(value: int = i) -> int:
                return value * 2

        end_time = time.time()
        registration_time = end_time - start_time

        # Should complete in reasonable time (less than 5 seconds)
        assert (
            registration_time < 5.0
        ), f"Tool registration took {registration_time:.2f} seconds"

        # Verify all tools are registered (including built-in tools from MCP discovery)
        available_tools = self.registry.get_available_tools()
        assert len(available_tools) >= 100  # At least 100 tools should be registered
        # Verify our performance tools are there
        perf_tools = [tool for tool in available_tools if tool.startswith("perf_tool_")]
        assert len(perf_tools) == 100

    def test_tool_execution_performance(self):
        """Test tool execution performance."""

        # Register a simple tool
        @tool(name="perf_exec_tool", description="Performance execution tool")
        def perf_exec_tool(value: int) -> int:
            return value * 2

        # Measure execution time for 1000 calls
        start_time = time.time()

        for i in range(1000):
            result = self.registry.execute_tool("perf_exec_tool", {"value": i})
            assert result == i * 2

        end_time = time.time()
        execution_time = end_time - start_time

        # Should complete in reasonable time (less than 1 second)
        assert execution_time < 1.0, f"Tool execution took {execution_time:.2f} seconds"

    def test_tool_metadata_retrieval_performance(self):
        """Test tool metadata retrieval performance."""
        # Register 50 tools
        for i in range(50):

            @tool(name=f"metadata_tool_{i}", description=f"Metadata tool {i}")
            def metadata_tool(param: str = f"default_{i}") -> str:
                return f"result: {param}"

        # Measure metadata retrieval time
        start_time = time.time()

        for i in range(50):
            metadata = self.registry.get_tool_metadata(f"metadata_tool_{i}")
            assert metadata is not None
            assert metadata.name == f"metadata_tool_{i}"

        end_time = time.time()
        retrieval_time = end_time - start_time

        # Should complete in reasonable time (less than 0.5 seconds)
        assert (
            retrieval_time < 0.5
        ), f"Metadata retrieval took {retrieval_time:.2f} seconds"

    def test_concurrent_tool_registration_performance(self):
        """Test concurrent tool registration performance."""
        results = []
        errors = []

        def register_tool(tool_id: int):
            try:

                @tool(
                    name=f"concurrent_perf_tool_{tool_id}",
                    description=f"Concurrent tool {tool_id}",
                )
                def concurrent_tool(value: int) -> int:
                    return value * 2

                results.append(tool_id)
            except Exception as e:
                errors.append((tool_id, e))

        # Measure concurrent registration time
        start_time = time.time()

        # Create 20 threads registering tools simultaneously
        threads = []
        for i in range(20):
            thread = threading.Thread(target=register_tool, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        end_time = time.time()
        concurrent_time = end_time - start_time

        # Should complete without errors
        assert len(errors) == 0, f"Errors during concurrent registration: {errors}"
        assert len(results) == 20

        # Should complete in reasonable time (less than 2 seconds)
        assert (
            concurrent_time < 2.0
        ), f"Concurrent registration took {concurrent_time:.2f} seconds"

    def test_concurrent_tool_execution_performance(self):
        """Test concurrent tool execution performance."""

        # Register a tool
        @tool(name="concurrent_exec_tool", description="Concurrent execution tool")
        def concurrent_exec_tool(value: int) -> int:
            time.sleep(0.001)  # Simulate some work
            return value * 2

        results = []
        errors = []

        def execute_tool(tool_id: int):
            try:
                result = self.registry.execute_tool(
                    "concurrent_exec_tool", {"value": tool_id}
                )
                results.append((tool_id, result))
            except Exception as e:
                errors.append((tool_id, e))

        # Measure concurrent execution time
        start_time = time.time()

        # Create 50 threads executing tools simultaneously
        threads = []
        for i in range(50):
            thread = threading.Thread(target=execute_tool, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        end_time = time.time()
        concurrent_time = end_time - start_time

        # Should complete without errors
        assert len(errors) == 0, f"Errors during concurrent execution: {errors}"
        assert len(results) == 50

        # Verify results
        for tool_id, result in results:
            assert result == tool_id * 2

        # Should complete in reasonable time (less than 2 seconds)
        assert (
            concurrent_time < 2.0
        ), f"Concurrent execution took {concurrent_time:.2f} seconds"

    def test_memory_usage_stability(self):
        """Test memory usage stability with many tools."""
        import os

        import psutil

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Register 200 tools
        for i in range(200):

            @tool(name=f"memory_tool_{i}", description=f"Memory test tool {i}")
            def memory_tool(param: str = f"default_{i}") -> str:
                return f"result: {param}"

        # Execute tools multiple times
        for _ in range(10):
            for i in range(200):
                result = self.registry.execute_tool(
                    f"memory_tool_{i}", {"param": f"test_{i}"}
                )
                assert result == f"result: test_{i}"

        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 50MB)
        assert memory_increase < 50, f"Memory increased by {memory_increase:.2f}MB"

    def test_tool_registry_lookup_performance(self):
        """Test tool registry lookup performance."""
        # Register 1000 tools
        for i in range(1000):

            @tool(name=f"lookup_tool_{i}", description=f"Lookup tool {i}")
            def lookup_tool(value: int = i) -> int:
                return value

        # Measure lookup time
        start_time = time.time()

        # Perform 1000 lookups (more efficient approach)
        available_tools = self.registry.get_available_tools()  # Get once
        for i in range(1000):
            tool_name = f"lookup_tool_{i}"
            assert tool_name in available_tools
            metadata = self.registry.get_tool_metadata(tool_name)
            assert metadata is not None

        end_time = time.time()
        lookup_time = end_time - start_time

        # Should complete in reasonable time (less than 5 seconds)
        assert lookup_time < 5.0, f"Tool lookup took {lookup_time:.2f} seconds"

    def test_agent_tool_assignment_performance(self):
        """Test agent tool assignment performance."""
        # Register 100 tools
        for i in range(100):

            @tool(name=f"assignment_tool_{i}", description=f"Assignment tool {i}")
            def assignment_tool(value: int = i) -> int:
                return value

        # Measure assignment time
        start_time = time.time()

        # Assign tools to 50 agents
        for agent_id in range(50):
            tool_names = [f"assignment_tool_{i}" for i in range(agent_id % 10 + 1)]
            self.registry.assign_tools_to_agent(f"agent_{agent_id}", tool_names)

        end_time = time.time()
        assignment_time = end_time - start_time

        # Should complete in reasonable time (less than 2 seconds)
        assert (
            assignment_time < 2.0
        ), f"Tool assignment took {assignment_time:.2f} seconds"

        # Verify assignments
        for agent_id in range(50):
            agent_tools = self.registry.get_agent_tools(f"agent_{agent_id}")
            assert len(agent_tools) == agent_id % 10 + 1

    def test_tool_context_generation_performance(self):
        """Test tool context generation performance."""
        # Register 50 tools with complex metadata
        for i in range(50):

            @tool(
                name=f"context_tool_{i}",
                description=f"Context tool {i} with complex metadata",
            )
            def context_tool(
                param1: str = f"default1_{i}", param2: int = i, param3: bool = True
            ) -> dict:
                return {"param1": param1, "param2": param2, "param3": param3}

        # Assign tools to agent
        tool_names = [f"context_tool_{i}" for i in range(50)]
        self.registry.assign_tools_to_agent("context_agent", tool_names)

        # Measure context generation time
        start_time = time.time()

        # Generate context 100 times
        for _ in range(100):
            agent_tools = self.registry.get_agent_tools("context_agent")
            tool_context = {
                "available_tools": agent_tools,
                "tool_descriptions": {},
                "tool_usage_examples": {},
                "tool_parameters": {},
                "tool_return_types": {},
                "tool_namespaces": {},
            }

            for tool_name in agent_tools:
                metadata = self.registry.get_tool_metadata(tool_name)
                tool_context["tool_descriptions"][tool_name] = metadata.description
                tool_context["tool_usage_examples"][tool_name] = metadata.examples
                tool_context["tool_parameters"][tool_name] = metadata.parameters
                tool_context["tool_return_types"][tool_name] = metadata.return_type
                tool_context["tool_namespaces"][tool_name] = metadata.namespace

        end_time = time.time()
        context_time = end_time - start_time

        # Should complete in reasonable time (less than 2 seconds)
        assert (
            context_time < 2.0
        ), f"Tool context generation took {context_time:.2f} seconds"

    def test_registry_cleanup_performance(self):
        """Test registry cleanup performance."""
        # Register 500 tools
        for i in range(500):

            @tool(name=f"cleanup_tool_{i}", description=f"Cleanup tool {i}")
            def cleanup_tool(value: int = i) -> int:
                return value

        # Assign tools to 100 agents
        for agent_id in range(100):
            tool_names = [f"cleanup_tool_{i}" for i in range(agent_id % 5 + 1)]
            self.registry.assign_tools_to_agent(f"cleanup_agent_{agent_id}", tool_names)

        # Measure cleanup time
        start_time = time.time()

        self.registry.cleanup()

        end_time = time.time()
        cleanup_time = end_time - start_time

        # Should complete in reasonable time (less than 0.5 seconds)
        assert cleanup_time < 0.5, f"Registry cleanup took {cleanup_time:.2f} seconds"

        # Verify cleanup (except built-in tools from MCP discovery)
        available_tools = self.registry.get_available_tools()
        cleanup_tools = [
            tool for tool in available_tools if tool.startswith("cleanup_tool_")
        ]
        assert len(cleanup_tools) == 0  # Our test tools should be gone
        assert len(self.registry.agent_tool_access) == 0

    def test_benchmark_tool_registration_scalability(self):
        """Benchmark tool registration scalability."""
        registration_times = []

        # Test with different numbers of tools
        for tool_count in [10, 50, 100, 200, 500]:
            # Clear existing tools for this iteration
            self.registry.cleanup()

            start_time = time.time()

            # Register tools
            for i in range(tool_count):

                @tool(name=f"benchmark_tool_{i}", description=f"Benchmark tool {i}")
                def benchmark_tool(value: int = i) -> int:
                    return value

            end_time = time.time()
            registration_time = end_time - start_time
            registration_times.append((tool_count, registration_time))

            # Verify tools are registered (including built-in tools from MCP discovery)
            available_tools = self.registry.get_available_tools()
            benchmark_tools = [
                tool for tool in available_tools if tool.startswith("benchmark_tool_")
            ]
            assert len(benchmark_tools) == tool_count

        # Print benchmark results
        print("\nTool Registration Benchmark:")
        print("Tools | Time (s) | Time/Tool (ms)")
        print("-" * 40)
        for tool_count, reg_time in registration_times:
            time_per_tool = (reg_time / tool_count) * 1000
            print(f"{tool_count:5d} | {reg_time:8.3f} | {time_per_tool:12.3f}")

        # Verify scalability (time per tool should be relatively constant)
        times_per_tool = [
            reg_time / tool_count for tool_count, reg_time in registration_times
        ]
        max_time_per_tool = max(times_per_tool)
        min_time_per_tool = min(times_per_tool)

        # Variation should not be too large (less than 10x difference)
        assert (
            max_time_per_tool / min_time_per_tool < 10
        ), "Tool registration scalability is poor"
