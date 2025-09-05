#!/usr/bin/env python3
"""
Real MCP Client - Following Official MCP SDK Patterns

This is a proper MCP client that communicates via MCP protocol.
"""

import asyncio
import sys
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    """Run the real MCP client example."""
    print("🚀 Real MCP Client - Using Official MCP Protocol")
    print("=" * 50)
    
    # Server parameters for stdio communication
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[os.path.join(os.path.dirname(__file__), "real_mcp_server.py")]
    )
    
    try:
        # Connect to MCP server via stdio
        async with stdio_client(server_params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                # Initialize MCP connection
                await session.initialize()
                print("✅ Connected to MCP server via MCP protocol")
                
                # Discover tools through MCP protocol
                print("\n🔍 Discovering tools via MCP protocol...")
                tools_response = await session.list_tools()
                print(f"✅ Found {len(tools_response.tools)} tools:")
                for tool in tools_response.tools:
                    print(f"   - {tool.name}: {tool.description}")
                
                # Call tools through MCP protocol
                print("\n🔧 Calling tools via MCP protocol...")
                
                # Call calculator tool
                result = await session.call_tool("calculator", {"a": 10, "b": 5, "operation": "add"})
                print(f"✅ Calculator result: {result.content[0].text if result.content else 'No result'}")
                
                # Call greeter tool
                result = await session.call_tool("greeter", {"person": "MCP User"})
                print(f"✅ Greeter result: {result.content[0].text if result.content else 'No result'}")
                
                # Call file_info tool
                result = await session.call_tool("file_info", {"file_path": "README.md"})
                print(f"✅ File info result: {result.content[0].text if result.content else 'No result'}")
                
                # Discover resources through MCP protocol
                print("\n📚 Discovering resources via MCP protocol...")
                resources_response = await session.list_resources()
                print(f"✅ Found {len(resources_response.resources)} resources:")
                for resource in resources_response.resources:
                    print(f"   - {resource.uri}: {resource.name}")
                
                # Read a resource
                if resources_response.resources:
                    resource = resources_response.resources[0]
                    print(f"\n📖 Reading resource: {resource.uri}")
                    read_result = await session.read_resource(resource.uri)
                    if read_result.contents:
                        content = read_result.contents[0]
                        if hasattr(content, 'text'):
                            print(f"✅ Resource content preview: {content.text[:200]}...")
                
                # Discover prompts through MCP protocol
                print("\n💬 Discovering prompts via MCP protocol...")
                prompts_response = await session.list_prompts()
                print(f"✅ Found {len(prompts_response.prompts)} prompts:")
                for prompt in prompts_response.prompts:
                    print(f"   - {prompt.name}: {prompt.description}")
                
                # Use a prompt
                if prompts_response.prompts:
                    prompt = prompts_response.prompts[0]
                    print(f"\n💭 Using prompt: {prompt.name}")
                    prompt_result = await session.get_prompt(prompt.name, {"code": "def hello(): print('world')"})
                    if prompt_result.messages:
                        message = prompt_result.messages[0]
                        if hasattr(message, 'content'):
                            print(f"✅ Prompt result: {message.content.text[:200]}...")
                
                print("\n🎉 Real MCP communication successful!")
                print("✅ Tools discovered and called via MCP protocol")
                print("✅ Resources discovered and read via MCP protocol") 
                print("✅ Prompts discovered and used via MCP protocol")
                
    except Exception as e:
        print(f"❌ MCP communication failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
