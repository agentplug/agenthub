#!/usr/bin/env python3
"""
Better Agent Example with Proper Tool Usage

This example demonstrates how to create an agent that uses tools correctly
and handles the "Who is the US President 2025?" query properly.
"""

import os
from agenthub import load_agent, tool
from agenthub.config import get_config


# Define tools that make sense for the query
@tool(name="get_president_info", description="Get information about US President for a given year")
def get_president_info(year: int) -> dict:
    """
    Get information about the US President for a given year.
    
    Args:
        year (int): The year to get president information for
        
    Returns:
        Dict containing president information
    """
    print(f"[TOOL] Getting president info for year: {year}")
    
    # Simplified data - in reality, you'd query a reliable source
    president_data = {
        2024: {
            "name": "Joe Biden",
            "party": "Democratic", 
            "term_start": "January 20, 2021",
            "term_end": "January 20, 2025",
            "status": "Current President"
        },
        2025: {
            "name": "TBD (Election in November 2024)",
            "party": "TBD",
            "term_start": "January 20, 2025", 
            "term_end": "January 20, 2029",
            "status": "To be determined by 2024 election",
            "note": "The 2024 presidential election will determine who becomes president in 2025"
        }
    }
    
    if year in president_data:
        return president_data[year]
    else:
        return {
            "error": f"No president information available for year {year}",
            "note": "This tool only has data for recent years"
        }


@tool(name="get_current_year", description="Get the current year")
def get_current_year() -> int:
    """Get the current year."""
    import datetime
    year = datetime.datetime.now().year
    print(f"[TOOL] Current year: {year}")
    return year


@tool(name="web_search", description="Search the web for current information")
def web_search(query: str) -> list:
    """
    Search the web for current information.
    
    Args:
        query (str): The search query
        
    Returns:
        List of search results
    """
    print(f"[TOOL] Searching web for: '{query}'")
    
    try:
        from ddgs import DDGS
        ddg = DDGS()
        results = list(ddg.text(query, max_results=3))
        
        formatted_results = []
        for result in results:
            formatted_results.append({
                "title": result.get("title", ""),
                "url": result.get("href", ""),
                "snippet": result.get("body", "")[:200] + "..." if len(result.get("body", "")) > 200 else result.get("body", "")
            })
        
        return formatted_results
        
    except ImportError:
        return [{"error": "Web search not available - install 'duckduckgo-search' package"}]
    except Exception as e:
        return [{"error": f"Search failed: {str(e)}"}]


def create_president_agent():
    """Create an agent that can answer president-related questions."""
    
    # Configure AgentHub
    config = get_config()
    
    # Set model based on available API keys
    if os.getenv("OPENAI_API_KEY"):
        config.model = "openai:gpt-4o-mini"
    elif os.getenv("ANTHROPIC_API_KEY"):
        config.model = "anthropic:claude-3-5-sonnet-20241022"
    else:
        config.model = "ollama:llama3.2:3b"
    
    config.setup_environment_by_default = True
    
    # Create agent with proper tools
    agent = load_agent(
        namespace="examples",
        agent_name="president-agent",
        agent_id="president-agent-001"
    )
    
    return agent


def main():
    """Main function to demonstrate proper agent usage."""
    print("🚀 Creating President Agent...")
    
    try:
        # Create agent
        agent = create_president_agent()
        
        # Test query
        query = "Who is the US President 2025?"
        print(f"❓ Query: {query}")
        print("🔄 Processing...")
        
        # Execute query
        result = agent.solve(query)
        
        print("✅ Result:")
        print(result)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Suggestions:")
        print("1. Make sure you have the required API keys set")
        print("2. Install required packages: pip install duckduckgo-search")
        print("3. Check that the agent is properly configured")


if __name__ == "__main__":
    main()
