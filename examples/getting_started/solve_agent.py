import agenthub as ah

# Load agents
coding_agent = ah.load_agent("agentplug/coding-agent")
analysis_agent = ah.load_agent("agentplug/analysis-agent")

print("🤖 Agent Solve Method Demo")
print("=" * 50)

# Example 1: Code Generation
print("\n💰 Generating Financial Calculator...")
code = coding_agent.solve(
    "Create a Python function that calculates compound interest "
    "with monthly contributions"
)
print(code["result"])

print("\n" + "=" * 50)

# Example 2: Text Analysis
print("\n📊 Analyzing Customer Feedback...")
feedback = """
The new mobile app is fantastic! The user interface is intuitive and the
performance is much better than the previous version. However, I noticed
some issues with the payment processing - it sometimes takes 3-4 attempts
to complete a transaction. The customer support team was very helpful when
I contacted them about this issue. Overall, I'm satisfied but hope the
payment bugs get fixed soon.
"""

analysis = analysis_agent.solve(feedback)
print(f"Analysis: {analysis['result']['summary']}")

print("\n" + "=" * 50)

# Example 3: Code Explanation
print("\n🔍 Explaining Code...")
code_to_explain = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""

explanation = coding_agent.solve(f"Explain what this code does: {code_to_explain}")
print(explanation["result"])

print("\n🎉 All examples completed successfully!")
print("\n💡 The solve() method automatically selects the best method for your query!")
