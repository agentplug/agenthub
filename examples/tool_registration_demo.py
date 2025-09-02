#!/usr/bin/env python3
"""
AgentHub Tool Registration Demo - Complete Step 1 Features

This demo showcases the full tool registration and HTTP service hosting workflow.
"""

import signal
import sys
import time
import requests
from typing import Dict, Any

from agentmanager.core.tool_decorators import tool, get_global_registry
from agentmanager.core.tool_registration import register_function
from agentmanager.core.tool_service_host import start_tool_service, stop_tool_service, is_service_running


# Define some example tools
@tool(name="text_processor", description="Process text with various operations")
def process_text(text: str, operation: str = "upper") -> str:
    """Process text with the specified operation."""
    if operation == "upper":
        return text.upper()
    elif operation == "lower":
        return text.lower()
    elif operation == "title":
        return text.title()
    elif operation == "reverse":
        return text[::-1]
    else:
        return f"Unknown operation: {operation}"


@tool(name="math_calculator", description="Perform basic math calculations")
def calculate(a: float, b: float, operation: str) -> float:
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


def simple_greeter(name: str, style: str = "casual") -> str:
    """Generate a greeting message."""
    if style == "casual":
        return f"Hey {name}! What's up?"
    elif style == "formal":
        return f"Good day, {name}. How may I assist you?"
    else:
        return f"Hello {name}!"


def cleanup_handler(signum, frame):
    """Handle cleanup on signal."""
    print(f"\n🛑 Received signal {signum}. Cleaning up...")
    stop_tool_service()
    print("   ✅ Service stopped.")
    sys.exit(0)


def test_api_endpoints(port: int) -> None:
    """Test the HTTP API endpoints."""
    base_url = f"http://localhost:{port}"
    
    print("🧪 Testing API endpoints...")
    
    try:
        # Test health check
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"   ✅ Health check: {response.status_code}")
        
        # Test tool listing
        response = requests.get(f"{base_url}/tools/", timeout=5)
        tools_data = response.json()
        print(f"   ✅ Tool listing: {tools_data['count']} tools found")
        
        # Test tool info
        response = requests.get(f"{base_url}/tools/text_processor", timeout=5)
        tool_info = response.json()
        print(f"   ✅ Tool info: {tool_info['name']} - {tool_info['description']}")
        
        # Test tool execution
        exec_data = {
            "parameters": {
                "text": "hello world",
                "operation": "upper"
            }
        }
        response = requests.post(f"{base_url}/tools/text_processor/execute", json=exec_data, timeout=5)
        exec_result = response.json()
        print(f"   ✅ Tool execution: {exec_result['result']}")
        
        # Test math calculator
        calc_data = {
            "parameters": {
                "a": 10,
                "b": 5,
                "operation": "multiply"
            }
        }
        response = requests.post(f"{base_url}/tools/math_calculator/execute", json=calc_data, timeout=5)
        calc_result = response.json()
        print(f"   ✅ Math calculation: {calc_result['result']}")
        
        # Test error handling (invalid tool)
        response = requests.get(f"{base_url}/tools/nonexistent", timeout=5)
        print(f"   ✅ Error handling: {response.status_code} for invalid tool")
        
    except requests.RequestException as e:
        print(f"   ❌ API test failed: {e}")


def main():
    """Main demo function."""
    # Setup signal handlers for clean shutdown
    signal.signal(signal.SIGINT, cleanup_handler)
    signal.signal(signal.SIGTERM, cleanup_handler)
    
    print("🚀 AgentHub Tool Registration Demo")
    print("=" * 50)
    
    # Step 1: Show registered tools from decorators
    registry = get_global_registry()
    tools = registry.list_tools()
    print(f"📝 Auto-registered tools: {tools}")
    
    # Step 2: Register additional tool manually
    print("📝 Registering additional tools...")
    result = register_function(simple_greeter, name="simple_greeter", description="Simple greeting tool")
    if result.success:
        print(f"   ✅ Registered: {result.tool_name}")
    else:
        print(f"   ❌ Failed: {result.message}")
    
    # Step 3: Start HTTP service
    print("🌐 Starting tool service...")
    port = 8080
    try:
        service = start_tool_service(port=port, background=True)
        print(f"   ✅ Service running at {service.get_service_url()}")
        
        # Wait a moment for service to fully start
        time.sleep(1)
        
        # Step 4: Show available API endpoints
        print("📡 Available API endpoints:")
        print(f"   GET  http://localhost:{port}/tools/                    - List all tools")
        print(f"   GET  http://localhost:{port}/tools/text_processor      - Tool info")
        print(f"   POST http://localhost:{port}/tools/text_processor/execute - Execute tool")
        print(f"   GET  http://localhost:{port}/health                    - Health check")
        
        # Step 5: Show example API calls
        print("💡 Example API calls:")
        print("    # List tools")
        print(f"    curl http://localhost:{port}/tools/")
        print("")
        print("    # Get tool info")
        print(f"    curl http://localhost:{port}/tools/text_processor")
        print("")
        print("    # Execute tool")
        print(f"    curl -X POST http://localhost:{port}/tools/text_processor/execute \\")
        print("         -H \"Content-Type: application/json\" \\")
        print("         -d '{\"parameters\": {\"text\": \"hello world\", \"operation\": \"upper\"}}'")
        print("")
        
        # Step 6: Test the APIs
        test_api_endpoints(port)
        
        print("🎯 Service is running! Try the API calls above.")
        print("   Press Ctrl+C to stop...")
        
        # Keep running until interrupted
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping service...")
            stop_tool_service()
            print("   ✅ Service stopped. Goodbye!")
        finally:
            print("🧹 Cleaning up...")
            stop_tool_service()
            
    except Exception as e:
        print(f"   ❌ Failed to start service: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())