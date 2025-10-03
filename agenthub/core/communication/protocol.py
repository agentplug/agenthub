"""A2A-compatible message protocol adapter."""

import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ==================== A2A Protocol Constants ====================

# Based on official A2A SDK structure
A2A_VERSION = "1.0.0"
A2A_PROTOCOL = "a2a"


# ==================== Message Types (A2A Compatible) ====================


class A2AMessageType(Enum):
    """A2A message types - aligned with official SDK."""

    TASK = "task"
    STATUS = "status"
    RESULT = "result"
    ERROR = "error"
    AGENT_CARD = "agent_card"


class A2ATaskStatus(Enum):
    """A2A task status - aligned with official SDK."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ==================== Data Classes (A2A Compatible) ====================


@dataclass
class A2AParameter:
    """Parameter definition compatible with A2A SDK."""

    name: str
    type: str
    description: str = ""
    required: bool = True
    default: Any = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        result = {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "required": self.required,
        }
        if self.default is not None:
            result["default"] = self.default
        return result


@dataclass
class A2AAction:
    """
    Action (method) definition compatible with A2A SDK.

    This aligns with the A2A SDK's Action structure.
    """

    name: str
    description: str
    parameters: list[A2AParameter] = field(default_factory=list)
    returns: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": [p.to_dict() for p in self.parameters],
            "returns": self.returns,
        }

    @classmethod
    def from_agent_method(  # type: ignore[misc]
        cls, method_name: str, method_info: dict[str, Any]
    ) -> "A2AAction":
        """Create Action from AgentHub method info."""
        parameters = []
        for param_name, param_info in method_info.get("parameters", {}).items():
            if isinstance(param_info, dict):
                parameters.append(
                    A2AParameter(
                        name=param_name,
                        type=param_info.get("type", "string"),
                        description=param_info.get("description", ""),
                        required=param_info.get("required", True),
                        default=param_info.get("default"),
                    )
                )
            else:
                # Simple type string
                parameters.append(
                    A2AParameter(
                        name=param_name,
                        type=str(param_info),
                        description="",
                        required=True,
                    )
                )

        return cls(
            name=method_name,
            description=method_info.get("description", ""),
            parameters=parameters,
            returns={"type": method_info.get("return_type", "any")},
        )


@dataclass
class A2AAgentCard:
    """
    Agent Card compatible with official A2A SDK.

    This structure aligns with the A2A protocol's Agent Card specification
    and can be converted to/from the official SDK's AgentCard class.
    """

    id: str  # Changed from agent_id to match A2A SDK
    name: str
    description: str
    version: str
    protocol_version: str = A2A_VERSION
    capabilities: list[str] = field(default_factory=list)
    actions: list[A2AAction] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format compatible with A2A SDK."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "protocol_version": self.protocol_version,
            "capabilities": self.capabilities,
            "actions": [action.to_dict() for action in self.actions],
            "metadata": self.metadata,
        }

    @classmethod
    def from_agent_metadata(cls, agent_metadata: dict[str, Any]) -> "A2AAgentCard":  # type: ignore[misc]
        """
        Create Agent Card from AgentHub agent metadata.

        Args:
            agent_metadata: AgentHub agent metadata structure

        Returns:
            A2AAgentCard instance compatible with A2A SDK
        """
        # Convert methods to actions
        actions = []
        for method_name, method_info in agent_metadata.get("interface", {}).items():
            actions.append(A2AAction.from_agent_method(method_name, method_info))

        # Extract capabilities
        capabilities = []
        if agent_metadata.get("assigned_tools"):
            capabilities.extend(
                [f"tool:{tool}" for tool in agent_metadata["assigned_tools"]]
            )
        if agent_metadata.get("knowledge_available"):
            capabilities.append("knowledge:available")

        return cls(
            id=agent_metadata.get("agent_id", "unknown"),
            name=agent_metadata.get("name", "Unknown Agent"),
            description=agent_metadata.get("description", ""),
            version=agent_metadata.get("version", "0.1.0"),
            protocol_version=A2A_VERSION,
            capabilities=capabilities,
            actions=actions,
            metadata={
                "namespace": agent_metadata.get("namespace", ""),
                "author": agent_metadata.get("author", "unknown"),
                "agenthub_version": agent_metadata.get("agenthub_version", "unknown"),
            },
        )

    def to_sdk_format(self) -> dict[str, Any]:
        """
        Convert to format expected by official A2A SDK.

        This can be used when migrating to Phase 4.x with full SDK.
        """
        return self.to_dict()


@dataclass
class A2ATaskMessage:
    """
    Task message compatible with official A2A SDK.

    Field names aligned with A2A SDK's Task class.
    """

    id: str  # Changed from task_id to match A2A SDK
    source: str  # Changed from from_agent to match A2A SDK
    target: str  # Changed from to_agent to match A2A SDK
    action: str  # Changed from task_type to match A2A SDK
    parameters: dict[str, Any]
    context: dict[str, Any] | None = None
    priority: str = "normal"
    timeout: float | None = None
    created_at: float = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = time.time()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format compatible with A2A SDK."""
        result = {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "action": self.action,
            "parameters": self.parameters,
            "created_at": self.created_at,
            "priority": self.priority,
        }
        if self.context:
            result["context"] = self.context
        if self.timeout:
            result["timeout"] = self.timeout
        return result

    @classmethod
    def create(
        cls,
        source: str,
        target: str,
        action: str,
        parameters: dict[str, Any],
        **kwargs: Any,
    ) -> "A2ATaskMessage":
        """Create new task message with auto-generated ID."""
        task_id = kwargs.pop("id", str(uuid.uuid4()))
        return cls(
            id=task_id,
            source=source,
            target=target,
            action=action,
            parameters=parameters,
            **kwargs,
        )

    def to_sdk_format(self) -> dict[str, Any]:
        """Convert to format expected by official A2A SDK."""
        return self.to_dict()


