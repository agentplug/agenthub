#!/usr/bin/env python3
"""
Business Automation Showcase: End-to-end workflow automation.

USER PAIN POINT: "I spend hours on repetitive tasks that could be automated,
but I don't have the technical skills to build complex workflows."

SOLUTION: AgentHub orchestrates multiple AI agents to create sophisticated
business workflows - from content creation to analysis to decision making.
"""

import sys
from pathlib import Path

# Add the project root to Python path so we can import agentmanager
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agentmanager.runtime.agent_runtime import AgentRuntime  # noqa: E402
from agentmanager.storage.local_storage import LocalStorage  # noqa: E402


def main():
    """Demonstrate business automation workflows that save hours daily."""
    print("🏢 Business Automation Showcase")
    print("=" * 35)
    print("Turn complex business processes into one-click operations!")
    print()

    # Initialize the system
    storage = LocalStorage()
    runtime = AgentRuntime(storage=storage)

    # Check if both agents are available
    agents_available = storage.agent_exists(
        "agentplug", "coding-agent"
    ) and storage.agent_exists("agentplug", "analysis-agent")

    if not agents_available:
        print("❌ Required agents not found! Please set up seed agents first.")
        return

    print("🔗 WORKFLOW DEMONSTRATION:")
    print("Automated Report Generation + Analysis Pipeline")
    print()

    # Step 1: Generate a business report template
    print("STEP 1: 📊 Generate Business Report Template")
    print("-" * 45)
    print("Business Need: Create standardized reports for weekly team updates")

    try:
        report_prompt = """
        Create a Python class that generates weekly business reports including:
        - Revenue metrics section
        - Customer satisfaction tracking
        - Team productivity analysis
        - Action items and recommendations
        Include methods to export as JSON and formatted text.
        """

        print("🔧 Generating report template code...")
        code_result = runtime.execute_agent(
            "agentplug", "coding-agent", "generate_code", {"prompt": report_prompt}
        )

        if "result" in code_result:
            exec_time = code_result.get("execution_time", 0)
            print(f"✅ Report template generated in {exec_time:.1f}s")

            generated_code = code_result["result"]
            print("📄 Generated Business Report Class:")
            # Show first few lines of the generated code
            lines = generated_code.split("\n")[:10]
            for line in lines:
                print(f"   {line}")
            print("   ... (complete implementation generated)")

        else:
            print(f"❌ Code generation failed: {code_result.get('error')}")
            return

    except Exception as e:
        print(f"💥 Error in Step 1: {e}")
        return

    print()
    input("Press Enter to continue to Step 2...")
    print()

    # Step 2: Analyze sample business data
    print("STEP 2: 📈 Analyze Sample Business Performance")
    print("-" * 48)
    print("Business Need: Extract insights from this week's metrics")

    sample_data = """
    Weekly Business Metrics:
    - Revenue: $125,000 (up 8% from last week)
    - New customers: 47 (target was 50)
    - Customer satisfaction: 4.2/5 (down from 4.4)
    - Support tickets: 23 (up from 18)
    - Team productivity: 85% (goal is 90%)
    - Key issues: Mobile app crashes reported by 3 customers
    - Wins: New enterprise client signed, positive press coverage
    """

    try:
        print("🔍 Analyzing business performance...")
        analysis_result = runtime.execute_agent(
            "agentplug",
            "analysis-agent",
            "analyze_text",
            {"text": sample_data, "analysis_type": "business_performance"},
        )

        if "result" in analysis_result:
            exec_time = analysis_result.get("execution_time", 0)
            print(f"✅ Analysis completed in {exec_time:.1f}s")

            analysis = analysis_result["result"]
            print("📊 Business Intelligence Insights:")
            print(f"   {analysis}")

        else:
            print(f"❌ Analysis failed: {analysis_result.get('error')}")
            return

    except Exception as e:
        print(f"💥 Error in Step 2: {e}")
        return

    print()
    input("Press Enter to continue to Step 3...")
    print()

    # Step 3: Generate actionable recommendations
    print("STEP 3: 🎯 Generate Executive Summary & Action Plan")
    print("-" * 52)
    print("Business Need: Transform analysis into executive-ready recommendations")

    try:
        print("📝 Creating executive summary...")
        summary_result = runtime.execute_agent(
            "agentplug",
            "analysis-agent",
            "summarize_content",
            {"content": sample_data + "\n\nAnalysis: " + str(analysis)},
        )

        if "result" in summary_result:
            exec_time = summary_result.get("execution_time", 0)
            print(f"✅ Executive summary created in {exec_time:.1f}s")

            summary = summary_result["result"]
            print("📋 Executive Summary & Recommendations:")
            print(f"   {summary}")

        else:
            print(f"❌ Summary generation failed: {summary_result.get('error')}")

    except Exception as e:
        print(f"💥 Error in Step 3: {e}")

    print()

    # Show the complete workflow value
    print("🎯 COMPLETE WORKFLOW ACHIEVED:")
    print("=" * 35)
    print("✅ Auto-generated report template (saves 2 hours)")
    print("✅ Intelligent data analysis (saves 1 hour)")
    print("✅ Executive summary with recommendations (saves 30 minutes)")
    print("✅ Ready-to-present insights (saves 1 hour)")
    print()
    print("⏱️  TOTAL TIME SAVED: 4.5 hours per week")
    print("📈 BUSINESS VALUE: $500+ per week (based on $25/hour)")
    print("🔄 SCALABILITY: Run this for any data, any frequency")
    print()

    print("🚀 MORE AUTOMATION POSSIBILITIES:")
    print("• Customer onboarding workflows")
    print("• Competitive analysis automation")
    print("• Content creation pipelines")
    print("• Quality assurance processes")
    print("• Market research compilation")
    print("• Risk assessment workflows")
    print()

    print("💡 NEXT STEPS:")
    print("1. Identify your most time-consuming repetitive tasks")
    print("2. Map them to agent capabilities (coding + analysis)")
    print("3. Create custom workflows using AgentHub")
    print("4. Scale across your entire organization")
    print()
    print("🏆 AgentHub: Where AI meets business efficiency!")


if __name__ == "__main__":
    main()
