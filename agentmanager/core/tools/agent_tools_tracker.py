"""Agent-Tools Tracker for managing tool assignments to agents.

This module provides centralized tracking of which tools are assigned to which agents,
with bidirectional lookup, usage statistics, and CLI management integration.
"""

import logging
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict

from .registry import get_global_registry

logger = logging.getLogger(__name__)


@dataclass
class AgentToolAssignment:
    """Data structure representing tool assignment for a specific agent."""
    
    agent_name: str
    tool_names: List[str]
    assigned_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    usage_count: int = 0
    last_used: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert assignment to dictionary representation."""
        return {
            "agent_name": self.agent_name,
            "tool_names": self.tool_names,
            "assigned_at": self.assigned_at.isoformat(),
            "is_active": self.is_active,
            "usage_count": self.usage_count,
            "last_used": self.last_used.isoformat() if self.last_used else None,
        }


class AgentToolsTracker:
    """Centralized system that manages tool assignments and provides tracking capabilities."""
    
    def __init__(self) -> None:
        self._agent_assignments: Dict[str, AgentToolAssignment] = {}
        self._tool_to_agents: Dict[str, Set[str]] = defaultdict(set)
        self._global_tool_registry = get_global_registry()
        self._usage_stats: Dict[str, int] = defaultdict(int)

    def assign_tools_to_agent(self, agent_name: str, tool_names: List[str]) -> None:
        """Assign tools to an agent."""
        # Validate tools exist in global registry
        for tool_name in tool_names:
            if not self._global_tool_registry.get_tool(tool_name):
                raise ValueError(f"Tool '{tool_name}' not found in global registry")
        
        # Remove existing assignment for this agent
        if agent_name in self._agent_assignments:
            self._remove_agent_from_tool_mappings(agent_name)
        
        # Create new assignment
        assignment = AgentToolAssignment(
            agent_name=agent_name,
            tool_names=tool_names.copy()
        )
        
        self._agent_assignments[agent_name] = assignment
        
        # Update tool-to-agents mapping
        for tool_name in tool_names:
            self._tool_to_agents[tool_name].add(agent_name)
        
        logger.info(f"Assigned tools {tool_names} to agent {agent_name}")

    def remove_agent_tools(self, agent_name: str) -> None:
        """Remove all tools from an agent."""
        if agent_name not in self._agent_assignments:
            logger.warning(f"Agent {agent_name} has no tool assignments")
            return
        
        self._remove_agent_from_tool_mappings(agent_name)
        del self._agent_assignments[agent_name]
        
        logger.info(f"Removed all tools from agent {agent_name}")

    def get_agent_tools(self, agent_name: str) -> List[str]:
        """Get tools assigned to an agent."""
        assignment = self._agent_assignments.get(agent_name)
        if not assignment or not assignment.is_active:
            return []
        return assignment.tool_names.copy()

    def get_agents_with_tool(self, tool_name: str) -> List[str]:
        """Get agents that have access to a specific tool."""
        return list(self._tool_to_agents.get(tool_name, set()))

    def is_agent_assigned_tool(self, agent_name: str, tool_name: str) -> bool:
        """Check if an agent is assigned a specific tool."""
        assignment = self._agent_assignments.get(agent_name)
        if not assignment or not assignment.is_active:
            return False
        return tool_name in assignment.tool_names

    def get_all_assignments(self) -> Dict[str, List[str]]:
        """Get all agent-tool assignments."""
        return {
            agent_name: assignment.tool_names
            for agent_name, assignment in self._agent_assignments.items()
            if assignment.is_active
        }

    def get_assignment_info(self, agent_name: str) -> Optional[AgentToolAssignment]:
        """Get detailed assignment information for an agent."""
        return self._agent_assignments.get(agent_name)

    def get_tool_usage_stats(self) -> Dict[str, int]:
        """Get statistics on tool usage across agents."""
        return dict(self._usage_stats)

    def get_agent_usage_stats(self) -> Dict[str, int]:
        """Get statistics on agent tool usage."""
        return {
            agent_name: assignment.usage_count
            for agent_name, assignment in self._agent_assignments.items()
        }

    def record_tool_usage(self, agent_name: str, tool_name: str) -> None:
        """Record that an agent used a tool."""
        if not self.is_agent_assigned_tool(agent_name, tool_name):
            logger.warning(f"Agent {agent_name} used unassigned tool {tool_name}")
            return
        
        assignment = self._agent_assignments.get(agent_name)
        if assignment:
            assignment.usage_count += 1
            assignment.last_used = datetime.now()
        
        self._usage_stats[tool_name] += 1
        logger.debug(f"Recorded usage: {agent_name} -> {tool_name}")

    def get_tool_assignment_count(self) -> int:
        """Get total number of tool assignments."""
        return len(self._agent_assignments)

    def get_active_assignments_count(self) -> int:
        """Get number of active tool assignments."""
        return sum(1 for assignment in self._agent_assignments.values() if assignment.is_active)

    def deactivate_agent(self, agent_name: str) -> None:
        """Deactivate an agent's tool assignments."""
        assignment = self._agent_assignments.get(agent_name)
        if assignment:
            assignment.is_active = False
            logger.info(f"Deactivated tool assignments for agent {agent_name}")

    def activate_agent(self, agent_name: str) -> None:
        """Activate an agent's tool assignments."""
        assignment = self._agent_assignments.get(agent_name)
        if assignment:
            assignment.is_active = True
            logger.info(f"Activated tool assignments for agent {agent_name}")

    def _remove_agent_from_tool_mappings(self, agent_name: str) -> None:
        """Remove agent from all tool-to-agents mappings."""
        assignment = self._agent_assignments.get(agent_name)
        if assignment:
            for tool_name in assignment.tool_names:
                self._tool_to_agents[tool_name].discard(agent_name)
                if not self._tool_to_agents[tool_name]:
                    del self._tool_to_agents[tool_name]

    def get_tracker_status(self) -> Dict[str, Any]:
        """Get comprehensive tracker status."""
        return {
            "total_agents": len(self._agent_assignments),
            "active_agents": self.get_active_assignments_count(),
            "total_tools": len(self._tool_to_agents),
            "total_assignments": sum(len(assignment.tool_names) for assignment in self._agent_assignments.values()),
            "usage_stats": dict(self._usage_stats),
            "agent_usage_stats": self.get_agent_usage_stats(),
        }


# Global agent-tools tracker instance
_global_agent_tools_tracker = AgentToolsTracker()


def get_agent_tools_tracker() -> AgentToolsTracker:
    """Get the global agent-tools tracker instance."""
    return _global_agent_tools_tracker
