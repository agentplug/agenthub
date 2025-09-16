"""Configuration management for AgentHub."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AgentHubConfig:
    """Centralized configuration for AgentHub."""

    # Default paths
    agent_hub_dir: Path = field(default_factory=lambda: Path.home() / ".agenthub")
    agents_dir: Path = field(
        default_factory=lambda: Path.home() / ".agenthub" / "agents"
    )

    # Execution settings
    default_timeout: int = 300
    max_concurrent_agents: int = 4
    use_subprocess_execution: bool = True
    setup_environment_by_default: bool = True

    # Tool settings
    mcp_server_url: str = "http://localhost:8000/sse"
    enable_tool_caching: bool = True
    tool_timeout: int = 30

    # Performance settings
    enable_agent_caching: bool = True
    cache_ttl_seconds: int = 3600  # 1 hour

    # Logging
    log_level: str = "INFO"
    enable_debug_logging: bool = False
    quiet_mode: bool = False
    suppress_http_logs: bool = True

    # LLM settings
    llm_temperature: float = 0.0

    @classmethod
    def from_env(cls) -> "AgentHubConfig":
        """Create configuration from environment variables."""
        config = cls()

        # Override with environment variables if present
        if agent_dir := os.getenv("AGENTHUB_DIR"):
            config.agent_hub_dir = Path(agent_dir)
            config.agents_dir = Path(agent_dir) / "agents"

        if timeout := os.getenv("AGENTHUB_TIMEOUT"):
            config.default_timeout = int(timeout)

        if max_workers := os.getenv("AGENTHUB_MAX_WORKERS"):
            config.max_concurrent_agents = int(max_workers)

        if mcp_url := os.getenv("AGENTHUB_MCP_URL"):
            config.mcp_server_url = mcp_url

        if log_level := os.getenv("AGENTHUB_LOG_LEVEL"):
            config.log_level = log_level

        if llm_temperature := os.getenv("AGENTHUB_LLM_TEMPERATURE"):
            config.llm_temperature = float(llm_temperature)

        config.enable_debug_logging = os.getenv("AGENTHUB_DEBUG", "").lower() in (
            "true",
            "1",
            "yes",
        )
        config.use_subprocess_execution = os.getenv(
            "AGENTHUB_USE_SUBPROCESS", "true"
        ).lower() in ("true", "1", "yes")
        config.quiet_mode = os.getenv("AGENTHUB_QUIET", "").lower() in (
            "true",
            "1",
            "yes",
        )
        config.suppress_http_logs = os.getenv(
            "AGENTHUB_SUPPRESS_HTTP", "true"
        ).lower() in ("true", "1", "yes")

        return config

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "agent_hub_dir": str(self.agent_hub_dir),
            "agents_dir": str(self.agents_dir),
            "default_timeout": self.default_timeout,
            "max_concurrent_agents": self.max_concurrent_agents,
            "use_subprocess_execution": self.use_subprocess_execution,
            "setup_environment_by_default": self.setup_environment_by_default,
            "mcp_server_url": self.mcp_server_url,
            "enable_tool_caching": self.enable_tool_caching,
            "tool_timeout": self.tool_timeout,
            "enable_agent_caching": self.enable_agent_caching,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "log_level": self.log_level,
            "enable_debug_logging": self.enable_debug_logging,
            "quiet_mode": self.quiet_mode,
            "suppress_http_logs": self.suppress_http_logs,
        }


# Global configuration instance
_config: AgentHubConfig | None = None


def get_config() -> AgentHubConfig:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = AgentHubConfig.from_env()
    return _config


def set_config(config: AgentHubConfig) -> None:
    """Set the global configuration instance."""
    global _config
    _config = config


def reset_config() -> None:
    """Reset configuration to default."""
    global _config
    _config = None
