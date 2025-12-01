"""Unit tests for A2A Protocol Adapter."""

from agenthub.core.communication.protocol import (
    A2AAction,
    A2AAgentCard,
    A2AMessageAdapter,
    A2AMessageType,
    A2AParameter,
    A2AResultMessage,
    A2AStatusMessage,
    A2ATaskMessage,
    A2ATaskStatus,
    create_analysis_task,
    create_generation_task,
    create_search_task,
)


def test_a2a_message_type_enum():
    """Test A2A message type enum."""
    assert A2AMessageType.TASK.value == "task"
    assert A2AMessageType.STATUS.value == "status"
    assert A2AMessageType.RESULT.value == "result"
    assert A2AMessageType.ERROR.value == "error"
    assert A2AMessageType.AGENT_CARD.value == "agent_card"


def test_a2a_task_status_enum():
    """Test A2A task status enum."""
    assert A2ATaskStatus.PENDING.value == "pending"
    assert A2ATaskStatus.RUNNING.value == "running"
    assert A2ATaskStatus.COMPLETED.value == "completed"
    assert A2ATaskStatus.FAILED.value == "failed"
    assert A2ATaskStatus.CANCELLED.value == "cancelled"


def test_a2a_parameter():
    """Test A2A parameter dataclass."""
    param = A2AParameter(
        name="content",
        type="string",
        description="Content to analyze",
        required=True,
        default=None,
    )

    param_dict = param.to_dict()
    assert param_dict["name"] == "content"
    assert param_dict["type"] == "string"
    assert param_dict["description"] == "Content to analyze"
    assert param_dict["required"] is True


def test_a2a_action():
    """Test A2A action dataclass."""
    param1 = A2AParameter(name="query", type="string", description="Search query")
    param2 = A2AParameter(
        name="limit", type="integer", description="Result limit", default=10
    )

    action = A2AAction(
        name="search",
        description="Search for content",
        parameters=[param1, param2],
        returns={"type": "array"},
    )

    action_dict = action.to_dict()
    assert action_dict["name"] == "search"
    assert action_dict["description"] == "Search for content"
    assert len(action_dict["parameters"]) == 2
    assert action_dict["returns"]["type"] == "array"


def test_a2a_action_from_agent_method():
    """Test creating A2A action from AgentHub method info."""
    method_info = {
        "description": "Analyze content",
        "parameters": {
            "content": {
                "type": "string",
                "description": "Content to analyze",
                "required": True,
            },
            "depth": {"type": "integer", "default": 1},
        },
        "return_type": "dict",
    }

    action = A2AAction.from_agent_method("analyze", method_info)
    assert action.name == "analyze"
    assert action.description == "Analyze content"
    assert len(action.parameters) == 2
    assert action.returns["type"] == "dict"


def test_a2a_agent_card():
    """Test A2A agent card."""
    card = A2AAgentCard(
        id="test-agent",
        name="Test Agent",
        description="A test agent",
        version="1.0.0",
        capabilities=["search", "analyze"],
        actions=[],
        metadata={"author": "test"},
    )

    card_dict = card.to_dict()
    assert card_dict["id"] == "test-agent"
    assert card_dict["name"] == "Test Agent"
    assert card_dict["version"] == "1.0.0"
    assert len(card_dict["capabilities"]) == 2
    assert card_dict["metadata"]["author"] == "test"


def test_a2a_agent_card_from_metadata():
    """Test creating agent card from AgentHub metadata."""
    agent_metadata = {
        "agent_id": "research-agent",
        "name": "Research Agent",
        "description": "Research and analysis agent",
        "version": "2.0.0",
        "interface": {
            "search": {
                "description": "Search for information",
                "parameters": {"query": "string"},
                "return_type": "list",
            }
        },
        "assigned_tools": ["web_search", "calculator"],
        "knowledge_available": True,
        "namespace": "agentplug",
        "author": "agenthub",
    }

    card = A2AAgentCard.from_agent_metadata(agent_metadata)
    assert card.id == "research-agent"
    assert card.name == "Research Agent"
    assert card.version == "2.0.0"
    assert len(card.actions) == 1
    assert card.actions[0].name == "search"
    assert "tool:web_search" in card.capabilities
    assert "tool:calculator" in card.capabilities
    assert "knowledge:available" in card.capabilities


def test_a2a_task_message():
    """Test A2A task message."""
    task = A2ATaskMessage.create(
        source="agent1",
        target="agent2",
        action="analyze_content",
        parameters={"content": "test"},
    )

    task_dict = task.to_dict()
    assert task_dict["source"] == "agent1"
    assert task_dict["target"] == "agent2"
    assert task_dict["action"] == "analyze_content"
    assert task_dict["parameters"]["content"] == "test"
    assert "id" in task_dict
    assert "created_at" in task_dict


def test_a2a_status_message():
    """Test A2A status message."""
    status = A2AStatusMessage(
        task_id="task-123", status="running", progress=0.5, message="Processing..."
    )

    status_dict = status.to_dict()
    assert status_dict["task_id"] == "task-123"
    assert status_dict["status"] == "running"
    assert status_dict["progress"] == 0.5
    assert status_dict["message"] == "Processing..."


