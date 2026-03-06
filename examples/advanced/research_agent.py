import agenthub as ah

research_agent = ah.load_agent(
    "agentplug/research-agent", external_tools=["web_search"]
)
query = "Tell me the news about H1B policy"
result = research_agent.instant_research(query)
print(result)
