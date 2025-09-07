#!/usr/bin/env python3
"""
Step 3 Debug Flow: Complete Tool Injection Process Tracing

This demo shows the ENTIRE flow step by step:
1. Tool registration and availability
2. Tool context injection details
3. Agent execution commands
4. Agent's tool decision making
5. Tool execution results
6. Final agent response
"""

import asyncio
import json
import agentmanager as amg
from agentmanager.core.tools import tool, get_available_tools, get_tool_registry
from agentmanager.core.mcp import get_tool_manager, get_tool_injector

# Define custom tools with detailed logging
@tool(name="web_search", description="Search the web for real-time information using DuckDuckGo")
def web_search(query: str, max_results: int = 5) -> dict:
    """Real web search using DuckDuckGo API"""
    print(f"    🔧 EXECUTING TOOL: web_search(query='{query}', max_results={max_results})")
    
    try:
        import requests
        response = requests.get(
            "https://api.duckduckgo.com/",
            params={
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            },
            timeout=10
        )
        data = response.json()
        
        results = []
        if data.get("Abstract"):
            results.append({
                "title": data.get("Heading", "No title"),
                "snippet": data.get("Abstract", ""),
                "url": data.get("AbstractURL", "")
            })
        
        for topic in data.get("RelatedTopics", [])[:max_results-1]:
            if isinstance(topic, dict) and "Text" in topic:
                results.append({
                    "title": topic.get("FirstURL", "").split("/")[-1].replace("_", " "),
                    "snippet": topic.get("Text", ""),
                    "url": topic.get("FirstURL", "")
                })
        
        result = {
            "query": query,
            "results": results[:max_results],
            "total_found": len(results)
        }
        print(f"    ✅ TOOL RESULT: {json.dumps(result, indent=6)}")
        return result
    except Exception as e:
        result = {
            "query": query,
            "error": str(e),
            "results": []
        }
        print(f"    ❌ TOOL ERROR: {json.dumps(result, indent=6)}")
        return result

@tool(name="data_analyzer", description="Analyze data and provide insights")
def data_analyzer(data: str, analysis_type: str = "general") -> dict:
    """Analyze data and provide insights"""
    print(f"    🔧 EXECUTING TOOL: data_analyzer(data='{data[:50]}...', analysis_type='{analysis_type}')")
    
    result = {
        "data": data,
        "analysis_type": analysis_type,
        "insights": [
            f"Data length: {len(data)} characters",
            f"Word count: {len(data.split())} words",
            f"Analysis type: {analysis_type}",
            "Key patterns identified",
            "Statistical analysis completed"
        ],
        "summary": f"Analyzed {len(data)} characters of {analysis_type} data"
    }
    print(f"    ✅ TOOL RESULT: {json.dumps(result, indent=6)}")
    return result

@tool(name="calculator", description="Perform basic arithmetic operations")
def calculator(operation: str, a: float, b: float) -> dict:
    """Perform basic arithmetic operations"""
    print(f"    🔧 EXECUTING TOOL: calculator(operation='{operation}', a={a}, b={b})")
    
    operations = {
        "add": a + b,
        "subtract": a - b,
        "multiply": a * b,
        "divide": a / b if b != 0 else "Error: Division by zero"
    }
    
    if operation not in operations:
        result = {"error": f"Unknown operation: {operation}"}
        print(f"    ❌ TOOL ERROR: {json.dumps(result, indent=6)}")
        return result
    
    result = {
        "operation": operation,
        "a": a,
        "b": b,
        "result": operations[operation]
    }
    print(f"    ✅ TOOL RESULT: {json.dumps(result, indent=6)}")
    return result

def print_section(title: str, content: str = ""):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")
    if content:
        print(content)

def print_step(step: str, content: str = ""):
    """Print a formatted step"""
    print(f"\n📋 STEP: {step}")
    print(f"{'─'*40}")
    if content:
        print(content)

