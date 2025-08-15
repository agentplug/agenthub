#!/usr/bin/env python3
"""
Code Generation Workflow: From idea to implementation in seconds.

USER PAIN POINT: "I need to quickly prototype code but I'm not sure about syntax,
best practices, or how to structure the solution."

SOLUTION: AgentHub's coding agent generates clean, documented code with explanations,
turning your ideas into working implementations instantly.
"""

import sys
from pathlib import Path

# Add the project root to Python path so we can import agentmanager
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agentmanager.runtime.agent_runtime import AgentRuntime  # noqa: E402
from agentmanager.storage.local_storage import LocalStorage  # noqa: E402


def main():
    """Demonstrate code generation workflow solving real user pain points."""
    print("💡 Code Generation Workflow")
    print("=" * 40)
    print("Transform your ideas into working code in seconds!")
    print()

    # Initialize the system
    storage = LocalStorage()
    runtime = AgentRuntime(storage=storage)

    # Check if coding agent is available
    if not storage.agent_exists("agentplug", "coding-agent"):
        print("❌ Coding agent not found! Please set up seed agents first.")
        return

    # Real-world scenarios users face daily
    scenarios = [
        {
            "title": "🚀 API Client Creation",
            "pain_point": "Need REST API client with proper error handling",
            "prompt": "Create Python class for REST API calls with error handling",
            "value": "Saves hours of research and debugging",
        },
        {
            "title": "📊 Data Processing Pipeline",
            "pain_point": "Need to process CSV data but struggling with pandas syntax",
            "prompt": "Create function to read CSV, filter and export data",
            "value": "Eliminates need to search documentation",
        },
        {
            "title": "🔐 Input Validation System",
            "pain_point": "Need secure input validation with best practices",
            "prompt": "Create input validation class for email, phone, password",
            "value": "Prevents security vulnerabilities",
        },
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['title']}")
        print(f"   Pain Point: {scenario['pain_point']}")
        print(f"   Business Value: {scenario['value']}")
        print()

        try:
            # Generate code solution
            print("   🔧 Generating solution...")
            result = runtime.execute_agent(
                "agentplug",
                "coding-agent",
                "generate_code",
                {"prompt": scenario["prompt"]},
            )

            if "result" in result:
                exec_time = result.get("execution_time", 0)
                print(f"   ✅ Generated in {exec_time:.1f}s")

                # Show first part of generated code
                code = result["result"]
                lines = code.split("\n")
                preview_lines = lines[:15]  # Show first 15 lines

                print("   📝 Generated Code Preview:")
                print("   " + "-" * 35)
                for line in preview_lines:
                    print(f"   {line}")

                if len(lines) > 15:
                    print(f"   ... ({len(lines) - 15} more lines)")

                print("   " + "-" * 35)

                # Get explanation
                print("   💭 Getting code explanation...")
                explanation_result = runtime.execute_agent(
                    "agentplug", "coding-agent", "explain_code", {"code": code}
                )

                if "result" in explanation_result:
                    explanation = explanation_result["result"]
                    # Show brief explanation
                    print(f"   📚 Explanation: {explanation[:200]}...")

            else:
                print(f"   ❌ Error: {result.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"   💥 Exception: {e}")

        print()
        input("   Press Enter to continue to next scenario...")
        print()

    # Summary of value delivered
    print("🎯 VALUE DELIVERED:")
    print("=" * 20)
    print("✅ Instant code generation - no more blank page syndrome")
    print("✅ Best practices built-in - secure, maintainable code")
    print("✅ Complete with explanations - learn while you build")
    print("✅ Multiple scenarios covered - from APIs to data processing")
    print("✅ Production-ready quality - not just snippets")
    print()
    print("💰 TIME SAVED: Hours of coding, research, and debugging")
    print("🛡️  RISK REDUCED: Following security and performance best practices")
    print("📈 PRODUCTIVITY: From idea to implementation in under 30 seconds")
    print()
    print("🚀 AgentHub turns you into a coding powerhouse!")


if __name__ == "__main__":
    main()
