#!/usr/bin/env python3
"""
Business Automation Showcase - Advanced Workflow Example

This example demonstrates how to create automated business workflows
using multiple agents working together.
"""

import agenthub as ah


def main():
    """Demonstrate a business automation workflow."""
    print("🏢 Business Automation Showcase")
    print("=" * 40)
    print(
        "This example shows how to automate business processes using multiple agents.\n"
    )

    # Step 1: Generate business report
    print("📊 Step 1: Generate Business Report")
    print("-" * 35)

    try:
        # Load coding agent with tools
        coding_agent = ah.load_agent(
            "agentplug/coding-agent", external_tools=["add", "multiply"]
        )

        # Generate a business report template
        report_prompt = """
        Create a Python class for generating weekly business reports with:
        - Revenue metrics calculation
        - Customer satisfaction tracking
        - Team productivity analysis
        - Action items and recommendations
        Include methods to export as JSON and formatted text.
        """

        print("🔧 Generating business report template...")
        code_result = coding_agent.generate_code(report_prompt)
        print("✅ Report template generated")
        print(f"📄 Code length: {len(str(code_result))} characters")

    except Exception as e:
        print(f"⚠️  Could not generate report: {e}")

    print()

    # Step 2: Analyze customer feedback
    print("📈 Step 2: Analyze Customer Feedback")
    print("-" * 35)

    try:
        # Load analysis agent with tools
        analysis_agent = ah.load_agent(
            "agentplug/analysis-agent",
            external_tools=["process_text", "add", "multiply"],
        )

        # Sample customer feedback
        feedback = """
        The new mobile app is fantastic! The user interface is intuitive and
        the performance is much better than the previous version. However, I
        noticed some issues with the payment processing - it sometimes takes
        3-4 attempts to complete a transaction. The customer support team
        was very helpful when I contacted them about this issue. Overall,
        I'm satisfied but hope the payment bugs get fixed soon.
        """

        print("🔍 Analyzing customer feedback...")
        analysis_result = analysis_agent.analyze_text(feedback)
        print("✅ Feedback analysis completed")
        print(f"📊 Analysis result: {str(analysis_result)[:100]}...")

    except Exception as e:
        print(f"⚠️  Could not analyze feedback: {e}")

    print()

    # Step 3: Generate recommendations
    print("💡 Step 3: Generate Business Recommendations")
    print("-" * 40)

    try:
        # Use analysis agent to generate recommendations
        recommendations_prompt = """
        Based on the customer feedback analysis, generate actionable business
        recommendations for improving the mobile app and customer experience.
        Focus on:
        - Payment processing improvements
        - Customer support enhancements
        - User interface optimizations
        """

        print("🔧 Generating business recommendations...")
        recommendations = analysis_agent.analyze_text(recommendations_prompt)
        print("✅ Recommendations generated")
        print(f"📋 Recommendations: {str(recommendations)[:100]}...")

    except Exception as e:
        print(f"⚠️  Could not generate recommendations: {e}")

    print()

    # Step 4: Create automation summary
    print("🤖 Step 4: Automation Summary")
    print("-" * 30)

    print("✅ Business Automation Workflow Completed!")
    print("\n📋 What was automated:")
    print("• Business report template generation")
    print("• Customer feedback analysis")
    print("• Business recommendations generation")
    print("• Multi-agent coordination")

    print("\n💡 Key Benefits:")
    print("• Automated business processes")
    print("• Consistent analysis and reporting")
    print("• Scalable workflow execution")
    print("• Reduced manual work")

    print("\n🔧 Technical Features Used:")
    print("• Multiple agent coordination")
    print("• Tool integration (math, text processing)")
    print("• Automated workflow execution")
    print("• Error handling and fallbacks")


if __name__ == "__main__":
    main()
