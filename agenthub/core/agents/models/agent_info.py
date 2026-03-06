"""Agent information and metadata management."""

from dataclasses import dataclass
from typing import Any


@dataclass
class AgentInfo:
    """Encapsulates agent information and metadata."""

    # Core properties
    name: str
    namespace: str
    agent_name: str
    path: str
    version: str
    description: str
    methods: list[str]
    dependencies: list[str]

    # Manifest and interface
    manifest: dict[str, Any]
    interface: dict[str, Any]

    # Raw agent info for reference
    raw_info: dict[str, Any]

    def __init__(self, agent_info: dict[str, Any]):
        """Initialize from agent information dictionary."""
        self.raw_info = agent_info

        # Extract key information for easy access
        self.name = agent_info.get("name", "unknown")
        self.namespace = agent_info.get("namespace", "unknown")
        self.agent_name = agent_info.get("agent_name", "unknown")
        self.path = agent_info.get("path", "")
        self.version = agent_info.get("version", "unknown")
        self.description = agent_info.get("description", "")
        self.methods = agent_info.get("methods", [])
        self.dependencies = agent_info.get("dependencies", [])

        # Extract interface for method operations
        self.manifest = agent_info.get("manifest", {})
        self.interface = self.manifest.get("interface", {}).get("methods", {})

    @property
    def agent_id(self) -> str:
        """Get the agent ID."""
        return f"{self.namespace}/{self.name}"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "namespace": self.namespace,
            "agent_name": self.agent_name,
            "path": self.path,
            "version": self.version,
            "description": self.description,
            "methods": self.methods,
            "dependencies": self.dependencies,
            "manifest": self.manifest,
            "interface": self.interface,
        }

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"AgentInfo(name='{self.name}', namespace='{self.namespace}', "
            f"version='{self.version}', methods={len(self.methods)})"
        )

    def get_method_info(self, method_name: str) -> dict[str, Any]:
        """Get information about a specific method."""
        if method_name not in self.methods:
            raise ValueError(f"Method '{method_name}' not found in agent methods")

        # Get method info from interface
        method_info = self.interface.get(method_name, {})
        if not method_info:
            # Fallback to basic info
            return {
                "description": f"Execute {method_name}",
                "parameters": {},
            }

        return {
            "description": method_info.get("description", f"Execute {method_name}"),
            "parameters": method_info.get("parameters", {}),
            "required": method_info.get("required", False),
            "optional": method_info.get("optional", True),
        }

    def has_method(self, method_name: str) -> bool:
        """Check if agent has a specific method."""
        return method_name in self.methods

    def get_available_methods(self) -> list[str]:
        """Get list of available methods."""
        return self.methods.copy()

    def get_method_count(self) -> int:
        """Get number of available methods."""
        return len(self.methods)

    def is_valid(self) -> bool:
        """Check if agent info is valid."""
        return (
            self.name != "unknown"
            and self.namespace != "unknown"
            and len(self.methods) > 0
        )
