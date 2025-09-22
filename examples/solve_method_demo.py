#!/usr/bin/env python3
"""
Phase 3.2 Intelligent Solve Method Demo

This example demonstrates the new solve() method functionality.
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "agenthub"))

from agenthub.core.agents import AgentSolveInterface, SolveResult
from agenthub.core.llm import LLMDecisionEngine


class DemoAgent(AgentSolveInterface):
    """Demo agent that implements custom solve method."""

    def __init__(self):
        self.name = "Demo Agent"
        self.capabilities = [
            "analyze_data",
            "generate_report",
            "search_information",
            "process_text",
        ]

    def solve(self, query: str, context=None, **kwargs):
        """Custom solve method that handles queries intelligently."""
        query_lower = query.lower()

        if "analyze" in query_lower or "data" in query_lower:
            return self._analyze_data(query, context)
        elif "report" in query_lower or "generate" in query_lower:
            return self._generate_report(query, context)
        elif "search" in query_lower or "find" in query_lower:
            return self._search_information(query, context)
        elif "process" in query_lower or "text" in query_lower:
            return self._process_text(query, context)
        else:
            return (
                f"I can help with: {', '.join(self.capabilities)}. "
                f"Your query: '{query}'"
            )

    def _analyze_data(self, query: str, context=None):
        """Analyze data based on query."""
        return (
            f"📊 Data Analysis Result: Analyzed '{query}' and found "
            f"interesting patterns."
        )

    def _generate_report(self, query: str, context=None):
        """Generate a report based on query."""
        return f"📋 Report Generated: Created comprehensive report for '{query}'."

    def _search_information(self, query: str, context=None):
        """Search for information based on query."""
        return f"🔍 Search Results: Found relevant information for '{query}'."

    def _process_text(self, query: str, context=None):
        """Process text based on query."""
        return f"📝 Text Processing: Processed '{query}' with advanced NLP techniques."


def demo_solve_result():
    """Demonstrate SolveResult functionality."""
    print("🔍 Demo: SolveResult Functionality")
    print("=" * 50)

    # Create a successful result
    success_result = SolveResult(
        result="Analysis completed successfully",
        success=True,
        method_used="analyze_data",
        method_type="custom",
        confidence=0.95,
        reasoning="Custom solve method selected analyze_data based on query keywords",
        execution_time=0.5,
        parameters_used={"query": "analyze sales data", "format": "json"},
    )

    print("✅ Successful Result:")
    print(f"   Result: {success_result.result}")
    print(f"   Method: {success_result.method_used}")
    print(f"   Confidence: {success_result.confidence}")
    print(f"   Summary: {success_result.get_summary()}")
    print()

    # Create an error result
    error_result = SolveResult(
        result=None,
        success=False,
        error="Method not found",
        error_type="MethodNotFoundError",
        execution_time=0.1,
    )

    print("❌ Error Result:")
    print(f"   Error: {error_result.get_error_message()}")
    print(f"   Summary: {error_result.get_summary()}")
    print()

    # Test dictionary conversion
    result_dict = success_result.to_dict()
    print("📋 Dictionary Representation:")
    print(f"   Keys: {list(result_dict.keys())}")
    print()


def demo_custom_solve():
    """Demonstrate custom solve method."""
    print("🤖 Demo: Custom Solve Method")
    print("=" * 50)

    agent = DemoAgent()

    # Test different types of queries
    queries = [
        "analyze the sales data from last quarter",
        "generate a comprehensive report on market trends",
        "search for information about AI developments",
        "process this text document for sentiment analysis",
        "help me with something random",
    ]

    for query in queries:
        print(f"Query: '{query}'")
        result = agent.solve(query)
        print(f"Result: {result}")
        print()

    # Test with context
    print("With Context:")
    context = {"user_id": "demo_user", "session": "test"}
    result = agent.solve("analyze user behavior", context)
    print("Query: 'analyze user behavior'")
    print(f"Result: {result}")
    print()


def demo_llm_decision_engine():
    """Demonstrate LLM Decision Engine."""
    print("🧠 Demo: LLM Decision Engine")
    print("=" * 50)

    engine = LLMDecisionEngine()

    # Mock agent methods
    methods = [
        {
            "name": "analyze_data",
            "description": "Analyze data and provide insights",
            "parameters": {
                "data": {"type": "string", "description": "Data to analyze"},
                "format": {
                    "type": "string",
                    "description": "Output format",
                    "optional": True,
                },
            },
        },
        {
            "name": "generate_report",
            "description": "Generate a detailed report",
            "parameters": {
                "title": {"type": "string", "description": "Report title"},
                "sections": {
                    "type": "list",
                    "description": "Report sections",
                    "optional": True,
                },
            },
        },
        {
            "name": "search_web",
            "description": "Search the web for information",
            "parameters": {
                "query": {"type": "string", "description": "Search query"},
                "limit": {
                    "type": "integer",
                    "description": "Number of results",
                    "optional": True,
                },
            },
        },
    ]

    # Test method selection
    test_queries = [
        "I need to analyze my sales data",
        "Generate a report about market trends",
        "Search for information about AI",
    ]

    for query in test_queries:
        print(f"Query: '{query}'")
        method_name, confidence, reasoning = engine.select_method(query, methods)
        print(f"Selected Method: {method_name}")
        print(f"Confidence: {confidence:.2f}")
        print(f"Reasoning: {reasoning}")
        print()

    # Test parameter extraction
    print("Parameter Extraction:")
    method_parameters = {
        "data": {"type": "string", "description": "Data to analyze"},
        "format": {"type": "string", "description": "Output format", "optional": True},
    }

    query = "analyze my sales data in JSON format"
    params, confidence, reasoning = engine.extract_parameters(
        query, "analyze_data", method_parameters
    )

    print(f"Query: '{query}'")
    print(f"Extracted Parameters: {params}")
    print(f"Confidence: {confidence:.2f}")
    print(f"Reasoning: {reasoning}")
    print()


def demo_integration():
    """Demonstrate integration of all components."""
    print("🔗 Demo: Component Integration")
    print("=" * 50)

    # Test that all components work together
    from agenthub.core.agents import SolveResult
    from agenthub.core.llm import LLMDecisionEngine

    # Create components
    agent = DemoAgent()
    engine = LLMDecisionEngine()

    # Test solve method
    result = agent.solve("analyze customer feedback")
    print(f"Agent solve result: {result}")

    # Test decision engine
    methods = [{"name": "test_method", "description": "Test method", "parameters": {}}]
    method_name, confidence, reasoning = engine.select_method("test query", methods)
    print(f"Selected method: {method_name}")

    # Test result creation
    solve_result = SolveResult(
        result=result, success=True, method_used="analyze_data", method_type="custom"
    )
    print(f"Solve result summary: {solve_result.get_summary()}")
    print()


def main():
    """Run all demos."""
    print("🚀 Phase 3.2 Intelligent Solve Method Demo")
    print("=" * 60)
    print()

    try:
        demo_solve_result()
        demo_custom_solve()
        demo_llm_decision_engine()
        demo_integration()

        print("🎉 All demos completed successfully!")
        print()
        print("Key Features Demonstrated:")
        print("✅ SolveResult - Standardized result format")
        print("✅ AgentSolveInterface - Custom solve method interface")
        print("✅ LLMDecisionEngine - Intelligent method selection")
        print("✅ Component Integration - All parts working together")
        print()
        print("Next Steps:")
        print("1. Implement the solve() method in AgentWrapper")
        print("2. Test with real agents")
        print("3. Add comprehensive error handling")
        print("4. Implement caching for performance")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
