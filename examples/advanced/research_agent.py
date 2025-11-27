import agenthub as ah

research_agent = ah.load_agent(
    "agentplug/research-agent", external_tools=["web_search"]
)

query = "Who is the current president of US"
result = research_agent.instant_research(query)
print(result)
