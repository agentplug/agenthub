"""CLI configuration management."""

import json
from pathlib import Path
from typing import Any


class CLIConfig:
    """Manage CLI configuration and preferences."""

    def __init__(self) -> None:
        self.config_dir = Path.home() / ".agenthub"
        self.config_file = self.config_dir / "cli_config.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    data = json.load(f)
                    return (
                        data if isinstance(data, dict) else self._get_default_config()
                    )
            except Exception:
                return self._get_default_config()
        return self._get_default_config()

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration."""
        return {
            "storage_path": str(Path.home() / ".agenthub" / "agents"),
            "auto_setup_environment": True,
            "backup_path": str(Path.home() / ".agenthub" / "backups"),
            "log_level": "INFO",
            "interactive_mode": True,
            "confirm_actions": True,
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self._config[key] = value
        self._save_config()

    def _save_config(self) -> None:
        """Save configuration to file."""
        with open(self.config_file, "w") as f:
            json.dump(self._config, f, indent=2)

    def reset(self) -> None:
        """Reset to default configuration."""
        self._config = self._get_default_config()
        self._save_config()

    def show(self) -> dict[str, Any]:
        """Show current configuration."""
        return dict(self._config)
