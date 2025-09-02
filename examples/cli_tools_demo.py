#!/usr/bin/env python3
"""Demo script showing CLI tool management functionality.

This script demonstrates the new CLI tool management commands:
- agenthub tools start
- agenthub tools status  
- agenthub tools list
- agenthub tools stop
"""

import subprocess
import time
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and display the result."""
    print(f"\n🔧 {description}")
    print(f"Command: {cmd}")
    print("-" * 50)
    
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            capture_output=True, 
            text=True,
            cwd=Path(__file__).parent.parent
        )
        
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"Stderr: {result.stderr}")
        
        return result.returncode == 0
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run the CLI tools demo."""
    print("🚀 AgentHub CLI Tools Management Demo")
    print("=" * 60)
    
    # Check if CLI is available
    if not run_command("python -m agentmanager.cli.main --help", "Checking CLI availability"):
        print("❌ CLI not available. Make sure you're in the correct directory.")
        return 1
    
    # Test tools help
    if not run_command("python -m agentmanager.cli.main tools --help", "Showing tools command help"):
        print("❌ Tools command not available.")
        return 1
    
    # Test status (should show not running)
    if not run_command("python -m agentmanager.cli.main tools status", "Checking initial service status"):
        print("❌ Status command failed.")
        return 1
    
    # Start the service
    print("\n🚀 Starting tool service...")
    if not run_command("python -m agentmanager.cli.main tools start --port 8006", "Starting tool service on port 8006"):
        print("❌ Failed to start service.")
        return 1
    
    # Wait a moment for service to start
    time.sleep(2)
    
    # Check status (should show running)
    if not run_command("python -m agentmanager.cli.main tools status --port 8006", "Checking service status after start"):
        print("❌ Status check failed.")
        return 1
    
    # List tools (should show empty)
    if not run_command("python -m agentmanager.cli.main tools list --port 8006", "Listing registered tools"):
        print("❌ List command failed.")
        return 1
    
    # Stop the service
    if not run_command("python -m agentmanager.cli.main tools stop --port 8006", "Stopping tool service"):
        print("❌ Failed to stop service.")
        return 1
    
    # Wait a moment for service to stop
    time.sleep(1)
    
    # Check status (should show not running)
    if not run_command("python -m agentmanager.cli.main tools status --port 8006", "Checking service status after stop"):
        print("❌ Final status check failed.")
        return 1
    
    print("\n" + "=" * 60)
    print("✅ CLI Tools Management Demo Completed Successfully!")
    print("\n📋 Available Commands:")
    print("  • agenthub tools start    - Start the tool registry service")
    print("  • agenthub tools stop     - Stop the tool registry service") 
    print("  • agenthub tools status   - Check service status")
    print("  • agenthub tools list     - List registered tools")
    print("  • agenthub tools info     - Get tool information")
    print("  • agenthub tools restart  - Restart the service")
    print("  • agenthub tools unregister - Unregister a tool")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
