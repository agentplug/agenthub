"""Async tool executor with proper resource management."""

import asyncio
import logging
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from ...monitoring.metrics import record_metric, record_tool_execution
from ..tools import ToolAccessDeniedError, ToolNotFoundError, get_tool_registry
from .connection_manager import get_connection_pool

logger = logging.getLogger(__name__)


class AsyncToolExecutor:
    """Async tool executor with proper resource management and monitoring."""

    def __init__(self, agent_id: str) -> None:
        """Initialize async tool executor.

        Args:
            agent_id: ID of the agent using this executor
        """
        self.agent_id = agent_id
        self.tool_registry = get_tool_registry()
        self.connection_pool = get_connection_pool()

    async def execute_tool(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Execute a tool with proper error handling and monitoring.

        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments to pass to the tool

        Returns:
            JSON string result from tool execution

        Raises:
            ToolNotFoundError: If tool doesn't exist
            ToolAccessDeniedError: If agent doesn't have access to tool
        """
        start_time = time.time()
        success = False
        error_type = None

        try:
            # Validate tool access
            if not self.tool_registry.can_agent_access_tool(self.agent_id, tool_name):
                raise ToolAccessDeniedError(
                    f"Agent '{self.agent_id}' does not have access to "
                    f"tool '{tool_name}'"
                )

            # Check if tool exists
            available_tools = self.tool_registry.get_available_tools()
            if tool_name not in available_tools:
                raise ToolNotFoundError(f"Tool '{tool_name}' not found in registry")

            # Execute tool with connection pooling
            async with self.connection_pool.get_connection() as client:
                result = await client.call_tool(tool_name, arguments)

                if result and hasattr(result, "content") and len(result.content) > 0:
                    response = (
                        result.content[0].text
                        if hasattr(result.content[0], "text")
                        else str(result.content[0])
                    )
                    success = True
                    return response
                else:
                    return '{"error": "No result returned from tool"}'

        except ToolNotFoundError:
            error_type = "ToolNotFoundError"
            raise
        except ToolAccessDeniedError:
            error_type = "ToolAccessDeniedError"
            raise
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"Tool execution failed for {tool_name}: {e}")
            return (
                f'{{"error": "Tool execution failed: {str(e)}", '
                f'"tool_name": "{tool_name}", "error_type": "{error_type}"}}'
            )

        finally:
            # Record metrics
            execution_time = time.time() - start_time
            record_tool_execution(
                tool_name, self.agent_id, execution_time, success, error_type
            )
            record_metric(
                "tool_execution_time",
                execution_time,
                {"tool_name": tool_name, "agent_id": self.agent_id},
            )

    async def execute_tool_with_retry(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ) -> str:
        """Execute a tool with retry logic.

        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments to pass to the tool
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds

        Returns:
            JSON string result from tool execution
        """
        last_error = None

        for attempt in range(max_retries + 1):
            try:
                return await self.execute_tool(tool_name, arguments)
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    logger.warning(
                        f"Tool execution attempt {attempt + 1} failed for "
                        f"{tool_name}: {e}. Retrying..."
                    )
                    await asyncio.sleep(
                        retry_delay * (2**attempt)
                    )  # Exponential backoff
                else:
                    logger.error(
                        f"Tool execution failed after {max_retries + 1} attempts "
                        f"for {tool_name}: {e}"
                    )

        # If we get here, all retries failed
        if last_error is not None:
            raise last_error
        else:
            raise RuntimeError(
                f"Tool execution failed for {tool_name} "
                f"after {max_retries + 1} attempts"
            )

    async def execute_multiple_tools(
        self, tool_requests: list[dict[str, Any]]
    ) -> list[str]:
        """Execute multiple tools concurrently.

        Args:
            tool_requests: List of tool execution requests
                Each request should have 'tool_name' and 'arguments' keys

        Returns:
            List of results from tool executions
        """
        tasks = []
        for request in tool_requests:
            task = self.execute_tool(request["tool_name"], request["arguments"])
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to error strings
        processed_results: list[str] = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append(
                    f'{{"error": "Tool execution failed: {str(result)}"}}'
                )
            else:
                processed_results.append(str(result))

        return processed_results

    @asynccontextmanager
    async def tool_execution_context(
        self, tool_name: str, arguments: dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """Context manager for tool execution with proper resource management.

        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments to pass to the tool

        Yields:
            Tool execution result
        """
        result = None
        try:
            result = await self.execute_tool(tool_name, arguments)
            yield result
        finally:
            # Any cleanup logic can go here
            pass


# Global async tool executor factory
_async_executors: dict[str, AsyncToolExecutor] = {}


def get_async_tool_executor(agent_id: str) -> AsyncToolExecutor:
    """Get or create an async tool executor for an agent.

    Args:
        agent_id: ID of the agent

    Returns:
        AsyncToolExecutor instance for the agent
    """
    if agent_id not in _async_executors:
        _async_executors[agent_id] = AsyncToolExecutor(agent_id)
    return _async_executors[agent_id]


async def cleanup_async_executors() -> None:
    """Cleanup all async tool executors."""
    global _async_executors
    _async_executors.clear()
