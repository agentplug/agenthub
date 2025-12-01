"""
Process manager for executing agents in isolated subprocesses.

This module provides the ProcessManager class for managing agent execution
with support for:
- Subprocess isolation
- Real-time WebSocket communication
- Optional monitoring and analysis
- Dynamic or subprocess execution

The module has been refactored into smaller components for better maintainability:
- manager.py: Main orchestration
- executor.py: Process execution logic
- communication.py: WebSocket communication
- log_streaming.py: Real-time log capture
- monitoring_adapter.py: Optional monitoring integration
"""

# Import from new modular architecture
from agenthub.runtime.process_manager.manager import ProcessManager

__all__ = ["ProcessManager"]

# Version info
__version__ = "2.0.0"  # Major version for refactoring