def test_a2a_result_message():
    """Test A2A result message."""
    result = A2AResultMessage(
        task_id="task-123",
        status="completed",
        result={"output": "success"},
        metadata={"duration": 5.2},
    )

    result_dict = result.to_dict()
    assert result_dict["task_id"] == "task-123"
    assert result_dict["status"] == "completed"
    assert result_dict["result"]["output"] == "success"
    assert result_dict["metadata"]["duration"] == 5.2


def test_create_task_message():
    """Test creating task message with adapter."""
    message = A2AMessageAdapter.create_task_message(
        source="agent1", target="agent2", action="search", parameters={"query": "test"}
    )

    assert message["type"] == A2AMessageType.TASK.value
    assert message["data"]["source"] == "agent1"
    assert message["data"]["target"] == "agent2"
    assert message["data"]["action"] == "search"
    assert "protocol_version" in message


def test_create_status_message():
    """Test creating status message with adapter."""
    message = A2AMessageAdapter.create_status_message(
        task_id="task-123", status="running", progress=0.75
    )

    assert message["type"] == A2AMessageType.STATUS.value
    assert message["data"]["task_id"] == "task-123"
    assert message["data"]["status"] == "running"
    assert message["data"]["progress"] == 0.75


def test_create_result_message():
    """Test creating result message with adapter."""
    message = A2AMessageAdapter.create_result_message(
        task_id="task-123", status="completed", result={"data": "output"}
    )

    assert message["type"] == A2AMessageType.RESULT.value
    assert message["data"]["task_id"] == "task-123"
    assert message["data"]["status"] == "completed"
    assert message["data"]["result"]["data"] == "output"


def test_create_agent_card():
    """Test creating agent card with adapter."""
    agent_metadata = {
        "agent_id": "test-agent",
        "name": "Test Agent",
        "description": "Test",
        "version": "1.0.0",
        "interface": {},
    }

    message = A2AMessageAdapter.create_agent_card(agent_metadata)

    assert message["type"] == A2AMessageType.AGENT_CARD.value
    assert message["data"]["id"] == "test-agent"
    assert message["data"]["name"] == "Test Agent"


def test_validate_message():
    """Test message validation."""
    # Valid task message
    valid_task = {
        "type": "task",
        "data": {
            "id": "123",
            "source": "agent1",
            "target": "agent2",
            "action": "test",
            "parameters": {},
        },
    }
    assert A2AMessageAdapter.validate_message(valid_task) is True

    # Valid result message
    valid_result = {"type": "result", "data": {"task_id": "123", "status": "completed"}}
    assert A2AMessageAdapter.validate_message(valid_result) is True

    # Invalid - missing type
    invalid1 = {"data": {}}
    assert A2AMessageAdapter.validate_message(invalid1) is False

    # Invalid - missing data
    invalid2 = {"type": "task"}
    assert A2AMessageAdapter.validate_message(invalid2) is False

    # Invalid - missing required fields
    invalid3 = {
        "type": "task",
        "data": {"id": "123"},  # Missing source, target, action, parameters
    }
    assert A2AMessageAdapter.validate_message(invalid3) is False


def test_format_conversion():
    """Test conversion between A2A and AgentHub formats."""
    # AgentHub -> A2A
    agenthub_msg = {
        "type": "agent_request",
        "data": {
            "request_id": "req-123",
            "from_agent": "agent1",
            "to_agent": "agent2",
            "method": "search",
            "parameters": {"query": "test"},
        },
    }

    a2a_msg = A2AMessageAdapter.from_agenthub_format(agenthub_msg)
    assert a2a_msg["type"] == "task"
    assert a2a_msg["data"]["source"] == "agent1"
    assert a2a_msg["data"]["target"] == "agent2"
    assert a2a_msg["data"]["action"] == "search"

    # A2A -> AgentHub
    converted_back = A2AMessageAdapter.to_agenthub_format(a2a_msg)
    assert converted_back["type"] == "agent_request"
    assert converted_back["data"]["from_agent"] == "agent1"
    assert converted_back["data"]["to_agent"] == "agent2"
    assert converted_back["data"]["method"] == "search"


def test_utility_functions():
    """Test utility functions for common task types."""
    # Analysis task
    analysis = create_analysis_task("agent1", "agent2", "test content", "detailed")
    assert analysis["data"]["action"] == "analyze_content"
    assert analysis["data"]["parameters"]["content"] == "test content"
    assert analysis["data"]["parameters"]["analysis_type"] == "detailed"

    # Generation task
    generation = create_generation_task("agent1", "agent2", "test prompt", "json")
    assert generation["data"]["action"] == "generate_content"
    assert generation["data"]["parameters"]["prompt"] == "test prompt"
    assert generation["data"]["parameters"]["format"] == "json"

    # Search task
    search = create_search_task("agent1", "agent2", "test query", {"limit": 10})
    assert search["data"]["action"] == "search"
    assert search["data"]["parameters"]["query"] == "test query"
    assert search["data"]["parameters"]["filters"]["limit"] == 10
