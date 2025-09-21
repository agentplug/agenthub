#!/usr/bin/env python3
"""
Web Tools Demo with Agent Integration

Demonstrates how to load an agent and pass it built-in web tools
for search, scraping, analysis, and summarization. This example shows
how agents can use these tools for comprehensive web research and content analysis.

Run this demo to see the web tools in action with agents:
    python examples/tools/web_tools_demo.py
"""

import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import agenthub as ah
from agenthub.core.tools.builtin.web import (
    web_search,
    web_scrape,
    web_summarize,
    web_analyze,
    web_search_and_scrape
)

# Configure logging to suppress HTTP logs
ah.set_quiet_mode(True)


def example_1_basic_agent():
    """Load agent without web tools"""
    print("📋 Example 1: Basic Agent (no web tools)")
    question = "What are the latest trends in artificial intelligence?"
    print(f"📄 Input: {question}")
    agent = ah.load_agent("agentplug/analysis-agent")
    result = agent.analyze_text(question)
    # ================================================
    status = result.get("result", {}).get("status", "completed")
    analysis = result.get("result", {}).get("summary", "No analysis")
    print(f"✅ Status: {status}")
    print(f"📄 Analysis: {analysis}")
    return result


def example_2_agent_with_web_search():
    """Load agent with web search tool"""
    print("\n📋 Example 2: Agent with Web Search Tool")
    agent = ah.load_agent("agentplug/analysis-agent", external_tools=["web_search"])
    question = "What are the latest trends in artificial intelligence in 2024?"
    print(f"📄 Input: {question}")
    result = agent.analyze_text(question)
    # ================================================
    status = result.get("result", {}).get("status", "completed")
    analysis = result.get("result", {}).get("summary", "No analysis")
    tools_used = result.get("result", {}).get("tools_used", [])
    print(f"✅ Status: {status}")
    print(f"🔧 Tools used: {tools_used}")
    print(f"📄 Analysis: {analysis}")
    return result


def example_3_agent_with_web_scrape():
    """Load agent with web scraping tool"""
    print("\n📋 Example 3: Agent with Web Scraping Tool")
    agent = ah.load_agent("agentplug/analysis-agent", external_tools=["web_scrape"])
    question = "Use the web_scrape tool to get content from https://httpbin.org/html and tell me what you found"
    print(f"📄 Input: {question}")
    result = agent.analyze_text(question)
    # ================================================
    status = result.get("result", {}).get("status", "completed")
    analysis = result.get("result", {}).get("summary", "No analysis")
    tools_used = result.get("result", {}).get("tools_used", [])
    print(f"✅ Status: {status}")
    print(f"🔧 Tools used: {tools_used}")
    print(f"📄 Analysis: {analysis}")
    return result


def example_4_agent_with_web_analyze():
    """Load agent with web analysis tool"""
    print("\n📋 Example 4: Agent with Web Analysis Tool")
    agent = ah.load_agent("agentplug/analysis-agent", external_tools=["web_analyze"])
    question = "Use the web_analyze tool to analyze https://httpbin.org/html and tell me about its sentiment, topics, and readability"
    print(f"📄 Input: {question}")
    result = agent.analyze_text(question)
    # ================================================
    status = result.get("result", {}).get("status", "completed")
    analysis = result.get("result", {}).get("summary", "No analysis")
    tools_used = result.get("result", {}).get("tools_used", [])
    print(f"✅ Status: {status}")
    print(f"🔧 Tools used: {tools_used}")
    print(f"📄 Analysis: {analysis}")
    return result


def example_5_agent_with_web_summarize():
    """Load agent with web summarization tool"""
    print("\n📋 Example 5: Agent with Web Summarization Tool")
    agent = ah.load_agent("agentplug/analysis-agent", external_tools=["web_summarize"])
    question = "Use the web_summarize tool to summarize https://httpbin.org/html and provide key points"
    print(f"📄 Input: {question}")
    result = agent.analyze_text(question)
    # ================================================
    status = result.get("result", {}).get("status", "completed")
    analysis = result.get("result", {}).get("summary", "No analysis")
    tools_used = result.get("result", {}).get("tools_used", [])
    print(f"✅ Status: {status}")
    print(f"🔧 Tools used: {tools_used}")
    print(f"📄 Analysis: {analysis}")
    return result


