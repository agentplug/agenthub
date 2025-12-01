# A2A SDK Integration Guide - Phase 3.4

**Document Type**: Integration Guide
**Component**: A2A SDK Compatibility Layer
**Module**: core/communication
**Phase**: 3.4
**Status**: Design Phase

## 🎯 **Purpose**

This document provides guidance on integrating AgentHub with the official [A2A Python SDK](https://github.com/a2aproject/a2a-python) for full A2A protocol compliance.

## 📊 **Integration Strategy**

### **Phase 3.4 Approach: Compatibility Layer**

```
┌─────────────────────────────────────────────────────────────┐
│                    AgentHub Phase 3.4                       │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         A2A Compatibility Layer                      │  │
│  │  (Lightweight, no SDK dependency)                    │  │
│  │                                                      │  │
│  │  • Message format compatible with A2A              │  │
│  │  • Agent Card structure aligned with A2A           │  │
│  │  • Can be replaced with SDK in Phase 4.x           │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  AgentHub Core (ProcessManager, AgentWrapper, etc.)        │
└─────────────────────────────────────────────────────────────┘
```

### **Phase 4.x Approach: Full SDK Integration**

```
┌─────────────────────────────────────────────────────────────┐
│                    AgentHub Phase 4.x                       │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Official A2A Python SDK                      │  │
│  │  (Full protocol support)                             │  │
│  │                                                      │  │
│  │  from a2a import Agent, Task, AgentCard            │  │
│  │  • HTTP Server (FastAPI/Starlette)                 │  │
│  │  • gRPC Support                                     │  │
│  │  • OpenTelemetry Tracing                           │  │
│  │  • SQL Database Integration                        │  │
│  └──────────────────────────────────────────────────────┘  │
│              ↓                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         AgentHub SDK Adapter                         │  │
│  │  (Bridges AgentHub and A2A SDK)                     │  │
│  └──────────────────────────────────────────────────────┘  │
│              ↓                                              │
│  AgentHub Core (ProcessManager, AgentWrapper, etc.)        │
└─────────────────────────────────────────────────────────────┘
```

## 🏗️ **Understanding Official A2A SDK Structure**

Based on the [official A2A Python SDK](https://github.com/a2aproject/a2a-python):

### **1. A2A Server Structure**

```python
# Official A2A SDK approach (Phase 4.x target)
from a2a import Agent, Task, AgentCard
from a2a.server import A2AServer

# Define agent
agent = Agent(
    name="research-agent",
    description="Research and analysis agent",
    version="1.0.0"
)

# Add capabilities
@agent.task("analyze_content")
async def analyze_content(task: Task):
    """Analyze content and return insights."""
    content = task.parameters.get("content")
    result = await perform_analysis(content)
    return result

# Run A2A server
server = A2AServer(agent)
await server.serve()
```

### **2. A2A Message Format (Official)**

The official SDK uses these core components:

- **Agent Card**: JSON schema describing agent capabilities
- **Task Message**: Request from one agent to another
- **Status Update**: Progress notifications during task execution
- **Result Message**: Task completion with result or error
- **Artifacts**: Files, data objects exchanged between agents

## 🔄 **Phase 3.4 Compatibility Requirements**

### **Message Format Alignment**

Our Phase 3.4 implementation should produce messages that are **structurally compatible** with the A2A SDK format:

```python
# Phase 3.4: Our lightweight implementation
{
    "type": "task",
    "data": {
        "task_id": "uuid-string",
        "from_agent": "agent-1",
        "to_agent": "agent-2",
        "task_type": "analyze_content",
        "parameters": {"content": "..."},
        "timestamp": 1234567890.0
    }
}

# Compatible with A2A SDK structure (Phase 4.x)
# Can be converted to:
Task(
    id="uuid-string",
    source="agent-1",
    target="agent-2",
    action="analyze_content",
    parameters={"content": "..."},
    created_at=datetime.fromtimestamp(1234567890.0)
)
```

### **Agent Card Alignment**

```python
# Phase 3.4: Simplified Agent Card
{
    "agent_id": "research-agent",
    "name": "Research Agent",
    "description": "Agent for research tasks",
    "version": "1.0.0",
    "capabilities": ["tool:search", "tool:calculator"],
    "methods": [
        {
            "name": "analyze_content",
            "description": "Analyze content",
            "parameters": {"content": "str"},
            "return_type": "dict"
        }
    ]
}

# Compatible with A2A SDK AgentCard (Phase 4.x)
AgentCard(
    id="research-agent",
    name="Research Agent",
    description="Agent for research tasks",
    version="1.0.0",
    capabilities=["tool:search", "tool:calculator"],
    actions=[
        Action(
            name="analyze_content",
            description="Analyze content",
            parameters=Parameter(
                type="object",
                properties={"content": {"type": "string"}}
            ),
            returns={"type": "object"}
        )
    ]
)
```

## 📝 **Updated A2A Adapter Implementation**

### **Enhanced Protocol Adapter for SDK Compatibility**

```python
# agenthub/core/communication/protocol.py
"""A2A-compatible message protocol adapter aligned with official SDK."""

import json
import logging
import time
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime

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

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result = {
            "name": self.name,
            "type": self.type,
            "description": self.description,
            "required": self.required
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
    parameters: List[A2AParameter] = field(default_factory=list)
    returns: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": [p.to_dict() for p in self.parameters],
            "returns": self.returns
        }

    @classmethod
    def from_agent_method(cls, method_name: str, method_info: Dict[str, Any]) -> 'A2AAction':
        """Create Action from AgentHub method info."""
        parameters = []
        for param_name, param_info in method_info.get('parameters', {}).items():
            if isinstance(param_info, dict):
                parameters.append(A2AParameter(
                    name=param_name,
                    type=param_info.get('type', 'string'),
                    description=param_info.get('description', ''),
                    required=param_info.get('required', True),
                    default=param_info.get('default')
                ))
            else:
                # Simple type string
                parameters.append(A2AParameter(
                    name=param_name,
                    type=str(param_info),
                    description='',
                    required=True
                ))

        return cls(
            name=method_name,
            description=method_info.get('description', ''),
            parameters=parameters,
            returns={"type": method_info.get('return_type', 'any')}
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
    capabilities: List[str] = field(default_factory=list)
    actions: List[A2AAction] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format compatible with A2A SDK."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "protocol_version": self.protocol_version,
            "capabilities": self.capabilities,
            "actions": [action.to_dict() for action in self.actions],
            "metadata": self.metadata
        }

    @classmethod
    def from_agent_metadata(cls, agent_metadata: Dict[str, Any]) -> 'A2AAgentCard':
        """
        Create Agent Card from AgentHub agent metadata.

        Args:
            agent_metadata: AgentHub agent metadata structure

        Returns:
            A2AAgentCard instance compatible with A2A SDK
        """
        # Convert methods to actions
        actions = []
        for method_name, method_info in agent_metadata.get('interface', {}).items():
            actions.append(A2AAction.from_agent_method(method_name, method_info))

        # Extract capabilities
        capabilities = []
        if agent_metadata.get('assigned_tools'):
            capabilities.extend([f"tool:{tool}" for tool in agent_metadata['assigned_tools']])
        if agent_metadata.get('knowledge_available'):
            capabilities.append('knowledge:available')

        return cls(
            id=agent_metadata.get('agent_id', 'unknown'),
            name=agent_metadata.get('name', 'Unknown Agent'),
            description=agent_metadata.get('description', ''),
            version=agent_metadata.get('version', '0.1.0'),
            protocol_version=A2A_VERSION,
            capabilities=capabilities,
            actions=actions,
            metadata={
                'namespace': agent_metadata.get('namespace', ''),
                'author': agent_metadata.get('author', 'unknown'),
                'agenthub_version': agent_metadata.get('agenthub_version', 'unknown')
            }
        )

    def to_sdk_format(self) -> Dict[str, Any]:
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
    parameters: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    priority: str = "normal"
    timeout: Optional[float] = None
    created_at: float = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format compatible with A2A SDK."""
        result = {
            "id": self.id,
            "source": self.source,
            "target": self.target,
            "action": self.action,
            "parameters": self.parameters,
            "created_at": self.created_at,
            "priority": self.priority
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
        parameters: Dict[str, Any],
        **kwargs
    ) -> 'A2ATaskMessage':
        """Create new task message with auto-generated ID."""
        task_id = kwargs.pop('id', str(uuid.uuid4()))
        return cls(
            id=task_id,
            source=source,
            target=target,
            action=action,
            parameters=parameters,
            **kwargs
        )

    def to_sdk_format(self) -> Dict[str, Any]:
        """Convert to format expected by official A2A SDK."""
        return self.to_dict()


@dataclass
class A2AStatusMessage:
    """Status message compatible with A2A SDK."""
    task_id: str
    status: str
    progress: Optional[float] = None
    message: Optional[str] = None
    created_at: float = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result = {
            "task_id": self.task_id,
            "status": self.status,
            "created_at": self.created_at
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
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: float = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        result_dict = {
            "task_id": self.task_id,
            "status": self.status,
            "created_at": self.created_at
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
        source: str,
        target: str,
        action: str,
        parameters: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
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
            source=source,
            target=target,
            action=action,
            parameters=parameters,
            **kwargs
        )

        return {
            'type': A2AMessageType.TASK.value,
            'data': task.to_dict(),
            'protocol_version': A2A_VERSION
        }

    @staticmethod
    def create_status_message(
        task_id: str,
        status: str,
        progress: Optional[float] = None,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create A2A-compatible status message."""
        status_msg = A2AStatusMessage(
            task_id=task_id,
            status=status,
            progress=progress,
            message=message
        )

        return {
            'type': A2AMessageType.STATUS.value,
            'data': status_msg.to_dict(),
            'protocol_version': A2A_VERSION
        }

    @staticmethod
    def create_result_message(
        task_id: str,
        status: str,
        result: Optional[Any] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create A2A-compatible result message."""
        result_msg = A2AResultMessage(
            task_id=task_id,
            status=status,
            result=result,
            error=error,
            metadata=metadata
        )

        return {
            'type': A2AMessageType.RESULT.value,
            'data': result_msg.to_dict(),
            'protocol_version': A2A_VERSION
        }

    @staticmethod
    def create_agent_card(agent_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create A2A-compatible Agent Card.

        Args:
            agent_metadata: AgentHub agent metadata

        Returns:
            A2A Agent Card dictionary compatible with SDK
        """
        card = A2AAgentCard.from_agent_metadata(agent_metadata)
        return {
            'type': A2AMessageType.AGENT_CARD.value,
            'data': card.to_dict(),
            'protocol_version': A2A_VERSION
        }

    @staticmethod
    def validate_message(message: Dict[str, Any]) -> bool:
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
            if 'type' not in message or 'data' not in message:
                logger.warning("Missing 'type' or 'data' field")
                return False

            msg_type = message.get('type')
            data = message.get('data', {})

            # Validate based on message type
            if msg_type == A2AMessageType.TASK.value:
                required_fields = ['id', 'source', 'target', 'action', 'parameters']
                for field in required_fields:
                    if field not in data:
                        logger.warning(f"Task message missing required field: {field}")
                        return False

            elif msg_type == A2AMessageType.RESULT.value:
                required_fields = ['task_id', 'status']
                for field in required_fields:
                    if field not in data:
                        logger.warning(f"Result message missing required field: {field}")
                        return False

            elif msg_type == A2AMessageType.AGENT_CARD.value:
                required_fields = ['id', 'name', 'version', 'actions']
                for field in required_fields:
                    if field not in data:
                        logger.warning(f"Agent Card missing required field: {field}")
                        return False

            return True

        except Exception as e:
            logger.error(f"Error validating message: {e}")
            return False
```

## 🔄 **Migration Path to Official SDK**

### **Phase 4.x: Integrating Official A2A SDK**

```python
# Phase 4.x implementation (future)
# agenthub/core/communication/a2a_sdk_adapter.py

"""Adapter for official A2A Python SDK."""

try:
    from a2a import Agent, Task, AgentCard, A2AServer
    A2A_SDK_AVAILABLE = True
except ImportError:
    A2A_SDK_AVAILABLE = False
    # Fall back to Phase 3.4 compatibility layer

class AgentHubA2AAdapter:
    """
    Adapter between AgentHub and official A2A SDK.

    Provides backward compatibility with Phase 3.4 while
    using the official A2A SDK for protocol compliance.
    """

    def __init__(self, use_sdk: bool = True):
        self.use_sdk = use_sdk and A2A_SDK_AVAILABLE

        if self.use_sdk:
            logger.info("Using official A2A SDK")
        else:
            logger.info("Using Phase 3.4 compatibility layer")

    def create_agent_from_metadata(self, agent_metadata: Dict[str, Any]) -> Agent:
        """Convert AgentHub metadata to A2A SDK Agent."""
        if not self.use_sdk:
            # Use Phase 3.4 compatibility layer
            return A2AAgentCard.from_agent_metadata(agent_metadata)

        # Use official SDK
        agent = Agent(
            name=agent_metadata['name'],
            description=agent_metadata.get('description', ''),
            version=agent_metadata.get('version', '1.0.0')
        )

        # Register methods as tasks
        for method_name, method_info in agent_metadata.get('interface', {}).items():
            # Create wrapper that executes AgentHub method
            @agent.task(method_name)
            async def task_handler(task: Task, method=method_name):
                return await self._execute_agenthub_method(
                    agent_metadata['agent_id'],
                    method,
                    task.parameters
                )

        return agent

    async def _execute_agenthub_method(
        self,
        agent_id: str,
        method: str,
        parameters: Dict[str, Any]
    ) -> Any:
        """Execute AgentHub method through ProcessManager."""
        from agenthub.runtime import ProcessManager

        pm = ProcessManager()
        return await pm.execute_method(agent_id, method, parameters)
```

## 📋 **Compatibility Checklist**

- ✅ Message structure aligned with A2A SDK field names (`id`, `source`, `target`, `action`)
- ✅ Agent Card structure uses A2A SDK conventions (`id`, `actions` instead of `methods`)
- ✅ Protocol version included in all messages
- ✅ Timestamp format compatible (Unix timestamp)
- ✅ Task, Status, Result message formats match SDK
- ✅ Parameter definitions compatible with SDK
- ✅ Can be converted to/from SDK classes in Phase 4.x
- ✅ Validation logic aligned with A2A requirements
- ✅ Extensible for future SDK features (HTTP, gRPC, OpenTelemetry)

## 🚀 **Benefits of This Approach**

1. **Phase 3.4**: Lightweight, no SDK dependency, fast to implement
2. **Forward Compatible**: Message structure matches SDK exactly
3. **Smooth Migration**: Phase 4.x can add SDK as dependency without breaking changes
4. **Standards Compliant**: Follows official A2A protocol specification
5. **Backward Compatible**: AgentHub agents work unchanged
6. **Extensible**: Can add SDK features incrementally in Phase 4.x

## 📚 **References**

- Official A2A Python SDK: [https://github.com/a2aproject/a2a-python](https://github.com/a2aproject/a2a-python)
- A2A Protocol Documentation: [https://a2a-protocol.org](https://a2a-protocol.org)
- A2A Python SDK API: [https://a2a-protocol.org/latest/sdk/python/api/](https://a2a-protocol.org/latest/sdk/python/api/)