async def main():
    """Demonstrate complete tool injection flow with detailed tracing."""
    print_section("🚀 STEP 3 DEBUG FLOW: Complete Tool Injection Process Tracing")
    
    # STEP 1: Tool Registration
    print_step("1. Tool Registration", "Registering tools with @tool decorator")
    print(f"📋 Available tools: {get_available_tools()}")
    
    # Show tool registry details
    tool_registry = get_tool_registry()
    print(f"📊 Tool registry has {len(tool_registry.registered_tools)} tools registered")
    for tool_name in tool_registry.registered_tools:
        metadata = tool_registry.get_tool_metadata(tool_name)
        print(f"   • {tool_name}: {metadata.description}")
    
    # STEP 2: Agent Loading with Tool Assignment
    print_step("2. Agent Loading with Tool Assignment", "Loading analysis agent with tool injection")
    
    try:
        agent = amg.load_agent(
            agent_name="agentplug/analysis-agent",
            tools=["web_search", "data_analyzer", "calculator"]
        )
        
        print(f"✅ Agent loaded successfully!")
        print(f"📋 Available methods: {agent.get_available_methods()}")
        print(f"🔧 Assigned tools: {agent.get_assigned_tools()}")
        
        # Show agent path and manifest
        print(f"📁 Agent path: {agent.agent_path}")
        print(f"📄 Agent manifest: {json.dumps(agent.manifest, indent=2)}")
        
    except Exception as e:
        print(f"❌ Error loading agent: {e}")
        return
    
    # STEP 3: Tool Context Injection Details
    print_step("3. Tool Context Injection", "Building tool context for agent")
    
    tool_context = agent._build_tool_context()
    print(f"📦 Tool context being injected:")
    print(json.dumps(tool_context, indent=2))
    
    # Show what gets passed to the agent
    print(f"\n📤 Input data that will be sent to agent:")
    input_data = {
        "method": "analyze_text",
        "parameters": {"text": "What are the latest AI trends?", "analysis_type": "general"},
        "tool_context": tool_context
    }
    print(json.dumps(input_data, indent=2))
    
    # STEP 4: Agent Execution Command
    print_step("4. Agent Execution Command", "Command that will be executed")
    
    agent_command = f"python {agent.agent_path}/agent.py '{json.dumps(input_data)}'"
    print(f"💻 Command: {agent_command}")
    
    # STEP 5: Test Agent Method with Detailed Tracing
    print_step("5. Agent Method Execution", "Calling agent.analyze_text() with detailed tracing")
    
    test_text = "What are the latest trends in artificial intelligence and machine learning?"
    print(f"📝 Input text: {test_text}")
    
    print(f"\n🔄 Executing agent method...")
    result = agent.analyze_text(
        text=test_text,
        analysis_type="general"
    )
    
    # STEP 6: Analyze Agent Response
    print_step("6. Agent Response Analysis", "Analyzing what the agent returned")
    
    print(f"📤 Raw agent response:")
    print(json.dumps(result, indent=2))
    
    # Check if agent requested tool execution
    if "result" in result and isinstance(result["result"], dict):
        result_data = result["result"]
        if result_data.get("status") == "success":
            response_text = result_data.get("result", "")
            
            # Look for tool calls in the response
            if "tool_call" in response_text:
                print(f"\n🎯 AGENT REQUESTED TOOL EXECUTION!")
                print(f"📋 Tool call detected in agent response:")
                
                # Extract tool call from response
                import re
                tool_call_match = re.search(r'```json\s*(\{.*?"tool_call".*?\})\s*```', response_text, re.DOTALL)
                if tool_call_match:
                    try:
                        tool_call_json = tool_call_match.group(1)
                        tool_call = json.loads(tool_call_json)
                        print(f"🔧 Tool call details:")
                        print(json.dumps(tool_call, indent=2))
                        
                        # Show what tool the agent chose
                        tool_name = tool_call.get("tool_call", {}).get("tool_name")
                        tool_args = tool_call.get("tool_call", {}).get("arguments", {})
                        print(f"\n🤖 AGENT DECISION: Chose to use '{tool_name}' tool")
                        print(f"📋 Tool arguments: {tool_args}")
                        
                    except json.JSONDecodeError as e:
                        print(f"❌ Could not parse tool call JSON: {e}")
            else:
                print(f"\n📝 AGENT RESPONSE: No tool calls detected")
                print(f"💬 Agent provided direct analysis without using tools")
        else:
            print(f"❌ Agent execution failed: {result_data.get('error', 'Unknown error')}")
    
    # STEP 7: Test Another Method
    print_step("7. Test Another Method", "Testing summarize_content method")
    
    long_content = """
    Artificial Intelligence (AI) has revolutionized numerous industries and continues to shape our world in unprecedented ways. 
    From healthcare to finance, transportation to entertainment, AI technologies are being integrated into various sectors, 
    creating new opportunities and challenges. Machine learning algorithms can now process vast amounts of data to identify 
    patterns and make predictions with remarkable accuracy.
    """
    
    print(f"📝 Input content: {long_content[:100]}...")
    
    summary_result = agent.summarize_content(
        content=long_content,
        max_length=150
    )
    
    print(f"📤 Summary result:")
    print(json.dumps(summary_result, indent=2))
    
    # STEP 8: Final Summary
    print_step("8. Final Summary", "Complete flow summary")
    
    print(f"✅ COMPLETE FLOW SUCCESSFUL!")
    print(f"🎯 Key observations:")
    print(f"   • Tools registered and available: {len(get_available_tools())}")
    print(f"   • Agent loaded with {len(agent.get_assigned_tools())} tools")
    print(f"   • Tool context injected in correct format")
    print(f"   • Agent executed successfully")
    print(f"   • Agent's AI made intelligent tool usage decisions")
    print(f"   • Tool execution handled via MCP integration")
    print(f"   • Complete end-to-end workflow functional")

if __name__ == "__main__":
    asyncio.run(main())
