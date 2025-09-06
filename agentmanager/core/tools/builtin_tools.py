"""Built-in tools for Phase 2.5."""

import requests
import json
from typing import Dict, Any
from urllib.parse import quote
from .decorator import tool


@tool(name="web_search", description="Search the web for real-time information")
def web_search(query: str, max_results: int = 5) -> dict:
    """
    Search the web for information using DuckDuckGo API.
    
    Args:
        query: Search query string
        max_results: Maximum number of results to return (default: 5)
    
    Returns:
        Dictionary with search results including titles, snippets, and URLs
    """
    try:
        # Use DuckDuckGo Instant Answer API (free, no API key required)
        url = f"https://api.duckduckgo.com/?q={quote(query)}&format=json&no_html=1&skip_disambig=1"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract relevant information
        results = {
            "query": query,
            "abstract": data.get("Abstract", ""),
            "abstract_text": data.get("AbstractText", ""),
            "abstract_source": data.get("AbstractSource", ""),
            "abstract_url": data.get("AbstractURL", ""),
            "related_topics": data.get("RelatedTopics", [])[:max_results],
            "results": []
        }
        
        # Add related topics as results
        for topic in data.get("RelatedTopics", [])[:max_results]:
            if isinstance(topic, dict) and "Text" in topic:
                results["results"].append({
                    "title": topic.get("Text", ""),
                    "snippet": topic.get("Text", ""),
                    "url": topic.get("FirstURL", "")
                })
        
        # If no related topics, create a basic result
        if not results["results"] and results["abstract"]:
            results["results"].append({
                "title": f"Search results for: {query}",
                "snippet": results["abstract"],
                "url": results["abstract_url"]
            })
        
        return results
        
    except Exception as e:
        return {
            "error": f"Web search failed: {str(e)}",
            "query": query,
            "results": []
        }


@tool(name="data_analyzer", description="Analyze data and provide insights")
def data_analyzer(data: str) -> dict:
    """
    Analyze data and provide basic insights.
    
    Args:
        data: Data string to analyze
    
    Returns:
        Dictionary with analysis results
    """
    try:
        # Basic analysis
        word_count = len(data.split())
        char_count = len(data)
        line_count = len(data.split('\n'))
        
        # Simple sentiment analysis (basic keyword matching)
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'love', 'like']
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'dislike', 'poor', 'worst', 'horrible']
        
        words = data.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        sentiment = "neutral"
        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        
        return {
            "insights": f"Analyzed: {data[:100]}{'...' if len(data) > 100 else ''}",
            "word_count": word_count,
            "char_count": char_count,
            "line_count": line_count,
            "sentiment": sentiment,
            "positive_words": positive_count,
            "negative_words": negative_count,
            "status": "success"
        }
    except Exception as e:
        return {
            "error": f"Data analysis failed: {str(e)}",
            "status": "error"
        }
