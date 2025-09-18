import agenthub as ah

agent = ah.load_agent(
    "agentplug/analysis-agent", external_tools=["multiply", "add"], monitoring=True
)
question = "Calculate 12 times 5, then add 8"
print(f"📄 Input: {question}")
result = agent.analyze_text(question)
print(result)
