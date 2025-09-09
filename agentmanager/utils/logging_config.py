"""Logging configuration utilities for AgentHub."""

import logging
import os
import sys
from typing import Optional


class HTTPLogFilter(logging.Filter):
    """Filter to suppress HTTP request logs while keeping useful agent logs."""
    
    def filter(self, record):
        # Keep useful agent logs
        if hasattr(record, 'msg') and record.msg:
            msg = str(record.msg)
            if any(pattern in msg for pattern in [
                'Successfully loaded agent',
                'Assigned tools to agent',
                'Agent loaded',
                'Tool execution',
                'Agent processing'
            ]):
                return True
        
        # Suppress HTTP request logs from various libraries
        if hasattr(record, 'name'):
            # Common HTTP client loggers
            if any(pattern in record.name.lower() for pattern in [
                'httpx', 'httpcore', 'urllib3', 'requests', 'aiohttp',
                '_client', 'client'
            ]):
                return False
            
            # Suppress specific log messages
            if hasattr(record, 'msg') and record.msg:
                msg = str(record.msg).lower()
                if any(pattern in msg for pattern in [
                    'http request:', 'http/1.1', 'post http', 'get http',
                    'session_id=', 'localhost:8000', 'sse', 'messages/?session_id'
                ]):
                    return False
        
        return True


def setup_logging(
    level: str = "INFO",
    quiet: bool = False,
    suppress_http: bool = True
) -> None:
    """
    Set up logging configuration for AgentHub.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        quiet: If True, suppress most logs except errors
        suppress_http: If True, suppress HTTP request logs
    """
    # Convert string level to logging constant
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Create formatter
    if quiet:
        formatter = logging.Formatter('%(message)s')
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    
    # Add HTTP filter if requested
    if suppress_http:
        console_handler.addFilter(HTTPLogFilter())
    
    # Add handler to root logger
    root_logger.addHandler(console_handler)
    
    # Configure specific loggers
    if quiet:
        # Suppress verbose logs but keep important agent logs
        logging.getLogger('agentmanager').setLevel(logging.INFO)  # Keep agent logs
        logging.getLogger('urllib3').setLevel(logging.ERROR)
        logging.getLogger('httpx').setLevel(logging.ERROR)
        logging.getLogger('httpcore').setLevel(logging.ERROR)
        logging.getLogger('requests').setLevel(logging.ERROR)
    else:
        # Set appropriate levels for common libraries
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('httpx').setLevel(logging.WARNING)
        logging.getLogger('httpcore').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with AgentHub configuration."""
    return logging.getLogger(f"agentmanager.{name}")


def set_quiet_mode(enabled: bool = True) -> None:
    """Enable or disable quiet mode for logging."""
    setup_logging(quiet=enabled, suppress_http=True)


def set_debug_mode(enabled: bool = True) -> None:
    """Enable or disable debug mode for logging."""
    level = "DEBUG" if enabled else "INFO"
    setup_logging(level=level, quiet=not enabled, suppress_http=not enabled)
