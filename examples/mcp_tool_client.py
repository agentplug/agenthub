#!/usr/bin/env python3
"""
AgentManager MCP SSE Client Example

This client demonstrates how to connect to an MCP SSE server and call tools
that were registered using the @tool() decorator from agentmanager.core.tools.

Usage:
    # First start the server in one terminal:
    python examples/mcp_tool_server.py
    
    # Then run the client in another terminal:
    python examples/mcp_tool_client.py
"""

import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client


async def call_tool(session: ClientSession, tool_name: str, arguments: dict):
    """Helper function to call a tool and handle the response."""
    print(f"\n🔧 Calling tool '{tool_name}' with arguments: {arguments}")
    try:
        result = await session.call_tool(tool_name, arguments)
        if result:
            print(f"✅ Result: {result}")
            if hasattr(result, 'content') and result.content:
                if len(result.content) > 0:
                    content_item = result.content[0]
                    if hasattr(content_item, 'text'):
                        print(f"✅ Result text: {content_item.text}")
                        return content_item.text
                    else:
                        print(f"✅ Result: {content_item}")
                        return str(content_item)
            else:
                print("✅ Tool executed successfully")
                return str(result)
        else:
            print("❌ No result returned")
            return None
    except Exception as e:
        print(f"❌ Error calling tool '{tool_name}': {e}")
        return None


async def main():
    """Main client function."""
    print("🚀 Starting AgentManager MCP SSE Client...")
    
    # Connect to the MCP SSE server
    async with sse_client(url="http://localhost:8000/sse") as streams:
        async with ClientSession(*streams) as session:
            print("🔗 Connected to MCP SSE server")
            
            # Initialize the session
            await session.initialize()
            print("✅ Session initialized")
            
            # List available tools
            print("\n📋 Available tools:")
            tools = await session.list_tools()
            if hasattr(tools, 'tools'):
                # Handle response format
                for tool in tools.tools:
                    print(f"  - {tool.name}: {tool.description}")
            else:
                print(f"  Raw tools response: {tools}")
            
            # Test mathematical tools
            print("\n🧮 Testing mathematical tools:")
            await call_tool(session, "add", {"a": 15, "b": 27})
            await call_tool(session, "subtract", {"a": 100, "b": 37})
            await call_tool(session, "multiply", {"a": 8, "b": 9})
            await call_tool(session, "divide", {"a": 100, "b": 4})
            
            # Test greeting tool
            print("\n👋 Testing greeting tool:")
            await call_tool(session, "greet", {"name": "Alice"})
            await call_tool(session, "greet", {"name": "Bob", "greeting": "Hi"})
            
            # Test weather tool
            print("\n🌤️  Testing weather tool:")
            await call_tool(session, "get_weather", {"location": "New York"})
            await call_tool(session, "get_weather", {"location": "London", "unit": "fahrenheit"})
            
            # Test text processing tool
            print("\n📝 Testing text processing tool:")
            await call_tool(session, "process_text", {"text": "hello world", "operation": "uppercase"})
            await call_tool(session, "process_text", {"text": "Hello World", "operation": "lowercase"})
            await call_tool(session, "process_text", {"text": "hello world", "operation": "titlecase"})
            await call_tool(session, "process_text", {"text": "hello world", "operation": "reverse"})
            await call_tool(session, "process_text", {"text": "The quick brown fox jumps over the lazy dog", "operation": "wordcount"})
            await call_tool(session, "process_text", {"text": "Hello World", "operation": "charcount"})
            
            # Test error handling
            print("\n⚠️  Testing error handling:")
            await call_tool(session, "divide", {"a": 10, "b": 0})  # Should handle division by zero
            await call_tool(session, "process_text", {"text": "hello", "operation": "invalid"})  # Should handle invalid operation
            
            print("\n✅ All tests completed!")


if __name__ == "__main__":
    print("AgentManager MCP SSE Client Example")
    print("====================================")
    print("Make sure the server is running on http://localhost:8000/sse")
    print("Start the server with: python examples/mcp_tool_server.py")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Client stopped by user")
    except Exception as e:
        print(f"\n❌ Client error: {e}")
        print("Make sure the server is running on http://localhost:8000/sse")