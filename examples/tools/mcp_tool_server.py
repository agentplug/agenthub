#!/usr/bin/env python3
"""
AgentHub Tool Server - Framework-level Background Execution Example

This example demonstrates how to use the framework-level run_resources() method
for clean background server execution.
"""

from agenthub.config import get_config
from agenthub.core.tools import get_available_tools, run_resources, tool


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


@tool(name="multiply", description="Multiply two numbers")
def multiply(a: int, b: int) -> int:
    """Multiply two numbers."""
    print(f"[TOOL] Multiplying {a} * {b}")
    return a * b


@tool(name="divide", description="Divide the first number by the second")
def divide(a: float, b: float) -> float:
    """Divide the first number by the second."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    print(f"[TOOL] Dividing {a} / {b}")
    return a / b


@tool(name="greet", description="Generate a personalized greeting")
def greet(name: str, greeting: str = "Hello") -> str:
    """Generate a personalized greeting."""
    print(f"[TOOL] Greeting {name} with '{greeting}'")
    return f"{greeting}, {name}!"


@tool(
    name="get_weather", description="Get weather information for a location (simulated)"
)
def get_weather(location: str, unit: str = "celsius") -> dict:
    """Get weather information for a location (simulated)."""
    print(f"[TOOL] Getting weather for {location} in {unit}")

    # Simulate weather data
    import random

    temp = random.randint(-10, 35) if unit == "celsius" else random.randint(14, 95)
    conditions = ["sunny", "cloudy", "rainy", "snowy", "windy"]
    condition = random.choice(conditions)

    return {
        "location": location,
        "temperature": temp,
        "unit": unit,
        "condition": condition,
        "humidity": random.randint(30, 90),
    }


@tool(name="process_text", description="Process text with various operations")
def process_text(text: str, operation: str = "uppercase") -> str:
    """Process text with various operations."""
    print(f"[TOOL] Processing text with operation: {operation}")

    operations = {
        "uppercase": text.upper(),
        "lowercase": text.lower(),
        "titlecase": text.title(),
        "reverse": text[::-1],
        "wordcount": str(len(text.split())),
        "charcount": str(len(text)),
    }

    if operation not in operations:
        raise ValueError(
            f"Unknown operation: {operation}. Available: {list(operations.keys())}"
        )

    return operations[operation]


def query_rewriter(query: str) -> str:
    import aisuite as ai

    client = ai.Client()
    config = get_config()
    prompt = f"""
DDGS search operators

Query example	Result
cats dogs	Results about cats or dogs
"cats and dogs"	Results for exact term "cats and dogs". If no results are
		found, related results are shown.
cats -dogs	Fewer dogs in results
cats +dogs	More dogs in results
dogs site:example.com	Pages about dogs from example.com
cats -site:example.com	Pages about cats, excluding example.com
intitle:dogs	Page title includes the word "dogs"
inurl:cats	Page url includes the word "cats"
Above is some examples of best practices to write query for search.

This is the query you need to rewrite: {query}
Query must be similar with appropriate suggested operators.
Just return the rewritten query, no other text.
    """
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(
        model="openai:gpt-4o-mini",
        messages=messages,
        temperature=config.llm_temperature,
    )
    return response.choices[0].message.content


@tool(
    name="web_search",
    description="Search the web for a query and return summarized results",
)
def web_search(query: str) -> list:
    """
    Search the web for a query using DuckDuckGo and return summarized results.

    Args:
        query (str): The search query.

    Returns:
        list: A list of dictionaries with 'title', 'url', and 'snippet' for each result.
    """
    query = query_rewriter(query)
    print(f"[TOOL] Performing web search for: '{query}' (max_results=5)")
    try:
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        import aiohttp
        from bs4 import BeautifulSoup
        from ddgs import DDGS
    except ImportError as e:
        raise ImportError(
            "Required packages 'ddgs', 'beautifulsoup4', and 'aiohttp' "
            "are not installed."
        ) from e

    ddg = DDGS()
    search_results = list(ddg.text(query, max_results=5))

    async def fetch_snippet_async(session, url, title):
        """Fetch page content asynchronously"""
        try:
            async with session.get(
                url, timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                # crude text extraction: first 2 paragraphs
                paragraphs = [p.get_text() for p in soup.find_all("p")]
                snippet = " ".join(paragraphs[:2])  # Limit to first 2 paragraphs
                return {
                    "title": title,
                    "url": url,
                    "snippet": (
                        snippet[:500] + "..." if len(snippet) > 500 else snippet
                    ),  # Limit snippet length
                }
        except Exception as e:
            return {"title": title, "url": url, "snippet": f"Error fetching page: {e}"}

    async def process_all_urls():
        """Process all URLs concurrently"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for r in search_results:
                url = r.get("href")
                title = r.get("title", "No title")
                if url:
                    task = fetch_snippet_async(session, url, title)
                    tasks.append(task)
                else:
                    # Handle results without URLs
                    def create_no_url_result(result_title):
                        async def no_url_result():
                            return {
                                "title": result_title,
                                "url": "",
                                "snippet": "No URL available",
                            }

                        return no_url_result

                    tasks.append(create_no_url_result(title)())

            # Execute all requests concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle any exceptions
            processed_results = []
            for result in results:
                if isinstance(result, Exception):
                    processed_results.append(
                        {
                            "title": "Error",
                            "url": "",
                            "snippet": f"Error processing result: {result}",
                        }
                    )
                else:
                    processed_results.append(result)

            return processed_results

    # Run the async function in a thread pool to avoid blocking
    def run_async():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(process_all_urls())
        finally:
            loop.close()

    with ThreadPoolExecutor(max_workers=1) as executor:
        results = executor.submit(run_async).result()

    return {"results": results}


@tool(
    name="compare_numbers",
    description="Compare two numbers and answer which one is larger",
)
def compare_numbers(a: float, b: float) -> str:
    """Compare two numbers and return the larger one."""
    print(f"[TOOL] Comparing {a} and {b}")
    if not isinstance(a, float):
        a = float(a)
    if not isinstance(b, float):
        b = float(b)

    return f"The larger number is {float(max(a, b))}"


if __name__ == "__main__":
    print("🚀 AgentHub Tool Server - Framework Background Execution")
    print("=" * 60)

    # Show available tools
    tools = get_available_tools()
    print("📋 Available tools:")
    for tool_name in tools:
        print(f"  - {tool_name}")

    print("\n✨ Starting server with framework run_resources() method...")

    # Use the clean framework-level run_resources() function

    run_resources()
