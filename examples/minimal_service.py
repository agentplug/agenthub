#!/usr/bin/env python3
"""
Minimal tool service script for persistent background execution.
This script runs the tool service in a truly detached process.
"""

import sys
import os
import time
import signal

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agentmanager.core.tools import tool, get_global_registry
from agentmanager.core.tools import start_tool_service

def signal_handler(signum, frame):
    """Handle shutdown signals gracefully."""
    print(f"\n🛑 Received signal {signum}, shutting down service...")
    sys.exit(0)

def main():
    """Main service function."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🚀 Starting minimal tool service...")
    
    # Register the same tools as the demo using the @tool decorator
    @tool(name="text_transformer", description="Transform text in various ways")
    def text_transformer(text: str, style: str = "upper") -> str:
        """Transform text based on style."""
        if style == "upper":
            return text.upper()
        elif style == "lower":
            return text.lower()
        elif style == "reverse":
            return text[::-1]
        else:
            return text
    
    @tool(name="calculator", description="Perform basic math operations")
    def calculator(a: float, b: float, operation: str) -> float:
        """Perform basic math operations."""
        if operation == "add":
            return a + b
        elif operation == "subtract":
            return a - b
        elif operation == "multiply":
            return a * b
        elif operation == "divide":
            if b == 0:
                raise ValueError('Cannot divide by zero')
            return a / b
        else:
            raise ValueError(f'Unknown operation: {operation}')
    
    # Get the registry to check registered tools
    registry = get_global_registry()
    print(f"📋 Registered tools: {list(registry.list_tools())}")
    
    # Start the service
    port = 8000
    service = start_tool_service(port=port, background=False)
    print(f"✅ Service running at http://127.0.0.1:{port}")
    print("💡 Service will continue running until stopped")
    
    # Keep the service running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Service stopping...")
        service.stop()

if __name__ == "__main__":
    main()
