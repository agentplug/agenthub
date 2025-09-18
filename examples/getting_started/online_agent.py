import agenthub as ah

paper_analyzer = ah.load_agent("agentplug/scientific-paper-analyzer")
print("Analyzing paper...")
result = paper_analyzer.analyze_paper("sample_docs/2501.12948v1.pdf")
print(result)
