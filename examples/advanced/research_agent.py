import agenthub as ah

research_agent = ah.load_agent(
    "agentplug/research-agent", external_tools=["web_search"]
)

query = "state of the art AI for semiconductor and chip design"
result = research_agent.deep_research(query)
print(result)
