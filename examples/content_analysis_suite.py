#!/usr/bin/env python3
"""
Content Analysis Suite: Understand your content at scale.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import agentmanager as amg


def main():
    """Demonstrate content analysis solving real business problems."""
    print("📊 Content Analysis Suite")
    print("=" * 30)
    print("Transform overwhelming text into actionable insights!")
    print()

    # Load analysis agent
    try:
        analysis_agent = amg.load_agent("agentplug/analysis-agent")
    except Exception as e:
        print(f"❌ Analysis agent not found: {e}")
        print("💡 Please set up seed agents first.")
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
            result = analysis_agent.analyze_text(
                text=scenario["content"].strip(),
                analysis_type=scenario["analysis_type"],
            )

            if "result" in result:
                print("   ✅ Analysis complete!")
                print("   📊 Insights:")
                insights = result["result"]

                # Format insights nicely
                if isinstance(insights, dict):
                    for key, value in insights.items():
                        if key == "result":
                            print(f"      {value}")
                        else:
                            print(f"      {key}: {value}")
                else:
                    print(f"      {insights}")

                print()
                print("   💡 Business Impact:")
                print(f"      {scenario['business_value']}")

            else:
                print(f"   ❌ Analysis failed: {result.get('error')}")

        except Exception as e:
            print(f"   💥 Error during analysis: {e}")

        print()
        input("   Press Enter to continue to next scenario...")
        print()

    # Summary of capabilities
    print("🎯 CONTENT ANALYSIS CAPABILITIES DEMONSTRATED:")
    print("=" * 50)
    print("✅ Sentiment analysis for customer feedback")
    print("✅ Urgency detection for support tickets")
    print("✅ Meeting summarization with action items")
    print("✅ Multi-format content processing")
    print("✅ Instant insights and recommendations")
    print("✅ Scalable text analysis")
    print()

    print("💼 BUSINESS VALUE:")
    print("🚀 Process thousands of documents in minutes vs hours")
    print("📊 Extract actionable insights, not just data")
    print("⚡ Consistent quality without human fatigue")
    print("📈 Scale content operations 10x with same team")
    print("🎯 Focus on high-value analysis tasks")

    print("\n🚀 MORE USE CASES:")
    print("• Competitive content analysis")
    print("• Legal document review")
    print("• Research paper summarization")
    print("• Social media sentiment tracking")
    print("• Product feedback categorization")
    print("• Compliance document analysis")


if __name__ == "__main__":
    main()
