"""
Configuration classes for AgentHub monitoring system

Provides flexible configuration options for monitoring behavior, display modes,
and performance settings.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class MonitoringConfig:
    """
    Configuration for agent monitoring system
    
    Provides comprehensive configuration options for monitoring behavior,
    display modes, and performance settings.
    """
    
    # Core settings
    enabled: bool = True
    display_mode: str = "incremental"  # "incremental" or "fullscreen"
    interactive: bool = False
    
    # Performance settings
    max_memory_mb: int = 100
    analysis_interval: float = 2.0
    refresh_rate: float = 1.0
    max_logs: int = 1000
    
    # Display settings
    show_metrics: bool = True
    show_timeline: bool = False
    compact_mode: bool = False
    
    # Export settings
    export_format: str = "json"  # "json", "txt", "csv"
    export_path: Optional[str] = None
    
    # Analysis settings
    enable_learning: bool = True
    context_window: int = 50  # Number of previous executions to keep
    
    # Advanced settings
    adaptive_analysis: bool = True
    error_priority: bool = True  # Analyze immediately when errors detected
    
    @classmethod
    def from_environment(cls) -> 'MonitoringConfig':
        """Create configuration from environment variables"""
        return cls(
            enabled=os.getenv("AGENTHUB_MONITORING_ENABLED", "true").lower() == "true",
            display_mode=os.getenv("AGENTHUB_DISPLAY_MODE", "incremental"),
            interactive=os.getenv("AGENTHUB_MONITORING_INTERACTIVE", "false").lower() == "true",
            max_memory_mb=int(os.getenv("AGENTHUB_MAX_MEMORY_MB", "100")),
            analysis_interval=float(os.getenv("AGENTHUB_ANALYSIS_INTERVAL", "2.0")),
            refresh_rate=float(os.getenv("AGENTHUB_REFRESH_RATE", "1.0")),
            max_logs=int(os.getenv("AGENTHUB_MAX_LOGS", "1000")),
            show_metrics=os.getenv("AGENTHUB_SHOW_METRICS", "true").lower() == "true",
            export_format=os.getenv("AGENTHUB_EXPORT_FORMAT", "json"),
        )
    
    @classmethod
    def incremental(cls) -> 'MonitoringConfig':
        """Quick setup for incremental monitoring with interactive controls"""
        return cls(
            display_mode="incremental",
            interactive=True,
            show_metrics=True,
            enable_learning=True
        )
    
    @classmethod
    def fullscreen(cls) -> 'MonitoringConfig':
        """Quick setup for fullscreen monitoring (clean view)"""
        return cls(
            display_mode="fullscreen",
            interactive=False,
            show_metrics=True,
            enable_learning=True
        )
    
    @classmethod
    def minimal(cls) -> 'MonitoringConfig':
        """Minimal monitoring setup for resource-constrained environments"""
        return cls(
            display_mode="incremental",
            interactive=False,
            refresh_rate=0.5,
            show_metrics=False,
            max_memory_mb=50,
            max_logs=500
        )
    
    @classmethod
    def debug(cls) -> 'MonitoringConfig':
        """Debug monitoring setup with high verbosity"""
        return cls(
            display_mode="incremental",
            interactive=True,
            analysis_interval=0.5,
            refresh_rate=0.5,
            show_metrics=True,
            show_timeline=True,
            enable_learning=True,
            adaptive_analysis=True
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return {
            'enabled': self.enabled,
            'display_mode': self.display_mode,
            'interactive': self.interactive,
            'max_memory_mb': self.max_memory_mb,
            'analysis_interval': self.analysis_interval,
            'refresh_rate': self.refresh_rate,
            'max_logs': self.max_logs,
            'show_metrics': self.show_metrics,
            'show_timeline': self.show_timeline,
            'compact_mode': self.compact_mode,
            'export_format': self.export_format,
            'export_path': self.export_path,
            'enable_learning': self.enable_learning,
            'context_window': self.context_window,
            'adaptive_analysis': self.adaptive_analysis,
            'error_priority': self.error_priority,
        }
    
    def validate(self) -> None:
        """Validate configuration values"""
        if self.display_mode not in ["incremental", "fullscreen"]:
            raise ValueError(f"Invalid display_mode: {self.display_mode}")
        
        if self.export_format not in ["json", "txt", "csv"]:
            raise ValueError(f"Invalid export_format: {self.export_format}")
        
        if self.max_memory_mb <= 0:
            raise ValueError("max_memory_mb must be positive")
        
        if self.analysis_interval <= 0:
            raise ValueError("analysis_interval must be positive")
        
        if self.refresh_rate <= 0:
            raise ValueError("refresh_rate must be positive")
        
        if self.max_logs <= 0:
            raise ValueError("max_logs must be positive")


class MonitoringBuilder:
    """
    Builder pattern for creating MonitoringConfig instances
    
    Provides a fluent interface for building complex monitoring configurations.
    """
    
    def __init__(self):
        self.config = MonitoringConfig()
    
    def incremental(self) -> 'MonitoringBuilder':
        """Set incremental display mode"""
        self.config.display_mode = "incremental"
        return self
    
    def fullscreen(self) -> 'MonitoringBuilder':
        """Set fullscreen display mode"""
        self.config.display_mode = "fullscreen"
        return self
    
    def interactive(self, enabled: bool = True) -> 'MonitoringBuilder':
        """Enable/disable interactive controls"""
        self.config.interactive = enabled
        return self
    
    def memory_limit(self, mb: int) -> 'MonitoringBuilder':
        """Set memory limit in MB"""
        self.config.max_memory_mb = mb
        return self
    
    def analysis_interval(self, seconds: float) -> 'MonitoringBuilder':
        """Set analysis interval in seconds"""
        self.config.analysis_interval = seconds
        return self
    
    def refresh_rate(self, seconds: float) -> 'MonitoringBuilder':
        """Set display refresh rate in seconds"""
        self.config.refresh_rate = seconds
        return self
    
    def max_logs(self, count: int) -> 'MonitoringBuilder':
        """Set maximum number of logs to keep"""
        self.config.max_logs = count
        return self
    
    def show_metrics(self, enabled: bool = True) -> 'MonitoringBuilder':
        """Enable/disable metrics display"""
        self.config.show_metrics = enabled
        return self
    
    def show_timeline(self, enabled: bool = True) -> 'MonitoringBuilder':
        """Enable/disable timeline display"""
        self.config.show_timeline = enabled
        return self
    
    def compact_mode(self, enabled: bool = True) -> 'MonitoringBuilder':
        """Enable/disable compact display mode"""
        self.config.compact_mode = enabled
        return self
    
    def export_format(self, format_type: str) -> 'MonitoringBuilder':
        """Set export format"""
        self.config.export_format = format_type
        return self
    
    def enable_learning(self, enabled: bool = True) -> 'MonitoringBuilder':
        """Enable/disable learning from previous executions"""
        self.config.enable_learning = enabled
        return self
    
    def adaptive_analysis(self, enabled: bool = True) -> 'MonitoringBuilder':
        """Enable/disable adaptive analysis behavior"""
        self.config.adaptive_analysis = enabled
        return self
    
    def build(self) -> MonitoringConfig:
        """Build and validate the configuration"""
        self.config.validate()
        return self.config


# Preset configurations for common use cases
PRESETS = {
    "incremental": MonitoringConfig.incremental,
    "fullscreen": MonitoringConfig.fullscreen,
    "minimal": MonitoringConfig.minimal,
    "debug": MonitoringConfig.debug,
}


def create_monitoring_config(
    config: Optional[MonitoringConfig] = None,
    preset: Optional[str] = None,
    **kwargs
) -> MonitoringConfig:
    """
    Create monitoring configuration with flexible options
    
    Args:
        config: Existing MonitoringConfig instance
        preset: Preset name ("incremental", "fullscreen", "minimal", "debug")
        **kwargs: Additional configuration parameters
    
    Returns:
        MonitoringConfig instance
    """
    if config is not None:
        # Update existing config with kwargs
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        config.validate()
        return config
    
    if preset is not None:
        if preset not in PRESETS:
            raise ValueError(f"Unknown preset: {preset}. Available: {list(PRESETS.keys())}")
        config = PRESETS[preset]()
        # Apply any additional kwargs
        for key, value in kwargs.items():
            if hasattr(config, key):
                setattr(config, key, value)
        config.validate()
        return config
    
    # Create from environment or defaults
    config = MonitoringConfig.from_environment()
    # Apply any additional kwargs
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    config.validate()
    return config
