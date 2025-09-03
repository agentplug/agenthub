#!/usr/bin/env python3
"""
Standalone persistent tool service for AgentHub demo.

This script starts a tool service that will persist independently
of the demo script that launched it.
"""

import sys
import os
import time
import signal
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agentmanager.core.tools import tool, start_tool_service

# Register the same tools as the demo
@tool("text_transformer", description="Transform text with various operations")
def text_transformer(text: str, operation: str = "upper") -> str:
    """Transform text with various operations."""
    if operation == "upper":
        return text.upper()
    elif operation == "lower":
        return text.lower()
    elif operation == "reverse":
        return text[::-1]
    else:
        return text

@tool("calculator", description="Perform basic math operations")
def calculator(a: float, b: float, operation: str = "add") -> float:
    """Perform basic math operations."""
    if operation == "add":
        return a + b
    elif operation == "subtract":
        return a - b
    elif operation == "multiply":
        return a * b
    elif operation == "divide":
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    else:
        raise ValueError(f"Unknown operation: {operation}")

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully."""
    print(f"\n🛑 Received signal {sig}, stopping service...")
    if 'service' in globals():
        service.stop()
    sys.exit(0)

def main():
    """Main service function."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    port = 8000
    print("🚀 Starting persistent tool service...")
    print(f"📋 Registered tools: text_transformer, calculator")
    
    # Start the service
    global service
    service = start_tool_service(port=port, background=False)
    
    print(f"✅ Service running at http://127.0.0.1:{port}")
    print("💡 Service will continue running until stopped with 'agenthub tools stop'")
    print("🔄 Use Ctrl+C to stop the service manually")
    
    try:
        # Keep the service running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()