@dataclass
class A2AStatusMessage:
    """Status message compatible with A2A SDK."""

    task_id: str
    status: str
    progress: float | None = None
    message: str | None = None
    created_at: float = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = time.time()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        result = {
            "task_id": self.task_id,
            "status": self.status,
            "created_at": self.created_at,
        }
        if self.progress is not None:
            result["progress"] = self.progress
        if self.message:
            result["message"] = self.message
        return result


@dataclass
class A2AResultMessage:
    """Result message compatible with A2A SDK."""

    task_id: str
    status: str
    result: Any | None = None
    error: str | None = None
    metadata: dict[str, Any] | None = None
    created_at: float = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.created_at is None:
            self.created_at = time.time()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        result_dict = {
            "task_id": self.task_id,
            "status": self.status,
            "created_at": self.created_at,
        }
        if self.result is not None:
            result_dict["result"] = self.result
        if self.error:
            result_dict["error"] = self.error
        if self.metadata:
            result_dict["metadata"] = self.metadata
        return result_dict


# ==================== A2A Message Adapter ====================


class A2AMessageAdapter:
    """
    Adapter for A2A-compatible messages aligned with official SDK.

    Phase 3.4: Lightweight implementation
    Phase 4.x: Will be replaced/extended with official A2A SDK

    Design Goals:
    - Message structure compatible with A2A SDK
    - Can be seamlessly upgraded to use official SDK
    - Maintains backward compatibility with AgentHub
    """

    @staticmethod
    def create_task_message(
        source: str, target: str, action: str, parameters: dict[str, Any], **kwargs: Any
    ) -> dict[str, Any]:
        """
        Create A2A-compatible task message.

        Args:
            source: Source agent identifier
            target: Target agent identifier
            action: Action/method name (e.g., "analyze_content")
            parameters: Action parameters
            **kwargs: Additional fields (context, priority, timeout, id)

        Returns:
            A2A task message dictionary compatible with SDK
        """
        task = A2ATaskMessage.create(
            source=source, target=target, action=action, parameters=parameters, **kwargs
        )

        return {
            "type": A2AMessageType.TASK.value,
            "data": task.to_dict(),
            "protocol_version": A2A_VERSION,
        }

    @staticmethod
    def create_status_message(
        task_id: str,
        status: str,
        progress: float | None = None,
        message: str | None = None,
    ) -> dict[str, Any]:
        """Create A2A-compatible status message."""
        status_msg = A2AStatusMessage(
            task_id=task_id, status=status, progress=progress, message=message
        )

        return {
            "type": A2AMessageType.STATUS.value,
            "data": status_msg.to_dict(),
            "protocol_version": A2A_VERSION,
        }

    @staticmethod
    def create_result_message(
        task_id: str,
        status: str,
        result: Any | None = None,
        error: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Create A2A-compatible result message."""
        result_msg = A2AResultMessage(
            task_id=task_id,
            status=status,
            result=result,
            error=error,
            metadata=metadata,
        )

        return {
            "type": A2AMessageType.RESULT.value,
            "data": result_msg.to_dict(),
            "protocol_version": A2A_VERSION,
        }

    @staticmethod
    def create_agent_card(agent_metadata: dict[str, Any]) -> dict[str, Any]:
        """
        Create A2A-compatible Agent Card.

        Args:
            agent_metadata: AgentHub agent metadata

        Returns:
            A2A Agent Card dictionary compatible with SDK
        """
        card = A2AAgentCard.from_agent_metadata(agent_metadata)
        return {
            "type": A2AMessageType.AGENT_CARD.value,
            "data": card.to_dict(),
            "protocol_version": A2A_VERSION,
        }

    @staticmethod
    def validate_message(message: dict[str, Any]) -> bool:
        """
        Validate A2A message structure.

        Args:
            message: Message to validate

        Returns:
            True if valid A2A message
        """
        try:
            # Check basic structure
            if not isinstance(message, dict):
                return False

            # Check required top-level fields
            if "type" not in message or "data" not in message:
                logger.warning("Missing 'type' or 'data' field")
                return False

            msg_type = message.get("type")
            data = message.get("data", {})

            # Validate based on message type
            if msg_type == A2AMessageType.TASK.value:
                required_fields = ["id", "source", "target", "action", "parameters"]
                for field in required_fields:
                    if field not in data:
                        logger.warning(f"Task message missing required field: {field}")
                        return False

            elif msg_type == A2AMessageType.RESULT.value:
                required_fields = ["task_id", "status"]
                for field in required_fields:
                    if field not in data:
                        logger.warning(
                            f"Result message missing required field: {field}"
                        )
                        return False

            elif msg_type == A2AMessageType.AGENT_CARD.value:
                required_fields = ["id", "name", "version", "actions"]
                for field in required_fields:
                    if field not in data:
                        logger.warning(f"Agent Card missing required field: {field}")
                        return False

            return True

        except Exception as e:
            logger.error(f"Error validating message: {e}")
            return False

    @staticmethod
    def to_agenthub_format(a2a_message: dict[str, Any]) -> dict[str, Any]:
        """
        Convert A2A message to AgentHub internal format.

        Args:
            a2a_message: A2A-formatted message

        Returns:
            AgentHub internal format message
        """
        msg_type = a2a_message.get("type")
        data = a2a_message.get("data", {})

        if msg_type == A2AMessageType.TASK.value:
            return {
                "type": "agent_request",
                "data": {
                    "request_id": data.get("id"),
                    "from_agent": data.get("source"),
                    "to_agent": data.get("target"),
                    "method": data.get("action"),
                    "parameters": data.get("parameters"),
                    "context": data.get("context"),
                    "timeout": data.get("timeout"),
                },
            }

        elif msg_type == A2AMessageType.RESULT.value:
            return {
                "type": "agent_response",
                "data": {
                    "request_id": data.get("task_id"),
                    "status": data.get("status"),
                    "result": data.get("result"),
                    "error": data.get("error"),
                },
            }

        # Pass through other message types
        return a2a_message

    @staticmethod
    def from_agenthub_format(agenthub_message: dict[str, Any]) -> dict[str, Any]:
        """
        Convert AgentHub internal format to A2A message.

        Args:
            agenthub_message: AgentHub internal format message

        Returns:
            A2A-formatted message
        """
        msg_type = agenthub_message.get("type")
        data = agenthub_message.get("data", {})

        if msg_type == "agent_request":
            return A2AMessageAdapter.create_task_message(
                source=data.get("from_agent"),
                target=data.get("to_agent"),
                action=data.get("method"),
                parameters=data.get("parameters", {}),
                id=data.get("request_id"),
                context=data.get("context"),
                timeout=data.get("timeout"),
            )

        elif msg_type == "agent_response":
            return A2AMessageAdapter.create_result_message(
                task_id=data.get("request_id"),
                status=data.get("status"),
                result=data.get("result"),
                error=data.get("error"),
            )

        # Pass through other message types
        return agenthub_message


# ==================== Utility Functions ====================


def create_analysis_task(
    source: str, target: str, content: str, analysis_type: str = "general"
) -> dict[str, Any]:
    """Create analysis task message."""
    return A2AMessageAdapter.create_task_message(
        source=source,
        target=target,
        action="analyze_content",
        parameters={"content": content, "analysis_type": analysis_type},
    )


def create_generation_task(
    source: str, target: str, prompt: str, format: str = "text"  # noqa: A002
) -> dict[str, Any]:
    """Create content generation task message."""
    return A2AMessageAdapter.create_task_message(
        source=source,
        target=target,
        action="generate_content",
        parameters={"prompt": prompt, "format": format},
    )


def create_search_task(
    source: str, target: str, query: str, filters: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Create search task message."""
    return A2AMessageAdapter.create_task_message(
        source=source,
        target=target,
        action="search",
        parameters={"query": query, "filters": filters or {}},
    )
