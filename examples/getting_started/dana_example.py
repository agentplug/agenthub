import agenthub as ah

dana_agent = ah.load_agent("aitomatic/Fenrir-Dana")
result = dana_agent.solve_poticon()
