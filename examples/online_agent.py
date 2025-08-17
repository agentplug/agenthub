import agentmanager as amg

paper_analyzer = amg.load_agent("agentplug/scientific-paper-analyzer")
result = paper_analyzer.analyze_paper("/Users/nguyennm/Project/agenthub/sample_docs/2501.12948v1.pdf")
print(result)
