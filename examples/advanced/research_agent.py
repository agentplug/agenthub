import agenthub as ah

research_agent = ah.load_agent(
    "agentplug/research-agent", external_tools=["web_search"]
)

query = (
    "Does $100,000 fee apply to F1 STEM OPT who want to change status to H1B visa? "
    "Just check gov source."
)
result = research_agent.standard_research(query)
print(result)
