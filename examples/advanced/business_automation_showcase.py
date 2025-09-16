import agenthub as ah


def main():
    """Demonstrate business automation workflows."""
    print("🏢 Business Automation Showcase")
    print("=" * 35)

    # Initialize system
    storage = ah.LocalStorage()
    runtime = ah.AgentRuntime(storage=storage)

    # Check agents
    if not (
        storage.agent_exists("agentplug", "coding-agent")
        and storage.agent_exists("agentplug", "analysis-agent")
    ):
        print("❌ Required agents not found!")
        return

    print("🔗 Automated Report Generation + Analysis Pipeline\n")

    # Step 1: Generate report template
    print("STEP 1: 📊 Generate Business Report Template")
    print("-" * 45)

    report_prompt = """
    Create a Python class that generates weekly business reports including:
    - Revenue metrics section
    - Customer satisfaction tracking
    - Team productivity analysis
    - Action items and recommendations
    Include methods to export as JSON and formatted text.
    """

    print("🔧 Generating report template...")
    code_result = runtime.execute_agent(
        "agentplug", "coding-agent", "generate_code", {"prompt": report_prompt}
    )

    if "result" in code_result:
        exec_time = code_result.get("execution_time", 0)
        print(f"✅ Report template generated in {exec_time:.1f}s")
        print("📄 Generated Business Report Class:")
        lines = code_result["result"].split("\n")[:10]
        for line in lines:
            print(f"   {line}")
        print("   ... (complete implementation generated)")
    else:
        print(f"❌ Code generation failed: {code_result.get('error')}")
        return

    print()
    input("Press Enter to continue...")
    print()

    # Step 2: Analyze business data
    print("STEP 2: 📈 Analyze Sample Business Performance")
    print("-" * 48)

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
        print("📊 Business Intelligence Insights:")
        print(f"   {analysis_result['result']}")
    else:
        print(f"❌ Analysis failed: {analysis_result.get('error')}")
        return

    print()
    input("Press Enter to continue...")
    print()

    # Step 3: Generate recommendations
    print("STEP 3: 🎯 Generate Executive Summary & Action Plan")
    print("-" * 52)

    print("📝 Creating executive summary...")
    summary_result = runtime.execute_agent(
        "agentplug",
        "analysis-agent",
        "summarize_content",
        {"content": sample_data + "\n\nAnalysis: " + str(analysis_result["result"])},
    )

    if "result" in summary_result:
        exec_time = summary_result.get("execution_time", 0)
        print(f"✅ Executive summary created in {exec_time:.1f}s")
        print("📋 Executive Summary & Recommendations:")
        print(f"   {summary_result['result']}")
    else:
        print(f"❌ Summary generation failed: {summary_result.get('error')}")

    # Show workflow value
    print("\n🎯 COMPLETE WORKFLOW ACHIEVED:")
    print("=" * 35)
    print("✅ Auto-generated report template (saves 2 hours)")
    print("✅ Intelligent data analysis (saves 1 hour)")
    print("✅ Executive summary with recommendations (saves 30 minutes)")
    print("✅ Ready-to-present insights (saves 1 hour)")
    print()
    print("⏱️  TOTAL TIME SAVED: 4.5 hours per week")
    print("📈 BUSINESS VALUE: $500+ per week")
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
