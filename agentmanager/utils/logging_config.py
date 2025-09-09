"""Logging configuration utilities for AgentHub."""

import logging
import os
import sys
from typing import Optional

# ANSI color codes for terminal output
class Colors:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    
    # Basic text colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors (more vibrant)
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'


class ColorfulFormatter(logging.Formatter):
    """Colorful formatter for agent logs."""
    
    def format(self, record):
        # Get the original message
        message = super().format(record)
        
        # Add colors to specific log messages
        if hasattr(record, 'msg') and record.msg:
            msg = str(record.msg)
            
            # Agent loading success
            if 'Successfully loaded agent' in msg:
                # Extract agent name and tool count
                if 'with' in msg and 'tools' in msg:
                    parts = msg.split('with')
                    if len(parts) == 2:
                        agent_part = parts[0].strip()
                        tools_part = parts[1].strip()
                        message = f"{Colors.BRIGHT_GREEN}✅ {Colors.BOLD}{agent_part}{Colors.RESET} {Colors.BRIGHT_CYAN}{Colors.BOLD}{tools_part}{Colors.RESET}"
                else:
                    message = f"{Colors.BRIGHT_GREEN}✅ {Colors.BOLD}{msg}{Colors.RESET}"
            
            # Tool assignment
            elif 'Assigned tools to agent' in msg:
                # Extract agent name and tools
                if ':' in msg:
                    parts = msg.split(':')
                    if len(parts) == 2:
                        agent_part = parts[0].strip()
                        tools_part = parts[1].strip()
                        # Use 🔧 for colorful version, keep 🔐 for original
                        icon = "🔧" if msg.startswith("🔐") else "🔧"
                        message = f"{Colors.BRIGHT_BLUE}{icon} {Colors.BOLD}{agent_part}{Colors.RESET}{Colors.BRIGHT_CYAN}:{Colors.RESET} {Colors.BRIGHT_MAGENTA}{tools_part}{Colors.RESET}"
                else:
                    message = f"{Colors.BRIGHT_BLUE}🔧 {Colors.BOLD}{msg}{Colors.RESET}"
            
            # Agent processing
            elif 'Agent processing' in msg or 'Tool execution' in msg:
                message = f"{Colors.YELLOW}⚙️  {Colors.BOLD}{msg}{Colors.RESET}"
            
            # Error messages
            elif record.levelno >= logging.ERROR:
                message = f"{Colors.RED}❌ {Colors.BOLD}{msg}{Colors.RESET}"
            
            # Warning messages
            elif record.levelno >= logging.WARNING:
                message = f"{Colors.YELLOW}⚠️  {Colors.BOLD}{msg}{Colors.RESET}"
        
        return message


class HTTPLogFilter(logging.Filter):
    """Filter to suppress HTTP request logs while keeping useful agent logs."""
    
    def filter(self, record):
        # Keep useful agent logs but avoid duplicates
        if hasattr(record, 'msg') and record.msg:
            msg = str(record.msg)
            
            # Skip duplicate tool assignment logs (keep only the colorful one)
            if 'Assigned tools to agent' in msg and not msg.startswith('🔧') and not msg.startswith('🔐'):
                return False
                
            # Keep other useful agent logs
            if any(pattern in msg for pattern in [
                'Successfully loaded agent',
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
        formatter = ColorfulFormatter('%(message)s')
    else:
        formatter = ColorfulFormatter(
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