def example_6_agent_with_multiple_web_tools():
    """Load agent with multiple web tools"""
    print("\n📋 Example 6: Agent with Multiple Web Tools")
    agent = ah.load_agent(
        "agentplug/analysis-agent", 
        external_tools=["web_search", "web_scrape", "web_analyze", "web_summarize"],
        monitoring=True
    )
    question = "Research the latest trends in machine learning, scrape some content, analyze it, and provide a summary"
    print(f"📄 Input: {question}")
    result = agent.analyze_text(question)
    # ================================================
    status = result.get("result", {}).get("status", "completed")
    analysis = result.get("result", {}).get("summary", "No analysis")
    tools_used = result.get("result", {}).get("tools_used", [])
    print(f"✅ Status: {status}")
    print(f"🔧 Tools used: {tools_used}")
    print(f"🛠️  Tools available: {len(agent.assigned_tools)} tools")
    print(f"📄 Analysis: {analysis}")
    return result


def example_7_agent_with_web_search_and_scrape():
    """Load agent with combined search and scrape tool"""
    print("\n📋 Example 7: Agent with Search and Scrape Tool")
    agent = ah.load_agent("agentplug/analysis-agent", external_tools=["web_search_and_scrape"])
    question = "Search for information about Python programming best practices and scrape the content from the top results"
    print(f"📄 Input: {question}")
    result = agent.analyze_text(question)
    # ================================================
    status = result.get("result", {}).get("status", "completed")
    analysis = result.get("result", {}).get("summary", "No analysis")
    tools_used = result.get("result", {}).get("tools_used", [])
    print(f"✅ Status: {status}")
    print(f"🔧 Tools used: {tools_used}")
    print(f"📄 Analysis: {analysis}")
    return result


def wait_for_key(message="Press Enter to continue to next example..."):
    """Wait for user input before continuing"""
    input(f"\n⏸️  {message}")


def main():
    """Run the complete web tools demo with agent integration."""
    print("🚀 AgentHub Web Tools Demo with Agent Integration")
    print("=" * 60)
    print("This demo shows how to load agents with built-in web tools")
    print("for search, scraping, analysis, and summarization.")
    print("=" * 60)
    
    try:
        # Run examples with pauses
        example_1_basic_agent()
        wait_for_key("Press Enter to continue to Example 2...")
        
        example_2_agent_with_web_search()
        wait_for_key("Press Enter to continue to Example 3...")
        
        example_3_agent_with_web_scrape()
        wait_for_key("Press Enter to continue to Example 4...")
        
        example_4_agent_with_web_analyze()
        wait_for_key("Press Enter to continue to Example 5...")
        
        example_5_agent_with_web_summarize()
        wait_for_key("Press Enter to continue to Example 6...")
        
        example_6_agent_with_multiple_web_tools()
        wait_for_key("Press Enter to continue to Example 7...")
        
        example_7_agent_with_web_search_and_scrape()
        wait_for_key("Press Enter to finish...")
        
        print("\n🎉 All examples completed successfully!")
        print("Copy any function above to use in your own code.")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


def test_direct_tool_usage():
    """Test direct tool usage to verify tools are working"""
    print("🧪 Testing Direct Tool Usage")
    print("=" * 50)
    
    # Test web search directly
    print("\n1. Testing web_search directly:")
    result = web_search("python programming", max_results=3)
    print(f"   Success: {result['success']}")
    if result['success']:
        print(f"   Results: {len(result.get('results', []))}")
    else:
        print(f"   Error: {result.get('error', 'Unknown error')}")
    
    # Test web scrape directly
    print("\n2. Testing web_scrape directly:")
    result = web_scrape("https://httpbin.org/html", extract_text=True)
    print(f"   Success: {result['success']}")
    if result['success']:
        print(f"   Content length: {result.get('data', {}).get('content_length', 0)}")
    else:
        print(f"   Error: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    # Uncomment the line below to test direct tool usage
    # test_direct_tool_usage()
    
    # Uncomment the line below to run just one example for testing
    # example_3_agent_with_web_scrape()
    
    # Run the full demo
    main()
