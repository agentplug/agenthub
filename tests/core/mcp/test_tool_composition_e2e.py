"""Composition contract, proven without mocks: a function registered via
@tool becomes visible to an agent and executable — over the MCP protocol.

Uses mcp.shared.memory.create_connected_server_and_client_session, which
runs the real FastMCP server in-process over memory streams: zero network,
zero subprocess, zero mocked tool logic. The only stub is SSE metadata
discovery, disabled so the test never probes localhost:8000.

Deliberately not covered: AgentToolManager.execute_tool's stdio-subprocess
path, which builds a fresh empty registry in the child process and cannot
see @tool functions (known defect; see ARCHITECTURE.md "Known
limitations").
"""

import pytest
from mcp.shared.memory import create_connected_server_and_client_session

from agenthub.core.mcp.agent_tool_manager import AgentToolManager
from agenthub.core.tools.decorator import tool
from agenthub.core.tools.registry import ToolRegistry


@pytest.fixture
def clean_registry(monkeypatch):
    """Fresh in-memory ToolRegistry wired into every lookup path.

    Three references must move together or the pieces disagree about
    which registry exists: the singleton slot (ToolRegistry._instance),
    the module global returned by get_tool_registry() (used by
    AgentToolManager), and the reference the @tool decorator captured at
    import time (decorator._registry).
    """
    import agenthub.core.tools.decorator as decorator_module
    import agenthub.core.tools.registry as registry_module

    original_instance = ToolRegistry._instance
    ToolRegistry._instance = None
    fresh = ToolRegistry()
    monkeypatch.setattr(registry_module, "_registry", fresh)
    monkeypatch.setattr(decorator_module, "_registry", fresh)
    monkeypatch.setattr(ToolRegistry, "_discover_mcp_tool_metadata", lambda self: [])
    yield fresh
    # Restore the singleton slot to the SAME object the decorator's
    # import-time reference points at. Leaving None here makes the next
    # ToolRegistry() a different object than decorator._registry, and
    # downstream tests that clear one while registering into the other
    # fail with phantom ToolNameConflictError.
    ToolRegistry._instance = original_instance


@pytest.mark.integration
async def test_tool_composition_round_trip_over_mcp(clean_registry):
    @tool(name="greet_e2e", description="Greet an agent")
    def greet(name: str) -> str:
        return f"hello {name}"

    # Agent-side access computation against the same real registry
    manager = AgentToolManager()
    manager.assign_tools_to_agent("agent-1", ["greet_e2e"])
    assert manager.has_tool_access("agent-1", "greet_e2e")
    assert "greet_e2e" in manager.get_all_available_tools("agent-1")

    # Metadata was extracted from the function signature
    metadata = clean_registry.get_tool_metadata("greet_e2e")
    assert metadata.description == "Greet an agent"
    assert "name" in metadata.parameters

    # In-process execution leg (what AgentWrapper.execute_tool uses)
    assert clean_registry.execute_tool("greet_e2e", {"name": "agent-1"}) == (
        "hello agent-1"
    )

    # MCP protocol leg: visibility and execution through a real
    # client<->server session
    server = clean_registry.mcp_manager.get_server()
    async with create_connected_server_and_client_session(server) as session:
        listed = await session.list_tools()
        assert "greet_e2e" in {t.name for t in listed.tools}
        result = await session.call_tool("greet_e2e", {"name": "agent-1"})
        assert result.content[0].text == "hello agent-1"
