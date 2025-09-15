import agentmanager as amg


def main():
    # Load agents
    coding_agent = amg.load_agent("agentplug/coding-agent")
    analysis_agent = amg.load_agent("agentplug/analysis-agent")

    # Generate code using the correct method
    code = coding_agent.generate_code(
        "Create a Python function that calculates compound interest "
        "with monthly contributions"
    )
    print("💰 Financial Calculator Code:")
    print("Response structure:", code)
    print("Code result:", code.get("result", code), "\n", "=" * 50)

    # Analyze feedback using the correct method
    feedback = (
        "The new mobile app is fantastic! The user interface is intuitive and "
        "the performance is much better than the previous version. However, I "
        "noticed some issues with the payment processing - it sometimes takes "
        "3-4 attempts to complete a transaction. The customer support team "
        "was very helpful when I contacted them about this issue. Overall, "
        "I'm satisfied but hope the payment bugs get fixed soon."
    )

    insights = analysis_agent.analyze_text(feedback)
    print("\n📊 Customer Feedback Analysis:")
    print(insights)


if __name__ == "__main__":
    main()
