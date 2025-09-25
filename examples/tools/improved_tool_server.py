#!/usr/bin/env python3
"""
Improved AgentHub Tool Server with Better Tool Definitions

This example demonstrates improved tool definitions and error handling
for better agent performance.
"""

import os
from typing import Any, Dict, List

from agenthub.config import get_config
from agenthub.core.tools import get_available_tools, run_resources, tool


def _load_model_name() -> str:
    """Automatically detect and return the best available model."""
    # Priority order: Check API keys and return corresponding model
    if os.getenv("OPENAI_API_KEY"):
        return "openai:gpt-4o-mini"
    elif os.getenv("ANTHROPIC_API_KEY"):
        return "anthropic:claude-3-5-sonnet-20241022"
    elif os.getenv("GOOGLE_API_KEY"):
        return "google:gemini-1.5-pro"
    elif os.getenv("DEEPSEEK_API_KEY"):
        return "deepseek:deepseek-chat"
    elif os.getenv("FIREWORKS_API_KEY"):
        return "fireworks:accounts/fireworks/models/llama-v3p2-3b-instruct"
    elif os.getenv("COHERE_API_KEY"):
        return "cohere:command-r-plus"
    elif os.getenv("MISTRAL_API_KEY"):
        return "mistral:mistral-large-latest"
    else:
        # Default to Ollama if available
        return "ollama:llama3.2:3b"


# Basic Math Tools
@tool(name="add", description="Add two numbers together")
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    print(f"[TOOL] Adding {a} + {b}")
    return a + b


@tool(name="subtract", description="Subtract the second number from the first")
def subtract(a: int, b: int) -> int:
    """Subtract the second number from the first."""
    print(f"[TOOL] Subtracting {a} - {b}")
    return a - b


@tool(name="multiply", description="Multiply two numbers together")
def multiply(a: int, b: int) -> int:
    """Multiply two numbers together."""
    print(f"[TOOL] Multiplying {a} * {b}")
    return a * b


@tool(name="divide", description="Divide the first number by the second")
def divide(a: int, b: int) -> float:
    """Divide the first number by the second."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    print(f"[TOOL] Dividing {a} / {b}")
    return a / b


# Information Tools
@tool(name="get_current_year", description="Get the current year")
def get_current_year() -> int:
    """Get the current year."""
    import datetime
    year = datetime.datetime.now().year
    print(f"[TOOL] Current year: {year}")
    return year


@tool(name="get_president_info", description="Get information about US President for a given year")
def get_president_info(year: int) -> Dict[str, Any]:
    """
    Get information about the US President for a given year.
    
    Args:
        year (int): The year to get president information for
        
    Returns:
        Dict containing president information
    """
    print(f"[TOOL] Getting president info for year: {year}")
    
    # This is a simplified implementation
    # In a real scenario, you'd query a reliable data source
    president_info = {
        2024: {
            "name": "Joe Biden",
            "party": "Democratic",
            "term_start": "January 20, 2021",
            "term_end": "January 20, 2025"
        },
        2025: {
            "name": "TBD (Election in November 2024)",
            "party": "TBD",
            "term_start": "January 20, 2025",
            "term_end": "January 20, 2029"
        }
    }
    
    if year in president_info:
        return president_info[year]
    else:
        return {
            "error": f"No president information available for year {year}",
            "note": "This tool only has data for recent years"
        }


# Improved Web Search Tool
@tool(name="web_search", description="Search the web for information")
def web_search(query: str, max_results: int = 3) -> List[Dict[str, str]]:
    """
    Search the web for a query and return summarized results.
    
    Args:
        query (str): The search query
        max_results (int): Maximum number of results to return (default: 3)
        
    Returns:
        List of dictionaries with search results
    """
    print(f"[TOOL] Performing web search for: '{query}' (max_results={max_results})")
    
    try:
        from ddgs import DDGS
    except ImportError:
        return [{
            "error": "DuckDuckGo search not available",
            "message": "Please install 'ddgs' package: pip install duckduckgo-search"
        }]
    
    try:
        ddg = DDGS()
        search_results = list(ddg.text(query, max_results=max_results))
        
        results = []
        for result in search_results:
            results.append({
                "title": result.get("title", ""),
                "url": result.get("href", ""),
                "snippet": result.get("body", "")[:200] + "..." if len(result.get("body", "")) > 200 else result.get("body", "")
            })
        
        return results
        
    except Exception as e:
        return [{
            "error": f"Search failed: {str(e)}",
            "message": "Please try a different search query"
        }]


# Utility Tools
@tool(name="format_date", description="Format a date string")
def format_date(year: int, month: int, day: int) -> str:
    """Format a date from year, month, day components."""
    print(f"[TOOL] Formatting date: {year}-{month:02d}-{day:02d}")
    return f"{year}-{month:02d}-{day:02d}"


@tool(name="calculate_age", description="Calculate age from birth year")
def calculate_age(birth_year: int, current_year: int = None) -> int:
    """Calculate age from birth year."""
    if current_year is None:
        import datetime
        current_year = datetime.datetime.now().year
    
    age = current_year - birth_year
    print(f"[TOOL] Age calculation: {current_year} - {birth_year} = {age}")
    return age


def main():
    """Main function to start the tool server."""
    print("🚀 Starting improved tool server...")
    
    # Configure AgentHub
    config = get_config()
    config.model = _load_model_name()
    config.setup_environment_by_default = True
    
    print(f"📋 Available tools: {list(get_available_tools().keys())}")
    print(f"🤖 Using model: {config.model}")
    print("🔄 Starting MCP server...")
    
    # Start the MCP server
    run_resources()


if __name__ == "__main__":
    main()
