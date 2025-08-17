"""Configuration management for Agent Hub."""

import os
from pathlib import Path
from typing import Dict, Any, Optional

import yaml


class ConfigManager:
    """Manage Agent Hub configuration from YAML files."""

    def __init__(self):
        """Initialize the configuration manager."""
        self.config_dir = Path.home() / ".agenthub" / "config"
        self.config_file = self.config_dir / "settings.yaml"
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = yaml.safe_load(f)
                    if config is None:
                        return self._get_default_config()
                    return config
            except Exception as e:
                print(f"Warning: Failed to load configuration from {self.config_file}: {e}")
                return self._get_default_config()
        return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            "registry": {
                "github_token": "",
                "cache_ttl": 3600,
                "max_retries": 3,
                "user_agent": "Agent-Hub/1.0.0"
            },
            "storage": {
                "base_path": "~/.agenthub",
                "max_cache_size": "500MB",
                "cleanup_interval": 86400,
                "backup_enabled": True
            },
            "logging": {
                "level": "INFO",
                "file": "~/.agenthub/logs/agenthub.log",
                "max_size": "10MB",
                "backup_count": 5
            },
            "performance": {
                "max_concurrent_agents": 5,
                "timeout": 30,  # Default 30 seconds
                "memory_limit": "1GB",
                "cpu_limit": 100
            },
            "security": {
                "process_isolation": True,
                "file_access_control": True,
                "dependency_isolation": True,
                "max_file_size": "100MB"
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value using dot notation (e.g., 'performance.timeout')."""
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def get_timeout(self) -> int:
        """Get the default timeout for agent execution."""
        return self.get("performance.timeout", 30)

    def get_memory_limit(self) -> str:
        """Get the default memory limit for agents."""
        return self.get("performance.memory_limit", "1GB")

    def get_cpu_limit(self) -> int:
        """Get the default CPU limit for agents."""
        return self.get("performance.cpu_limit", 100)

    def reload(self) -> None:
        """Reload configuration from file."""
        self._config = self._load_config()

    def show(self) -> Dict[str, Any]:
        """Show current configuration."""
        return self._config.copy()


# Global configuration instance
config = ConfigManager()
