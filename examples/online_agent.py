import agentmanager as amg

paper_analyzer = amg.load_agent("agentplug/scientific-paper-analyzer")
print("Analyzing paper...")
result = paper_analyzer.analyze_paper("C:/Users/Andrea Vu/repos/agenthub/examples/papers/1706.03762v7.pdf")
print(result)