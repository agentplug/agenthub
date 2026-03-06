# A2A Protocol Adapter Implementation Details - Phase 3.4

**Document Type**: Implementation Details
**Component**: A2AMessageAdapter
**Module**: core/communication
**Phase**: 3.4
**Status**: Design Phase

## 🎯 **Purpose**

Detailed implementation of the A2AMessageAdapter that provides A2A-compatible message structure for agent-to-agent communication, designed for future integration with the official [A2A Python SDK](https://github.com/a2aproject/a2a-python).

## 🏗️ **Architecture Overview**

```
A2AMessageAdapter
├── Message Format
│   ├── Task messages
│   ├── Status messages
│   └── Result messages
├── Agent Card (simplified)
│   ├── Agent metadata
│   ├── Capabilities
│   └── Available methods
├── Validation
│   ├── Message structure
│   ├── Required fields
│   └── Type checking
└── Conversion
    ├── AgentHub → A2A format
    ├── A2A → AgentHub format
    └── Future SDK compatibility layer
```

## 🔧 **Core Implementation**

### **1. A2AMessageAdapter Class**

```python
# agenthub/core/communication/protocol.py
"""A2A-compatible message protocol adapter."""

import json
import logging
import time
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class A2AMessageType(Enum):
    """A2A message types."""
    TASK = "task"
    STATUS = "status"
    RESULT = "result"
    ERROR = "error"


class A2ATaskStatus(Enum):
    """A2A task status values."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class A2AAgentCard:
    """
    Simplified A2A Agent Card.

    Based on A2A protocol specification but simplified for Phase 3.4.
    Can be upgraded to full Agent Card format in future phases.
    """
    agent_id: str
    name: str
    description: str
    version: str
    capabilities: List[str]
    methods: List[Dict[str, Any]]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return asdict(self)

    @classmethod
    def from_agent_metadata(cls, agent_metadata: Dict[str, Any]) -> 'A2AAgentCard':
        """
        Create Agent Card from AgentHub agent metadata.

        Args:
            agent_metadata: AgentHub agent metadata structure

        Returns:
            A2AAgentCard instance
        """
        # Extract methods information
        methods = []
        for method_name, method_info in agent_metadata.get('interface', {}).items():
            methods.append({
                'name': method_name,
                'description': method_info.get('description', ''),
                'parameters': method_info.get('parameters', {}),
                'return_type': method_info.get('return_type', 'any')
            })

        # Extract capabilities
        capabilities = []
        if agent_metadata.get('assigned_tools'):
            capabilities.extend([f"tool:{tool}" for tool in agent_metadata['assigned_tools']])
        if agent_metadata.get('knowledge_available'):
            capabilities.append('knowledge')

        return cls(
            agent_id=agent_metadata.get('agent_id', 'unknown'),
            name=agent_metadata.get('name', 'Unknown Agent'),
            description=agent_metadata.get('description', ''),
            version=agent_metadata.get('version', '0.1.0'),
            capabilities=capabilities,
            methods=methods,
            metadata={
                'namespace': agent_metadata.get('namespace', ''),
                'author': agent_metadata.get('author', 'unknown')
            }
        )


@dataclass
class A2ATaskMessage:
    """
    A2A-compatible task message.

    Used for agent-to-agent task requests.
    """
    task_id: str
    from_agent: str
    to_agent: str
    task_type: str
    parameters: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    priority: str = "normal"
    timeout: Optional[float] = None
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return asdict(self)

    @classmethod
    def create(
        cls,
        from_agent: str,
        to_agent: str,
        task_type: str,
        parameters: Dict[str, Any],
        **kwargs
    ) -> 'A2ATaskMessage':
        """Create new task message with auto-generated task_id."""
        task_id = kwargs.pop('task_id', str(uuid.uuid4()))
        return cls(
            task_id=task_id,
            from_agent=from_agent,
            to_agent=to_agent,
            task_type=task_type,
            parameters=parameters,
            **kwargs
        )


@dataclass
class A2AStatusMessage:
    """A2A-compatible status message."""
    task_id: str
    status: str
    progress: Optional[float] = None
    message: Optional[str] = None
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return asdict(self)


@dataclass
class A2AResultMessage:
    """A2A-compatible result message."""
    task_id: str
    status: str
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    timestamp: float = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return asdict(self)


class A2AMessageAdapter:
    """
    Adapter for A2A-compatible message format.

    Design Principles:
    - Compatible with A2A protocol structure
    - Lightweight implementation (no full SDK dependency)
    - Designed for future SDK integration
    - Backward compatible with AgentHub patterns

    Future Migration:
    Phase 4.x can replace this adapter with official A2A Python SDK
    while maintaining compatibility with Phase 3.4 messages.
    """

    @staticmethod
    def create_task_message(
        from_agent: str,
        to_agent: str,
        task_type: str,
        parameters: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create A2A-compatible task message.

        Args:
            from_agent: Source agent identifier
            to_agent: Target agent identifier
            task_type: Type of task (e.g., "analyze_content", "generate_report")
            parameters: Task parameters
            **kwargs: Additional optional fields (context, priority, timeout)

        Returns:
            A2A task message dictionary
        """
        task = A2ATaskMessage.create(
            from_agent=from_agent,
            to_agent=to_agent,
            task_type=task_type,
            parameters=parameters,
            **kwargs
        )

        return {
            'type': A2AMessageType.TASK.value,
            'data': task.to_dict()
        }

    @staticmethod
    def create_status_message(
        task_id: str,
        status: str,
        progress: Optional[float] = None,
        message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create A2A-compatible status message.

        Args:
            task_id: Task identifier
            status: Task status (pending, running, completed, failed)
            progress: Optional progress percentage (0.0 to 1.0)
            message: Optional status message

        Returns:
            A2A status message dictionary
        """
        status_msg = A2AStatusMessage(
            task_id=task_id,
            status=status,
            progress=progress,
            message=message
        )

        return {
            'type': A2AMessageType.STATUS.value,
            'data': status_msg.to_dict()
        }

    @staticmethod
    def create_result_message(
        task_id: str,
        status: str,
        result: Optional[Any] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create A2A-compatible result message.

        Args:
            task_id: Task identifier
            status: Task status (completed or failed)
            result: Task result (if successful)
            error: Error message (if failed)
            metadata: Optional metadata

        Returns:
            A2A result message dictionary
        """
        result_msg = A2AResultMessage(
            task_id=task_id,
            status=status,
            result=result,
            error=error,
            metadata=metadata
        )

        return {
            'type': A2AMessageType.RESULT.value,
            'data': result_msg.to_dict()
        }

    @staticmethod
    def create_agent_card(agent_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create A2A-compatible Agent Card.

        Args:
            agent_metadata: AgentHub agent metadata

        Returns:
            A2A Agent Card dictionary
        """
        card = A2AAgentCard.from_agent_metadata(agent_metadata)
        return card.to_dict()

    @staticmethod
    def validate_task_message(message: Dict[str, Any]) -> bool:
        """
        Validate A2A task message structure.

        Args:
            message: Message to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            if message.get('type') != A2AMessageType.TASK.value:
                return False

            data = message.get('data', {})
            required_fields = ['task_id', 'from_agent', 'to_agent', 'task_type', 'parameters']

            for field in required_fields:
                if field not in data:
                    logger.warning(f"Missing required field: {field}")
                    return False

            return True

        except Exception as e:
            logger.error(f"Error validating task message: {e}")
            return False

    @staticmethod
    def validate_result_message(message: Dict[str, Any]) -> bool:
        """
        Validate A2A result message structure.

        Args:
            message: Message to validate

        Returns:
            True if valid, False otherwise
        """
        try:
            if message.get('type') != A2AMessageType.RESULT.value:
                return False

            data = message.get('data', {})
            required_fields = ['task_id', 'status']

            for field in required_fields:
                if field not in data:
                    logger.warning(f"Missing required field: {field}")
                    return False

            # Either result or error should be present
            if data.get('status') == 'completed' and data.get('result') is None:
                logger.warning("Completed task missing result")
                return False

            if data.get('status') == 'failed' and data.get('error') is None:
                logger.warning("Failed task missing error")
                return False

            return True

        except Exception as e:
            logger.error(f"Error validating result message: {e}")
            return False

    @staticmethod
    def to_agenthub_format(a2a_message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert A2A message to AgentHub internal format.

        Args:
            a2a_message: A2A-formatted message

        Returns:
            AgentHub internal format message
        """
        msg_type = a2a_message.get('type')
        data = a2a_message.get('data', {})

        if msg_type == A2AMessageType.TASK.value:
            return {
                'type': 'agent_request',
                'data': {
                    'request_id': data.get('task_id'),
                    'from_agent': data.get('from_agent'),
                    'to_agent': data.get('to_agent'),
                    'method': data.get('task_type'),
                    'parameters': data.get('parameters'),
                    'context': data.get('context'),
                    'timeout': data.get('timeout')
                }
            }

        elif msg_type == A2AMessageType.RESULT.value:
            return {
                'type': 'agent_response',
                'data': {
                    'request_id': data.get('task_id'),
                    'status': data.get('status'),
                    'result': data.get('result'),
                    'error': data.get('error')
                }
            }

        # Pass through other message types
        return a2a_message

    @staticmethod
    def from_agenthub_format(agenthub_message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert AgentHub internal format to A2A message.

        Args:
            agenthub_message: AgentHub internal format message

        Returns:
            A2A-formatted message
        """
        msg_type = agenthub_message.get('type')
        data = agenthub_message.get('data', {})

        if msg_type == 'agent_request':
            return A2AMessageAdapter.create_task_message(
                from_agent=data.get('from_agent'),
                to_agent=data.get('to_agent'),
                task_type=data.get('method'),
                parameters=data.get('parameters', {}),
                task_id=data.get('request_id'),
                context=data.get('context'),
                timeout=data.get('timeout')
            )

        elif msg_type == 'agent_response':
            return A2AMessageAdapter.create_result_message(
                task_id=data.get('request_id'),
                status=data.get('status'),
                result=data.get('result'),
                error=data.get('error')
            )

        # Pass through other message types
        return agenthub_message


# Utility functions for common message patterns

def create_analysis_task(
    from_agent: str,
    to_agent: str,
    content: str,
    analysis_type: str = "general"
) -> Dict[str, Any]:
    """Create analysis task message."""
    return A2AMessageAdapter.create_task_message(
        from_agent=from_agent,
        to_agent=to_agent,
        task_type="analyze_content",
        parameters={
            'content': content,
            'analysis_type': analysis_type
        }
    )


def create_generation_task(
    from_agent: str,
    to_agent: str,
    prompt: str,
    format: str = "text"
) -> Dict[str, Any]:
    """Create content generation task message."""
    return A2AMessageAdapter.create_task_message(
        from_agent=from_agent,
        to_agent=to_agent,
        task_type="generate_content",
        parameters={
            'prompt': prompt,
            'format': format
        }
    )


def create_search_task(
    from_agent: str,
    to_agent: str,
    query: str,
    filters: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create search task message."""
    return A2AMessageAdapter.create_task_message(
        from_agent=from_agent,
        to_agent=to_agent,
        task_type="search",
        parameters={
            'query': query,
            'filters': filters or {}
        }
    )
```

## 🔄 **Integration with Agent Wrapper**

```python
# agenthub/core/agents/wrapper.py
# Add to AgentWrapper class

class AgentWrapper:
    def send_task_to_agent(
        self,
        target_agent: str,
        task_type: str,
        parameters: Dict[str, Any],
        timeout: float = 300.0
    ) -> Any:
        """
        Send task to another agent using A2A protocol.

        Args:
            target_agent: Target agent identifier
            task_type: Type of task
            parameters: Task parameters
            timeout: Task timeout in seconds

        Returns:
            Task result from target agent
        """
        from agenthub.core.communication import get_communication_server
        from agenthub.core.communication.protocol import A2AMessageAdapter

        # Get communication server
        server = get_communication_server()
        if not server.is_running:
            raise RuntimeError("Communication server not available")

        # Create A2A task message
        message = A2AMessageAdapter.create_task_message(
            from_agent=self.agent_id,
            to_agent=target_agent,
            task_type=task_type,
            parameters=parameters,
            timeout=timeout
        )

        # Send to target agent
        # This would integrate with MessageRouter for request/response tracking
        return self._send_and_wait_for_response(target_agent, message, timeout)
```

## 📊 **A2A Compatibility Matrix**

```python
# Phase 3.4 Implementation vs Full A2A Protocol

FEATURE_MATRIX = {
    "Agent Cards": {
        "phase_3.4": "Simplified structure",
        "full_a2a": "Complete JSON schema",
        "compatible": True
    },
    "Task Messages": {
        "phase_3.4": "Core fields (task_id, from, to, type, params)",
        "full_a2a": "Extended fields (priority, dependencies, etc.)",
        "compatible": True
    },
    "Status Updates": {
        "phase_3.4": "Basic status (pending, running, completed, failed)",
        "full_a2a": "Rich status with progress and metadata",
        "compatible": True
    },
    "Results": {
        "phase_3.4": "Result or error",
        "full_a2a": "Artifacts, structured data, streaming",
        "compatible": True
    },
    "Authentication": {
        "phase_3.4": "None (localhost only)",
        "full_a2a": "OAuth2, API keys, mTLS",
        "compatible": False  # Phase 4.x feature
    },
    "Transport": {
        "phase_3.4": "WebSocket only",
        "full_a2a": "WebSocket, HTTP, gRPC",
        "compatible": "Partial"
    }
}
```

## 🧪 **Testing Requirements**

```python
# tests/phase3.4/test_a2a_protocol.py

import pytest
from agenthub.core.communication.protocol import (
    A2AMessageAdapter,
    A2AAgentCard,
    A2ATaskMessage
)

def test_create_task_message():
    """Test A2A task message creation."""
    message = A2AMessageAdapter.create_task_message(
        from_agent="agent1",
        to_agent="agent2",
        task_type="analyze_content",
        parameters={'content': 'test'}
    )

    assert message['type'] == 'task'
    assert message['data']['from_agent'] == 'agent1'
    assert message['data']['to_agent'] == 'agent2'
    assert message['data']['task_type'] == 'analyze_content'
    assert 'task_id' in message['data']

def test_validate_task_message():
    """Test task message validation."""
    valid_message = {
        'type': 'task',
        'data': {
            'task_id': '123',
            'from_agent': 'agent1',
            'to_agent': 'agent2',
            'task_type': 'test',
            'parameters': {}
        }
    }

    assert A2AMessageAdapter.validate_task_message(valid_message) is True

    # Missing required field
    invalid_message = {
        'type': 'task',
        'data': {
            'task_id': '123',
            'from_agent': 'agent1'
            # Missing to_agent, task_type, parameters
        }
    }

    assert A2AMessageAdapter.validate_task_message(invalid_message) is False

def test_agent_card_creation():
    """Test Agent Card creation from metadata."""
    agent_metadata = {
        'agent_id': 'test-agent',
        'name': 'Test Agent',
        'description': 'A test agent',
        'version': '1.0.0',
        'interface': {
            'analyze': {
                'description': 'Analyze content',
                'parameters': {'content': 'str'},
                'return_type': 'dict'
            }
        },
        'assigned_tools': ['search', 'calculator']
    }

    card = A2AAgentCard.from_agent_metadata(agent_metadata)

    assert card.agent_id == 'test-agent'
    assert card.name == 'Test Agent'
    assert len(card.methods) == 1
    assert 'tool:search' in card.capabilities
```

## 🚀 **Migration Path to Full A2A SDK**

```python
# Phase 4.x: Migration to full A2A Python SDK

"""
Phase 4.x can replace A2AMessageAdapter with official SDK:

from a2a import Agent, Task, AgentCard  # Official A2A SDK

class A2AMessageAdapter:
    # Compatibility layer for Phase 3.4 messages

    @staticmethod
    def create_task_message_v2(...):
        # Use official SDK
        task = Task(...)
        return task.to_message()

    # Keep Phase 3.4 methods for backward compatibility
    @staticmethod
    def create_task_message(...):
        # Legacy method redirects to v2
        return A2AMessageAdapter.create_task_message_v2(...)
"""
```

Phase 3.4 message structure is designed to be **forward compatible** with the official A2A SDK, allowing seamless migration in Phase 4.x.
