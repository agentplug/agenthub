#!/usr/bin/env python3
"""
Content Analysis Suite: Understand your content at scale.

USER PAIN POINT: "I have tons of text content (reviews, feedback, documents)
but no time to read and analyze it all manually."

SOLUTION: AgentHub's analysis agent processes any text content and provides
instant insights - sentiment, summaries, key themes, and actionable recommendations.
"""

import sys
from pathlib import Path

# Add the project root to Python path so we can import agentmanager
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agentmanager.runtime.agent_runtime import AgentRuntime  # noqa: E402
from agentmanager.storage.local_storage import LocalStorage  # noqa: E402


def main():
    """Demonstrate content analysis solving real business problems."""
    print("📊 Content Analysis Suite")
    print("=" * 30)
    print("Transform overwhelming text into actionable insights!")
    print()

    # Initialize the system
    storage = LocalStorage()
    runtime = AgentRuntime(storage=storage)

    # Check if analysis agent is available
    if not storage.agent_exists("agentplug", "analysis-agent"):
        print("❌ Analysis agent not found! Please set up seed agents first.")
        return

    # Real-world content analysis scenarios
    scenarios = [
        {
            "title": "🛍️ Customer Review Analysis",
            "pain_point": "Thousands of reviews - need sentiment analysis",
            "content": """
            The product arrived quickly and packaging was excellent. However, quality
            feels cheaper than expected. Customer service was responsive when I had
            questions. Features work as advertised but interface needs improvement.
            Overall decent value but room for improvement.
            """,
            "analysis_type": "sentiment",
            "business_value": "Identify improvement areas and satisfaction drivers",
        },
        {
            "title": "📧 Support Ticket Prioritization",
            "pain_point": "Too many tickets - need urgent issue identification",
            "content": """
            Our entire production system has been down for 2 hours. Multiple customers
            are reporting they cannot access their accounts or complete purchases.
            This is causing significant revenue loss and damaging our reputation.
            We need immediate assistance to resolve this critical outage.
            """,
            "analysis_type": "urgency",
            "business_value": "Auto-prioritize critical issues, reduce response time",
        },
        {
            "title": "📝 Meeting Notes Summarization",
            "pain_point": "Long meeting transcripts - need key points and action items",
            "content": """
            We discussed Q4 roadmap: new user dashboard, mobile app improvements, and
            third-party API integration. Sarah leads dashboard project, target Dec 15th.
            Mobile team needs two more developers. Budget approval pending for APIs.
            Next meeting Friday to review progress and address blockers.
            """,
            "analysis_type": "summary",
            "business_value": "Extract actionable items and key decisions",
        },
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"{i}. {scenario['title']}")
        print(f"   Business Challenge: {scenario['pain_point']}")
        print(f"   Value: {scenario['business_value']}")
        print()
        print("   📄 Content to Analyze:")
        print("   " + "-" * 40)
        content_preview = scenario["content"].strip()[:150] + "..."
        print(f"   {content_preview}")
        print("   " + "-" * 40)
        print()

        try:
            # Analyze the content
            print("   🔍 Analyzing content...")
            result = runtime.execute_agent(
                "agentplug",
                "analysis-agent",
                "analyze_text",
                {
                    "text": scenario["content"].strip(),
                    "analysis_type": scenario["analysis_type"],
                },
            )

            if "result" in result:
                exec_time = result.get("execution_time", 0)
                print(f"   ✅ Analysis completed in {exec_time:.1f}s")
                print()

                analysis = result["result"]
                if isinstance(analysis, dict):
                    print("   📋 Analysis Results:")
                    print("   " + "=" * 25)
                    for key, value in analysis.items():
                        if key != "result":
                            print(f"   {key.title()}: {value}")

                    if "result" in analysis:
                        print(f"   Detailed Analysis: {analysis['result'][:200]}...")
                else:
                    print(f"   📋 Analysis: {str(analysis)[:300]}...")

                print()

                # Get a summary for longer content
                if len(scenario["content"]) > 200:
                    print("   📝 Generating executive summary...")
                    summary_result = runtime.execute_agent(
                        "agentplug",
                        "analysis-agent",
                        "summarize_content",
                        {"content": scenario["content"].strip()},
                    )

                    if "result" in summary_result:
                        summary = summary_result["result"]
                        print(f"   📊 Executive Summary: {summary}")

            else:
                print(f"   ❌ Error: {result.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"   💥 Exception: {e}")

        print()
        input("   Press Enter to continue to next scenario...")
        print()

    # Show the business impact
    print("💼 BUSINESS IMPACT:")
    print("=" * 20)
    print("⚡ Instant Analysis - Process thousands of documents in minutes")
    print("🎯 Actionable Insights - Not just data, but recommendations")
    print("📈 Scale Operations - Handle 10x more content with same team")
    print("⏰ Time Savings - Hours of manual reading reduced to seconds")
    print("🔍 Consistent Quality - No human fatigue or oversight")
    print()
    print("💰 ROI EXAMPLES:")
    print("• Customer Support: 50% faster ticket resolution")
    print("• Content Marketing: Analyze competitor content in minutes")
    print("• Product Management: Process user feedback 10x faster")
    print("• Sales: Prioritize leads based on inquiry sentiment")
    print()
    print("🚀 AgentHub transforms your content into competitive advantage!")


if __name__ == "__main__":
    main()
