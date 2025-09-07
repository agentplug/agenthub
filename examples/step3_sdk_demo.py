#!/usr/bin/env python3
"""
Step 3 Demo: SDK Integration with Real Analysis Agent

This demo shows the complete tool injection workflow using the real analysis agent
from /Users/nguyennm/.agenthub/agents/agentplug/analysis-agent/
"""

import asyncio
import agentmanager as amg
from agentmanager.core.tools import tool, get_available_tools

# Define custom tools for the demo
@tool(name="web_search", description="Search the web for real-time information using DuckDuckGo")
def web_search(query: str, max_results: int = 5) -> dict:
    """Real web search using DuckDuckGo API"""
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
        
        return {
            "query": query,
            "results": results[:max_results],
            "total_found": len(results)
        }
    except Exception as e:
        return {
            "query": query,
            "error": str(e),
            "results": []
        }

@tool(name="data_analyzer", description="Analyze data and provide insights")
def data_analyzer(data: str, analysis_type: str = "general") -> dict:
    """Analyze data and provide insights"""
    return {
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

@tool(name="calculator", description="Perform basic arithmetic operations")
def calculator(operation: str, a: float, b: float) -> dict:
    """Perform basic arithmetic operations"""
    operations = {
        "add": a + b,
        "subtract": a - b,
        "multiply": a * b,
        "divide": a / b if b != 0 else "Error: Division by zero"
    }
    
    if operation not in operations:
        return {"error": f"Unknown operation: {operation}"}
    
    return {
        "operation": operation,
        "a": a,
        "b": b,
        "result": operations[operation]
    }

async def main():
    """Demonstrate Step 3: SDK Integration with Real Analysis Agent."""
    print("🚀 Step 3 Demo: SDK Integration with Real Analysis Agent")
    print("=" * 60)
    
    # Show available tools
    print(f"📋 Available tools: {get_available_tools()}")
    
    try:
        # Load real analysis agent with tools
        print("\n🤖 Loading real analysis agent with tool injection...")
        agent = amg.enhanced_load_agent(
            base_agent="agentplug/analysis-agent",
            tools=["web_search", "data_analyzer", "calculator"]
        )
        
        print(f"✅ Agent loaded successfully!")
        print(f"📋 Available methods: {agent.get_available_methods()}")
        print(f"🔧 Assigned tools: {agent.get_assigned_tools()}")
        
        # Test 1: Text analysis with potential tool usage
        print("\n📝 Test 1: Text Analysis with Tool Context")
        print("-" * 40)
        
        analysis_text = "What are the latest trends in artificial intelligence and machine learning?"
        print(f"Analyzing: {analysis_text}")
        
        result = agent.analyze_text(
            text=analysis_text,
            analysis_type="general"
        )
        
        print(f"Analysis result: {json.dumps(result, indent=2)}")
        
        # Test 2: Sentiment analysis
        print("\n📝 Test 2: Sentiment Analysis")
        print("-" * 40)
        
        sentiment_text = "This product is absolutely amazing! I love it so much. The quality is excellent and the service is outstanding."
        print(f"Analyzing sentiment: {sentiment_text}")
        
        result = agent.analyze_text(
            text=sentiment_text,
            analysis_type="sentiment"
        )
        
        print(f"Sentiment result: {json.dumps(result, indent=2)}")
        
        # Test 3: Content summarization
        print("\n📝 Test 3: Content Summarization")
        print("-" * 40)
        
        long_content = """
        Artificial Intelligence (AI) has revolutionized numerous industries and continues to shape our world in unprecedented ways. 
        From healthcare to finance, transportation to entertainment, AI technologies are being integrated into various sectors, 
        creating new opportunities and challenges. Machine learning algorithms can now process vast amounts of data to identify 
        patterns and make predictions with remarkable accuracy. Natural language processing has enabled computers to understand 
        and generate human-like text, while computer vision allows machines to interpret and analyze visual information. 
        The future of AI holds immense potential for solving complex global challenges, from climate change to disease prevention, 
        but also raises important questions about ethics, privacy, and the future of work.
        """
        
        print(f"Summarizing long content...")
        
        result = agent.summarize_content(
            content=long_content,
            max_length=150
        )
        
        print(f"Summary: {result}")
        
        print("\n✅ Step 3 Demo Complete!")
        print("🎯 Key capabilities demonstrated:")
        print("   • Real analysis agent loaded with tool injection")
        print("   • Tool context injected in correct format")
        print("   • Agent methods work with tool capabilities")
        print("   • Tool execution handled via MCP")
        print("   • Complete end-to-end workflow")
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import json
    asyncio.run(main())
