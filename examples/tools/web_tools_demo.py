#!/usr/bin/env python3
"""
Web Tools Demo with Agent Integration

This demo clearly demonstrates the difference between agents with and without web tools.
Each example shows:
1. Agent WITHOUT web tools (limited knowledge)
2. Agent WITH specific web tools (enhanced capabilities)
3. Agent WITH multiple web tools (comprehensive analysis)

Perfect for client demonstrations showing the value of web tools.

Run this demo:
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
    web_analyze
)

# Configure logging to suppress HTTP logs
ah.set_quiet_mode(True)


def print_section_header(title, description=""):
    """Print a formatted section header"""
    print(f"\n{'='*80}")
    print(f"🔍 {title}")
    if description:
        print(f"   {description}")
    print(f"{'='*80}")


def print_comparison_header(without_tools, with_tools):
    """Print comparison header"""
    print(f"\n📊 COMPARISON: {without_tools} vs {with_tools}")
    print("-" * 60)


def run_agent_analysis(agent, question, show_tools=True):
    """Run agent analysis and return formatted result"""
    print(f"📄 Question: {question}")
    print("⏳ Processing...")
    
    result = agent.analyze_text(question)
    status = result.get("result", {}).get("status", "completed")
    analysis = result.get("result", {}).get("summary", "No analysis available")
    tools_used = result.get("result", {}).get("tools_used", [])
    
    print(f"✅ Status: {status}")
    if show_tools and tools_used:
        print(f"🔧 Tools used: {', '.join(tools_used)}")
    elif show_tools:
        print("🔧 Tools used: None")
    
    print(f"📝 Response: {analysis}")
    return result


def print_demo_summary(tool_name, key_benefit):
    """Print a summary of what was demonstrated"""
    print(f"\n💡 DEMO SUMMARY:")
    print(f"   🚫 Without {tool_name}: Limited to training data knowledge")
    print(f"   ✅ With {tool_name}: {key_benefit}")
    print(f"   📈 Impact: Dramatically enhanced agent capabilities!")


def demo_1_web_search_comparison():
    """Demonstrate the difference between agents with and without web search"""
    print_section_header(
        "DEMO 1: Web Search Tool", 
        "Shows how web search enables agents to access current information"
    )
    
    question = "What are the latest changes to H1B visa fees in 2025?"
    
    # Agent WITHOUT web search
    print_comparison_header("Agent WITHOUT Web Search", "Agent WITH Web Search")
    print("\n🚫 WITHOUT Web Search:")
    agent_no_tools = ah.load_agent("agentplug/analysis-agent")
    run_agent_analysis(agent_no_tools, question, show_tools=False)
    
    print("\n" + "="*60)
    
    # Agent WITH web search
    print("\n✅ WITH Web Search:")
    agent_with_search = ah.load_agent("agentplug/analysis-agent", external_tools=["web_search"])
    run_agent_analysis(agent_with_search, question)
    
    print_demo_summary("Web Search", "Access to real-time, current information")


def demo_2_web_scraping_comparison():
    """Demonstrate the difference between agents with and without web scraping"""
    print_section_header(
        "DEMO 2: Web Scraping Tool", 
        "Shows how web scraping enables agents to extract specific content from websites"
    )
    
    question = "Analyze the content from https://httpbin.org/html and tell me what you found"
    
    # Agent WITHOUT web scraping
    print_comparison_header("Agent WITHOUT Web Scraping", "Agent WITH Web Scraping")
    print("\n🚫 WITHOUT Web Scraping:")
    agent_no_tools = ah.load_agent("agentplug/analysis-agent")
    run_agent_analysis(agent_no_tools, question, show_tools=False)
    
    print("\n" + "="*60)
    
    # Agent WITH web scraping
    print("\n✅ WITH Web Scraping:")
    agent_with_scrape = ah.load_agent("agentplug/analysis-agent", external_tools=["web_scrape"])
    run_agent_analysis(agent_with_scrape, question)
    
    print_demo_summary("Web Scraping", "Extract and analyze specific website content")


def demo_3_web_analysis_comparison():
    """Demonstrate the difference between agents with and without web analysis"""
    print_section_header(
        "DEMO 3: Web Analysis Tool", 
        "Shows how web analysis provides sentiment, topics, and readability insights"
    )
    
    question = "Analyze the sentiment, topics, and readability of content from https://kennethreitz.org/essays/2025-08-26-programming_as_spiritual_practice"
    
    # Agent WITHOUT web analysis
    print_comparison_header("Agent WITHOUT Web Analysis", "Agent WITH Web Analysis")
    print("\n🚫 WITHOUT Web Analysis:")
    agent_no_tools = ah.load_agent("agentplug/analysis-agent")
    run_agent_analysis(agent_no_tools, question, show_tools=False)
    
    print("\n" + "="*60)
    
    # Agent WITH web analysis
    print("\n✅ WITH Web Analysis:")
    agent_with_analyze = ah.load_agent("agentplug/analysis-agent", external_tools=["web_analyze"])
    run_agent_analysis(agent_with_analyze, question)
    
    print_demo_summary("Web Analysis", "Sentiment analysis, topic extraction, and readability insights")


def demo_4_web_summarization_comparison():
    """Demonstrate the difference between agents with and without web summarization"""
    print_section_header(
        "DEMO 4: Web Summarization Tool", 
        "Shows how web summarization can extract key points from long articles"
    )
    
    question = "Summarize the key points from https://kennethreitz.org/essays/2025-08-26-programming_as_spiritual_practice"
    
    # Agent WITHOUT web summarization
    print_comparison_header("Agent WITHOUT Web Summarization", "Agent WITH Web Summarization")
    print("\n🚫 WITHOUT Web Summarization:")
    agent_no_tools = ah.load_agent("agentplug/analysis-agent")
    run_agent_analysis(agent_no_tools, question, show_tools=False)
    
    print("\n" + "="*60)
    
    # Agent WITH web summarization
    print("\n✅ WITH Web Summarization:")
    agent_with_summarize = ah.load_agent("agentplug/analysis-agent", external_tools=["web_summarize"])
    run_agent_analysis(agent_with_summarize, question)
    
    print_demo_summary("Web Summarization", "Extract key points from long articles and documents")


def demo_5_multiple_tools_workflow():
    """Demonstrate how multiple web tools work together"""
    print_section_header(
        "DEMO 5: Multiple Web Tools Working Together", 
        "Shows how agents can use multiple web tools for comprehensive analysis"
    )
    
    question = "Research the latest trends in Python programming, analyze the content, and provide a comprehensive summary"
    
    print("\n🔄 MULTI-TOOL WORKFLOW:")
    print("   1. Search for current information")
    print("   2. Scrape relevant content")
    print("   3. Analyze sentiment and topics")
    print("   4. Summarize key findings")
    
    agent_multi_tools = ah.load_agent(
        "agentplug/analysis-agent", 
        external_tools=["web_search", "web_scrape", "web_analyze", "web_summarize"],
        monitoring=True
    )
    
    print(f"\n📄 Question: {question}")
    print("⏳ Processing with multiple tools...")
    
    result = agent_multi_tools.analyze_text(question)
    status = result.get("result", {}).get("status", "completed")
    analysis = result.get("result", {}).get("summary", "No analysis available")
    tools_used = result.get("result", {}).get("tools_used", [])
    
    print(f"✅ Status: {status}")
    print(f"🔧 Tools used: {', '.join(tools_used) if tools_used else 'None'}")
    print(f"🛠️  Total tools available: {len(agent_multi_tools.assigned_tools)}")
    print(f"📝 Comprehensive Analysis: {analysis}")


def demo_6_advanced_workflow():
    """Demonstrate advanced multi-tool workflow with chaining"""
    print_section_header(
        "DEMO 6: Advanced Multi-Tool Workflow", 
        "Shows how multiple tools work together for comprehensive analysis"
    )
    
    question = "Find and analyze the latest information about Taylor Swift new album"
    
    print("\n🔄 ADVANCED WORKFLOW:")
    print("   1. Search for relevant articles")
    print("   2. Scrape content from top results")
    print("   3. Analyze the scraped content")
    print("   4. Summarize key insights")
    
    agent_advanced = ah.load_agent("agentplug/analysis-agent", external_tools=["web_search", "web_scrape", "web_analyze", "web_summarize"])
    
    print(f"\n📄 Question: {question}")
    print("⏳ Processing with advanced workflow...")
    
    result = agent_advanced.analyze_text(question)
    status = result.get("result", {}).get("status", "completed")
    analysis = result.get("result", {}).get("summary", "No analysis available")
    tools_used = result.get("result", {}).get("tools_used", [])
    
    print(f"✅ Status: {status}")
    print(f"🔧 Tools used: {', '.join(tools_used) if tools_used else 'None'}")
    print(f"📝 Analysis: {analysis}")


def demo_7_real_world_scenario():
    """Demonstrate a real-world business scenario"""
    print_section_header(
        "DEMO 7: Real-World Business Scenario", 
        "Competitive analysis using multiple web tools"
    )
    
    scenario = """
    BUSINESS SCENARIO: Your company wants to understand the competitive landscape
    for AI-powered customer service tools. You need to:
    1. Research current market leaders
    2. Analyze their product descriptions and features
    3. Understand market sentiment
    4. Provide actionable insights
    """
    
    print(scenario)
    
    question = """
    Conduct a competitive analysis of AI-powered customer service tools. 
    Research the top 3 companies, analyze their product descriptions, 
    assess market sentiment, and provide strategic recommendations.
    """
    
    agent_business = ah.load_agent(
        "agentplug/analysis-agent", 
        external_tools=["web_search", "web_scrape", "web_analyze", "web_summarize"],
        monitoring=True
    )
    
    print(f"📄 Business Question: {question}")
    print("⏳ Processing comprehensive competitive analysis...")
    
    result = agent_business.analyze_text(question)
    status = result.get("result", {}).get("status", "completed")
    analysis = result.get("result", {}).get("summary", "No analysis available")
    tools_used = result.get("result", {}).get("tools_used", [])
    
    print(f"✅ Status: {status}")
    print(f"🔧 Tools used: {', '.join(tools_used) if tools_used else 'None'}")
    print(f"📊 Business Analysis: {analysis}")


def wait_for_key(message="Press Enter to continue..."):
    """Wait for user input before continuing"""
    input(f"\n⏸️  {message}")


def quick_demo():
    """Run a quick demo showing key differences"""
    print("🚀 AgentHub Web Tools - Quick Demo")
    print("=" * 50)
    print("This quick demo shows the key difference between agents")
    print("with and without web tools.")
    print("=" * 50)
    
    try:
        # Quick comparison demo
        demo_1_web_search_comparison()
        wait_for_key("Press Enter to see web scraping comparison...")
        
        demo_2_web_scraping_comparison()
        wait_for_key("Press Enter to see multiple tools working together...")
        
        demo_5_multiple_tools_workflow()
        
        print("\n🎉 Quick demo completed!")
        print("💡 Key takeaway: Web tools dramatically enhance agent capabilities!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


def full_demo():
    """Run the complete web tools demo with agent integration."""
    print("🚀 AgentHub Web Tools - Complete Demo")
    print("=" * 60)
    print("This comprehensive demo shows all web tools in action")
    print("and demonstrates their real-world business value.")
    print("=" * 60)
    
    try:
        # Run all demos with pauses
        demo_1_web_search_comparison()
        wait_for_key("Press Enter to continue to web scraping demo...")
        
        demo_2_web_scraping_comparison()
        wait_for_key("Press Enter to continue to web analysis demo...")
        
        demo_3_web_analysis_comparison()
        wait_for_key("Press Enter to continue to web summarization demo...")
        
        demo_4_web_summarization_comparison()
        wait_for_key("Press Enter to continue to multiple tools demo...")
        
        demo_5_multiple_tools_workflow()
        wait_for_key("Press Enter to continue to advanced workflow demo...")
        
        demo_6_advanced_workflow()
        wait_for_key("Press Enter to continue to real-world scenario...")
        
        demo_7_real_world_scenario()
        
        print("\n🎉 Complete demo finished successfully!")
        print("💡 All web tools are now ready for production use!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main demo selector"""
    print("🔧 AgentHub Web Tools Demo")
    print("=" * 40)
    print("Choose your demo type:")
    print("1. Quick Demo (5 minutes) - Key comparisons")
    print("2. Full Demo (15 minutes) - Complete showcase")
    print("3. Individual Tool Tests")
    print("=" * 40)
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            quick_demo()
            break
        elif choice == "2":
            full_demo()
            break
        elif choice == "3":
            test_direct_tool_usage()
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    # Run the main demo selector
        main()
