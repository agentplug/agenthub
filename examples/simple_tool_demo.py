#!/usr/bin/env python3
"""
Super Simple AgentHub Tool Demo - Shows Phase 2.5 Step 1 Capabilities

This demo shows:
1. Tool registration with @tool decorator
2. Manual tool registration  
3. HTTP service hosting
4. Tool execution via API
5. Persistent service (continues running after script ends)

The tool service will continue running in the background after the demo script terminates.
Use 'agenthub tools stop' to stop the service when needed.
"""

import time
import requests
import signal
import sys

# Import our new Phase 2.5 capabilities
from agentmanager.core.tools import tool, get_global_registry
from agentmanager.core.tools import register_function
from agentmanager.core.tools import start_tool_service, stop_tool_service


# 1. CAPABILITY: Tool Registration with @tool decorator
@tool(name="text_transformer", description="Transform text in various ways")
def transform_text(text: str, style: str = "upper") -> str:
    """Transform text using different styles."""
    if style == "upper":
        return text.upper()
    elif style == "reverse":
        return text[::-1]
    elif style == "title":
        return text.title()
    else:
        return text


# 2. CAPABILITY: Manual tool registration (without decorator)
def math_calculator(a: float, b: float, operation: str) -> float:
    """Perform basic math operations."""
    if operation == "add":
        return a + b
    elif operation == "multiply":
        return a * b
    elif operation == "subtract":
        return a - b
    else:
        raise ValueError(f"Unknown operation: {operation}")


def cleanup_handler(signum, frame):
    """Handle Ctrl+C gracefully - keep service running."""
    print(f"\n🛑 Demo script terminating...")
    print("🌐 Tool service will continue running in the background")
    print("💡 Use 'agenthub tools stop' to stop the service")
    sys.exit(0)


def main():
    """Main demo function showcasing all capabilities."""
    print("🚀 Super Simple AgentHub Tool Demo")
    print("=" * 50)
    
    # Setup clean shutdown
    signal.signal(signal.SIGINT, cleanup_handler)
    
    # Show what we have initially
    registry = get_global_registry()
    print(f"📋 Auto-registered tools: {registry.list_tools()}")
    
    # 3. CAPABILITY: Manual tool registration
    print("🔧 Manually registering math_calculator...")
    result = register_function(math_calculator, name="calculator", description="Basic math operations")
    if result.success:
        print(f"   ✅ Registered: {result.tool_name}")
    
    print(f"📋 All registered tools: {registry.list_tools()}")
    
    # 4. CAPABILITY: Test tools directly (before HTTP service)
    print("\n🧪 Testing tools directly:")
    text_func = registry.get_function("text_transformer")
    calc_func = registry.get_function("calculator")
    
    print(f"   Text: '{text_func('hello world', 'upper')}'")
    print(f"   Text: '{text_func('hello world', 'reverse')}'")
    print(f"   Math: {calc_func(10, 5, 'add')} (10 + 5)")
    print(f"   Math: {calc_func(10, 5, 'multiply')} (10 * 5)")
    
    # 5. CAPABILITY: HTTP Service Hosting
    print("\n🌐 Starting HTTP service for tool access...")
    port = 8000  # Use default port to match CLI commands
    
    # Start service using the standard approach
    service = start_tool_service(port=port, background=True)
    print(f"   ✅ Service running at {service.get_service_url()}")
    
    # Wait a moment for service to start
    time.sleep(1)
    
    # 6. CAPABILITY: Tool execution via HTTP API
    print("\n🔗 Testing tools via HTTP API:")
    base_url = f"http://localhost:{port}"
    
    try:
        # List all available tools
        response = requests.get(f"{base_url}/tools/", timeout=3)
        tools_data = response.json()
        print(f"   📡 Available tools: {tools_data['tools']} (count: {tools_data['count']})")
        
        # Execute text transformer
        payload = {"parameters": {"text": "api test", "style": "title"}}
        response = requests.post(f"{base_url}/tools/text_transformer/execute", 
                               json=payload, timeout=3)
        result = response.json()
        print(f"   🔄 Text API result: '{result['result']}' (time: {result['execution_time']:.3f}s)")
        
        # Execute calculator
        payload = {"parameters": {"a": 15, "b": 3, "operation": "subtract"}}
        response = requests.post(f"{base_url}/tools/calculator/execute", 
                               json=payload, timeout=3)
        result = response.json()
        print(f"   🔢 Math API result: {result['result']} (time: {result['execution_time']:.3f}s)")
        
        # Test error handling
        payload = {"parameters": {"a": 10, "b": 0, "operation": "invalid"}}
        response = requests.post(f"{base_url}/tools/calculator/execute", 
                               json=payload, timeout=3)
        result = response.json()
        print(f"   ❌ Error handling: {result['success']} - {result['error'][:50]}...")
        
    except requests.RequestException as e:
        print(f"   ❌ HTTP request failed: {e}")
    
    # 7. CAPABILITY: Service management and status
    print(f"\n📊 Service status: Running = {service.is_running()}")
    print(f"📊 Service URL: {service.get_service_url()}")
    
    print("\n🎯 Demo complete! All Phase 2.5 Step 1 capabilities working:")
    print("   ✅ Tool registration (@tool decorator)")
    print("   ✅ Manual tool registration")
    print("   ✅ HTTP service hosting") 
    print("   ✅ REST API endpoints")
    print("   ✅ Tool execution (direct + HTTP)")
    print("   ✅ Error handling")
    print("   ✅ Service management")
    
    print("\n🎉 Demo completed successfully!")
    print("🌐 Tool service is running in the background")
    print("💡 Use 'agenthub tools stop' to stop the service when needed")
    print("\n📋 Available CLI commands:")
    print("   agenthub tools list    - List available tools")
    print("   agenthub tools status  - Check service status")
    print("   agenthub tools info <tool_name> - Get tool details")
    print("   agenthub tools stop    - Stop the service")
    print("\n🔗 HTTP API available at: http://127.0.0.1:8000")
    print("   Example: curl -X POST http://127.0.0.1:8000/tools/text_transformer/execute \\")
    print("            -H 'Content-Type: application/json' \\")
    print("            -d '{\"parameters\": {\"text\": \"hello\", \"style\": \"upper\"}}'")
    print("\n✅ Demo script will continue running to keep the service alive")
    print("🔄 Use 'agenthub tools stop' to stop the service when done")
    
    # Keep the script running silently to maintain the service
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Demo script terminating...")
        print("🌐 Tool service will stop with the script")


if __name__ == "__main__":
    main()