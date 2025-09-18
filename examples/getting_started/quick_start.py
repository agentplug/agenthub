#!/usr/bin/env python3
"""
AgentHub Quick Start - Simple Examples

This file demonstrates the most common AgentHub usage patterns
in simple, executable examples. Perfect for beginners!
"""

import agenthub as ah


def example_1_basic_agent():
    """Load and use an agent without any tools."""
    print("📋 Example 1: Basic Agent")
    print("-" * 30)

    # Load an agent
    agent = ah.load_agent("agentplug/analysis-agent")

    # Use the agent
    result = agent.analyze_text("This is a great product! I love using it.")
    print(f"Result: {result}")
    print()


def example_2_agent_with_tools():
    """Load an agent with external tools."""
    print("📋 Example 2: Agent with Tools")
    print("-" * 30)

    # Load an agent with math tools
    agent = ah.load_agent(
        "agentplug/analysis-agent", external_tools=["add", "multiply"]
    )

    # Ask the agent to do math
    result = agent.analyze_text("What is 15 times 7?")
    print(f"Result: {result}")
    print()


def example_3_file_processing():
    """Process a file using an agent (demonstrates path resolution)."""
    print("📋 Example 3: File Processing")
    print("-" * 30)

    # Load an agent that can process files
    agent = ah.load_agent("agentplug/scientific-paper-analyzer")

    # Process a file (relative path will be automatically resolved)
    result = agent.analyze_paper("sample_docs/2501.12948v1.pdf")
    print(f"Result: {result}")
    print()


def example_4_multiple_agents():
    """Use multiple agents for different tasks."""
    print("📋 Example 4: Multiple Agents")
    print("-" * 30)

    # Load different agents
    coding_agent = ah.load_agent("agentplug/coding-agent")
    analysis_agent = ah.load_agent("agentplug/analysis-agent")

    # Use coding agent
    code_result = coding_agent.generate_code(
        "Create a Python function to calculate fibonacci numbers"
    )
    print(f"Coding Result: {code_result}")

    # Use analysis agent
    analysis_result = analysis_agent.analyze_text(
        "The user interface is intuitive and easy to use."
    )
    print(f"Analysis Result: {analysis_result}")
    print()


def main():
    """Run all examples."""
    print("🚀 AgentHub Quick Start Examples")
    print("=" * 50)
    print("These examples show the most common usage patterns.\n")

    try:
        example_1_basic_agent()
        example_2_agent_with_tools()
        example_3_file_processing()
        example_4_multiple_agents()

        print("🎉 All examples completed successfully!")
        print("\n💡 Next Steps:")
        print("• Try modifying the examples above")
        print("• Check out examples/tools/ for more advanced usage")
        print("• Read the documentation for more features")

    except Exception as e:
        print(f"❌ Error running examples: {e}")
        print("Make sure you have the required agents installed.")


if __name__ == "__main__":
    main()
